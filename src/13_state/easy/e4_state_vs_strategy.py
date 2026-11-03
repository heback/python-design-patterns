"""13 상태 — 전략·상태 비교 코드: 한 Scooter 안의 두 슬롯.

상황: 킥고 운영팀은 시간대마다 요금 정책을 바꾼다. 요금 정책은 바깥(운영 콘솔)이 갈아 끼우는
전략 슬롯이고, 대여 단계는 사건에 반응해 상태 객체가 스스로 바꾸는 상태 슬롯이다.
두 슬롯의 '교체 경로'가 어떻게 다른지 비교한다.
"""
from __future__ import annotations

from typing import Callable

Pricing = Callable[[int], int]   # [Strategy] 주행 분 -> 요금. 메서드 하나라 함수로 충분하다


def day_rate(minutes: int) -> int:
    """[Concrete Strategy] 주간 요금."""
    return 1000 + 150 * minutes


def night_rate(minutes: int) -> int:
    """[Concrete Strategy] 야간 할증 요금."""
    return 1000 + 250 * minutes


class Available:
    """[Concrete State] 대여 가능. 잠금 해제되면 스스로 Riding을 고른다."""
    label = "대여 가능"

    def unlock(self, scooter: Scooter) -> None:
        """출발하는 순간의 요금 정책을 Riding에 붙잡아 둔다."""
        scooter.change_state(Riding(scooter.pricing))


class Riding:
    """[Concrete State] 주행 중. 출발 때의 정책을 들고 있어, 도중에 정책이 바뀌어도 소급되지 않는다."""
    label = "주행 중"

    def __init__(self, pricing: Pricing) -> None:
        """이 상태에서만 의미 있는 데이터: 계약된 요금 정책."""
        self.pricing = pricing

    def end_ride(self, scooter: Scooter, minutes: int) -> None:
        """요금을 계산하고 스스로 Available로 돌아간다."""
        print(f"    요금 {self.pricing(minutes)}원")
        scooter.change_state(Available())


class Scooter:
    """[Context] 전략 슬롯(pricing)과 상태 슬롯(_state)을 함께 가진다."""

    def __init__(self) -> None:
        """주간 요금, 대여 가능으로 시작한다."""
        self.pricing: Pricing = day_rate
        self._state: Available | Riding = Available()

    def set_pricing(self, pricing: Pricing) -> None:
        """전략 교체: 바깥(운영 콘솔)이 부른다. 아무 정책으로나 바꿔도 된다."""
        print(f"    (운영) 요금 정책 -> {pricing.__name__}")
        self.pricing = pricing

    def change_state(self, new: Available | Riding) -> None:
        """상태 교체: 상태 객체만 부른다. 허용된 전이만 일어난다."""
        print(f"    {self._state.label} -> {new.label}")
        self._state = new

    # 위임. (이 비교 코드는 상태가 둘뿐이라 '기본은 거부' 기반 클래스를 생략했다.)
    def unlock(self) -> None:
        """현재 상태에 맡긴다."""
        self._state.unlock(self)  # type: ignore[union-attr]

    def end_ride(self, minutes: int) -> None:
        """현재 상태에 맡긴다."""
        self._state.end_ride(self, minutes)  # type: ignore[union-attr]


if __name__ == "__main__":
    s = Scooter()
    print("[1] 주간에 출발 → 주행 중 야간 정책으로 교체 → 10분 뒤 반납")
    s.unlock()
    s.set_pricing(night_rate)
    s.end_ride(minutes=10)    # 출발 때 붙잡은 주간 요금(2500원)으로 계산된다
