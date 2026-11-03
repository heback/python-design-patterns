"""10 전략 — 패턴 코드: 요금 규칙을 교체 가능한 정책 객체로 뺀다.

상황: 민재는 delivery_fee()의 줄들을 둘로 나눴다. 지역마다·주마다 바뀌는 요금표는
정책(전략)으로 빼고, 어느 요금표든 같은 구독 무료·가게 할인은 서비스에 남긴다.
"어느 지역에 어느 정책"이라는 선택은 서비스 바깥의 설정과 build_policy()로 옮긴다.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass(frozen=True)
class FeeInput:
    """정책이 알아야 하는 사실만 담은 좁은 입력. Order를 통째로 넘기지 않는다."""
    distance_km: float
    hour: int
    is_raining: bool

def is_night(hour: int) -> bool:
    """밤 할증 판정(22시~6시). 복사되던 기준을 한 곳에 모았다."""
    return hour >= 22 or hour < 6

class FeePolicy(ABC):
    """[Strategy] 요금 계산 규칙의 공통 인터페이스. 서비스는 이 타입만 안다."""
    name: str            # 구체 전략마다 이름을 붙여 로그에 남긴다
    @abstractmethod
    def calculate(self, q: FeeInput) -> int:
        """할증까지 넣은 요금(원). 구독·가게 할인은 서비스 몫이다."""

    def describe(self) -> str:
        """로그에 남길 정책 이름."""
        return self.name

class DistancePolicy(FeePolicy):
    """[Concrete Strategy] 서울: 3,000원 + km당 500원. 할증도 이 클래스 안에 있다."""
    name = "distance"
    def calculate(self, q: FeeInput) -> int:
        """거리 요금 + 비 1,000원 + 밤 1,500원."""
        return (3000 + int(q.distance_km * 500)
                + (1000 if q.is_raining else 0) + (1500 if is_night(q.hour) else 0))

class TieredPolicy(FeePolicy):
    """[Concrete Strategy] 부산: 구간제(2km 2,500 / 5km 4,000 / 그 너머 6,000)."""
    name = "tiered"
    def calculate(self, q: FeeInput) -> int:
        """구간 요금 + 비 500원 + 밤 1,500원. 밤 판정은 서울과 같은 is_night()다."""
        fee = 2500 if q.distance_km <= 2 else 4000 if q.distance_km <= 5 else 6000
        return fee + (500 if q.is_raining else 0) + (1500 if is_night(q.hour) else 0)

@dataclass
class FlatPolicy(FeePolicy):
    """[Concrete Strategy] 제주 정액 이벤트. 인터페이스가 좁아 할증을 억지로 0으로 둘 필요가 없다."""
    fee: int            # 1,900원이 2,500원이 되면 이 숫자만 바뀐다
    name = "flat"
    def calculate(self, q: FeeInput) -> int:
        """입력과 무관하게 정액."""
        return self.fee

@dataclass
class Order:
    """주문. delivery_fee()가 사라졌다. 요금 규칙은 주문이 바뀔 이유가 아니다."""
    is_subscriber: bool
    promo_discount: int
    distance_km: float
    hour: int = 12
    is_raining: bool = False

    def fee_input(self) -> FeeInput:
        """정책이 필요한 사실만 뽑는다. 주문과 정책이 닿는 곳은 여기 하나다."""
        return FeeInput(self.distance_km, self.hour, self.is_raining)

@dataclass
class DeliveryFeeService:
    """[Context] 정책을 상속하지 않고 '갖는다'. 그래서 실행 중에 바꿔 끼울 수 있다."""
    policy: FeePolicy    # 어떤 정책인지 묻지 않고 받는다

    def quote(self, order: Order) -> int:
        """공통 규칙만 직접 처리한다. 정책 종류를 묻는 if가 하나도 없다."""
        if order.is_subscriber:
            return 0
        return max(0, self.policy.calculate(order.fee_input()) - order.promo_discount)

def build_policy(spec: dict) -> FeePolicy:
    """[선택 로직] 설정 한 줄을 정책으로. 선택은 서비스 바깥, 여기 한 곳에만 있다."""
    kinds = {"distance": DistancePolicy, "tiered": TieredPolicy, "flat": FlatPolicy}
    # 새 정책은 클래스 하나 + 위 dict 한 줄이면 된다. 서비스는 고치지 않는다(OCP).
    return kinds[spec["type"]](**{k: v for k, v in spec.items() if k != "type"})

if __name__ == "__main__":
    # 운영팀이 고치는 설정. 코드가 아니라 데이터라 제주 이벤트에 재배포가 필요 없다.
    config = {"seoul": {"type": "distance"}, "busan": {"type": "tiered"},
              "jeju": {"type": "flat", "fee": 1900}}
    services = {r: DeliveryFeeService(build_policy(s)) for r, s in config.items()}
    print("[1] 정책만 따로 시험 — Order 없이 FeeInput 한 줄이면 된다")
    for p in (DistancePolicy(), TieredPolicy(), FlatPolicy(1900)):   # 비 오는 밤 11시, 3.2km
        print(f"    {p.describe():8s} {p.calculate(FeeInput(3.2, 23, True))}원")
    print("[2] 새벽 5시 1km — 이제 두 지역 모두 밤 할증이 붙는다")
    for r in ("seoul", "busan"):
        print(f"    {r}: {services[r].quote(Order(False, 0, 1.0, hour=5))}원")
    print("[3] 실행 중 정책 교체 — 서울을 구간제로 바꿔 본다")
    services["seoul"].policy = build_policy({"type": "tiered"})
    print(f"    seoul: {services['seoul'].quote(Order(False, 0, 3.2))}원")
