"""순진한 설계: 규칙이 늘 때마다 자라는 도서관 연체료 함수.

상황: 구립 새솔도서관의 사서 지민은 반납일을 넘긴 도서의 연체료(일당 100원)를 계산하는
함수를 만들었다. 처음에는 한 줄이었다. 그 뒤 아동 회원 50% 감면, DVD 일당 500원,
시험 기간 대학생 면제가 차례로 붙었고, 이번에는 시청이 "구립 도서관 세 곳의 정책을
각자 다르게 운영하라"고 했다. 이 파일은 그 요구를 if/elif로 받아들인 결과다.

읽을 때 주목할 점:
- 자료 유형 × 회원 유형 × 기간 × 지점의 조합이 한 함수 안에서 곱해진다.
- 새 규칙 하나가 기존 분기 사이에 끼어들며, 적용 '순서'가 암묵적인 정책이 된다.
- 이 함수가 바뀌어야 할 이유가 규칙의 수만큼 있다(SRP), 새 규칙은 늘 수정이다(OCP).
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class Loan:
    """대출 한 건. 연체료 계산에 필요한 사실만 담는다."""

    material: str      # "book" | "dvd"
    member: str        # "adult" | "child" | "university"
    due: date
    returned: date
    branch: str        # "새솔" | "하늘" | "바다"


EXAM_WEEKS = (date(2026, 6, 8), date(2026, 6, 21))  # 시험 기간(대학생 면제)


def late_fee(loan: Loan) -> int:
    """연체료(원)를 계산한다."""
    days = (loan.returned - loan.due).days
    if days <= 0:
        return 0
    # ⚠ 문제: 자료 유형 요율이 지점 분기 '안'에 복제되어 있다. 하늘 지점만 DVD 요율이 다르다.
    if loan.branch == "하늘":
        rate = 700 if loan.material == "dvd" else 100
    else:
        rate = 500 if loan.material == "dvd" else 100
    fee = days * rate
    # ⚠ 문제: 감면·면제 규칙이 지점 조건과 뒤엉킨다. 바다 지점은 아동 감면이 없다는 요구를
    #   넣으면서 조건이 길어졌고, 다음 요구가 오면 이 줄을 또 고쳐야 한다.
    if loan.member == "child" and loan.branch != "바다":
        fee = fee // 2
    # ⚠ 문제: 적용 '순서'가 숨은 정책이다. 면제를 감면보다 먼저 두든 나중에 두든 결과가 같아
    #   보이지만, 다음에 '최대 3,000원 상한' 규칙이 들어오면 순서가 결과를 바꾼다.
    if loan.member == "university" and EXAM_WEEKS[0] <= loan.returned <= EXAM_WEEKS[1]:
        if loan.branch in ("새솔", "바다"):  # 하늘 지점은 시험 기간 면제를 하지 않는다
            fee = 0
    return fee


if __name__ == "__main__":
    print("[1] 지점·회원·자료별 연체료 (모두 5일 연체)")
    due, back = date(2026, 6, 10), date(2026, 6, 15)
    for branch in ("새솔", "하늘", "바다"):
        row = []
        for material, member in (("book", "adult"), ("dvd", "adult"), ("book", "child"), ("book", "university")):
            row.append(f"{material}/{member}={late_fee(Loan(material, member, due, back, branch)):>5}")
        print(f"  {branch}: " + "  ".join(row))

    print("\n[2] 이 함수를 수정해야 하는 이유를 세어 보면")
    reasons = ["자료 유형 요율 변경", "회원 감면 정책 변경", "시험 기간 변경",
               "지점별 예외 추가", "새 지점 개설", "상한·하한 도입"]
    for r in reasons:
        print(f"  - {r}")
    print(f"  → 변경 이유 {len(reasons)}가지가 한 함수에 모여 있다")
