"""추상 팩토리 적용: 팩토리 하나를 고르면 스토리지·큐·시크릿 제품군 전체가 정해진다.

상황: 01_naive.py에서는 생성 지점이 UploadService와 ThumbnailWorker에 흩어져 있었고,
GCP 전환 때 한 곳을 빠뜨리자 GCS 업로드 + S3 다운로드라는 '섞인 조합'이 만들어져
첫 메시지 처리 때에야 실패했다. 여기서는 "함께 쓰여야 하는 객체들의 생성"을
CloudFactory 하나에 묶는다. 서비스 코드는 팩토리만 받으므로 제품을 섞을 방법 자체가 없다.

GoF 의도(intent): "구체 클래스를 지정하지 않고, 서로 관련되거나 의존하는 객체들의
군(family)을 생성하기 위한 인터페이스를 제공한다."

역할 대응:
- [Abstract Factory]  CloudFactory
- [Concrete Factory]  AwsFactory, GcpFactory, LocalFactory
- [Abstract Product]  BlobStorage, MessageQueue, SecretVault
- [Concrete Product]  S3Storage, SqsQueue, ... / GcsStorage, ... / LocalFileStorage, ...
- [Client]            UploadService, ThumbnailWorker
"""
from __future__ import annotations

import os
from abc import ABC, abstractmethod
from dataclasses import dataclass, field


# ---------------------------------------------------------------------------
# 각 클라우드의 '계정 컨텍스트'. 실제로는 boto3.Session이나 GCP 자격 증명에 해당한다.
# 제품군이 일관되어야 하는 진짜 이유가 바로 이것이다 — 같은 제품군의 제품들은
# 같은 자격 증명·리전·프로젝트를 공유해야 서로의 결과(URL, 메시지)를 이해한다.
# ---------------------------------------------------------------------------

@dataclass
class CloudAccount:
    """시뮬레이션용 클라우드 계정: 버킷과 큐를 메모리에 둔다."""

    name: str
    url_scheme: str
    bucket: dict[str, bytes] = field(default_factory=dict)
    queue: list[dict[str, str]] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Abstract Product — 서비스 코드가 아는 것은 이 세 인터페이스뿐이다.
# ---------------------------------------------------------------------------

class BlobStorage(ABC):
    """[Abstract Product] 객체 저장소."""

    @abstractmethod
    def put(self, key: str, data: bytes) -> str:
        """저장하고 같은 제품군의 다른 제품이 이해하는 URL을 돌려준다."""

    @abstractmethod
    def get(self, url: str) -> bytes:
        """URL로 객체를 읽는다."""


class MessageQueue(ABC):
    """[Abstract Product] 메시지 큐."""

    @abstractmethod
    def publish(self, message: dict[str, str]) -> None:
        """메시지를 넣는다."""

    @abstractmethod
    def pull(self) -> dict[str, str]:
        """메시지 하나를 꺼낸다."""


class SecretVault(ABC):
    """[Abstract Product] 시크릿 저장소."""

    @abstractmethod
    def get(self, name: str) -> str:
        """시크릿 값을 돌려준다."""


# ---------------------------------------------------------------------------
# Concrete Product — 계정 컨텍스트를 공유하는 공통 구현을 먼저 둔다.
# 실제 SDK 래퍼라면 클래스마다 내용이 완전히 다르겠지만, 예제에서는 '어느 계정을
# 쓰는가'만 다르므로 공통 부분을 기반 클래스로 모아 반복을 줄였다.
# ---------------------------------------------------------------------------

class _AccountStorage(BlobStorage):
    """계정 하나에 묶인 저장소의 공통 구현. 자기 계정의 URL 형식만 이해한다."""

    def __init__(self, account: CloudAccount) -> None:
        """제품은 스스로 계정을 만들지 않고 팩토리가 준 것을 쓴다(제품군 공유 컨텍스트)."""
        self.account = account

    def put(self, key: str, data: bytes) -> str:
        """계정 버킷에 저장한다."""
        self.account.bucket[key] = data
        return f"{self.account.url_scheme}://uploads/{key}"

    def get(self, url: str) -> bytes:
        """자기 URL 형식이 아니면 거부한다 — 01_naive.py에서 터졌던 바로 그 검사."""
        prefix = f"{self.account.url_scheme}://uploads/"
        if not url.startswith(prefix):
            raise ValueError(f"{type(self).__name__}는 이 URL을 읽을 수 없음: {url}")
        return self.account.bucket[url.removeprefix(prefix)]


class _AccountQueue(MessageQueue):
    """계정 하나에 묶인 큐의 공통 구현."""

    def __init__(self, account: CloudAccount) -> None:
        """팩토리가 준 계정을 쓴다."""
        self.account = account

    def publish(self, message: dict[str, str]) -> None:
        """계정 큐에 넣는다."""
        self.account.queue.append(message)

    def pull(self) -> dict[str, str]:
        """계정 큐에서 꺼낸다."""
        return self.account.queue.pop(0)


