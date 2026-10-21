"""07 컴포지트 — 연습문제 3 해설: 깊이가 항상 2인 메뉴에 컴포지트가 필요한가.

상황: 다온기계의 부품 온라인몰은 '카테고리 → 상품' 2단계 메뉴만 쓴다. 카테고리 안에
카테고리가 들어갈 계획은 없고, 상품 안에 상품이 들어갈 일도 없다. 신입 개발자가
"트리니까 컴포지트로 가자"고 하자, 소연은 아래의 단순한 구조를 제안했다.
요점: 깊이가 고정되고 두 계층의 '역할이 다르면'(카테고리는 상품을 묶을 뿐, 가격이 없다)
공통 인터페이스로 묶는 것이 오히려 의미를 흐린다.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Product:
    """상품. 가격이 있다."""

    name: str
    price: int


@dataclass
class Category:
    """카테고리. 상품 목록만 가진다 — 타입이 '깊이 2'를 그대로 표현한다.

    컴포지트로 만들면 Category.price()나 Product.children 같은 '억지 메서드'가 필요해진다.
    여기서는 타입 시스템이 "카테고리 안에 카테고리는 없다"는 도메인 규칙을 강제한다.
    """

    name: str
    products: list[Product] = field(default_factory=list)


def render_menu(categories: list[Category]) -> list[str]:
    """[Client] 이중 루프로 충분하다. 깊이가 고정이므로 이 루프는 '가정'이 아니라 '명세'다."""
    lines = []
    for cat in categories:
        lines.append(f"▸ {cat.name} ({len(cat.products)})")
        lines += [f"    {p.name} — {p.price:,}원" for p in cat.products]
    return lines


if __name__ == "__main__":
    menu = [
        Category("엔진 부품", [Product("피스톤 링 세트", 7_900), Product("점화 플러그", 4_500)]),
        Category("소모품", [Product("엔진 오일 1L", 9_800)]),
    ]
    print("\n".join(render_menu(menu)))
