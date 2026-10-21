"""연습문제 1 해설: __new__ 싱글턴에서 __init__이 매번 다시 불려 상태가 초기화되는 버그.

상황: 태윤의 첫 싱글턴 초안에는 02_singleton.py의 _initialized 가드가 없었다. 처방 모듈이
기록을 남긴 뒤 검사 모듈이 처음으로 AuditLogger()를 부르자, 앞서 쌓인 기록이 사라졌다.
"인스턴스는 분명 하나인데 왜 기록이 지워지는가?" — 이 파일은 그 버그를 재현하고 원인을 보인다.

원인 요약: 클래스 호출 Cls()는 type.__call__이 처리하며, 그 동작은 대략
    obj = Cls.__new__(Cls); if isinstance(obj, Cls): obj.__init__()
이다. __new__가 '이미 있던' 객체를 돌려줘도 그것이 Cls의 인스턴스이므로 __init__이 다시 불린다.
"""
from __future__ import annotations


class BuggyAuditLogger:
    """[Singleton, 결함 있음] __init__ 가드가 없는 __new__ 싱글턴."""

    _instance: BuggyAuditLogger | None = None

    def __new__(cls) -> BuggyAuditLogger:
        """유일성은 지킨다 — 문제는 여기가 아니다."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """AuditLogger()가 불릴 때마다 실행되어 entries를 빈 리스트로 갈아 끼운다."""
        self.entries: list[str] = []


class GuardedAuditLogger:
    """[Singleton] 해결 1: 첫 초기화 여부를 플래그로 기억한다(02_singleton.py의 방식)."""

    _instance: GuardedAuditLogger | None = None

    def __new__(cls) -> GuardedAuditLogger:
        """BuggyAuditLogger와 같다."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """두 번째 호출부터는 즉시 반환한다."""
        if getattr(self, "_initialized", False):
            return
        self.entries: list[str] = []
        self._initialized = True


class NewOnlyAuditLogger:
    """[Singleton] 해결 2: 상태 초기화를 __new__ 안의 '최초 생성' 분기로 옮기고 __init__을 두지 않는다.

    __init__을 정의하지 않으면 object.__init__이 불리고, 그것은 아무 일도 하지 않는다.
    """

    _instance: NewOnlyAuditLogger | None = None
    entries: list[str]

    def __new__(cls) -> NewOnlyAuditLogger:
        """처음 만들 때만 상태를 초기화한다."""
        if cls._instance is None:
            inst = super().__new__(cls)
            inst.entries = []
            cls._instance = inst
        return cls._instance


if __name__ == "__main__":
    for cls in (BuggyAuditLogger, GuardedAuditLogger, NewOnlyAuditLogger):
        cls().entries.append("dr.kim 처방 발행")  # 처방 모듈이 기록
        same = cls() is cls()                       # 검사 모듈이 처음 AuditLogger()를 부름
        print(f"{cls.__name__:20} 같은 인스턴스? {same}  남은 기록: {cls().entries}")
