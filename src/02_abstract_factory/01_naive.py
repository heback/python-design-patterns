"""순진한 설계: 서비스 코드 곳곳에서 클라우드 SDK 래퍼를 직접 생성한다.

상황: 스타트업 '구름다리'의 플랫폼 엔지니어 도현은 AWS 위에 파일 업로드 서비스를 만들었다.
업로드 API(UploadService)는 파일을 S3에 올리고 SQS에 "썸네일 만들어 줘" 메시지를 넣는다.
썸네일 워커(ThumbnailWorker)는 큐를 읽어 원본을 S3에서 내려받는다. 둘 다 Secrets
Manager에서 API 키를 꺼낸다. 대형 고객사가 GCP 전용 배포를 요구하자, 도현의 동료가
각 생성 지점에 `if CLOUD == "gcp"` 분기를 넣기 시작했다 — 그런데 한 곳을 빠뜨렸다.

읽을 때 주목할 점:
- 생성 지점이 여러 클래스에 흩어져 있어 환경 전환 시 '모든 곳'을 고쳐야 한다.
- 스토리지·큐·시크릿은 '함께 쓰여야 하는 제품군'인데, 섞여도 아무것도 막지 않는다.
- 섞였을 때의 실패는 시작 시점이 아니라 메시지가 처리되는 '런타임 한참 뒤'에 드러난다.
"""
from __future__ import annotations

# 실제로는 os.environ["CLOUD"]에서 읽는다. 예제에서는 전역 설정으로 흉내 낸다.
CLOUD = "aws"


# ---------------------------------------------------------------------------
# 벤더 SDK 래퍼들. 실제 네트워크 대신 인메모리로 흉내 낸다.
# 클래스 이름 앞부분(S3/Gcs, Sqs/PubSub ...)이 '어느 제품군인가'를 나타낸다.
# ---------------------------------------------------------------------------

_S3_BUCKET: dict[str, bytes] = {}   # AWS 쪽 저장 공간
_GCS_BUCKET: dict[str, bytes] = {}  # GCP 쪽 저장 공간
_QUEUE: list[dict[str, str]] = []   # 큐는 단순화를 위해 하나만 둔다


class S3Storage:
    """AWS S3 래퍼. URL 형식은 s3://."""

    def put(self, key: str, data: bytes) -> str:
        """객체를 저장하고 URL을 돌려준다."""
        _S3_BUCKET[key] = data
        return f"s3://uploads/{key}"

    def get(self, url: str) -> bytes:
        """s3:// URL만 이해한다. 다른 클라우드의 URL은 이 SDK가 다룰 수 없다."""
        if not url.startswith("s3://"):
            raise ValueError(f"S3 SDK는 이 URL을 읽을 수 없음: {url}")
        return _S3_BUCKET[url.removeprefix("s3://uploads/")]


class GcsStorage:
    """GCP Cloud Storage 래퍼. URL 형식은 gs://."""

    def put(self, key: str, data: bytes) -> str:
        """객체를 저장하고 URL을 돌려준다."""
        _GCS_BUCKET[key] = data
        return f"gs://uploads/{key}"

    def get(self, url: str) -> bytes:
        """gs:// URL만 이해한다."""
        if not url.startswith("gs://"):
            raise ValueError(f"GCS SDK는 이 URL을 읽을 수 없음: {url}")
        return _GCS_BUCKET[url.removeprefix("gs://uploads/")]


class SqsQueue:
    """AWS SQS 래퍼."""

    def publish(self, message: dict[str, str]) -> None:
        """메시지를 큐에 넣는다."""
        _QUEUE.append(message)

    def pull(self) -> dict[str, str]:
        """메시지 하나를 꺼낸다."""
        return _QUEUE.pop(0)


class PubSubQueue:
    """GCP Pub/Sub 래퍼."""

    def publish(self, message: dict[str, str]) -> None:
        """메시지를 토픽에 발행한다."""
        _QUEUE.append(message)

    def pull(self) -> dict[str, str]:
        """구독에서 메시지 하나를 꺼낸다."""
        return _QUEUE.pop(0)


