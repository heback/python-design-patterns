"""00 서론 — 리팩터링 코드: 변하는 것을 찾아, 인터페이스 뒤에 숨기고, 합성으로 조립한다.

상황: 순진한 코드의 late_fee()는 지점 정책이 셋으로 갈리자 if가 곱해졌다. 먼저 물었다.
"어디서나 같은 것은? 지점마다 다른 것은?"
- 같은 것: 일수 × 요율을 구한 뒤 조정 규칙을 차례로 적용하는 '절차' → FeePolicy
- 다른 것: 요율표, 그리고 어떤 규칙을 어떤 순서로 쓰는가 → Adjustment 목록
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class Loan:
    """대출 한 건(순진한 코드와 같다)."""

    material: str
    member: str
    due: date
    returned: date
    branch: str


class Adjustment(ABC):
    """[변하는 것의 인터페이스] 연체료에 적용하는 조정 규칙 하나.

    ABC를 쓴 이유: 우리가 정하고 우리가 구현하는 확장 지점이라, apply()를 빠뜨린
    규칙 클래스를 인스턴스를 만드는 순간 TypeError로 잡고 싶다.
    """

    @abstractmethod
    def apply(self, loan: Loan, fee: int) -> int:
        """조정된 금액을 돌려준다. 다른 규칙은 모른다."""


class ChildDiscount(Adjustment):
    """아동 50% 감면."""

    def apply(self, loan: Loan, fee: int) -> int:
        """아동이면 절반."""
        return fee // 2 if loan.member == "child" else fee


@dataclass(frozen=True)
class ExamWaiver(Adjustment):
    """시험 기간 대학생 면제. 기간이라는 '설정'을 필드로 가진다."""

    start: date
    end: date

    def apply(self, loan: Loan, fee: int) -> int:
        """기간 안에 반납한 대학생이면 0원."""
        return 0 if loan.member == "university" and self.start <= loan.returned <= self.end else fee


@dataclass(frozen=True)
class Cap(Adjustment):
    """상한. 순진한 코드라면 '어느 if 앞에 둘까'로 하루를 보냈을 규칙."""

    limit: int

    def apply(self, loan: Loan, fee: int) -> int:
        """상한을 넘지 않게 자른다."""
        return min(fee, self.limit)


@dataclass(frozen=True)
class FeePolicy:
    """[변하지 않는 절차] 일수 × 요율 → 규칙을 목록 순서대로 적용.

    지점마다 하위 클래스를 만들지 않은 이유: 지점의 차이는 '행동'이 아니라 '조합'이다(합성 우선).
    """

    rates: dict[str, int]
    adjustments: list[Adjustment]

    def late_fee(self, loan: Loan) -> int:
        """지점 이름도 회원 유형도 등장하지 않는다."""
        days = (loan.returned - loan.due).days
        if days <= 0:
            return 0
        fee = days * self.rates[loan.material]
        for rule in self.adjustments:  # 적용 순서 = 리스트 순서. 이제 눈에 보인다.
            fee = rule.apply(loan, fee)
        return fee


# 규칙 객체는 frozen이라 여러 지점이 같은 인스턴스를 나눠 써도 안전하다.
EXAM = ExamWaiver(date(2026, 6, 8), date(2026, 6, 21))
# 지점 정책은 코드가 아니라 '조립'이다. 순진한 코드의 if 사슬이 이 표 한 장이 되었다.
BRANCH_POLICIES = {
    "새솔": FeePolicy({"book": 100, "dvd": 500}, [ChildDiscount(), EXAM]),
    "하늘": FeePolicy({"book": 100, "dvd": 700}, [ChildDiscount()]),
    "바다": FeePolicy({"book": 100, "dvd": 500}, [EXAM]),
}


if __name__ == "__main__":
    due, back = date(2026, 6, 10), date(2026, 6, 15)  # 5일 연체
    print("[1] 순진한 코드와 같은 입력, 같은 결과 (동작 보존)")
    for branch, policy in BRANCH_POLICIES.items():
        fees = [policy.late_fee(Loan(m, who, due, back, branch))
                for m, who in [("book", "adult"), ("dvd", "adult"), ("book", "child"), ("book", "university")]]
        print(f"  {branch}: {fees}")

    print("[2] 하늘 지점에 상한 3,000원 추가 — 기존 클래스는 그대로, 조립만 바꾼다")
    haneul = FeePolicy({"book": 100, "dvd": 700}, [ChildDiscount(), Cap(3000)])
    print(f"  DVD/성인 5일: {haneul.late_fee(Loan('dvd', 'adult', due, back, '하늘'))}원")

    print("[3] 순서가 결과를 바꾼다 — 그 순서가 이제 리스트에 적혀 있다")
    kid = Loan("dvd", "child", due, back, "하늘")
    a = FeePolicy({"dvd": 700}, [ChildDiscount(), Cap(3000)]).late_fee(kid)
    b = FeePolicy({"dvd": 700}, [Cap(3000), ChildDiscount()]).late_fee(kid)
    print(f"  감면→상한 {a}원, 상한→감면 {b}원")
