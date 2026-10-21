"""연습문제 3 해설: 정렬 기준 2가지뿐인 리포트에는 sorted(key=...)로 충분하다.

상황: 가맹점 월간 리포트를 '매출순'과 '가게명순' 두 가지로 정렬해 보여 준다.
SortStrategy 추상 클래스와 구체 클래스 두 개를 만들 것인가? sorted()의 key 인자가
이미 '교체 가능한 비교 알고리즘을 주입받는 자리' — 즉 표준 라이브러리에 내장된
전략 패턴이다. 우리가 할 일은 key 함수 두 개에 이름을 붙이는 것뿐이다.
"""
from __future__ import annotations

from operator import attrgetter
from typing import NamedTuple


class StoreSales(NamedTuple):
    """리포트 한 줄. NamedTuple이라 attrgetter로 필드를 바로 key로 쓸 수 있다."""

    name: str
    revenue: int


# 정렬 기준 = key 함수 + 방향. 이름 → (key, reverse) 매핑이 전부다.
# 클래스 계층을 만들었다면 이 3줄이 추상 클래스 1개 + 구체 클래스 2개 + 선택 로직이 된다.
SORT_OPTIONS = {
    "revenue": (attrgetter("revenue"), True),   # 매출 높은 순
    "name": (attrgetter("name"), False),        # 가나다순
}


def report(rows: list[StoreSales], sort_by: str) -> list[str]:
    """리포트 문자열 목록. sort_by는 화면의 드롭다운 값이 그대로 들어온다."""
    key, reverse = SORT_OPTIONS[sort_by]
    return [f"{r.name:6s} {r.revenue:>9,}원" for r in sorted(rows, key=key, reverse=reverse)]


if __name__ == "__main__":
    rows = [StoreSales("마라탕집", 8_200_000), StoreSales("국밥집", 12_500_000),
            StoreSales("분식집", 15_100_000)]
    for opt in SORT_OPTIONS:
        print(f"[{opt} 순]")
        for line in report(rows, opt):
            print("   ", line)
