"""연습문제 2 해설: '스마트 주차장' 순진한 코드에서 변경 축 3개를 찾아 각각 가장 가벼운 패턴으로.

상황: 한빛로지스 물류센터의 직원 주차장 시스템(문제 본문 코드)은 ParkingLot.leave() 하나에
요금 계산·차단기 제어·알림이 다 들어 있었다. 변경 요구 이력을 보면 축이 셋이다.
1. 요금 규칙(경차 할인, 야간 정액, 직원 무료…)이 분기마다 바뀐다     → 전략(10장): 함수 + 이름표 dict
2. 차단기 제조사가 바뀐다(GateCo의 open_bar(gate_no) → 신형 BarrierX의 lift(id, ms)) → 어댑터(5장)
3. 출차 알림을 받는 쪽이 는다(전광판, 문자, 정산 시스템)            → 옵저버(11장): 콜러블 구독
축이 아닌 것에는 패턴을 넣지 않았다: 차량 상태(입차/출차)는 bool 하나, 주차장은 하나지만 싱글턴 없음.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Protocol

# ---------------------------------------------------------------------------
# 축 1: 요금 규칙 — 전략이지만 파이썬에서는 그냥 함수
# ---------------------------------------------------------------------------

FeeRule = Callable[[str, int], int]  # (차종, 주차 분) → 요금(원)


def standard(car: str, minutes: int) -> int:
    """기본: 30분 1,000원, 경차 50% 할인. 할인은 규칙 내부 사정이라 여기에 둔다."""
    fee = -(-minutes // 30) * 1000  # 올림 나눗셈: 31분은 2구간
    return fee // 2 if car == "compact" else fee


def staff_free(car: str, minutes: int) -> int:
    """직원 주차장: 무료."""
    return 0


FEE_RULES: dict[str, FeeRule] = {"standard": standard, "staff": staff_free}

# ---------------------------------------------------------------------------
# 축 2: 차단기 — 어댑터
# ---------------------------------------------------------------------------


class Gate(Protocol):
    """[Target] 주차장이 차단기에게 원하는 것은 '열어라' 하나."""

    def open(self) -> str:
        """차단기를 연다."""
        ...


class GateCoSDK:
    """[Adaptee] 구형 차단기 SDK."""

    def open_bar(self, gate_no: int) -> str:
        """게이트 번호로 연다."""
        return f"GateCo #{gate_no} 열림"


class BarrierXSDK:
    """[Adaptee] 신형 차단기 SDK: 장치 ID와 열림 유지 시간(ms)이 필요하다."""

    def lift(self, device_id: str, hold_ms: int) -> str:
        """연다."""
        return f"BarrierX {device_id} {hold_ms}ms 열림"


@dataclass
class GateCoAdapter:
    """[Adapter] 게이트 번호를 기억해 open()을 open_bar(n)으로 번역."""

    sdk: GateCoSDK
    gate_no: int

    def open(self) -> str:
        """번역."""
        return self.sdk.open_bar(self.gate_no)


@dataclass
class BarrierXAdapter:
    """[Adapter] 장치 ID와 기본 유지 시간을 채워 lift()로 번역."""

    sdk: BarrierXSDK
    device_id: str
    hold_ms: int = 5000

    def open(self) -> str:
        """번역."""
        return self.sdk.lift(self.device_id, self.hold_ms)


# ---------------------------------------------------------------------------
# 축 3: 알림 — 옵저버(콜러블 구독)
# ---------------------------------------------------------------------------

Listener = Callable[[str, int], None]  # (번호판, 요금)


@dataclass
class ParkingLot:
    """[Context + Subject] 출차 흐름만 안다. 요금·차단기·알림의 구체는 모두 주입받는다."""

    fee_rule: FeeRule
    gate: Gate
    listeners: list[Listener] = field(default_factory=list)

    def leave(self, plate: str, car: str, minutes: int) -> str:
        """요금 계산 → 차단기 열기 → 통지. 문제 본문의 if 사슬이 위임 세 줄이 되었다."""
        fee = self.fee_rule(car, minutes)
        opened = self.gate.open()
        for notify in list(self.listeners):  # 복사본 순회: 통지 중 구독 변경에 안전
            notify(plate, fee)
        return opened


if __name__ == "__main__":
    log: list[str] = []
    lot = ParkingLot(FEE_RULES["standard"], GateCoAdapter(GateCoSDK(), 2),
                     [lambda p, f: log.append(f"전광판: {p} {f}원"),
                      lambda p, f: log.append(f"문자: {p}님 {f}원 결제")])
    print("[1] 일반 주차장, 구형 차단기")
    print("  ", lot.leave("12가3456", "compact", 45), log)

    print("\n[2] 직원 주차장으로 바꾸고 신형 차단기 설치 — ParkingLot 코드 수정 0줄")
    log.clear()
    lot.fee_rule, lot.gate = FEE_RULES["staff"], BarrierXAdapter(BarrierXSDK(), "BX-7")
    print("  ", lot.leave("34나5678", "sedan", 600), log)

    print("\n[3] 정산 시스템이 알림을 받고 싶다 — 구독 한 줄")
    lot.listeners.append(lambda p, f: log.append(f"정산: {p} {f}"))
    log.clear()
    lot.leave("56다7890", "sedan", 30)
    print("  ", log)
