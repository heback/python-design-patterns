"""05 어댑터 — 연습문제 3 해설: 이름만 다르고 의미가 같을 때 어떤 어댑터를 고를까.

상황: 새로 계약한 PG사 D의 SDK는 make_payment(amount_krw, token) -> str,
cancel_payment(tid, amount_krw) -> None 로, 우리 PaymentGateway(pay/refund)와
이름만 다르고 인자 순서·단위·반환·예외가 모두 같다. 선택지는 셋이다:
클래스 어댑터, __getattr__ 위임, 명시적 얇은 어댑터(혹은 함수).
이 파일은 권장 해법인 '명시적 얇은 어댑터'와, 메서드가 하나뿐일 때의 '바운드 메서드
그대로 쓰기'를 보인다. 왜 나머지 둘을 고르지 않는지는 각 docstring에 적었다.
"""
from __future__ import annotations

from typing import Callable, Protocol


class PgDClient:
    """[Adaptee] D SDK. 의미는 Target과 같고 이름만 다르다."""

    def make_payment(self, amount_krw: int, token: str) -> str:
        """결제."""
        return f"D-{amount_krw}"

    def cancel_payment(self, tid: str, amount_krw: int) -> None:
        """환불."""
        print(f"    (D SDK) {tid} {amount_krw}원 취소")

    def debug_dump(self) -> str:
        """SDK 내부 디버그 기능 — 우리 Target에는 노출하고 싶지 않다."""
        return "secret-merchant-key=..."


class PaymentGateway(Protocol):
    """[Target] 우리 결제 포트."""

    def pay(self, amount_krw: int, card_token: str) -> str:
        """결제."""
        ...

    def refund(self, transaction_id: str, amount_krw: int) -> None:
        """환불."""
        ...


class PgDAdapter:
    """[Adapter] 권장안: 메서드 두 개를 손으로 위임한다.

    왜 이것인가:
    - 위임이 두 줄뿐이라 '보일러플레이트를 줄인다'는 다른 선택지의 장점이 거의 없다.
    - 공개 표면이 정확히 pay/refund로 고정된다. debug_dump 같은 SDK 기능이 새지 않는다.
    - 나중에 D가 단위나 예외 방식을 바꾸면 이 두 메서드에 번역을 '추가'만 하면 된다.
      __getattr__이나 클래스 어댑터로 시작했다면 그때 구조를 갈아엎어야 한다.
    클래스 어댑터를 고르지 않는 이유: SDK 전체가 is-a로 공개되고 이름 충돌 위험(연습문제 1).
    __getattr__을 고르지 않는 이유: 이름이 '다르기' 때문에 어차피 pay→make_payment
    매핑을 써야 하며, 그 외 모든 SDK 속성이 새어 나온다.
    """

    def __init__(self, client: PgDClient) -> None:
        """합성."""
        self._client = client

    def pay(self, amount_krw: int, card_token: str) -> str:
        """이름만 번역."""
        return self._client.make_payment(amount_krw, card_token)

    def refund(self, transaction_id: str, amount_krw: int) -> None:
        """이름만 번역."""
        self._client.cancel_payment(transaction_id, amount_krw)


def run_settlement(charge: Callable[[int, str], str]) -> str:
    """[Client] 함수 하나만 필요한 클라이언트(정산 배치)."""
    return charge(3_000, "tok")


if __name__ == "__main__":
    print("[1] 명시적 얇은 어댑터")
    gw: PaymentGateway = PgDAdapter(PgDClient())
    tid = gw.pay(12_000, "tok")
    gw.refund(tid, 12_000)
    print(f"    hasattr(gw, 'debug_dump') = {hasattr(gw, 'debug_dump')}  ← SDK 내부 기능이 새지 않는다")

    print("[2] 메서드 하나만 필요하면 바운드 메서드가 곧 어댑터다")
    print(f"    run_settlement(PgDClient().make_payment) → {run_settlement(PgDClient().make_payment)}")
