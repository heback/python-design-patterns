"""[13장 상태 · 파이썬다운 변형 1] Enum + 전이표(dict)로 쓴 유한 상태 기계, 그리고 match 버전.

상황: 킥고의 관제팀장 유나가 서진에게 묻는다. "전이 규칙 전체를 한 장으로 볼 수 없어요?
지금은 상태 클래스 여섯 개를 다 열어 봐야 정비 중에서 어디로 갈 수 있는지 알 수 있잖아요."
02의 상태 패턴은 전이 규칙을 상태 클래스들에 '분산'시켰다. 이 파일은 정반대로 전이 규칙을
하나의 표(데이터)에 '집중'시킨다. 전이의 책임자가 상태 객체에서 Context(표)로 옮겨 간다.

얻는 것: 전이 전체가 한눈에 보이고, 표가 데이터이므로 출력·검증(도달 불가 상태 찾기)·
문서 생성이 공짜다. 잃는 것: 상태별 '행동'과 '데이터'가 다시 Context로 돌아온다.
조건부 전이(가드)는 표에 들어가지 않아 Context의 if로 남는다. 데모 끝의 검증 출력과
Scooter 메서드 안의 if를 함께 보며 이 거래를 저울질하라.
"""
from __future__ import annotations

from collections import deque
from enum import Enum, auto

RESERVATION_TTL = 600
LOW_BATTERY = 15


class Status(Enum):
    """상태 이름의 닫힌 집합. 문자열 status와 달리 오타는 AttributeError로 즉시 드러난다.

    값에 표시 문구를 넣어 01 label()의 상태별 문구 dict를 없앴다.
    """

    AVAILABLE = "대여 가능"
    RESERVED = "예약됨"
    RIDING = "주행 중"
    LOW_BATTERY = "배터리 부족"
    MAINTENANCE = "정비 중"
    LOST = "분실 신고"


class Event(Enum):
    """전이를 일으키는 사건. 값은 의미가 없으므로 auto()."""

    RESERVE = auto()
    UNLOCK = auto()
    END_RIDE = auto()
    EXPIRE = auto()
    BATTERY_LOW = auto()
    BATTERY_OK = auto()
    MAINTAIN = auto()
    REPAIRED = auto()
    LOSE = auto()


# 별칭을 모듈 전역에 두는 것은 보통 피할 일이지만, 전이표의 가독성이 이 장의 요점이라 예외로 한다.
S, E = Status, Event   # 표를 한 줄씩 읽히게 하려는 별칭. 이 표 근처에서만 쓴다.

# 전이표: (현재 상태, 사건) → 다음 상태. 표에 없는 조합은 전부 불법 전이다.
# 02에서 'ScooterState 기본 메서드 = 거부'가 하던 일을, 여기서는 'dict에 키가 없음'이 한다.
TRANSITIONS: dict[tuple[Status, Event], Status] = {
    # --- 대여 가능: 출구가 가장 많은 허브 상태 ---
    (S.AVAILABLE, E.RESERVE): S.RESERVED,
    (S.AVAILABLE, E.UNLOCK): S.RIDING,
    (S.AVAILABLE, E.BATTERY_LOW): S.LOW_BATTERY,
    (S.AVAILABLE, E.MAINTAIN): S.MAINTENANCE,
    (S.AVAILABLE, E.LOSE): S.LOST,
    # --- 예약됨: 예약자 확인 가드는 표 밖(Scooter.unlock)에 있다 ---
    (S.RESERVED, E.UNLOCK): S.RIDING,
    (S.RESERVED, E.EXPIRE): S.AVAILABLE,
    (S.RIDING, E.END_RIDE): S.AVAILABLE,       # 배터리 분기는 표에 못 넣는다 → Scooter.end_ride 참고
    # --- 배터리 부족: 대여 관련 사건(RESERVE/UNLOCK)이 아예 없다 = 거부 ---
    (S.LOW_BATTERY, E.BATTERY_OK): S.AVAILABLE,
    (S.LOW_BATTERY, E.MAINTAIN): S.MAINTENANCE,
    (S.LOW_BATTERY, E.LOSE): S.LOST,
    # --- 정비 중·분실: 01에서 사고가 난 지점. UNLOCK 행이 없으므로 자동으로 불법 ---
    (S.MAINTENANCE, E.REPAIRED): S.AVAILABLE,
    (S.LOST, E.MAINTAIN): S.MAINTENANCE,
}


class IllegalTransition(Exception):
    """표에 없는 (상태, 사건) 조합."""


