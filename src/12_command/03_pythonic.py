"""파이썬다운 변형: partial 커맨드의 한계, dataclass 커맨드와 직렬화, 매크로 녹화.

상황: 02_command.py로 undo/redo는 해결됐다. 남은 요구는 둘이다.
  (a) 사용자가 여러 동작을 '매크로'로 녹화해 다른 도형에 재생하기
  (b) 협업: 동작 로그를 서버로 보내 다른 사용자의 캔버스에서 그대로 재현하기
은우는 먼저 "파이썬이니 functools.partial이면 충분하지 않나?"를 시험해 보고, 그 한계에서
dataclass 커맨드로 넘어간다.

02와 달라진 설계 판단 하나: 커맨드가 수신자(Canvas)를 필드로 들고 있지 않고,
execute(canvas)/undo(canvas)의 '인자'로 받는다. 그래야 커맨드가 순수한 데이터가 되어
JSON으로 직렬화되고, 다른 캔버스(다른 사용자의 화면)에 재생될 수 있다.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field, fields, replace
from functools import partial
from typing import Any, ClassVar


@dataclass
class Shape:
    """캔버스 위의 도형."""

    id: str
    x: int
    y: int
    color: str = "black"


class Canvas:
    """[Receiver] 02와 같은 역할을 하는 축약판."""

    def __init__(self, shapes: list[Shape]) -> None:
        """초기 도형들. 협업 데모에서 두 캔버스가 같은 초기 상태로 시작한다."""
        self.shapes = {s.id: Shape(**vars(s)) for s in shapes}   # 복사: 두 캔버스가 도형을 공유하지 않게

    def move_to(self, shape_id: str, x: int, y: int) -> None:
        """절대 위치 이동(0에서 자름)."""
        s = self.shapes[shape_id]
        s.x, s.y = max(0, x), max(0, y)

    def set_color(self, shape_id: str, color: str) -> str:
        """색 변경 후 이전 색 반환(02와 같은 수신자 API)."""
        s = self.shapes[shape_id]
        prev, s.color = s.color, color
        return prev

    def dump(self) -> str:
        """상태 문자열."""
        return ", ".join(f"{s.id}({s.x},{s.y},{s.color})" for s in self.shapes.values())


# ---------------------------------------------------------------------------
# 시도 ①: functools.partial 커맨드 — 실행은 되지만 그 이상은 안 된다
# ---------------------------------------------------------------------------
def partial_command_demo(canvas: Canvas) -> None:
    """partial로 만든 '커맨드'의 가능과 한계를 보여 준다.

    partial은 '나중에 실행할 호출'을 객체로 만든다 — 커맨드의 절반(요청의 객체화)은
    공짜로 얻는다. 툴바 버튼에 콜백을 거는 용도라면 이것으로 끝이다. 그러나
    undo 정보를 담을 자리가 없고, 바인딩된 canvas 객체 때문에 직렬화도 안 된다.
    """
    move_box = partial(canvas.move_to, "box", 40, 10)
    move_box()                                   # 실행: OK
    print("    실행        :", canvas.dump())
    print("    undo 가능?  :", hasattr(move_box, "undo"), "— 이전 좌표를 담을 곳이 없다")
    try:
        json.dumps(move_box)
    except TypeError as e:
        print("    직렬화?     : TypeError —", e)


# ---------------------------------------------------------------------------
# 시도 ②: dataclass 커맨드 — 요청 매개변수 = 직렬화 대상, undo 정보 = 비직렬화 필드
# ---------------------------------------------------------------------------
COMMAND_TYPES: dict[str, type[EditCommand]] = {}


@dataclass
class EditCommand:
    """[Command] 직렬화 가능한 편집 명령의 기반.

    필드를 두 종류로 나눈다.
      - init=True 필드: '무엇을 하라'는 요청 매개변수. 로그로 보내고 재생할 대상.
      - init=False 필드: execute() 때 채워지는 undo 정보. 로컬 실행에만 의미가 있으므로
        직렬화에서 빠진다(다른 사용자의 캔버스에서는 그쪽에서 새로 채운다).
    __init_subclass__로 하위 클래스를 자동 등록해, from_dict()가 'type' 문자열로
    클래스를 찾게 한다 — 새 명령은 클래스 정의만으로 역직렬화까지 지원된다(OCP).
    구조가 특별한 명령(Macro)은 from_payload()/retarget() 훅만 재정의하면 되므로,
    역직렬화 진입점에 '매크로면 따로' 같은 분기가 생기지 않는다.
    """

    kind: ClassVar[str] = "abstract"

    def __init_subclass__(cls, **kw: Any) -> None:
        """하위 클래스 정의 시점에 등록부에 올린다.

        kind를 직접 선언하지 않은 하위 클래스(예: Move를 상속한 FastMove)는 부모의 kind를
        물려받아 부모의 등록을 조용히 덮어쓴다. 그러면 로그의 "move"가 엉뚱한 클래스로
        재생된다. 정의 시점에 바로 실패시킨다.
        """
        super().__init_subclass__(**kw)
        if "kind" not in cls.__dict__:
            raise TypeError(f"{cls.__name__}: 직렬화 이름(kind)을 선언해야 한다")
        if cls.kind in COMMAND_TYPES:
            raise TypeError(f"{cls.__name__}: kind {cls.kind!r}는 이미 {COMMAND_TYPES[cls.kind].__name__}가 쓴다")
        COMMAND_TYPES[cls.kind] = cls

    def execute(self, canvas: Canvas) -> None:
        """요청 수행. 하위 클래스가 구현한다."""
        raise NotImplementedError

    def undo(self, canvas: Canvas) -> None:
        """되돌리기. 하위 클래스가 구현한다."""
        raise NotImplementedError

    def to_dict(self) -> dict[str, Any]:
        """요청 매개변수만 dict로. undo 필드(init=False)는 제외한다."""
        return {"type": self.kind, **{f.name: getattr(self, f.name) for f in fields(self) if f.init}}

    @staticmethod
    def from_dict(d: dict[str, Any]) -> EditCommand:
        """로그 한 줄 → 명령 객체. 알 수 없는 type은 즉시 KeyError로 드러난다."""
        data = dict(d)
        return COMMAND_TYPES[data.pop("type")].from_payload(data)

    @classmethod
    def from_payload(cls, data: dict[str, Any]) -> EditCommand:
        """역직렬화 훅. 평범한 명령은 필드가 곧 생성자 인자다."""
        return cls(**data)

    def retarget(self, shape_id: str) -> EditCommand:
        """같은 요청을 다른 도형에 — 항상 '새' 인스턴스를 만든다.

        같은 명령 객체를 두 번 실행하면 undo 정보(_before 등)가 덮어쓰여, 먼저 실행한
        쪽을 되돌릴 수 없게 된다. dataclasses.replace는 init=False 필드를 기본값으로 둔
        새 객체를 만든다.
        """
        return replace(self, shape_id=shape_id)


@dataclass
class Move(EditCommand):
    """[Concrete Command] 상대 이동. 이전 좌표 스냅샷으로 정확히 되돌린다."""

    kind: ClassVar[str] = "move"
    shape_id: str
    dx: int
    dy: int
    _before: tuple[int, int] | None = field(default=None, init=False, repr=False)

    def execute(self, canvas: Canvas) -> None:
        """이전 좌표 기억 후 이동."""
        s = canvas.shapes[self.shape_id]
        self._before = (s.x, s.y)
        canvas.move_to(self.shape_id, s.x + self.dx, s.y + self.dy)

    def undo(self, canvas: Canvas) -> None:
        """기억한 좌표로 복귀."""
        assert self._before is not None
        canvas.move_to(self.shape_id, *self._before)


@dataclass
class Recolor(EditCommand):
    """[Concrete Command] 색 변경."""

    kind: ClassVar[str] = "recolor"
    shape_id: str
    color: str
    _prev: str | None = field(default=None, init=False, repr=False)

    def execute(self, canvas: Canvas) -> None:
        """수신자 API로 변경하고 이전 색을 기억한다."""
        self._prev = canvas.set_color(self.shape_id, self.color)

    def undo(self, canvas: Canvas) -> None:
        """이전 색 복원."""
        assert self._prev is not None
        canvas.set_color(self.shape_id, self._prev)


@dataclass
class Macro(EditCommand):
    """[Concrete Command / Composite] 명령 목록. 매크로도 하나의 명령으로 직렬화된다."""

    kind: ClassVar[str] = "macro"
    name: str
    steps: list[EditCommand]

    def execute(self, canvas: Canvas) -> None:
        """순서대로. 중간 실패 시 실행한 단계를 역순으로 되돌리고 다시 던진다(02와 같은 롤백)."""
        done: list[EditCommand] = []
        try:
            for s in self.steps:
                s.execute(canvas)
                done.append(s)
        except Exception:
            for s in reversed(done):
                s.undo(canvas)
            raise

    def undo(self, canvas: Canvas) -> None:
        """역순으로."""
        for s in reversed(self.steps):
            s.undo(canvas)

    def to_dict(self) -> dict[str, Any]:
        """하위 명령까지 재귀적으로 직렬화한다. 하위가 Macro여도 각자의 to_dict()가 처리한다."""
        return {"type": self.kind, "name": self.name, "steps": [s.to_dict() for s in self.steps]}

    @classmethod
    def from_payload(cls, data: dict[str, Any]) -> Macro:
        """역직렬화 훅 재정의. 하위 단계를 from_dict()로 되살리므로 중첩 매크로도 재귀적으로 복원된다."""
        return cls(data["name"], [EditCommand.from_dict(s) for s in data["steps"]])

    def retarget(self, shape_id: str) -> Macro:
        """하위 명령 각각의 retarget()에 위임한다 — 하위가 Macro면 재귀, 아니면 replace."""
        return Macro(self.name, [s.retarget(shape_id) for s in self.steps])


class Session:
    """[Invoker] 한 사용자의 편집 세션: 실행, undo, 그리고 서버로 보낼 로그."""

    def __init__(self, canvas: Canvas) -> None:
        """수신자와 이력, 전송 로그(JSON 줄 목록)."""
        self.canvas = canvas
        self.history: list[EditCommand] = []
        self.outbox: list[str] = []

    def run(self, cmd: EditCommand) -> None:
        """실행 + 이력 + 로그. 로그에는 요청만 실린다(undo 정보는 로컬 전용)."""
        cmd.execute(self.canvas)
        self.history.append(cmd)
        self.outbox.append(json.dumps(cmd.to_dict(), ensure_ascii=False))

    def undo(self) -> None:
        """최근 명령 취소. 협업 로그에는 '취소'를 별도 이벤트로 보내야 하지만 여기선 생략."""
        self.history.pop().undo(self.canvas)


if __name__ == "__main__":
    initial = [Shape("box", 10, 10), Shape("arrow", 50, 20)]

    print("[1] partial 커맨드: 실행은 되지만 undo·직렬화는 불가")
    partial_command_demo(Canvas(initial))

    print("[2] 은우의 세션: 매크로 '강조하기'를 box에 실행, 그것을 품은 중첩 매크로를 arrow에 재생")
    eunwoo = Session(Canvas(initial))
    highlight = Macro("강조하기", [Move("box", 20, 0), Recolor("box", "red")])
    eunwoo.run(highlight)
    # 매크로 안의 매크로(컴포지트). retarget·직렬화·역직렬화가 모두 재귀로 내려간다.
    # ⚠ nested는 이미 실행된 highlight 인스턴스를 품는다 — retarget 없이 run(nested)하면 같은 인스턴스가 두 번 실행되어 undo 정보가 덮어쓰인다.
    nested = Macro("강조 후 내리기", [highlight, Move("box", 0, 30)])
    eunwoo.run(nested.retarget("arrow"))
    print("    은우 캔버스 :", eunwoo.canvas.dump())

    print("[3] 서버로 보낸 로그(JSON) — undo 정보(_before, _prev)는 실리지 않는다")
    for line in eunwoo.outbox:
        print("   ", line)

    print("[4] 동료 지아의 캔버스에서 로그 재생 → 같은 상태")
    jia = Canvas(initial)
    for line in eunwoo.outbox:
        EditCommand.from_dict(json.loads(line)).execute(jia)
    print("    지아 캔버스 :", jia.dump())
    print("    일치?       :", jia.dump() == eunwoo.canvas.dump())

    print("[5] 은우가 Ctrl+Z — 재생용 새 인스턴스 덕분에 arrow 쪽 중첩 매크로만 정확히 되돌아간다")
    eunwoo.undo()
    print("    은우 캔버스 :", eunwoo.canvas.dump())

    print("[6] kind를 선언하지 않은 하위 클래스는 정의 시점에 거부된다(등록 덮어쓰기 방지)")
    try:
        @dataclass
        class FastMove(Move):
            """kind를 빠뜨린 하위 클래스 — 'move' 등록을 덮어쓸 뻔했다."""
    except TypeError as e:
        print("    TypeError   :", e)
