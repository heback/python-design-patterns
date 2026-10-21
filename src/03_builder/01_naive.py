"""순진한 설계: 매개변수 11개짜리 생성자와 문자열 이어 붙이기로 SQL을 만든다.

상황: 이커머스 회사 '장바구니랩'의 데이터 분석가 하은은 사내 BI 대시보드의 "기간별 매출"
차트용 SQL을 문자열 포매팅으로 만들었다. 대시보드가 늘면서 지역·카테고리·회원 등급 필터,
GROUP BY·HAVING·ORDER BY·LIMIT 조합이 차트마다 달라졌고, 하은은 그때마다 생성자에
선택 인자를 하나씩 추가했다. 이어서 "같은 쿼리를 사람이 읽는 요약으로도 보여 달라"는
요청이 와서 to_summary()를 만들었다.

읽을 때 주목할 점:
- 호출부의 None 행렬: 어느 None이 어느 인자인지 위치로만 알 수 있다.
- 조건부 문자열 이어 붙이기가 만드는 문법 오류("WHERE AND")와 팀 규칙상 실수인 조합(GROUP BY 없는 HAVING — 비집계 열이 섞이면 DB도 거부한다).
- 값이 SQL 문자열에 직접 들어가는 주입(injection) 위험.
- to_sql()과 to_summary()가 같은 분기 구조를 복제한다.
"""
from __future__ import annotations


class SalesQuery:
    """대시보드 매출 쿼리. 모든 선택 사항이 생성자 인자다."""

    def __init__(self, table: str, columns: str, start: str | None = None,
                 end: str | None = None, region: str | None = None,
                 category: str | None = None, grade: str | None = None,
                 group_by: str | None = None, having: str | None = None,
                 order_by: str | None = None, limit: int | None = None) -> None:
        """⚠ 문제: 점층적 생성자(telescoping constructor). 선택 인자가 하나 늘 때마다
        모든 호출부가 '위치'를 다시 맞춰야 하고, 인자 사이의 제약(HAVING은 GROUP BY가
        있어야 의미가 있다)은 시그니처에 전혀 드러나지 않는다.
        """
        self.table, self.columns = table, columns
        self.start, self.end = start, end
        self.region, self.category, self.grade = region, category, grade
        self.group_by, self.having = group_by, having
        self.order_by, self.limit = order_by, limit

    def to_sql(self) -> str:
        """SQL 문자열을 만든다."""
        sql = f"SELECT {self.columns} FROM {self.table}"
        if self.start or self.end or self.region or self.category or self.grade:
            sql += " WHERE"
        # ⚠ 문제: 첫 조건만 AND 없이 붙는다고 '가정'했다. start가 없으면 "WHERE AND"가 된다.
        if self.start:
            sql += f" order_date >= '{self.start}'"
        if self.end:
            sql += f" AND order_date < '{self.end}'"
        # ⚠ 문제: 값을 문자열에 그대로 끼워 넣는다 → SQL 주입. 따옴표가 든 값이면 쿼리가 바뀐다.
        if self.region:
            sql += f" AND region = '{self.region}'"
        if self.category:
            sql += f" AND category = '{self.category}'"
        if self.grade:
            sql += f" AND member_grade = '{self.grade}'"
        if self.group_by:
            sql += f" GROUP BY {self.group_by}"
        # ⚠ 문제: GROUP BY 없이도 HAVING이 붙는다. SQL 문법상 허용되지만(전체를 한 그룹으로 봄)
        #   SELECT에 비집계 열(category)이 있으면 DB가 거부한다. 이런 조합을 미리 막을 시점이 없다.
        if self.having:
            sql += f" HAVING {self.having}"
        if self.order_by:
            sql += f" ORDER BY {self.order_by}"
        if self.limit:
            sql += f" LIMIT {self.limit}"
        return sql

    def to_summary(self) -> str:
        """사람이 읽는 요약. ⚠ 문제: to_sql()의 분기를 거의 그대로 복제했다.
        새 필터를 추가하면 두 메서드를 모두 고쳐야 하고, 한쪽을 잊으면 둘이 어긋난다.
        """
        parts = [f"{self.table}에서 {self.columns}"]
        if self.start or self.end:
            parts.append(f"기간 {self.start or '처음'}~{self.end or '현재'}")
        if self.region:
            parts.append(f"지역={self.region}")
        if self.category:
            parts.append(f"카테고리={self.category}")
        # (grade 요약을 깜빡했다 — 바로 위 docstring이 말한 어긋남이 실제로 일어났다)
        if self.group_by:
            parts.append(f"{self.group_by}별 집계")
        return ", ".join(parts)


if __name__ == "__main__":
    print("[1] 정상 경로: 기간 + 지역 필터, 월별 집계")
    q = SalesQuery("orders", "month, SUM(amount)", "2026-01-01", "2026-07-01", "서울",
                   None, None, "month", None, "month", None)  # ← None 하나하나가 무엇인지?
    print("  ", q.to_sql())

    print("\n[2] 기간 없이 지역만 걸면")
    print("  ", SalesQuery("orders", "*", region="부산").to_sql())

    print("\n[3] GROUP BY 없이 HAVING (오타로 group_by 인자를 빠뜨림)")
    print("  ", SalesQuery("orders", "category, SUM(amount)", having="SUM(amount) > 1000000").to_sql())

    print("\n[4] 대시보드 검색창에 누군가 따옴표를 입력하면")
    # start를 넣어 [2]의 'WHERE AND' 버그를 피했다 — 그래야 문법상 '유효한' 주입 쿼리가 보인다.
    # OR이 AND보다 우선순위가 낮으므로 기간 조건까지 무력화되어 전체 주문이 조회된다.
    print("  ", SalesQuery("orders", "*", start="2026-01-01", region="서울' OR '1'='1").to_sql())

    print("\n[5] 같은 쿼리의 요약 — 회원 등급 필터가 사라졌다")
    vip = SalesQuery("orders", "SUM(amount)", start="2026-01-01", region="서울", grade="VIP")
    print("   SQL :", vip.to_sql())
    print("   요약:", vip.to_summary())
