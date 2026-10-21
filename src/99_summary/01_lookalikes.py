"""닮은 패턴 구별하기: 같은 클래스 모양, 다른 의도 — 전략 vs 상태, 데코레이터 vs 프록시.

상황: 물류 기업 '한빛로지스'의 로봇 창고 팀 신입 다온은 코드 리뷰에서 두 번 지적을 받았다.
"이건 전략이 아니라 상태예요", "이건 데코레이터가 아니라 프록시예요". 다온은 항의했다.
"클래스 다이어그램이 똑같은데요?" 맞다. 이 파일은 일부러 같은 모양으로 짠 두 쌍을 나란히 두고,
'누가 무엇을 결정하는가'라는 질문 하나로 둘을 가른다.

- 전략 vs 상태(10장·13장): 둘 다 Context가 교체 가능한 객체에 위임한다.
  → 교체를 '바깥(클라이언트)'이 결정하면 전략, '상태 객체 자신'이 결정하면 상태.
- 데코레이터 vs 프록시(6장·9장): 둘 다 같은 인터페이스로 감싸고 위임한다.
  → 감쌀 객체를 '받아서' 책임을 더하면 데코레이터, 실제 객체의 생성·접근을 '소유·통제'하면 프록시.
"""
from __future__ import annotations

from typing import Callable, Protocol


# ===========================================================================
# 1. 전략 vs 상태 — 로봇의 속도 결정
# ===========================================================================

SpeedRule = Callable[[int], float]  # 적재 무게(kg) → 최고 속도(m/s)


def careful(load_kg: int) -> float:
    """[Concrete Strategy] 깨지기 쉬운 상품 구역용: 무게와 무관하게 저속."""
    return 0.5


def by_weight(load_kg: int) -> float:
    """[Concrete Strategy] 일반 구역용: 무거울수록 느리게."""
    return max(0.5, 2.0 - load_kg / 50)


class StrategyRobot:
    """[Context — 전략] 속도 규칙을 '바깥에서' 받는다. 로봇은 규칙이 언제 바뀌는지 모른다."""

    def __init__(self, rule: SpeedRule) -> None:
        """교체 결정권은 이 생성자를 부르는 쪽(관제 시스템)에 있다."""
        self.rule = rule

    def speed(self, load_kg: int) -> float:
        """위임만 한다. 다음 규칙을 고르는 코드는 이 클래스 어디에도 없다."""
        return self.rule(load_kg)


class Mode(Protocol):
    """[State] 상태별 행동 + '다음 상태'를 돌려주는 계약."""

    name: str

    def speed(self, load_kg: int) -> float:
        """이 상태에서의 속도."""
        ...

    def after_trip(self, battery: int) -> Mode:
        """주행을 마친 뒤 다음 상태를 '스스로' 고른다 — 전략에는 없는 메서드."""
        ...


class Normal:
    """[Concrete State] 정상 주행."""

    name = "정상"

    def speed(self, load_kg: int) -> float:
        """무게 기반 속도."""
        return by_weight(load_kg)

    def after_trip(self, battery: int) -> Mode:
        """배터리가 30% 미만이면 절전 모드로 넘어간다. 이 지식이 상태 객체 안에 있다."""
        return PowerSave() if battery < 30 else self


class PowerSave:
    """[Concrete State] 절전 주행."""

    name = "절전"

    def speed(self, load_kg: int) -> float:
        """절전 중에는 저속."""
        return 0.5

    def after_trip(self, battery: int) -> Mode:
        """충전되면 정상으로 돌아간다."""
        return Normal() if battery >= 60 else self


class StateRobot:
    """[Context — 상태] 같은 위임 구조지만, 교체는 상태 객체가 결정한다."""

    def __init__(self) -> None:
        """처음 상태만 정한다. 이후 교체는 바깥이 아니라 after_trip()의 반환값이 한다."""
        self.mode: Mode = Normal()

    def speed(self, load_kg: int) -> float:
        """위임."""
        return self.mode.speed(load_kg)

    def finish_trip(self, battery: int) -> None:
        """다음 상태를 묻고 갈아 끼운다. 로봇은 '어떤 조건에서 무엇으로'를 모른다."""
        self.mode = self.mode.after_trip(battery)


