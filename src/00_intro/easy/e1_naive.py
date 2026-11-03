"""00 서론 — 순진한 코드: 규칙이 늘 때마다 if가 자라는 도서관 연체료 함수.

상황: 새솔도서관 사서 지민의 연체료 함수는 "일수 × 100원" 한 줄이었다. 아동 감면,
DVD 요율, 시험 기간 면제가 붙고, 지점 세 곳(새솔·하늘·바다)이 정책을 따로 정하게 되자
지점 조건이 규칙마다 끼어들었다. 이 코드는 그 결과다.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class Loan:
    """대출 한 건. 생성 후 바뀌지 않는 사실이라 frozen으로 둔다."""

    material: str   # "book" | "dvd"
    member: str     # "adult" | "child" | "university"
    due: date       # 반납 기한
    returned: date  # 실제 반납일
    branch: str     # "새솔" | "하늘" | "바다"


EXAM = (date(2026, 6, 8), date(2026, 6, 21))  # 시험 기간(대학생 면제)


def late_fee(loan: Loan) -> int:
    """연체료(원). 바뀌는 규칙이 전부 이 함수 하나에 쌓여 있다."""
    days = (loan.returned - loan.due).days
    if days <= 0:
        return 0
    # ⚠ 문제: 요율이 지점 분기 안에 복제되어 있다. 하늘 지점만 DVD 700원이다.
    if loan.branch == "하늘":
        rate = 700 if loan.material == "dvd" else 100
    else:
        rate = 500 if loan.material == "dvd" else 100
    fee = days * rate
    # ⚠ 문제: 감면 규칙과 지점 조건이 한 줄에 엉켜 있다(바다 지점은 아동 감면 없음).
    if loan.member == "child" and loan.branch != "바다":
        fee //= 2
    # ⚠ 문제: 규칙의 적용 '순서'가 어디에도 적혀 있지 않다. if가 놓인 위치가 곧 정책이다.
    if loan.member == "university" and EXAM[0] <= loan.returned <= EXAM[1]:
        if loan.branch != "하늘":  # 하늘 지점은 시험 기간 면제가 없다
            fee = 0
    return fee


if __name__ == "__main__":
    due, back = date(2026, 6, 10), date(2026, 6, 15)  # 5일 연체
    print("[1] 지점별 연체료 (책/성인, DVD/성인, 책/아동, 책/대학생)")
    for branch in ("새솔", "하늘", "바다"):
        fees = [late_fee(Loan(m, who, due, back, branch))
                for m, who in [("book", "adult"), ("dvd", "adult"), ("book", "child"), ("book", "university")]]
        print(f"  {branch}: {fees}")

    print("[2] 이 함수를 고쳐야 하는 이유")
    # 이유가 여럿이고 서로 무관하다 — 바뀌어야 할 이유가 하나여야 한다는 SRP 위반이다.
    for reason in ("요율 변경", "감면 정책 변경", "시험 기간 변경", "지점 예외 추가", "새 지점", "상한 도입"):
        print(f"  - {reason}")
