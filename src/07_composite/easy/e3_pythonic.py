"""07 컴포지트 — 파이썬다운 변형: 순회는 walk() 한 번만 쓰고, 연산은 그 위에서 한다.

상황: 구매팀이 "경운기 10대에 볼트가 몇 개 필요한가"(소요량 전개)를 물었다.
연산마다 세 클래스를 여는 대신, 트리를 (항목, 누적 수량)의 평평한 흐름으로 바꾸는
walk()를 두고, 원가·소요량은 그 흐름 위의 짧은 함수로 쓴다.
"""
from __future__ import annotations

from collections import Counter
from typing import Iterator


class BomItem:
    """[Component] 연산을 둘로 줄였다: 자기 몫(own_cost)과 순회(walk)."""

    def __init__(self, name: str, own_cost: int) -> None:
        """own_cost: 단품은 단가, 조립품은 공임."""
        self.name, self.own_cost = name, own_cost

    def walk(self, qty: int = 1) -> Iterator[tuple[BomItem, int]]:
        """(항목, 누적 수량)을 하나씩 내놓는다. 단품은 자기 하나뿐."""
        yield self, qty


class Part(BomItem):
    """[Leaf] 단품. walk()는 물려받은 그대로 쓴다."""


class Assembly(BomItem):
    """[Composite] 조립품."""

    def __init__(self, name: str, labor: int) -> None:
        """공임과 (항목, 수량) 목록."""
        super().__init__(name, labor)
        self.children: list[tuple[BomItem, int]] = []

    def add(self, item: BomItem, qty: int = 1) -> Assembly:
        """자식 추가."""
        self.children.append((item, qty))
        return self

    def walk(self, qty: int = 1) -> Iterator[tuple[BomItem, int]]:
        """자기 자신을 내놓고, 자식의 walk()가 내는 값을 그대로 흘려보낸다. 재귀는 여기 한 곳뿐."""
        yield self, qty
        for child, n in self.children:
            yield from child.walk(qty * n)


def total_cost(item: BomItem) -> int:
    """원가 = Σ(자기 몫 × 누적 수량). 재귀가 한 줄도 없다."""
    return sum(i.own_cost * q for i, q in item.walk())


def explode(item: BomItem, units: int) -> Counter[str]:
    """소요량 전개: 완제품 units개에 필요한 단품별 총수량.

    isinstance(i, Part)는 타입마다 다른 계산을 하는 분기가 아니라 '단품만 골라라'는 필터다.
    """
    need: Counter[str] = Counter()
    for i, q in item.walk(units):
        if isinstance(i, Part):
            need[i.name] += q
    return need


if __name__ == "__main__":
    bolt = Part("M8 볼트", 120)
    engine = Assembly("엔진", 40_000).add(Part("피스톤", 15_300), 2).add(bolt, 16)
    tiller = Assembly("경운기", 60_000).add(engine).add(Assembly("프레임", 25_000).add(bolt, 24))
    print(f"[1] 경운기 원가: {total_cost(tiller):,}원")
    print(f"[2] 경운기 10대 소요량: {explode(tiller, 10).most_common()}")   # 볼트는 (16 + 24) × 10
