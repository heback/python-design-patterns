"""[13장 상태 · 전략과의 비교] 한 Context 안에 전략(요금 정책)과 상태(대여 생명주기)를 나란히 둔다.

상황: 킥고 운영팀은 도시·시간대별 요금 정책을 수시로 바꾼다(10장의 전략 패턴 그대로).
같은 `Scooter`에 02에서 만든 상태 패턴도 들어 있다. 두 패턴의 클래스 다이어그램은 거의
같다 — Context가 추상 타입 필드를 들고 있고 호출을 위임한다. 이 파일은 둘을 한 클래스에
나란히 놓아, 구조가 같아도 '누가, 언제, 왜 교체하는가'가 완전히 다르다는 것을 보인다.

  - 요금 정책(Strategy): 바깥(운영 콘솔)이 `set_pricing()`으로 교체한다. 정책끼리는 서로 모른다.
  - 생명주기(State): 상태 객체가 사건에 반응해 스스로 교체한다. 상태는 후속 상태를 안다.

마지막 데모는 '전이 책임을 바깥(클라이언트)에 두면 어떻게 되는가'를 보여 준다:
상태 객체가 사실상 전략이 되고, 순진한 코드의 if 분기가 클라이언트로 이사 간다.

02와 겹치지 않게 상태는 셋(Available, Riding, LowBattery)으로 줄였다.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

LOW_BATTERY = 15


class IllegalTransition(Exception):
    """현재 상태에서 허용되지 않는 동작."""


# ---------------------------------------------------------------------------
# 전략 계열: 요금 정책 — "어떻게 계산할 것인가"의 교체 가능한 변형
# ---------------------------------------------------------------------------

class PricingPolicy(ABC):
    """[Strategy] 요금 계산 규칙. 입력은 주행 시간(분) 하나뿐인 좁은 인터페이스다.

    전략은 Context의 상태 기계를 전혀 모른다. 어떤 정책이 다른 정책으로 '넘어가는' 일도
    없다. 교체는 언제나 바깥의 결정이다 — 이것이 상태 객체와의 첫 번째 차이다.
    """

    @abstractmethod
    def fare(self, minutes: int) -> int:
        """요금(원)."""


@dataclass(frozen=True)
class StandardPricing(PricingPolicy):
    """[Concrete Strategy] 기본 요금 + 분당 요금. frozen: 정책 값은 공유돼도 안전해야 한다."""

    unlock_fee: int = 1_000
    per_minute: int = 150

    def fare(self, minutes: int) -> int:
        """기본 요금 계산."""
        return self.unlock_fee + self.per_minute * minutes


@dataclass(frozen=True)
class NightPricing(PricingPolicy):
    """[Concrete Strategy] 심야 할증: 분당 요금만 1.5배."""

    base: StandardPricing = StandardPricing()

    def fare(self, minutes: int) -> int:
        """기본 정책을 합성해 재사용한다(상속 대신 합성 — 할증 대상이 바뀌어도 이 클래스만 고친다)."""
        return self.base.unlock_fee + int(self.base.per_minute * 1.5) * minutes


# ---------------------------------------------------------------------------
# 상태 계열: 대여 생명주기 — "지금 무엇이 허용되고, 다음은 어디인가"
# ---------------------------------------------------------------------------

class RentalState(ABC):
    """[State] 상태는 '사건에 대한 반응'과 '다음 상태 결정'을 함께 가진다."""

    def unlock(self, scooter: Scooter, user: str, now: int) -> None:
        """기본은 거부."""
        raise IllegalTransition(f"[{self.label()}] 잠금 해제 불가")

    def end_ride(self, scooter: Scooter, now: int) -> int:
        """기본은 거부."""
        raise IllegalTransition(f"[{self.label()}] 반납 불가")

    @abstractmethod
    def label(self) -> str:
        """표시 문구."""


class Available(RentalState):
    """[Concrete State] 대여 가능."""

    def unlock(self, scooter: Scooter, user: str, now: int) -> None:
        """주행 시작. 이 순간의 요금 정책을 Riding에 '고정'해 넘긴다(아래 Riding 설명)."""
        if scooter.battery < LOW_BATTERY:
            # 전이 가드도 상태 안에 있다. 클라이언트는 배터리 규칙을 몰라도 된다.
            # 거부하면서 상태를 바로잡는 이유: 센서 보고가 늦어 아직 Available로 남아 있던
            # 기기를 발견한 순간 지도에서 내려야 다음 사용자가 헛걸음하지 않는다.
            scooter.change_state(LowBattery())
            raise IllegalTransition("배터리 부족으로 대여할 수 없습니다")
        scooter.change_state(Riding(user, now, scooter.pricing))

    def label(self) -> str:
        """표시 문구."""
        return "대여 가능"


class Riding(RentalState):
    """[Concrete State] 주행 중 — 상태와 전략이 만나는 지점.

    잠금 해제 시점의 PricingPolicy를 필드로 붙잡아 둔다. 운영팀이 주행 도중 정책을
    바꿔도(전략 교체) 이미 출발한 손님에게는 소급 적용되지 않는다. '정책은 언제든
    바뀌어도 되지만, 계약은 시작 시점에 확정된다'는 업무 규칙을 상태 데이터가 표현한다.
    """

    def __init__(self, rider: str, started_at: int, pricing: PricingPolicy) -> None:
        """탑승자, 출발 시각, 출발 시점의 요금 정책."""
        self.rider = rider
        self.started_at = started_at
        self.pricing = pricing

    def end_ride(self, scooter: Scooter, now: int) -> int:
        """요금은 전략에 위임하고, 다음 상태는 스스로 정한다 — 한 메서드 안에서 두 패턴이 협력한다."""
        minutes = max(1, (now - self.started_at + 59) // 60)
        fare = self.pricing.fare(minutes)               # Strategy에 위임: "얼마인가"
        scooter.change_state(                           # State가 결정: "다음은 어디인가"
            LowBattery() if scooter.battery < LOW_BATTERY else Available())
        return fare

    def label(self) -> str:
        """표시 문구."""
        return f"주행 중({self.rider})"


class LowBattery(RentalState):
    """[Concrete State] 배터리 부족 — 잠금 해제·반납 모두 기본(거부)을 그대로 쓴다."""

    def label(self) -> str:
        """표시 문구."""
        return "배터리 부족"


class Scooter:
    """[Context] 전략 슬롯과 상태 슬롯을 하나씩 가진다. 두 슬롯의 '교체 경로'를 비교해 읽어라."""

    def __init__(self, battery: int = 100) -> None:
        """기본 정책·Available로 시작."""
        self.battery = battery
        self.pricing: PricingPolicy = StandardPricing()   # 전략: 공개 속성/세터로 바깥이 바꾼다
        self._state: RentalState = Available()             # 상태: 클라이언트용 세터 없음 — change_state()는 상태 객체 전용
        self.log: list[str] = []

    def set_pricing(self, policy: PricingPolicy, by: str) -> None:
        """전략 교체 창구 — 호출자는 '바깥'(운영 콘솔, 설정, A/B 테스트 배정기)이다.

        어떤 정책에서 어떤 정책으로든, 어느 순간에든 바꿀 수 있다. 정책들 사이에
        허용/불허 전이라는 개념 자체가 없다. 그래서 검사할 불변식도 없다.
        """
        self.log.append(f"[전략 교체] {by}: {type(self.pricing).__name__} → {type(policy).__name__}")
        self.pricing = policy

    def change_state(self, new_state: RentalState) -> None:
        """상태 교체 창구 — 호출자는 '안쪽'(현재 상태 객체)뿐이다."""
        self.log.append(f"[상태 전이] {type(self._state).__name__} → {type(new_state).__name__}")
        self._state = new_state

    def unlock(self, user: str, now: int) -> None:
        """위임."""
        self._state.unlock(self, user, now)

    def end_ride(self, now: int) -> int:
        """위임."""
        return self._state.end_ride(self, now)

    def label(self) -> str:
        """위임."""
        return self._state.label()


# ---------------------------------------------------------------------------
# 반례: 전이 책임을 클라이언트에 두면?
# ---------------------------------------------------------------------------

def app_server_end_ride(scooter: Scooter, now: int) -> int:
    """앱 서버가 '다음 상태'를 직접 고르는 설계(상태를 전략처럼 다루기)를 흉내 낸다.

    상태 객체에서 change_state 호출을 빼고 클라이언트가 결정하게 하면, 클라이언트는
    현재 상태를 알아내 분기할 수밖에 없다. 01_naive.py의 if 사슬이 사라진 게 아니라
    Scooter 밖으로 이사 온 것이다. 게다가 이런 클라이언트가 둘(앱, 관제)이 되면
    전이 규칙도 두 벌이 된다. 이 함수는 '이렇게 하지 말라'는 예시다.
    이 함수가 change_state()를 부를 수 있다는 것 자체가 관례 기반 캡슐화의 한계다 —
    파이썬은 '상태 객체만 호출'을 강제하지 못하고, 문서와 리뷰가 지킨다.
    """
    state = scooter._state                     # ⚠ 캡슐화 위반: 내부 상태를 꺼내 봐야만 한다
    if isinstance(state, Riding):              # ⚠ 타입 분기가 돌아왔다
        minutes = max(1, (now - state.started_at + 59) // 60)
        fare = state.pricing.fare(minutes)
        # ⚠ 배터리 규칙도 클라이언트가 알아야 한다. 관제 서버가 같은 규칙을 다르게 쓰면 끝이다.
        scooter.change_state(LowBattery() if scooter.battery < LOW_BATTERY else Available())
        return fare
    raise IllegalTransition("주행 중이 아닙니다")


if __name__ == "__main__":
    print("[1] 운영 콘솔이 요금 전략을 바꾸고, 상태는 사건에 반응해 스스로 바뀐다")
    s = Scooter(battery=80)
    s.unlock("민지", now=0)                                  # 상태 전이(안쪽)
    s.set_pricing(NightPricing(), by="운영 콘솔 22:00 스케줄")  # 전략 교체(바깥) — 주행 도중에!
    fare = s.end_ride(now=10 * 60)                          # 상태 전이(안쪽)
    print(f"    민지 요금: {fare:,}원 (출발 시점 기본 요금 적용 — 소급 없음)")
    s.unlock("도현", now=1_000)
    print(f"    도현 요금: {s.end_ride(now=1_000 + 10 * 60):,}원 (출발 시점이 심야 요금)")
    for line in s.log:
        print("   ", line)

    print("[2] 전략은 아무 때나 무엇으로든 바꿔도 된다. 상태는 그렇지 않다")
    s.set_pricing(StandardPricing(), by="A/B 테스트 배정기")
    s.set_pricing(NightPricing(), by="A/B 테스트 배정기")
    print("    정책 두 번 교체: 검사할 불변식이 없으므로 아무 문제 없음")
    try:
        s.end_ride(now=5_000)
    except IllegalTransition as e:
        print("    주행 중이 아닌데 반납 시도 →", e)

    print("[3] 가드가 상태 안에 있으므로 클라이언트는 배터리 규칙을 모른다")
    weak = Scooter(battery=9)
    try:
        weak.unlock("서윤", now=0)
    except IllegalTransition as e:
        print("    거부:", e, "/ 현재:", weak.label())

    print("[4] 반례: 전이 결정을 앱 서버로 옮기면 분기가 돌아온다")
    t = Scooter(battery=40)
    t.unlock("지호", now=0)
    t.battery = 12                                           # 주행 중 방전
    print(f"    app_server_end_ride → {app_server_end_ride(t, now=300):,}원, 상태 {t.label()}")
    print("    (동작은 같지만 if isinstance 분기와 배터리 규칙이 Scooter 밖에 한 벌 더 생겼다)")
