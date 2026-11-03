"""12 커맨드 — 패턴 코드: 요청을 명령 객체로 만들어 쌓고 되돌린다.

상황: 은우는 책임을 셋으로 나눴다. 도형을 어떻게 옮기는지는 Canvas가, 무엇을 했고
어떻게 되돌리는지는 명령 객체가, 무엇을 되돌릴 차례인지는 CommandHistory가 안다.
툴바·화살표 키·우클릭은 같은 명령을 만들어 건네기만 한다.
"""
from abc import ABC, abstractmethod

class Canvas:
    """[Receiver] 실제 작업을 안다. 명령도 이력도 모른다."""

    def __init__(self) -> None:
        """도형 id -> 가로 위치 x."""
        self.shapes = {"box": 20, "arrow": 50}

    def move_to(self, sid: str, x: int) -> None:
        """0에서 자르는 규칙이 여기 한 곳에만 있다. 어느 명령도 이 규칙을 건너뛰지 못한다."""
        self.shapes[sid] = max(0, x)

    def remove(self, sid: str) -> int:
        """지우고, 되돌리기에 필요한 x를 돌려준다. 수신자는 undo를 몰라도 그 재료는 내준다."""
        return self.shapes.pop(sid)

class Command(ABC):
    """[Command] 실행과 되돌리기의 약속. 이력은 이 타입만 안다."""
    @abstractmethod
    def execute(self) -> None:
        """실행하면서 되돌리기 정보를 기록한다."""

    @abstractmethod
    def undo(self) -> None:
        """직전 execute의 효과를 되돌린다."""

class MoveShape(Command):
    """[Concrete Command] 이동. -dx로 거꾸로 빼지 않고 '이전 x'를 스냅샷으로 남긴다."""

    def __init__(self, canvas: Canvas, sid: str, dx: int) -> None:
        """요청(어느 도형을 얼마나)과 수신자를 한 객체에 담는다."""
        self.canvas, self.sid, self.dx = canvas, sid, dx

    def execute(self) -> None:
        """생성 때가 아니라 실행 직전 값을 기억한다. 그래서 0에서 잘려도 정확히 돌아온다."""
        self.before = self.canvas.shapes[self.sid]
        self.canvas.move_to(self.sid, self.before + self.dx)

    def undo(self) -> None:
        """기억한 x로 되돌린다."""
        self.canvas.move_to(self.sid, self.before)

class DeleteShape(Command):
    """[Concrete Command] 삭제. 지운 도형의 값을 통째로 남긴다."""

    def __init__(self, canvas: Canvas, sid: str) -> None:
        """지울 도형을 받는다."""
        self.canvas, self.sid = canvas, sid

    def execute(self) -> None:
        """Canvas가 돌려준 되돌리기 정보를 보관한다."""
        self.x = self.canvas.remove(self.sid)

    def undo(self) -> None:
        """되살린다. 우클릭이든 단축키든 이 명령을 쓰면 기록을 잊을 수 없다."""
        self.canvas.shapes[self.sid] = self.x

class CommandHistory:
    """[Invoker] 실행하고 쌓는다. 한 칸짜리 last_action 대신 스택이라 여러 번 되돌린다."""

    def __init__(self) -> None:
        """되돌리기 스택."""
        self.done: list[Command] = []

    def execute(self, cmd: Command) -> None:
        """실행과 기록을 한 곳에서 한다. 기록을 잊는 핸들러가 생길 수 없다."""
        cmd.execute()
        self.done.append(cmd)

    def undo(self) -> None:
        """Ctrl+Z. 명령의 종류를 묻는 분기 없이 cmd.undo() 한 줄이다."""
        if self.done:
            self.done.pop().undo()

if __name__ == "__main__":
    canvas, history = Canvas(), CommandHistory()
    # [Client] 툴바와 화살표 키가 같은 MoveShape를 만든다. 복사한 코드가 없다.
    def toolbar_move(sid: str, dx: int) -> None:
        """툴바 버튼."""
        history.execute(MoveShape(canvas, sid, dx))
    shortcut_arrow_key = toolbar_move
    print("[1] box(x=20)를 -30 이동 -> 0에서 멈춤 -> 되돌리기")
    toolbar_move("box", -30)
    history.undo()
    print(f"    {canvas.shapes} (box가 정확히 20으로 돌아왔다)")
    print("[2] 화살표 키로 -50 이동 — 같은 명령이라 0에서 멈춘다")
    shortcut_arrow_key("box", -50)
    print(f"    {canvas.shapes}")
    print("[3] 우클릭 삭제 -> 되돌리기 두 번(삭제, 이동 순으로)")
    history.execute(DeleteShape(canvas, "arrow"))
    history.undo()
    history.undo()
    print(f"    {canvas.shapes}")