class S3Storage(_AccountStorage):
    """[Concrete Product] AWS 제품군의 저장소."""


class SqsQueue(_AccountQueue):
    """[Concrete Product] AWS 제품군의 큐."""


class SecretsManagerVault(SecretVault):
    """[Concrete Product] AWS 제품군의 시크릿 저장소."""

    def __init__(self, region: str) -> None:
        """시크릿은 리전에 묶인다."""
        self.region = region

    def get(self, name: str) -> str:
        """리전 정보가 붙은 값을 돌려준다."""
        return f"aws[{self.region}]:{name}"


class GcsStorage(_AccountStorage):
    """[Concrete Product] GCP 제품군의 저장소."""


class PubSubQueue(_AccountQueue):
    """[Concrete Product] GCP 제품군의 큐."""


class GcpSecretManagerVault(SecretVault):
    """[Concrete Product] GCP 제품군의 시크릿 저장소."""

    def __init__(self, project: str) -> None:
        """시크릿은 GCP 프로젝트에 묶인다."""
        self.project = project

    def get(self, name: str) -> str:
        """프로젝트 정보가 붙은 값을 돌려준다."""
        return f"gcp[{self.project}]:{name}"


class LocalFileStorage(_AccountStorage):
    """[Concrete Product] 로컬 제품군의 저장소(개발자 노트북용, file:// URL)."""


class InMemoryQueue(_AccountQueue):
    """[Concrete Product] 로컬 제품군의 큐. 프로세스 안 리스트로 충분하다."""


class DotEnvVault(SecretVault):
    """[Concrete Product] 로컬 제품군의 시크릿 저장소. .env 파일 내용을 흉내 낸다."""

    def __init__(self, values: dict[str, str]) -> None:
        """.env를 파싱한 결과를 받는다."""
        self.values = values

    def get(self, name: str) -> str:
        """없는 키는 개발용 기본값으로 대신한다 — 로컬에서만 허용되는 관대함."""
        return self.values.get(name, f"dev-{name}")


# ---------------------------------------------------------------------------
# Abstract Factory / Concrete Factory
# ---------------------------------------------------------------------------

class CloudFactory(ABC):
    """[Abstract Factory] 제품군 하나를 만드는 생성 메서드들의 묶음.

    각 create_*는 그 자체로 팩토리 메서드(1장)다. 추상 팩토리의 새로움은 이것들을
    '한 객체'에 묶었다는 데 있다. 클라이언트가 팩토리 '하나'를 받으므로, 제품군의
    일관성이 '사람이 기억할 규칙'에서 '객체 구조'로 옮겨 간다.
    """

    @abstractmethod
    def create_storage(self) -> BlobStorage:
        """제품군의 저장소를 만든다."""

    @abstractmethod
    def create_queue(self) -> MessageQueue:
        """제품군의 큐를 만든다."""

    @abstractmethod
    def create_vault(self) -> SecretVault:
        """제품군의 시크릿 저장소를 만든다."""


class AwsFactory(CloudFactory):
    """[Concrete Factory] AWS 제품군. 리전과 계정 컨텍스트를 한 번만 정하고 모든 제품에 나눠 준다."""

    def __init__(self, region: str) -> None:
        """계정 컨텍스트를 팩토리가 소유한다 — 제품마다 따로 만들면 일관성이 깨질 수 있다."""
        self.region = region
        self._account = CloudAccount(name=f"aws/{region}", url_scheme="s3")

    def create_storage(self) -> BlobStorage:
        """S3 저장소."""
        return S3Storage(self._account)

    def create_queue(self) -> MessageQueue:
        """SQS 큐."""
        return SqsQueue(self._account)

    def create_vault(self) -> SecretVault:
        """Secrets Manager."""
        return SecretsManagerVault(self.region)


class GcpFactory(CloudFactory):
    """[Concrete Factory] GCP 제품군."""

    def __init__(self, project: str) -> None:
        """GCP는 리전 대신 프로젝트가 경계다 — 제품군마다 필요한 설정이 다르다."""
        self.project = project
        self._account = CloudAccount(name=f"gcp/{project}", url_scheme="gs")

    def create_storage(self) -> BlobStorage:
        """GCS 저장소."""
        return GcsStorage(self._account)

    def create_queue(self) -> MessageQueue:
        """Pub/Sub 큐."""
        return PubSubQueue(self._account)

    def create_vault(self) -> SecretVault:
        """GCP Secret Manager."""
        return GcpSecretManagerVault(self.project)


class LocalFactory(CloudFactory):
    """[Concrete Factory] 클라우드 없이 노트북에서 돌아가는 제품군."""

    def __init__(self, dotenv: dict[str, str]) -> None:
        """.env 내용을 받는다."""
        self._dotenv = dotenv
        self._account = CloudAccount(name="local", url_scheme="file")

    def create_storage(self) -> BlobStorage:
        """로컬 파일 저장소."""
        return LocalFileStorage(self._account)

    def create_queue(self) -> MessageQueue:
        """인메모리 큐."""
        return InMemoryQueue(self._account)

    def create_vault(self) -> SecretVault:
        """.env 시크릿."""
        return DotEnvVault(self._dotenv)


