"""03 빌더 — GoF 빌더 코드: 같은 조립 절차로 SQL과 요약을 만든다.

상황: 순진한 코드는 to_sql()과 to_summary()가 조립 절차를 각자 들고 있다가
요약에서 조건 하나를 빠뜨렸다. 여기서는 절차를 QueryDirector 한 곳에 두고,
각 단계를 '어떻게 표현할지'만 렌더러(구체 빌더)가 정한다.
[Director] QueryDirector / [Builder] QueryRenderer / [Concrete Builder] SqlRenderer, SummaryRenderer
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class Query:
    """쿼리의 정의(패턴 코드의 완성품을 간추렸다)."""

    where: tuple[str, ...] = ()
    group_by: tuple[str, ...] = ()


class QueryRenderer(ABC):
    """[Builder] 단계별 조립 인터페이스. 순서는 모른다.

    result()를 여기 두지 않는 이유: SQL 문장과 요약 문자열은 공통 부모 타입이 없다.
    클라이언트는 자기가 만든 구체 렌더러에서 결과를 직접 꺼낸다.
    """

    @abstractmethod
    def add_filters(self, conds: tuple[str, ...]) -> None:
        """조건 묶음을 표현한다."""

    @abstractmethod
    def add_grouping(self, cols: tuple[str, ...]) -> None:
        """묶는 기준을 표현한다."""


class SqlRenderer(QueryRenderer):
    """[Concrete Builder] SQL 조각을 쌓는다."""

    def __init__(self) -> None:
        """시작 조각."""
        self.parts = ["SELECT SUM(amount) FROM orders"]

    def add_filters(self, conds: tuple[str, ...]) -> None:
        """WHERE 절."""
        self.parts.append("WHERE " + " AND ".join(conds))

    def add_grouping(self, cols: tuple[str, ...]) -> None:
        """GROUP BY 절."""
        self.parts.append("GROUP BY " + ", ".join(cols))

    def result(self) -> str:
        """완성된 SQL."""
        return " ".join(self.parts)


class SummaryRenderer(QueryRenderer):
    """[Concrete Builder] 한국어 요약 조각을 쌓는다."""

    def __init__(self) -> None:
        """시작 조각."""
        self.parts = ["매출 합계"]

    def add_filters(self, conds: tuple[str, ...]) -> None:
        """조건을 종류 구분 없이 모두 적는다 — 하나만 빠뜨릴 분기가 없다."""
        self.parts.append("조건: " + ", ".join(conds))

    def add_grouping(self, cols: tuple[str, ...]) -> None:
        """묶는 기준."""
        self.parts.append(f"{', '.join(cols)}별")

    def result(self) -> str:
        """완성된 요약."""
        return " / ".join(self.parts)


class QueryDirector:
    """[Director] 조립 절차의 유일한 주인: 어떤 단계를, 어떤 순서로, 언제 건너뛸지."""

    def construct(self, query: Query, renderer: QueryRenderer) -> None:
        """조건이 없으면 필터 단계를 건너뛴다. 이 규칙은 모든 표현에 똑같이 적용된다."""
        if query.where:
            renderer.add_filters(query.where)
        if query.group_by:
            renderer.add_grouping(query.group_by)


if __name__ == "__main__":
    q = Query(where=("order_date >= '2026-01-01'", "tier = 'VIP'"), group_by=("month",))
    director = QueryDirector()
    print("[1] SQL 렌더러를 건네면 SQL이 나온다")
    sql = SqlRenderer()
    director.construct(q, sql)
    print("  ", sql.result())

    print("[2] 같은 Query, 같은 절차에 요약 렌더러를 건네면 요약이 나온다 (VIP 조건 포함)")
    summary = SummaryRenderer()
    director.construct(q, summary)
    print("  ", summary.result())
