"""GoF 빌더: 같은 조립 절차(Director)로 서로 다른 표현(SQL, 사람이 읽는 요약)을 만든다.

상황: 02_builder.py로 쿼리 정의(Query)는 안전해졌다. 그런데 분석 팀이 "대시보드마다
이 차트가 무엇을 집계하는지 한국어 요약을 같이 보여 달라"고 요청했다. 01_naive.py에서는
to_sql()과 to_summary()가 같은 분기를 복제했고, 결국 회원 등급 필터가 요약에서 빠지는
불일치가 났다. 여기서는 "어떤 순서로 무엇을 조립하는가"를 Director 한 곳에 두고,
"각 조각을 어떻게 표현하는가"만 Concrete Builder마다 다르게 한다.

GoF 의도(intent): "복잡한 객체의 생성 과정과 표현 방법을 분리하여, 동일한 생성 절차에서
서로 다른 표현 결과를 만들 수 있게 한다."

역할 대응:
- [Director]          QueryDirector — 조립 절차(단계 순서와 생략 규칙)를 소유
- [Builder]           QueryRenderer — 단계별 조립 인터페이스
- [Concrete Builder]  PostgresRenderer, SummaryRenderer — 각자의 표현을 쌓는다
- [Product]           SqlStatement, 요약 문자열 — 서로 공통 타입이 없다는 점이 GoF 빌더의 특징

02와의 차이: 02의 '빌더'는 Query라는 단일 제품을 유창하게 조립하는 현대적 의미의 빌더이고,
이 파일의 '빌더'는 GoF 원전의 의미(같은 절차, 다른 표현)다. 둘은 이름만 같고 목적이 다르다.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


# ---------------------------------------------------------------------------
# 입력: 02_builder.py의 Query를 간추린 것. (파일 간 import를 하지 않는 교재 규칙 때문에 다시 정의)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Condition:
    """조건 하나."""

    expr: str
    op: str
    value: object


@dataclass(frozen=True)
class Query:
    """검증이 끝난 쿼리 정의. 실제로는 02의 QueryBuilder.build()가 만든다."""

    table: str
    select: tuple[str, ...]
    where: tuple[Condition, ...] = ()
    group_by: tuple[str, ...] = ()
    having: tuple[Condition, ...] = ()
    limit: int | None = None


# ---------------------------------------------------------------------------
# Builder 계층
# ---------------------------------------------------------------------------

class QueryRenderer(ABC):
    """[Builder] 조립 단계의 인터페이스. 단계 '순서'는 모른다 — 그것은 Director의 지식이다.

    result()를 이 인터페이스에 두지 않은 이유: 제품 타입이 빌더마다 다르다(SQL 객체 vs 문자열).
    GoF도 "제품들은 공통 부모 클래스를 가질 이유가 거의 없다"고 하며, 결과는 클라이언트가
    구체 빌더에서 직접 꺼낸다. 억지로 공통 타입(object)을 두면 타입 정보만 잃는다.
    """

    @abstractmethod
    def add_source(self, table: str, select: tuple[str, ...]) -> None:
        """무엇을 어디서 조회하는가."""

    @abstractmethod
    def add_filters(self, conds: tuple[Condition, ...]) -> None:
        """행 필터."""

    @abstractmethod
    def add_grouping(self, group_by: tuple[str, ...], having: tuple[Condition, ...]) -> None:
        """집계 기준과 집계 후 필터. HAVING은 GROUP BY와 '한 단계'로 묶었다 — 둘은 따로 의미가 없다."""

    @abstractmethod
    def add_limit(self, n: int) -> None:
        """행 수 제한."""


@dataclass(frozen=True)
class SqlStatement:
    """[Product] PostgreSQL용 표현: 텍스트와 바인딩 값."""

    text: str
    params: tuple[object, ...]


class PostgresRenderer(QueryRenderer):
    """[Concrete Builder] 단계마다 SQL 조각과 매개변수를 쌓는다."""

    def __init__(self) -> None:
        """조립 중인 상태. 빌더는 가변이고, 완성품(SqlStatement)은 불변이다."""
        self._clauses: list[str] = []
        self._params: list[object] = []

    def _render(self, conds: tuple[Condition, ...]) -> str:
        """조건을 자리표시자로 바꾸고 값은 params로 보낸다."""
        self._params.extend(c.value for c in conds)
        return " AND ".join(f"{c.expr} {c.op} %s" for c in conds)

    def add_source(self, table: str, select: tuple[str, ...]) -> None:
        """SELECT ... FROM ..."""
        self._clauses.append(f"SELECT {', '.join(select)} FROM {table}")

    def add_filters(self, conds: tuple[Condition, ...]) -> None:
        """WHERE 절."""
        self._clauses.append("WHERE " + self._render(conds))

    def add_grouping(self, group_by: tuple[str, ...], having: tuple[Condition, ...]) -> None:
        """GROUP BY와 (있으면) HAVING."""
        self._clauses.append("GROUP BY " + ", ".join(group_by))
        if having:
            self._clauses.append("HAVING " + self._render(having))

    def add_limit(self, n: int) -> None:
        """LIMIT 절."""
        self._clauses.append(f"LIMIT {n}")

    def result(self) -> SqlStatement:
        """완성품을 꺼낸다. 구체 타입(SqlStatement)을 돌려주므로 호출자가 타입을 잃지 않는다."""
        return SqlStatement(" ".join(self._clauses), tuple(self._params))


class SummaryRenderer(QueryRenderer):
    """[Concrete Builder] 같은 단계에서 분석 팀용 한국어 요약을 쌓는다."""

    _OPS = {"=": "", ">=": " 이상", "<": " 미만", ">": " 초과", "<=": " 이하", "<>": " 제외"}

    def __init__(self) -> None:
        """요약 문장 조각들."""
        self._parts: list[str] = []

    def _describe(self, conds: tuple[Condition, ...]) -> str:
        """조건을 '열 값 이상' 같은 말로 바꾼다."""
        return ", ".join(f"{c.expr} {c.value}{self._OPS.get(c.op, ' ' + c.op)}" for c in conds)

    def add_source(self, table: str, select: tuple[str, ...]) -> None:
        """무엇을 보는가."""
        self._parts.append(f"[{table}] {' · '.join(select)}")

    def add_filters(self, conds: tuple[Condition, ...]) -> None:
        """조건. 01_naive.py처럼 필터 종류마다 분기하지 않으므로 '빠뜨릴' 필터가 없다."""
        self._parts.append(f"조건: {self._describe(conds)}")

    def add_grouping(self, group_by: tuple[str, ...], having: tuple[Condition, ...]) -> None:
        """집계."""
        text = f"{'·'.join(group_by)}별 집계"
        if having:
            text += f" (집계 후 {self._describe(having)})"
        self._parts.append(text)

    def add_limit(self, n: int) -> None:
        """상위 n개."""
        self._parts.append(f"상위 {n}개")

    def result(self) -> str:
        """완성된 요약 문장."""
        return " / ".join(self._parts)


# ---------------------------------------------------------------------------
# Director
# ---------------------------------------------------------------------------

class QueryDirector:
    """[Director] 조립 절차를 소유한다: 어떤 단계를, 어떤 순서로, 언제 생략하는가.

    이 지식(예: "WHERE가 없으면 필터 단계를 건너뛴다", "SQL 절 순서는 FROM-WHERE-GROUP-LIMIT")을
    한 곳에 두었기 때문에 새 표현(예: 데이터프레임 코드 생성기)을 추가해도 절차를 다시 쓰지 않는다.
    절차가 고정되고 단계 구현만 바뀐다는 점에서 템플릿 메서드(14장)와 닮았지만, 변이를 상속이
    아니라 '건네받은 빌더 객체'(합성)로 다룬다.
    """

    def construct(self, query: Query, renderer: QueryRenderer) -> None:
        """query를 renderer에 단계적으로 흘려 넣는다. 결과는 renderer에 쌓인다."""
        renderer.add_source(query.table, query.select)
        if query.where:
            renderer.add_filters(query.where)
        if query.group_by:
            renderer.add_grouping(query.group_by, query.having)
        if query.limit is not None:
            renderer.add_limit(query.limit)


if __name__ == "__main__":
    vip_by_category = Query(
        table="orders",
        select=("category", "SUM(amount)"),
        where=(Condition("region", "=", "서울"), Condition("member_grade", "=", "VIP"),
               Condition("order_date", ">=", "2026-01-01")),
        group_by=("category",),
        having=(Condition("SUM(amount)", ">", 1_000_000),),
        limit=5,
    )
    director = QueryDirector()

    print("[1] 같은 Query, 같은 절차 → PostgreSQL 표현")
    pg = PostgresRenderer()
    director.construct(vip_by_category, pg)
    stmt = pg.result()
    print("  text  :", stmt.text)
    print("  params:", stmt.params)

    print("\n[2] 같은 Query, 같은 절차 → 사람이 읽는 요약 (회원 등급 필터가 빠지지 않는다)")
    summary = SummaryRenderer()
    director.construct(vip_by_category, summary)
    print("  ", summary.result())

    print("\n[3] 필터·집계 없는 단순 쿼리 — 생략 규칙도 Director 한 곳에서 두 표현에 똑같이 적용")
    simple = Query(table="orders", select=("order_id", "amount"), limit=3)
    for renderer in (PostgresRenderer(), SummaryRenderer()):
        director.construct(simple, renderer)
        print(f"  {type(renderer).__name__:16}: {renderer.result()}")
