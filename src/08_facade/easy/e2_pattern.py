"""08 퍼사드 — 패턴 코드: CheckInFacade가 체크인 순서와 규칙을 한 곳에 모은다.

상황: 지호는 화면마다 복사된 호출 순서를 CheckInFacade.check_in() 하나로 모은다.
같은 시기에 좌석 서비스가 v2(allocate)로 바뀌었는데, 이 변경도 퍼사드만 고치면 된다.
퍼사드는 서브시스템을 숨기지 않는다. 카운터 직원은 좌석 수동 지정(override)을 직접 부른다.
서브시스템은 순진한 코드와 같고 좌석 서비스만 v2로 바뀌었다.
"""
from __future__ import annotations

from dataclasses import dataclass


# --- 서브시스템 (Subsystem) — 퍼사드를 모른다 ---
@dataclass
class Booking:
    """예약 정보."""
    pnr: str
    last_name: str
    destination: str
    passport_ok: bool = False
    seat: str | None = None


class ReservationSystem:
    """[Subsystem] 예약 조회."""
    def find(self, pnr: str, last_name: str) -> Booking:
        """예약 번호가 US로 시작하면 미국행."""
        return Booking(pnr, last_name, "JFK" if pnr.startswith("US") else "NRT")


class PassportReader:
    """[Subsystem] 여권 판독기."""
    def scan(self, booking: Booking, passport_name: str) -> None:
        """이름이 같으면 확인 표시."""
        booking.passport_ok = booking.last_name.upper() == passport_name.upper()


class SeatServiceV2:
    """[Subsystem] 좌석 배정 v2. v1의 assign(pref)이 allocate(zone)으로 바뀌었다."""
    def allocate(self, pnr: str, zone: str) -> str:
        """zone은 'W'(창가) 또는 'A'(통로)."""
        return {"W": "31A", "A": "31C"}[zone]

    def override(self, pnr: str, seat: str) -> str:
        """직원 전용 좌석 수동 지정. 퍼사드에는 없는 기능이다."""
        return seat


class UsEntryReport:
    """[Subsystem] 미국행 승객 정보 신고."""
    def submit(self, booking: Booking) -> None:
        """신고 전송."""
        print(f"    (미국행 신고) {booking.pnr} 전송")


class BoardingPassPrinter:
    """[Subsystem] 탑승권 발급."""
    def issue(self, b: Booking) -> str:
        """탑승권 문자열."""
        return f"[탑승권] {b.last_name} → {b.destination} 좌석 {b.seat}"


# --- 퍼사드 (Facade) ---
class CheckInError(Exception):
    """체크인 실패. 클라이언트는 이것 하나만 처리한다."""


class CheckInFacade:
    """[Facade] 셀프 체크인의 단일 진입점. 책임은 '조율'뿐이다.

    좌석을 고르는 방법 같은 업무 로직은 서브시스템에 남긴다. 서브시스템을 생성자로
    받는 이유: 테스트에서 가짜를 넣고, 같은 인스턴스를 다른 클라이언트와 공유하려고.
    """

    def __init__(self, res: ReservationSystem, passports: PassportReader, seats: SeatServiceV2,
                 us_report: UsEntryReport, printer: BoardingPassPrinter) -> None:
        """서브시스템 주입."""
        self._res, self._passports, self._seats = res, passports, seats
        self._us, self._printer = us_report, printer

    def check_in(self, pnr: str, last_name: str, passport_name: str,
                 seat_pref: str = "window") -> str:
        """체크인 전체 흐름. 순서 규칙이 여기 단 한 번 적힌다. 탑승권 문자열을 돌려준다."""
        booking = self._res.find(pnr, last_name)
        # 규칙 1: 여권 확인이 좌석 배정보다 먼저. 실패하면 멈춘다.
        self._passports.scan(booking, passport_name)
        if not booking.passport_ok:
            raise CheckInError("여권 정보가 예약자와 다릅니다")
        # 좌석 v2 변경은 이 두 줄만 바뀌었다. 클라이언트는 여전히 seat_pref="window"로 부른다.
        zone = "W" if seat_pref == "window" else "A"
        booking.seat = self._seats.allocate(pnr, zone)
        # 규칙 2: 미국행은 발권 전에 신고.
        if booking.destination == "JFK":
            self._us.submit(booking)
        return self._printer.issue(booking)


if __name__ == "__main__":
    # 조립 지점: 서브시스템을 한 번 만들어 퍼사드와 카운터 직원 화면이 함께 쓴다.
    seats = SeatServiceV2()
    facade = CheckInFacade(ReservationSystem(), PassportReader(), seats,
                           UsEntryReport(), BoardingPassPrinter())
    print("[1] 키오스크와 모바일이 같은 퍼사드를 부른다 — 둘 다 미국행 신고를 보낸다")
    for client in ("키오스크", "모바일"):
        print(f"    {client}: {facade.check_in('US123', 'Lee', 'LEE')}")
    print("[2] 남의 여권 — 좌석 배정 전에 멈춘다")
    try:
        facade.check_in("KR9", "Lee", "PARK")
    except CheckInError as e:
        print(f"    거절: {e}")
    print("[3] 카운터 직원은 퍼사드를 거치지 않고 좌석 서비스를 직접 쓴다:", seats.override("KR9", "1A"))
