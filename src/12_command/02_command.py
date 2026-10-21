"""커맨드 패턴 적용: 편집 동작을 '실행·취소할 수 있는 객체'로 만든다.

상황: 01_naive.py에서 은우의 편집기는 동작 코드가 UI 핸들러 세 곳에 복제되고, undo
정보가 형식 없는 튜플 하나에 제각각 기록되었다. 은우는 '무엇을 할지'(요청)를 객체로
만들어, '언제·어디서 호출하는지'(툴바·단축키·메뉴)와 분리한다.

  - Canvas                                [Receiver]  실제 작업을 아는 쪽(도형 저장소)
  - Command(ABC)                          [Command]   execute()/undo() 계약
  - MoveShape, ChangeColor, DeleteShape   [Concrete Command] 요청 + 되돌리기 정보
  - MacroCommand                          [Concrete Command + Composite] 여러 명령을 하나로
  - CommandHistory                        [Invoker]   실행 기록, undo/redo 스택
  - Toolbar/단축키/메뉴 함수                  [Client]    명령을 만들어 Invoker에 건넨다

undo 정보 보존 방식: 이 파일의 세 명령은 모두 '스냅샷'이다(MoveShape는 좌표, ChangeColor는 색,
DeleteShape는 도형+z-순서). 역연산(−dx)이 왜 실패하는지는 MoveShape docstring과 01의 [1]을 보라.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class Shape:
    """캔버스 위의 도형 하나."""

    id: str
    x: int
    y: int
    color: str = "black"


class Canvas:
    """[Receiver] 도형을 보관하고 조작하는 법을 안다. undo·UI·이력은 전혀 모른다.

    '0에서 자르기' 같은 도메인 규칙이 여기 한 곳에만 있다. naive 코드에서 단축키
    핸들러가 이 규칙을 빠뜨린 것은 규칙이 핸들러마다 복제되어 있었기 때문이다.
    """

    def __init__(self) -> None:
        """id → 도형. dict는 삽입 순서를 유지하므로 순서(그리기 순서)도 의미가 있다."""
        self.shapes: dict[str, Shape] = {}

    def add(self, shape: Shape, index: int | None = None) -> None:
        """도형 추가. index를 주면 그 위치(z-순서)에 끼워 넣는다 — 삭제 취소용."""
        items = list(self.shapes.items())
        items.insert(len(items) if index is None else index, (shape.id, shape))
        self.shapes = dict(items)

    def remove(self, shape_id: str) -> tuple[Shape, int]:
        """도형 제거. 되돌리기에 필요한 '원래 위치'를 함께 돌려준다."""
        index = list(self.shapes).index(shape_id)
        return self.shapes.pop(shape_id), index

    def move_to(self, shape_id: str, x: int, y: int) -> None:
        """절대 위치로 이동. 캔버스 밖(음수)으로는 나가지 않는다."""
        s = self.shapes[shape_id]
        s.x, s.y = max(0, x), max(0, y)

    def set_color(self, shape_id: str, color: str) -> str:
        """색 변경. 이전 색을 돌려준다 — 명령이 도형 내부를 직접 만지지 않고도 undo 정보를 얻게."""
        s = self.shapes[shape_id]
        prev, s.color = s.color, color
        return prev

    def dump(self) -> str:
        """현재 상태 문자열."""
        return ", ".join(f"{s.id}({s.x},{s.y},{s.color})" for s in self.shapes.values()) or "(빈 캔버스)"


class Command(ABC):
    """[Command] '실행할 수 있고 되돌릴 수 있는 요청'의 계약.

    Protocol이 아니라 ABC인 이유: undo()를 빠뜨린 명령이 이력 스택에 들어가면
    Ctrl+Z 시점에야 터진다. 인스턴스화 시점에 잡아내는 편이 낫다.
    """

    @abstractmethod
    def execute(self) -> None:
        """요청을 수행하고, undo에 필요한 정보를 이 객체 안에 남긴다."""

    @abstractmethod
    def undo(self) -> None:
        """execute()의 효과를 정확히 되돌린다. execute() 이후에만 호출된다."""

    @property
    def label(self) -> str:
        """메뉴의 '실행 취소: ○○' 표시용 이름."""
        return type(self).__name__


class MoveShape(Command):
    """[Concrete Command] 상대 이동. undo 방식: 바뀌는 필드(좌표)의 스냅샷.

    주의: 이름만 보면 역연산(−dx)이 자연스럽지만, Canvas가 0에서 자르므로 요청(-30)과
    실제 변화(-10)가 다를 수 있다. 역연산은 이런 정보 손실 앞에서 틀린다 — naive 코드의
    undo가 틀린 이유다. 그래서 execute() 때 이전 좌표를 기억한다(스냅샷).
    """

    def __init__(self, canvas: Canvas, shape_id: str, dx: int, dy: int) -> None:
        """수신자와 요청 매개변수를 보관한다. 생성 시점에는 아무것도 바꾸지 않는다."""
        self.canvas, self.shape_id, self.dx, self.dy = canvas, shape_id, dx, dy
        self._before: tuple[int, int] | None = None

    def execute(self) -> None:
        """이전 좌표를 기억한 뒤 이동."""
        s = self.canvas.shapes[self.shape_id]
        self._before = (s.x, s.y)
        self.canvas.move_to(self.shape_id, s.x + self.dx, s.y + self.dy)

    def undo(self) -> None:
        """기억해 둔 좌표로 복귀. 자르기가 일어났어도 정확하다."""
        assert self._before is not None, "execute() 전에 undo() 호출"
        self.canvas.move_to(self.shape_id, *self._before)

    @property
    def label(self) -> str:
        """메뉴 표시용."""
        return f"{self.shape_id} 이동({self.dx:+},{self.dy:+})"


class ChangeColor(Command):
    """[Concrete Command] 색 변경. undo 방식: 바뀌는 필드 하나의 스냅샷."""

    def __init__(self, canvas: Canvas, shape_id: str, color: str) -> None:
        """새 색만 받는다. 이전 색은 execute() 시점에 읽어야 정확하다(생성 후 다른 명령이 끼어들 수 있으므로)."""
        self.canvas, self.shape_id, self.color = canvas, shape_id, color
        self._prev: str | None = None

    def execute(self) -> None:
        """수신자 API로 변경하고, 돌려받은 이전 색을 저장한다(수신자를 우회하지 않는다)."""
        self._prev = self.canvas.set_color(self.shape_id, self.color)

    def undo(self) -> None:
        """이전 색 복원."""
        assert self._prev is not None
        self.canvas.set_color(self.shape_id, self._prev)

    @property
    def label(self) -> str:
        """메뉴 표시용."""
        return f"{self.shape_id} 색→{self.color}"


class DeleteShape(Command):
    """[Concrete Command] 삭제. undo 방식: 도형 객체 전체 + z-순서 스냅샷.

    삭제에는 역연산이 없다(무엇을 되살릴지 정보가 사라지므로). 사라질 것을 통째로
    붙잡아 두는 수밖에 없다. 도형이 크면(이미지 등) 이 방식은 메모리를 쓴다.
    """

    def __init__(self, canvas: Canvas, shape_id: str) -> None:
        """삭제 대상만 받는다."""
        self.canvas, self.shape_id = canvas, shape_id
        self._removed: tuple[Shape, int] | None = None

    def execute(self) -> None:
        """제거하면서 도형과 위치를 보관."""
        self._removed = self.canvas.remove(self.shape_id)

    def undo(self) -> None:
        """같은 z-순서 위치에 되살린다."""
        assert self._removed is not None
        shape, index = self._removed
        self.canvas.add(shape, index)

    @property
    def label(self) -> str:
        """메뉴 표시용."""
        return f"{self.shape_id} 삭제"


class MacroCommand(Command):
    """[Concrete Command / Composite] 여러 명령을 하나의 명령처럼.

    MacroCommand도 Command이므로 이력 입장에서는 '명령 하나'다 — undo 한 번에
    통째로 되돌아간다(07장 컴포지트와 같은 구조). undo는 '역순'이어야 한다:
    이동 후 삭제한 것을 되돌리려면 삭제부터 취소해야 이동 취소가 대상을 찾을 수 있다.
    """

    def __init__(self, name: str, commands: list[Command]) -> None:
        """하위 명령 목록. 리스트를 복사해 바깥에서의 변경에 영향받지 않게 한다."""
        self.name, self.commands = name, list(commands)

    def execute(self) -> None:
        """순서대로 실행. 중간 단계가 실패하면 이미 실행한 단계를 역순으로 되돌리고 예외를 다시 던진다.

        롤백이 없으면 앞 단계의 변경만 남고, 매크로는 이력에 들어가지 않아(History.execute가
        예외로 중단되므로) 사용자가 Ctrl+Z로 되돌릴 수도 없는 '반쯤 적용된' 상태가 된다.
        """
        done: list[Command] = []
        try:
            for c in self.commands:
                c.execute()
                done.append(c)
        except Exception:
            for c in reversed(done):
                c.undo()
            raise

    def undo(self) -> None:
        """역순으로 취소."""
        for c in reversed(self.commands):
            c.undo()

    @property
    def label(self) -> str:
        """메뉴 표시용."""
        return f"매크로[{self.name}]"


class CommandHistory:
    """[Invoker] 명령을 실행하고 이력을 관리한다. 명령의 '종류'는 전혀 모른다.

    naive 코드의 on_undo()가 동작 종류마다 분기했던 것과 대조하라. 여기서는
    cmd.undo() 한 줄이다 — 되돌리는 법은 각 명령이 안다(캡슐화).
    """

    def __init__(self) -> None:
        """undo 스택과 redo 스택."""
        self._undo: list[Command] = []
        self._redo: list[Command] = []

    def execute(self, cmd: Command) -> None:
        """실행 후 기록. 새 동작이 들어오면 redo 스택은 무효가 된다(분기된 미래는 버린다)."""
        cmd.execute()
        self._undo.append(cmd)
        self._redo.clear()

    def undo(self) -> None:
        """가장 최근 명령 취소 → redo 스택으로."""
        if not self._undo:
            print("    (되돌릴 동작 없음)")
            return
        cmd = self._undo.pop()
        cmd.undo()
        self._redo.append(cmd)
        print(f"    실행 취소: {cmd.label}")

    def redo(self) -> None:
        """취소했던 명령 재실행 → undo 스택으로. execute()를 다시 부르므로 스냅샷도 새로 뜬다."""
        if not self._redo:
            print("    (다시 실행할 동작 없음)")
            return
        cmd = self._redo.pop()
        cmd.execute()
        self._undo.append(cmd)
        print(f"    다시 실행: {cmd.label}")


# ---------------------------------------------------------------------------
# [Client] UI 진입점들 — 세 곳 모두 '명령을 만들어 Invoker에 넘길' 뿐이다
# ---------------------------------------------------------------------------
def toolbar_move(history: CommandHistory, canvas: Canvas, shape_id: str, dx: int, dy: int) -> None:
    """툴바 '이동' 버튼."""
    history.execute(MoveShape(canvas, shape_id, dx, dy))


def shortcut_arrow_key(history: CommandHistory, canvas: Canvas, shape_id: str, key: str) -> None:
    """화살표 키. 키 → 이동량 변환만 하고 동작 자체는 툴바와 같은 명령을 쓴다(복제 없음)."""
    dx, dy = {"left": (-10, 0), "right": (10, 0), "up": (0, -10), "down": (0, 10)}[key]
    history.execute(MoveShape(canvas, shape_id, dx, dy))


def context_menu_delete(history: CommandHistory, canvas: Canvas, shape_id: str) -> None:
    """우클릭 '삭제'. undo 기록을 '잊을' 방법이 없다 — 이력은 Invoker가 일괄 관리한다."""
    history.execute(DeleteShape(canvas, shape_id))


if __name__ == "__main__":
    canvas, history = Canvas(), CommandHistory()
    canvas.add(Shape("box", 10, 10))
    canvas.add(Shape("arrow", 50, 20))
    print("[0] 시작        :", canvas.dump())

    print("[1] 툴바로 box (-30,0) 이동(0에서 잘림) 후 Ctrl+Z — 정확히 x=10으로")
    toolbar_move(history, canvas, "box", -30, 0)
    print("    이동 후     :", canvas.dump())
    history.undo()
    print("    결과        :", canvas.dump())

    print("[2] 단축키로 arrow를 왼쪽 6번 — 같은 명령이라 캔버스 밖으로 나가지 않는다")
    for _ in range(6):
        shortcut_arrow_key(history, canvas, "arrow", "left")
    print("    결과        :", canvas.dump())

    print("[3] 색 변경 두 번 후 Ctrl+Z 두 번 → black까지 되돌아간다")
    history.execute(ChangeColor(canvas, "box", "red"))
    history.execute(ChangeColor(canvas, "box", "blue"))
    history.undo()
    history.undo()
    print("    결과        :", canvas.dump())

    print("[4] 우클릭 삭제 후 Ctrl+Z → 같은 z-순서 자리에 복원, Ctrl+Y로 재삭제")
    context_menu_delete(history, canvas, "box")
    print("    삭제 후     :", canvas.dump())
    history.undo()
    print("    복원        :", canvas.dump())
    history.redo()
    print("    다시 실행   :", canvas.dump())
    history.undo()

    print("[5] 매크로 '강조하기' = 오른쪽 이동 + 빨간색 → undo 한 번에 통째로")
    history.execute(MacroCommand("강조하기", [MoveShape(canvas, "box", 20, 0),
                                              ChangeColor(canvas, "box", "red")]))
    print("    실행 후     :", canvas.dump())
    history.undo()
    print("    결과        :", canvas.dump())

    print("[6] 중간 단계가 실패하는 매크로 — 앞 단계(이동)가 롤백되어 반쯤 적용된 상태가 남지 않는다")
    try:
        history.execute(MacroCommand("망가진 매크로", [MoveShape(canvas, "box", 50, 0),
                                                      DeleteShape(canvas, "ghost")]))
    except ValueError as e:   # Canvas.remove()의 list.index가 없는 id에 ValueError를 낸다
        print("    실패        :", e)
    print("    결과        :", canvas.dump())
