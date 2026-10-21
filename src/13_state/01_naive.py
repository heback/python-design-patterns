"""[13장 상태 · 순진한 설계] 전동킥보드 대여 생명주기를 status 문자열과 if 분기로 관리한다.

상황: 공유 모빌리티 스타트업 '킥고'의 백엔드 개발자 서진은 처음에 킥보드를
"available"/"riding" 두 상태로만 관리했다. 그 뒤 예약됨(10분 유지), 배터리 부족,
정비 중, 분실 신고가 차례로 추가되면서 모든 메서드에 `if self.status == ...` 분기가
복제되었다. 이 파일은 그 시점의 코드를 그대로 보여 주고, 두 상태 시절에 쓴 `else`
분기 하나 때문에 "정비 중인 킥보드로 주행이 시작되는" 실제 버그를 데모로 재현한다.

시간은 테스트 가능하도록 `now`(초 단위 정수)를 인자로 받는다. 실제 서비스라면
시계를 주입하겠지만, 이 장의 주제가 아니므로 가장 단순한 형태를 택했다.
"""
from __future__ import annotations

RESERVATION_TTL = 600      # 예약 유지 시간(초) — 10분
LOW_BATTERY = 15           # 이 미만이면 대여 불가
UNLOCK_FEE = 1_000         # 잠금 해제 기본요금(원)
PER_MINUTE = 150           # 분당 요금(원)
NO_SHOW_FEE = 500          # 예약 후 나타나지 않으면 부과


