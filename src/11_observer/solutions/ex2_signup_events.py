"""연습문제 2 해설: 회원가입 함수가 직접 부르던 후속 작업을 옵저버로 분리한다.

상황: 원래 sign_up()은 회원 저장 뒤 환영 메일·쿠폰 발급·통계 기록을 차례로 직접 호출했다.
마케팅팀이 후속 작업을 추가할 때마다 회원가입이라는 핵심 흐름을 수정해야 했고, 메일
서버가 느리거나 실패하면 가입 자체가 실패했다.

해결: sign_up()은 '회원이 가입했다'는 사실만 통지하고, 후속 작업은 구독자가 된다.
구독자는 콜러블로 충분하다 — 상태가 없는 한 줄짜리 반응에 Observer 클래스는 과하다.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class UserSignedUp:
    """통지 메시지(도메인 이벤트). 과거형 이름: '일어난 사실'을 알릴 뿐, 무엇을 하라고 시키지 않는다."""

    user_id: int
    email: str
    # 추천인 포인트 구독자를 위해 추가한 필드. 구독자 추가는 sign_up()의 '흐름'을 건드리지
    # 않지만, 새 구독자가 필요로 하는 '사실'이 이벤트에 없으면 이벤트 스키마는 넓혀야 한다.
    # 기본값 None을 둔 덕분에 기존 구독자와 발행 코드는 깨지지 않는다(하위 호환).
    referrer_id: int | None = None


Listener = Callable[[UserSignedUp], None]


class SignupEvents:
    """[Subject] 가입 이벤트 구독 목록. 회원 서비스는 구독자가 누구인지 모른다."""

    def __init__(self) -> None:
        """구독자 목록."""
        self._listeners: list[Listener] = []

    def subscribe(self, fn: Listener) -> Listener:
        """구독. 함수를 그대로 돌려주므로 @events.subscribe 데코레이터로도 쓸 수 있다."""
        self._listeners.append(fn)
        return fn

    def publish(self, event: UserSignedUp) -> None:
        """통지. 후속 작업 하나의 실패가 가입 자체나 다른 후속 작업을 막지 않게 격리한다."""
        for fn in list(self._listeners):
            try:
                fn(event)
            except Exception as exc:  # noqa: BLE001 — 격리가 목적
                print(f"    !! {fn.__name__} 실패(가입은 유지됨): {exc}")


events = SignupEvents()
USERS: dict[int, str] = {}


def sign_up(email: str, referrer_id: int | None = None) -> int:
    """회원가입. 이제 이 함수의 변경 이유는 '가입 규칙'뿐이다(SRP).

    referrer_id는 가입 폼이 받는 '가입 사실'의 일부라서 여기로 들어온다. 포인트를
    어떻게 줄지는 이 함수가 모른다 — 사실을 이벤트에 실어 보낼 뿐이다.
    """
    user_id = len(USERS) + 1
    USERS[user_id] = email
    print(f"    회원 {user_id} 저장: {email}")
    events.publish(UserSignedUp(user_id, email, referrer_id))   # 후속 작업을 부르지 않고 '알린다'
    return user_id


# --- 구독자들: 각 팀의 모듈에 있을 코드. sign_up()을 수정하지 않고 추가된다(OCP). ---
@events.subscribe
def send_welcome_mail(e: UserSignedUp) -> None:
    """[Concrete Observer] 환영 메일. 데모를 위해 특정 도메인에서 실패한다."""
    if e.email.endswith("@down.example"):
        raise ConnectionError("SMTP 타임아웃")
    print(f"    환영 메일 → {e.email}")


@events.subscribe
def issue_coupon(e: UserSignedUp) -> None:
    """[Concrete Observer] 신규 가입 쿠폰."""
    print(f"    쿠폰 발급 → 회원 {e.user_id}")


@events.subscribe
def record_stats(e: UserSignedUp) -> None:
    """[Concrete Observer] 가입 통계."""
    print(f"    통계 +1 (누적 {len(USERS)})")


@events.subscribe
def award_referral_points(e: UserSignedUp) -> None:
    """[Concrete Observer] 마케팅팀의 새 요구: 추천인 포인트. 추천인 없는 가입은 무시한다."""
    if e.referrer_id is None:
        return
    print(f"    추천인 {e.referrer_id}에게 1,000포인트")


if __name__ == "__main__":
    print("[1] 정상 가입")
    sign_up("mina@example.com")
    print("[2] 메일 서버 장애 — 가입·쿠폰·통계는 계속된다")
    sign_up("joon@down.example")
    print("[3] 회원 1의 추천으로 가입 — 추천인 포인트 구독자가 반응")
    sign_up("hana@example.com", referrer_id=1)
