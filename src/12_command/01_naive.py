"""순진한 설계: 도형 편집 동작이 UI 핸들러 안에 직접 박혀 있다.

상황: 웹 기반 다이어그램 도구 '스케치보드'의 개발자 은우는 툴바 버튼 핸들러 안에서
도형 이동·색 변경·삭제를 바로 실행했다. 그런데 같은 기능을 단축키와 우클릭 메뉴에서도
불러야 했고, Ctrl+Z(실행 취소)가 필요해졌다. 은우는 핸들러마다 '직전 동작'을 각자
기록하는 방식으로 대응했다.

이 파일에서 확인할 고통:
  1) 같은 동작 코드가 툴바·단축키·메뉴 세 곳에 복제되고, 복제본끼리 어긋난다.
  2) undo 정보를 핸들러마다 제각각 기록한다. 한 곳이라도 잊으면 Ctrl+Z가 엉뚱하게 동작한다.
  3) 직전 동작 '하나'만 기억하므로 여러 단계 undo, redo, 매크로 녹화가 불가능하다.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Shape:
    """캔버스 위의 도형 하나."""

    id: str
    x: int
    y: int
    color: str = "black"


class Editor:
    """편집기. 도형 저장소이면서 UI 이벤트 핸들러 모음이기도 하다(책임이 섞였다)."""

    def __init__(self) -> None:
        """도형 목록과 '직전 동작' 기록 하나."""
        self.shapes: dict[str, Shape] = {}
        # ⚠ 문제: undo 정보가 형식 없는 튜플 하나다. 핸들러마다 다른 모양으로 채운다.
        self.last_action: tuple | None = None

    # --- 툴바 버튼 ---------------------------------------------------------
    def on_toolbar_move(self, shape_id: str, dx: int, dy: int) -> None:
        """툴바의 '이동' 버튼."""
        s = self.shapes[shape_id]
        s.x, s.y = max(0, s.x + dx), max(0, s.y + dy)   # 캔버스 밖으로 못 나가게 0에서 자른다
        self.last_action = ("move", shape_id, dx, dy)

    def on_toolbar_color(self, shape_id: str, color: str) -> None:
        """툴바의 색상 팔레트."""
        s = self.shapes[shape_id]
        self.last_action = ("color", shape_id, s.color)   # 이전 색을 기억
        s.color = color

    # --- 단축키 ------------------------------------------------------------
    def on_shortcut_move(self, shape_id: str, dx: int, dy: int) -> None:
        """화살표 키 이동. ⚠ 문제: 툴바 코드를 복사했는데 0 자르기를 빠뜨렸다."""
        s = self.shapes[shape_id]
        s.x, s.y = s.x + dx, s.y + dy
        self.last_action = ("move", shape_id, dx, dy)

    # --- 우클릭 메뉴 -------------------------------------------------------
    def on_context_delete(self, shape_id: str) -> None:
        """우클릭 '삭제'. ⚠ 문제: last_action 기록을 잊었다 — 이 삭제는 Ctrl+Z로 되돌릴 수 없다."""
        del self.shapes[shape_id]

    # --- Ctrl+Z ------------------------------------------------------------
    def on_undo(self) -> None:
        """⚠ 문제: undo가 '모든 동작의 종류'를 알아야 한다. 동작이 늘 때마다 이 분기도 는다."""
        if self.last_action is None:
            print("    (되돌릴 동작 없음)")
            return
        kind, shape_id, *rest = self.last_action
        if kind == "move":
            dx, dy = rest
            s = self.shapes[shape_id]
            # ⚠ 문제: 역연산이 '0에서 자르기'를 모른다. 잘린 이동은 정확히 되돌려지지 않는다.
            s.x, s.y = s.x - dx, s.y - dy
        elif kind == "color":
            self.shapes[shape_id].color = rest[0]
        self.last_action = None   # ⚠ 문제: 한 단계만. 두 번째 Ctrl+Z는 아무것도 못 한다. redo도 없다.

    def dump(self) -> str:
        """현재 캔버스 상태 문자열."""
        return ", ".join(f"{s.id}({s.x},{s.y},{s.color})" for s in self.shapes.values())


if __name__ == "__main__":
    ed = Editor()
    ed.shapes = {"box": Shape("box", 10, 10), "arrow": Shape("arrow", 50, 20)}
    print("[0] 시작      :", ed.dump())

    print("[1] 툴바로 box를 (-30, 0) 이동 → x가 0에서 잘림, 그리고 Ctrl+Z")
    ed.on_toolbar_move("box", -30, 0)
    print("    이동 후   :", ed.dump())
    ed.on_undo()
    print("    undo 후   :", ed.dump(), "← 원래 x=10이 아니라 30이 됐다")

    print("[2] 같은 이동을 단축키로 → 캔버스 밖(음수 좌표)으로 나간다")
    ed.on_shortcut_move("arrow", -60, 0)
    print("    이동 후   :", ed.dump())

    print("[3] 색 변경 두 번 후 Ctrl+Z 두 번 → 한 번만 되돌려진다")
    ed.on_toolbar_color("box", "red")
    ed.on_toolbar_color("box", "blue")
    ed.on_undo()
    ed.on_undo()
    print("    결과      :", ed.dump(), "← black이 아니라 red")

    print("[4] 우클릭으로 arrow 삭제 후 Ctrl+Z")
    ed.on_context_delete("arrow")
    ed.on_undo()
    print("    결과      :", ed.dump(), "← arrow는 영영 사라졌다")
