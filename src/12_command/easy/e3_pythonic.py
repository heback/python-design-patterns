"""12 커맨드 — 파이썬다운 변형: '나중에 실행'은 partial로, 되돌리기·전송은 dataclass 명령으로.

상황: 은우는 매크로 녹화와 협업(내 편집을 동료 화면에서 재생)을 만들려 한다.
partial은 실행은 미뤄 주지만 되돌리기 정보도 JSON도 담지 못한다. 그래서 명령이
수신자(Canvas)를 필드로 들지 않고 execute(canvas)의 인자로 받게 바꾼다.
그러면 명령은 순수한 데이터가 되어 JSON으로 보낼 수 있다.
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field, replace
from functools import partial
from typing import ClassVar

class Canvas:
    """[Receiver] 도형 id -> x. 0에서 자르는 규칙은 여기에만 있다."""

    def __init__(self) -> None:
        """두 도형으로 시작."""
        self.shapes = {"box": 20, "arrow": 50}

    def move_to(self, sid: str, x: int) -> None:
        """이동."""
        self.shapes[sid] = max(0, x)

@dataclass
class EditCommand:
    """[Command] 데이터인 명령. 수신자는 실행할 때 인자로 받는다."""
    # ClassVar라 dataclass 필드가 아니다. 생성자 인자도, asdict 결과도 되지 않는다.
    kind: ClassVar[str] = ""

    def execute(self, canvas: Canvas) -> None:
        """하위 클래스가 구현한다."""
        raise NotImplementedError

    def undo(self, canvas: Canvas) -> None:
        """하위 클래스가 구현한다."""
        raise NotImplementedError

    def to_dict(self) -> dict:
        """보낼 것은 요청뿐이다. init=False인 되돌리기 정보는 실행한 쪽의 것이라 뺀다."""
        return {"kind": self.kind, **{k: v for k, v in asdict(self).items() if not k.startswith("_")}}

    def retarget(self, sid: str) -> EditCommand:
        """같은 요청을 다른 도형에. 새 객체를 만든다: 한 객체를 두 번 실행하면 _before가 덮인다."""
        return replace(self, sid=sid)

@dataclass
class Move(EditCommand):
    """[Concrete Command] 이동. 요청은 생성자 인자, 되돌리기 정보는 init=False 필드."""
    kind: ClassVar[str] = "move"
    sid: str
    dx: int
    # 밑줄 + init=False: 요청이 아니라 실행한 쪽만 쓰는 정보라 생성자에도 로그에도 없다.
    _before: int = field(init=False, default=0)

    def execute(self, canvas: Canvas) -> None:
        """실행 직전 x를 스냅샷으로 남긴다."""
        # 패턴 코드의 MoveShape와 같다: 0에서 잘려도 정확히 돌아오려면 -dx가 아니라 이전 값.
        self._before = canvas.shapes[self.sid]
        canvas.move_to(self.sid, self._before + self.dx)

    def undo(self, canvas: Canvas) -> None:
        """스냅샷으로 되돌린다."""
        canvas.move_to(self.sid, self._before)

@dataclass
class Macro(EditCommand):
    """[Concrete Command] 명령 목록을 가진 명령. 녹화한 매크로를 다른 도형에 재생한다."""
    kind: ClassVar[str] = "macro"
    steps: list[EditCommand]

    def execute(self, canvas: Canvas) -> None:
        """차례로 실행."""
        for s in self.steps:
            s.execute(canvas)

    def undo(self, canvas: Canvas) -> None:
        """역순으로 되돌린다."""
        for s in reversed(self.steps):
            s.undo(canvas)

    def to_dict(self) -> dict:
        """하위 단계도 각자 to_dict로. 중첩 구조 그대로 실린다."""
        return {"kind": self.kind, "steps": [s.to_dict() for s in self.steps]}

    def retarget(self, sid: str) -> Macro:
        """각 단계의 retarget에 맡긴다. 그래서 매크로 안의 매크로도 바뀐다."""
        return Macro([s.retarget(sid) for s in self.steps])

def from_dict(d: dict) -> EditCommand:
    """받은 JSON을 명령으로 되살린다. 매크로면 하위 단계도 같은 함수로 되살린다."""
    # 명령 종류가 늘면 이름 -> 클래스 등록부로 바꾼다(10장 build_policy와 같은 방법).
    if d["kind"] == "macro":
        return Macro([from_dict(s) for s in d["steps"]])
    return Move(d["sid"], d["dx"])

if __name__ == "__main__":
    mine, friend = Canvas(), Canvas()
    print("[1] partial: 실행은 미룰 수 있지만 이전 x를 담을 자리도, JSON으로 보낼 방법도 없다")
    # 바운드 메서드 mine.move_to가 들어 있다. 메모리 속 객체라 다른 화면으로 보낼 수 없다.
    later = partial(mine.move_to, "box", 0)
    later()
    print(f"    {mine.shapes}  (되돌리려면? 보내려면?)")
    mine.shapes["box"] = 20
    print("[2] 'box에서 녹화한' 매크로를 arrow에 재생하고 로그를 남긴다")
    recorded = Macro([Move("box", 10), Move("box", -5)])
    cmd = recorded.retarget("arrow")      # recorded는 그대로 두고 새 명령을 만든다
    cmd.execute(mine)
    log = json.dumps(cmd.to_dict(), ensure_ascii=False)
    print(f"    내 화면 {mine.shapes}\n    로그 {log}")
    print("[3] 동료 화면이 로그만으로 같은 편집을 재생한다")
    # 동료 화면에는 내 Canvas 객체가 없다. 명령이 Canvas를 인자로 받기에 재생할 수 있다.
    from_dict(json.loads(log)).execute(friend)
    print(f"    동료 화면 {friend.shapes}")
    print("[4] 내 화면에서 되돌리기 — 되돌리기 정보는 실행한 쪽에 남아 있다")
    cmd.undo(mine)
    print(f"    내 화면 {mine.shapes}")
