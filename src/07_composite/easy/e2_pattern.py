"""07 컴포지트 — 패턴 코드: BomItem 하나로 단품과 조립품을 똑같이 다룬다.

상황: 소연은 깊이 가정을 버린다. Part(단품)와 Assembly(조립품)가 공통 타입 BomItem을
갖고, 조립품의 연산은 "내 몫 + 자식들에게 같은 질문을 던진 결과의 합"으로 정의한다.
그러면 BOM이 몇 단계든 재귀가 알아서 내려간다.
"""
from __future__ import annotations

from abc import ABC, abstractmethod


class BomItem(ABC):
    """[Component] 부품표의 한 항목. 클라이언트는 이 타입만 안다.

    add()를 여기 두지 않았다(안전성 설계). 단품에 add()가 있으면 '부를 수는 있지만
    의미가 없는' 메서드가 생긴다. 트리를 조립하는 코드만 Assembly를 알면 된다.
    """

    def __init__(self, name: str) -> None:
        """모든 항목은 이름이 있다."""
        self.name = name

    @abstractmethod
    def cost(self) -> int:
        """이 항목 1개의 총원가(원)."""

    @abstractmethod
    def weight_g(self) -> int:
        """이 항목 1개의 총중량(g)."""


class Part(BomItem):
    """[Leaf] 단품. 재귀가 멈추는 바닥이라 자기 값만 돌려준다."""

    def __init__(self, name: str, unit_cost: int, weight_g: int) -> None:
        """구매 단가와 중량."""
        super().__init__(name)
        self._unit_cost, self._weight_g = unit_cost, weight_g

    def cost(self) -> int:
        """단품 원가는 단가 그 자체."""
        return self._unit_cost

    def weight_g(self) -> int:
        """단품 중량."""
        return self._weight_g


class Assembly(BomItem):
    """[Composite] 조립품. 자식이 단품인지 조립품인지 묻지 않는다."""

    def __init__(self, name: str, labor: int) -> None:
        """조립 공임과 자식 목록. 수량은 자식 객체가 아니라 (항목, 수량) 쌍에 둔다.

        그래야 같은 볼트 객체 하나를 엔진(16개)과 프레임(24개)이 함께 쓸 수 있다.
        """
        super().__init__(name)
        self._labor = labor
        self._children: list[tuple[BomItem, int]] = []

    def add(self, item: BomItem, qty: int = 1) -> Assembly:
        """자식 추가. 자기 자신을 돌려줘 이어서 쓸 수 있게 한다."""
        self._children.append((item, qty))
        return self

    def cost(self) -> int:
        """공임 + Σ(자식 원가 × 수량). 자식에게 '같은 질문'을 던진다."""
        return self._labor + sum(item.cost() * qty for item, qty in self._children)

    def weight_g(self) -> int:
        """같은 모양. 합치는 값만 다르다."""
        return sum(item.weight_g() * qty for item, qty in self._children)


def report(item: BomItem) -> str:
    """[Client] 단품이든 엔진이든 경운기 전체든 같은 코드. isinstance가 없다."""
    return f"{item.name}: 원가 {item.cost():,}원, 중량 {item.weight_g():,}g"


if __name__ == "__main__":
    ring, pin = Part("피스톤 링", 1_200, 15), Part("피스톤 핀", 2_100, 40)
    bolt = Part("M8 볼트", 120, 20)   # 엔진과 프레임이 함께 쓰는 공유 부품
    ring_set = Assembly("링 세트", 500).add(ring, 3)              # 순진한 코드를 무너뜨린 변경
    piston = Assembly("피스톤 조립품", 9_600).add(ring_set).add(pin)
    engine = Assembly("엔진", 40_000).add(piston, 2).add(bolt, 16)
    frame = Assembly("프레임", 25_000).add(Part("강관", 18_000, 9_000), 4).add(bolt, 24)
    tiller = Assembly("경운기", 60_000).add(engine).add(frame)

    print("[1] 깊이가 다른 세 항목을 같은 report()로")
    for item in (bolt, engine, tiller):
        print("   ", report(item))
