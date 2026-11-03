"""09 프록시 — 파이썬다운 변형: 프록시 객체 없이 지연과 캐싱을 얻는 두 도구.

상황: 팀에는 지연 로딩이 필요한 무거운 데이터가 더 있다. 그 클래스를 우리가
직접 만든다면, 바깥에 프록시를 씌우는 대신 (1) cached_property로 객체 안에서 지연시키고,
(2) 함수 하나짜리 캐시라면 lru_cache 한 줄로 캐싱 프록시를 대신할 수 있다.
"""
from __future__ import annotations

from functools import cached_property, lru_cache

LOADS: list[str] = []   # 무거운 로딩이 언제 일어났는지 기록한다(데모가 출력한다)


class LandCoverScene:
    """우리가 설계하는 클래스. 무거운 부분만 첫 접근 때 한 번 만든다."""

    def __init__(self, scene_id: str) -> None:
        """생성은 가볍다. 아무것도 받지 않는다."""
        self.scene_id = scene_id

    @cached_property
    def data(self) -> str:
        """첫 접근 때 한 번 계산해 인스턴스에 저장한다. 이후엔 보통 속성처럼 읽힌다."""
        LOADS.append(self.scene_id)
        return f"<{self.scene_id} 데이터>"


@lru_cache(maxsize=2)
def fetch_tile(tile_id: str) -> str:
    """같은 인자로 다시 부르면 기억해 둔 결과를 돌려준다. 최근 2개까지만 기억한다."""
    LOADS.append(tile_id)
    return f"<{tile_id}>"


if __name__ == "__main__":
    scene = LandCoverScene("LC-01")
    print(f"[1] 만든 직후 로딩 기록: {LOADS}")
    scene.data
    scene.data   # 두 번째 접근은 저장된 값 — 로딩이 다시 일어나지 않는다
    print(f"    data에 두 번 접근한 뒤: {LOADS}")
    LOADS.clear()
    for t in "ABACAB":
        fetch_tile(t)
    # A는 기억에 남아 재사용되고, C가 들어오며 가장 오래 안 쓴 B가 밀려나 마지막 B는 다시 받는다.
    print(f"[2] A B A C A B 요청 → 실제 로딩: {LOADS}, {fetch_tile.cache_info()}")
