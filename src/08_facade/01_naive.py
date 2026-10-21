"""08 퍼사드 — 순진한 설계: 세 클라이언트가 다섯 서브시스템의 호출 순서를 각자 복제한다.

상황: 항공사 '푸른날개항공'의 키오스크 개발자 지호는 화면 코드에서 예약 조회 → 여권 판독 →
좌석 배정 → 수하물 요금 → 탑승권 출력을 순서대로 호출했다. 같은 체크인 흐름이 모바일 앱과
카운터 직원용 웹에도 필요해지자 각 팀이 지호의 코드를 보고 호출 순서를 '복제'했다.
그 뒤 미국행 노선에 사전 승객정보(APIS) 전송 단계가 추가되었다. 키오스크 팀은 반영했지만
모바일 팀은 놓쳤다. 이 파일은 그 상태를 재현한다 — 데모 [2]를 보라.
"""
from __future__ import annotations

from dataclasses import dataclass

# ---------------------------------------------------------------------------
# 서브시스템 — 각자 독립된 팀이 관리하는 사내 서비스(흉내). 각각은 잘 설계되어 있다.
# 문제는 이들이 아니라, 이들을 '어떤 순서와 규칙으로' 엮는 지식이 어디 있느냐다.
# ---------------------------------------------------------------------------


@dataclass
class Booking:
    """예약 정보."""

    pnr: str
    last_name: str
    destination: str
    passport_verified: bool = False
    seat: str | None = None


class ReservationSystem:
    """예약 조회 서브시스템."""

    def find(self, pnr: str, last_name: str) -> Booking:
        """예약 번호와 성으로 예약을 찾는다."""
        dest = "JFK" if pnr.startswith("US") else "NRT"
        return Booking(pnr, last_name, dest)


class PassportReader:
    """여권 판독기(하드웨어 드라이버 래퍼)."""

    def scan(self, booking: Booking, mrz: str) -> None:
        """MRZ(기계 판독 영역)의 성이 예약과 일치하면 검증 표시."""
        booking.passport_verified = booking.last_name.upper() in mrz


class SeatService:
    """좌석 배정 서브시스템. 규칙: 여권 검증 전에는 배정 금지(출입국 규정)."""

    def assign(self, booking: Booking, preference: str) -> str:
        """선호(창가/통로)에 따라 좌석 배정. 규칙 검사는 하지 않는다 — 호출자 책임이라는 계약."""
        booking.seat = "23A" if preference == "window" else "23C"
        return booking.seat


class BaggageService:
    """수하물 요금 서브시스템."""

    def quote(self, booking: Booking, bags: int) -> int:
        """1개 무료, 이후 개당 요금. 미국행은 요금이 다르다."""
        unit = 100_000 if booking.destination == "JFK" else 60_000
        return max(0, bags - 1) * unit


class ApisGateway:
    """미국행 사전 승객정보(APIS) 전송. 전송 없이 발권하면 항공사가 벌금을 문다."""

    def submit(self, booking: Booking) -> None:
        """승객 정보 전송."""
        print(f"    (APIS) {booking.pnr} 승객 정보 전송")


class BoardingPassPrinter:
    """탑승권 발급기."""

    def issue(self, booking: Booking) -> str:
        """탑승권 문자열을 만든다."""
        return f"[탑승권] {booking.last_name} {booking.pnr} → {booking.destination} 좌석 {booking.seat}"


# ---------------------------------------------------------------------------
# 클라이언트 셋 — 각자 다섯(여섯) 서브시스템을 직접 안다.
# ---------------------------------------------------------------------------

class KioskScreen:
    """공항 키오스크 화면."""

    def __init__(self) -> None:
        """⚠ 문제: UI 클래스가 서브시스템 여섯 개를 직접 생성·보유한다(결합도 6)."""
        self.res, self.passport, self.seats = ReservationSystem(), PassportReader(), SeatService()
        self.bags, self.apis, self.printer = BaggageService(), ApisGateway(), BoardingPassPrinter()

    def on_check_in(self, pnr: str, name: str, mrz: str, pref: str, bags: int) -> str:
        """체크인 버튼 처리."""
        booking = self.res.find(pnr, name)
        self.passport.scan(booking, mrz)
        if not booking.passport_verified:
            return "여권 불일치"
        self.seats.assign(booking, pref)
        fee = self.bags.quote(booking, bags)
        # ⚠ 문제: 'APIS는 미국행에만, 발권 전에'라는 규칙이 UI 코드에 있다.
        if booking.destination == "JFK":
            self.apis.submit(booking)
        return f"{self.printer.issue(booking)} / 수하물 {fee:,}원"


class MobileApp:
    """모바일 앱 체크인. 키오스크 코드를 보고 복제했다."""

    def __init__(self) -> None:
        """⚠ 문제: 다섯 의존이 또 생긴다(APIS 게이트웨이는 복제 과정에서 빠졌다)."""
        self.res, self.passport, self.seats = ReservationSystem(), PassportReader(), SeatService()
        self.bags, self.printer = BaggageService(), BoardingPassPrinter()

    def check_in(self, pnr: str, name: str, mrz: str, pref: str, bags: int) -> str:
        """⚠ 문제: 복제 과정에서 순서 규칙(여권 → 좌석)이 뒤바뀌고 APIS 단계가 빠졌다."""
        booking = self.res.find(pnr, name)
        self.seats.assign(booking, pref)            # ⚠ 여권 검증 전 좌석 배정 — 규정 위반
        self.passport.scan(booking, mrz)
        fee = self.bags.quote(booking, bags)
        return f"{self.printer.issue(booking)} / 수하물 {fee:,}원"   # ⚠ APIS 미전송


if __name__ == "__main__":
    print("[1] 키오스크: 미국행 체크인")
    print("    " + KioskScreen().on_check_in("US7Q2K", "Kim", "P<KORKIM<<JIHO", "window", 2))

    print("[2] 모바일 앱: 같은 승객, 같은 노선")
    print("    " + MobileApp().check_in("US7Q2K", "Kim", "P<KORKIM<<JIHO", "window", 2))
    print("    → APIS 전송 로그가 없다. 그리고 좌석은 여권 판독 '전에' 배정됐다.")

    print("[3] 모바일 앱: 여권이 다른 사람인데도 탑승권이 나온다")
    print("    " + MobileApp().check_in("NR11AB", "Lee", "P<KORPARK<<MINA", "aisle", 1))
