"""04 싱글턴 — 패턴 코드: AuditLogger()를 어디서 부르든 같은 객체가 나온다.

상황: 순진한 코드에서는 모듈마다 기록기를 만들어 체인이 갈라졌다. 태윤은 싱글턴으로
유일성을 강제했다. 앞부분은 유일성 구현, 뒷부분은 그 대가(숨은 의존성, 테스트 간섭)다.
[Singleton] AuditLogger
"""
from __future__ import annotations

import threading


class AuditLogger:
    """[Singleton] 인스턴스가 하나임을 클래스 스스로 보장한다."""

    _instance: AuditLogger | None = None
    _lock = threading.Lock()  # 서버 재시작 직후 두 요청이 동시에 '처음' 만드는 것을 막는다

    def __new__(cls) -> AuditLogger:
        """객체를 할당하는 단계에서 유일성을 통제한다. 있으면 기존 객체를 돌려준다."""
        with cls._lock:  # 검사와 대입 사이에 다른 스레드가 끼어들지 못하게 한다
            if cls._instance is None:
                cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """AuditLogger()를 부를 때마다 __init__은 '다시' 불린다(__new__가 기존 객체를 줘도).

        가드가 없으면 새 모듈이 AuditLogger()를 부를 때마다 기록이 초기화된다.
        """
        if getattr(self, "_initialized", False):
            return
        self.entries: list[str] = []
        self._initialized = True

    def record(self, who: str, action: str) -> None:
        """기록을 덧붙인다. 기록기가 하나이므로 체인도 하나다."""
        self.entries.append(f"{who} {action}")


class PrescriptionModule:
    """처방 모듈. 시그니처 어디에도 감사 로그가 보이지 않는다."""

    def prescribe(self, doctor: str) -> None:
        """⚠ 숨은 의존성: 본문을 읽어야만 전역 기록기에 쓴다는 것을 안다."""
        AuditLogger().record(doctor, "처방")


def test_one_entry(name: str) -> None:
    """'처방 한 번에 기록 한 줄'을 확인하는 테스트. 혼자 돌리면 통과한다."""
    PrescriptionModule().prescribe(name)
    count = len(AuditLogger().entries)
    print(f"  {name}: 기록 {count}줄 → {'통과' if count == 1 else '실패'}")


if __name__ == "__main__":
    print("[1] 몇 번을 부르든 같은 객체 — 체인은 하나다")
    print("  같은 객체인가:", AuditLogger() is AuditLogger())

    print("[2] 같은 프로세스의 두 테스트가 싱글턴을 공유한다")
    test_one_entry("테스트A")
    test_one_entry("테스트B")  # A가 남긴 기록까지 보인다 — 결과가 실행 순서에 달렸다

    print("[3] 그래서 운영 코드에 '리셋 뒷문'을 달라는 요청이 온다")
    AuditLogger._instance = None  # 유일한 인스턴스를 지우는 뒷문. 증상만 가린다.
    test_one_entry("테스트B")
