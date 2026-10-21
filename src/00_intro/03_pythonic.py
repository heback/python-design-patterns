"""파이썬이라는 렌즈: Protocol(구조적 타이핑), 일급 함수, __call__ — 클래스가 필요한 순간은 언제인가.

상황: 02_refactored.py는 조정 규칙마다 Adjustment ABC를 상속한 클래스를 만들었다. Java라면
자연스러운 모양이다. 그런데 ChildDiscount는 상태도 없고 메서드도 apply() 하나뿐이다.
파이썬에서 이것은 그냥 '함수'가 아닌가? 이 파일은 같은 정책을 세 가지 재료로 다시 조립한다.
1. 상태 없는 규칙        → 평범한 함수 (일급 함수)
2. 설정이 있는 규칙      → 클로저, 또는 __call__을 가진 작은 클래스
3. 계약(인터페이스)      → typing.Protocol: 상속 없이 '모양'만 맞으면 된다

그리고 교재 전체의 반복 질문을 던진다: "여기서 클래스가 필요한 순간은 언제인가?"
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Protocol


@dataclass(frozen=True)
class Loan:
    """대출 한 건. 01·02에서 branch를 뺐다 — 이 파일은 지점을 BRANCH_POLICIES의 키로 고르므로 대출에 실을 필요가 없다."""

    material: str
    member: str
    due: date
    returned: date


class Adjustment(Protocol):
    """[구조적 인터페이스] '(loan, fee)를 받아 int를 돌려주는 호출 가능한 것'이면 무엇이든.

    ABC(명목적 타이핑)와의 차이: 구현체가 이 클래스를 상속하거나 import할 필요가 없다.
    함수, 람다, __call__을 가진 객체가 모두 자격을 얻는다. 검사는 mypy 같은 정적 검사기가 한다.
    선택 기준(이 교재 전체에서 쓰는 것):
    - 우리가 소유한 확장 지점이고, 구현 누락을 실행 시점에 잡고 싶다 → ABC
    - 외부 코드·함수·테스트 대역이 상속 없이 끼어들어야 한다      → Protocol
    """

    def __call__(self, loan: Loan, fee: int) -> int:
        """조정된 연체료."""
        ...


def child_discount(loan: Loan, fee: int) -> int:
    """상태 없는 규칙은 함수 하나로 충분하다. 클래스 + 메서드 + 인스턴스화가 모두 사라졌다."""
    return fee // 2 if loan.member == "child" else fee


def cap(limit: int) -> Adjustment:
    """설정이 있는 규칙 1: 클로저. limit을 캡처한 함수를 돌려준다(함수를 만드는 함수)."""

    def apply(loan: Loan, fee: int) -> int:
        """캡처한 limit으로 자른다."""
        return min(fee, limit)

    return apply


@dataclass(frozen=True)
class ExamWaiver:
    """설정이 있는 규칙 2: __call__을 가진 클래스. '함수처럼 호출되면서' 추가 기능도 갖는다.

    클로저 대신 클래스를 고른 이유: describe()처럼 '두 번째 메서드'가 필요하고, 설정값(start, end)을
    출력·비교·직렬화하고 싶기 때문이다(dataclass가 __repr__과 __eq__를 공짜로 준다).
    클로저는 이런 것을 외부에 드러내지 못한다 — 이것이 '클래스가 필요한 순간'의 대표 신호다.
    """

    start: date
    end: date

    def __call__(self, loan: Loan, fee: int) -> int:
        """__call__ 덕분에 이 객체는 Adjustment 프로토콜을 만족한다."""
        if loan.member == "university" and self.start <= loan.returned <= self.end:
            return 0
        return fee

    def describe(self) -> str:
        """사람이 읽는 설명. 함수에는 둘 수 없는 두 번째 행동."""
        return f"시험 기간 {self.start:%m/%d}~{self.end:%m/%d} 대학생 면제"


@dataclass(frozen=True)
class FeePolicy:
    """02와 같은 절차. 규칙 목록의 타입만 Protocol로 바뀌었다."""

    rates: dict[str, int]
    adjustments: list[Adjustment] = field(default_factory=list)

    def late_fee(self, loan: Loan) -> int:
        """연체료를 계산한다."""
        days = (loan.returned - loan.due).days
        if days <= 0:
            return 0
        fee = days * self.rates[loan.material]
        for rule in self.adjustments:
            fee = rule(loan, fee)  # 함수든 객체든 똑같이 '호출'한다 — 덕 타이핑
        return fee


# 모듈 수준 상수: 파이썬에서 '지점 정책 표'는 클래스가 아니라 모듈에 둔 값이면 충분하다.
# 모듈은 한 번만 import되므로 이 표는 프로세스에서 하나다(4장 싱글턴의 논점으로 이어진다).
EXAM = ExamWaiver(date(2026, 6, 8), date(2026, 6, 21))
BRANCH_POLICIES: dict[str, FeePolicy] = {
    "새솔": FeePolicy({"book": 100, "dvd": 500}, [child_discount, EXAM]),
    "하늘": FeePolicy({"book": 100, "dvd": 700}, [child_discount, cap(3000)]),
    "바다": FeePolicy({"book": 100, "dvd": 500}, [EXAM]),
}


if __name__ == "__main__":
    due, back = date(2026, 6, 10), date(2026, 6, 15)
    print("[1] 함수·클로저·__call__ 객체가 한 목록 안에서 똑같이 쓰인다")
    for branch, policy in BRANCH_POLICIES.items():
        kinds = [type(r).__name__ for r in policy.adjustments]
        fee = policy.late_fee(Loan("dvd", "child", due, back))
        print(f"  {branch}: 규칙 종류 {kinds} → 아동 DVD 5일 연체 {fee}원")

    print("\n[2] 클래스로 둔 규칙만 자기 자신을 설명할 수 있다")
    print(f"  EXAM → {EXAM!r}")
    print(f"  EXAM.describe() → {EXAM.describe()}")
    # repr에는 메모리 주소가 섞여 실행마다 달라지므로 이름만 보인다. 어느 쪽이든 3000은 보이지 않는다.
    # (cap(3000).__closure__[0].cell_contents로 꺼낼 수는 있지만, 그것은 공개 인터페이스가 아니다.)
    print(f"  cap(3000) → <function {cap(3000).__qualname__}>  (설정값 3000이 공개 인터페이스로 드러나지 않는다)")

    print("\n[3] 테스트 대역도 상속 없이 람다 한 줄 — Protocol이라 가능하다")
    always_100 = FeePolicy({"book": 100}, [lambda loan, fee: 100])
    print(f"  {always_100.late_fee(Loan('book', 'adult', due, back))}원")
