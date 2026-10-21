"""07 컴포지트 — 패턴 적용: BomItem 하나로 단품과 조립품을 똑같이 다룬다.

상황: 소연은 깊이 가정을 버리기로 한다. 단품(Part)과 조립품(Assembly)이 공통 타입
BomItem을 갖고, 조립품의 연산은 "내 몫 + 자식들에게 같은 질문을 던진 결과"로 정의한다.
그러면 깊이가 몇이든 재귀가 알아서 내려간다. 이 파일은 원가·중량·리드타임(최장 경로)·
단종 부품 탐색 네 가지 연산과, 실제 BOM의 함정인 순환 참조·공유 부품을 다룬다.
"""
from __future__ import annotations

from abc import ABC, abstractmethod


class BomItem(ABC):
    """[Component] 부품표의 한 항목. 클라이언트는 이 타입만 안다.

    자식 관리 메서드(add)를 여기 두지 않은 것이 이 설계의 핵심 선택이다(안전성 우선).
    단품에 add()가 있으면 '호출은 되지만 의미가 없는' 메서드가 생겨 LSP가 흔들린다.
    대가로, 트리를 '조립하는' 코드는 Assembly 타입을 알아야 한다. 트리를 '사용하는'
    코드(원가 계산 등)는 BomItem만 알면 된다 — 대부분의 코드는 후자다.
    """

    def __init__(self, name: str) -> None:
        """모든 항목은 이름을 가진다."""
        self.name = name

    @abstractmethod
    def cost(self) -> int:
        """이 항목 1개를 만드는 데 드는 총원가(원)."""

    @abstractmethod
    def weight_g(self) -> int:
        """이 항목 1개의 총중량(g)."""

    @abstractmethod
    def lead_time_days(self) -> int:
        """이 항목 1개를 확보하는 데 걸리는 최장 일수."""

    @abstractmethod
    def discontinued_paths(self, prefix: str = "") -> list[str]:
        """단종 단품까지 이어지는 경로 목록. 비어 있으면 생산에 문제없다."""

    @abstractmethod
    def contains(self, item: BomItem) -> bool:
        """item이 이 항목 자신이거나 하위 어딘가에 있는가. 순환 검사에 쓴다."""

    @abstractmethod
    def render(self, qty: int = 1, depth: int = 0) -> list[str]:
        """깊이 우선으로 트리를 들여쓰기 문자열 목록으로 만든다."""


class Part(BomItem):
    """[Leaf] 단품. 재귀가 멈추는 곳이다."""

    def __init__(self, name: str, unit_cost: int, weight_g: int,
                 lead_time_days: int, discontinued: bool = False) -> None:
        """구매 단가·중량·조달 기간·단종 여부."""
        super().__init__(name)
        self._unit_cost = unit_cost
        self._weight_g = weight_g
        self._lead = lead_time_days
        self.discontinued = discontinued

    def cost(self) -> int:
        """단품의 원가는 구매 단가 그 자체."""
        return self._unit_cost

    def weight_g(self) -> int:
        """단품 중량."""
        return self._weight_g

    def lead_time_days(self) -> int:
        """구매 조달 기간."""
        return self._lead

    def discontinued_paths(self, prefix: str = "") -> list[str]:
        """단종이면 자기까지의 경로 하나, 아니면 빈 목록."""
        return [f"{prefix}{self.name}"] if self.discontinued else []

    def contains(self, item: BomItem) -> bool:
        """단품은 자식이 없으므로 자기 자신인지만 본다."""
        return item is self

    def render(self, qty: int = 1, depth: int = 0) -> list[str]:
        """한 줄."""
        return [f"{'  ' * depth}- {self.name} ×{qty}  ({self._unit_cost:,}원)"]


