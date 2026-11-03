"""13 상태 — 전이표 변형: Enum 상태와 (상태, 사건) -> 다음 상태 dict.

상황: 관제팀장 유나가 묻는다. "전이 규칙 전체를 한 장으로 볼 수 없나요?"
패턴 코드는 전이 규칙을 상태 클래스들에 나눠 두었다. 이 코드는 반대로 규칙을 표 하나에 모은다.
전이를 정하는 쪽이 상태 객체에서 Scooter(표)로 옮겨 간다.
"""
from __future__ import annotations

from enum import Enum, auto


class Status(Enum):
    """상태 이름의 닫힌 집합. 값이 곧 앱 표시 문구다."""
    # 문자열 "maintenance"와 달리 Status.MAINTENACE 같은 오타는 곧바로 AttributeError가 난다.
    AVAILABLE = "대여 가능"
    RESERVED = "예약됨"
    RIDING = "주행 중"
    LOW_BATTERY = "배터리 부족"
    MAINTENANCE = "정비 중"


class Event(Enum):
    """전이를 일으키는 사건. 값에 의미가 없어 auto()로 매긴다."""
    RESERVE = auto()
    UNLOCK = auto()
    END_RIDE = auto()
    BATTERY_LOW = auto()
    MAINTAIN = auto()
    REPAIRED = auto()


S, E = Status, Event   # 표를 한 줄씩 읽히게 하려는 짧은 별칭
# 표에 없는 조합은 모두 불법 전이다. 패턴 코드의 '기본은 거부'를 여기서는 '키가 없음'이 한다.
TRANSITIONS: dict[tuple[Status, Event], Status] = {
    (S.AVAILABLE, E.RESERVE): S.RESERVED,
    (S.AVAILABLE, E.UNLOCK): S.RIDING,
    (S.RESERVED, E.UNLOCK): S.RIDING,
    (S.RIDING, E.END_RIDE): S.AVAILABLE,
    (S.AVAILABLE, E.BATTERY_LOW): S.LOW_BATTERY,
    (S.LOW_BATTERY, E.MAINTAIN): S.MAINTENANCE,
    (S.MAINTENANCE, E.REPAIRED): S.AVAILABLE,
}


class Scooter:
    """[Context + 전이 결정자] 상태는 Enum 값 하나. 가드와 상태별 데이터가 다시 여기로 왔다.

    공개 메서드는 '요청 -> 사건'으로 옮기는 얇은 층이다. 허용 여부는 표가 정하므로
    상태가 늘어도 메서드 본문에 상태 if를 더하지 않는다(가드는 예외).
    """

    def __init__(self, battery: int = 100) -> None:
        """대여 가능으로 시작한다."""
        self.status, self.battery = Status.AVAILABLE, battery
        self.reserved_by: str | None = None   # 예약 상태의 데이터가 다시 Context 필드가 되었다

    def _fire(self, event: Event) -> None:
        """모든 전이가 지나는 관문: 표 조회 -> 대입 -> 진입 동작."""
        # 패턴 코드의 change_state()에 해당한다. 다만 '다음 상태'를 고르는 일까지 여기서 한다.
        new = TRANSITIONS.get((self.status, event))
        if new is None:
            raise ValueError(f"[{self.status.value}] {event.name} 불가")
        print(f"    {self.status.value} -> {new.value}")
        self.status = new
        # 진입 동작은 대입 '뒤'에 부른다. 불법 전이면 위에서 예외가 나 여기까지 오지 않는다.
        self._enter(new)

    def _enter(self, new: Status) -> None:
        """진입 동작: 새 상태에 들어갈 때마다 실행한다. 찌꺼기 정리를 한 곳에 모은다."""
        if new is not Status.RESERVED:
            self.reserved_by = None
        if new is Status.MAINTENANCE:
            self.battery = 100            # 정비에 들어가면 충전부터 한다

    def reserve(self, user: str) -> None:
        """표가 허용하면 예약하고, 전이가 성공한 뒤에 데이터를 기록한다."""
        # 순서가 중요하다: 먼저 기록하면 거부된 예약의 예약자가 찌꺼기로 남는다.
        self._fire(Event.RESERVE)
        self.reserved_by = user

    def unlock(self, user: str) -> None:
        """가드(예약자 확인)는 표에 담을 수 없어 if로 남는다 — 표 방식의 한계."""
        if self.status is Status.RESERVED and user != self.reserved_by:
            raise ValueError(f"{self.reserved_by}님이 예약한 킥보드")
        self._fire(Event.UNLOCK)

    def end_ride(self) -> None:
        """조건부 전이는 사건 두 개로 쪼갠다. 그래서 방전 반납도 잠깐 '대여 가능'을 거친다."""
        self._fire(Event.END_RIDE)
        if self.battery < 15:
            self._fire(Event.BATTERY_LOW)

    def send_to_maintenance(self) -> None:
        """정비 입고. 허용 여부는 표가 정한다."""
        self._fire(Event.MAINTAIN)


if __name__ == "__main__":
    print("[1] 전이표를 그대로 출력 — 규칙 전체가 한 장에 보인다")
    # 표가 데이터라서 규칙 문서를 코드에서 바로 뽑는다. 문서와 구현이 어긋날 수 없다.
    for (src, ev), dst in TRANSITIONS.items():
        print(f"    {src.value} + {ev.name} -> {dst.value}")
    print("[2] 방전 반납: '대여 가능'을 잠깐 거쳐 배터리 부족으로 간다")
    s = Scooter(battery=10)   # 반납 때 배터리 부족으로 가도록 낮게 시작
    s.unlock("민지")
    s.end_ride()
    s.send_to_maintenance()
    print("[3] 정비 중 잠금 해제는 표에 키가 없어 거부된다")
    try:
        s.unlock("지나가던 사람")
    except ValueError as e:
        print(f"    거부: {e}")
