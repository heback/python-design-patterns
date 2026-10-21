"""07 컴포지트 — 연습문제 1 해설: add()를 Component에 두는 '투명성' 설계와 그 대가.

상황: 다온기계의 다른 팀은 BOM 편집 화면을 만든다. 화면 코드는 사용자가 클릭한 항목에
"하위 항목 추가"를 호출하는데, 그 항목이 단품인지 조립품인지 매번 isinstance로 묻기 싫어서
add()를 BomItem(Component)에 올리자고 제안했다. 이 파일은 그 투명성 설계를 구현해,
무엇이 편해지고 어떤 원칙(LSP)이 위협받는지를 실행으로 보인다.
"""
from __future__ import annotations


class LeafHasNoChildrenError(TypeError):
    """단품에 자식을 넣으려 할 때의 도메인 예외.

    NotImplementedError를 쓰지 않는 이유: 파이썬에서 그것은 "하위 클래스가 아직 구현하지 않았다"는
    뜻이다. 단품의 add()는 '아직'이 아니라 '영원히' 불가능하므로 TypeError 계열이 관례에 맞다.
    """


class BomItem:
    """[Component] 투명성 설계: 자식 관리 메서드까지 공통 인터페이스에 둔다.

    GoF 원전은 이 방식을 '투명성(transparency)'이라 부르며 기본안으로 제시한다.
    클라이언트가 단품·조립품을 '완전히' 구분 없이 다룰 수 있기 때문이다.
    """

    def __init__(self, name: str) -> None:
        """이름."""
        self.name = name

    def add(self, item: BomItem, qty: int = 1) -> None:
        """기본 구현은 '지원하지 않음'. 단품이 이것을 물려받는다.

        여기가 LSP 위반 지점이다. BomItem의 계약이 "add()를 부를 수 있다"인데
        Part는 그 계약을 런타임 예외로 깨뜨린다. 오류가 타입 검사 시점이 아니라
        사용자가 버튼을 누른 시점에 드러난다.
        """
        raise LeafHasNoChildrenError(f"{self.name}은(는) 단품이라 하위 항목을 가질 수 없다")

    def cost(self) -> int:
        """원가."""
        raise NotImplementedError


class Part(BomItem):
    """[Leaf] add()를 재정의하지 않으므로 호출하면 예외."""

    def __init__(self, name: str, unit_cost: int) -> None:
        """단가."""
        super().__init__(name)
        self.unit_cost = unit_cost

    def cost(self) -> int:
        """단가."""
        return self.unit_cost


class Assembly(BomItem):
    """[Composite] add()를 실제로 구현한다."""

    def __init__(self, name: str, labor: int) -> None:
        """공임과 자식 목록."""
        super().__init__(name)
        self.labor = labor
        self.children: list[tuple[BomItem, int]] = []

    def add(self, item: BomItem, qty: int = 1) -> None:
        """자식 추가."""
        self.children.append((item, qty))

    def cost(self) -> int:
        """재귀 합."""
        return self.labor + sum(c.cost() * q for c, q in self.children)


def on_add_clicked(selected: BomItem, new_item: BomItem) -> str:
    """[Client] 편집 화면의 '하위 항목 추가' 버튼 처리기.

    투명성 덕분에 isinstance 없이 add()를 부를 수 있다 — 이것이 얻는 것.
    그러나 결국 예외 처리가 필요하다. '분기'가 isinstance에서 try/except로 이름만 바뀐 셈이다.
    """
    try:
        selected.add(new_item)
        return f"{selected.name}에 {new_item.name} 추가됨"
    except LeafHasNoChildrenError as e:
        return f"오류: {e}"


if __name__ == "__main__":
    engine = Assembly("엔진", 40_000)
    bolt = Part("M8 볼트", 120)
    print("[1] 조립품에 추가:", on_add_clicked(engine, bolt))
    print("[2] 단품에 추가:", on_add_clicked(bolt, Part("와셔", 30)))
    print(f"[3] 엔진 원가 {engine.cost():,}원 — 계산 쪽은 두 설계 모두 똑같이 투명하다")
