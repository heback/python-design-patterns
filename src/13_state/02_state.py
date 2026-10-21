"""[13장 상태 · 패턴 적용] 킥보드의 상태별 행동과 전이 규칙을 상태 객체로 옮긴다.

상황: 01_naive.py에서 서진의 `Scooter`는 label()을 뺀 동작 메서드 여덟 개마다 여섯 상태의 분기를 반복했고,
두 상태 시절에 쓴 `else` 하나 때문에 정비 중인 킥보드로 주행이 시작되는 사고가 났다.
이 파일은 GoF 상태 패턴으로 다시 짠 버전이다.

핵심 설계 결정 세 가지:
1. 행동이 상태별로 다른 메서드(reserve, unlock, end_ride ...)는 모두 현재 상태 객체에 위임한다.
   `Scooter`(Context)에는 상태 분기가 한 줄도 남지 않는다.
2. 상태 기본 클래스의 기본 구현은 '사용자 명령은 거부(예외)'다. 그래서 새 상태를 추가할 때
   허용할 동작만 오버라이드하면 되고, 깜빡 잊은 동작은 자동으로 '불법 전이'가 된다.
   순진한 코드의 `else`가 기본값을 '허용'으로 둔 것과 정반대의 안전한 기본값이다.
3. 다음 상태는 상태 객체가 스스로 정한다(`scooter.change_state(...)` 호출).
   이것이 같은 구조를 가진 전략 패턴과 갈라지는 지점이다 — 03_state_vs_strategy.py 참고.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import NoReturn

RESERVATION_TTL = 600      # 예약 유지 시간(초)
LOW_BATTERY = 15           # 이 미만이면 대여 불가
UNLOCK_FEE = 1_000         # 원
PER_MINUTE = 150           # 원
NO_SHOW_FEE = 500          # 원


class IllegalTransition(Exception):
    """현재 상태에서 허용되지 않는 동작을 요청했을 때.

    ValueError 대신 전용 예외를 두는 이유: API 계층이 이 예외만 골라 409 Conflict로
    번역할 수 있고, 테스트도 '불법 전이가 거부되었다'는 의도를 정확히 단언할 수 있다.
    """


class ScooterState(ABC):
    """[State] 킥보드 상태의 공통 인터페이스이자 '기본은 거부' 정책의 보관소.

    메서드마다 context(`scooter`)를 인자로 받는다. 상태 객체가 context를 필드로 들고
    있지 않게 한 이유: 순환 참조를 피하고, 상태 객체가 '어느 킥보드의 상태인지'에
    묶이지 않게 하기 위해서다(무상태 상태 객체는 여러 킥보드가 공유할 수도 있다 — 05 참고).

    추상 메서드는 label() 하나뿐이다. 동작 메서드를 전부 abstractmethod로 만들면
    새 상태마다 거부용 보일러플레이트 여섯 개를 써야 하고, 그 복붙 속에서 또 실수가 난다.
    """

    # --- 사용자 명령: 기본은 거부. 허용하는 상태만 오버라이드한다. -------------------
    def reserve(self, scooter: Scooter, user: str, now: int) -> None:
        """예약 요청."""
        self._reject("예약")

    def unlock(self, scooter: Scooter, user: str, now: int) -> None:
        """잠금 해제(주행 시작) 요청."""
        self._reject("잠금 해제")

    def end_ride(self, scooter: Scooter, now: int) -> int:
        """반납 요청. 요금을 돌려준다."""
        self._reject("반납")

    def send_to_maintenance(self, scooter: Scooter) -> None:
        """정비 입고 요청(운영자)."""
        self._reject("정비 입고")

    def finish_maintenance(self, scooter: Scooter) -> None:
        """정비 완료 요청(운영자)."""
        self._reject("정비 완료")

    def report_lost(self, scooter: Scooter) -> None:
        """분실 신고(관제 시스템)."""
        self._reject("분실 신고")

    # --- 시스템 이벤트: 기본은 무시. ------------------------------------------------
    # 시계·센서 이벤트는 누가 '요청'한 것이 아니라 그냥 일어나는 일이다. 대부분 상태에서
    # 의미가 없으므로 예외 대신 조용히 무시하는 편이 맞다. 기본값을 이벤트 종류에 따라
    # 다르게 두는 것 자체가 설계 판단이며, 그 판단이 이 기본 클래스 한 곳에 모여 있다.
    def tick(self, scooter: Scooter, now: int) -> None:
        """주기적 시간 이벤트."""

    def on_battery_changed(self, scooter: Scooter) -> None:
        """배터리 값이 갱신된 직후 호출된다."""

    @abstractmethod
    def label(self) -> str:
        """앱 지도에 표시할 문구. 상태마다 반드시 달라야 하므로 유일한 추상 메서드다."""

    def _reject(self, action: str) -> NoReturn:
        """불법 전이를 한 가지 형식의 예외로 알린다. NoReturn 덕분에 end_ride(-> int)의
        기본 구현이 return 없이 끝나도 타입 검사기가 '값을 안 돌려준다'고 불평하지 않는다."""
        raise IllegalTransition(f"[{self.label()}] 상태에서는 {action}할 수 없습니다")

    def __repr__(self) -> str:
        """전이 로그에 클래스 이름이 찍히도록."""
        return type(self).__name__


# ---------------------------------------------------------------------------
# 구체 상태들 — 각 클래스는 '이 상태에서 허용되는 것'과 '그다음 어디로 가는지'만 안다.
# ---------------------------------------------------------------------------

class Available(ScooterState):
    """[Concrete State] 대여 가능. 가장 많은 동작이 허용되는 출발점."""

    def reserve(self, scooter: Scooter, user: str, now: int) -> None:
        """예약하면 Reserved로. 예약자·시각은 '그 상태의 데이터'이므로 새 상태 객체가 품는다."""
        scooter.change_state(Reserved(user, now))

    def unlock(self, scooter: Scooter, user: str, now: int) -> None:
        """예약 없이 바로 타는 경우."""
        scooter.change_state(Riding(user, now))

    def send_to_maintenance(self, scooter: Scooter) -> None:
        """정비 입고."""
        scooter.change_state(Maintenance())

    def report_lost(self, scooter: Scooter) -> None:
        """주차된 채 GPS 신호가 끊긴 경우."""
        scooter.change_state(Lost())

    def on_battery_changed(self, scooter: Scooter) -> None:
        """대기 중 방전되면 지도에서 대여 불가로 바꾼다."""
        if scooter.battery < LOW_BATTERY:
            scooter.change_state(LowBattery())

    def label(self) -> str:
        """지도 표시 문구."""
        return "대여 가능"


class Reserved(ScooterState):
    """[Concrete State] 예약됨. 예약자와 예약 시각을 '이 상태만의 데이터'로 가진다.

    순진한 코드에서는 reserved_by가 Scooter 필드라 예약이 끝난 뒤에도 값이 남았다.
    여기서는 Reserved 객체가 버려지는 순간 데이터도 함께 사라진다 — 찌꺼기가 생길 수 없다.
    """

    def __init__(self, user: str, reserved_at: int) -> None:
        """예약자와 예약 시각을 기억한다."""
        self.user = user
        self.reserved_at = reserved_at

    def unlock(self, scooter: Scooter, user: str, now: int) -> None:
        """예약자 본인만 잠금 해제할 수 있다. 가드(guard) 조건도 상태 안에 있다."""
        if user != self.user:
            raise IllegalTransition(f"{self.user}님이 예약한 킥보드입니다")
        scooter.change_state(Riding(user, now))

    def tick(self, scooter: Scooter, now: int) -> None:
        """시간 기반 전이: 만료되면 노쇼 수수료를 물리고 Available로 돌아간다."""
        if now - self.reserved_at >= RESERVATION_TTL:
            scooter.charge(f"{self.user} 노쇼", NO_SHOW_FEE)
            scooter.change_state(Available())

    def label(self) -> str:
        """예약자 이름까지 보여 준다 — 상태 데이터를 가진 상태라서 가능한 일."""
        return f"예약됨({self.user})"


class Riding(ScooterState):
    """[Concrete State] 주행 중. 요금 계산 책임이 여기 모인다(SRP: 주행에 관한 것은 주행 상태에)."""

    def __init__(self, rider: str, started_at: int) -> None:
        """탑승자와 출발 시각."""
        self.rider = rider
        self.started_at = started_at

    def end_ride(self, scooter: Scooter, now: int) -> int:
        """요금을 정산하고, 배터리에 따라 다음 상태를 '스스로' 고른다."""
        minutes = max(1, (now - self.started_at + 59) // 60)   # 시작한 분은 1분으로 친다
        fare = UNLOCK_FEE + PER_MINUTE * minutes
        scooter.charge(f"{self.rider} 주행 {minutes}분", fare)
        # 전이 결정이 이 상태 안에 있다: Riding은 자신의 후속 상태(LowBattery/Available)를 안다.
        # 이 '상태끼리 서로를 안다'는 결합이 상태 패턴의 대가다(6절 트레이드오프).
        scooter.change_state(LowBattery() if scooter.battery < LOW_BATTERY else Available())
        return fare

    def label(self) -> str:
        """지도 표시 문구."""
        return "주행 중"


class LowBattery(ScooterState):
    """[Concrete State] 배터리 부족. 대여는 막고, 충전·정비·분실 처리만 받는다."""

    def on_battery_changed(self, scooter: Scooter) -> None:
        """충전 기사가 교체하면 다시 대여 가능."""
        if scooter.battery >= LOW_BATTERY:
            scooter.change_state(Available())

    def send_to_maintenance(self, scooter: Scooter) -> None:
        """정비 입고."""
        scooter.change_state(Maintenance())

    def report_lost(self, scooter: Scooter) -> None:
        """방전된 채 사라지는 경우가 실제로 가장 흔하다."""
        scooter.change_state(Lost())

    def label(self) -> str:
        """지도 표시 문구."""
        return "배터리 부족"


class Maintenance(ScooterState):
    """[Concrete State] 정비 중. unlock을 오버라이드하지 않았으므로 잠금 해제는 '자동으로' 거부된다."""

    def finish_maintenance(self, scooter: Scooter) -> None:
        """정비가 끝나면 배터리 상태에 따라 복귀한다."""
        scooter.change_state(Available() if scooter.battery >= LOW_BATTERY else LowBattery())

    def label(self) -> str:
        """지도 표시 문구."""
        return "정비 중"


class Lost(ScooterState):
    """[Concrete State] 분실 신고. 회수되면 무조건 정비부터 받는다."""

    def send_to_maintenance(self, scooter: Scooter) -> None:
        """회수된 기기는 점검 없이 바로 대여 가능으로 돌리지 않는다 — 규칙이 코드에 드러난다."""
        scooter.change_state(Maintenance())

    def label(self) -> str:
        """지도 표시 문구."""
        return "분실 신고"


# ---------------------------------------------------------------------------
# Context
# ---------------------------------------------------------------------------

class Scooter:
    """[Context] 외부(앱·관제·센서)가 보는 유일한 객체. 상태를 묻지 않고 위임만 한다.

    공개 메서드에 상태 분기가 없다는 점에 주목하라. 새 상태가 추가되어도 이 클래스는
    바뀌지 않는다(OCP). 바뀌는 것은 새 상태 클래스와, 그 상태로 '들어가는' 이웃 상태뿐이다.
    """

    def __init__(self, scooter_id: str, battery: int = 100) -> None:
        """새 킥보드는 Available에서 시작한다."""
        self.scooter_id = scooter_id
        self.battery = battery
        self._state: ScooterState = Available()
        self.charges: list[tuple[str, int]] = []
        self.history: list[str] = []   # 전이 로그 — 한 곳(change_state)에서만 쌓인다

    # --- 상태 객체가 쓰는 협력 메서드 ----------------------------------------------
    def change_state(self, new_state: ScooterState) -> None:
        """상태 객체 전용. 이름에 밑줄을 붙이지 않은 이유는 '다른 클래스(상태)가 부른다'는
        사실을 숨기지 않기 위해서다. 대신 외부 클라이언트용 API가 아님을 문서로 밝힌다.

        모든 전이가 이 한 지점을 지나가므로 로그·통지(옵저버, 11장)·지표 수집을 붙이기 좋다.
        """
        self.history.append(f"{self._state!r} → {new_state!r}")
        self._state = new_state

    def charge(self, reason: str, amount: int) -> None:
        """정산 기록. 상태 객체가 Scooter 내부 리스트를 직접 만지지 않게 하는 좁은 창구."""
        self.charges.append((reason, amount))

    # --- 외부 API: 전부 한 줄 위임 -------------------------------------------------
    def reserve(self, user: str, now: int) -> None:
        """예약."""
        self._state.reserve(self, user, now)

    def unlock(self, user: str, now: int) -> None:
        """잠금 해제."""
        self._state.unlock(self, user, now)

    def end_ride(self, now: int) -> int:
        """반납 후 요금 반환."""
        return self._state.end_ride(self, now)

    def tick(self, now: int) -> None:
        """시간 이벤트."""
        self._state.tick(self, now)

    def update_battery(self, level: int) -> None:
        """배터리 기록은 상태와 무관한 '데이터'라 Context가 하고, 그 의미 해석은 상태에 맡긴다."""
        self.battery = level
        self._state.on_battery_changed(self)

    def send_to_maintenance(self) -> None:
        """정비 입고."""
        self._state.send_to_maintenance(self)

    def finish_maintenance(self) -> None:
        """정비 완료."""
        self._state.finish_maintenance(self)

    def report_lost(self) -> None:
        """분실 신고."""
        self._state.report_lost(self)

    def label(self) -> str:
        """앱 표시 문구."""
        return self._state.label()


def attempt(desc: str, action) -> None:
    """데모용: 동작을 시도하고 불법 전이면 거부 메시지를 출력한다."""
    try:
        action()
        print(f"    {desc}: 성공")
    except IllegalTransition as e:
        print(f"    {desc}: 거부 — {e}")


if __name__ == "__main__":
    print("[1] 정상 흐름: 예약 → 잠금 해제 → 12분 주행 후 반납 (배터리 10%)")
    s = Scooter("KG-001")
    s.reserve("민지", now=0)
    s.unlock("민지", now=120)
    s.update_battery(10)                     # 주행 중 방전: Riding은 이 이벤트를 무시한다
    fare = s.end_ride(now=120 + 12 * 60)
    print(f"    반납 요금 {fare:,}원, 상태: {s.label()}")
    print("    전이 로그:", " | ".join(s.history))

    print("[2] 시간 기반 전이: 예약 만료")
    s2 = Scooter("KG-002")
    s2.reserve("도현", now=1_000)
    s2.tick(now=1_300)                       # 5분 경과: 아무 일도 없음
    print("    5분 뒤:", s2.label())
    s2.tick(now=1_000 + RESERVATION_TTL)
    print("    10분 뒤:", s2.label(), "/ 정산:", s2.charges)

    print("[3] 순진한 코드의 버그 시나리오를 그대로 다시 시도")
    s3 = Scooter("KG-003")
    s3.send_to_maintenance()
    attempt("정비 중 잠금 해제", lambda: s3.unlock("해커", now=2_000))
    s4 = Scooter("KG-004")
    s4.unlock("서윤", now=0)
    attempt("주행 중 분실 신고", s4.report_lost)
    attempt("남의 예약 가로채기", lambda: (s2.reserve("도현", 5_000), s2.unlock("지호", 5_010)))
    print("    KG-003:", s3.label(), "/ KG-004:", s4.label(), "/ KG-002:", s2.label())

    print("[4] 분실 → 회수 → 정비 → 복귀: 회수된 기기는 정비를 건너뛸 수 없다")
    s5 = Scooter("KG-005")
    s5.report_lost()
    attempt("분실 기기 바로 정비 완료 처리", s5.finish_maintenance)
    s5.send_to_maintenance()
    s5.finish_maintenance()
    print("    전이 로그:", " | ".join(s5.history))
