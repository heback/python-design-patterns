"""[13장 상태 · 파이썬다운 변형 2] 무상태 상태 객체의 공유, 그리고 `__class__` 교체 트릭.

상황: 킥고가 서울·부산에 킥보드 3만 대를 깔았다. 02 방식은 전이마다 `Available()` 같은
새 상태 객체를 만든다. 대부분의 상태는 필드가 없는데도 말이다. 서진은 두 가지를 검토한다.

A. 무상태(stateless) 상태 객체를 모듈 상수로 하나씩만 만들어 모든 킥보드가 공유한다.
   GoF가 "상태 객체는 흔히 싱글턴"이라고 쓴 바로 그 지점이다. 파이썬에서는 싱글턴 클래스
   (4장)가 필요 없다 — 모듈 수준 상수 하나면 된다. 대가: 상태별 데이터(예약자, 출발 시각)를
   상태 객체에 둘 수 없으므로 Context로 돌아간다.

B. 객체의 `__class__`를 바꿔 '객체 자체가 다른 클래스가 되게' 하는 트릭. 파이썬에서 실제로
   동작하고 코드도 짧지만, 왜 권하지 않는지를 데모로 확인한다.
"""
from __future__ import annotations

import sys
from abc import ABC, abstractmethod


class IllegalTransition(Exception):
    """허용되지 않는 동작."""


# ===========================================================================
# A. 공유되는 무상태 상태 객체
# ===========================================================================

class SharedState(ABC):
    """[State] 필드를 갖지 않는 상태. 그래서 모든 킥보드가 같은 인스턴스를 공유해도 안전하다.

    __slots__ = () 로 인스턴스 속성 추가를 막는다. 누군가 실수로 self.rider = ...를
    쓰면 즉시 AttributeError가 난다. '공유 객체에 개별 데이터를 넣는' 치명적 버그
    (A 킥보드의 탑승자가 B 킥보드에도 보이는)를 언어 수준에서 차단하는 장치다.
    """

    __slots__ = ()

    def unlock(self, scooter: FleetScooter, user: str) -> None:
        """기본은 거부."""
        raise IllegalTransition(f"[{self.label()}] 잠금 해제 불가")

    def end_ride(self, scooter: FleetScooter) -> None:
        """기본은 거부."""
        raise IllegalTransition(f"[{self.label()}] 반납 불가")

    @abstractmethod
    def label(self) -> str:
        """표시 문구."""


class _Available(SharedState):
    """[Concrete State] 대여 가능. 클래스 이름 앞 밑줄: 외부는 클래스가 아니라 아래 상수를 쓰라는 뜻."""

    __slots__ = ()

    def unlock(self, scooter: FleetScooter, user: str) -> None:
        """탑승자는 상태가 아니라 Context에 기록한다 — 공유 객체이므로."""
        scooter.rider = user
        scooter.state = RIDING

    def label(self) -> str:
        """표시 문구."""
        return "대여 가능"


class _Riding(SharedState):
    """[Concrete State] 주행 중."""

    __slots__ = ()

    def end_ride(self, scooter: FleetScooter) -> None:
        """반납. 상태별 데이터 정리 책임이 Context 필드를 만지는 이 코드로 돌아왔다(공유의 대가)."""
        scooter.rider = None
        scooter.state = AVAILABLE

    def label(self) -> str:
        """표시 문구."""
        return "주행 중"


# 모듈 상수 = 파이썬식 '싱글턴'. 모듈은 한 번만 import되므로 인스턴스도 프로세스당 하나다.
# 순환 참조 문제(Available이 RIDING을, Riding이 AVAILABLE을 참조)는 메서드 '실행 시점'에
# 이름을 찾으므로 생기지 않는다 — 클래스 정의 시점에는 아직 상수가 없어도 된다.
AVAILABLE = _Available()
RIDING = _Riding()