class SecretsManagerVault:
    """AWS Secrets Manager 래퍼."""

    def get(self, name: str) -> str:
        """시크릿 값을 돌려준다."""
        return f"aws-secret:{name}"


class GcpSecretManagerVault:
    """GCP Secret Manager 래퍼."""

    def get(self, name: str) -> str:
        """시크릿 값을 돌려준다."""
        return f"gcp-secret:{name}"


# ---------------------------------------------------------------------------
# 서비스 코드 — 생성이 여기저기 흩어져 있다.
# ---------------------------------------------------------------------------

class UploadService:
    """업로드 API: 파일 저장 → 썸네일 작업 메시지 발행."""

    def __init__(self) -> None:
        """필요한 클라우드 객체를 '직접' 만든다."""
        # ⚠ 문제: 환경 분기가 생성 지점마다 복제된다. 세 줄이 '같은 환경'이어야 한다는
        #   사실은 코드 어디에도 표현되지 않고, 사람이 기억해야 하는 규칙으로만 존재한다.
        self.storage = GcsStorage() if CLOUD == "gcp" else S3Storage()
        self.queue = PubSubQueue() if CLOUD == "gcp" else SqsQueue()
        self.vault = GcpSecretManagerVault() if CLOUD == "gcp" else SecretsManagerVault()

    def upload(self, key: str, data: bytes) -> str:
        """저장하고 메시지를 발행한다."""
        api_key = self.vault.get("upload-api-key")
        url = self.storage.put(key, data)
        self.queue.publish({"url": url, "auth": api_key})
        return url


class ThumbnailWorker:
    """썸네일 워커: 큐에서 메시지를 받아 원본을 내려받는다."""

    def __init__(self) -> None:
        """여기도 클라우드 객체를 직접 만든다."""
        self.queue = PubSubQueue() if CLOUD == "gcp" else SqsQueue()
        # ⚠ 문제: GCP 전환 때 이 줄을 빠뜨렸다. 분기 없이 S3Storage가 하드코딩되어 있다.
        #   타입 검사도, 시작 시 검사도 이것을 잡지 못한다 — 둘 다 put/get을 가진 '정상' 객체다.
        self.storage = S3Storage()

    def process_one(self) -> str:
        """메시지 하나를 처리한다."""
        message = self.queue.pull()
        original = self.storage.get(message["url"])  # 섞인 조합은 여기서야 터진다
        return f"썸네일 생성 완료 ({len(original)} bytes)"


def run_scenario(cloud: str) -> None:
    """주어진 환경에서 업로드 → 썸네일 처리를 한 번 돌린다."""
    global CLOUD
    CLOUD = cloud  # 배포 환경 변수 전환을 흉내 낸다
    service = UploadService()
    worker = ThumbnailWorker()  # 시작 시점에는 아무 오류도 없다
    print(f"  서비스 시작 OK (storage={type(service.storage).__name__}, "
          f"worker.storage={type(worker.storage).__name__})")
    url = service.upload("cat.png", b"\x89PNG....")
    print(f"  업로드: {url}")
    try:
        print(f"  워커: {worker.process_one()}")
    except ValueError as e:
        print(f"  워커 실패: {e}")


if __name__ == "__main__":
    print("[1] AWS 배포 — 모든 생성 지점이 우연히 일치한다")
    run_scenario("aws")

    print("\n[2] GCP 배포 — 한 곳을 빠뜨린 결과: 시작은 멀쩡하고, 첫 메시지에서 실패")
    run_scenario("gcp")

    print("\n[3] 로컬 개발 환경을 추가하려면?")
    print("  UploadService, ThumbnailWorker, 그리고 생성 지점이 있는 모든 클래스의")
    print("  삼항 연산자를 if/elif 3갈래로 바꿔야 한다 — 환경 수 × 생성 지점 수만큼의 수정.")
