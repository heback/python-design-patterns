"""08 퍼사드 — 패턴 적용: CheckInFacade가 체크인 흐름과 순서 규칙을 한 곳에 모은다.

상황: 지호는 세 클라이언트(키오스크·모바일·카운터 웹)가 각자 복제한 호출 순서를
CheckInFacade.check_in() 하나로 모은다. 순서 규칙(여권 검증 → 좌석 배정), 노선별 단계
(미국행 APIS)는 이제 퍼사드 안에만 있다. 같은 시기에 좌석 서비스가 v2 API(allocate)로
바뀌었는데, 이 변경도 퍼사드 한 곳만 고치면 된다.
주의: 퍼사드는 서브시스템을 '숨기지' 않는다. 카운터 직원 웹은 좌석 수동 변경을 위해
SeatServiceV2에 직접 접근한다(데모 [3]). 퍼사드는 '쉬운 길'을 추가할 뿐 '다른 길'을 막지 않는다.
"""
from __future__ import annotations

from dataclasses import dataclass

# ===========================================================================
# 서브시스템 (01_naive.py와 같되, 좌석 서비스가 v2로 바뀌었다)
# ===========================================================================


@dataclass
class Booking:
    """예약 정보."""

    pnr: str
    last_name: str
    destination: str
    passport_verified: bool = False
    seat: str | None = None


class ReservationSystem:
    """[Subsystem] 예약 조회."""

    def find(self, pnr: str, last_name: str) -> Booking:
        """예약 번호와 성으로 예약을 찾는다."""
        return Booking(pnr, last_name, "JFK" if pnr.startswith("US") else "NRT")


class PassportReader:
    """[Subsystem] 여권 판독기."""

    def scan(self, booking: Booking, mrz: str) -> None:
        """MRZ의 성이 예약과 일치하면 검증 표시."""
        booking.passport_verified = booking.last_name.upper() in mrz


class SeatServiceV2:
    """[Subsystem] 좌석 배정 v2. 메서드 이름과 인자가 v1(assign)에서 바뀌었다."""

    def allocate(self, pnr: str, zone: str) -> str:
        """zone은 'W'(창가) 또는 'A'(통로). 좌석 번호를 돌려준다."""
        return {"W": "31A", "A": "31C"}[zone]

    def override(self, pnr: str, seat: str) -> str:
        """카운터 직원 전용: 좌석 수동 지정. 퍼사드에는 없는 고급 기능이다."""
        return seat


class BaggageService:
    """[Subsystem] 수하물 요금."""

    def quote(self, booking: Booking, bags: int) -> int:
        """1개 무료, 이후 개당 요금."""
        unit = 100_000 if booking.destination == "JFK" else 60_000
        return max(0, bags - 1) * unit


class ApisGateway:
    """[Subsystem] 미국행 사전 승객정보 전송."""

    def submit(self, booking: Booking) -> None:
        """승객 정보 전송."""
        print(f"    (APIS) {booking.pnr} 승객 정보 전송")


class BoardingPassPrinter:
    """[Subsystem] 탑승권 발급."""

    def issue(self, booking: Booking) -> str:
        """탑승권 문자열."""
        return f"[탑승권] {booking.last_name} {booking.pnr} → {booking.destination} 좌석 {booking.seat}"


# ===========================================================================
# 퍼사드
# ===========================================================================

class CheckInError(Exception):
    """체크인 실패. 클라이언트는 서브시스템별 오류가 아니라 이것 하나만 처리한다."""


@dataclass(frozen=True)
class CheckInResult:
    """체크인 결과. 클라이언트가 화면에 그릴 정보만 담는다(Booking 내부를 노출하지 않음)."""

    boarding_pass: str
    baggage_fee: int


