"""연습문제 2 해설: 분실 배상금 if/elif 함수를 '변하는 것/변하지 않는 것'으로 나눠 ABC판과 함수판으로.

상황: 새솔도서관은 연체료에 이어 분실 배상금 규칙도 if/elif 한 함수로 관리했다(문제 본문 코드).
기증 자료는 정가 대신 고정 5,000원, 절판 자료는 정가의 1.5배, 아동 회원은 50% 감면, 그리고
배상금은 최소 1,000원이다. 본문 02/03과 같은 순서로 리팩터링한다.

변하지 않는 것: "기준 금액을 정한다 → 조정 규칙을 차례로 적용한다"는 절차.
변하는 것   : (a) 기준 금액을 정하는 방식(정가/고정액/배수), (b) 조정 규칙의 목록과 순서.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class LostItem:
    """분실 자료 한 건."""

    price: int
    donated: bool
    out_of_print: bool
    member: str


# ---------------------------------------------------------------------------
# 버전 A: ABC 기반 — 규칙이 '이름 있는 타입'이 된다
# ---------------------------------------------------------------------------

class Rule(ABC):
    """조정 규칙의 명목적 계약."""

    @abstractmethod
    def apply(self, item: LostItem, amount: int) -> int:
        """조정된 금액."""


class DonatedFlat(Rule):
    """기증 자료는 정가와 무관하게 5,000원. 기준 금액을 '덮어쓰는' 규칙이라 맨 앞에 둬야 한다."""

    def apply(self, item: LostItem, amount: int) -> int:
        """기증이면 고정액."""
        return 5000 if item.donated else amount


class OutOfPrintSurcharge(Rule):
    """절판 자료는 재구매가 어려워 1.5배. 단, 기증 자료(고정액)에는 붙지 않는다.

    원래 코드의 `out_of_print and not donated`를 그대로 옮겼다. 규칙을 목록 순서에만 맡기면
    기증+절판 자료가 5,000 → 7,500원이 되어 동작이 바뀐다. 리팩터링은 동작을 보존해야 하므로
    이 결합 조건은 규칙 안에 남긴다(정책을 바꾸고 싶다면 그것은 별도의 결정이다).
    """

    def apply(self, item: LostItem, amount: int) -> int:
        """정수 연산으로 1.5배(× 3 // 2)."""
        return amount * 3 // 2 if item.out_of_print and not item.donated else amount


class ChildHalf(Rule):
    """아동 50% 감면."""

    def apply(self, item: LostItem, amount: int) -> int:
        """아동이면 절반."""
        return amount // 2 if item.member == "child" else amount


@dataclass(frozen=True)
class MinimumFee(Rule):
    """최소 배상금. 감면 '뒤에' 와야 의미가 있다 — 순서가 리스트에 드러난다."""

    floor: int

    def apply(self, item: LostItem, amount: int) -> int:
        """하한을 보장한다."""
        return max(amount, self.floor)


def compensation_abc(item: LostItem, rules: list[Rule]) -> int:
    """변하지 않는 절차(ABC판)."""
    amount = item.price
    for rule in rules:
        amount = rule.apply(item, amount)
    return amount


# ---------------------------------------------------------------------------
# 버전 B: 함수 기반 — 상태 없는 규칙은 함수, 설정 있는 규칙은 클로저
# ---------------------------------------------------------------------------

RuleFn = Callable[[LostItem, int], int]


def donated_flat(item: LostItem, amount: int) -> int:
    """기증 자료 고정액."""
    return 5000 if item.donated else amount


def out_of_print(item: LostItem, amount: int) -> int:
    """절판 1.5배(기증 자료 제외 — ABC판과 같은 이유)."""
    return amount * 3 // 2 if item.out_of_print and not item.donated else amount


def child_half(item: LostItem, amount: int) -> int:
    """아동 감면."""
    return amount // 2 if item.member == "child" else amount


def minimum(floor: int) -> RuleFn:
    """하한 규칙을 만드는 함수. floor를 캡처한다."""
    return lambda item, amount: max(amount, floor)


def compensation_fn(item: LostItem, rules: list[RuleFn]) -> int:
    """변하지 않는 절차(함수판). ABC판과 한 줄만 다르다: rule.apply(...) → rule(...)."""
    amount = item.price
    for rule in rules:
        amount = rule(item, amount)
    return amount


if __name__ == "__main__":
    cases = [
        LostItem(18000, donated=False, out_of_print=False, member="adult"),
        LostItem(18000, donated=True, out_of_print=False, member="adult"),
        LostItem(18000, donated=False, out_of_print=True, member="adult"),
        LostItem(1500, donated=False, out_of_print=False, member="child"),
        LostItem(18000, donated=True, out_of_print=True, member="adult"),  # 원래 코드에서 5,000원
    ]
    abc_rules: list[Rule] = [DonatedFlat(), OutOfPrintSurcharge(), ChildHalf(), MinimumFee(1000)]
    fn_rules: list[RuleFn] = [donated_flat, out_of_print, child_half, minimum(1000)]
    print("[1] 두 버전은 같은 결과를 낸다")
    for item in cases:
        a, b = compensation_abc(item, abc_rules), compensation_fn(item, fn_rules)
        print(f"  정가 {item.price:>6} 기증={item.donated!s:5} 절판={item.out_of_print!s:5} "
              f"{item.member:5} → ABC {a:>6} / 함수 {b:>6}")
    print("\n[2] 순서를 바꾸면 결과가 바뀐다: 하한 → 감면 순서로 두면 아동 1,500원 자료가")
    wrong = [donated_flat, out_of_print, minimum(1000), child_half]
    # 하한을 감면 '앞'에 두면 1,500원(하한 통과) → 감면 750원. 원래 코드는 감면 뒤에 하한을 둔다.
    print(f"  {compensation_fn(cases[3], wrong)}원 — 하한(1,000원)이 무력화된다")
