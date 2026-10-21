"""파이썬다운 변형: 키워드 전용 dataclass + __post_init__ 검증 + dataclasses.replace 파생.

상황: 02_builder.py의 QueryBuilder는 70줄 남짓한 클래스였다. 하은의 동료 민재가 물었다.
"Java라면 이름 있는 인자가 없으니 빌더가 필요하지만, 파이썬에는 키워드 인자와 기본값이 있잖아요.
점층적 생성자 문제는 그걸로 이미 풀리는 것 아닌가요?" 이 파일은 그 질문에 답한다.

결론 미리보기:
- 점층적 생성자(None 행렬)와 반쯤 만든 객체 문제 → 키워드 전용 + frozen dataclass로 충분히 풀린다.
- 교차 검증 → __post_init__에서 할 수 있다(생성 = 검증 시점).
- 기존 쿼리에서 조금 바꾼 쿼리 파생 → dataclasses.replace가 빌더보다 간결하고, 검증도 다시 돈다.
- 그러나 '여러 코드 경로에서 조각을 조금씩 모아야 하는' 조립은 결국 손으로 만든 빌더가 된다.
"""
from __future__ import annotations

from dataclasses import dataclass, field, replace


@dataclass(frozen=True, kw_only=True)
class Query:
    """[Product이자 스스로 검증하는 값 객체] 빌더 없이 키워드 인자로 만든다.

    kw_only=True(3.10+)인 이유: 위치 인자로 부를 수 없게 막아야 01_naive.py의 None 행렬이
    원천적으로 생기지 않는다. 기본값이 있는 필드와 없는 필드의 순서 제약도 사라진다.
    """

    table: str
    select: tuple[str, ...]
    where: tuple[tuple[str, str, object], ...] = ()
    group_by: tuple[str, ...] = ()
    having: tuple[tuple[str, str, object], ...] = ()
    limit: int | None = None
    # 비교·해시에서 제외되는 메모. field(compare=False)는 '정의의 일부가 아닌' 정보를 표시하는 방법.
    note: str = field(default="", compare=False)

    def __post_init__(self) -> None:
        """교차 검증. 02의 build()가 하던 일을 '생성 시점'으로 옮겼다.

        frozen 객체는 생성 후 바뀌지 않으므로, 여기를 통과한 Query는 영원히 유효하다.
        replace()도 내부적으로 __init__을 호출하므로 이 검증을 다시 거친다.
        """
        if not self.select:
            raise ValueError("SELECT할 열이 없다")
        if self.having and not self.group_by:
            raise ValueError("HAVING은 GROUP BY와 함께 써야 한다(대시보드 규칙)")
        if self.limit is not None and self.limit <= 0:
            raise ValueError("LIMIT은 양수여야 한다")


def assemble_from_ui(toggles: dict[str, object]) -> Query:
    """대시보드 UI 토글에서 쿼리를 조립한다 — dataclass만으로는 어색해지는 경우.

    조각이 조건부로 하나씩 결정되므로, 생성자를 한 번에 부르려면 임시 리스트들에 먼저 모아야 한다.
    아래 where/group_by 리스트가 바로 '손으로 만든 빌더 상태'다. 이런 조립이 여러 곳에서
    반복되면 그 리스트와 규칙을 클래스로 묶는 것, 즉 02의 QueryBuilder가 정당화된다.
    """
    where: list[tuple[str, str, object]] = []
    group_by: list[str] = []
    for column, chosen in toggles.items():
        if column == "group":
            group_by.append(str(chosen))
        elif chosen is not None:
            where.append((column, "=", chosen))
    select = (*group_by, "SUM(amount)")
    return Query(table="orders", select=select, where=tuple(where), group_by=tuple(group_by))


if __name__ == "__main__":
    print("[1] 키워드 인자만으로 — 무엇이 무엇인지 호출부에 이름이 남는다")
    monthly = Query(table="orders", select=("month", "SUM(amount)"),
                    where=(("region", "=", "서울"),), group_by=("month",), note="월간 리포트")
    print("  ", monthly)

    print("\n[2] 위치 인자는 아예 거부된다 (kw_only)")
    try:
        Query("orders", ("month",))  # type: ignore[misc]
    except TypeError as e:
        print(f"   TypeError: {e}")

    print("\n[3] replace로 파생: 월별 쿼리에 LIMIT 3을 더한 변형. 원본은 그대로, 검증은 다시 돈다")
    top3 = replace(monthly, limit=3)
    print(f"   원본 limit={monthly.limit}, 파생 limit={top3.limit}")
    try:
        # GROUP BY를 지우면서 HAVING을 더한 파생 — 생성 시점 검증에 걸린다
        replace(monthly, group_by=(), having=(("SUM(amount)", ">", 1),))
    except ValueError as e:
        print(f"   잘못된 파생은 거부: {e}")

    print("\n[4] note는 compare=False — 메모만 다른 두 쿼리는 같은 캐시 키")
    print("  ", monthly == replace(monthly, note="다른 메모"))

    print("\n[5] 조건부 조립이 필요해지면 임시 리스트(=손수 만든 빌더)가 등장한다")
    print("  ", assemble_from_ui({"region": "부산", "category": None, "group": "category"}))
