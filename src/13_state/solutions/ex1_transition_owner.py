"""[13장 연습문제 1 해설] 전이를 누가 결정하는가 — 분산(상태 객체) vs 집중(전이표)의 결합도 비교.

상황: 킥고에 '재배치 중(Relocating)' 상태가 추가된다. 배터리 부족 킥보드를 트럭이 수거해
충전소로 옮기는 동안의 상태다. LowBattery → Relocating → Available 경로가 생긴다.

같은 세 상태 기계를 두 방식으로 만들고, 새 상태를 추가할 때 '누구를 고쳐야 하는가'와
'상태 클래스들이 서로를 얼마나 아는가'를 코드로 측정한다. 측정에는 함수의 바이트코드가
참조하는 전역 이름(`__code__.co_names`)을 쓴다 — 정적 분석기 없이 의존을 보는 가벼운 방법이다.
"""
from __future__ import annotations

from enum import Enum


class IllegalTransition(Exception):
    """불법 전이."""


# ---------------------------------------------------------------------------
# 방식 1: 분산 — 상태 객체가 다음 상태를 직접 만든다 (GoF 기본형, 02_state.py)
# ---------------------------------------------------------------------------

class State:
    """[State] 기본은 거부. 새 사건(relocate)이 생기면 이 기본 클래스에도 메서드가 늘어난다."""

    def end_ride(self, ctx: Ctx) -> None:
        """반납."""
        raise IllegalTransition(type(self).__name__)

    def relocate(self, ctx: Ctx) -> None:
        """[추가됨] 재배치 시작 — 새 상태 하나 때문에 기본 클래스가 바뀌었다."""
        raise IllegalTransition(type(self).__name__)

    def arrive(self, ctx: Ctx) -> None:
        """[추가됨] 충전소 도착."""
        raise IllegalTransition(type(self).__name__)


class Riding(State):
    """[Concrete State] 후속 상태 두 개(Available, LowBattery)를 이름으로 안다."""

    def end_ride(self, ctx: Ctx) -> None:
        """배터리에 따라 다음 상태를 고른다."""
        ctx.state = LowBattery() if ctx.battery < 15 else Available()


class Available(State):
    """[Concrete State] 이 예제에서는 반납의 도착점일 뿐이다."""


class LowBattery(State):
    """[Concrete State] [수정됨] 재배치로 가는 출구가 생겨 이 클래스도 고쳐야 했다."""

    def relocate(self, ctx: Ctx) -> None:
        """새 상태 Relocating을 안다 — 새 상태의 '이웃'이 수정 대상이 된다."""
        ctx.state = Relocating()


class Relocating(State):
    """[Concrete State] [추가됨] 도착하면 충전 완료로 보고 Available."""

    def arrive(self, ctx: Ctx) -> None:
        """충전소 도착."""
        ctx.battery = 100
        ctx.state = Available()


class Ctx:
    """[Context] 축약판이라 위임 메서드를 생략하고 데모가 ctx.state.xxx(ctx)를 직접 부른다.

    실제 Context(02의 Scooter)라면 새 사건마다 위임 메서드가 하나씩 는다(relocate, arrive).
    """

    def __init__(self, battery: int) -> None:
        """주행 중으로 시작(예제 단순화)."""
        self.battery = battery
        self.state: State = Riding()


# ---------------------------------------------------------------------------
# 방식 2: 집중 — 상태는 Enum 값, 전이 결정은 Context의 표
# ---------------------------------------------------------------------------

class St(Enum):
    """상태 이름. [추가됨] RELOCATING 한 줄."""

    RIDING = "주행 중"
    AVAILABLE = "대여 가능"
    LOW_BATTERY = "배터리 부족"
    RELOCATING = "재배치 중"


TABLE: dict[tuple[St, str], St] = {
    (St.LOW_BATTERY, "relocate"): St.RELOCATING,   # [추가됨]
    (St.RELOCATING, "arrive"): St.AVAILABLE,       # [추가됨]
}


class TableCtx:
    """[Context + 전이 책임자] 수정은 Enum 한 줄 + 표 두 줄로 끝났다. 다른 '상태'는 아무것도 몰랐다."""

    def __init__(self, battery: int) -> None:
        """주행 중으로 시작."""
        self.battery = battery
        self.state = St.RIDING

    def end_ride(self) -> None:
        """조건부 전이는 표에 못 넣으므로 Context의 코드로 남는다(방식 2의 비용)."""
        if self.state is not St.RIDING:
            raise IllegalTransition(self.state.value)
        self.state = St.LOW_BATTERY if self.battery < 15 else St.AVAILABLE

    def fire(self, event: str) -> None:
        """표로 표현 가능한 전이는 전부 이 한 메서드가 처리한다."""
        try:
            self.state = TABLE[(self.state, event)]
        except KeyError:
            raise IllegalTransition(f"{self.state.value}: {event}") from None
        if self.state is St.AVAILABLE and event == "arrive":
            self.battery = 100   # 진입 동작도 Context가 맡는다 — 행동이 다시 모이는 모습


def state_dependencies() -> dict[str, list[str]]:
    """방식 1에서 각 상태 클래스가 '이름으로 참조하는' 다른 상태 클래스 목록."""
    names = {"Riding", "Available", "LowBattery", "Relocating"}
    deps: dict[str, list[str]] = {}
    for cls in (Riding, Available, LowBattery, Relocating):
        refs: set[str] = set()
        for attr in vars(cls).values():
            code = getattr(attr, "__code__", None)
            if code is not None:
                refs |= set(code.co_names) & names
        deps[cls.__name__] = sorted(refs - {cls.__name__})
    return deps


if __name__ == "__main__":
    print("[1] 두 방식 모두 같은 시나리오를 통과한다: 방전 반납 → 재배치 → 도착")
    c = Ctx(battery=9)
    c.state.end_ride(c)
    c.state.relocate(c)
    c.state.arrive(c)
    t = TableCtx(battery=9)
    t.end_ride()
    t.fire("relocate")
    t.fire("arrive")
    print(f"    분산: {type(c.state).__name__}, 배터리 {c.battery} / 집중: {t.state.name}, 배터리 {t.battery}")

    print("[2] 분산 방식: 상태 클래스 사이의 이름 의존(그래프의 간선 = 결합)")
    for name, refs in state_dependencies().items():
        print(f"    {name:<11} → {refs or '-'}")

    print("[3] Relocating 추가 시 수정해야 했던 곳")
    print("    분산: State(기본 메서드 2개) + LowBattery(출구) + Relocating(신규) + Context(위임 2개, 축약판에선 생략)")
    print("    집중: St(1줄) + TABLE(2줄) — 다른 상태는 수정 없음. 단, 진입 동작이 Context로 왔다")
