"""연습문제 2 해설: 스마트홈 리모컨을 커맨드로 바꾸고 undo 버튼을 추가한다.

상황: 리모컨의 press(button)가 'if button == 1: light.on()' 식으로 기기를 직접 호출했다.
버튼 배치를 사용자가 바꾸고 싶어 하고, '방금 누른 것 취소' 버튼이 필요해졌다.
리모컨(Invoker)이 기기(Receiver)를 모르게 하고, 버튼 슬롯에는 명령 객체를 꽂는다.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Callable


class Light:
    """[Receiver] 조명."""

    def __init__(self) -> None:
        """꺼진 상태로 시작."""
        self.on = False


class Thermostat:
    """[Receiver] 온도 조절기."""

    def __init__(self) -> None:
        """기본 설정 온도."""
        self.target = 22


class Command(ABC):
    """[Command] 버튼에 꽂을 수 있는 동작."""

    @abstractmethod
    def execute(self) -> None:
        """동작 수행 + undo 정보 기록."""

    @abstractmethod
    def undo(self) -> None:
        """직전 execute의 효과를 되돌린다."""


class LightSwitch(Command):
    """[Concrete Command] 조명 켜기/끄기. undo: 이전 상태 스냅샷(토글 역연산보다 안전)."""

    def __init__(self, light: Light, turn_on: bool) -> None:
        """대상 조명과 원하는 상태."""
        self.light, self.turn_on = light, turn_on
        self._prev = False

    def execute(self) -> None:
        """이전 상태를 기억하고 설정. '이미 켜진 조명 켜기'도 정확히 undo된다."""
        self._prev, self.light.on = self.light.on, self.turn_on
        print(f"    조명 {'켜짐' if self.turn_on else '꺼짐'}")

    def undo(self) -> None:
        """이전 상태로."""
        self.light.on = self._prev
        print(f"    (취소) 조명 {'켜짐' if self._prev else '꺼짐'}")


class AdjustTemp(Command):
    """[Concrete Command] 온도 ±. undo: 역연산(하한·상한이 없으므로 안전)."""

    def __init__(self, thermo: Thermostat, delta: int) -> None:
        """대상 기기와 변화량."""
        self.thermo, self.delta = thermo, delta

    def execute(self) -> None:
        """설정 온도 변경."""
        self.thermo.target += self.delta
        print(f"    설정 온도 {self.thermo.target}℃")

    def undo(self) -> None:
        """반대로 변경."""
        self.thermo.target -= self.delta
        print(f"    (취소) 설정 온도 {self.thermo.target}℃")


class Remote:
    """[Invoker] 버튼 슬롯 + 취소 스택. 어떤 기기도 import하지 않는다."""

    def __init__(self) -> None:
        """슬롯 번호 → '명령을 만드는 함수', 실행 이력.

        슬롯에 명령 인스턴스가 아니라 팩토리를 두는 이유: 같은 버튼을 연타하면 같은
        인스턴스가 두 번 execute되어, 스냅샷 명령(LightSwitch)의 _prev가 덮어쓰인다.
        그러면 연타 후 취소 두 번이 원래 상태로 돌아가지 못한다. 누를 때마다 새 명령을
        만들면 이력의 각 항목이 자기만의 되돌리기 정보를 갖는다.
        """
        self.slots: dict[int, Callable[[], Command]] = {}
        self._history: list[Command] = []

    def assign(self, button: int, make: Callable[[], Command]) -> None:
        """버튼 재배치 = 슬롯에 다른 명령 팩토리 꽂기. 리모컨 코드는 바뀌지 않는다."""
        self.slots[button] = make

    def press(self, button: int) -> None:
        """버튼 누름. 빈 슬롯은 조용히 무시(실제 리모컨처럼)."""
        if make := self.slots.get(button):
            cmd = make()          # 누를 때마다 새 명령 — 이력 항목끼리 되돌리기 정보를 공유하지 않는다
            cmd.execute()
            self._history.append(cmd)

    def press_undo(self) -> None:
        """취소 버튼."""
        # 빈 이력에서의 취소는 실제 리모컨처럼 아무 일도 하지 않는다(예외로 사용자를 괴롭히지 않는다).
        if self._history:
            self._history.pop().undo()


if __name__ == "__main__":
    light, thermo, remote = Light(), Thermostat(), Remote()
    remote.assign(1, lambda: LightSwitch(light, True))
    remote.assign(2, lambda: LightSwitch(light, False))
    remote.assign(3, lambda: AdjustTemp(thermo, +1))
    print("[1] 1, 1(연타), 3, 3 버튼")
    for b in (1, 1, 3, 3):
        remote.press(b)
    print("[2] 취소 네 번 — 연타한 켜기까지 정확히 원래(꺼짐)로")
    for _ in range(4):
        remote.press_undo()
    print("[3] 사용자가 1번 버튼을 '온도 -2'로 재배치")
    remote.assign(1, lambda: AdjustTemp(thermo, -2))
    remote.press(1)
