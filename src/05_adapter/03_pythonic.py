"""05 어댑터 — 파이썬다운 변형: Protocol target, 함수 어댑터, __getattr__ 위임의 함정.

상황: 02_adapter.py의 구조는 잘 돌아가지만, 예린의 팀 리드 도윤은 세 가지를 묻는다.
(1) 어댑터가 꼭 PaymentGateway를 상속해야 하나? 남이 만든 클래스도 그대로 끼울 수 없나?
(2) 정산 배치는 "금액과 토큰을 받아 거래번호를 돌려주는 함수" 하나만 필요한데, 그것도 클래스로?
(3) B SDK에는 영수증 조회 등 메서드가 스무 개다. 전부 손으로 위임해야 하나? __getattr__이면 한 줄인데?
이 파일은 세 질문에 차례로 답한다. 외부 SDK는 설명에 필요한 만큼만 축약해 실었다.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from functools import partial
from typing import Any, Callable, Protocol, runtime_checkable


# --- 축약한 외부 SDK (Adaptee) ---------------------------------------------

@dataclass
class PaymentResponse:
    """PG사 B 응답(축약)."""

    status_code: int
    payment_id: str | None


class PgBClient:
    """[Adaptee] PG사 B SDK(축약). 결제 외에 부가 메서드가 많다는 점만 흉내 낸다."""

    def create_payment(self, amount: Decimal, currency: str, token: str) -> PaymentResponse:
        """결제 생성(상태 코드 방식)."""
        if token == "tok_declined":
            return PaymentResponse(51, None)
        return PaymentResponse(0, "B-77")

    def refund_payment(self, payment_id: str, amount: Decimal) -> PaymentResponse:
        """환불(상태 코드 방식)."""
        return PaymentResponse(0, payment_id)

    def get_receipt_url(self, payment_id: str) -> str:
        """영수증 URL 조회 — Target에는 없는 SDK 고유 기능."""
        return f"https://pg-b.example/receipts/{payment_id}"


class PgAClient:
    """[Adaptee] PG사 A SDK(축약). 가맹점 ID를 매 호출마다 요구한다는 차이를 추가했다."""

    def charge(self, merchant_id: str, amount_krw: int, card_token: str) -> dict:
        """결제 승인. 첫 인자 merchant_id는 우리 도메인에는 없는 개념이다."""
        return {"tid": f"A-{merchant_id}-{amount_krw}"}


class PaymentDeclined(Exception):
    """우리 도메인의 결제 거절 예외."""


# --- (1) Protocol target: 상속 없이 '모양'으로 맞춘다 ----------------------

@runtime_checkable
class PaymentGateway(Protocol):
    """[Target] 구조적 타입(Protocol)으로 정의한 결제 포트.

    ABC와의 차이: 어댑터가 이 클래스를 상속하지 않아도 pay/refund만 맞으면 Target이다.
    덕분에 다른 팀이 만든 클래스, 테스트용 가짜 객체도 '등록' 없이 끼울 수 있다.
    대가: 구현 누락을 인스턴스화 시점이 아니라 정적 검사(mypy) 시점에야 잡는다.
    runtime_checkable의 isinstance()는 메서드 '이름' 존재만 보고 시그니처는 보지 않는다.
    """

    def pay(self, amount_krw: int, card_token: str) -> str:
        """결제하고 거래번호를 돌려준다."""
        ...

    def refund(self, transaction_id: str, amount_krw: int) -> None:
        """환불한다."""
        ...


class PgBAdapter:
    """[Adapter] PaymentGateway를 상속하지 않는다. 그래도 Protocol 관점에선 Target이다.

    SDK 고유 기능(영수증 URL)이 필요하면 '명시적으로' 노출한다 — 무엇이 공개되는지
    이 클래스만 읽으면 다 보인다. 아래 LeakyPgBAdapter와 비교하라.
    """

    def __init__(self, client: PgBClient) -> None:
        """SDK를 합성으로 보유한다."""
        self._client = client

    def pay(self, amount_krw: int, card_token: str) -> str:
        """int → Decimal, 상태 코드 → 예외."""
        res = self._client.create_payment(Decimal(amount_krw), "KRW", card_token)
        if res.status_code != 0 or res.payment_id is None:
            raise PaymentDeclined(f"[B] 코드 {res.status_code}")
        return res.payment_id

    def refund(self, transaction_id: str, amount_krw: int) -> None:
        """환불도 같은 번역 규칙."""
        if self._client.refund_payment(transaction_id, Decimal(amount_krw)).status_code != 0:
            raise PaymentDeclined("[B] 환불 실패")

    def receipt_url(self, transaction_id: str) -> str:
        """필요한 부가 기능만 골라서, 우리 이름으로 노출한다."""
        return self._client.get_receipt_url(transaction_id)


# --- (2) 함수 하나짜리 인터페이스면 함수 어댑터로 충분하다 -----------------

Charger = Callable[[int, str], str]
"""정산 배치가 기대하는 Target: (금액, 토큰) -> 거래번호. 메서드 하나뿐이면 '타입=함수'다."""


def settle_batch(charge: Charger, items: list[tuple[int, str]]) -> list[str]:
    """[Client] 정산 배치. 클래스가 아니라 호출 가능한 것 하나만 받는다."""
    return [charge(amount, token) for amount, token in items]


def a_charger(client: PgAClient, merchant_id: str) -> Charger:
    """[Adapter 팩토리] A SDK를 Charger 모양으로 바꾼다.

    partial로 merchant_id를 미리 묶어 인자 개수를 맞추고, 내부 함수로 dict → str을 번역한다.
    클래스 없이도 어댑터의 본질(인터페이스 변환)은 그대로다.
    """
    bound = partial(client.charge, merchant_id)        # (amount, token) -> dict 가 된다

    def charge(amount_krw: int, card_token: str) -> str:
        """결과 dict에서 거래번호만 꺼낸다."""
        return bound(amount_krw, card_token)["tid"]

    return charge


# --- (3) __getattr__ 위임: 편하지만 인터페이스 경계가 사라진다 ---------------

class LeakyPgBAdapter(PgBAdapter):
    """[안티 예시] 정의하지 않은 속성은 전부 SDK로 넘긴다.

    한 줄로 스무 개 메서드를 '노출'하지만, 그 대가로
    - SDK 원본 메서드(create_payment)가 번역 없이 새어 나와 호출자가 status_code를 다시 알게 된다.
    - 오타(pay 대신 paay)의 오류 메시지가 어댑터가 아닌 SDK 쪽 이름으로 나와 원인 추적이 어렵다.
    - 정적 분석기는 이 객체에 무엇이 있는지 알 수 없다(타입 힌트 무력화).
    """

    def __getattr__(self, name: str) -> Any:
        """인스턴스·클래스에서 못 찾은 이름일 때만 호출된다(__getattribute__와 다름)."""
        return getattr(self._client, name)


# --- 예외 변환의 문법: raise ... from -----------------------------------------

def translate_errors(fn: Callable[[], str]) -> str:
    """통신 계열 예외(ConnectionError, TimeoutError)를 우리 예외로 바꾸되 원인은 __cause__에 보존한다.

    'from e'를 빼면 파이썬은 "During handling of the above exception, another
    exception occurred"로 출력해 마치 번역 코드가 버그를 낸 것처럼 보인다.
    'from e'는 "이건 의도한 변환"이라는 표시다.
    """
    try:
        return fn()
    except (ConnectionError, TimeoutError) as e:
        raise PaymentDeclined("PG 통신 실패") from e


if __name__ == "__main__":
    print("[1] Protocol: 상속 없이도 Target으로 인정된다")
    b = PgBAdapter(PgBClient())
    print(f"    isinstance(b, PaymentGateway) = {isinstance(b, PaymentGateway)}")
    print(f"    결제 → {b.pay(9_900, 'tok_ok')}, 영수증 → {b.receipt_url('B-77')}")

    print("[2] 함수 어댑터: partial + 내부 함수로 A SDK를 Charger 모양으로")
    charge = a_charger(PgAClient(), merchant_id="M01")
    print(f"    settle_batch → {settle_batch(charge, [(1_000, 't1'), (2_500, 't2')])}")

    print("[3] __getattr__ 위임의 함정")
    leaky = LeakyPgBAdapter(PgBClient())
    raw = leaky.create_payment(Decimal(1), "KRW", "tok_declined")   # 번역을 우회한 호출
    print(f"    leaky.create_payment(...) → {raw}  ← 호출자가 status_code를 다시 알게 됐다")
    try:
        leaky.paay(1_000, "tok_ok")   # 오타
    except AttributeError as e:
        print(f"    오타 paay → AttributeError: {e}  ← 어댑터가 아닌 SDK 이름이 보인다")

    print("[4] raise ... from: 원인 예외가 __cause__로 남는다")

    def flaky() -> str:
        """네트워크 오류를 흉내 낸다."""
        raise ConnectionError("pg-b.example:443 연결 거부")

    try:
        translate_errors(flaky)
    except PaymentDeclined as e:
        print(f"    PaymentDeclined: {e} / __cause__ = {e.__cause__!r}")
