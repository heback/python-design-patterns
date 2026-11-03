"""05 어댑터 — 패턴 코드: PaymentGateway(Target)와 PG별 객체 어댑터.

상황: 예린은 "우리가 결제를 말하는 방식"을 PaymentGateway로 먼저 정한다.
금액은 원 단위 int, 결과는 거래번호 str, 실패는 우리 예외 PaymentDeclined 하나.
SDK마다 어댑터를 하나씩 두고, 번역 규칙은 그 어댑터 안에만 둔다.
OrderService는 PaymentGateway만 안다. SDK 흉내는 순진한 코드와 같아 줄였다.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal
from typing import Callable


# --- 외부 SDK 흉내 (Adaptee, 수정 불가) — 순진한 코드와 같다 ---
@dataclass
class PaymentResponse:
    """B SDK의 응답. 실패는 status_code로 온다."""
    status_code: int
    payment_id: str | None


class PgBClient:
    """[Adaptee] PG사 B SDK."""

    def create_payment(self, amount: Decimal, currency: str, token: str) -> PaymentResponse:
        """결제 생성."""
        return PaymentResponse(51, None) if token == "tok_declined" else PaymentResponse(0, "B-1")

    def refund_payment(self, payment_id: str, amount: Decimal) -> PaymentResponse:
        """환불."""
        return PaymentResponse(0, payment_id)


class PgCClient:
    """[Adaptee] 간편결제 C SDK. minor unit 금액, 결과는 콜백."""

    def submit(self, amount_minor: int, token: str, on_done: Callable[[bool, str], None]) -> None:
        """결제 제출."""
        on_done(token != "tok_declined", "C-1" if token != "tok_declined" else "card_declined")

    def reverse(self, charge_id: str, amount_minor: int, on_done: Callable[[bool, str], None]) -> None:
        """환불."""
        print(f"    (C SDK) {charge_id} 환불 금액 {amount_minor} minor unit")
        on_done(True, charge_id)


# --- 우리 쪽 인터페이스 (Target) ---
class PaymentDeclined(Exception):
    """우리 도메인의 결제 거절. 어느 PG든 거절은 이 예외 하나로 보인다."""


class PaymentGateway(ABC):
    """[Target] 주문 서비스가 기대하는 결제 인터페이스.

    주인은 SDK가 아니라 우리다. 그래서 SDK가 아니라 주문 서비스에 맞춰 정한다.
    ABC인 이유: refund()를 빠뜨린 어댑터는 객체를 만들 때 바로 TypeError가 난다.
    """

    @abstractmethod
    def pay(self, amount_krw: int, card_token: str) -> str:
        """결제하고 거래번호를 돌려준다. 거절이면 PaymentDeclined."""

    @abstractmethod
    def refund(self, transaction_id: str, amount_krw: int) -> None:
        """환불한다."""


# --- 어댑터 (Adapter) — 번역 규칙은 PG마다 여기 한 곳에만 있다 ---
class PgBAdapter(PaymentGateway):
    """[Adapter] B → PaymentGateway. 번역: int → Decimal, 상태 코드 → 예외.

    객체 어댑터: PgBClient를 상속하지 않고 _client 필드로 갖는다.
    그래서 create_payment 같은 SDK 메서드가 우리 인터페이스로 새지 않는다.
    """

    def __init__(self, client: PgBClient) -> None:
        """감쌀 SDK 객체를 받는다(테스트에서는 가짜를 넣을 수 있다)."""
        self._client = client

    def _check(self, res: PaymentResponse) -> str:
        """상태 코드 방식의 실패를 예외로 바꾼다. pay·refund가 함께 쓴다."""
        if res.status_code != 0 or res.payment_id is None:
            raise PaymentDeclined(f"B 거절(코드 {res.status_code})")
        return res.payment_id

    def pay(self, amount_krw: int, card_token: str) -> str:
        """원 단위 int를 B가 원하는 Decimal로 바꿔 부른다."""
        return self._check(self._client.create_payment(Decimal(amount_krw), "KRW", card_token))

    def refund(self, transaction_id: str, amount_krw: int) -> None:
        """이름(refund → refund_payment)과 단위를 번역한다."""
        self._check(self._client.refund_payment(transaction_id, Decimal(amount_krw)))


class PgCAdapter(PaymentGateway):
    """[Adapter] C → PaymentGateway. 번역: 원 → minor unit, 콜백 → 반환값."""

    MINOR_PER_KRW = 100   # 단위 규칙은 이 상수 하나. 순진한 코드의 환불 버그가 설 자리가 없다.

    def __init__(self, client: PgCClient) -> None:
        """감쌀 SDK 객체를 받는다."""
        self._client = client

    def _wait(self, start: Callable[[Callable[[bool, str], None]], None]) -> str:
        """콜백으로 오는 결과를 받아 반환값으로 돌려준다. 실패면 우리 예외."""
        box: dict = {}
        start(lambda ok, v: box.update(ok=ok, v=v))
        if not box["ok"]:
            raise PaymentDeclined(f"C 거절({box['v']})")
        return box["v"]

    def pay(self, amount_krw: int, card_token: str) -> str:
        """pay와 refund가 같은 MINOR_PER_KRW를 쓴다."""
        minor = amount_krw * self.MINOR_PER_KRW
        return self._wait(lambda cb: self._client.submit(minor, card_token, cb))

    def refund(self, transaction_id: str, amount_krw: int) -> None:
        """환불도 같은 변환 규칙을 거친다."""
        minor = amount_krw * self.MINOR_PER_KRW
        self._wait(lambda cb: self._client.reverse(transaction_id, minor, cb))


# --- 클라이언트 (Client) — PG가 몇 개든 바뀌지 않는다 ---
class OrderService:
    """[Client] 주문 결제·환불. PaymentGateway에만 의존한다(DIP)."""

    def __init__(self, gateway: PaymentGateway) -> None:
        """어느 PG를 쓸지는 바깥이 정한다."""
        self._gateway = gateway

    def checkout(self, amount_krw: int, token: str) -> str | None:
        """결제하고 거래번호를, 거절이면 None을 돌려준다. SDK 어휘가 하나도 없다."""
        try:
            return self._gateway.pay(amount_krw, token)
        except PaymentDeclined as e:
            print(f"    거절: {e}")
            return None


if __name__ == "__main__":
    # 구체 SDK와 어댑터를 아는 곳은 이 조립 부분뿐이다.
    gateways = [PgBAdapter(PgBClient()), PgCAdapter(PgCClient())]
    print("[1] 같은 OrderService로 두 PG 결제 → 환불")
    for gw in gateways:
        tid = OrderService(gw).checkout(15_000, "tok_ok")
        print(f"    결제 {tid}")
        gw.refund(str(tid), 15_000)   # C는 이번에 1500000 minor unit이 나간다
    print("[2] 거절 카드 — 두 가지 실패 방식이 PaymentDeclined 하나로 보인다")
    for gw in gateways:
        OrderService(gw).checkout(15_000, "tok_declined")