def next_status(status: Status, event: Event) -> Status:
    """표 조회 한 줄. 상태 기계의 '전이 함수' 그 자체다."""
    try:
        return TRANSITIONS[(status, event)]
    except KeyError:
        # from None: KeyError 연쇄를 숨긴다. 호출자에게 중요한 건 dict 구현이 아니라 규칙 위반이다.
        raise IllegalTransition(f"[{status.value}] 상태에서 {event.name} 불가") from None


def next_status_match(status: Status, event: Event) -> Status:
    """같은 전이 함수를 match 문으로 쓴 버전 — 비교용.

    match는 '패턴이 여러 값을 묶는' 경우(| 로 OR)나 가드(if)를 직접 쓸 수 있어 표보다
    표현력이 높다. 대신 코드이므로 출력·순회·검증이 불가능하다: '정비 중에서 갈 수 있는
    상태 목록'을 프로그램으로 뽑아낼 수 없다. 데이터냐 코드냐의 선택이다.
    """
    match (status, event):
        case (S.AVAILABLE, E.RESERVE):
            return S.RESERVED
        case (S.AVAILABLE | S.RESERVED, E.UNLOCK):          # 두 상태를 한 줄에 — 표에는 없는 압축
            return S.RIDING
        case (S.AVAILABLE, E.BATTERY_LOW):
            return S.LOW_BATTERY
        # 표의 세 줄(MAINTAIN)이 한 case로 압축됐다 — 대신 '정비로 가는 출구 목록'을 뽑아낼 수 없다.
        case (S.AVAILABLE | S.LOW_BATTERY | S.LOST, E.MAINTAIN):
            return S.MAINTENANCE
        case (S.AVAILABLE | S.LOW_BATTERY, E.LOSE):
            return S.LOST
        case (S.RESERVED, E.EXPIRE) | (S.RIDING, E.END_RIDE) \
                | (S.LOW_BATTERY, E.BATTERY_OK) | (S.MAINTENANCE, E.REPAIRED):
            return S.AVAILABLE
        # 와일드카드 = 표의 '키 없음'. 이 줄을 빼먹으면 None이 반환되어 조용히 망가진다.
        case _:
            raise IllegalTransition(f"[{status.value}] 상태에서 {event.name} 불가")


class Scooter:
    """[Context + 전이 책임자] 상태는 Enum 값 하나이고, 행동과 가드는 다시 여기로 돌아왔다.

    02와 비교하면 상태별 데이터(reserved_by, rider ...)가 Context 필드로 돌아왔다는 점이
    가장 큰 후퇴다. 그래서 _enter()에서 '들어가는 상태에 필요 없는 필드는 지운다'는
    규칙을 한 곳에 모아 01의 찌꺼기 문제를 완화한다.
    """

    def __init__(self, battery: int = 100) -> None:
        """대여 가능으로 시작."""
        self.status = Status.AVAILABLE
        self.battery = battery
        self.reserved_by: str | None = None
        self.reserved_at: int | None = None
        self.rider: str | None = None
        self.history: list[str] = []

    def _fire(self, event: Event) -> None:
        """모든 전이가 지나가는 유일한 관문. 표 조회 → 기록 → 진입 처리."""
        new = next_status(self.status, event)      # 불법이면 여기서 예외 → 아래 기록·대입은 실행되지 않는다
        self.history.append(f"{self.status.name} -{event.name}-> {new.name}")
        self.status = new
        # 진입 동작은 대입 '뒤'에: _enter가 현재 상태를 근거로 판단할 수 있게.
        self._enter(new)

    def _enter(self, new: Status) -> None:
        """진입 동작(entry action). 상태별 데이터의 수명을 여기서 관리한다."""
        if new is not Status.RESERVED:
            self.reserved_by = self.reserved_at = None
        if new is not Status.RIDING:
            self.rider = None

    # 아래 공개 메서드들은 '외부 요청 → 사건'으로 번역하는 어댑터 층이다. 02에서는 이 번역과
    # 행동이 상태 클래스에 있었고, 여기서는 상태와 무관한 Context 메서드에 있다.
    def reserve(self, user: str, now: int) -> None:
        """표가 허용하면 예약. 데이터 기록은 전이 성공 뒤에 한다(실패 시 오염 방지)."""
        self._fire(Event.RESERVE)
        self.reserved_by, self.reserved_at = user, now

    def unlock(self, user: str) -> None:
        """가드(예약자 확인)는 표로 표현할 수 없어 if로 남는다 — 표 방식의 한계."""
        if self.status is Status.RESERVED and user != self.reserved_by:
            raise IllegalTransition(f"{self.reserved_by}님이 예약한 킥보드입니다")
        self._fire(Event.UNLOCK)
        # 탑승자는 상태별 데이터지만 Enum 값에 담을 수 없어 Context 필드가 된다.
        self.rider = user

    def end_ride(self) -> None:
        """조건부 전이를 '사건 두 개'로 쪼갠다: END_RIDE 후 배터리가 낮으면 BATTERY_LOW.

        대가: 방전 반납은 잠깐 AVAILABLE을 거친다. 전이마다 통지한다면 그 중간 상태가 바깥에 보인다.
        """
        self._fire(Event.END_RIDE)
        if self.battery < LOW_BATTERY:
            self._fire(Event.BATTERY_LOW)

    def tick(self, now: int) -> None:
        """시간 이벤트를 EXPIRE 사건으로 번역한다. 번역 규칙(10분)은 여전히 Context의 if다."""
        if self.status is Status.RESERVED and self.reserved_at is not None \
                and now - self.reserved_at >= RESERVATION_TTL:
            self._fire(Event.EXPIRE)

    def send_to_maintenance(self) -> None:
        """정비 입고."""
        self._fire(Event.MAINTAIN)


