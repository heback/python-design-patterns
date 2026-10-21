"""세 원칙으로 리팩터링: 변하는 것을 찾아 → 인터페이스 뒤에 숨기고 → 합성으로 조립한다.

상황: 01_naive.py의 late_fee()는 지점 정책이 셋으로 갈라지자 if/elif가 곱해졌다. 지민의
선배 개발자 현우는 함수를 고치기 전에 질문부터 했다. "이 함수에서 지점마다 '다른' 것은
무엇이고, 어디서나 '같은' 것은 무엇인가?" 답은 이랬다.
- 같은 것: 연체 일수 × 일당 요율을 구한 뒤 조정 규칙들을 차례로 적용한다는 '절차'.
- 다른 것: 자료별 요율표, 그리고 어떤 조정 규칙(감면·면제·상한)을 어떤 순서로 쓰는가.

세 단계가 각각 교재 전체를 관통하는 원칙이다.
1. 변하는 것을 찾아 캡슐화하라   → 조정 규칙 하나하나를 클래스로 분리(Adjustment).
2. 구현이 아닌 인터페이스에 프로그래밍하라 → FeePolicy는 Adjustment 추상에만 의존.
3. 상속보다 합성                → 지점 정책 = 요율표 + 규칙 목록의 '조립'. 지점별 하위 클래스가 없다.
이 모양은 10장 전략 패턴의 씨앗이다.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import date


@dataclass(frozen=True)
class Loan:
    """대출 한 건(01과 같다)."""

    material: str
    member: str
    due: date
    returned: date
    branch: str


class Adjustment(ABC):
    """[변하는 것의 인터페이스] 기본 연체료에 적용하는 조정 규칙 하나.

    ABC를 고른 이유: 이 교재에서는 '우리가 정의하고 우리가 구현하는' 계약에 ABC를 쓴다.
    구현을 빠뜨린 규칙 클래스를 인스턴스화 시점에 잡아 주기 때문이다(Protocol과의 비교는 03).
    """

    @abstractmethod
    def apply(self, loan: Loan, fee: int) -> int:
        """조정된 연체료를 돌려준다. 다른 규칙에 대해서는 아무것도 모른다."""


class ChildDiscount(Adjustment):
    """아동 회원 50% 감면."""

    def apply(self, loan: Loan, fee: int) -> int:
        """아동이면 절반. 정수 나눗셈으로 원 단위를 유지한다."""
        return fee // 2 if loan.member == "child" else fee


@dataclass(frozen=True)
class ExamWaiver(Adjustment):
    """시험 기간 대학생 면제. 기간이 '설정'이므로 필드로 가진다 — 클래스가 필요한 이유 중 하나."""

    start: date
    end: date

    def apply(self, loan: Loan, fee: int) -> int:
        """기간 안에 반납한 대학생이면 0원."""
        if loan.member == "university" and self.start <= loan.returned <= self.end:
            return 0
        return fee


@dataclass(frozen=True)
class Cap(Adjustment):
    """연체료 상한. naive 코드에서 '순서가 결과를 바꾼다'고 경고했던 바로 그 규칙."""

    limit: int

    def apply(self, loan: Loan, fee: int) -> int:
        """상한을 넘지 않게 자른다."""
        return min(fee, self.limit)


@dataclass(frozen=True)
class FeePolicy:
    """[변하지 않는 절차] 일수 × 요율 → 규칙을 '목록 순서대로' 적용.

    naive 코드에서 숨어 있던 적용 순서가 여기서는 adjustments 리스트의 순서로 '눈에 보인다'.
    지점 정책을 하위 클래스로 만들지 않은 이유: 지점의 차이는 '행동'이 아니라 '조합'이다.
    하위 클래스로 표현하면 규칙 조합마다 클래스가 필요해 조합 폭발이 일어난다.
    """

    rates: dict[str, int]
    adjustments: list[Adjustment] = field(default_factory=list)

    def late_fee(self, loan: Loan) -> int:
        """연체료를 계산한다. 이 메서드에는 지점 이름도 회원 유형도 등장하지 않는다."""
        days = (loan.returned - loan.due).days
        if days <= 0:
            return 0
        fee = days * self.rates[loan.material]
        for rule in self.adjustments:
            fee = rule.apply(loan, fee)
        return fee


EXAM = ExamWaiver(date(2026, 6, 8), date(2026, 6, 21))

# 지점 정책은 '코드'가 아니라 '조립'이다. 01의 if 사슬이 이 표 한 장으로 바뀌었다.
BRANCH_POLICIES: dict[str, FeePolicy] = {
    "새솔": FeePolicy({"book": 100, "dvd": 500}, [ChildDiscount(), EXAM]),
    "하늘": FeePolicy({"book": 100, "dvd": 700}, [ChildDiscount()]),
    "바다": FeePolicy({"book": 100, "dvd": 500}, [EXAM]),
}


if __name__ == "__main__":
    print("[1] 01_naive.py와 같은 입력, 같은 결과")
    due, back = date(2026, 6, 10), date(2026, 6, 15)
    for branch, policy in BRANCH_POLICIES.items():
        row = []
        for material, member in (("book", "adult"), ("dvd", "adult"), ("book", "child"), ("book", "university")):
            row.append(f"{material}/{member}={policy.late_fee(Loan(material, member, due, back, branch)):>5}")
        print(f"  {branch}: " + "  ".join(row))

    print("\n[2] 새 요구: 하늘 지점만 상한 3,000원 — 기존 클래스 수정 없이 조립만 바꾼다")
    haneul = BRANCH_POLICIES["하늘"]
    capped = FeePolicy(haneul.rates, [*haneul.adjustments, Cap(3000)])
    dvd = Loan("dvd", "adult", due, back, "하늘")
    print(f"  상한 전 {haneul.late_fee(dvd)}원 → 상한 후 {capped.late_fee(dvd)}원")

    print("\n[3] 순서가 결과를 바꾸는 경우, 그 순서는 이제 리스트에 '쓰여' 있다")
    child_dvd = Loan("dvd", "child", due, back, "하늘")
    a = FeePolicy(haneul.rates, [ChildDiscount(), Cap(3000)]).late_fee(child_dvd)
    b = FeePolicy(haneul.rates, [Cap(3000), ChildDiscount()]).late_fee(child_dvd)
    print(f"  감면→상한: {a}원, 상한→감면: {b}원  (어느 쪽이 정책인지 시청에 물어볼 수 있게 되었다)")
