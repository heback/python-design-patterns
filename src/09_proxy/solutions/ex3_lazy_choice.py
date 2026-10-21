"""09 프록시 — 연습문제 3 해설: 대용량 객체 지연 로딩의 세 가지 선택지를 나란히.

상황: 위성 영상 뷰어 팀은 새 객체 HyperspectralCube(초분광 영상, 수 GB)를 들인다.
지연 로딩 방법 후보는 (A) 가상 프록시, (B) 객체 내부의 cached_property, (C) 팩토리에서
지연 생성(필요해질 때 만드는 함수/thunk를 넘김). 이 파일은 셋을 같은 시나리오로 실행해
'누가 객체를 만드는가, 클라이언트가 무엇을 알아야 하는가'의 차이를 드러낸다.
"""
from __future__ import annotations

from functools import cached_property
from typing import Callable

LOADS: list[str] = []


class ExternalCube:
    """외부 라이브러리의 큐브(수정 불가). 생성자에서 로딩한다."""

    def __init__(self, cube_id: str) -> None:
        """로딩 기록."""
        LOADS.append(cube_id)
        self.cube_id = cube_id

    def band(self, n: int) -> str:
        """n번 밴드."""
        return f"{self.cube_id}:band{n}"


class LazyCubeProxy:
    """(A) [Proxy: 가상] 외부 클래스를 고칠 수 없을 때. 클라이언트는 Cube와 같은 인터페이스로 쓴다."""

    def __init__(self, cube_id: str) -> None:
        """재료만 보관."""
        self.cube_id = cube_id
        self._real: ExternalCube | None = None

    def band(self, n: int) -> str:
        """첫 호출에 생성."""
        if self._real is None:
            self._real = ExternalCube(self.cube_id)
        return self._real.band(n)


class OwnCube:
    """(B) 우리 클래스라면: 무거운 부분만 cached_property로. 프록시 계층이 아예 필요 없다."""

    def __init__(self, cube_id: str) -> None:
        """가벼운 정보만."""
        self.cube_id = cube_id

    @cached_property
    def _data(self) -> str:
        """첫 접근 때 로딩."""
        LOADS.append(self.cube_id)
        return self.cube_id

    def band(self, n: int) -> str:
        """필요할 때 _data 접근."""
        return f"{self._data}:band{n}"


def analyze(get_cube: Callable[[], ExternalCube], need: bool) -> str:
    """(C) 팩토리 지연: 클라이언트가 '만드는 법'을 받아 필요할 때 직접 호출한다.

    가장 단순하지만, 클라이언트가 지연 사실을 알아야 한다(타입이 Cube가 아니라 Callable).
    여러 곳에서 같은 큐브를 쓰면 각자 만들 위험도 있다.
    """
    return get_cube().band(3) if need else "건너뜀"


if __name__ == "__main__":
    # 생성과 사용을 분리해 출력한다: '생성 시점에는 로딩이 없다'가 지연의 핵심이기 때문이다.
    proxy = LazyCubeProxy("HSI-A")
    print("[A] 가상 프록시 생성 직후 로딩:", LOADS)
    print("    band(3) →", proxy.band(3), "| 로딩:", LOADS)
    LOADS.clear()
    own = OwnCube("HSI-B")
    print("[B] cached_property 객체 생성 직후 로딩:", LOADS)
    print("    band(3) →", own.band(3), "| 로딩:", LOADS)
    LOADS.clear()
    print("[C] 팩토리 지연(불필요):", analyze(lambda: ExternalCube("HSI-C"), need=False), "| 로딩:", LOADS)
    print("[C] 팩토리 지연(필요):", analyze(lambda: ExternalCube("HSI-C"), need=True), "| 로딩:", LOADS)