def reachable_from(start: Status) -> set[Status]:
    """전이표가 데이터이기 때문에 가능한 정적 검증: 시작 상태에서 도달 가능한 상태 집합(BFS)."""
    # 표를 그래프의 간선 목록으로 읽는다. 상태 클래스 방식이라면 간선이 메서드 본문에
    # 숨어 있어 이런 순회 자체가 불가능하다.
    seen, queue = {start}, deque([start])
    while queue:
        cur = queue.popleft()
        for (src, _), dst in TRANSITIONS.items():
            if src is cur and dst not in seen:
                seen.add(dst)
                queue.append(dst)
    return seen


if __name__ == "__main__":
    print("[1] 전이표를 그대로 출력 — 관제팀장이 원한 '한 장짜리 규칙'")
    # 표가 데이터이므로 '문서'를 코드에서 바로 생성한다. 문서와 구현이 어긋날 수 없다.
    width = max(len(s.name) for s in Status)
    for state in Status:
        outs = [f"{ev.name}→{dst.name}" for (src, ev), dst in TRANSITIONS.items() if src is state]
        print(f"    {state.name:<{width}} : {', '.join(outs)}")

    print("[2] 정적 검증: 도달 불가 상태와 출구 없는 상태 찾기")
    # 새 상태를 Enum에 추가하고 표에 들어가는 간선을 깜빡하면 '도달 불가'로 잡힌다.
    # CI에서 단언(assert)으로 돌리면 01의 '분기 누락'을 기계가 대신 찾아 준다.
    unreachable = set(Status) - reachable_from(Status.AVAILABLE)
    dead_ends = {s for s in Status if not any(src is s for src, _ in TRANSITIONS)}
    print(f"    도달 불가: {unreachable or '없음'} / 출구 없음: {dead_ends or '없음'}")

    print("[3] 표 버전과 match 버전이 모든 (상태, 사건) 조합에서 같은가")
    # 두 전이 함수를 모든 조합(6 상태 × 9 사건)에 대해 대조한다. 표를 정답지로 삼아
    # match 같은 '코드' 구현을 검증할 수 있다는 것도 데이터 방식의 이점이다.
    agree = 0
    for st in Status:
        for ev in Event:
            results = []
            for fn in (next_status, next_status_match):
                try:
                    results.append(fn(st, ev))
                except IllegalTransition:
                    results.append("불법")
            agree += results[0] == results[1]
    print(f"    {agree}/{len(Status) * len(Event)} 조합 일치")

    print("[4] 시나리오: 예약 → 남의 잠금 해제 시도 → 본인 해제 → 방전 상태로 반납 → 정비 중 해제 시도")
    sc = Scooter()
    sc.reserve("민지", now=0)
    # 가드는 표가 아니라 Scooter.unlock의 if가 처리한다 — 거부 메시지의 출처가 다르다.
    for who in ("지호", "민지"):
        try:
            sc.unlock(who)
            print(f"    {who}: 잠금 해제 성공")
        except IllegalTransition as e:
            print(f"    {who}: 거부 — {e}")
    # 주행 중 방전: END_RIDE → BATTERY_LOW 두 사건으로 쪼개진 조건부 전이를 확인한다.
    sc.battery = 8
    sc.end_ride()
    sc.send_to_maintenance()
    # 01의 사고 시나리오: 정비 중 잠금 해제. 표에 (MAINTENANCE, UNLOCK) 행이 없어 거부된다.
    try:
        sc.unlock("해커")
    except IllegalTransition as e:
        print("    해커: 거부 —", e)
    print("    전이 로그:", " | ".join(sc.history))
