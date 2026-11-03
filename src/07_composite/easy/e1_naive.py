"""07 컴포지트 — 순진한 코드: 단품과 조립품을 isinstance로 구별하며 루프를 중첩한다.

상황: 다온기계 생산관리팀 소연은 BOM으로 엔진 원가를 뽑는다. Part(단품)와
Assembly(조립품)는 공통 타입이 없는 별개의 클래스이고, 계산 함수가 둘을 구별한다.
루프 중첩이 두 겹이라 BOM이 한 단계 깊어지는 순간 계산이 무너진다.
"""
from __future__ import annotations


class Part:
    """단품. 단가와 중량을 가진다."""

    def __init__(self, name: str, unit_cost: int, weight_g: int) -> None:
        """구매 단가(원)와 중량(g)."""
        self.name, self.unit_cost, self.weight_g = name, unit_cost, weight_g


class Assembly:
    """조립품. 조립 공임과 (항목, 수량) 목록을 가진다. Part와 공통 타입이 없다."""

    def __init__(self, name: str, labor: int, children: list[tuple[object, int]]) -> None:
        """자식은 Part일 수도, Assembly일 수도 있다."""
        self.name, self.labor, self.children = name, labor, children


def total_cost(asm: Assembly) -> int:
    """조립품 원가 = 공임 + 자식 원가 × 수량."""
    total = asm.labor
    for child, qty in asm.children:
        # ⚠ 문제: 자식을 만질 때마다 "단품이냐 조립품이냐"를 물어야 한다.
        if isinstance(child, Part):
            total += child.unit_cost * qty
        else:
            # ⚠ 문제: 두 겹 루프 = "BOM은 최대 2단계"라는 가정. 손자가 조립품이면 깨진다.
            sub = child.labor + sum(g.unit_cost * q for g, q in child.children)
            total += sub * qty
    return total


def total_weight(asm: Assembly) -> int:
    """총중량. ⚠ 문제: total_cost의 골격을 그대로 복사했다. 고칠 곳이 두 배다."""
    total = 0   # 조립품은 공임만 있고 자기 무게는 없다고 가정한다
    for child, qty in asm.children:
        if isinstance(child, Part):
            total += child.weight_g * qty
        else:
            total += sum(g.weight_g * q for g, q in child.children) * qty
    return total


if __name__ == "__main__":
    ring, pin = Part("피스톤 링", 1_200, 15), Part("피스톤 핀", 2_100, 40)
    piston = Assembly("피스톤 조립품", 9_600, [(ring, 3), (pin, 1)])
    engine = Assembly("엔진", 40_000, [(piston, 2), (Part("M8 볼트", 120, 20), 16)])
    print(f"[1] 엔진 원가 {total_cost(engine):,}원, 중량 {total_weight(engine):,}g")

    print("[2] 설계 변경: 링 3개를 '링 세트' 조립품으로 바꾼다 — BOM이 한 단계 깊어진다")
    # 링 세트는 조립품이라 unit_cost가 없다. 두 겹 루프가 손자를 단품으로 착각한다.
    ring_set = Assembly("링 세트", 500, [(ring, 3)])
    piston.children = [(ring_set, 1), (pin, 1)]
    try:
        total_cost(engine)
    except AttributeError as e:
        print(f"    계산 실패: AttributeError: {e}")
