"""파이썬의 싱글턴 구현 비교: 잠금 없는 __new__의 경쟁, 메타클래스, Borg, 모듈 객체, functools.cache.

상황: 02_singleton.py의 이중 검사 잠금을 리뷰하던 동료 수아가 물었다. "잠금이 정말 필요해요?
그리고 파이썬에선 싱글턴을 만드는 방법이 너무 많던데, 뭐가 달라요?" 이 파일은 그 질문에
실험으로 답한다. 감사 로그 기록기를 단순화한 클래스들로 각 방식의 성질을 비교한다.

비교 축:
- 유일성을 '무엇이' 보장하는가 (클래스 자신 / 메타클래스 / import 캐시 / 함수 캐시)
- 하위 클래스·테스트에서 교체할 수 있는가
- 정체성(identity)이 하나인가, 상태(state)만 공유하는가 (Borg)
"""
from __future__ import annotations

import threading
import time
from functools import cache
from typing import Any


# ---------------------------------------------------------------------------
# 1. 잠금 없는 __new__: '검사 후 대입' 사이의 틈
# ---------------------------------------------------------------------------

class UnsafeLogger:
    """[Singleton, 결함 있음] 잠금 없이 None 검사만 하는 구현."""

    _instance: UnsafeLogger | None = None

    def __new__(cls) -> UnsafeLogger:
        """검사와 대입 사이에 다른 스레드가 끼어들 수 있다.

        실제 초기화(파일 열기, 체인 마지막 해시 읽기)는 I/O라서 이 틈이 현실에서도 생긴다.
        sleep은 그 I/O 시간을 흉내 내 경쟁을 재현 가능하게 만든다.
        """
        if cls._instance is None:
            time.sleep(0.01)  # 초기화 I/O를 흉내 냄 — 이 사이에 다른 스레드도 None을 본다
            cls._instance = super().__new__(cls)
        return cls._instance


