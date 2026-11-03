"""00 서론 — 파이썬다운 변형: 함수·클로저·__call__로 같은 정책을 다시 조립한다.

상황: 리팩터링 코드의 ChildDiscount는 상태도 없고 메서드도 apply() 하나다. 파이썬에서
이것은 그냥 함수가 아닌가? 이 코드는 규칙 계약을 Protocol로 바꾸고, 규칙을 세 재료로 만든다.
그리고 이 교재가 장마다 묻는 질문을 던진다. "여기서 클래스가 필요한 순간은 언제인가?"
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Protocol


@dataclass(frozen=True)
class Loan:
    """대출 한 건. 지점은 정책 표의 키로 고르므로 뺐다."""

    material: str
    member: str
    due: date
    returned: date


class Adjustment(Protocol):
    """[계약] '(loan, fee)를 받아 int를 돌려주는 것'이면 무엇이든 규칙이다.

    ABC와 달리 상속이 필요 없다. 함수, 람다, __call__을 가진 객체가 모두 자격을 얻는다.
    대신 모양이 맞는지는 실행 전에 정적 타입 검사기가 확인한다.
    """

    def __call__(self, loan: Loan, fee: int) -> int:
        """조정된 금액."""
        ...


def child_discount(loan: Loan, fee: int) -> int:
    """상태 없는 규칙 → 함수 하나로 충분하다(클래스·인스턴스화가 사라졌다)."""
    return fee // 2 if loan.member == "child" else fee


def cap(limit: int) -> Adjustment:
    """설정이 있는 규칙 1: 클로저. limit을 기억하는 안쪽 함수를 돌려준다."""

    def apply(loan: Loan, fee: int) -> int:
        """기억해 둔 limit으로 자른다."""
        return min(fee, limit)

    return apply


@dataclass(frozen=True)
class ExamWaiver:
    """설정이 있는 규칙 2: __call__을 가진 클래스.

    클로저 대신 클래스를 고른 이유: describe()라는 두 번째 행동이 있고, 설정값을
    repr로 바깥에 보여 줘야 하기 때문이다. 이것이 '클래스가 필요한 순간'의 신호다.
    """

    start: date
    end: date

    def __call__(self, loan: Loan, fee: int) -> int:
        """__call__ 덕분에 이 객체는 함수처럼 불린다."""
        return 0 if loan.member == "university" and self.start <= loan.returned <= self.end else fee

    def describe(self) -> str:
        """함수에는 둘 수 없는 두 번째 행동."""
        return f"시험 기간 {self.start:%m/%d}~{self.end:%m/%d} 대학생 면제"


@dataclass(frozen=True)
class FeePolicy:
    """리팩터링 코드와 같은 절차. rule.apply(...) 대신 rule(...)로 부르는 것만 다르다."""

    rates: dict[str, int]
    adjustments: list[Adjustment]

    def late_fee(self, loan: Loan) -> int:
        """함수든 객체든 똑같이 '호출'한다 — 덕 타이핑."""
        days = (loan.returned - loan.due).days
        if days <= 0:
            return 0
        fee = days * self.rates[loan.material]
        for rule in self.adjustments:
            fee = rule(loan, fee)
        return fee


EXAM = ExamWaiver(date(2026, 6, 8), date(2026, 6, 21))


if __name__ == "__main__":
    due, back = date(2026, 6, 10), date(2026, 6, 15)  # 5일 연체
    print("[1] 함수·클로저·__call__ 객체가 한 목록 안에서 똑같이 쓰인다")
    haneul = FeePolicy({"book": 100, "dvd": 700}, [child_discount, cap(3000), EXAM])
    print(f"  규칙 종류: {[type(r).__name__ for r in haneul.adjustments]}")
    print(f"  DVD/아동 5일: {haneul.late_fee(Loan('dvd', 'child', due, back))}원")

    print("[2] 클래스로 둔 규칙만 자기를 설명할 수 있다")
    print(f"  {EXAM!r}")
    print(f"  {EXAM.describe()}")
    print(f"  cap(3000) → {cap(3000).__qualname__}  (설정값 3000이 보이지 않는다)")

    print("[3] 테스트 대역도 상속 없이 람다 한 줄")
    fake = FeePolicy({"book": 100}, [lambda loan, fee: 100])
    print(f"  {fake.late_fee(Loan('book', 'adult', due, back))}원")
