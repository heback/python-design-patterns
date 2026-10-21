"""05 어댑터 — 패턴 적용: PaymentGateway 포트와 PG별 객체 어댑터.

상황: 예린은 주문 서비스에서 PG별 분기를 걷어내기로 한다. 먼저 "우리 쪽이 원하는
결제 인터페이스"(Target)를 PaymentGateway로 정의한다. 이 인터페이스는 우리 언어로
말한다 — 금액은 원 단위 int, 실패는 우리 예외 PaymentDeclined, 결과는 즉시 반환.
그다음 SDK마다 어댑터를 하나씩 만들어, 이름·단위·오류 체계·콜백을 Target의 언어로
번역한다. OrderService는 이제 PaymentGateway 하나만 안다(DIP).

외부 SDK 흉내 코드는 01_naive.py와 같되, C SDK만 실제처럼 '다른 스레드에서' 콜백하도록
바꿨다(01은 단순화를 위해 즉시 콜백했다). 파일 하나만 열어도 전체가 보이도록 다시 실었다.
"""
from __future__ import annotations

import itertools
import threading
from abc import ABC, abstractmethod
from concurrent.futures import Future
from concurrent.futures import TimeoutError as FutureTimeout  # 3.11 미만에선 내장 TimeoutError와 다른 클래스
from dataclasses import dataclass
from decimal import Decimal
from typing import Callable

# ===========================================================================
# 외부 SDK (Adaptee) — 수정 불가. 01_naive.py와 동일하되 C는 실제처럼 다른 스레드에서 콜백한다.
# ===========================================================================

_ids = itertools.count(1001)


class PgAError(Exception):
    """[Adaptee 측 예외] PG사 A SDK의 예외."""


class PgAClient:
    """[Adaptee] PG사 A SDK. 원 단위 int, dict 결과, 실패는 PgAError."""

    def charge(self, amount_krw: int, card_token: str) -> dict:
        """결제 승인."""
        if card_token == "tok_declined":
            raise PgAError("A-401 한도 초과")
        return {"tid": f"A{next(_ids)}", "approved": amount_krw}

    def cancel(self, tid: str, amount_krw: int) -> dict:
        """승인 취소(환불)."""
        return {"tid": tid, "canceled": amount_krw}


@dataclass
class PaymentRequest:
    """PG사 B SDK의 요청 객체."""

    amount: Decimal
    currency: str
    token: str


@dataclass
class PaymentResponse:
    """PG사 B SDK의 응답. 실패도 status_code로 온다."""

    status_code: int
    payment_id: str | None
    message: str = ""


class PgBClient:
    """[Adaptee] PG사 B SDK. 요청 객체 + 상태 코드 방식."""

    def create_payment(self, req: PaymentRequest) -> PaymentResponse:
        """결제 생성."""
        if req.token == "tok_declined":
            return PaymentResponse(status_code=51, payment_id=None, message="잔액 부족")
        return PaymentResponse(status_code=0, payment_id=f"B{next(_ids)}")

    def refund_payment(self, payment_id: str, amount: Decimal) -> PaymentResponse:
        """환불."""
        return PaymentResponse(status_code=0, payment_id=payment_id, message=f"refunded {amount}")


class PgCClient:
    """[Adaptee] 해외 간편결제 C SDK. minor unit 금액, 결과는 '다른 스레드에서' 콜백."""

    def submit(self, amount_minor: int, currency: str, token: str,
               on_complete: Callable[[bool, str], None]) -> None:
        """결제 제출. 즉시 반환하고, 결과는 잠시 뒤 별도 스레드에서 콜백으로 온다."""
        ok, value = (False, "card_declined") if token == "tok_declined" else (True, f"C{next(_ids)}")
        threading.Timer(0.01, on_complete, args=(ok, value)).start()

    def reverse(self, charge_id: str, amount_minor: int,
                on_complete: Callable[[bool, str], None]) -> None:
        """환불. 역시 비동기 콜백."""
        print(f"    (C SDK) {charge_id}에 대해 {amount_minor} minor unit 환불 처리")
        threading.Timer(0.01, on_complete, args=(True, charge_id)).start()


# ===========================================================================
# 우리 쪽 포트 (Target) — "우리가 결제에 대해 말하는 방식"을 정의한다.
# ===========================================================================

@dataclass(frozen=True)
class PaymentResult:
    """결제 결과 값 객체. frozen인 이유: 결과는 기록이지 바꿔 쓸 대상이 아니다."""

    transaction_id: str
    amount_krw: int
    gateway: str


