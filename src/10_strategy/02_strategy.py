"""전략 패턴 적용: 배달비 알고리즘을 교체 가능한 정책 객체로 분리한다.

상황: 01_naive.py에서 Order.delivery_fee()는 지역별 요금표, 할증, 구독 무료, 가게 할인을
모두 if 문으로 품고 있었다. 민재는 '변하는 것'(요금 산정 알고리즘 = 정책)과
'변하지 않는 것'(구독 무료·가게 할인이라는 상품 공통 규칙)을 나누기로 한다.

  - FeePolicy(ABC)            [Strategy]          요금 알고리즘의 공통 인터페이스
  - DistancePolicy 등          [Concrete Strategy] A안·B안·정액제 각각의 알고리즘
  - DeliveryFeeService         [Context]           정책을 '보유'하고 위임만 한다
  - build_policy()             [선택 로직]          운영팀 설정(dict/JSON)을 정책 객체로 바꾼다

핵심 판단 두 가지를 코드에서 확인하라.
  1) 전략에게는 Order가 아니라 좁은 입력(FeeInput)만 넘긴다 → 정책 단독 테스트가 쉬워진다.
  2) '어떤 정책을 쓸지' 결정은 Context 안이 아니라 바깥(조립 지점)에 있다.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


# ---------------------------------------------------------------------------
# 전략에게 넘길 '좁은 입력'
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class FeeInput:
    """요금 정책이 알아야 하는 사실만 담은 값 객체.

    전략에게 Order 전체를 넘기면 전략이 Order의 내부 구조(customer.is_subscriber,
    store.promo_discount …)에 결합된다. 필요한 사실만 뽑아 넘기면
      - 정책 테스트에 FeeInput(3.2, 12, False) 한 줄이면 충분하고,
      - Order 구조가 바뀌어도 정책 클래스는 영향을 받지 않는다.
    frozen=True: 정책이 입력을 고쳐서 다음 계산에 영향을 주는 일을 원천 차단한다.
    """

    distance_km: float
    hour: int          # 0~23
    is_raining: bool


def is_night(hour: int, start: int, end: int) -> bool:
    """심야 시간대 판정. 자정을 넘기는 구간(22시~6시)을 한 곳에서 처리한다.

    naive 코드에서 A안·B안이 각자 'hour >= 22 or hour < 6'을 복제하다 기준이
    어긋났다. 판정을 함수로 빼 두면 정책은 '몇 시부터'라는 매개변수만 다르게 갖는다.
    """
    return hour >= start or hour < end


# ---------------------------------------------------------------------------
# [Strategy] 와 [Concrete Strategy]
# ---------------------------------------------------------------------------
class FeePolicy(ABC):
    """[Strategy] 배달비 산정 알고리즘의 공통 인터페이스.

    DeliveryFeeService(Context)는 이 추상 타입에만 의존한다(인터페이스에 프로그래밍).
    Protocol 대신 ABC를 쓴 이유: 운영 설정으로 정책을 '생성'하는 코드가 있어서,
    calculate()를 빠뜨린 정책 클래스를 인스턴스화 시점에 바로 실패시키는 편이 안전하다.
    """

    #: 로그·A/B 리포트에 남길 정책 이름. 함수가 아닌 클래스로 둔 이유 중 하나다.
    name: str = "abstract"

    @abstractmethod
    def calculate(self, q: FeeInput) -> int:
        """할증까지 포함한 '정책 요금'(원)을 돌려준다. 구독·가게 할인은 여기서 다루지 않는다."""

    def describe(self) -> str:
        """정책 설정을 사람이 읽는 문자열로. A/B 실험 로그에 그대로 남긴다."""
        return self.name


class DistancePolicy(FeePolicy):
    """[Concrete Strategy] A안: 기본료 + km당 요금 + 우천/심야 할증.

    상태(요율)를 생성자 매개변수로 받는다. 같은 클래스로 '강남 요율'과 '마포 요율'을
    서로 다른 인스턴스로 만들 수 있으므로 지역이 늘어도 클래스는 늘지 않는다.
    """

    name = "distance"

    def __init__(self, base: int = 3000, per_km: int = 500, rain: int = 1000,
                 night: int = 1500, night_start: int = 22, night_end: int = 6) -> None:
        """요율을 보관한다. 기본값은 민재의 최초 요구사항(3,000원 + km당 500원)이다."""
        self.base, self.per_km = base, per_km
        self.rain, self.night = rain, night
        self.night_start, self.night_end = night_start, night_end

    def calculate(self, q: FeeInput) -> int:
        """거리 비례 요금에 할증을 더한다. Order도, 지역도 모른다 — 알 필요가 없다."""
        fee = self.base + int(q.distance_km * self.per_km)
        if q.is_raining:
            fee += self.rain
        if is_night(q.hour, self.night_start, self.night_end):
            fee += self.night
        return fee

    def describe(self) -> str:
        """실험 로그용 요약."""
        return f"distance(base={self.base}, per_km={self.per_km})"


class TieredPolicy(FeePolicy):
    """[Concrete Strategy] B안: 거리 구간제 요금.

    naive 코드에서는 A안의 할증 분기를 복사해 왔지만, 여기서는 할증 판단이
    is_night()를 공유하고 금액만 매개변수로 다르다. 복제가 사라졌다.
    """

    name = "tiered"

    def __init__(self, tiers: list[tuple[float, int]], over_fee: int,
                 rain: int = 500, night: int = 1500) -> None:
        """tiers는 (최대 km, 요금) 목록. 정렬해 두어 설정 순서 실수에 강하게 한다."""
        self.tiers = sorted(tiers)
        self.over_fee = over_fee     # 마지막 구간을 넘는 거리의 요금
        self.rain, self.night = rain, night

    def calculate(self, q: FeeInput) -> int:
        """구간 요금표에서 첫 번째로 맞는 구간을 찾는다."""
        fee = next((f for max_km, f in self.tiers if q.distance_km <= max_km), self.over_fee)
        if q.is_raining:
            fee += self.rain
        if is_night(q.hour, 22, 6):   # 심야 기준을 A안과 통일했다(구간제 실험의 대상은 요금표지 심야 기준이 아니므로)
            fee += self.night
        return fee

    def describe(self) -> str:
        """실험 로그용 요약."""
        return f"tiered({len(self.tiers)} tiers)"


class FlatPolicy(FeePolicy):
    """[Concrete Strategy] 이벤트 정액제. 할증도 없다.

    '정책마다 할증이 있다'고 가정해 상위 클래스에 할증 로직을 넣었다면 이 클래스는
    그것을 무시하도록 오버라이드해야 했을 것이다. 전략 인터페이스를 calculate() 하나로
    좁게 둔 덕분에 정액제는 그냥 정액을 돌려준다.
    """

    name = "flat"

    def __init__(self, fee: int) -> None:
        """정액 요금을 보관한다."""
        self.fee = fee

    def calculate(self, q: FeeInput) -> int:
        """입력과 무관하게 정액. 인터페이스를 맞추려고 q를 받지만 쓰지 않는다."""
        return self.fee

    def describe(self) -> str:
        """실험 로그용 요약."""
        return f"flat({self.fee})"


# ---------------------------------------------------------------------------
# 도메인 객체 — 이제 요금 정책을 모른다
# ---------------------------------------------------------------------------
@dataclass
class Order:
    """주문 엔티티. delivery_fee()가 사라졌다 — 요금 정책은 Order의 변경 이유가 아니다(SRP)."""

    customer_name: str
    is_subscriber: bool
    store_promo_discount: int
    distance_km: float
    region: str
    hour: int = 12
    is_raining: bool = False

    def fee_input(self) -> FeeInput:
        """주문에서 정책이 필요로 하는 사실만 추출한다. 결합 지점이 이 한 메서드로 모인다."""
        return FeeInput(self.distance_km, self.hour, self.is_raining)


# ---------------------------------------------------------------------------
# [Context]
# ---------------------------------------------------------------------------
class DeliveryFeeService:
    """[Context] 정책 객체를 보유하고 요금 계산을 위임한다.

    상속이 아닌 합성: 정책을 런타임에 바꿔 끼울 수 있어야 하므로(A/B 실험, 이벤트 기간)
    DeliveryFeeService의 서브클래스를 정책마다 만드는 대신 정책 객체를 '갖는다'.

    여기에 남겨 둔 것은 '모든 정책에 공통인 규칙'뿐이다 — 구독 무료와 가게 부담 할인.
    이것들은 실험 대상이 아니라 회원 약관·가게 계약이므로 변하는 것이 아니라고 판단했다.
    만약 운영팀이 구독 혜택까지 실험하겠다고 하면, 그때 이 규칙을 정책 쪽으로 옮긴다.
    """

    def __init__(self, policy: FeePolicy) -> None:
        """시작 정책을 주입받는다. 서비스는 어떤 구체 정책인지 묻지 않는다."""
        self.policy = policy

    def quote(self, order: Order) -> int:
        """최종 배달비. 주목: 여기에는 정책 종류를 묻는 if가 하나도 없다."""
        if order.is_subscriber:
            return 0
        fee = self.policy.calculate(order.fee_input())
        return max(0, fee - order.store_promo_discount)


# ---------------------------------------------------------------------------
# 선택 로직: 설정 → 정책 객체 (Context 바깥, 조립 지점)
# ---------------------------------------------------------------------------
# 이름 → 정책 클래스 등록부. 새 정책은 클래스 하나 + 이 dict 한 줄로 끝난다(OCP).
# if/elif가 완전히 사라진 것은 아니다 — '선택'이라는 행위는 남는다. 다만 그 선택이
# Context가 아닌 한 곳(여기)으로 모였고, 데이터(dict 조회)로 바뀌었다.
POLICY_TYPES: dict[str, type[FeePolicy]] = {
    "distance": DistancePolicy,
    "tiered": TieredPolicy,
    "flat": FlatPolicy,
}


def build_policy(spec: dict[str, Any]) -> FeePolicy:
    """운영팀 설정 한 항목을 정책 객체로 만든다. 사실상 작은 팩토리다(01장 참고).

    spec 예: {"type": "flat", "fee": 1900}. 'type' 외의 키는 생성자 인자로 전달한다.
    알 수 없는 type은 조용히 기본값으로 넘기지 않고 즉시 실패시킨다 — 잘못된 설정으로
    배달비가 엉뚱하게 매겨지는 것보다 배포 전에 터지는 편이 낫다.
    """
    kwargs = dict(spec)
    kind = kwargs.pop("type")
    try:
        cls = POLICY_TYPES[kind]
    except KeyError:
        raise ValueError(f"알 수 없는 정책 type: {kind!r}") from None
    return cls(**kwargs)


# 운영팀이 관리하는 지역별 설정(실제로는 JSON 파일이나 설정 서버에서 읽는다).
# 코드가 아니므로 '이번 주 제주 정액제' 같은 변경이 재배포 없이 가능해진다.
REGION_CONFIG: dict[str, dict[str, Any]] = {
    "seoul-gangnam": {"type": "distance"},
    "busan-haeundae": {"type": "tiered", "tiers": [(2, 2500), (5, 4000)], "over_fee": 6000},
    "jeju": {"type": "flat", "fee": 1900},
}


if __name__ == "__main__":
    print("[1] 정책 단독 테스트 — Order 없이 FeeInput 한 줄이면 된다")
    rainy_night = FeeInput(distance_km=3.2, hour=23, is_raining=True)
    for p in (DistancePolicy(), TieredPolicy([(2, 2500), (5, 4000)], 6000), FlatPolicy(1900)):
        print(f"    {p.describe():32s} → {p.calculate(rainy_night):>5}원")

    print("[2] 지역 설정으로 서비스 조립 — 선택은 설정, 계산은 정책, 위임은 서비스")
    services = {region: DeliveryFeeService(build_policy(spec)) for region, spec in REGION_CONFIG.items()}
    order = Order("도윤", False, store_promo_discount=1000, distance_km=3.2,
                  region="busan-haeundae", hour=23, is_raining=True)
    svc = services[order.region]
    print(f"    {order.region}: {svc.policy.describe()} → {svc.quote(order)}원 (가게 할인 1,000원 반영)")

    print("[3] 새벽 5시대 주문 — 이제 두 정책의 심야 기준이 같다")
    for region in ("seoul-gangnam", "busan-haeundae"):
        o = Order("서아", False, 0, distance_km=1.0, region=region, hour=5)
        print(f"    {region:15s} → {services[region].quote(o)}원")

    print("[4] 운영 중 정책 교체(A/B 실험 전환) — 서비스 클래스는 그대로")
    gangnam = services["seoul-gangnam"]
    o = Order("지우", False, 0, distance_km=3.2, region="seoul-gangnam")
    print(f"    교체 전 {gangnam.policy.describe():32s} → {gangnam.quote(o)}원")
    gangnam.policy = build_policy({"type": "tiered", "tiers": [(3, 3000), (6, 4500)], "over_fee": 6500})
    print(f"    교체 후 {gangnam.policy.describe():32s} → {gangnam.quote(o)}원")

    print("[5] 구독 회원 — 어떤 정책이든 0원(Context의 공통 규칙)")
    print(f"    jeju → {services['jeju'].quote(Order('하준', True, 0, 4.0, 'jeju'))}원")

    print("[6] 오타 난 설정은 즉시 실패한다")
    try:
        build_policy({"type": "flatt", "fee": 1000})
    except ValueError as e:
        print("    ValueError:", e)