# ---------------------------------------------------------------------------
# Client — 구체 클래스 이름이 하나도 없다.
# ---------------------------------------------------------------------------

class UploadService:
    """[Client] 업로드 API. 어느 클라우드인지 모른다."""

    def __init__(self, cloud: CloudFactory) -> None:
        """제품 세 개를 따로 받지 않고 팩토리 하나를 받는다.

        왜 제품을 개별 인자로 주입하지 않는가? 그러면 호출자가 다시 GCS와 SQS를
        섞어 넘길 수 있다. 팩토리를 받으면 '어느 제품군인가'라는 결정이 한 번만 내려진다.
        """
        self.storage = cloud.create_storage()
        self.queue = cloud.create_queue()
        self.vault = cloud.create_vault()

    def upload(self, key: str, data: bytes) -> str:
        """저장하고 메시지를 발행한다."""
        url = self.storage.put(key, data)
        self.queue.publish({"url": url, "auth": self.vault.get("upload-api-key")})
        return url


class ThumbnailWorker:
    """[Client] 썸네일 워커. 01_naive.py에서 S3Storage를 하드코딩했던 바로 그 클래스."""

    def __init__(self, cloud: CloudFactory) -> None:
        """같은 팩토리에서 받으므로 저장소와 큐가 반드시 같은 제품군이다."""
        self.queue = cloud.create_queue()
        self.storage = cloud.create_storage()

    def process_one(self) -> str:
        """메시지 하나를 처리한다."""
        message = self.queue.pull()
        original = self.storage.get(message["url"])
        return f"썸네일 생성 완료 ({len(original)} bytes, auth={message['auth']})"


# ---------------------------------------------------------------------------
# Composition root — 구체 팩토리를 고르는 곳은 프로그램 전체에서 여기 한 곳이다.
# ---------------------------------------------------------------------------

def make_cloud_factory(env: str) -> CloudFactory:
    """배포 환경 이름으로 구체 팩토리를 고른다.

    여기에는 if/elif가 있어도 된다. 01_naive.py의 문제는 분기가 '있다'는 것이 아니라
    생성 지점마다 '복제'되었다는 것이었다. 분기가 한 곳에만 있으면 환경 추가 비용은 한 줄이다.
    """
    if env == "aws":
        return AwsFactory(region="ap-northeast-2")
    if env == "gcp":
        return GcpFactory(project="gureumdari-prod")
    if env == "local":
        return LocalFactory(dotenv={"upload-api-key": "local-key"})
    raise ValueError(f"알 수 없는 환경: {env}")


if __name__ == "__main__":
    print("[1] 같은 서비스 코드를 세 환경에서 실행한다 (환경 변수 CLOUD_ENV를 흉내 냄)")
    for env in ("aws", "gcp", "local"):
        os.environ["CLOUD_ENV"] = env
        factory = make_cloud_factory(os.environ["CLOUD_ENV"])
        service, worker = UploadService(factory), ThumbnailWorker(factory)
        url = service.upload("cat.png", b"\x89PNG....")
        print(f"  [{env:5}] {type(factory).__name__:12} 업로드 {url:22} → {worker.process_one()}")

    print("\n[2] 섞인 조합은 어디서 만들 수 있는가?")
    print("  UploadService/ThumbnailWorker는 CloudFactory 하나만 받는다.")
    print("  GcpFactory가 S3Storage를 돌려주는 코드는 GcpFactory 클래스 안에서만 쓸 수 있고,")
    print("  그곳은 '제품군 정의'를 리뷰하는 단 한 곳이다.")

    print("\n[3] 로컬 제품군의 함정: 인메모리 큐는 '팩토리 인스턴스'에 묶여 있다")
    # 실제 AWS라면 팩토리 인스턴스가 둘이어도 같은 리전의 같은 클라우드를 본다.
    # 그러나 로컬 제품군의 큐는 프로세스 메모리이므로 팩토리 인스턴스마다 따로 생긴다.
    # (주의: 이 예제의 시뮬레이션에서는 AwsFactory/GcpFactory도 인스턴스마다 CloudAccount를 새로
    #  만들므로 같은 현상이 난다. 실제 클라우드에서는 계정이 외부 상태라 두 인스턴스가 공유한다.)
    uploader = UploadService(make_cloud_factory("local"))
    stranger = ThumbnailWorker(make_cloud_factory("local"))  # 같은 종류, 다른 인스턴스
    uploader.upload("dog.png", b"woof")
    try:
        stranger.process_one()
    except IndexError:
        print("  워커의 큐가 비어 있음 → composition root에서 팩토리를 '하나' 만들어 모두에게 나눠 줘야 한다")
        print("  (그렇다고 팩토리를 싱글턴으로 만들 필요는 없다 — 4장에서 다룬다)")