class PaymentDeclined(Exception):
    """우리 도메인의 결제 거절 예외. 어떤 PG든 거절은 이 하나로 보인다.

    호출자는 PgAError나 status_code 51 같은 '남의 어휘'를 몰라도 된다.
    원래 원인은 raise ... from 으로 __cause__에 보존하므로 디버깅 정보는 잃지 않는다.
    """


class PaymentGateway(ABC):
    """[Target] 주문 서비스가 기대하는 결제 인터페이스.

    이 인터페이스의 주인은 SDK가 아니라 '우리'다(헥사고날 아키텍처의 포트).
    그래서 시그니처를 SDK에 맞추지 않고 도메인에 맞춘다: 원 단위 int, 동기 반환, 우리 예외.
    ABC를 쓴 이유: 어댑터가 refund()를 빠뜨리면 인스턴스화 시점에 TypeError로 바로 드러난다.
    """

    name: str = "?"

    @abstractmethod
    def pay(self, amount_krw: int, card_token: str) -> PaymentResult:
        """결제한다. 거절되면 PaymentDeclined를 던진다."""

    @abstractmethod
    def refund(self, transaction_id: str, amount_krw: int) -> None:
        """환불한다. 실패하면 PaymentDeclined를 던진다."""


# ===========================================================================
# 어댑터 (Adapter) — 번역 규칙은 PG마다 여기 한 곳에만 있다(SRP).
# ===========================================================================

class PgAAdapter(PaymentGateway):
    """[Adapter] PG사 A → PaymentGateway. 번역할 것: dict 결과, PgAError.

    객체 어댑터(합성)다. PgAClient를 상속하지 않고 필드로 갖는 이유:
    SDK의 charge()/cancel()이 우리 인터페이스에 새어 나오지 않게 하기 위해서다.
    """

    name = "A"

    def __init__(self, client: PgAClient) -> None:
        """SDK 클라이언트를 주입받는다. 테스트에서는 가짜 클라이언트를 넣을 수 있다."""
        self._client = client

    def pay(self, amount_krw: int, card_token: str) -> PaymentResult:
        """A는 단위가 같으므로 결과 형태와 예외만 번역한다."""
        try:
            raw = self._client.charge(amount_krw, card_token)
        except PgAError as e:
            # 예외 변환: 남의 예외를 우리 예외로. from e 로 원인 체인을 남긴다.
            raise PaymentDeclined(f"[A] {e}") from e
        return PaymentResult(raw["tid"], amount_krw, self.name)

    def refund(self, transaction_id: str, amount_krw: int) -> None:
        """이름(cancel → refund)만 번역하면 되는 가장 얇은 경우."""
        try:
            self._client.cancel(transaction_id, amount_krw)
        except PgAError as e:
            raise PaymentDeclined(f"[A] 환불 실패: {e}") from e


class PgBAdapter(PaymentGateway):
    """[Adapter] PG사 B → PaymentGateway. 번역할 것: int↔Decimal, 상태 코드 → 예외."""

    name = "B"

    def __init__(self, client: PgBClient) -> None:
        """SDK 클라이언트를 주입받는다."""
        self._client = client

    @staticmethod
    def _check(res: PaymentResponse, action: str) -> str:
        """상태 코드 방식의 실패를 예외 방식으로 바꾼다.

        pay/refund 둘 다 쓰므로 한 메서드로 뺐다. 01_naive.py에서는 이 규칙이
        두 곳에 복제되어 있었다는 점을 떠올려 보라.
        """
        if res.status_code != 0 or res.payment_id is None:
            raise PaymentDeclined(f"[B] {action} 실패: 코드 {res.status_code} {res.message}")
        return res.payment_id

    def pay(self, amount_krw: int, card_token: str) -> PaymentResult:
        """원 단위 int를 B가 원하는 Decimal 요청 객체로 감싼다."""
        res = self._client.create_payment(PaymentRequest(Decimal(amount_krw), "KRW", card_token))
        return PaymentResult(self._check(res, "결제"), amount_krw, self.name)

    def refund(self, transaction_id: str, amount_krw: int) -> None:
        """환불도 같은 단위·오류 번역 규칙을 거친다."""
        self._check(self._client.refund_payment(transaction_id, Decimal(amount_krw)), "환불")


