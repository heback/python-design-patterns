"""05 어댑터 — 연습문제 2 해설: isinstance 분기로 두 온도 센서를 다루던 코드를 어댑터로.

상황: 스마트 온실 컨트롤러가 구형 센서(LegacyThermo, 화씨, read_f())와 신형 센서
(NewThermo, 섭씨, get_celsius())를 섞어 쓴다. 원래 코드는 평균 온도를 구할 때
isinstance로 분기해 단위를 바꿨다. 여기서는 Target을 '클라이언트가 원하는 모양'으로
정하고, 그 모양과 다른 쪽에만 어댑터를 단다.

설계 판단: Target 메서드 이름을 신형 센서와 같은 get_celsius()로 정했다. 그러면 신형
센서는 어댑터 없이 그대로 Target이 된다(Protocol의 구조적 타이핑). 어댑터는 '차이가
있는 곳에만' 두는 것이 원칙이다. 반대로 Target 이름을 temperature_c() 같은 새 이름으로
정하면 두 센서 모두 어댑터가 필요해지지만, 앞으로 세 번째 센서가 와도 Target이
특정 벤더에 끌려가지 않는다는 장점이 있다 — 어느 쪽도 정답일 수 있다.
"""
from __future__ import annotations

from typing import Iterable, Protocol


class LegacyThermo:
    """[Adaptee] 구형 센서 라이브러리. 화씨를 돌려준다(수정 불가)."""

    def __init__(self, f: float) -> None:
        """측정값을 고정해 둔 가짜 센서."""
        self._f = f

    def read_f(self) -> float:
        """화씨 온도."""
        return self._f


class NewThermo:
    """신형 센서. 이미 Target 모양(get_celsius)이므로 어댑터가 필요 없다."""

    def __init__(self, c: float) -> None:
        """측정값을 고정해 둔 가짜 센서."""
        self._c = c

    def get_celsius(self) -> float:
        """섭씨 온도."""
        return self._c


class CelsiusSource(Protocol):
    """[Target] 컨트롤러가 기대하는 온도원. 단위는 섭씨로 고정한다.

    '단위'를 인터페이스 계약에 포함시킨 것이 핵심이다. 원래 코드의 버그 가능성은
    대부분 '이 숫자가 무슨 단위냐'에서 나왔다.
    """

    def get_celsius(self) -> float:
        """섭씨 온도를 돌려준다."""
        ...


class LegacyThermoAdapter:
    """[Adapter] 화씨 센서를 CelsiusSource로. 단위 변환 규칙은 오직 여기에만 있다."""

    def __init__(self, sensor: LegacyThermo) -> None:
        """구형 센서를 합성으로 보유한다."""
        self._sensor = sensor

    def get_celsius(self) -> float:
        """화씨 → 섭씨."""
        return (self._sensor.read_f() - 32) * 5 / 9


def average_celsius(sensors: Iterable[CelsiusSource]) -> float:
    """[Client] isinstance 분기가 사라졌다. 센서 종류가 늘어도 이 함수는 그대로다."""
    values = [s.get_celsius() for s in sensors]
    return sum(values) / len(values)


def max_celsius(sensors: Iterable[CelsiusSource]) -> float:
    """[Client] 원래 코드에서 분기가 복제되던 두 번째 함수. 이제 한 줄이다."""
    return max(s.get_celsius() for s in sensors)


if __name__ == "__main__":
    # 조립 지점에서만 '어느 센서가 구형인가'를 안다.
    sensors: list[CelsiusSource] = [
        LegacyThermoAdapter(LegacyThermo(77.0)),  # 25℃
        NewThermo(23.0),
        LegacyThermoAdapter(LegacyThermo(71.6)),  # 22℃
    ]
    print("[1] 센서별 섭씨 값:", [round(s.get_celsius(), 1) for s in sensors])
    print(f"[2] 평균 온도: {average_celsius(sensors):.1f}℃")
    print(f"[3] 최고 온도: {max_celsius(sensors):.1f}℃  (두 클라이언트 모두 isinstance가 사라졌다)")
