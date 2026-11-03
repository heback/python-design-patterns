"""13 상태 — 순진한 코드: 상태 문자열 하나와 메서드마다 붙은 if 분기.

상황: 공유 킥보드 '킥고'의 Scooter는 처음에 대여 가능/주행 중 두 상태뿐이었다.
그 뒤 예약됨·배터리 부족·정비 중이 늘었고, 서진은 메서드마다 분기를 덧붙였다.
상태가 둘이던 시절에 쓴 unlock()의 else가 새 상태를 모두 '허용'으로 삼킨다.
"""
from __future__ import annotations


class Scooter:
    """상태를 문자열로 들고, 동작마다 상태를 묻는다."""

    def __init__(self) -> None:
        """대여 가능으로 시작한다."""
        self.status = "available"
        # ⚠ 문제: 예약 상태에서만 의미 있는 값이 언제나 객체에 붙어 있다.
        self.reserved_by: str | None = None

    def reserve(self, user: str) -> None:
        """대여 가능일 때만 예약한다."""
        if self.status != "available":
            raise ValueError(f"{self.status}: 예약 불가")
        self.status, self.reserved_by = "reserved", user

    def unlock(self, user: str) -> None:
        """잠금을 풀고 주행을 시작한다."""
        if self.status == "riding":
            raise ValueError("이미 주행 중")
        elif self.status == "reserved" and user != self.reserved_by:
            raise ValueError("남의 예약")
        else:
            # ⚠ 문제: 두 상태 시절의 else는 '대여 가능'이라는 뜻이었다.
            # 뒤에 생긴 low_battery·maintenance도 모두 여기로 흘러 들어와 주행이 된다.
            self.status = "riding"

    def end_ride(self, battery: int) -> None:
        """반납한다. 배터리가 낮으면 배터리 부족으로 간다."""
        if self.status != "riding":
            raise ValueError(f"{self.status}: 반납 불가")
        # ⚠ 문제: reserved_by를 지우는 일을 잊었다. 이전 상태의 찌꺼기가 남는다.
        self.status = "low_battery" if battery < 15 else "available"

    def send_to_maintenance(self) -> None:
        """정비 입고. ⚠ 문제: 새 상태를 넣을 때마다 이런 메서드를 전부 다시 열어야 한다."""
        if self.status == "riding":
            raise ValueError("주행 중에는 입고 불가")
        self.status = "maintenance"


if __name__ == "__main__":
    s = Scooter()
    print("[1] 예약 → 잠금 해제 → 반납")
    s.reserve("민지")
    s.unlock("민지")
    s.end_ride(battery=80)
    print(f"    상태={s.status}, 남은 예약자={s.reserved_by}   <- 찌꺼기")

    print("[2] 정비 중인 킥보드를 연다 (사고 재현)")
    s.send_to_maintenance()
    s.unlock("지나가던 사람")      # 예외가 나야 하는데 그대로 통과한다
    print(f"    상태={s.status}   <- 브레이크를 분해해 둔 킥보드가 주행 중")
