"""[13장 연습문제 3 해설] 상태 3개, 행동 차이는 거의 없고 전이만 중요한 경우 — Enum + 전이표를 택한다.

상황: 킥고 사무실 회의실 앞 태블릿은 '비어 있음 / 예약됨 / 사용 중' 세 상태를 색으로만 표시한다.
상태마다 다른 '행동'은 사실상 색과 문구뿐이고, 중요한 것은 어떤 전이가 허용되는지다.

판단: 상태 패턴을 쓰면 클래스 3개 + 기본 클래스 + 위임 메서드가 생기지만, 각 클래스의 본문은
"다음 상태는 X"와 "색은 Y" 한두 줄이다. 클래스가 담을 '행동'이 없으니 다형성이 일할 곳이 없다.
반면 전이표는 규칙 전체를 한 화면에 보여 주고, 표시 속성은 Enum 값에 붙이면 된다.
행동이 상태별로 크게 갈라지기 시작하면(예: '사용 중'에만 연장 결제 로직이 생김) 그때
그 상태 하나만 객체로 승격하면 된다 — 처음부터 계층을 깔 이유는 없다.
"""
from __future__ import annotations

from enum import Enum


class Room(Enum):
    """상태와 그 표시 속성을 한 곳에. 튜플 값으로 (문구, 색)을 묶었다 — 상태별 '행동'이 이것뿐이다."""

    FREE = ("비어 있음", "green")
    BOOKED = ("예약됨", "yellow")
    IN_USE = ("사용 중", "red")

    @property
    def text(self) -> str:
        """표시 문구."""
        return self.value[0]

    @property
    def color(self) -> str:
        """LED 색."""
        return self.value[1]


# 전이 규칙 전체가 다섯 줄이다. 상태 패턴이었다면 이 정보가 세 클래스에 흩어진다.
TRANSITIONS: dict[tuple[Room, str], Room] = {
    (Room.FREE, "book"): Room.BOOKED,
    (Room.FREE, "walk_in"): Room.IN_USE,
    (Room.BOOKED, "check_in"): Room.IN_USE,
    (Room.BOOKED, "no_show"): Room.FREE,
    (Room.IN_USE, "leave"): Room.FREE,
}


class MeetingRoom:
    """[Context] 전이 함수 하나와 현재 상태 하나. 이 규모에서는 이것이 전부여야 한다."""

    def __init__(self, name: str) -> None:
        """비어 있음으로 시작."""
        self.name = name
        self.state = Room.FREE

    def handle(self, event: str) -> None:
        """표에 없으면 거부. 예외 대신 False를 돌려줄 수도 있지만, 키오스크 오작동을 숨기지 않으려 예외로 둔다."""
        key = (self.state, event)
        if key not in TRANSITIONS:
            raise ValueError(f"{self.state.text} 상태에서 '{event}' 불가")
        self.state = TRANSITIONS[key]


if __name__ == "__main__":
    room = MeetingRoom("한라")
    for ev in ("book", "check_in", "book", "leave", "walk_in"):
        try:
            room.handle(ev)
            print(f"    {ev:<9} → {room.state.text} ({room.state.color})")
        except ValueError as e:
            print(f"    {ev:<9} → 거부: {e}")
