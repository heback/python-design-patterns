"""05 어댑터 — 연습문제 1 해설: 클래스 어댑터가 파이썬에서 '가능하지만 권하지 않는' 이유.

상황: 예린의 동료가 "어댑터 클래스를 따로 두지 말고 PaymentGateway와 PgBClient를
다중 상속하면 위임 코드가 필요 없다"고 제안했다. 이 파일은 그 클래스 어댑터를 실제로
만들어 보고, (1) MRO가 어떻게 생기는지, (2) SDK 메서드가 Target에 새어 나오는
인터페이스 오염, (3) 이름 충돌 시 SDK 내부의 self 호출이 우리 메서드로 '납치'되는
문제를 데모로 보인다.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal


@dataclass
class PaymentResponse:
    """B SDK 응답."""

    status_code: int
    payment_id: str


class PgBClient:
    """[Adaptee] B SDK. 공교롭게도 refund라는 이름을 '다른 시그니처·반환형'으로 쓴다."""

    def create_payment(self, amount: Decimal, token: str) -> PaymentResponse:
        """결제 생성."""
        return PaymentResponse(0, "B-1")

    def refund(self, payment_id: str, amount: Decimal) -> PaymentResponse:
        """SDK의 환불. PaymentResponse를 '반환'한다."""
        return PaymentResponse(0, payment_id)

    def refund_all(self, payment_ids: list[str]) -> int:
        """SDK 내부 편의 기능. self.refund()를 호출한다 — 여기가 함정의 입구다.

        SDK 작성자는 self.refund가 '자기' refund라고 가정했다. 서브클래스가
        같은 이름을 재정의하면 동적 디스패치 때문에 그 가정이 깨진다.
        """
        return sum(1 for pid in payment_ids if self.refund(pid, Decimal(0)).status_code == 0)


class PaymentGateway(ABC):
    """[Target] 우리 결제 포트. refund는 None을 반환하고 실패 시 예외."""

    @abstractmethod
    def pay(self, amount_krw: int, card_token: str) -> str:
        """결제."""

    @abstractmethod
    def refund(self, transaction_id: str, amount_krw: int) -> None:
        """환불(반환값 없음)."""


class PgBClassAdapter(PaymentGateway, PgBClient):
    """[클래스 어댑터] Target과 Adaptee를 모두 상속한다.

    위임 필드가 없으니 코드가 짧아 보이지만, '이 객체는 PgBClient이기도 하다'는
    is-a 관계를 외부에 약속해 버린다.
    """

    def pay(self, amount_krw: int, card_token: str) -> str:
        """SDK 메서드를 self로 바로 부른다(합성 대신 상속)."""
        return self.create_payment(Decimal(amount_krw), card_token).payment_id

    def refund(self, transaction_id: str, amount_krw: int) -> None:  # type: ignore[override]
        """Target의 refund. SDK의 refund를 덮어쓴다 — 이름이 같기 때문에 피할 수 없다.

        SDK 원본을 부르려면 self.refund가 아니라 PgBClient.refund(self, ...)로
        MRO를 우회해야 한다. 이미 어색함이 시작됐다.
        """
        PgBClient.refund(self, transaction_id, Decimal(amount_krw))
        return None


if __name__ == "__main__":
    print("[1] MRO — 두 부모가 한 줄로 선형화된다")
    print("    " + " → ".join(c.__name__ for c in PgBClassAdapter.__mro__))

    adapter = PgBClassAdapter()
    print("[2] 인터페이스 오염 — Target에 없는 SDK 메서드가 그대로 공개된다")
    leaked = [n for n in ("create_payment", "refund_all") if hasattr(adapter, n)]
    print(f"    호출 가능한 SDK 원본 메서드: {leaked}")
    print(f"    isinstance(adapter, PgBClient) = {isinstance(adapter, PgBClient)}  ← SDK 타입을 받는 곳에도 들어간다")

    print("[3] 이름 충돌 — SDK 내부의 self.refund()가 우리 refund()로 납치된다")
    try:
        adapter.refund_all(["B-1", "B-2"])
    except AttributeError as e:
        print(f"    refund_all 실패: AttributeError: {e}")
        print("    SDK는 PaymentResponse를 기대했지만 우리 refund()가 None을 돌려줬다.")
