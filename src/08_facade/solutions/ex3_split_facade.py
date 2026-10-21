"""08 퍼사드 — 연습문제 3 해설: 메서드 30개짜리 퍼사드를 어떻게 할까.

상황: CheckInFacade가 2년 사이 30개 메서드로 불었다. 승객용(체크인, 좌석 변경, 수하물 추가),
직원용(수동 좌석 지정, 오버부킹 처리, 탑승 마감), 운영용(통계, 장비 상태)이 한 클래스에
섞였다. 판단 기준은 '메서드 수'가 아니라 '누가, 왜 바뀌는가'다. 이 파일은 (가) 클라이언트
역할별로 퍼사드를 나누는 결과를 보인다. (나) 서브시스템 재설계는 원고 해설의 서술을 참조하라.
"""
from __future__ import annotations


class SeatService:
    """[Subsystem] 좌석."""

    def allocate(self, pnr: str, zone: str) -> str:
        """자동 배정."""
        return "31A" if zone == "W" else "31C"

    def override(self, pnr: str, seat: str) -> str:
        """수동 지정."""
        return seat


class BoardingControl:
    """[Subsystem] 탑승 관리."""

    def close_flight(self, flight: str) -> str:
        """탑승 마감."""
        return f"{flight} 마감"


class PassengerCheckIn:
    """[Facade] 승객용 — 키오스크·모바일이 쓴다. 변경 이유: 승객 UX 요구.

    메서드가 적고 '안전한' 연산만 있다. 직원 권한이 필요한 기능이 섞여 있지 않으므로
    승객 퍼사드를 '통해서는' 수동 지정을 호출할 길이 없다(ISP). 다만 퍼사드는 접근을 막지 않으므로
    모바일 앱이 SeatService를 직접 쓰는 것까지 막지는 못한다. 진짜 차단은 보호 프록시나
    서브시스템의 권한 검사 몫이다(9장).
    """

    def __init__(self, seats: SeatService) -> None:
        """서브시스템 주입."""
        self._seats = seats

    def choose_seat(self, pnr: str, window: bool) -> str:
        """선호만 받는다."""
        return self._seats.allocate(pnr, "W" if window else "A")


class AgentConsole:
    """[Facade] 카운터·게이트 직원용. 변경 이유: 운영 절차 개정.

    서브시스템 인스턴스는 PassengerCheckIn과 공유한다 — 퍼사드를 나눠도 상태가 갈라지지 않는다.
    """

    def __init__(self, seats: SeatService, boarding: BoardingControl) -> None:
        """서브시스템 주입."""
        self._seats, self._boarding = seats, boarding

    def force_seat(self, pnr: str, seat: str) -> str:
        """수동 좌석 지정."""
        return self._seats.override(pnr, seat)

    def close_gate(self, flight: str) -> str:
        """탑승 마감."""
        return self._boarding.close_flight(flight)


if __name__ == "__main__":
    seats = SeatService()
    passenger, agent = PassengerCheckIn(seats), AgentConsole(seats, BoardingControl())
    print("[1] 승객 퍼사드:", passenger.choose_seat("NR11AB", window=True))
    print("[2] 직원 퍼사드:", agent.force_seat("NR11AB", "12F"), "/", agent.close_gate("BW702"))
    print(f"[3] 승객 퍼사드에 force_seat(수동 지정)가 있는가? {hasattr(passenger, 'force_seat')}")
