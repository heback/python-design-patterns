"""02 추상 팩토리 — 순진한 코드: 생성 지점마다 클라우드를 따로 고른다.

상황: 업로드 서비스와 썸네일 처리기가 각자 저장소를 직접 만든다. GCP 전환 때
생성 지점마다 `if CLOUD == "gcp"`를 붙였는데, 처리기의 저장소 한 줄을 빠뜨렸다.
실제 클라우드 SDK 대신 주소 형식만 흉내 낸다.
"""
from __future__ import annotations

CLOUD = "gcp"  # 배포 설정값. 실제로는 환경 변수에서 읽는다고 생각하자.


class S3Storage:
    """AWS 저장소. 자기 형식("s3")의 주소만 읽을 수 있다."""

    scheme = "s3"

    def put(self, key: str) -> str:
        """파일을 올리고 주소를 돌려준다."""
        return f"{self.scheme}://bucket/{key}"

    def get(self, url: str) -> str:
        """주소의 파일을 읽는다. 다른 클라우드의 주소는 해석하지 못한다."""
        if not url.startswith(self.scheme):
            raise ValueError(f"{type(self).__name__}가 읽을 수 없는 주소: {url}")
        return url


class GcsStorage(S3Storage):
    """GCP 저장소. 동작은 같고 주소 형식만 "gs"다(코드를 줄이려고 상속했다)."""

    scheme = "gs"


class UploadService:
    """파일을 올리고 썸네일 작업을 넘긴다."""

    def __init__(self) -> None:
        """⚠ 문제: 생성 지점마다 같은 분기가 복제된다."""
        self.storage = GcsStorage() if CLOUD == "gcp" else S3Storage()

    def upload(self, key: str) -> str:
        """올린 파일의 주소를 돌려준다(실제로는 작업 대기열에 넣는다)."""
        return self.storage.put(key)


class ThumbnailWorker:
    """받은 주소로 원본을 읽어 썸네일을 만든다. 업로드와는 다른 프로그램이다."""

    def __init__(self) -> None:
        """⚠ 문제: 여기서만 분기를 빠뜨렸다. 아무도 알려 주지 않는다."""
        self.storage = S3Storage()

    def process(self, url: str) -> str:
        """원본을 읽는다."""
        return f"썸네일 완성: {self.storage.get(url)}"


if __name__ == "__main__":
    print("[1] 서비스 시작: 두 객체 모두 멀쩡히 만들어진다")
    service, worker = UploadService(), ThumbnailWorker()
    print("  시작 OK")

    print("[2] 첫 업로드가 들어온 뒤에야 조합이 틀린 것이 드러난다")
    url = service.upload("cat.png")
    try:
        worker.process(url)
    except ValueError as e:
        print(f"  장애: {e}")  # ⚠ 문제: 배포 몇 시간 뒤에야 터진다
