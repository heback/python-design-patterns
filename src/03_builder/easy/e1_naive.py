"""03 빌더 — 순진한 코드: 선택 인자를 생성자에 계속 덧붙인 SalesQuery.

상황: 하은은 대시보드 요구가 들어올 때마다 SalesQuery 생성자에 선택 인자를 하나씩
추가했다. to_sql()은 문자열을 순서대로 이어 붙이고, to_summary()는 그 분기를
복사해 한국어 요약을 만든다.
"""
from __future__ import annotations


class SalesQuery:
    """매출 쿼리 하나. 만드는 즉시 완성되어야 한다."""

    def __init__(self, start: str | None = None, region: str | None = None,
                 tier: str | None = None, group_by: str | None = None,
                 having: str | None = None) -> None:
        """⚠ 문제: 선택 인자가 늘 때마다 매개변수가 하나씩 길어진다."""
        self.start, self.region, self.tier = start, region, tier
        self.group_by, self.having = group_by, having
        # ⚠ 문제: having만 있고 group_by가 없는 조합을 검사할 자리가 없다.

    def to_sql(self) -> str:
        """조건을 순서대로 이어 붙인다."""
        # 조각을 순서대로 덧붙인다. "지금이 첫 조건인가"라는 숨은 상태를 아무도 관리하지 않는다.
        sql = "SELECT SUM(amount) FROM orders"
        if self.start:
            sql += f" WHERE order_date >= '{self.start}'"
        if self.region:
            sql += f" AND region = '{self.region}'"  # ⚠ 문제: 첫 조건이면 "WHERE AND"가 된다
        if self.tier:
            sql += f" AND tier = '{self.tier}'"
        if self.group_by:
            sql += f" GROUP BY {self.group_by}"
        if self.having:
            sql += f" HAVING {self.having}"
        return sql

    def to_summary(self) -> str:
        """to_sql()의 분기를 따라 하며 요약을 만든다."""
        # SQL과 같은 정의를 다른 말로 표현할 뿐인데, 조립 절차를 통째로 다시 쓴다.
        parts = ["매출 합계"]
        if self.start:
            parts.append(f"{self.start} 이후")
        if self.region:
            parts.append(f"지역 {self.region}")
        # ⚠ 문제: 복사하다 tier 분기를 빠뜨렸다. 조립 절차가 두 벌이라 언젠가 어긋난다.
        return ", ".join(parts)


if __name__ == "__main__":
    print("[1] 호출부: 어느 None이 무엇인지 위치로만 구분된다")
    # 세 번째 자리가 등급이라는 것은 생성자 정의를 열어 봐야 안다.
    q = SalesQuery("2026-01-01", None, "VIP", None, None)
    print("  ", q.to_sql())

    print("[2] 기간 없이 지역만 걸면 문법 오류가 난다")
    # 키워드로 부르면 None 행렬은 피하지만, 아래 문법 오류는 그대로다.
    print("  ", SalesQuery(region="서울").to_sql())

    print("[3] GROUP BY 없는 HAVING도 그대로 만들어진다 (팀 규칙 위반)")
    print("  ", SalesQuery(having="SUM(amount) > 100").to_sql())

    print("[4] 요약에서 VIP 조건이 빠졌다")
    print("  ", q.to_summary())
