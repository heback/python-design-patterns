"""파이썬다운 변형: 전략 = 함수. 매개변수는 클로저·partial·호출 가능한 dataclass로.

상황: 02_strategy.py의 정책 클래스들을 다시 보면, 각 클래스의 본질은 calculate()
메서드 하나다. 파이썬에서 함수는 일급 객체이므로 '메서드 하나짜리 인터페이스'는
Callable[[FeeInput], int] 타입으로 대체할 수 있다. 민재는 정책을 함수로 바꿔 보면서
다음 질문에 답하려 한다.

  1) 매개변수(요율)가 있는 정책은 클로저, functools.partial, dataclass 중 무엇으로?
  2) 운영팀 JSON 설정을 함수 정책과 어떻게 연결하나? (등록부 + 등록 데코레이터)
  3) 그렇다면 클래스는 언제 여전히 필요한가? (데모 [2]의 repr 비교가 힌트다)
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from functools import partial
from typing import Any, Callable

# ---------------------------------------------------------------------------
# 공통 재료 (파일 단독 실행을 위해 02와 같은 정의를 다시 둔다)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class FeeInput:
    """정책이 알아야 하는 사실만 담은 좁은 입력. 함수 전략에서도 이 경계는 그대로 유효하다."""

    distance_km: float
    hour: int
    is_raining: bool


def is_night(hour: int, start: int = 22, end: int = 6) -> bool:
    """자정을 넘기는 심야 구간 판정."""
    return hour >= start or hour < end


# [Strategy] 인터페이스가 ABC 대신 '타입 별칭'이 되었다. 구조적 타이핑이므로
# 함수든, 람다든, __call__을 가진 객체든 이 모양이면 모두 전략이다.
FeePolicy = Callable[[FeeInput], int]


# ---------------------------------------------------------------------------
# 방법 ① 매개변수 없는 정책 = 그냥 함수
# ---------------------------------------------------------------------------
def standard_distance(q: FeeInput) -> int:
    """[Concrete Strategy] A안 기본 요율. 설정이 없으니 클래스로 감쌀 이유도 없다."""
    fee = 3000 + int(q.distance_km * 500)
    fee += 1000 if q.is_raining else 0
    fee += 1500 if is_night(q.hour) else 0
    return fee


# ---------------------------------------------------------------------------
# 방법 ② 클로저 — 요율을 '캡처'한 함수를 만들어 돌려준다
# ---------------------------------------------------------------------------
def make_distance(base: int = 3000, per_km: int = 500, rain: int = 1000, night: int = 1500) -> FeePolicy:
    """요율이 다른 거리 정책을 만든다. 클로저가 생성자 역할, 캡처 변수가 필드 역할을 한다.

    단점: 만들어진 함수의 repr은 '<function make_distance.<locals>.policy ...>'라서
    A/B 로그에 '어떤 요율이었는지'가 남지 않는다. 데모 [2]에서 확인하라.
    """

    def policy(q: FeeInput) -> int:
        """캡처한 base/per_km/rain/night로 계산한다."""
        fee = base + int(q.distance_km * per_km)
        fee += rain if q.is_raining else 0
        fee += night if is_night(q.hour) else 0
        return fee

    return policy


# ---------------------------------------------------------------------------
# 방법 ③ functools.partial — 키워드 인자를 미리 채운 함수
# ---------------------------------------------------------------------------
def tiered(q: FeeInput, *, tiers: list[tuple[float, int]], over_fee: int,
           rain: int = 500, night: int = 1500) -> int:
    """[Concrete Strategy] B안 구간제. 설정을 키워드 전용 인자로 받는 '평범한 함수'다.

    partial(tiered, tiers=..., over_fee=...)로 q만 남은 FeePolicy를 만든다.
    클로저와 달리 partial 객체의 repr에는 채운 인자가 보이므로 로그 가독성이 낫다.
    """
    fee = next((f for max_km, f in sorted(tiers) if q.distance_km <= max_km), over_fee)
    fee += rain if q.is_raining else 0
    fee += night if is_night(q.hour) else 0
    return fee


# ---------------------------------------------------------------------------
# 방법 ④ 호출 가능한 frozen dataclass — '함수처럼 쓰이는 값 객체'
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class SurgePricing:
    """[Concrete Strategy] 수요 급증 배율제. 함수처럼 호출되지만 필드와 repr을 가진다.

    클래스를 택한 이유: (1) repr이 'SurgePricing(base=3000, multiplier=1.5)'로 자동 생성돼
    로그·디버깅에 그대로 쓰인다, (2) frozen이므로 해시 가능 → 캐시 키나 집합 원소가 된다,
    (3) dataclasses.asdict()로 설정을 다시 JSON으로 직렬화할 수 있다.
    ABC를 상속하지 않아도 __call__ 시그니처만 맞으면 FeePolicy로 통한다(덕 타이핑).
    """

    base: int
    multiplier: float

    def __call__(self, q: FeeInput) -> int:
        """기본료 + 거리 요금에 배율을 곱한다. 비·심야는 배율에 이미 반영됐다고 본다."""
        return int((self.base + q.distance_km * 500) * self.multiplier)


# ---------------------------------------------------------------------------
# 설정 연결: 이름 → '정책 팩토리' 등록부 + 등록 데코레이터
# ---------------------------------------------------------------------------
# 값이 FeePolicy가 아니라 'FeePolicy를 만드는 함수'인 이유: 설정에 요율 같은 인자가
# 들어 있으므로, 등록부는 인자를 받아 정책을 조립하는 쪽이어야 한다.
POLICY_FACTORIES: dict[str, Callable[..., FeePolicy]] = {}


def register(kind: str) -> Callable[[Callable[..., FeePolicy]], Callable[..., FeePolicy]]:
    """정책 팩토리를 등록부에 올리는 데코레이터.

    새 정책을 추가할 때 등록부 dict를 직접 편집하지 않고, 정책 정의 옆에 @register를
    붙이면 끝난다. '정책을 추가하는 사람'이 수정하는 파일이 하나로 줄어든다(OCP).
    중복 이름은 조용히 덮어쓰지 않고 실패시킨다 — 두 팀이 같은 이름을 쓰는 사고 방지.
    """

    def deco(factory: Callable[..., FeePolicy]) -> Callable[..., FeePolicy]:
        """실제 등록. 팩토리를 그대로 돌려주므로 직접 호출도 여전히 가능하다."""
        if kind in POLICY_FACTORIES:
            raise ValueError(f"이미 등록된 정책: {kind}")
        POLICY_FACTORIES[kind] = factory
        return factory

    return deco


@register("distance")
def _distance_factory(**cfg: Any) -> FeePolicy:
    """설정 → 클로저 정책."""
    return make_distance(**cfg)


@register("tiered")
def _tiered_factory(tiers: list[list[float]], over_fee: int, **cfg: Any) -> FeePolicy:
    """설정 → partial 정책. JSON에는 튜플이 없으므로 리스트를 튜플로 바꿔 둔다."""
    return partial(tiered, tiers=[(t[0], int(t[1])) for t in tiers], over_fee=over_fee, **cfg)


@register("flat")
def _flat_factory(fee: int) -> FeePolicy:
    """설정 → 람다 정책. 한 줄짜리 알고리즘에 클래스를 만드는 것은 과잉이다."""
    return lambda q: fee


@register("surge")
def _surge_factory(base: int, multiplier: float) -> FeePolicy:
    """설정 → dataclass 정책."""
    return SurgePricing(base, multiplier)


def build_policy(spec: dict[str, Any]) -> FeePolicy:
    """설정 한 항목을 정책으로. 선택 로직은 여전히 Context 바깥, 이 함수 한 곳에 있다."""
    cfg = dict(spec)
    kind = cfg.pop("type")
    if kind not in POLICY_FACTORIES:
        raise ValueError(f"알 수 없는 정책 type: {kind!r} (가능: {sorted(POLICY_FACTORIES)})")
    return POLICY_FACTORIES[kind](**cfg)


# ---------------------------------------------------------------------------
# [Context] — 전략이 함수가 되어도 Context의 모양은 거의 같다
# ---------------------------------------------------------------------------
@dataclass
class DeliveryFeeService:
    """[Context] 정책 콜러블을 보유하고 위임한다. 필드 하나 교체로 정책이 바뀐다."""

    policy: FeePolicy

    def quote(self, q: FeeInput, *, is_subscriber: bool = False, store_discount: int = 0) -> int:
        """공통 규칙(구독 무료·가게 할인)만 여기서, 요금 산정은 policy(q)에 맡긴다."""
        if is_subscriber:
            return 0
        return max(0, self.policy(q) - store_discount)


# 운영팀이 내려 주는 JSON. 02에서는 파이썬 dict였지만 이제 진짜 텍스트 설정이다.
REGION_CONFIG_JSON = """
{
  "seoul-gangnam":  {"type": "distance"},
  "seoul-mapo":     {"type": "distance", "per_km": 400},
  "busan-haeundae": {"type": "tiered", "tiers": [[2, 2500], [5, 4000]], "over_fee": 6000},
  "jeju":           {"type": "flat", "fee": 1900},
  "incheon":        {"type": "surge", "base": 3000, "multiplier": 1.5}
}
"""


if __name__ == "__main__":
    q = FeeInput(distance_km=3.2, hour=23, is_raining=True)

    print("[1] 네 가지 형태의 전략이 같은 자리에 꽂힌다")
    config = json.loads(REGION_CONFIG_JSON)
    services = {region: DeliveryFeeService(build_policy(spec)) for region, spec in config.items()}
    for region, svc in services.items():
        print(f"    {region:15s} → {svc.quote(q):>5}원")

    print("[2] 로그에 남는 정책 이름(repr) — 클래스가 여전히 필요한 이유 중 하나")
    for region in ("seoul-mapo", "busan-haeundae", "incheon"):
        # 메모리 주소(at 0x...)는 실행마다 달라 교재 출력에서 지운다. 정보량 비교에는 영향 없다.
        r = re.sub(r" at 0x[0-9a-f]+", "", repr(services[region].policy))
        print(f"    {region:15s} {r[:70]}{'…' if len(r) > 70 else ''}")

    print("[3] 테스트에서는 람다 하나로 정책을 대체할 수 있다(가짜 객체 클래스 불필요)")
    test_svc = DeliveryFeeService(policy=lambda _: 4000)
    print("    가게 할인 1,500원 적용:", test_svc.quote(q, store_discount=1500), "원")

    print("[4] 런타임 교체도 필드 대입 한 번")
    services["jeju"].policy = standard_distance
    print("    jeju(정액 이벤트 종료 후) →", services["jeju"].quote(q), "원")
