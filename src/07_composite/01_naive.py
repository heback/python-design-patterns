"""07 컴포지트 — 순진한 설계: isinstance 분기와 깊이만큼 늘어나는 중첩 루프.

상황: 소형 농기계 제조사 '다온기계' 생산관리팀의 소연은 경운기 한 대의 원가를 내는
스크립트를 쓴다. 처음엔 볼트·베어링 같은 단품(Part)의 평평한 목록이었지만, 곧
"엔진 조립품은 피스톤 조립품을 포함하고, 피스톤 조립품은 다시 단품을 포함한다"는
계층 구조가 들어왔다. 조립품(Assembly)에는 조립 공임도 붙는다. 여기에 총중량 계산 요구가 더해졌다.
이 파일은 소연이 두 클래스를 따로 만들고, 계산 함수마다 isinstance로 분기하며
깊이만큼 루프를 중첩한 버전이다. 데모 [3]에서 4단계 깊이의 BOM이 들어오자 무너진다.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Part:
    """단품. 원가와 중량을 가진다."""

    name: str
    unit_cost: int      # 원
    weight_g: int


@dataclass
class Assembly:
    """조립품. 자식은 (부품 또는 조립품, 수량) 쌍이다.

    ⚠ 문제: Part와 Assembly에 공통 타입이 없다. 그래서 '자식'을 다루는 모든 코드가
    "이게 단품인가 조립품인가"를 먼저 물어야 한다.
    """

    name: str
    labor_cost: int
    children: list[tuple[Part | Assembly, int]] = field(default_factory=list)


def total_cost(item: Part | Assembly) -> int:
    """원가 합계. 깊이 3단계까지만 처리한다."""
    if isinstance(item, Part):
        return item.unit_cost
    total = item.labor_cost
    for child, qty in item.children:
        # ⚠ 문제: 계산 함수마다 같은 isinstance 분기가 반복된다.
        if isinstance(child, Part):
            total += child.unit_cost * qty
        else:
            total += child.labor_cost * qty
            # ⚠ 문제: 한 단계 깊어질 때마다 루프가 한 겹 늘어난다. 3단계에서 멈췄다.
            for grandchild, gqty in child.children:
                # ⚠ 문제: "3단계는 항상 단품"이라는 가정. 4단계 BOM이 오면 AttributeError.
                total += grandchild.unit_cost * gqty * qty  # type: ignore[union-attr]
    return total


def total_weight(item: Part | Assembly) -> int:
    """총중량. total_cost와 '같은 골격'을 복제했다."""
    if isinstance(item, Part):
        return item.weight_g
    total = 0
    for child, qty in item.children:
        # ⚠ 문제: 새 계산(리드타임, 단종 부품 찾기...)마다 이 골격을 또 복사해야 한다.
        if isinstance(child, Part):
            total += child.weight_g * qty
        else:
            for grandchild, gqty in child.children:
                total += grandchild.weight_g * gqty * qty  # type: ignore[union-attr]
    return total


if __name__ == "__main__":
    bolt = Part("M8 볼트", 120, 18)
    ring = Part("피스톤 링", 2_400, 30)
    pin = Part("피스톤 핀", 3_100, 85)

    print("[1] 평평한 목록 시절: 단품 하나는 잘 된다")
    print(f"    {bolt.name}: {total_cost(bolt):,}원")

    print("[2] 3단계 BOM(엔진 → 피스톤 조립품 → 단품)")
    piston = Assembly("피스톤 조립품", 5_000, [(ring, 3), (pin, 1)])
    engine = Assembly("엔진", 40_000, [(piston, 2), (bolt, 16)])
    print(f"    엔진 원가 {total_cost(engine):,}원, 중량 {total_weight(engine):,}g")

    print("[3] 설계 변경: 피스톤 링이 '링 세트 조립품'이 되어 4단계가 됐다")
    ring_set = Assembly("링 세트", 800, [(ring, 3)])
    piston_v2 = Assembly("피스톤 조립품 v2", 5_000, [(ring_set, 1), (pin, 1)])
    # 엔진 v2 → 피스톤 조립품 v2 → 링 세트 → 피스톤 링: 4단계. 3단계 위치(손주)에 조립품(링 세트)이 왔다.
    engine_v2 = Assembly("엔진 v2", 40_000, [(piston_v2, 2), (bolt, 16)])
    try:
        total_cost(engine_v2)
    except AttributeError as e:
        print(f"    AttributeError: {e}")
        print("    → 깊이 가정이 깨졌다. 루프를 한 겹 더 중첩해야 할까? 다음 설계 변경 때는?")
