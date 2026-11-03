"""10 전략 — 파이썬다운 변형: 메서드 하나짜리 전략은 그냥 함수로.

상황: 패턴 코드의 정책 클래스들은 결국 calculate() 하나뿐이다. 파이썬은 함수를
변수에 담아 넘길 수 있으니 "FeeInput을 받아 int를 주는 함수"면 전략이 된다.
민재는 등록 데코레이터로 설정 이름과 정책을 잇고, 클래스가 여전히 나은 경우도 본다.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class FeeInput:
    """정책에 넘기는 좁은 입력. 함수 전략이 되어도 이 경계는 그대로다."""
    distance_km: float
    hour: int
    is_raining: bool


# [Strategy] ABC 대신 '호출 모양'이 인터페이스다. 함수든 람다든 모양만 맞으면 된다.
FeePolicy = Callable[[FeeInput], int]

# 설정 이름 -> '정책을 만드는 함수'. 설정에 금액 같은 인자가 들어 있어서 만드는 쪽을 담는다.
POLICY_FACTORIES: dict[str, Callable[..., FeePolicy]] = {}


def register(kind: str) -> Callable:
    """정책을 만드는 함수를 등록부에 올리는 데코레이터. 새 정책은 정의 옆 한 줄로 끝난다."""
    def deco(factory: Callable[..., FeePolicy]) -> Callable[..., FeePolicy]:
        """등록하고 함수를 그대로 돌려준다."""
        POLICY_FACTORIES[kind] = factory
        return factory
    return deco


def standard_distance(q: FeeInput) -> int:
    """[Concrete Strategy] 설정값이 없는 계산. 클래스로 감쌀 이유가 없다."""
    return 3000 + int(q.distance_km * 500) + (1000 if q.is_raining else 0)


@dataclass(frozen=True)
class SurgePricing:
    """[Concrete Strategy] 배율 요금. __call__이 있어 함수처럼 쓰인다.

    클래스를 고른 이유: 설정값(base, multiplier)이 repr에 그대로 찍혀 로그에서 읽힌다.
    상속 없이도 호출 모양이 맞으므로 FeePolicy 자리에 들어간다.
    """
    base: int
    multiplier: float

    def __call__(self, q: FeeInput) -> int:
        """(기본료 + 거리 요금) x 배율."""
        return int((self.base + q.distance_km * 500) * self.multiplier)


@register("distance")
def _distance() -> FeePolicy:
    """설정 -> 함수 정책."""
    return standard_distance


@register("flat")
def _flat(fee: int) -> FeePolicy:
    """설정 -> 람다 정책. 한 줄짜리 계산에 클래스는 과하다."""
    return lambda q: fee


@register("surge")
def _surge(base: int, multiplier: float) -> FeePolicy:
    """설정 -> dataclass 정책."""
    return SurgePricing(base, multiplier)


def build_policy(spec: dict) -> FeePolicy:
    """설정 한 줄을 정책으로. if/elif 대신 등록부를 찾아본다."""
    # "type" 말고 나머지 키는 만드는 함수의 인자로 넘긴다(예: fee=1900).
    args = {k: v for k, v in spec.items() if k != "type"}
    return POLICY_FACTORIES[spec["type"]](**args)


if __name__ == "__main__":
    q = FeeInput(3.2, 23, True)
    print("[1] 등록부로 설정을 정책으로 바꿔 계산")
    for spec in ({"type": "distance"}, {"type": "flat", "fee": 1900},
                 {"type": "surge", "base": 3000, "multiplier": 1.5}):
        policy = build_policy(spec)
        print(f"    {spec['type']:8s} {policy(q)}원")
    print("[2] 로그에 찍히는 모습 — 함수는 이름뿐, dataclass는 설정값까지")
    print("    ", build_policy({"type": "flat", "fee": 1900}))
    print("    ", build_policy({"type": "surge", "base": 3000, "multiplier": 1.5}))
    print("[3] 이미 있는 전략 자리: sorted(key=...)에 넘기는 함수도 전략이다")
    print("    ", sorted(["국밥집", "분식집", "카페"], key=len))
