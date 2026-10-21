"""유창한(fluent) 빌더: 단계적으로 조립하고, build()에서 한 번에 검증해 불변 Query를 낸다.

상황: 01_naive.py의 SalesQuery는 (1) None 투성이 점층적 생성자, (2) "WHERE AND" 같은
문자열 조립 오류, (3) GROUP BY 없는 HAVING 같은 팀 규칙 위반 조합, (4) 값 직접 삽입에 의한
SQL 주입 위험을 안고 있었다. 하은의 팀은 쿼리를 '조립하는 객체(QueryBuilder)'와
'완성된 쿼리(Query)'를 분리하기로 했다.

설계 결정 요약:
- Query는 frozen dataclass: 완성·검증된 상태로만 존재한다(반쯤 만들어진 Query는 없다).
- QueryBuilder는 가변: 조립 도중의 불완전한 상태는 빌더 안에만 머문다.
- 교차 검증(HAVING ⇒ GROUP BY 등)은 각 단계가 아니라 build()에서 한다 — 단계 호출 순서가
  자유로워야 대시보드 코드가 조건부로 단계를 붙일 수 있기 때문이다.
- 값은 SQL 문자열에 넣지 않고 params로 분리한다(매개변수 바인딩).

역할 대응: [Builder] QueryBuilder, [Product] Query. GoF의 Director와 '여러 표현'은
03_director.py에서 다룬다 — 이 파일은 현업에서 더 흔한 유창한 빌더 형태다.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Self

# 식별자(테이블·열 이름)는 매개변수로 바인딩할 수 없으므로 화이트리스트 정규식으로 막는다.
_IDENT = re.compile(r"^[a-z_][a-z0-9_]*$")
_AGG = re.compile(r"^(SUM|COUNT|AVG|MIN|MAX)\(([a-z_][a-z0-9_]*|\*)\)$")
_OPS = frozenset({"=", "<>", "<", "<=", ">", ">=", "IN"})


def _check_expr(expr: str) -> str:
    """열 이름이나 집계식만 허용한다. 주입은 값뿐 아니라 식별자로도 들어오기 때문이다."""
    if not (_IDENT.match(expr) or _AGG.match(expr)):
        raise ValueError(f"허용되지 않는 식별자/식: {expr!r}")
    return expr


@dataclass(frozen=True)
class Condition:
    """WHERE/HAVING 조건 하나. 값(value)은 SQL 텍스트가 아니라 바인딩될 데이터다."""

    expr: str
    op: str
    value: object


@dataclass(frozen=True)
class Query:
    """[Product] 완성된 쿼리 정의. 표현(SQL, 요약)과 무관한 '무엇을 질의하는가'만 담는다.

    frozen=True + 컬렉션 필드는 전부 tuple: 빌더가 build() 후에도 계속 수정되더라도 이미 만든
    Query는 변하지 않는다. 대시보드 캐시의 키로도 쓸 수 있다(해시 가능).
    """

    table: str
    select: tuple[str, ...]
    where: tuple[Condition, ...] = ()
    group_by: tuple[str, ...] = ()
    having: tuple[Condition, ...] = ()
    order_by: tuple[tuple[str, bool], ...] = ()  # (식, 내림차순 여부)
    limit: int | None = None

    def to_sql(self) -> tuple[str, list[object]]:
        """PostgreSQL용 (SQL 텍스트, 매개변수 목록)을 돌려준다.

        "WHERE AND" 버그가 사라진 이유: 조건을 리스트로 모은 뒤 " AND ".join()으로
        한 번에 잇는다. '첫 조건인가'를 판단하는 상태 자체가 없다.
        """
        params: list[object] = []

        def render(conds: tuple[Condition, ...]) -> str:
            """조건들을 자리표시자(%s)로 렌더링하고 값은 params에 쌓는다."""
            parts = []
            for c in conds:
                if c.op == "IN":
                    # IN은 값 개수만큼 자리표시자를 만든다. 리스트를 문자열로 펼쳐 넣으면 주입이 되살아난다.
                    parts.append(f"{c.expr} IN ({', '.join(['%s'] * len(c.value))})")  # type: ignore[arg-type]
                    params.extend(c.value)  # type: ignore[arg-type]
                else:
                    parts.append(f"{c.expr} {c.op} %s")
                    params.append(c.value)
            return " AND ".join(parts)

        # 절을 리스트에 모아 마지막에 공백으로 잇는다. 절 순서는 SQL 문법이 정한 고정 순서다.
        # 식별자는 빌더 단계에서 화이트리스트를 통과한 것만 여기 도달하므로 텍스트로 넣어도 된다.
        sql = [f"SELECT {', '.join(self.select)} FROM {self.table}"]
        if self.where:
            sql.append("WHERE " + render(self.where))
        if self.group_by:
            sql.append("GROUP BY " + ", ".join(self.group_by))
        if self.having:
            # WHERE와 같은 render()를 쓰므로 params 순서가 SQL 속 자리표시자 순서와 일치한다.
            sql.append("HAVING " + render(self.having))
        if self.order_by:
            sql.append("ORDER BY " + ", ".join(f"{e}{' DESC' if d else ''}" for e, d in self.order_by))
        if self.limit is not None:
            sql.append(f"LIMIT {self.limit}")  # limit()가 양의 int만 통과시키므로 텍스트에 넣어도 안전하다
        return " ".join(sql), params


class QueryBuilder:
    """[Builder] Query를 단계적으로 조립한다. 각 단계는 self를 돌려줘 체이닝된다.

    반환 타입이 Self(3.11+)인 이유: 하위 클래스(예: 특정 대시보드 전용 빌더)에서 체이닝해도
    타입 검사기가 하위 클래스 메서드를 계속 인식하게 하려는 것이다.
    """

    def __init__(self, table: str) -> None:
        """필수 값(테이블)만 생성자에서 받는다. 선택 사항은 전부 이름 붙은 단계가 된다."""
        self._table = _check_expr(table)
        # 조립 중 상태는 모두 가변 리스트다. 이 가변성이 빌더 밖으로 새지 않게 build()가 tuple로 복사한다.
        self._select: list[str] = []
        self._where: list[Condition] = []
        self._group_by: list[str] = []
        self._having: list[Condition] = []
        self._order_by: list[tuple[str, bool]] = []
        self._limit: int | None = None

    def select(self, *exprs: str) -> Self:
        """조회할 열·집계식을 더한다. 여러 번 불러도 누적된다."""
        self._select.extend(_check_expr(e) for e in exprs)
        return self

    def where(self, expr: str, op: str, value: object) -> Self:
        """WHERE 조건을 더한다. 연산자도 화이트리스트로 검사한다(연산자 자리 주입 방지)."""
        if op not in _OPS:
            raise ValueError(f"허용되지 않는 연산자: {op!r}")
        if op == "IN":
            value = tuple(value)  # type: ignore[arg-type]  # list는 해시 불가 → Query가 해시 가능하도록 tuple로
        self._where.append(Condition(_check_expr(expr), op, value))
        return self

    def group_by(self, *exprs: str) -> Self:
        """집계 기준 열을 더한다."""
        self._group_by.extend(_check_expr(e) for e in exprs)
        return self

    def having(self, expr: str, op: str, value: object) -> Self:
        """HAVING 조건을 더한다. GROUP BY와의 관계는 여기서 검사하지 않는다(아래 build() 참고)."""
        if op not in _OPS:
            raise ValueError(f"허용되지 않는 연산자: {op!r}")
        self._having.append(Condition(_check_expr(expr), op, value))
        return self

    def order_by(self, expr: str, *, desc: bool = False) -> Self:
        """정렬 기준을 더한다. desc는 키워드 전용 — order_by("x", True)의 True가 무엇인지 모호하므로."""
        self._order_by.append((_check_expr(expr), desc))
        return self

    def limit(self, n: int) -> Self:
        """행 수 제한. 개별 값 검사는 즉시 한다(다른 단계와 무관한 제약이므로)."""
        # bool은 int의 하위 클래스라 따로 거른다(limit(True)가 LIMIT True가 되지 않게).
        if not isinstance(n, int) or isinstance(n, bool) or n <= 0:
            raise ValueError("LIMIT은 양의 정수여야 한다")
        self._limit = n
        return self

    def build(self) -> Query:
        """교차 검증 후 불변 Query를 만든다.

        단계별로 검사하지 않고 여기서 모아 검사하는 이유: having()이 group_by()보다 먼저
        호출되는 것도 정당한 조립 순서다. '조립 순서는 자유, 완성 조건은 엄격'이 빌더의 계약이다.
        """
        if not self._select:
            raise ValueError("SELECT할 열이 없다")
        if self._having and not self._group_by:
            # SQL 문법은 GROUP BY 없는 HAVING을 허용하지만, 이 팀에서 그것은 언제나 group_by()를
            # 빠뜨린 실수였다. 그래서 문법보다 엄격한 '대시보드 규칙'으로 막는다.
            raise ValueError("HAVING은 GROUP BY와 함께 써야 한다(대시보드 규칙)")
        if self._group_by:
            # 집계식이 아닌 SELECT 열은 모두 GROUP BY에 있어야 한다(PostgreSQL 규칙).
            loose = [e for e in self._select if not _AGG.match(e) and e not in self._group_by]
            if loose:
                raise ValueError(f"GROUP BY에 없는 비집계 열: {loose}")
        # list → tuple 복사: 빌더를 계속 쓰더라도 이 Query는 영향받지 않는다.
        return Query(self._table, tuple(self._select), tuple(self._where), tuple(self._group_by),
                     tuple(self._having), tuple(self._order_by), self._limit)


if __name__ == "__main__":
    print("[1] 월별 서울 매출 — 각 단계가 이름을 가지므로 None 행렬이 없다")
    monthly = (QueryBuilder("orders")
               .select("month", "SUM(amount)")
               .where("order_date", ">=", "2026-01-01")
               .where("order_date", "<", "2026-07-01")
               .where("region", "=", "서울")
               .group_by("month")
               .order_by("month")
               .build())
    # 결과는 (텍스트, 값) 쌍이다. 실제로는 cursor.execute(sql, params)로 드라이버에 넘긴다.
    sql, params = monthly.to_sql()
    print("  SQL   :", sql)
    print("  params:", params)

    print("\n[2] 기간 없이 지역만 — 'WHERE AND'가 생길 수 없는 구조")
    print("  ", QueryBuilder("orders").select("order_id").where("region", "=", "부산").build().to_sql())

    print("\n[3] 대시보드 UI 토글에 따라 단계를 조건부로 붙인다 (빌더가 빛나는 지점)")
    # 실제 대시보드라면 요청 파라미터에서 온다. None은 '사용자가 이 필터를 고르지 않음'.
    ui_filters = {"category": "가전", "member_grade": None, "region": ["서울", "경기"]}
    b = QueryBuilder("orders").select("category", "SUM(amount)").group_by("category")
    for column, chosen in ui_filters.items():
        if chosen is None:
            continue  # 선택하지 않은 필터는 단계 자체를 건너뛴다
        # 여러 값을 고르면 IN, 하나면 =. 이런 분기가 호출부에 자연스럽게 섞일 수 있는 것이 빌더의 장점이다.
        b.where(column, "IN" if isinstance(chosen, list) else "=", chosen)
    b.having("SUM(amount)", ">", 1_000_000).order_by("SUM(amount)", desc=True).limit(10)
    print("  ", b.build().to_sql())

    print("\n[4] 잘못된 조합은 build()에서 막힌다")
    # 람다로 감싼 이유: 실패가 build() 호출 시점에 일어난다는 것을 각 경우마다 따로 보여 주기 위해.
    for label, make in [
        ("GROUP BY 없는 HAVING", lambda: QueryBuilder("orders").select("category", "SUM(amount)")
            .having("SUM(amount)", ">", 1).build()),
        ("비집계 열 누락", lambda: QueryBuilder("orders").select("region", "SUM(amount)")
            .group_by("month").build()),
    ]:
        try:
            make()
        except ValueError as e:
            print(f"  {label}: ValueError — {e}")

    print("\n[5] Query는 불변·해시 가능 → 대시보드 결과 캐시의 키로 쓸 수 있다")
    top10 = b.build()
    cache = {top10: "어제 계산한 결과"}
    b.limit(20)  # 같은 빌더를 계속 바꿔도 이미 만든 Query(top10)는 그대로다
    print(f"  빌더 수정 후에도 top10.limit = {top10.limit}, 새 build().limit = {b.build().limit}")
    print(f"  limit을 10으로 되돌려 다시 build하면 값이 같은 Query → 같은 키: {cache.get(b.limit(10).build(), '캐시 없음')}")

    print("\n[6] 주입 시도는 값이면 바인딩되고, 식별자면 거부된다")
    sql, params = QueryBuilder("orders").select("order_id").where("region", "=", "서울' OR '1'='1").build().to_sql()
    print(f"  값 자리: {sql}  params={params}")
    try:
        # 식별자는 바인딩할 수 없으므로(DB 드라이버는 값만 바인딩한다) 단계 호출 즉시 거부한다.
        QueryBuilder("orders").select("order_id; DROP TABLE orders")
    except ValueError as e:
        print(f"  식별자 자리: ValueError — {e}")