class Scooter:
    """킥보드 한 대. 상태·데이터·전이 규칙·요금 계산이 한 클래스에 모두 들어 있다.

    처음 두 상태일 때는 이 구조가 가장 짧고 읽기 쉬웠다. 문제는 상태가 늘 때마다
    '모든' 메서드가 '모든' 상태를 알아야 한다는 점이다. 상태 수 × 메서드 수만큼
    분기가 생기고, 그중 하나만 빠뜨려도 불법 전이가 조용히 허용된다.
    """

    def __init__(self, scooter_id: str, battery: int = 100) -> None:
        """새 킥보드는 대여 가능 상태로 시작한다."""
        self.scooter_id = scooter_id
        self.battery = battery
        # ⚠ 문제: 상태가 오타에 취약한 문자열이다. "maintenance"를 "maintanance"로
        #   잘못 써도 아무도 알려 주지 않는다.
        self.status = "available"
        # ⚠ 문제: 특정 상태에서만 의미 있는 필드가 객체 전체에 흩어져 있다.
        #   reserved_by는 "reserved"일 때만, ride_started_at은 "riding"일 때만 유효하지만
        #   다른 상태에서도 남아 있어 '이전 상태의 찌꺼기'를 읽는 버그를 부른다.
        self.reserved_by: str | None = None
        self.reserved_at: int | None = None
        self.rider: str | None = None
        self.ride_started_at: int | None = None
        self.charges: list[tuple[str, int]] = []   # (사유, 금액) — 정산 기록

    def reserve(self, user: str, now: int) -> None:
        """예약. 대여 가능 상태에서만 허용된다."""
        # ⚠ 문제: 이 if/elif 사슬과 거의 같은 사슬이 아래 메서드마다 반복된다.
        if self.status == "available":
            self.status = "reserved"
            self.reserved_by, self.reserved_at = user, now
        elif self.status == "reserved":
            raise ValueError("이미 예약된 킥보드입니다")
        elif self.status == "riding":
            raise ValueError("주행 중인 킥보드는 예약할 수 없습니다")
        elif self.status == "low_battery":
            raise ValueError("배터리가 부족합니다")
        elif self.status == "maintenance":
            raise ValueError("정비 중입니다")
        elif self.status == "lost":
            raise ValueError("분실 신고된 킥보드입니다")

    def unlock(self, user: str, now: int) -> None:
        """잠금 해제 = 주행 시작. 이 메서드는 상태가 둘뿐이던 첫 주에 작성되었다."""
        if self.status == "riding":
            raise ValueError("이미 주행 중입니다")
        elif self.status == "reserved" and user != self.reserved_by:
            raise ValueError("다른 사용자가 예약한 킥보드입니다")
        else:
            # ⚠ 문제: 작성 당시 상태는 available/riding 둘뿐이라 else는 곧 available이었다.
            #   이후 low_battery·maintenance·lost가 추가됐지만 이 메서드는 아무도 고치지
            #   않았고, 세 상태 모두 이 else로 흘러 주행이 시작된다. 컴파일러도 테스트도
            #   '분기를 빠뜨렸다'는 사실을 알려 주지 않는다.
            self.status = "riding"
            self.rider, self.ride_started_at = user, now
            # ⚠ 문제: 예약 필드를 지우는 것도 호출자가 기억해야 하는 일이다.
            self.reserved_by = self.reserved_at = None

    def end_ride(self, now: int) -> int:
        """반납. 요금을 계산해 돌려주고, 배터리에 따라 다음 상태를 정한다."""
        if self.status != "riding":
            raise ValueError(f"주행 중이 아닙니다(현재: {self.status})")
        assert self.ride_started_at is not None
        minutes = max(1, (now - self.ride_started_at + 59) // 60)   # 시작한 분은 1분으로 친다
        fare = UNLOCK_FEE + PER_MINUTE * minutes
        self.charges.append((f"{self.rider} 주행 {minutes}분", fare))
        # ⚠ 문제: '반납 후 어디로 가는가'라는 전이 규칙이 요금 계산과 한 덩어리로 섞여 있다.
        self.status = "low_battery" if self.battery < LOW_BATTERY else "available"
        self.rider = self.ride_started_at = None
        return fare

    def tick(self, now: int) -> None:
        """주기적으로 호출되는 시간 이벤트. 예약 만료를 처리한다."""
        # ⚠ 문제: 시간 기반 전이가 생기면서 '상태와 무관한' 정기 작업 안에도 상태 분기가 들어왔다.
        if self.status == "reserved" and self.reserved_at is not None \
                and now - self.reserved_at >= RESERVATION_TTL:
            self.charges.append((f"{self.reserved_by} 노쇼", NO_SHOW_FEE))
            self.status = "available"
            self.reserved_by = self.reserved_at = None

    def update_battery(self, level: int) -> None:
        """배터리 센서 보고. 상태에 따라 전이가 일어나기도 한다."""
        self.battery = level
        if self.status == "available" and level < LOW_BATTERY:
            self.status = "low_battery"
        elif self.status == "low_battery" and level >= LOW_BATTERY:
            self.status = "available"
        # riding/reserved/maintenance/lost에서는 기록만 한다 — 이 '아무것도 안 함'도
        # 사실은 상태별 규칙인데, 코드에는 드러나지 않고 암묵적으로 숨어 있다.

    def send_to_maintenance(self) -> None:
        """정비 입고. 주행 중이거나 예약된 킥보드는 입고할 수 없다."""
        if self.status in ("riding", "reserved"):
            raise ValueError(f"{self.status} 상태에서는 정비 입고할 수 없습니다")
        self.status = "maintenance"

    def finish_maintenance(self) -> None:
        """정비 완료."""
        if self.status != "maintenance":
            raise ValueError("정비 중이 아닙니다")
        self.status = "available" if self.battery >= LOW_BATTERY else "low_battery"

    def report_lost(self) -> None:
        """GPS 신호가 끊긴 킥보드를 분실로 표시한다."""
        # ⚠ 문제: 어떤 상태에서 분실 신고가 가능한지는 기획 문서에만 있고 코드엔 없다.
        #   지금은 아무 상태에서나 lost가 된다 — 주행 중이던 사용자의 요금은 증발한다.
        self.status = "lost"

    def label(self) -> str:
        """앱 지도에 표시할 문구."""
        # ⚠ 문제: 여섯 상태를 다시 한 번 전부 나열한다(reserve의 elif 사슬에 이어 이번엔 dict로).
        #   새 상태를 추가할 때 이 dict를 빠뜨리면 KeyError — 그나마 '시끄럽게' 실패하는 편이다.
        return {
            "available": "대여 가능",
            "reserved": f"예약됨({self.reserved_by})",
            "riding": "주행 중",
            "low_battery": "배터리 부족",
            "maintenance": "정비 중",
            "lost": "분실 신고",
        }[self.status]


if __name__ == "__main__":
    print("[1] 정상 흐름: 예약 → 잠금 해제 → 12분 주행 후 반납")
    s = Scooter("KG-001")
    s.reserve("민지", now=0)
    print("   ", s.label())
    s.unlock("민지", now=120)
    fare = s.end_ride(now=120 + 12 * 60)
    print(f"    반납 요금 {fare:,}원, 상태: {s.label()}")

    print("[2] 시간 기반 전이: 예약 후 10분이 지나면 자동 해제 + 노쇼 수수료")
    s.reserve("도현", now=1_000)
    s.tick(now=1_000 + RESERVATION_TTL)
    print(f"    상태: {s.label()}, 정산 기록: {s.charges[-1]}")

    print("[3] 버그 재현: 정비 중인 킥보드의 잠금을 해제한다")
    s.send_to_maintenance()
    print("    정비 입고 후 상태:", s.label())
    s.unlock("해커", now=2_000)          # 예외가 나야 하지만 나지 않는다
    print("    unlock() 후 상태:", s.label(), "← 정비 중인 기기로 주행이 시작됨!")

    print("[4] 버그 재현: 주행 중 분실 신고 → 요금이 정산되지 않는다")
    s2 = Scooter("KG-002")
    s2.unlock("서윤", now=0)
    s2.report_lost()
    print("    상태:", s2.label(), "/ 정산 기록:", s2.charges, "← 주행 요금 누락")