class FleetScooter:
    """[Context] 상태 슬롯에는 공유 상수가 들어가고, 개별 데이터는 여기 있다."""

    __slots__ = ("state", "rider")   # 3만 대이므로 Context 쪽도 메모리를 아낀다

    def __init__(self) -> None:
        """대여 가능으로 시작."""
        self.state: SharedState = AVAILABLE
        self.rider: str | None = None

    def unlock(self, user: str) -> None:
        """위임."""
        self.state.unlock(self, user)

    def end_ride(self) -> None:
        """위임."""
        self.state.end_ride(self)


# ===========================================================================
# B. __class__ 교체 트릭 — 동작하지만 권하지 않는다
# ===========================================================================

class ClassSwapScooter:
    """[Context이자 State] 상태 객체를 따로 두지 않고, 객체의 클래스 자체를 바꾼다.

    `self.__class__ = RidingScooter`는 같은 레이아웃의 클래스끼리라면 파이썬이 허용한다.
    위임 코드가 사라져 짧아 보이지만, 아래 데모가 보여 주는 문제가 따라온다.
    """

    def __init__(self, scooter_id: str) -> None:
        """이 생성자는 '처음 만들어질 때' 한 번만 실행된다. 클래스가 바뀌어도 재실행되지 않는다."""
        self.scooter_id = scooter_id

    def unlock(self, user: str) -> None:
        """기본 클래스 = 대여 가능 상태. 잠금 해제하면 자신을 RidingScooter로 '변신'시킨다."""
        self.rider = user                          # 이 속성은 변신 후에도, 반납 후에도 남는다
        self.__class__ = RidingScooter

    def label(self) -> str:
        """표시 문구."""
        return "대여 가능"


class RidingScooter(ClassSwapScooter):
    """[Concrete State] 주행 중 클래스. 상속으로 기본 클래스의 unlock까지 물려받는다는 점에 주의."""

    def end_ride(self) -> None:
        """반납하면 다시 기본 클래스로."""
        self.__class__ = ClassSwapScooter

    def label(self) -> str:
        """표시 문구."""
        return "주행 중"


if __name__ == "__main__":
    print("[A-1] 3만 대의 킥보드가 상태 객체 두 개를 공유한다")
    fleet = [FleetScooter() for _ in range(30_000)]
    fleet[0].unlock("민지")
    distinct = {id(s.state) for s in fleet}
    print(f"    서로 다른 상태 객체 수: {len(distinct)} (킥보드마다 새로 만들었다면 30,000)")
    print(f"    fleet[0]: {fleet[0].state.label()}({fleet[0].rider}) / fleet[1]: {fleet[1].state.label()}")
    print(f"    상태 객체 하나의 크기: {sys.getsizeof(AVAILABLE)}바이트 (__slots__ = () 덕분에 __dict__ 없음)")

    print("[A-2] 공유 상태 객체에 개별 데이터를 넣으려는 실수는 즉시 막힌다")
    try:
        RIDING.rider = "도현"   # type: ignore[attr-defined]
    except AttributeError as e:
        print("    AttributeError:", e)

    print("[B-1] __class__ 교체: 동작은 한다")
    k = ClassSwapScooter("KG-777")
    print("    처음:", k.label(), type(k).__name__)
    k.unlock("서윤")
    print("    잠금 해제 후:", k.label(), type(k).__name__)

    print("[B-2] 문제 1 — 객체의 '타입'이 수명 중에 바뀐다")
    registry = {type(k): [k]}                      # 예: 타입별로 묶어 둔 캐시/디스패치 표
    k.end_ride()
    print(f"    반납 후 type(k) = {type(k).__name__}, 그런데 캐시 키는 {list(registry)[0].__name__}")

    print("[B-3] 문제 2 — 이전 상태의 데이터가 남는다(01의 찌꺼기 문제 재발)")
    print(f"    대여 가능 상태인데 k.rider = {k.rider!r}")

    print("[B-4] 문제 3 — 상속 때문에 '주행 중 잠금 해제'가 조용히 허용된다")
    k.unlock("서윤")
    k.unlock("해커")                               # RidingScooter가 unlock을 물려받았다
    print(f"    주행 중 두 번째 unlock 결과: {k.label()}, 탑승자 {k.rider!r} ← 예외 없음")