class Assembly(BomItem):
    """[Composite] 조립품. 자식은 (BomItem, 수량) — 자식이 단품인지 조립품인지 묻지 않는다.

    공유 부품: 같은 Part 객체가 여러 조립품에 들어가도 된다(트리가 아니라 DAG가 된다).
    수량을 '간선'에 둔 이유가 이것이다. 볼트 객체 하나를 16번 add하지 않고 (볼트, 16)으로 표현하므로
    부품 마스터 정보(단가 변경 등)가 한 객체에만 있다.
    """

    def __init__(self, name: str, labor_cost: int, assembly_days: int) -> None:
        """조립 공임과 조립에 걸리는 일수."""
        super().__init__(name)
        self._labor_cost = labor_cost
        self._assembly_days = assembly_days
        self._children: list[tuple[BomItem, int]] = []

    def add(self, item: BomItem, qty: int = 1) -> Assembly:
        """자식 추가. 순환을 만들면 거부한다. 체이닝을 위해 self를 돌려준다.

        순환 검사가 필요한 이유: A가 B를 포함하고 B가 A를 포함하면 cost()가 무한 재귀에
        빠져 RecursionError로 끝난다. 실제 BOM 데이터는 ERP에서 사람이 입력하므로
        이런 실수는 '반드시' 생긴다. 조회 시점이 아니라 '추가 시점'에 막는 것이 싸다.
        """
        if qty <= 0:
            raise ValueError("수량은 1 이상이어야 한다")
        if item.contains(self):
            raise ValueError(f"순환 참조: {item.name} 안에 이미 {self.name}이(가) 있다")
        self._children.append((item, qty))
        return self

    def cost(self) -> int:
        """내 공임 + Σ(자식 원가 × 수량). 자식이 단품이든 조립품이든 같은 호출이다."""
        return self._labor_cost + sum(child.cost() * qty for child, qty in self._children)

    def weight_g(self) -> int:
        """Σ(자식 중량 × 수량). 조립품 자체의 무게는 없다고 본다."""
        return sum(child.weight_g() * qty for child, qty in self._children)

    def lead_time_days(self) -> int:
        """자식들은 병렬로 조달되므로 '가장 늦은 자식' + 내 조립 일수(최장 경로).

        합(sum)이 아니라 최댓값(max)이라는 점이 원가와 다르다. 같은 재귀 골격에
        '자식 결과를 합치는 방법'만 달라진다 — 이것이 컴포지트 연산의 일반형이다.
        """
        return self._assembly_days + max((c.lead_time_days() for c, _ in self._children), default=0)

    def discontinued_paths(self, prefix: str = "") -> list[str]:
        """자식들의 경로 앞에 내 이름을 붙여 모은다."""
        here = f"{prefix}{self.name} > "
        return [p for child, _ in self._children for p in child.discontinued_paths(here)]

    def contains(self, item: BomItem) -> bool:
        """나 자신이거나, 자식 중 누군가가 포함하면 참."""
        return item is self or any(child.contains(item) for child, _ in self._children)

    def render(self, qty: int = 1, depth: int = 0) -> list[str]:
        """내 줄 다음에 자식들을 한 단계 들여 쓴다."""
        lines = [f"{'  ' * depth}+ {self.name} ×{qty}  (공임 {self._labor_cost:,}원)"]
        for child, child_qty in self._children:
            lines += child.render(child_qty, depth + 1)
        return lines


def report(item: BomItem) -> None:
    """[Client] BomItem만 안다. 단품을 넘기든 경운기 전체를 넘기든 같은 코드다."""
    print(f"    {item.name}: 원가 {item.cost():,}원 / 중량 {item.weight_g():,}g / "
          f"리드타임 {item.lead_time_days()}일")


if __name__ == "__main__":
    # 공유 부품: bolt 객체 하나가 엔진과 프레임 양쪽에 쓰인다.
    bolt = Part("M8 볼트", 120, 18, lead_time_days=3)
    ring = Part("피스톤 링", 2_400, 30, lead_time_days=14)
    pin = Part("피스톤 핀", 3_100, 85, lead_time_days=10, discontinued=True)
    block = Part("실린더 블록", 180_000, 21_000, lead_time_days=30)
    pipe = Part("강관 프레임", 45_000, 9_500, lead_time_days=7)

    ring_set = Assembly("링 세트", 800, assembly_days=1).add(ring, 3)
    piston = Assembly("피스톤 조립품", 5_000, assembly_days=2).add(ring_set).add(pin)
    engine = Assembly("엔진", 40_000, assembly_days=5).add(block).add(piston, 2).add(bolt, 16)
    frame = Assembly("프레임", 15_000, assembly_days=3).add(pipe, 2).add(bolt, 24)
    tiller = Assembly("경운기", 120_000, assembly_days=4).add(engine).add(frame)

    print("[1] 같은 클라이언트 코드로 단품·중간 조립품·완제품 계산 (깊이 5단계)")
    for item in (bolt, piston, tiller):
        report(item)

    print("[2] 깊이 우선 트리 출력")
    print("\n".join("    " + line for line in tiller.render()))

    print("[3] 단종 부품이 포함된 경로")
    for path in tiller.discontinued_paths():
        print(f"    {path}")

    print("[4] 순환 참조 시도: 링 세트에 경운기를 넣는다")
    try:
        ring_set.add(tiller)
    except ValueError as e:
        print(f"    거부됨 — {e}")