# ===========================================================================
# 2. 데코레이터 vs 프록시 — 로봇 드라이버 감싸기
# ===========================================================================

class Driver(Protocol):
    """[Component / Subject] 로봇 드라이버 인터페이스."""

    def move(self, cell: str) -> str:
        """칸으로 이동한다."""
        ...


class RealDriver:
    """[Concrete Component / Real Subject] 실제 드라이버. 생성 시 로봇과 연결(비싸다)한다."""

    created = 0  # 몇 번 연결했는지 데모에서 보이려는 카운터

    def __init__(self, robot_id: str) -> None:
        """연결 비용이 큰 생성자."""
        RealDriver.created += 1
        self.robot_id = robot_id

    def move(self, cell: str) -> str:
        """이동."""
        return f"{self.robot_id}→{cell}"


class TimingDriver:
    """[Decorator] 이미 만들어진 드라이버를 '받아서' 책임(소요 시간 기록)을 더한다.

    누가 무엇을 감쌀지는 조립 코드가 정한다. 몇 겹이든 쌓을 수 있다.
    """

    def __init__(self, inner: Driver) -> None:
        """감쌀 객체를 바깥에서 받는다 — 생명주기를 소유하지 않는다."""
        self.inner = inner
        self.log: list[str] = []

    def move(self, cell: str) -> str:
        """위임 전후에 책임 하나를 덧붙인다."""
        result = self.inner.move(cell)
        self.log.append(f"move({cell}) 기록")
        return result


class LazyDriver:
    """[Proxy] 실제 드라이버를 '스스로 만들고' 그 시점을 통제한다(가상 프록시).

    클라이언트는 RealDriver 참조를 한 번도 갖지 않는다. 이것이 9장이 말한 «create» 화살표의 차이다.
    """

    def __init__(self, robot_id: str) -> None:
        """로봇 ID만 기억하고 연결은 미룬다."""
        self.robot_id = robot_id
        self._real: RealDriver | None = None

    def move(self, cell: str) -> str:
        """첫 호출 때 연결한다. 접근 통제가 목적이지 책임 추가가 목적이 아니다."""
        if self._real is None:
            self._real = RealDriver(self.robot_id)
        return self._real.move(cell)


if __name__ == "__main__":
    print("[1] 전략: 관제 시스템이 구역에 따라 규칙을 바꾼다 (교체 결정 = 바깥)")
    r = StrategyRobot(by_weight)
    print(f"  일반 구역 40kg: {r.speed(40)} m/s")
    r.rule = careful  # 클라이언트가 직접 교체
    print(f"  유리 구역 40kg: {r.speed(40)} m/s")

    print("\n[2] 상태: 로봇이 배터리에 따라 스스로 모드를 바꾼다 (교체 결정 = 상태 객체)")
    s = StateRobot()
    for battery in (55, 25, 40, 70):
        s.finish_trip(battery)
        print(f"  주행 후 배터리 {battery:>2}% → 모드 {s.mode.name}, 40kg 속도 {s.speed(40)} m/s")

    print("\n[3] 데코레이터: 이미 연결된 드라이버를 받아 감싼다 — 연결은 조립 시점에 일어남")
    RealDriver.created = 0
    timed = TimingDriver(RealDriver("R-7"))
    print(f"  감싼 직후 연결 수: {RealDriver.created}")
    timed.move("A-03")
    print(f"  {timed.log}")

    print("\n[4] 프록시: 실제 드라이버를 스스로 만든다 — 연결은 첫 사용 시점")
    RealDriver.created = 0
    lazy = LazyDriver("R-8")
    print(f"  프록시 생성 직후 연결 수: {RealDriver.created}")
    lazy.move("B-11")
    lazy.move("B-12")
    print(f"  두 번 이동한 뒤 연결 수: {RealDriver.created}")