class CheckInFacade:
    """[Facade] 셀프 체크인의 단일 진입점.

    책임은 '조율'뿐이다: 어떤 서브시스템을 어떤 순서와 조건으로 부를지.
    좌석 계산·요금 계산 같은 실제 업무 로직은 여전히 서브시스템에 있다. 퍼사드에 업무 로직이
    자라기 시작하면 '신 객체(God object)'로 가는 신호다.
    서브시스템을 생성자에서 주입받는 이유: 테스트에서 가짜를 넣고, 서브시스템 인스턴스를
    다른 클라이언트(카운터 웹)와 공유할 수 있게 하기 위해서다.
    """

    def __init__(self, reservations: ReservationSystem, passports: PassportReader,
                 seats: SeatServiceV2, baggage: BaggageService, apis: ApisGateway,
                 printer: BoardingPassPrinter) -> None:
        """서브시스템 주입."""
        self._res, self._passports, self._seats = reservations, passports, seats
        self._baggage, self._apis, self._printer = baggage, apis, printer

    def check_in(self, pnr: str, last_name: str, mrz: str,
                 seat_pref: str = "window", bags: int = 1) -> CheckInResult:
        """체크인 전체 흐름. 순서 규칙은 이 메서드의 '줄 순서'로 단 한 번 표현된다."""
        booking = self._res.find(pnr, last_name)

        # 규칙 1: 여권 검증이 좌석 배정보다 먼저(출입국 규정). 실패하면 이후 단계로 가지 않는다.
        self._passports.scan(booking, mrz)
        if not booking.passport_verified:
            raise CheckInError("여권 정보가 예약자와 일치하지 않습니다")

        # 좌석 서비스 v2 변경은 여기 두 줄만 바뀌었다. 세 클라이언트는 몰라도 된다.
        zone = "W" if seat_pref == "window" else "A"
        booking.seat = self._seats.allocate(booking.pnr, zone)

        fee = self._baggage.quote(booking, bags)

        # 규칙 2: 미국행은 발권 '전에' APIS 전송. 노선별 규칙이 늘면 이 부분을 별도 정책 객체로 뺄 시점이다.
        if booking.destination == "JFK":
            self._apis.submit(booking)

        return CheckInResult(self._printer.issue(booking), fee)


# ===========================================================================
# 클라이언트 — 각자 퍼사드 하나에만 의존한다.
# ===========================================================================

class KioskScreen:
    """[Client] 키오스크. 의존: CheckInFacade 1개."""

    def __init__(self, facade: CheckInFacade) -> None:
        """퍼사드만 받는다."""
        self._facade = facade

    def on_check_in(self, pnr: str, name: str, mrz: str, pref: str, bags: int) -> str:
        """화면 표시용 문자열. UI는 UI 일(메시지 포맷)만 한다."""
        try:
            r = self._facade.check_in(pnr, name, mrz, pref, bags)
        except CheckInError as e:
            return f"⚠ {e} — 카운터로 가 주세요"
        return f"{r.boarding_pass} / 수하물 {r.baggage_fee:,}원"


class MobileApp:
    """[Client] 모바일 앱. 키오스크와 같은 흐름을 '복제'하지 않고 '공유'한다."""

    def __init__(self, facade: CheckInFacade) -> None:
        """퍼사드만 받는다."""
        self._facade = facade

    def check_in(self, pnr: str, name: str, mrz: str, pref: str, bags: int) -> dict:
        """앱 API 응답(JSON 흉내)."""
        try:
            r = self._facade.check_in(pnr, name, mrz, pref, bags)
        except CheckInError as e:
            return {"ok": False, "error": str(e)}
        return {"ok": True, "pass": r.boarding_pass, "fee": r.baggage_fee}


if __name__ == "__main__":
    # 조립 지점: 서브시스템을 한 번 만들어 퍼사드와 (필요하면) 고급 클라이언트에 나눠 준다.
    seats = SeatServiceV2()
    facade = CheckInFacade(ReservationSystem(), PassportReader(), seats,
                           BaggageService(), ApisGateway(), BoardingPassPrinter())

    print("[1] 키오스크와 모바일 — 같은 미국행 승객, 같은 결과(APIS 포함)")
    print("    " + KioskScreen(facade).on_check_in("US7Q2K", "Kim", "P<KORKIM<<JIHO", "window", 2))
    print(f"    {MobileApp(facade).check_in('US7Q2K', 'Kim', 'P<KORKIM<<JIHO', 'window', 2)}")

    print("[2] 여권 불일치 — 어느 클라이언트든 좌석 배정 전에 멈춘다")
    print("    " + KioskScreen(facade).on_check_in("NR11AB", "Lee", "P<KORPARK<<MINA", "aisle", 1))
    print(f"    {MobileApp(facade).check_in('NR11AB', 'Lee', 'P<KORPARK<<MINA', 'aisle', 1)}")

    print("[3] 카운터 직원 웹 — 퍼사드로 체크인한 뒤, 서브시스템에 직접 접근해 좌석 수동 변경")
    result = facade.check_in("NR55CD", "Choi", "P<KORCHOI<<YUNA", "aisle", 1)
    print(f"    퍼사드 결과: {result.boarding_pass}")
    print(f"    직원 수동 변경: {seats.override('NR55CD', '12F')} (퍼사드는 이 길을 막지 않는다)")
