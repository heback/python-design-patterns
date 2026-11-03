"""12 커맨드 — 순진한 코드: 버튼 핸들러가 도형을 직접 바꾸고, 되돌리기는 따로 논다.

상황: 그림판 앱의 은우는 툴바 버튼으로 도형을 옮기고 지우게 했다. 실행 취소가
필요해지자 핸들러마다 "직전에 한 일"을 last_action에 적게 했고, 화살표 키와
우클릭 메뉴를 만들 때는 툴바 코드를 복사했다. 버그 보고가 세 건 들어왔다.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Shape:
    """도형. 이 예제는 가로 위치 x만 다룬다."""
    id: str
    x: int


class Editor:
    """편집기. 핸들러가 동작과 되돌리기 기록을 모두 직접 한다."""

    def __init__(self) -> None:
        """도형 둘과, 되돌리기용 기록 한 칸."""
        self.shapes = {"box": Shape("box", 20), "arrow": Shape("arrow", 50)}
        self.last_action: tuple | None = None   # ⚠ 문제: 한 칸뿐이라 두 번 되돌릴 수 없다

    def on_toolbar_move(self, sid: str, dx: int) -> None:
        """툴바 이동. 화면 밖(x < 0)으로 나가지 않게 0에서 자른다."""
        self.shapes[sid].x = max(0, self.shapes[sid].x + dx)
        self.last_action = ("move", sid, dx)

    def on_shortcut_move(self, sid: str, dx: int) -> None:
        """화살표 키 이동. 툴바 코드를 복사했다."""
        # ⚠ 문제: 복사하면서 0에서 자르는 검사를 빠뜨렸다.
        self.shapes[sid].x += dx
        self.last_action = ("move", sid, dx)

    def on_context_delete(self, sid: str) -> None:
        """우클릭 삭제."""
        # ⚠ 문제: 이 핸들러는 last_action 기록을 잊었다. 되돌릴 수 없다.
        del self.shapes[sid]

    def on_undo(self) -> None:
        """Ctrl+Z. 모든 동작의 종류와 되돌리는 법을 여기서 따로 안다."""
        if self.last_action and self.last_action[0] == "move":
            _, sid, dx = self.last_action
            # ⚠ 문제: '요청한 이동량'을 거꾸로 뺀다. 0에서 잘렸다면 엉뚱한 곳으로 간다.
            self.shapes[sid].x -= dx
        self.last_action = None


if __name__ == "__main__":
    ed = Editor()
    print("[1] box(x=20)를 툴바로 -30 이동 -> 0에서 멈춤 -> 되돌리기")
    ed.on_toolbar_move("box", -30)
    ed.on_undo()
    print(f"    box.x = {ed.shapes['box'].x} (원래 20이어야 한다)")
    print("[2] 화살표 키로 -50 이동")
    ed.on_shortcut_move("box", -50)
    print(f"    box.x = {ed.shapes['box'].x} (화면 밖으로 나갔다)")
    print("[3] 우클릭으로 arrow 삭제 -> 되돌리기")
    ed.on_context_delete("arrow")
    ed.on_undo()
    print(f"    남은 도형: {list(ed.shapes)} (arrow가 돌아오지 않는다)")