class PgCAdapter(PaymentGateway):
    """[Adapter] 간편결제 C → PaymentGateway. 번역할 것: 원↔minor unit, 비동기 콜백 → 동기 반환.

    어댑터가 숨길 수 있는 차이는 이름만이 아니다. '호출 모델'(콜백 vs 반환값)도
    번역 대상이다. 단, 동기화하면 그만큼 호출자가 기다린다는 비용이 있으므로
    timeout을 반드시 둔다.
    """

    name = "C"
    MINOR_PER_KRW = 100   # 단위 변환 규칙을 상수 하나로. 01_naive.py의 환불 버그가 여기서 사라진다.
    TIMEOUT_SEC = 5.0

    def __init__(self, client: PgCClient) -> None:
        """SDK 클라이언트를 주입받는다."""
        self._client = client

    def _await(self, start: Callable[[Callable[[bool, str], None]], None]) -> str:
        """콜백 API를 Future로 감싸 결과를 기다린다.

        Future를 쓰는 이유: 콜백이 같은 스레드에서 즉시 오든 다른 스레드에서 나중에 오든
        똑같이 동작하고, 스레드 간 결과 전달의 동기화를 직접 구현할 필요가 없다.
        """
        fut: Future[tuple[bool, str]] = Future()
        start(lambda ok, value: fut.set_result((ok, value)))
        try:
            ok, value = fut.result(timeout=self.TIMEOUT_SEC)
        except FutureTimeout as e:
            # 시간 초과도 '남의 사정'이다. 번역하지 않으면 호출자가 concurrent.futures를 알아야 한다.
            raise PaymentDeclined("[C] 응답 시간 초과") from e
        if not ok:
            raise PaymentDeclined(f"[C] {value}")
        return value

    def pay(self, amount_krw: int, card_token: str) -> PaymentResult:
        """원 → minor unit 변환 후 콜백 결과를 동기 반환값으로 바꾼다."""
        minor = amount_krw * self.MINOR_PER_KRW
        charge_id = self._await(lambda cb: self._client.submit(minor, "KRW", card_token, cb))
        return PaymentResult(charge_id, amount_krw, self.name)

    def refund(self, transaction_id: str, amount_krw: int) -> None:
        """pay()와 같은 변환 규칙을 공유하므로 단위 실수가 끼어들 틈이 없다."""
        minor = amount_krw * self.MINOR_PER_KRW
        self._await(lambda cb: self._client.reverse(transaction_id, minor, cb))


# ===========================================================================
# 클라이언트 (Client) — PG가 몇 개든 이 코드는 바뀌지 않는다.
# ===========================================================================

class OrderService:
    """[Client] 주문 결제/환불. PaymentGateway 추상에만 의존한다(DIP)."""

    def __init__(self, gateway: PaymentGateway) -> None:
        """어떤 PG를 쓸지는 바깥(설정/조립 코드)이 정한다. 서비스는 묻지 않는다."""
        self._gateway = gateway

    def checkout(self, order_id: str, amount_krw: int, card_token: str) -> PaymentResult | None:
        """결제를 시도하고, 거절이면 None. PG별 예외를 하나도 몰라도 된다."""
        try:
            result = self._gateway.pay(amount_krw, card_token)
        except PaymentDeclined as e:
            # __cause__는 raise ... from 으로 남긴 원래 예외. B·C는 애초에 예외가 없었으므로 None이다.
            cause = type(e.__cause__).__name__ if e.__cause__ else "없음"
            print(f"    주문 {order_id} 결제 거절: {e}  (SDK 원인 예외: {cause})")
            return None
        print(f"    주문 {order_id} 결제 완료: {result}")
        return result

    def cancel(self, result: PaymentResult) -> None:
        """환불. 분기도 단위 변환도 없다 — 그건 어댑터의 일이다."""
        self._gateway.refund(result.transaction_id, result.amount_krw)
        print(f"    {result.gateway} 거래 {result.transaction_id} 환불 완료")


if __name__ == "__main__":
    # 조립 지점(composition root): 구체 SDK와 어댑터를 아는 유일한 곳.
    gateways: list[PaymentGateway] = [
        PgAAdapter(PgAClient()), PgBAdapter(PgBClient()), PgCAdapter(PgCClient()),
    ]

    print("[1] 같은 OrderService 코드로 세 PG 결제 → 환불")
    for gw in gateways:
        svc = OrderService(gw)
        paid = svc.checkout(f"ORD-{gw.name}", 15_000, "tok_ok")
        if paid:
            svc.cancel(paid)

    print("[2] 거절 카드 — 세 PG의 서로 다른 실패 방식이 PaymentDeclined 하나로 보인다")
    for gw in gateways:
        OrderService(gw).checkout(f"ORD-{gw.name}-X", 15_000, "tok_declined")
