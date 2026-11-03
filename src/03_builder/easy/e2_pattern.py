"""03 빌더 — 패턴 코드: 유창한 빌더로 조립하고, build()에서 한 번에 검증한다.

상황: 순진한 코드의 SalesQuery는 None 행렬, "WHERE AND" 오류, 검사 없는 HAVING을
안고 있었다. 여기서는 '조립하는 객체'(QueryBuilder)와 '완성된 쿼리'(Query)를 나눈다.
[Builder] QueryBuilder / [Product] Query
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Self  # 3.11+: "이 메서드가 불린 객체의 실제 클래스"


@dataclass(frozen=True)
class Query:
    """[Product] 검증을 통과한 완성품. frozen이고 필드가 튜플이라 만든 뒤 바뀌지 않는다.

    반쯤 만들어진 Query는 없다. 불완전한 상태는 빌더에만 머물기 때문이다.
    그래서 Query를 받은 쪽은 "이게 유효한가"를 다시 따지지 않아도 된다.
    """

    where: tuple[str, ...]
    group_by: tuple[str, ...]
    having: tuple[str, ...]

    def to_sql(self) -> str:
        """조건을 모아 두었다가 한 번에 붙인다. '첫 조건인가'를 따질 일이 없다."""
        sql = "SELECT SUM(amount) FROM orders"
        if self.where:
            sql += " WHERE " + " AND ".join(self.where)
        if self.group_by:
            sql += " GROUP BY " + ", ".join(self.group_by)
        if self.having:
            sql += " HAVING " + " AND ".join(self.having)
        return sql


class QueryBuilder:
    """[Builder] 조립 중의 불완전한 상태는 여기에만 있다(가변 리스트)."""

    def __init__(self) -> None:
        """빈 상태에서 시작한다. 리스트(가변)는 조립 중에만 쓰고 완성품에는 넘기지 않는다."""
        self._where: list[str] = []
        self._group_by: list[str] = []
        self._having: list[str] = []

    # 반환 타입을 Self로 두면 하위 클래스 빌더에서 이어 불러도 타입이 유지된다.
    def where(self, cond: str) -> Self:
        """조건 하나를 더한다. 자신을 돌려주어 점으로 이어 부를 수 있다."""
        self._where.append(cond)  # 이어 붙이지 않고 모아 둔다 — 렌더링은 Query가 한 번에
        return self

    def group_by(self, col: str) -> Self:
        """묶을 열을 더한다."""
        self._group_by.append(col)
        return self

    def having(self, cond: str) -> Self:
        """집계 조건을 더한다. group_by()보다 먼저 불러도 된다 — 순서는 자유롭다."""
        self._having.append(cond)
        return self

    def build(self) -> Query:
        """완성 시점에 교차 검증한다. 조립 중에는 관대하게, 완성 시에는 엄격하게."""
        # 각 단계에서 검사하면 having()을 먼저 부르는 정당한 순서를 막게 된다.
        if self._having and not self._group_by:
            raise ValueError("HAVING을 쓰려면 GROUP BY도 있어야 한다(팀 규칙)")
        # 리스트를 튜플로 복사해 넘긴다. 빌더를 계속 써도 완성품은 영향받지 않는다.
        return Query(tuple(self._where), tuple(self._group_by), tuple(self._having))


if __name__ == "__main__":
    print("[1] 호출부가 그 자체로 쿼리를 설명한다")
    q = QueryBuilder().where("order_date >= '2026-01-01'").where("tier = 'VIP'").build()
    print("  ", q.to_sql())

    print("[2] 화면 토글에 따라 단계를 붙이거나 건너뛴다 (기간 없이 지역만)")
    # 대시보드 화면에서 사용자가 고른 값. None이면 그 필터는 건너뛴다.
    toggles = {"start": None, "region": "서울"}
    b = QueryBuilder()
    if toggles["start"]:
        b.where(f"order_date >= '{toggles['start']}'")
    if toggles["region"]:
        b.where(f"region = '{toggles['region']}'")
    print("  ", b.build().to_sql())

    print("[3] GROUP BY 없는 HAVING은 build()가 막는다 — 틀린 Query는 아예 존재하지 않는다")
    try:
        QueryBuilder().having("SUM(amount) > 100").build()
    except ValueError as e:
        print(f"  ValueError: {e}")

    print("[4] 완성품은 불변: 빌더를 더 써도 앞서 만든 Query는 그대로다")
    first = b.build()  # build()는 리스트를 튜플로 복사해 넘겼다
    b.where("tier = 'VIP'")
    print("  ", first.to_sql())
