"""09 프록시 — 파이썬다운 변형: __getattr__ 범용 지연 프록시, cached_property, lru_cache, weakref.proxy.

상황: 02_proxy.py의 LazyImageProxy는 SatelliteImage 전용이다. 수아의 팀에는 지연 로딩이
필요한 대형 객체가 더 있다(수치표고모델 DEM, 토지피복 분류 래스터). 팀원 건우는 "아무 객체나
감싸는 범용 지연 프록시를 __getattr__로 만들자"고 했다. 이 파일은 그 제안을 구현해 한계를 보고,
프록시 없이 해결되는 경우와 표준 라이브러리의 프록시를 차례로 본다.
  (1) LazyProxy: __getattr__ 기반 범용 가상 프록시 — 일반 속성은 되지만 특수 메서드·isinstance·== 에서 샌다.
  (2) functools.cached_property: 객체 '내부'의 지연 로딩. 생성 시점을 통제할 수 있다면 프록시가 필요 없다.
  (3) functools.lru_cache: 함수 결과 캐시 — 캐싱 프록시의 가장 가벼운 형태.
  (4) weakref.proxy: 표준 라이브러리의 프록시. 실제 객체의 생명주기를 '소유하지 않는' 참조.
"""
from __future__ import annotations

import gc
import weakref
from functools import cached_property, lru_cache
from typing import Any, Callable

LOADS: list[str] = []   # 무거운 로딩이 언제 일어났는지 관찰하기 위한 기록


class DemRaster:
    """수치표고모델(DEM). 생성 시 대용량 로딩을 한다고 가정."""

    def __init__(self, tile: str) -> None:
        """로딩을 기록한다."""
        LOADS.append(tile)
        self.tile = tile
        self.cells = [120, 340, 560, 410]   # 고도(m) 샘플

    def max_elevation(self) -> int:
        """최고 고도."""
        return max(self.cells)

    def __len__(self) -> int:
        """셀 수."""
        return len(self.cells)


# --- (1) __getattr__ 범용 지연 프록시 ----------------------------------------

class LazyProxy:
    """[Proxy: 가상, 범용] factory()를 처음 필요할 때 한 번 호출해 실제 객체를 만든다.

    __getattr__은 '일반 조회가 실패했을 때만' 불리므로, 프록시 자신의 속성(_factory, _obj)은
    그대로 보이고 나머지는 실제 객체로 넘어간다. 한계는 docstring이 아니라 데모 [1]이 보여 준다.
    """

    _UNSET: Any = object()   # '아직 안 만듦' 표시. None을 쓰면 factory가 None을 돌려줄 때 매번 다시 만든다.

    def __init__(self, factory: Callable[[], Any]) -> None:
        """생성 방법만 보관한다. 이 시점에는 아무것도 로딩하지 않는다."""
        self._factory = factory
        self._obj: Any = LazyProxy._UNSET

    def _target(self) -> Any:
        """실제 객체를 (필요하면 만들어) 돌려준다."""
        if self._obj is LazyProxy._UNSET:
            self._obj = self._factory()
        return self._obj

    def __getattr__(self, name: str) -> Any:
        """정의되지 않은 일반 속성은 실제 객체로 위임."""
        return getattr(self._target(), name)


# --- (2) cached_property: 객체 내부의 지연 로딩 -------------------------------

class LandCoverScene:
    """토지피복 분류 장면. 무거운 부분(raster)만 첫 접근 때 로딩한다.

    이 클래스를 우리가 설계할 수 있다면 프록시가 필요 없다. 지연이 클래스 안에 들어 있으므로
    isinstance·특수 메서드 문제도 없다. 프록시는 '실제 객체를 고칠 수 없거나, 정책을 분리하고 싶을 때'의 해법이다.
    """

    def __init__(self, scene_id: str) -> None:
        """가벼운 메타데이터만."""
        self.scene_id = scene_id

    @cached_property
    def raster(self) -> list[str]:
        """첫 접근 때 한 번 계산되어 인스턴스 __dict__에 저장된다. 이후엔 일반 속성 조회."""
        LOADS.append(self.scene_id)
        return ["농경지", "산림", "수계"]


# --- (3) lru_cache: 캐싱 프록시의 함수 버전 -----------------------------------

@lru_cache(maxsize=2)
def fetch_tile(tile_id: str) -> bytes:
    """원격 타일 다운로드(흉내). 같은 인자면 캐시에서 돌려준다.

    02의 CachingArchiveProxy와 하는 일이 같다. 차이: 인터페이스가 '함수 하나'면 이걸로 충분하고,
    캐시 키·적중 통계·무효화 정책을 객체 수준에서 바꾸고 싶으면 클래스 프록시가 낫다.
    """
    LOADS.append(f"tile:{tile_id}")
    return tile_id.encode()


if __name__ == "__main__":
    print("[1] __getattr__ 범용 지연 프록시")
    dem = LazyProxy(lambda: DemRaster("N37E127"))
    print(f"    프록시 생성 직후 로딩 기록: {LOADS}")
    print(f"    dem.max_elevation() = {dem.max_elevation()}, 로딩 기록: {LOADS}")
    try:
        len(dem)
    except TypeError as e:
        print(f"    len(dem) → TypeError: {e}  (특수 메서드는 타입에서 찾으므로 위임 안 됨)")
    print(f"    isinstance(dem, DemRaster) = {isinstance(dem, DemRaster)}")
    # == 도 특수 메서드(__eq__)라 위임되지 않는다. 기본 동작(정체성 비교)이 쓰인다.
    print(f"    dem == (실제 객체) → {dem == dem._target()}")

    print("[2] cached_property — 프록시 없이 객체 내부에서 지연")
    LOADS.clear()
    scene = LandCoverScene("LC-2026-09")
    print(f"    생성 직후: {LOADS}, 'raster' in __dict__ = {'raster' in vars(scene)}")
    print(f"    scene.raster → {scene.raster}, 기록: {LOADS}")
    _ = scene.raster
    print(f"    두 번째 접근 후 기록: {LOADS} (다시 로딩하지 않음)")

    print("[3] lru_cache — 캐싱 프록시의 가장 가벼운 형태")
    LOADS.clear()
    for t in ["A", "B", "A", "C", "A", "B"]:
        fetch_tile(t)
    print(f"    요청 A B A C A B → 실제 다운로드: {LOADS}")
    print(f"    {fetch_tile.cache_info()}")

    print("[4] weakref.proxy — 생명주기를 소유하지 않는 프록시")
    real = DemRaster("N35E129")
    weak = weakref.proxy(real)
    print(f"    weak.max_elevation() = {weak.max_elevation()}, len(weak) = {len(weak)} (특수 메서드도 위임)")
    del real
    gc.collect()   # CPython은 참조 카운트로 즉시 회수하지만, 다른 구현을 위해 명시한다
    try:
        weak.max_elevation()
    except ReferenceError as e:
        print(f"    실제 객체 소멸 후 → ReferenceError: {e}")
