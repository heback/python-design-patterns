"""03 빌더 — 파이썬다운 변형: 빌더 없이 키워드 전용 dataclass로.

상황: 유창한 빌더가 Java에서 필요했던 큰 이유는 이름 있는 인자와 기본값이 없어서였다.
파이썬에는 둘 다 있다. kw_only, frozen, __post_init__, dataclasses.replace로
패턴 코드의 Query를 빌더 없이 만든다.
"""
from __future__ import annotations

from dataclasses import dataclass, replace


@dataclass(frozen=True, kw_only=True)
class Query:
    """완성된 쿼리. kw_only=True라 위치 인자로는 만들 수 없다 — None 행렬이 불가능하다."""

    # 튜플을 쓰는 이유: frozen은 필드 재대입만 막는다. 리스트라면 안쪽을 바꿀 수 있다.
    where: tuple[str, ...] = ()
    group_by: tuple[str, ...] = ()
    having: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        """빌더의 build()가 하던 교차 검증을 생성 직후에 한다."""
        # 생성자·replace() 어느 길로 만들어도 이 검사를 지나므로, 틀린 Query는 존재할 수 없다.
        if self.having and not self.group_by:
            raise ValueError("HAVING을 쓰려면 GROUP BY도 있어야 한다(팀 규칙)")


if __name__ == "__main__":
    print("[1] 이름으로 부르니 무엇이 무엇인지 보인다")
    q = Query(where=("tier = 'VIP'",), group_by=("month",))
    print("  ", q)

    print("[2] 위치 인자 호출은 막힌다")
    try:
        Query(("tier = 'VIP'",))  # type: ignore[misc]
    except TypeError as e:
        print(f"  TypeError: {e}")

    print("[3] replace()로 하나만 바꾼 쿼리를 파생해도 검증은 다시 돈다")
    # replace()는 생성자를 다시 부른다. 그래서 파생된 쿼리도 같은 검사를 거친다.
    print("  ", replace(q, having=("SUM(amount) > 100",)))
    try:
        replace(q, group_by=(), having=("SUM(amount) > 100",))
    except ValueError as e:
        print(f"  ValueError: {e}")
