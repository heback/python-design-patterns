"""연습문제 4 해설: 할증을 요금표와 독립적으로 실험하기 — 전략 '슬롯'을 둘로 나눈다.

상황: 운영팀이 "요금표(A안/B안)와 우천 할증(정액 1,000원 / 거리 비례)을 따로 조합해
2×2 실험을 하고 싶다"고 한다. 02_strategy.py처럼 할증이 각 요금표 클래스 안에 들어
있으면 조합마다 클래스가 필요해 2×2=4개, 3×3이면 9개로 곱해진다.

해결: 변하는 축이 둘이면 전략도 둘이다. Context가 base 전략 하나와 surcharge 전략
목록을 따로 보유하면 조합은 '클래스 정의'가 아니라 '조립'으로 표현된다(N×M → N+M).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable


@dataclass(frozen=True)
class FeeInput:
    """정책에 넘기는 좁은 입력."""

    distance_km: float
    hour: int
    is_raining: bool


# 두 개의 전략 축. 둘 다 함수 모양으로 충분하다(상태 없음 또는 클로저로 캡처).
BaseFee = Callable[[FeeInput], int]        # [Strategy 1] 기본 요금표
Surcharge = Callable[[FeeInput], int]      # [Strategy 2] 할증 규칙 하나(해당 없으면 0)


def distance_base(q: FeeInput) -> int:
    """[Concrete Strategy 1] A안 기본 요금: 3,000원 + km당 500원."""
    return 3000 + int(q.distance_km * 500)


def tiered_base(q: FeeInput) -> int:
    """[Concrete Strategy 1] B안 기본 요금: 2km 2,500 / 5km 4,000 / 초과 6,000."""
    return 2500 if q.distance_km <= 2 else 4000 if q.distance_km <= 5 else 6000


def flat_rain(q: FeeInput) -> int:
    """[Concrete Strategy 2] 우천 정액 할증 1,000원."""
    return 1000 if q.is_raining else 0


def per_km_rain(q: FeeInput) -> int:
    """[Concrete Strategy 2] 우천 거리 비례 할증: km당 200원. 먼 배달일수록 라이더 부담이 크다는 가설."""
    return int(q.distance_km * 200) if q.is_raining else 0


def night(q: FeeInput) -> int:
    """[Concrete Strategy 2] 심야 할증 1,500원. 실험 대상은 아니지만 같은 슬롯에 꽂힌다."""
    return 1500 if q.hour >= 22 or q.hour < 6 else 0


@dataclass
class DeliveryFeeService:
    """[Context] 기본 요금 전략 1개 + 할증 전략 N개를 보유한다.

    할증을 리스트로 둔 이유: 할증은 서로 '더해지는' 관계라 순서·개수가 자유롭다.
    만약 할증이 기본 요금을 '감싸며 변형'(예: 배율 곱하기)한다면 그것은 06장의
    데코레이터에 가까워진다 — 전략은 알고리즘을 '교체', 데코레이터는 '덧입힘'.
    """

    base: BaseFee
    surcharges: list[Surcharge] = field(default_factory=list)

    def quote(self, q: FeeInput) -> int:
        """기본 요금 + 모든 할증의 합. 어떤 조합인지 묻는 if가 없다."""
        return self.base(q) + sum(s(q) for s in self.surcharges)


if __name__ == "__main__":
    q = FeeInput(distance_km=4.5, hour=21, is_raining=True)
    print("4.5km, 비, 21시 주문 — 2×2 실험 조합")
    # 조합 4개를 '클래스 4개'가 아니라 '조립 4번'으로 만든다.
    for base in (distance_base, tiered_base):
        for rain in (flat_rain, per_km_rain):
            svc = DeliveryFeeService(base, [rain, night])
            print(f"    {base.__name__:14s} + {rain.__name__:12s} → {svc.quote(q):>5}원")