class SafeLogger:
    """[Singleton] 02와 같은 이중 검사 잠금."""

    _instance: SafeLogger | None = None
    _lock = threading.Lock()

    def __new__(cls) -> SafeLogger:
        """잠금 안에서 다시 검사하므로 틈이 닫힌다."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    time.sleep(0.01)
                    cls._instance = super().__new__(cls)
        return cls._instance


def count_instances(factory: Any, n: int = 8) -> int:
    """n개 스레드가 '동시에' factory()를 불렀을 때 서로 다른 인스턴스가 몇 개 나오는지 센다."""
    barrier = threading.Barrier(n)  # 모든 스레드를 출발선에 세웠다가 한꺼번에 출발시킨다
    # id가 아니라 객체 자체를 모은다. 경쟁에서 진 객체는 _instance가 덮어써지는 순간 해제될 수 있고,
    # CPython은 해제된 주소를 재사용하므로 id만 모으면 서로 다른 인스턴스가 같은 id로 세어질 수 있다.
    seen: list[object] = []

    def worker() -> None:
        """출발 신호를 기다렸다가 인스턴스를 얻는다."""
        barrier.wait()
        seen.append(factory())

    threads = [threading.Thread(target=worker) for _ in range(n)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    return len({id(o) for o in seen})  # 모든 객체가 seen에 살아 있으므로 id가 유일하다


# ---------------------------------------------------------------------------
# 2. 메타클래스 싱글턴: 유일성 로직을 클래스 밖으로
# ---------------------------------------------------------------------------

class SingletonMeta(type):
    """클래스의 '호출'(Cls())을 가로채는 메타클래스.

    __new__ 방식과 달리 __init__ 재호출 함정이 없다: 이미 있으면 type.__call__ 자체를
    건너뛰므로 __new__도 __init__도 다시 불리지 않는다. 대가는 메타클래스라는 무거운 도구와,
    ABCMeta 같은 다른 메타클래스와 섞을 때의 충돌이다.
    """

    _instances: dict[type, Any] = {}
    _lock = threading.Lock()

    def __call__(cls, *args: Any, **kwargs: Any) -> Any:
        """클래스마다 인스턴스 하나. 하위 클래스는 자기 몫의 인스턴스를 따로 가진다."""
        with SingletonMeta._lock:
            if cls not in SingletonMeta._instances:
                SingletonMeta._instances[cls] = super().__call__(*args, **kwargs)
        return SingletonMeta._instances[cls]


class MetaLogger(metaclass=SingletonMeta):
    """[Singleton] 메타클래스로 유일성을 얻은 기록기."""

    def __init__(self) -> None:
        """첫 생성 때 한 번만 실행된다(가드 불필요)."""
        self.entries: list[str] = []


# ---------------------------------------------------------------------------
# 3. Borg(Monostate): 인스턴스는 여럿, 상태는 하나
# ---------------------------------------------------------------------------

class BorgLogger:
    """[Borg] 모든 인스턴스가 같은 __dict__를 공유한다. Alex Martelli가 제안한 관용구.

    '정체성이 하나인 것'이 아니라 '상태가 하나인 것'이 진짜 요구라면 이것으로 충분하다는 주장이다.
    is 비교는 False지만 동작은 같다. 하위 클래스가 자기 공유 상태를 가지게 하기 쉽다는 장점이 있다.
    """

    _shared_state: dict[str, Any] = {}

    def __init__(self) -> None:
        """인스턴스의 속성 저장소를 클래스 수준의 dict 하나로 바꿔치기한다."""
        self.__dict__ = self._shared_state
        # self.entries = []로 쓰면 안 된다: Borg도 BorgLogger()마다 __init__이 다시 불리고,
        # 이제 그 대입은 '공유' 상태를 덮어써 모든 인스턴스의 기록을 지운다. setdefault는 처음에만 채운다.
        self.__dict__.setdefault("entries", [])


# ---------------------------------------------------------------------------
# 4. 모듈 수준 객체 / 5. functools.cache 접근 함수
# ---------------------------------------------------------------------------

class PlainLogger:
    """평범한 클래스. 유일성 로직이 전혀 없다 — 테스트에서는 자유롭게 여러 개 만들 수 있다."""

    def __init__(self) -> None:
        """기록 목록."""
        self.entries: list[str] = []


# 모듈은 첫 import 때 한 번만 실행되고 sys.modules에 캐시된다. 그래서 이 줄은 프로세스에서
# 한 번만 실행되고, `from audit import audit_logger`는 어디서든 같은 객체를 준다.
# 파이썬에서 가장 흔하고 가장 덜 놀라운 '싱글턴'이다. 단, 생성 시점이 import 시점으로 고정된다.
audit_logger = PlainLogger()


@cache
def get_audit_logger() -> PlainLogger:
    """지연 생성 접근 함수. 첫 호출 때 만들고 이후 같은 객체를 돌려준다.

    모듈 객체와 달리 import만으로는 생성되지 않는다(설정을 읽은 뒤 만들어야 할 때 유용).
    테스트에서는 get_audit_logger.cache_clear()로 비울 수 있는데, 이것도 결국 전역 리셋이라는
    점에서 02의 _reset_for_tests와 같은 냄새를 풍긴다.
    """
    return PlainLogger()


if __name__ == "__main__":
    print("[1] 8개 스레드가 동시에 처음 생성할 때 만들어진 인스턴스 수")
    unsafe = count_instances(UnsafeLogger)
    # Barrier와 sleep 때문에 대개 8개 스레드가 모두 따로 만든다. 다만 스케줄링에 달린 일이라
    # 보장은 아니므로, 출력이 실행마다 같도록 '2개 이상인가'만 보인다.
    print(f"  UnsafeLogger 인스턴스가 2개 이상 생겼나? {unsafe >= 2}  ← 싱글턴이 깨졌다")
    print(f"  SafeLogger  인스턴스 수: {count_instances(SafeLogger)}")

    print("\n[2] 메타클래스: __init__이 다시 불리지 않는다")
    MetaLogger().entries.append("dr.kim 처방")
    print(f"  MetaLogger() is MetaLogger() → {MetaLogger() is MetaLogger()}, 기록 유지: {MetaLogger().entries}")

    print("\n[3] Borg: 다른 객체, 같은 상태")
    b1, b2 = BorgLogger(), BorgLogger()
    b1.entries.append("lab.lee 열람")
    print(f"  b1 is b2 → {b1 is b2}, b2.entries → {b2.entries}")
    b3 = BorgLogger()  # __init__이 다시 불려도 setdefault 덕분에 공유 기록이 지워지지 않는다
    print(f"  세 번째 BorgLogger() 뒤에도 b3.entries → {b3.entries}")

    print("\n[4] 모듈 객체와 cache 접근 함수: 클래스는 평범하고 '하나'는 관례로 보장된다")
    print(f"  get_audit_logger() is get_audit_logger() → {get_audit_logger() is get_audit_logger()}")
    print(f"  그래도 테스트는 PlainLogger()를 자유롭게 새로 만든다 → {PlainLogger() is not audit_logger}")
