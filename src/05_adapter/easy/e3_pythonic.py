"""05 어댑터 — 파이썬다운 변형: Protocol Target, 함수 어댑터, __getattr__ 위임의 함정.

상황: 팀 리드 도윤이 묻는다. (1) 어댑터가 꼭 Target을 상속해야 하나?
(2) 정산 배치는 "금액·토큰을 받아 거래번호를 돌려주는 함수" 하나만 원하는데 그것도 클래스로?
(3) SDK 메서드가 스무 개면 __getattr__ 한 줄로 넘기면 되지 않나? 이 코드가 차례로 답한다.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Callable, Protocol


@dataclass
class PaymentResponse:
    """B SDK의 응답(줄인 흉내)."""
    status_code: int
    payment_id: str | None


class PgBClient:
    """[Adaptee] B SDK(줄인 흉내). Target에 없는 부가 기능도 있다."""

    def create_payment(self, amount: Decimal, currency: str, token: str) -> PaymentResponse:
        """결제 생성(상태 코드 방식)."""
        return PaymentResponse(51, None) if token == "tok_declined" else PaymentResponse(0, "B-77")

    def get_receipt_url(self, payment_id: str) -> str:
        """영수증 주소 조회 — SDK 고유 기능."""
        return f"https://pg-b.example/r/{payment_id}"


class PaymentDeclined(Exception):
    """우리 도메인의 결제 거절."""


# (1) Protocol: 상속 없이 '모양'만 맞으면 Target이다.
class PaymentGateway(Protocol):
    """[Target] pay()만 있으면 된다. 대가: 빠뜨린 메서드는 정적 검사기를 돌려야 잡힌다."""

    def pay(self, amount_krw: int, card_token: str) -> str:
        """결제하고 거래번호를 돌려준다."""
        ...


class PgBAdapter:
    """[Adapter] PaymentGateway를 상속하지 않는다. 부가 기능은 골라서 우리 이름으로 연다."""

    def __init__(self, client: PgBClient) -> None:
        """SDK를 필드로 갖는다(객체 어댑터)."""
        self._client = client

    def pay(self, amount_krw: int, card_token: str) -> str:
        """int → Decimal, 상태 코드 → 예외."""
        res = self._client.create_payment(Decimal(amount_krw), "KRW", card_token)
        if res.status_code != 0 or res.payment_id is None:
            raise PaymentDeclined(f"B 거절(코드 {res.status_code})")
        return res.payment_id

    def receipt_url(self, transaction_id: str) -> str:
        """노출할 것을 이 클래스가 직접 정한다 — 무엇이 공개되는지 한눈에 보인다."""
        return self._client.get_receipt_url(transaction_id)


# (2) 메서드 하나짜리 Target이면 함수가 곧 어댑터다.
Charger = Callable[[int, str], str]   # 정산 배치가 원하는 모양: (금액, 토큰) -> 거래번호


def settle_batch(charge: Charger, items: list[tuple[int, str]]) -> list[str]:
    """[Client] 정산 배치. 클래스가 아니라 호출할 수 있는 것 하나만 받는다."""
    return [charge(amount, token) for amount, token in items]


def b_charger(client: PgBClient) -> Charger:
    """[Adapter] B SDK를 Charger 모양으로 바꾼 함수를 만든다(클로저가 client를 기억한다)."""
    def charge(amount_krw: int, card_token: str) -> str:
        """응답 객체에서 거래번호만 꺼낸다."""
        return str(client.create_payment(Decimal(amount_krw), "KRW", card_token).payment_id)
    return charge


# (3) __getattr__ 위임: 편하지만 경계에 구멍이 난다.
class LeakyPgBAdapter(PgBAdapter):
    """[나쁜 예] 어댑터에 없는 이름은 전부 SDK로 넘긴다."""

    def __getattr__(self, name: str) -> Any:
        """보통의 속성 찾기가 실패했을 때만 불린다."""
        return getattr(self._client, name)


def place_order(gateway: PaymentGateway) -> str:
    """[Client] PaymentGateway 모양이면 무엇이든 받는다."""
    return gateway.pay(9_900, "tok_ok")


if __name__ == "__main__":
    b = PgBAdapter(PgBClient())
    print(f"[1] 상속 없이 Target 자리에 들어간다: {place_order(b)}, 영수증 {b.receipt_url('B-77')}")
    print(f"[2] 함수 어댑터로 정산 배치: {settle_batch(b_charger(PgBClient()), [(1_000, 't1'), (2_500, 't2')])}")
    leaky = LeakyPgBAdapter(PgBClient())
    raw = leaky.create_payment(Decimal(1), "KRW", "tok_declined")   # 번역을 건너뛴 호출
    print(f"[3] 새어 나온 SDK 메서드: {raw} ← 호출자가 status_code를 다시 알아야 한다")
