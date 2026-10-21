"""07 컴포지트 — 파이썬다운 변형: 재귀 제너레이터, 컨테이너 프로토콜, singledispatch.

상황: 02_composite.py는 연산 하나마다 Part와 Assembly 양쪽에 메서드를 추가했다.
구매팀이 "경운기 10대 만들려면 볼트가 총 몇 개 필요한가"(소요량 전개, BOM explosion)를,
환경팀이 "탄소 배출량 보고서"를 요구하자 소연은 생각한다. 연산이 늘 때마다 두 클래스를
여는 것이 맞나? 이 파일은 세 가지 파이썬 도구로 답한다.
  (1) walk() + yield from: 트리 순회를 다형적 메서드 '하나'로 두고, 연산은 순회 결과 위에서 sum/Counter로.
  (2) __iter__ / __len__ / __contains__: 조립품을 파이썬 컨테이너처럼 쓰게 한다.
  (3) functools.singledispatch: 새 연산을 클래스 밖의 함수로 추가한다(방문자 패턴의 파이썬식 대체).
공통 기반 BomItem은 그대로 둔다. 순회와 '자기 몫(own_cost)'까지는 다형성으로 처리하므로,
클라이언트 코드에 단품/조립품 isinstance 분기가 다시 생기지 않는다.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from collections import Counter
from dataclasses import dataclass, field
from functools import singledispatch
from typing import Iterator


class BomItem(ABC):
    """[Component] 다형적 연산을 '최소한'으로 줄인 공통 인터페이스.

    02에서는 cost/weight/lead_time… 연산마다 추상 메서드가 있었다. 여기서는 두 가지만 둔다.
      - own_cost: 이 항목 '자체'의 몫(단품은 단가, 조립품은 공임).
      - walk():   자신과 하위 항목을 (항목, 누적 수량)으로 흘려보내는 순회.
    나머지 합산형 연산은 이 둘 위에서 클래스 밖의 함수로 표현된다.
    """

    @property
    @abstractmethod
    def own_cost(self) -> int:
        """이 항목 자체의 비용(하위 항목 제외)."""

    @abstractmethod
    def walk(self, multiplier: int = 1) -> Iterator[tuple[BomItem, int]]:
        """깊이 우선으로 (항목, 완제품 1개당 누적 수량)을 낸다."""


@dataclass(frozen=True, eq=False)
class Part(BomItem):
    """[Leaf] 단품. frozen: 부품 마스터 정보는 BOM 계산 도중 바뀌면 안 된다.

    eq=False인 이유: 이름·단가가 같은 두 부품을 '같은 부품'으로 취급하면 안 된다.
    정체성(is) 기반 해시를 유지해야 Counter의 키로 안전하게 쓸 수 있다.
    """

    name: str
    unit_cost: int
    co2_g: int          # 부품 1개 생산 시 탄소 배출(g)

    @property
    def own_cost(self) -> int:
        """단품의 몫은 단가."""
        return self.unit_cost

    def walk(self, multiplier: int = 1) -> Iterator[tuple[BomItem, int]]:
        """재귀의 바닥: 자기 자신 하나만 낸다."""
        yield self, multiplier


@dataclass(eq=False)
class Assembly(BomItem):
    """[Composite] 조립품. 자식 순회를 파이썬 프로토콜로 노출한다."""

    name: str
    labor_cost: int
    children: list[tuple[BomItem, int]] = field(default_factory=list)

    def add(self, item: BomItem, qty: int = 1) -> Assembly:
        """자식 추가(체이닝). 순환 검사는 02에서 다뤘으므로 생략했다."""
        self.children.append((item, qty))
        return self

    @property
    def own_cost(self) -> int:
        """조립품의 몫은 공임. 하위 비용은 walk()가 따로 흘려보낸다."""
        return self.labor_cost

    def walk(self, multiplier: int = 1) -> Iterator[tuple[BomItem, int]]:
        """자신을 낸 뒤, 자식에게 '같은 질문'을 던진다 — 자식이 단품인지 묻지 않는다.

        yield from은 하위 제너레이터의 값을 그대로 흘려보낸다. 재귀 구조를
        '평평한 스트림'으로 바꾸는 것이 핵심이다. 덕분에 연산마다 재귀를 다시 쓸 필요가 없다.
        """
        yield self, multiplier
        for child, qty in self.children:
            yield from child.walk(multiplier * qty)

    def __iter__(self) -> Iterator[BomItem]:
        """for item in assembly: 하위 모든 항목(자기 자신 제외)을 깊이 우선으로."""
        return (item for item, _ in self.walk() if item is not self)

    def __len__(self) -> int:
        """len(assembly): 직접 자식 '종류' 수. 전체 개수와 혼동하지 않도록 정의를 docstring에 못박는다."""
        return len(self.children)

    def __contains__(self, item: object) -> bool:
        """'볼트' in 엔진: 하위 어디든 있으면 참. 정체성 비교로 공유 부품을 정확히 찾는다."""
        return any(x is item for x in self)


def total_cost(root: BomItem) -> int:
    """[Client] 원가 = Σ(각 항목의 자기 몫 × 누적 수량). 타입 분기도 재귀도 없다."""
    return sum(item.own_cost * qty for item, qty in root.walk())


def explode(root: BomItem, units: int = 1) -> Counter[Part]:
    """소요량 전개: 완제품 units대에 필요한 단품별 총수량.

    여기의 isinstance(item, Part)는 '연산을 타입별로 다르게 처리하는' 분기가 아니라
    "단품만 골라 달라"는 질의(필터)다. 질문 자체가 '단품 목록'이므로 타입이 곧 조건이다.
    2절의 문제였던 분기(같은 계산을 타입마다 다르게 하는 것)와는 성격이 다르다.
    """
    need: Counter[Part] = Counter()
    for item, qty in root.walk(units):
        if isinstance(item, Part):
            need[item] += qty
    return need


@singledispatch
def co2_g(item: object) -> int:
    """[새 연산] 탄소 배출량. 등록되지 않은 타입이 오면 즉시 실패시킨다.

    singledispatch는 '타입별 분기'를 디스패치 표 한 곳으로 모은 것이다. 클라이언트에 isinstance가
    흩어지지 않는다는 점은 다형성과 같지만, 새 항목 타입(예: 외주 가공품)이 생기면 이 등록 함수들을
    모두 찾아 추가해야 한다 — 연산 추가는 쉬워지고 타입 추가는 어려워지는 교환이다.
    """
    raise TypeError(f"co2_g를 모르는 타입: {type(item).__name__}")


@co2_g.register
def _(item: Part) -> int:
    """단품: 생산 배출량."""
    return item.co2_g


@co2_g.register
def _(item: Assembly) -> int:
    """조립품: 자식 합 + 조립 공정 배출(공임 1,000원당 50g으로 가정)."""
    return item.labor_cost // 1000 * 50 + sum(co2_g(c) * q for c, q in item.children)


if __name__ == "__main__":
    # 02와 다른, 더 작은 BOM이다(실린더 블록·링 세트 없음). 금액을 02와 비교하지 말 것.
    bolt = Part("M8 볼트", 120, 40)
    ring = Part("피스톤 링", 2_400, 300)
    pin = Part("피스톤 핀", 3_100, 520)
    pipe = Part("강관 프레임", 45_000, 18_000)
    piston = Assembly("피스톤 조립품", 5_000).add(ring, 3).add(pin)
    engine = Assembly("엔진", 40_000).add(piston, 2).add(bolt, 16)
    frame = Assembly("프레임", 15_000).add(pipe, 2).add(bolt, 24)
    tiller = Assembly("경운기", 120_000).add(engine).add(frame)

    print("[1] 순회 한 번 + 다형적 own_cost로 원가")
    # walk()가 누적 수량을 곱해 주므로 피스톤 조립품의 공임도 ×2로 더해진다.
    # 이 BOM에 02식 재귀 cost()를 적용해도 같은 값이 나온다(02와는 BOM이 달라 금액이 다르다).
    print(f"    경운기 원가 {total_cost(tiller):,}원, 단품 하나도 같은 함수로: {total_cost(bolt):,}원")

    print("[2] 소요량 전개 — 경운기 10대")
    for part, qty in explode(tiller, 10).most_common():
        print(f"    {part.name:<8} {qty:>4}개")

    print("[3] 컨테이너 프로토콜")
    print(f"    len(engine) = {len(engine)}  (직접 자식 종류 수)")
    print(f"    bolt in frame = {bolt in frame}, pin in frame = {pin in frame}")
    print(f"    for 순회: {[x.name for x in piston]}")

    print("[4] singledispatch로 클래스 밖에서 새 연산 추가")
    # Part/Assembly 클래스는 한 줄도 바뀌지 않았다. 등록 안 된 타입은 기본 구현이 막는다.
    print(f"    경운기 탄소 배출 {co2_g(tiller):,}g")
    try:
        co2_g("엔진")
    except TypeError as e:
        print(f"    잘못된 입력 → {e}")
