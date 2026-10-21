"""순진한 설계: 배달비 계산이 Order 안의 거대한 if 문으로 자란 상태.

상황: 음식 배달 플랫폼 '한끼배달'의 백엔드 개발자 민재는 처음에 거리 기반 배달비
(기본 3,000원 + km당 500원)를 Order.delivery_fee()에 넣었다. 이후 우천·심야 할증,
구독 회원 무료 배달, 가게 부담 프로모션이 붙었고, 운영팀이 지역별 A/B 테스트를
요구하자 '실험군 B용 요금표'가 같은 메서드 안에 복제되었다.

이 파일은 그 결과물이다. 읽으면서 다음 세 가지 고통에 주목하라.
  1) 새 정책 하나가 이 메서드를 '수정'하게 만든다(OCP 위반).
  2) A/B 실험군마다 할증 로직이 복제되어, 한쪽만 고치는 버그가 생긴다.
  3) 정책 하나를 테스트하려면 메뉴·가게·고객까지 갖춘 Order 전체가 필요하다.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Customer:
    """주문 고객. 배달비에는 구독 여부만 쓰이지만 Order가 통째로 들고 있다."""

    name: str
    is_subscriber: bool = False


@dataclass
class Store:
    """가게. 배달비와 관련된 것은 '가게 부담 할인액' 하나뿐이다."""

    name: str
    promo_discount: int = 0  # 가게가 대신 내주는 배달비(원)


@dataclass
class Order:
    """주문 엔티티. 원래 책임은 '무엇을 누구에게 보내는가'인데 요금 정책까지 떠안았다."""

    customer: Customer
    store: Store
    items: list[tuple[str, int]] = field(default_factory=list)
    distance_km: float = 0.0
    region: str = "seoul-gangnam"
    hour: int = 12               # 주문 시각(0~23)
    is_raining: bool = False

    def delivery_fee(self) -> int:
        """배달비를 계산한다. 이 메서드가 '변하는 것' 전부를 한곳에 쌓고 있다."""
        # ⚠ 문제: 구독 무료 규칙이 맨 앞에 있어서, 실험군 B에서 '구독자도 1,000원'을
        #   시험하고 싶어지면 이 줄 자체를 지역별 if로 다시 쪼개야 한다.
        if self.customer.is_subscriber:
            return 0

        # ⚠ 문제: '어떤 요금표를 쓸지'(선택)와 '요금표가 어떻게 계산하는지'(알고리즘)가
        #   한 메서드에 섞여 있다. 지역이 늘 때마다 이 분기가 자란다.
        if self.region in ("seoul-gangnam", "seoul-mapo"):
            # A안: 거리 비례
            fee = 3000 + int(self.distance_km * 500)
            if self.is_raining:
                fee += 1000
            if self.hour >= 22 or self.hour < 6:
                fee += 1500
        elif self.region in ("busan-haeundae",):
            # B안(실험군): 거리 구간제 — A안의 할증 코드를 복사해 왔다.
            if self.distance_km <= 2:
                fee = 2500
            elif self.distance_km <= 5:
                fee = 4000
            else:
                fee = 6000
            if self.is_raining:
                fee += 500  # 금액 차이(500 vs 1000)는 의도된 정책이다. ⚠ 문제: 그러나 할증 '구조'가 복제되어 A안 규칙 변경이 여기엔 반영되지 않는다.
            if self.hour >= 22 or self.hour < 5:  # ⚠ 문제: 심야 기준이 A안(6시)과 미묘하게 다르다 — 의도인가, 복사 실수인가?
                fee += 1500
        else:
            # ⚠ 문제: 새 지역의 '이벤트 정액제'를 넣으려면 또 elif를 추가하고 재배포해야 한다.
            fee = 3000

        # 가게 부담 할인은 어떤 요금표든 공통이다. 하지만 위 분기와 같은 메서드에 있어서
        # '공통 규칙'인지 '정책의 일부'인지 코드만 봐서는 구분되지 않는다.
        return max(0, fee - self.store.promo_discount)


if __name__ == "__main__":
    # 정책 하나(B안의 우천 할증)를 확인하려는 것뿐인데, Customer·Store·메뉴까지 만들어야 한다.
    print("[1] 강남(A안) 3.2km, 맑음, 낮")
    o1 = Order(Customer("지우"), Store("마라탕집"), [("마라탕", 12000)], distance_km=3.2)
    print("    배달비:", o1.delivery_fee())

    print("[2] 해운대(B안) 3.2km, 비, 밤 11시")
    o2 = Order(Customer("도윤"), Store("국밥집", promo_discount=1000), [("국밥", 9000)],
               distance_km=3.2, region="busan-haeundae", hour=23, is_raining=True)
    print("    배달비:", o2.delivery_fee())

    print("[3] 새벽 5시대 주문 — 두 지역의 심야 기준이 다르다")
    for region in ("seoul-gangnam", "busan-haeundae"):
        o = Order(Customer("서아"), Store("분식집"), distance_km=1.0, region=region, hour=5)
        print(f"    {region:15s} 배달비: {o.delivery_fee()}")
    print("    → 같은 '심야 할증'인데 한쪽만 붙는다. 복제된 분기가 어긋난 흔적이다.")

    print("[4] 운영팀: '제주 지역은 이번 주만 정액 1,900원' → 코드 수정 + 재배포가 필요")
    o4 = Order(Customer("하준"), Store("흑돼지집"), distance_km=4.0, region="jeju")
    print("    지금 제주 배달비:", o4.delivery_fee(), "(else 분기의 임시값)")
