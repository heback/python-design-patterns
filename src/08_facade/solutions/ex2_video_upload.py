"""08 퍼사드 — 연습문제 2 해설: 동영상 업로드 핸들러를 퍼사드로.

상황: 푸른날개항공의 기내 엔터테인먼트 관리 콘솔에서 콘텐츠 담당자가 동영상을 올리면,
웹 핸들러가 저장소·트랜스코더·썸네일 생성기·메타데이터 DB를 직접 순서대로 불렀다.
같은 업로드가 일괄 등록 CLI에서도 필요해지자 호출 순서가 복제되기 시작했다.
여기서는 VideoIngestFacade.ingest() 하나로 흐름을 모으고, 실패 시 정리(저장한 원본 삭제)
규칙도 퍼사드에 둔다. 핸들러는 HTTP 일(요청 해석, 응답 코드)만 한다.
"""
from __future__ import annotations

from dataclasses import dataclass


class Storage:
    """[Subsystem] 객체 저장소."""

    def put(self, key: str, data: bytes) -> str:
        """저장 후 URL."""
        return f"s3://ife-media/{key}"

    def delete(self, url: str) -> None:
        """삭제(보상 처리용)."""
        print(f"    (storage) 삭제 {url}")


class Transcoder:
    """[Subsystem] 트랜스코딩. 지원하지 않는 형식이면 예외."""

    def transcode(self, url: str, profiles: list[str]) -> list[str]:
        """프로필별 결과 URL."""
        if url.endswith(".avi"):
            raise RuntimeError("지원하지 않는 코덱")
        return [f"{url}@{p}" for p in profiles]


class Thumbnailer:
    """[Subsystem] 썸네일."""

    def capture(self, url: str, at_sec: int) -> str:
        """지정 시점 캡처."""
        return f"{url}.thumb{at_sec}.jpg"


class MetadataDb:
    """[Subsystem] 메타데이터 DB."""

    def insert(self, title: str, renditions: list[str], thumb: str) -> int:
        """레코드 id."""
        return 42


class IngestError(Exception):
    """업로드 실패. 클라이언트는 이 하나만 처리한다."""


@dataclass(frozen=True)
class IngestResult:
    """클라이언트에 필요한 최소 정보."""

    video_id: int
    thumbnail: str


class VideoIngestFacade:
    """[Facade] 업로드 흐름의 단일 진입점.

    퍼사드가 가져가는 지식: 호출 순서, 트랜스코딩 프로필 목록(기내 화면 규격), 썸네일 시점,
    그리고 '중간 실패 시 저장한 원본을 지운다'는 보상 규칙. 이 마지막 규칙이 클라이언트마다
    복제되면 반드시 어느 한 곳에서 빠진다.
    """

    PROFILES = ["720p", "480p"]

    def __init__(self, storage: Storage, transcoder: Transcoder,
                 thumbs: Thumbnailer, db: MetadataDb) -> None:
        """서브시스템 주입."""
        self._s, self._t, self._th, self._db = storage, transcoder, thumbs, db

    def ingest(self, filename: str, title: str, data: bytes) -> IngestResult:
        """저장 → 트랜스코딩 → 썸네일 → 메타데이터. 실패하면 원본을 정리하고 IngestError."""
        url = self._s.put(filename, data)
        try:
            renditions = self._t.transcode(url, self.PROFILES)
            thumb = self._th.capture(url, at_sec=5)
            return IngestResult(self._db.insert(title, renditions, thumb), thumb)
        except RuntimeError as e:
            self._s.delete(url)
            raise IngestError(f"{filename}: {e}") from e


def upload_handler(facade: VideoIngestFacade, form: dict) -> tuple[int, str]:
    """[Client] 웹 핸들러. HTTP 관심사만 남았다: 입력 해석과 상태 코드."""
    try:
        r = facade.ingest(form["filename"], form["title"], form["data"])
    except IngestError as e:
        return 422, str(e)
    return 201, f"/videos/{r.video_id} (썸네일 {r.thumbnail})"


def cli_bulk_upload(facade: VideoIngestFacade, paths: list[str]) -> list[str]:
    """[Client] 일괄 등록 CLI. 같은 퍼사드를 공유하되 표현은 자기 방식(실패 목록, 상태 코드 없음)."""
    failed = []
    for path in paths:
        try:
            facade.ingest(path, title=path.rsplit(".", 1)[0], data=b"..")
        except IngestError as e:
            failed.append(str(e))
    return failed


if __name__ == "__main__":
    facade = VideoIngestFacade(Storage(), Transcoder(), Thumbnailer(), MetadataDb())
    print("[1] 정상 업로드:", upload_handler(facade, {"filename": "safety.mp4", "title": "안전 안내", "data": b".."}))
    print("[2] 실패 업로드 — 퍼사드가 원본을 정리한다")
    print("   ", upload_handler(facade, {"filename": "old.avi", "title": "구형 영상", "data": b".."}))
    print("[3] 일괄 등록 CLI — 흐름과 보상 규칙을 복제하지 않고 같은 퍼사드를 부른다")
    print(f"    실패 목록: {cli_bulk_upload(facade, ['menu.mp4', 'promo.avi', 'map.mp4'])}")
