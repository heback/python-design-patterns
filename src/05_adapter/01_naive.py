"""05 어댑터 — 순진한 설계: 주문 서비스가 세 PG사 SDK를 직접 부른다.

상황: 중소 쇼핑몰의 백엔드 개발자 예린은 PG사 A의 SDK로 결제를 붙였다. 이후
수수료 협상으로 PG사 B가, 해외 고객 때문에 간편결제 C가 추가되었다. 세 SDK는
메서드 이름, 금액 단위(원/Decimal/센트), 실패 보고 방식(예외/상태 코드/콜백)이
전부 다르다. 이 파일은 그 차이를 OrderService 안에서 if/elif로 직접 흡수한 첫 구현이다.
읽을 때는 pay()와 refund()에 같은 번역 로직이 어떻게 복제되는지, 그리고 그 복제가
실제로 어떤 버그를 낳는지(데모 [3])에 주목하라.
"""
from __future__ import annotations

import itertools
from dataclasses import dataclass
from decimal import Decimal
from typing import Callable

# ---------------------------------------------------------------------------
# 외부 SDK 흉내 — 실제로는 pip로 설치한 남의 코드다. 우리는 이 부분을 "수정할 수 없다".
# 세 SDK의 차이가 이 장의 핵심 재료이므로 일부러 서로 다르게 만들었다.
# ---------------------------------------------------------------------------

_ids = itertools.count(1001)  # 거래번호 생성용. SDK 내부 사정이라 의미는 없다.


class PgAError(Exception):
    """PG사 A SDK의 예외. A는 실패를 '예외'로 알린다."""


class PgAClient:
    """PG사 A SDK. 금액은 원 단위 int, 결과는 dict, 실패는 PgAError."""

    def charge(self, amount_krw: int, card_token: str) -> dict:
        """결제 승인. 성공 시 {'tid': ...}를 담은 dict를 돌려준다."""
        if card_token == "tok_declined":
            raise PgAError("A-401 한도 초과")
        return {"tid": f"A{next(_ids)}", "approved": amount_krw}

    def cancel(self, tid: str, amount_krw: int) -> dict:
        """승인 취소(환불)."""
        return {"tid": tid, "canceled": amount_krw}


@dataclass
class PaymentRequest:
    """PG사 B SDK의 요청 객체. 금액이 Decimal이라는 점이 A와 다르다."""

    amount: Decimal
    currency: str
    token: str


@dataclass
class PaymentResponse:
    """PG사 B SDK의 응답. 실패해도 예외를 던지지 않고 status_code로 알린다."""

    status_code: int          # 0 = 성공, 그 외는 실패 코드
    payment_id: str | None
    message: str = ""


class PgBClient:
    """PG사 B SDK. 요청 객체를 받고, 실패를 상태 코드로 돌려준다."""

    def create_payment(self, req: PaymentRequest) -> PaymentResponse:
        """결제 생성. 실패해도 예외가 아니라 status_code != 0인 응답을 준다."""
        if req.token == "tok_declined":
            return PaymentResponse(status_code=51, payment_id=None, message="잔액 부족")
        return PaymentResponse(status_code=0, payment_id=f"B{next(_ids)}")

    def refund_payment(self, payment_id: str, amount: Decimal) -> PaymentResponse:
        """환불. 역시 상태 코드로 결과를 알린다."""
        return PaymentResponse(status_code=0, payment_id=payment_id, message=f"refunded {amount}")


class PgCClient:
    """해외 간편결제 C SDK. 금액은 '소수 둘째 자리 단위'(원화 15,000원 → 1500000),
    결과는 반환값이 아니라 콜백으로 전달된다.

    단순화를 위해 이 흉내 코드는 콜백을 '즉시, 같은 스레드에서' 호출한다.
    실제 SDK는 다른 스레드에서 나중에 콜백한다(02_adapter.py는 그렇게 흉내 낸다).
    """

    def submit(self, amount_minor: int, currency: str, token: str,
               on_complete: Callable[[bool, str], None]) -> None:
        """결제 제출. 결과는 on_complete(ok, charge_id_or_reason)로 통지된다."""
        if token == "tok_declined":
            on_complete(False, "card_declined")
        else:
            on_complete(True, f"C{next(_ids)}")

    def reverse(self, charge_id: str, amount_minor: int,
                on_complete: Callable[[bool, str], None]) -> None:
        """환불. 금액 단위는 submit과 같은 minor unit이다."""
        print(f"    (C SDK) {charge_id}에 대해 {amount_minor} minor unit 환불 처리")
        on_complete(True, charge_id)


