"""99 종합 — 닮은 패턴 비교 코드: 같은 모양, 다른 의도(전략 vs 상태, 데코레이터 vs 프록시).

상황: 한빛로지스 로봇 창고 팀의 신입 다온은 리뷰에서 "이건 전략이 아니라 상태예요"라는
지적을 받고 항의했다. "다이어그램이 똑같은데요?" 이 코드는 일부러 같은 모양으로 짠 두 쌍을
나란히 두고, "누가 무엇을 결정하는가" 하나로 가른다.
"""
from __future__ import annotations

from typing import Callable

# ---------- 전략 vs 상태: 로봇의 속도 ----------


def careful(load_kg: int) -> float:
    """[Concrete Strategy] 유리 구역용: 무게와 무관하게 저속."""
    return 0.5


def by_weight(load_kg: int) -> float:
    """[Concrete Strategy] 일반 구역용: 무거울수록 느리게."""
    return max(0.5, 2.0 - load_kg / 50)


class StrategyRobot:
    """[Context — 전략] 규칙을 바깥에서 받는다. 규칙이 언제 바뀌는지 로봇은 모른다."""

    def __init__(self, rule: Callable[[int], float]) -> None:
        """교체 결정권은 이 로봇을 쓰는 쪽(관제 시스템)에 있다."""
        self.rule = rule

    def speed(self, load_kg: int) -> float:
        """위임만 한다. 다음 규칙을 고르는 코드가 이 클래스에 없다."""
        return self.rule(load_kg)


class Normal:
    """[Concrete State] 정상 주행."""

    name = "정상"

    def speed(self, load_kg: int) -> float:
        """무게 기반 속도."""
        return by_weight(load_kg)

    def after_trip(self, battery: int) -> Normal | PowerSave:
        """다음 상태를 '스스로' 고른다 — 전략에는 없는 메서드. 그래서 상태끼리 서로를 안다."""
        return PowerSave() if battery < 30 else self


class PowerSave:
    """[Concrete State] 절전 주행."""

    name = "절전"

    def speed(self, load_kg: int) -> float:
        """절전 중에는 저속."""
        return 0.5

    def after_trip(self, battery: int) -> Normal | PowerSave:
        """충전되면 정상으로 돌아간다."""
        return Normal() if battery >= 60 else self


class StateRobot:
    """[Context — 상태] 같은 위임 구조지만, 교체는 상태 객체가 정한다."""

    def __init__(self) -> None:
        """처음 상태만 정한다."""
        self.mode: Normal | PowerSave = Normal()

    def speed(self, load_kg: int) -> float:
        """위임."""
        return self.mode.speed(load_kg)

    def finish_trip(self, battery: int) -> None:
        """다음 상태를 묻고 갈아 끼운다. '어떤 조건에서 무엇으로'는 상태 객체만 안다."""
        self.mode = self.mode.after_trip(battery)


# ---------- 데코레이터 vs 프록시: 로봇 드라이버 감싸기 ----------


class RealDriver:
    """[Real Subject / Component] 실제 드라이버. 만들 때 로봇과 연결한다(비싸다)."""

    created = 0  # 연결 횟수 — 데모에서 '언제 연결되는가'를 보이려는 카운터

    def __init__(self, robot_id: str) -> None:
        """비싼 연결."""
        RealDriver.created += 1
        self.robot_id = robot_id

    def move(self, cell: str) -> str:
        """칸으로 이동한다."""
        return f"{self.robot_id}->{cell}"


class TimingDriver:
    """[Decorator] 이미 만든 드라이버를 '받아서' 기록 책임을 더한다. 몇 겹이든 쌓을 수 있다."""

    def __init__(self, inner: RealDriver) -> None:
        """감쌀 객체를 바깥에서 받는다 — 만들지 않는다."""
        self.inner = inner
        self.log: list[str] = []

    def move(self, cell: str) -> str:
        """위임하고 기록을 덧붙인다."""
        self.log.append(f"move({cell})")
        return self.inner.move(cell)


class LazyDriver:
    """[Proxy] 실제 드라이버를 '스스로 만들고' 그 시점을 통제한다. 클라이언트는 진짜를 본 적이 없다."""

    def __init__(self, robot_id: str) -> None:
        """ID만 기억하고 연결은 미룬다."""
        self.robot_id = robot_id
        self._real: RealDriver | None = None

    def move(self, cell: str) -> str:
        """첫 호출 때 연결한다. 목적은 책임 추가가 아니라 접근 통제다."""
        if self._real is None:
            self._real = RealDriver(self.robot_id)
        return self._real.move(cell)


if __name__ == "__main__":
    print("[1] 전략: 관제 시스템이 규칙을 갈아 끼운다 (결정 = 바깥)")
    r = StrategyRobot(by_weight)
    print(f"  일반 구역 40kg: {r.speed(40)} m/s")
    r.rule = careful  # 바깥이 직접 교체한다
    print(f"  유리 구역 40kg: {r.speed(40)} m/s")

    print("[2] 상태: 로봇이 배터리를 보고 스스로 모드를 바꾼다 (결정 = 상태 객체)")
    s = StateRobot()
    for battery in (55, 25, 40, 70):
        s.finish_trip(battery)
        print(f"  배터리 {battery:>2}% → {s.mode.name}, 40kg {s.speed(40)} m/s")

    print("[3] 데코레이터: 연결된 드라이버를 받아 감싼다 — 연결은 조립할 때")
    RealDriver.created = 0
    timed = TimingDriver(RealDriver("R-7"))
    print(f"  감싼 직후 연결 수: {RealDriver.created}")
    timed.move("A-03")
    print(f"  기록: {timed.log}")

    print("[4] 프록시: 드라이버를 스스로 만든다 — 연결은 처음 쓸 때")
    RealDriver.created = 0
    lazy = LazyDriver("R-8")
    print(f"  만든 직후 연결 수: {RealDriver.created}")
    lazy.move("B-11")
    lazy.move("B-12")
    print(f"  두 번 이동 뒤 연결 수: {RealDriver.created}")
