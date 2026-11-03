"""13 상태 — 패턴 코드: 상태마다 클래스 하나, 기본은 '거부'.

상황: 서진은 Scooter의 if 분기를 상태 클래스로 나눈다. Scooter(Context)는 위임만 하고,
상태 객체가 허용 여부와 다음 상태를 스스로 정한다.
"""
from __future__ import annotations


class IllegalTransition(Exception):
    """현재 상태에서 허용되지 않는 동작."""


class ScooterState:
    """[State] 기본 구현이 모두 거부다. 깜빡 잊은 동작은 '허용'이 아니라 '거부'가 된다."""
    label = "?"   # 앱 표시 문구. 구체 상태가 클래스 속성으로 덮어쓴다.

    def reserve(self, scooter: Scooter, user: str) -> None:
        """기본: 거부."""
        raise IllegalTransition(f"[{self.label}] 예약 불가")

    def unlock(self, scooter: Scooter, user: str) -> None:
        """기본: 거부. 순진한 코드의 else('허용')와 정반대다."""
        raise IllegalTransition(f"[{self.label}] 잠금 해제 불가")

    def end_ride(self, scooter: Scooter) -> None:
        """기본: 거부."""
        raise IllegalTransition(f"[{self.label}] 반납 불가")

    def send_to_maintenance(self, scooter: Scooter) -> None:
        """기본: 거부."""
        raise IllegalTransition(f"[{self.label}] 정비 입고 불가")


class Available(ScooterState):
    """[Concrete State] 대여 가능. 다음 상태를 이 클래스가 직접 고른다."""
    label = "대여 가능"

    def reserve(self, scooter: Scooter, user: str) -> None:
        """예약자는 Scooter가 아니라 Reserved 객체에 담긴다."""
        scooter.change_state(Reserved(user))

    def unlock(self, scooter: Scooter, user: str) -> None:
        """바로 주행."""
        scooter.change_state(Riding())


class Reserved(ScooterState):
    """[Concrete State] 예약됨. 예약자 데이터는 이 객체와 함께 생기고 함께 사라진다."""
    label = "예약됨"

    def __init__(self, user: str) -> None:
        """이 상태에서만 의미 있는 데이터를 받는다."""
        self.user = user

    def unlock(self, scooter: Scooter, user: str) -> None:
        """가드 조건: 예약자 본인일 때만 주행으로 간다."""
        if user != self.user:
            raise IllegalTransition(f"{self.user}님이 예약한 킥보드")
        scooter.change_state(Riding())


class Riding(ScooterState):
    """[Concrete State] 주행 중. 반납 뒤 어디로 갈지(조건부 전이)를 스스로 안다."""
    label = "주행 중"

    def end_ride(self, scooter: Scooter) -> None:
        """배터리에 따라 두 이웃 상태 중 하나를 고른다."""
        scooter.change_state(LowBattery() if scooter.battery < 15 else Available())


class LowBattery(ScooterState):
    """[Concrete State] 배터리 부족. 허용되는 것은 정비 입고뿐이다."""
    label = "배터리 부족"

    def send_to_maintenance(self, scooter: Scooter) -> None:
        """충전·정비하러 간다."""
        scooter.change_state(Maintenance())


class Maintenance(ScooterState):
    """[Concrete State] 정비 중. unlock()을 재정의하지 않았다 — 이것이 사고의 해답이다."""
    label = "정비 중"


class Scooter:
    """[Context] 상태를 묻지 않고 위임만 한다. 상태가 늘어도 이 클래스는 그대로다(OCP)."""

    def __init__(self, battery: int = 100) -> None:
        """대여 가능으로 시작한다."""
        self.battery = battery
        self._state: ScooterState = Available()

    def change_state(self, new: ScooterState) -> None:
        """모든 전이가 지나는 관문(상태 객체만 부른다). 기록·알림을 붙일 자리도 여기 하나다."""
        print(f"    {self._state.label} -> {new.label}")
        self._state = new

    def reserve(self, user: str) -> None:
        """위임. 상태를 묻는 if가 하나도 없다."""
        self._state.reserve(self, user)

    def unlock(self, user: str) -> None:
        """위임."""
        self._state.unlock(self, user)

    def end_ride(self) -> None:
        """위임."""
        self._state.end_ride(self)

    def send_to_maintenance(self) -> None:
        """위임."""
        self._state.send_to_maintenance(self)


if __name__ == "__main__":
    s, other = Scooter(battery=10), Scooter()
    print("[1] 예약 → 잠금 해제 → 방전 반납 → 정비 입고")
    s.reserve("민지")
    s.unlock("민지")
    s.end_ride()
    s.send_to_maintenance()
    print("[2] 정비 중 잠금 해제, 남의 예약 가로채기 — 모두 거부된다")
    other.reserve("민지")
    for scooter, user in ((s, "지나가던 사람"), (other, "도윤")):
        try:
            scooter.unlock(user)
        except IllegalTransition as e:
            print(f"    거부: {e}")