# ---------------------------------------------------------------------------
# 우리 코드 — 주문 서비스가 SDK 셋을 직접 안다.
# ---------------------------------------------------------------------------

class OrderService:
    """주문 결제/환불 서비스. PG별 차이를 스스로 흡수한다(이것이 문제다)."""

    def __init__(self) -> None:
        """세 SDK 클라이언트를 직접 생성한다."""
        # ⚠ 문제: 구체 SDK 셋을 직접 생성·보유한다. PG가 하나 늘 때마다 이 클래스가 바뀐다(OCP 위반).
        self.pg_a = PgAClient()
        self.pg_b = PgBClient()
        self.pg_c = PgCClient()

    def pay(self, pg: str, amount_krw: int, card_token: str) -> str:
        """결제하고 거래번호를 돌려준다. 실패하면 RuntimeError."""
        # ⚠ 문제: PG 이름 문자열로 분기한다. 이 분기는 refund()에도, 아마 정산 코드에도 복제된다.
        if pg == "A":
            try:
                return self.pg_a.charge(amount_krw, card_token)["tid"]
            except PgAError as e:
                raise RuntimeError(f"결제 실패: {e}")
        elif pg == "B":
            # ⚠ 문제: 단위 변환(int → Decimal)과 오류 해석(status_code)이 비즈니스 로직 한가운데 있다.
            res = self.pg_b.create_payment(PaymentRequest(Decimal(amount_krw), "KRW", card_token))
            if res.status_code != 0:
                raise RuntimeError(f"결제 실패: B-{res.status_code} {res.message}")
            assert res.payment_id is not None
            return res.payment_id
        elif pg == "C":
            # ⚠ 문제: 콜백을 동기 반환값으로 바꾸는 요령까지 주문 서비스가 알아야 한다.
            # ⚠ 문제: 게다가 이 box 트릭은 콜백이 '즉시' 오는 이 흉내 SDK에서만 동작한다.
            # 실제처럼 다른 스레드에서 나중에 콜백하면 box["ok"]를 읽는 시점에 KeyError가 난다.
            box: dict[str, object] = {}
            self.pg_c.submit(amount_krw * 100, "KRW", card_token,
                             lambda ok, v: box.update(ok=ok, value=v))
            if not box["ok"]:
                raise RuntimeError(f"결제 실패: C {box['value']}")
            return str(box["value"])
        raise ValueError(f"알 수 없는 PG: {pg}")

    def refund(self, pg: str, transaction_id: str, amount_krw: int) -> None:
        """환불. pay()와 같은 분기 구조를 다시 쓴다."""
        if pg == "A":
            self.pg_a.cancel(transaction_id, amount_krw)
        elif pg == "B":
            res = self.pg_b.refund_payment(transaction_id, Decimal(amount_krw))
            if res.status_code != 0:
                raise RuntimeError(f"환불 실패: B-{res.status_code}")
        elif pg == "C":
            # ⚠ 문제: 복제된 분기에서 C의 ×100 단위 변환을 빠뜨렸다. 15,000원이 150원으로 환불된다.
            # 번역 규칙이 한 곳에 모여 있지 않으면 이런 실수는 리뷰에서도 잘 안 보인다.
            self.pg_c.reverse(transaction_id, amount_krw, lambda ok, v: None)
        else:
            raise ValueError(f"알 수 없는 PG: {pg}")


if __name__ == "__main__":
    svc = OrderService()

    print("[1] 세 PG로 각각 15,000원 결제")
    tids = {pg: svc.pay(pg, 15_000, "tok_ok") for pg in ("A", "B", "C")}
    for pg, tid in tids.items():
        print(f"    PG {pg} → 거래번호 {tid}")

    print("[2] 한도 초과 카드 — 실패 메시지 형식이 PG마다 제각각이다")
    for pg in ("A", "B", "C"):
        try:
            svc.pay(pg, 15_000, "tok_declined")
        except RuntimeError as e:
            print(f"    PG {pg}: {e}")

    print("[3] PG C 거래 환불 — 15,000원을 환불해야 한다")
    svc.refund("C", tids["C"], 15_000)
    print("    → 1500000이어야 할 금액이 15000 minor unit(=150원)으로 나갔다. 복제된 분기의 버그다.")
