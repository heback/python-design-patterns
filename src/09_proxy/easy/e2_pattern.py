"""09 프록시 — 패턴 코드: 가상·보호·캐싱 프록시를 같은 인터페이스 뒤에 둔다.

상황: 수아는 화면에서 검사를 걷어낸다. 화면은 SatelliteImage 인터페이스만 다룬다.
  - LazyImageProxy(가상): 제목만 들고 있다가 zoom()이 처음 불릴 때 진짜 사진을 '만든다'.
  - ProtectedImageProxy(보호): 사용자를 보고 zoom()을 허용하거나 막는다.
  - CachingArchiveProxy(캐싱): 원격 저장소와 같은 Archive 인터페이스로, 받은 원본을 재사용한다.
화면은 진짜 사진 객체를 직접 만들지도, 참조를 받지도 않는다. 사진은 open_image()로만 얻는다.
"""
from __future__ import annotations

from abc import ABC, abstractmethod


# --- 저장소 층 ---
class Archive(ABC):
    """[Subject] 원본 저장소 인터페이스."""

    @abstractmethod
    def fetch(self, image_id: str) -> bytes:
        """원본을 돌려준다."""


class RemoteArchive(Archive):
    """[Real Subject] 원격 저장소. 한 번에 400MB."""

    def __init__(self) -> None:
        """누적 다운로드량."""
        self.downloaded_mb = 0

    def fetch(self, image_id: str) -> bytes:
        """다운로드 흉내."""
        self.downloaded_mb += 400
        return f"<원본 {image_id}>".encode()


class CachingArchiveProxy(Archive):
    """[Proxy: 캐싱] RemoteArchive와 같은 모양. 캐시를 화면이 아니라 저장소 앞에 둔다.

    그래서 사진을 여는 모든 경로(목록, 비교 뷰, 내보내기)가 저절로 같은 캐시를 쓴다.
    """

    def __init__(self, real: Archive) -> None:
        """진짜 저장소와 캐시."""
        self._real, self._cache, self.hits = real, {}, 0

    def fetch(self, image_id: str) -> bytes:
        """있으면 재사용, 없으면 받아서 기억한다."""
        if image_id in self._cache:
            self.hits += 1
        else:
            self._cache[image_id] = self._real.fetch(image_id)
        return self._cache[image_id]


# --- 사진 층 ---
class SatelliteImage(ABC):
    """[Subject] 화면이 아는 유일한 사진 타입.

    zoom()이 user를 받는 이유: 보호 프록시가 판단할 근거가 필요하고, 프록시와 진짜
    객체가 바꿔 끼울 수 있으려면(LSP) 모양이 같아야 한다.
    """
    title: str

    @abstractmethod
    def zoom(self, region: str, user: str) -> str:
        """확대 렌더링(무겁다)."""


class RealSatelliteImage(SatelliteImage):
    """[Real Subject] 순진한 코드와 같은 무거운 객체. 생성자에서 원본을 받는다(고치지 않았다)."""

    def __init__(self, image_id: str, title: str, archive: Archive) -> None:
        """원본을 즉시 받는다."""
        self.title, self._data = title, archive.fetch(image_id)

    def zoom(self, region: str, user: str) -> str:
        """렌더링."""
        return f"{self.title} [{region}] 확대"


class LazyImageProxy(SatelliteImage):
    """[Proxy: 가상] 진짜 객체 대신 '만드는 데 필요한 재료'를 들고 있다.

    진짜 객체를 생성자 인자로 받지 않는 것이 핵심이다. 받는다면 이미 다운로드가 끝난 뒤다.
    언제 만들지를 정하려면 만드는 일 자체가 프록시 안에 있어야 한다(데코레이터와의 차이).
    """

    def __init__(self, image_id: str, title: str, archive: Archive) -> None:
        """제목은 바로 답하고, 진짜 객체는 아직 없다."""
        self.title, self._id, self._archive = title, image_id, archive
        self._real: RealSatelliteImage | None = None

    def zoom(self, region: str, user: str) -> str:
        """처음 불릴 때 진짜 객체를 만들고, 이후엔 재사용한다."""
        if self._real is None:
            self._real = RealSatelliteImage(self._id, self.title, self._archive)
        return self._real.zoom(region, user)


class ProtectedImageProxy(SatelliteImage):
    """[Proxy: 보호] 보안 사진은 허가된 사용자에게만. 가상 프록시의 '바깥'에 둔다.

    안쪽에 두면 권한 없는 요청에도 400MB를 먼저 받은 뒤에 거부하게 된다.
    """

    ALLOWED = {"분석관"}

    def __init__(self, inner: SatelliteImage) -> None:
        """감쌀 사진."""
        self._inner, self.title = inner, inner.title

    def zoom(self, region: str, user: str) -> str:
        """허가된 사용자만 안쪽으로 넘긴다."""
        if user not in self.ALLOWED:
            raise PermissionError(f"{user}: 보안 사진 열람 불가")
        return self._inner.zoom(region, user)


def open_image(image_id: str, title: str, secret: bool, archive: Archive) -> SatelliteImage:
    """사진을 얻는 유일한 통로. 이 통로가 하나여야 보호 프록시를 우회할 수 없다."""
    image: SatelliteImage = LazyImageProxy(image_id, title, archive)
    return ProtectedImageProxy(image) if secret else image


if __name__ == "__main__":
    remote = RemoteArchive()
    archive = CachingArchiveProxy(remote)   # 조립 지점에서만 진짜 저장소를 안다
    images = [open_image(f"K3-{i:04}", f"동해안 {i}", i == 0, archive) for i in range(2000)]
    print(f"[1] 목록 2,000장: 제목 '{images[0].title}' 등, 다운로드 {remote.downloaded_mb}MB")
    print(f"[2] 분석관 확대: {images[0].zoom('중심부', '분석관')} → 누적 {remote.downloaded_mb}MB")
    try:
        images[0].zoom("중심부", "인턴")
    except PermissionError as e:
        print(f"    인턴 확대: 거부({e}) — 다운로드 전에 막았다")
    again = open_image("K3-0000", "동해안 0", True, archive)   # 다른 화면이 새 프록시로 연다
    again.zoom("북쪽", "분석관")
    print(f"[3] 다른 화면에서 같은 사진: 누적 {remote.downloaded_mb}MB, 캐시 적중 {archive.hits}회")
