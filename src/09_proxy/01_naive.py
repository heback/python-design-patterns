"""09 프록시 — 순진한 설계: 생성하자마자 수백 MB를 받는 영상 객체와, 화면 곳곳의 검사 코드.

상황: 국토 관측 기관의 GIS 개발자 수아는 위성 영상 아카이브 뷰어를 만든다.
SatelliteImage 객체는 생성될 때 원격 저장소에서 원본 타일(수백 MB)을 내려받는다.
카탈로그 화면은 수천 장을 나열해야 하는데 사용자는 그중 몇 장만 확대해 본다.
게다가 보안 구역이 찍힌 영상은 인가 등급이 있는 사용자만 원본을 볼 수 있고,
같은 영상을 반복해서 여는 일이 잦다. 이 파일은 그 요구를 '화면 코드'가 직접 떠안은 버전이다.
다운로드는 실제로 하지 않고, 받은 MB와 걸렸을 시간을 누적해 비용을 드러낸다.
"""
from __future__ import annotations

from dataclasses import dataclass

DOWNLOAD_MBPS = 50   # 아카이브 회선 속도(MB/s) 가정. 비용을 '초'로 환산하는 데만 쓴다.


class RemoteArchive:
    """원격 영상 저장소(흉내). 받은 총량을 기록한다."""

    def __init__(self) -> None:
        """누적 다운로드 MB."""
        self.downloaded_mb = 0

    def fetch(self, image_id: str) -> bytes:
        """원본 타일 다운로드. 영상 하나에 400MB라고 가정한다."""
        self.downloaded_mb += 400
        return f"<raster {image_id}>".encode()


@dataclass
class User:
    """뷰어 사용자. clearance가 높을수록 민감 영상을 볼 수 있다."""

    name: str
    clearance: int


class SatelliteImage:
    """위성 영상. ⚠ 문제: 생성자가 곧 다운로드다. 목록에 올리기만 해도 400MB."""

    def __init__(self, image_id: str, title: str, sensitivity: int, archive: RemoteArchive) -> None:
        """메타데이터와 함께 원본을 즉시 내려받는다."""
        self.image_id, self.title, self.sensitivity = image_id, title, sensitivity
        self._raster = archive.fetch(image_id)   # ⚠ 문제: 사용자가 볼지 말지 모르는데 받는다

    def zoom(self, region: str) -> str:
        """확대 영역 렌더링."""
        return f"{self.title} [{region}] 렌더링 (원본 {self._raster.decode()} 사용)"


class CatalogScreen:
    """카탈로그 화면. 지연 로딩·권한·캐시 검사를 스스로 한다."""

    def __init__(self, archive: RemoteArchive) -> None:
        """⚠ 문제: 캐시가 화면 객체의 필드다. 다른 화면(비교 뷰, 내보내기)은 이 캐시를 못 쓴다."""
        self.archive = archive
        self.cache: dict[str, SatelliteImage] = {}

    def open(self, user: User, image_id: str, title: str, sensitivity: int, region: str) -> str:
        """확대 보기. 세 가지 검사가 비즈니스 흐름에 섞인다."""
        # ⚠ 문제: '권한 있나?' 검사가 화면 코드에 있다. 내보내기 화면이 이걸 빠뜨리면 유출이다.
        if user.clearance < sensitivity:
            return f"접근 거부: {title}"
        # ⚠ 문제: '캐시에 있나?' 검사도 화면 코드에 있다. SatelliteImage를 쓰는 모든 곳이 반복해야 한다.
        if image_id not in self.cache:
            self.cache[image_id] = SatelliteImage(image_id, title, sensitivity, self.archive)
        return self.cache[image_id].zoom(region)


if __name__ == "__main__":
    archive = RemoteArchive()
    print("[1] 카탈로그에 2,000장 나열 — 목록용 객체를 만들기만 한다")
    catalog = [SatelliteImage(f"K3-{i:04d}", f"장면 {i}", i % 3, archive) for i in range(2_000)]
    print(f"    다운로드 {archive.downloaded_mb:,}MB ≈ {archive.downloaded_mb / DOWNLOAD_MBPS / 60:.0f}분")

    print("[2] (목록 로딩을 포기하고) 화면이 직접 지연·권한·캐시를 처리")
    archive2 = RemoteArchive()
    screen = CatalogScreen(archive2)
    analyst, intern = User("수아", clearance=2), User("인턴", clearance=0)
    print("    " + screen.open(analyst, "K3-0002", "장면 2", 2, "북동"))
    print("    " + screen.open(analyst, "K3-0002", "장면 2", 2, "남서"))   # 캐시 적중
    print("    " + screen.open(intern, "K3-0002", "장면 2", 2, "북동"))
    print(f"    다운로드 {archive2.downloaded_mb}MB — 동작은 한다. 하지만 이 검사들을 아는 것은 이 화면뿐이다.")
