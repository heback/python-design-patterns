"""08 퍼사드 — 순진한 코드: 화면마다 체크인 순서를 복사해 서브시스템을 직접 부른다.

상황: 푸른날개항공의 키오스크 화면은 예약·여권·좌석·수하물·미국행 신고·탑승권
서브시스템을 차례로 부른다. 모바일 앱 팀은 이 호출 순서를 베껴 왔는데,
베끼는 과정에서 미국행 신고를 빠뜨리고 여권 확인 순서를 바꿔 놓았다.
"""
from __future__ import annotations

from dataclasses import dataclass


# --- 서브시스템: 각자는 잘 만들어져 있다 ---
@dataclass
class Booking:
    """예약 정보. 단계마다 필드가 채워진다."""
    pnr: str
    last_name: str
    destination: str
    passport_ok: bool = False
    seat: str | None = None


class ReservationSystem:
    """예약 조회."""
    def find(self, pnr: str, last_name: str) -> Booking:
        """예약 번호가 US로 시작하면 미국행."""
        return Booking(pnr, last_name, "JFK" if pnr.startswith("US") else "NRT")


class PassportReader:
    """여권 판독기."""
    def scan(self, booking: Booking, passport_name: str) -> None:
        """여권의 이름이 예약자와 같으면 확인 표시."""
        booking.passport_ok = booking.last_name.upper() == passport_name.upper()


class SeatService:
    """좌석 배정."""
    def assign(self, pnr: str, pref: str) -> str:
        """창가 또는 통로."""
        return "31A" if pref == "window" else "31C"


class UsEntryReport:
    """미국행 승객 정보 신고. 발권 전에 반드시 보내야 한다."""
    def submit(self, booking: Booking) -> None:
        """신고 전송."""
        print(f"    (미국행 신고) {booking.pnr} 전송")


class BoardingPassPrinter:
    """탑승권 발급."""
    def issue(self, b: Booking) -> str:
        """탑승권 문자열."""
        return f"[탑승권] {b.last_name} → {b.destination} 좌석 {b.seat}"


# --- 클라이언트: 흐름을 각자 안다 ---
class KioskScreen:
    """키오스크. 원래의 올바른 흐름."""
    def __init__(self) -> None:
        """⚠ 문제: 서브시스템 다섯 개를 화면이 직접 만든다."""
        self.res, self.pp, self.seats = ReservationSystem(), PassportReader(), SeatService()
        self.us, self.printer = UsEntryReport(), BoardingPassPrinter()

    def check_in(self, pnr: str, last_name: str, passport_name: str) -> str:
        """여권 확인 → 좌석 → (미국행이면 신고) → 탑승권."""
        b = self.res.find(pnr, last_name)
        self.pp.scan(b, passport_name)
        if not b.passport_ok:   # ⚠ 문제: 규정(여권 먼저)이 화면 코드의 줄 순서에 들어 있다
            return "여권 불일치"
        b.seat = self.seats.assign(pnr, "window")
        if b.destination == "JFK":
            self.us.submit(b)
        return self.printer.issue(b)


class MobileApp(KioskScreen):
    """모바일 앱. 키오스크 흐름을 베껴 다시 썼다."""
    def check_in(self, pnr: str, last_name: str, passport_name: str) -> str:
        """⚠ 문제: 베끼다 미국행 신고를 빠뜨리고, 여권 결과도 보지 않는다."""
        b = self.res.find(pnr, last_name)
        b.seat = self.seats.assign(pnr, "window")
        self.pp.scan(b, passport_name)
        return self.printer.issue(b)


if __name__ == "__main__":
    print("[1] 키오스크, 미국행 — 신고 후 발권")
    print("   ", KioskScreen().check_in("US123", "Lee", "LEE"))
    print("[2] 모바일, 미국행 — 신고 로그가 없다")
    print("   ", MobileApp().check_in("US123", "Lee", "LEE"))
    print("[3] 모바일, 남의 여권 — 그래도 발권된다")
    print("   ", MobileApp().check_in("KR9", "Lee", "PARK"))
