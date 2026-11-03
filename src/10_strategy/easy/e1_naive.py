"""10 전략 — 순진한 코드: 배달비 규칙이 Order.delivery_fee() 안의 if로 자랐다.

상황: 배달 앱 '한끼배달'의 민재는 배달비를 "3,000원 + km당 500원"으로 시작했다.
비 오는 날 할증, 밤 할증, 구독 회원 무료, 가게 할인이 붙을 때마다 if를 더했고,
부산에서 구간제 요금을 시험하려고 서울 코드를 복사했다. 그 결과가 이 코드다.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Customer:
    """주문 고객. 배달비에는 구독 여부만 쓰인다."""
    name: str
    is_subscriber: bool = False


@dataclass
class Store:
    """가게. 배달비에 쓰이는 것은 가게가 대신 내 주는 할인액뿐이다."""
    name: str
    promo_discount: int = 0


@dataclass
class Order:
    """주문. 원래 일은 '무엇을 누구에게'인데 요금 규칙까지 떠안았다."""
    customer: Customer
    store: Store
    distance_km: float
    region: str = "seoul"
    hour: int = 12              # 주문 시각(0~23)
    is_raining: bool = False

    def delivery_fee(self) -> int:
        """배달비. 바뀌는 규칙이 전부 이 메서드 하나에 쌓여 있다."""
        # 구독 무료는 어느 지역이든 같은 규칙인데, 바뀌는 규칙들과 한 메서드에 섞여 있다.
        if self.customer.is_subscriber:
            return 0
        # ⚠ 문제: '어느 요금표를 쓸지'(선택)와 '요금표 계산'이 한 덩어리다.
        if self.region == "seoul":
            # 서울: 거리 비례 요금 + 비·밤 할증
            fee = 3000 + int(self.distance_km * 500)
            if self.is_raining:
                fee += 1000
            if self.hour >= 22 or self.hour < 6:
                fee += 1500
        elif self.region == "busan":
            # 구간제: 2km까지 2,500원, 5km까지 4,000원, 그 너머 6,000원. 할증은 서울 것을 복사했다.
            fee = 2500 if self.distance_km <= 2 else 4000 if self.distance_km <= 5 else 6000
            if self.is_raining:
                fee += 500
            # ⚠ 문제: 복사하다 심야 기준이 5시로 바뀌었다. 의도인지 실수인지 알 수 없다.
            if self.hour >= 22 or self.hour < 5:
                fee += 1500
        else:
            # ⚠ 문제: 제주 정액 1,900원 이벤트를 하려면 elif를 더하고 다시 배포해야 한다.
            fee = 3000
        # 가게 할인도 공통 규칙이지만, 위 분기와 붙어 있어 정책의 일부처럼 보인다.
        return max(0, fee - self.store.promo_discount)


if __name__ == "__main__":
    # 요금 규칙 하나를 보려는 것뿐인데 고객·가게까지 갖춘 Order를 만들어야 한다.
    print("[1] 서울 3.2km, 맑은 낮")
    print("    ", Order(Customer("지우"), Store("분식집"), 3.2).delivery_fee(), "원")
    print("[2] 새벽 5시 1km 주문 — 같은 '밤 할증'인데 한쪽만 붙는다")
    # 시각·거리는 같고 지역만 다르다. 이 차이가 의도인지 실수인지 코드로는 모른다.
    for region in ("seoul", "busan"):
        fee = Order(Customer("서아"), Store("국밥집"), 1.0, region, hour=5).delivery_fee()
        print(f"     {region}: {fee}원")
    print("[3] 제주는 아직 else의 임시값 — 정액 이벤트는 코드 수정이 필요하다")
    print("    ", Order(Customer("하준"), Store("흑돼지집"), 4.0, "jeju").delivery_fee(), "원")
