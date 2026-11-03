"""05 어댑터 — 순진한 코드: 주문 서비스가 PG SDK 둘을 직접 부른다.

상황: 솔숲상회의 주문 서비스는 PG사 B(Decimal 금액, 실패는 status_code)와
간편결제 C(금액은 minor unit, 결과는 콜백)를 직접 부른다. SDK마다 다른 점을
주문 서비스가 if 분기로 직접 번역하다가, 환불 쪽 분기에서 C의 ×100을 빠뜨린다.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Callable


# --- 외부 SDK 흉내 (우리가 고칠 수 없는 남의 코드) ---
@dataclass
class PaymentResponse:
    """B SDK의 응답. 실패해도 예외 대신 status_code가 0이 아니다."""
    status_code: int
    payment_id: str | None


class PgBClient:
    """PG사 B SDK. 금액을 Decimal로 받는다."""

    def create_payment(self, amount: Decimal, currency: str, token: str) -> PaymentResponse:
        """결제 생성. 거절 카드면 상태 코드 51."""
        return PaymentResponse(51, None) if token == "tok_declined" else PaymentResponse(0, "B-1")

    def refund_payment(self, payment_id: str, amount: Decimal) -> PaymentResponse:
        """환불."""
        return PaymentResponse(0, payment_id)


class PgCClient:
    """간편결제 C SDK. 금액은 minor unit(원 × 100), 결과는 콜백으로 알린다."""

    def submit(self, amount_minor: int, token: str, on_done: Callable[[bool, str], None]) -> None:
        """결제 제출. 결과를 반환하지 않고 on_done(성공 여부, 값)을 부른다."""
        on_done(token != "tok_declined", "C-1" if token != "tok_declined" else "card_declined")

    def reverse(self, charge_id: str, amount_minor: int, on_done: Callable[[bool, str], None]) -> None:
        """환불. 금액 단위는 submit과 같은 minor unit이다."""
        print(f"    (C SDK) {charge_id} 환불 금액 {amount_minor} minor unit")
        on_done(True, charge_id)


# --- 우리 코드 ---
class OrderService:
    """주문 결제·환불. PG마다 다른 점을 스스로 번역한다(이것이 문제다)."""

    def __init__(self) -> None:
        """SDK 둘을 직접 만든다."""
        # ⚠ 문제: PG가 늘 때마다 이 클래스를 고쳐야 한다.
        self.pg_b, self.pg_c = PgBClient(), PgCClient()

    def pay(self, pg: str, amount_krw: int, token: str) -> str:
        """결제하고 거래번호를 돌려준다."""
        # ⚠ 문제: PG 이름으로 분기하고, 단위 변환·오류 해석이 주문 로직 안에 섞여 있다.
        if pg == "B":
            res = self.pg_b.create_payment(Decimal(amount_krw), "KRW", token)
            if res.status_code != 0:
                raise RuntimeError(f"B 실패: 코드 {res.status_code}")
            return str(res.payment_id)
        box: dict = {}   # 콜백 결과를 받아 둘 상자
        self.pg_c.submit(amount_krw * 100, token, lambda ok, v: box.update(ok=ok, v=v))
        if not box["ok"]:
            raise RuntimeError(f"C 실패: {box['v']}")
        return box["v"]

    def refund(self, pg: str, transaction_id: str, amount_krw: int) -> None:
        """환불. pay()와 같은 분기를 한 번 더 쓴다."""
        if pg == "B":
            self.pg_b.refund_payment(transaction_id, Decimal(amount_krw))
        else:
            # ⚠ 문제: 복제한 분기에서 ×100을 빠뜨렸다. 15,000원이 150원으로 환불된다.
            self.pg_c.reverse(transaction_id, amount_krw, lambda ok, v: None)


if __name__ == "__main__":
    svc = OrderService()
    print("[1] 두 PG로 15,000원 결제")
    print(f"    B → {svc.pay('B', 15_000, 'tok_ok')}, C → {svc.pay('C', 15_000, 'tok_ok')}")
    print("[2] 거절 카드 — 실패를 알리는 방식이 PG마다 다르다")
    for pg in ("B", "C"):
        try:
            svc.pay(pg, 15_000, "tok_declined")
        except RuntimeError as e:
            print(f"    {e}")
    print("[3] C 거래 환불 — 1500000이 나가야 한다")
    svc.refund("C", "C-1", 15_000)
