"""02 추상 팩토리 — 패턴 코드: 한 클라우드의 제품들을 한 팩토리가 함께 만든다.

상황: 저장소·큐·비밀 값 저장소는 같은 클라우드끼리만 서로를 이해한다. 그래서
"어느 클라우드인가"를 팩토리 하나를 고르는 결정으로 한 번만 내리게 한다.
[Abstract Factory] CloudFactory / [Concrete Factory] AwsFactory, GcpFactory, LocalFactory
[Abstract Product] BlobStorage, MessageQueue, SecretVault / [Client] UploadService, ThumbnailWorker
"""
from __future__ import annotations

from abc import ABC, abstractmethod


# --- 추상 제품: 클라이언트가 아는 유일한 타입 ---------------------------------
# 실제로는 구체 제품마다 벤더 SDK를 감싼다. 여기서는 주소 형식(scheme)만 다르게 흉내 낸다.
class BlobStorage:
    """[Abstract Product] 파일 저장소. 자기 형식의 주소만 읽는다."""

    scheme = ""

    def put(self, key: str) -> str:
        """파일을 올리고 주소를 돌려준다."""
        return f"{self.scheme}://bucket/{key}"

    def get(self, url: str) -> str:
        """다른 클라우드의 주소면 실패한다 — 제품군이 섞이면 안 되는 이유."""
        if not url.startswith(f"{self.scheme}://"):
            raise ValueError(f"{type(self).__name__}가 읽을 수 없는 주소: {url}")
        return url


class MessageQueue:
    """[Abstract Product] 작업 메시지를 넘기는 큐(이 예제에서는 쓰지 않아 비워 둔다)."""


class SecretVault:
    """[Abstract Product] 비밀 값 저장소."""


# --- 구체 제품: 클라우드(제품군)마다 하나씩. 열 = 제품군, 행 = 제품 종류 ---------
class S3Storage(BlobStorage):
    """[Concrete Product] AWS 저장소."""
    scheme = "s3"
class SqsQueue(MessageQueue):
    """[Concrete Product] AWS 큐."""
class SecretsManagerVault(SecretVault):
    """[Concrete Product] AWS 비밀 값 저장소."""


class GcsStorage(BlobStorage):
    """[Concrete Product] GCP 저장소."""
    scheme = "gs"
class PubSubQueue(MessageQueue):
    """[Concrete Product] GCP 큐."""
class GcpSecretVault(SecretVault):
    """[Concrete Product] GCP 비밀 값 저장소."""


class LocalFileStorage(BlobStorage):
    """[Concrete Product] 노트북 개발용 저장소."""
    scheme = "file"
class InMemoryQueue(MessageQueue):
    """[Concrete Product] 노트북 개발용 큐."""
class DotEnvVault(SecretVault):
    """[Concrete Product] 노트북 개발용 비밀 값 저장소."""


# --- 팩토리 -----------------------------------------------------------------
class CloudFactory(ABC):
    """[Abstract Factory] 제품 종류마다 생성 메서드를 하나씩 둔다.

    ABC를 쓴 이유: 제품 종류가 늘어 메서드가 추가되면, 구현을 빠뜨린 구체 팩토리를
    인스턴스화하는 순간 TypeError로 잡아 준다.
    """

    @abstractmethod
    def create_storage(self) -> BlobStorage:
        """저장소를 만든다."""

    @abstractmethod
    def create_queue(self) -> MessageQueue:
        """큐를 만든다."""

    @abstractmethod
    def create_vault(self) -> SecretVault:
        """비밀 값 저장소를 만든다."""


class AwsFactory(CloudFactory):
    """[Concrete Factory] AWS 제품만 만든다. 섞인 조합은 이 클래스 정의를 틀려야만 생긴다."""

    def create_storage(self) -> BlobStorage:
        """AWS 저장소."""
        return S3Storage()

    def create_queue(self) -> MessageQueue:
        """AWS 큐."""
        return SqsQueue()

    def create_vault(self) -> SecretVault:
        """AWS의 비밀 값 저장소."""
        return SecretsManagerVault()


class GcpFactory(CloudFactory):
    """[Concrete Factory] GCP 제품만 만든다."""

    def create_storage(self) -> BlobStorage:
        """GCP 저장소."""
        return GcsStorage()

    def create_queue(self) -> MessageQueue:
        """GCP 큐."""
        return PubSubQueue()

    def create_vault(self) -> SecretVault:
        """GCP의 비밀 값 저장소."""
        return GcpSecretVault()


class LocalFactory(CloudFactory):
    """[Concrete Factory] 클라우드 없이 노트북에서 돌리는 제품군."""

    def create_storage(self) -> BlobStorage:
        """로컬 파일."""
        return LocalFileStorage()

    def create_queue(self) -> MessageQueue:
        """메모리 큐."""
        return InMemoryQueue()

    def create_vault(self) -> SecretVault:
        """설정 파일."""
        return DotEnvVault()


# --- 클라이언트: 구체 클래스 이름이 하나도 없다 ---------------------------------
class UploadService:
    """[Client] 제품을 따로 받지 않고 팩토리 하나를 받는다 — 섞어 넘길 길을 없앤다."""

    def __init__(self, cloud: CloudFactory) -> None:
        """같은 팩토리에서 꺼내므로 저장소와 큐는 늘 같은 클라우드다."""
        self.storage, self.queue = cloud.create_storage(), cloud.create_queue()

    def upload(self, key: str) -> str:
        """올린 파일의 주소를 돌려준다(실제로는 이 주소를 큐에 넣는다)."""
        return self.storage.put(key)


class ThumbnailWorker:
    """[Client] 순진한 코드에서 장애를 냈던 그 썸네일 처리기."""

    def __init__(self, cloud: CloudFactory) -> None:
        """저장소를 다른 클라우드에서 가져올 방법이 없다."""
        self.storage = cloud.create_storage()

    def process(self, url: str) -> str:
        """원본을 읽어 썸네일을 만든다."""
        return f"썸네일 완성: {self.storage.get(url)}"


def make_cloud_factory(env: str) -> CloudFactory:
    """분기가 남는 유일한 곳. 프로그램 시작 지점에서 한 번만 부른다."""
    factories = {"aws": AwsFactory, "gcp": GcpFactory, "local": LocalFactory}
    return factories[env]()


if __name__ == "__main__":
    print("[1] 같은 클라이언트 코드가 세 환경에서 그대로 돈다")
    for env in ["aws", "gcp", "local"]:
        cloud = make_cloud_factory(env)  # 결정은 여기서 한 번
        url = UploadService(cloud).upload("cat.png")
        print(f"  {env:5} → {ThumbnailWorker(cloud).process(url)}")

    print("[2] 섞인 조합을 만들 수 있는 곳은 구체 팩토리의 정의 한 곳뿐이다")
    print("  GcpFactory.create_storage()가 S3Storage를 돌려주게 쓰지 않는 한 섞이지 않는다")
