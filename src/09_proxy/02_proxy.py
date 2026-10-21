"""09 프록시 — 패턴 적용: 가상 프록시 · 보호 프록시 · 캐싱 프록시를 같은 인터페이스 뒤에 둔다.

상황: 수아는 화면 코드에서 "이미 받았나? 권한 있나? 캐시에 있나?" 검사를 걷어낸다.
화면은 SatelliteImage(인터페이스)만 다루고, 그 뒤에 무엇이 서 있는지는 모른다.
  - LazyImageProxy (가상 프록시): 메타데이터만 들고 있다가 zoom()이 처음 불릴 때 실제 영상을 '만든다'.
  - ProtectedImageProxy (보호 프록시): 사용자 등급을 보고 zoom()을 허용하거나 거부한다.
  - CachingArchiveProxy (캐싱 프록시): 원격 저장소와 같은 Archive 인터페이스로, 최근 받은 원본을 재사용한다.
핵심 관찰: 프록시는 실제 객체의 '생성과 생명주기'를 통제한다. 클라이언트는 RealSatelliteImage를
직접 만들지도, 참조를 받지도 않는다. 이것이 같은 구조의 데코레이터(6장)와 갈라지는 지점이다.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from collections import OrderedDict
from dataclasses import dataclass


# ===========================================================================
# 원격 저장소와 그 캐싱 프록시
# ===========================================================================

class Archive(ABC):
    """[Subject] 원본 타일 저장소 인터페이스."""

    @abstractmethod
    def fetch(self, image_id: str) -> bytes:
        """원본 타일을 돌려준다."""


class RemoteArchive(Archive):
    """[Real Subject] 원격 저장소. 한 번 받을 때마다 400MB(가정)."""

    def __init__(self) -> None:
        """누적 다운로드량."""
        self.downloaded_mb = 0

    def fetch(self, image_id: str) -> bytes:
        """다운로드를 흉내 낸다."""
        self.downloaded_mb += 400
        print(f"      (원격) {image_id} 다운로드 400MB")
        return f"<raster {image_id}>".encode()


class CachingArchiveProxy(Archive):
    """[Proxy: 캐싱] RemoteArchive와 같은 인터페이스. 최근 capacity개 원본을 기억한다(LRU).

    캐시를 '화면'이 아니라 '저장소 앞'에 둔 이유: 카탈로그·비교 뷰·내보내기 등 영상을 여는
    모든 경로가 자동으로 같은 캐시를 공유한다. 01_naive.py에서는 화면마다 캐시가 따로였다.
    OrderedDict를 쓴 이유: move_to_end/popitem(last=False)로 LRU를 몇 줄에 구현할 수 있다.
    """

    def __init__(self, real: Archive, capacity: int = 2) -> None:
        """실제 저장소와 캐시 용량. 원본이 수백 MB라 용량이 작다는 현실을 반영했다."""
        self._real = real
        self._capacity = capacity
        self._cache: OrderedDict[str, bytes] = OrderedDict()
        self.hits = 0

    def fetch(self, image_id: str) -> bytes:
        """적중하면 최근 사용으로 갱신, 아니면 받아서 넣고 가장 오래된 것을 내보낸다."""
        if image_id in self._cache:
            self.hits += 1
            self._cache.move_to_end(image_id)
            return self._cache[image_id]
        data = self._real.fetch(image_id)
        self._cache[image_id] = data
        if len(self._cache) > self._capacity:
            self._cache.popitem(last=False)
        return data


# ===========================================================================
# 영상과 그 프록시들
# ===========================================================================

@dataclass(frozen=True)
class ImageMeta:
    """카탈로그 색인에서 바로 얻을 수 있는 가벼운 정보. 목록 화면은 이것만으로 그린다."""

    image_id: str
    title: str
    sensitivity: int      # 0 = 공개, 2 = 보안 구역 포함


@dataclass
class User:
    """뷰어 사용자."""

    name: str
    clearance: int


class SatelliteImage(ABC):
    """[Subject] 클라이언트가 아는 유일한 영상 타입.

    zoom()에 user를 받는 이유: 보호 프록시가 판단할 근거가 호출마다 필요하다.
    이 인자를 인터페이스에 넣는 것 자체가 설계 결정이다 — 실제 영상은 user를 쓰지 않지만,
    프록시와 실제 객체가 '교환 가능'(LSP)하려면 시그니처가 같아야 한다.
    """

    @property
    @abstractmethod
    def meta(self) -> ImageMeta:
        """메타데이터(가볍다)."""

    @abstractmethod
    def zoom(self, region: str, user: User) -> str:
        """확대 영역 렌더링(무겁다)."""


class RealSatelliteImage(SatelliteImage):
    """[Real Subject] 생성자에서 원본을 받는다. 01과 같은 '무거운' 객체 — 바꾸지 않았다.

    프록시 패턴의 장점 하나가 여기 있다: 실제 객체는 지연·권한·캐시를 전혀 모른 채 자기 일만 한다.
    """

    def __init__(self, meta: ImageMeta, archive: Archive) -> None:
        """원본을 즉시 받는다."""
        self._meta = meta
        self._raster = archive.fetch(meta.image_id)

    @property
    def meta(self) -> ImageMeta:
        """메타데이터."""
        return self._meta

    def zoom(self, region: str, user: User) -> str:
        """렌더링."""
        return f"{self._meta.title} [{region}] 렌더링 (원본 {self._raster.decode()})"


class LazyImageProxy(SatelliteImage):
    """[Proxy: 가상] 메타데이터만 들고 있다가, 무거운 연산이 처음 요청될 때 실제 객체를 만든다.

    생성 책임이 프록시에 있다는 점이 핵심이다. 클라이언트는 RealSatelliteImage를 만들지 않으므로
    '언제 만들지'를 프록시가 결정할 수 있다. 데코레이터는 이미 만들어진 객체를 받아 감싸므로 이 결정을 못 한다.
    """

    def __init__(self, meta: ImageMeta, archive: Archive) -> None:
        """실제 객체 대신 '만드는 데 필요한 재료'를 보관한다."""
        self._meta = meta
        self._archive = archive
        self._real: RealSatelliteImage | None = None

    @property
    def meta(self) -> ImageMeta:
        """메타데이터는 실제 객체 없이 바로 답한다 — 목록 화면이 빠른 이유."""
        return self._meta

    def zoom(self, region: str, user: User) -> str:
        """첫 호출에서만 실제 객체를 만든다."""
        if self._real is None:
            self._real = RealSatelliteImage(self._meta, self._archive)
        return self._real.zoom(region, user)


class ProtectedImageProxy(SatelliteImage):
    """[Proxy: 보호] 사용자 등급이 민감도보다 낮으면 원본 접근을 거부한다.

    가상 프록시를 감싸도록 조립하는 이유: 권한 검사가 '먼저' 일어나야 거부된 사용자 때문에
    400MB를 받는 일이 없다. 프록시도 데코레이터처럼 중첩되며, 순서가 의미를 갖는다.
    """

    def __init__(self, inner: SatelliteImage) -> None:
        """감쌀 영상(대개 LazyImageProxy)."""
        self._inner = inner

    @property
    def meta(self) -> ImageMeta:
        """메타데이터는 등급과 무관하게 공개(목록에는 보여야 하므로). 정책에 따라 달라질 수 있다."""
        return self._inner.meta

    def zoom(self, region: str, user: User) -> str:
        """등급 검사 후 위임."""
        if user.clearance < self._inner.meta.sensitivity:
            raise PermissionError(f"{user.name}: '{self._inner.meta.title}' 원본 열람 등급 부족")
        return self._inner.zoom(region, user)


def open_image(meta: ImageMeta, archive: Archive) -> SatelliteImage:
    """[조립] 클라이언트가 영상을 얻는 유일한 통로. 프록시 조합 정책이 여기 한 곳에 있다.

    클라이언트가 RealSatelliteImage를 직접 만들 수 있다면 보호 프록시를 우회할 수 있다.
    생성 경로를 이 함수로 단일화하는 것이 보호 프록시를 '실제로' 보호하게 만든다.
    """
    return ProtectedImageProxy(LazyImageProxy(meta, archive))


class CatalogScreen:
    """[Client] 카탈로그 화면. 검사 코드가 하나도 없다."""

    def __init__(self, images: list[SatelliteImage]) -> None:
        """영상 목록."""
        self.images = images

    def view(self, index: int, region: str, user: User) -> str:
        """확대 보기. 거부는 예외로 받아 화면 문구로만 바꾼다."""
        try:
            return self.images[index].zoom(region, user)
        except PermissionError as e:
            return f"접근 거부 — {e}"


if __name__ == "__main__":
    remote = RemoteArchive()
    archive = CachingArchiveProxy(remote, capacity=2)

    print("[1] 2,000장 목록 — 프록시만 만든다")
    images = [open_image(ImageMeta(f"K3-{i:04d}", f"장면 {i}", i % 3), archive) for i in range(2_000)]
    screen = CatalogScreen(images)
    print(f"    목록 표시: {images[0].meta.title} … {images[-1].meta.title}, 다운로드 {remote.downloaded_mb}MB")

    analyst, intern = User("수아", clearance=2), User("인턴", clearance=0)
    print("[2] 확대 보기")
    print("    " + screen.view(2, "북동", analyst))     # 첫 열람: 실제 객체 생성 → 다운로드
    print("    " + screen.view(2, "남서", analyst))     # 같은 프록시: 이미 생성됨
    print("    " + screen.view(5, "중앙", intern))      # 보호 프록시가 다운로드 전에 거부

    print("[3] 다른 화면(비교 뷰)이 같은 영상을 새 프록시로 연다 — 캐싱 프록시가 받는다")
    compare = open_image(ImageMeta("K3-0002", "장면 2", 2), archive)
    print("    " + compare.zoom("전체", analyst))
    print(f"    원격 다운로드 총 {remote.downloaded_mb}MB, 캐시 적중 {archive.hits}회")
