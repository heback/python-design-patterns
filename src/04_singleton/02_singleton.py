"""싱글턴 적용: AuditLogger()를 몇 번 부르든 같은 인스턴스 — 체인은 고쳐지지만 새 고통이 생긴다.

상황: 01_naive.py에서 모듈마다 AuditLogger를 만들자 해시 체인이 갈라졌다. 태윤은 GoF 싱글턴을
적용했다. 이제 어느 모듈에서 AuditLogger()를 불러도 같은 객체가 나온다. 1차 고통(인스턴스 중복)은
해결된다. 그런데 몇 주 뒤 QA 팀이 모듈별 단위 테스트를 돌리면서 2차 고통이 드러났다.

GoF 의도(intent): "클래스의 인스턴스가 오직 하나임을 보장하고, 그 인스턴스에 대한
전역적인 접근점을 제공한다." — 이 문장에는 요구가 '둘' 들어 있다는 점에 주목하라.
(1) 유일성: 인스턴스가 하나여야 한다.  (2) 전역 접근: 어디서든 그것을 얻을 수 있다.
이 파일의 후반부는 (2)가 만드는 비용을 보여준다.

역할 대응: [Singleton] AuditLogger
"""
from __future__ import annotations

import hashlib
import threading
from dataclasses import dataclass

GENESIS = "0" * 16


@dataclass(frozen=True)
class AuditEntry:
    """감사 기록 한 줄(불변)."""

    actor: str
    action: str
    patient_id: str
    prev_hash: str
    hash: str


def digest(prev_hash: str, actor: str, action: str, patient_id: str) -> str:
    """직전 해시와 내용을 함께 해싱한다."""
    return hashlib.sha256(f"{prev_hash}|{actor}|{action}|{patient_id}".encode()).hexdigest()[:16]


class AuditLogger:
    """[Singleton] 프로세스 전체에서 하나뿐인 감사 로그 기록기.

    __new__를 재정의한 이유: 파이썬에서 AuditLogger()는 먼저 __new__로 객체를 '할당'하고
    그다음 __init__으로 '초기화'한다. 유일성은 할당 단계에서 통제해야 한다.
    """

    _instance: AuditLogger | None = None
    # 잠금 하나를 두 용도로 쓴다: (1) 멀티스레드 웹 서버에서 두 요청이 동시에 처음 생성하는 경쟁 방지,
    # (2) record()의 기록 순서 직렬화. threading.Lock은 재진입이 안 되므로, record() 안에서
    # 잠금을 쥔 채 AuditLogger()를 부르는 코드가 생기면 교착한다 — 분리하려면 인스턴스 잠금을 따로 둔다.
    _lock = threading.Lock()

    def __new__(cls) -> AuditLogger:
        """이중 검사 잠금(double-checked locking).

        바깥 검사: 이미 만들어졌다면 잠금 비용 없이 바로 돌려준다(대부분의 호출이 여기서 끝난다).
        안쪽 검사: 잠금을 기다리는 동안 다른 스레드가 먼저 만들었을 수 있으므로 다시 확인한다.
        CPython의 GIL이 있어도 '검사 후 대입' 사이에 스레드 전환이 일어날 수 있어 잠금이 필요하다.
        """
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """함정: __new__가 같은 객체를 돌려줘도 파이썬은 AuditLogger()마다 __init__을 '다시' 부른다.

        가드 없이 self.entries = []를 쓰면 새 모듈이 AuditLogger()를 부를 때마다 체인이 초기화된다.
        _initialized 플래그로 첫 호출만 통과시킨다(연습문제 1에서 이 버그를 재현한다).
        """
        if getattr(self, "_initialized", False):
            return
        self.entries: list[AuditEntry] = []
        self._last_hash = GENESIS
        self._initialized = True

    def record(self, actor: str, action: str, patient_id: str) -> None:
        """기록 한 줄을 체인에 잇는다. 여러 스레드가 동시에 쓰면 체인이 꼬이므로 잠근다."""
        with self._lock:
            h = digest(self._last_hash, actor, action, patient_id)
            self.entries.append(AuditEntry(actor, action, patient_id, self._last_hash, h))
            self._last_hash = h

    def verify(self) -> list[int]:
        """체인 무결성을 검사해 어긋난 줄 번호를 돌려준다."""
        broken, expected = [], GENESIS
        for i, e in enumerate(self.entries):
            if e.prev_hash != expected or e.hash != digest(e.prev_hash, e.actor, e.action, e.patient_id):
                broken.append(i)
            expected = e.hash
        return broken

    @classmethod
    def _reset_for_tests(cls) -> None:
        """⚠ 냄새: 테스트를 위해 운영 코드에 '유일한 인스턴스를 지우는' 뒷문을 만들었다.

        이 메서드가 필요하다는 것 자체가 싱글턴이 테스트 격리를 깨뜨린다는 증거다.
        게다가 스레드 기반 병렬 테스트에서는 한 테스트가 리셋하는 순간 같은 프로세스의 다른 테스트 로그가
        사라진다(pytest-xdist처럼 프로세스로 나누는 러너에서는 워커마다 싱글턴이 따로 있다).
        """
        cls._instance = None


# ---------------------------------------------------------------------------
# 진료 모듈 — 01과 똑같이 AuditLogger()를 부르지만, 이제 모두 같은 객체를 얻는다.
# ---------------------------------------------------------------------------

class PrescriptionModule:
    """처방 모듈."""

    def prescribe(self, doctor: str, patient_id: str) -> None:
        """⚠ 숨은 의존성: 시그니처만 봐서는 이 메서드가 전역 감사 로그에 쓴다는 것을 알 수 없다.

        생성자에도 인자에도 AuditLogger가 등장하지 않는다. 의존성이 메서드 본문 깊숙이 숨어 있어
        호출자도, 테스트도 이것을 다른 것으로 바꿀 수 없다(DIP와의 충돌: 구체 클래스에 정적 의존).
        """
        AuditLogger().record(doctor, "처방 발행", patient_id)


class LabModule:
    """검사 모듈."""

    def view_result(self, staff: str, patient_id: str) -> None:
        """검사 결과 열람을 기록한다(같은 숨은 의존성)."""
        AuditLogger().record(staff, "검사 결과 열람", patient_id)


def test_prescription_writes_one_entry() -> bool:
    """QA의 단위 테스트 A: 처방 한 번에 감사 기록 한 줄."""
    PrescriptionModule().prescribe("dr.test", "P-T1")
    return len(AuditLogger().entries) == 1


def test_lab_writes_one_entry() -> bool:
    """QA의 단위 테스트 B: 검사 열람 한 번에 감사 기록 한 줄. 테스트 A와 '독립적'이어야 한다."""
    LabModule().view_result("lab.test", "P-T2")
    return len(AuditLogger().entries) == 1


if __name__ == "__main__":
    print("[1] 1차 고통 해결: 어디서 불러도 같은 인스턴스, 체인은 하나")
    PrescriptionModule().prescribe("dr.kim", "P-1001")
    LabModule().view_result("lab.lee", "P-1001")
    PrescriptionModule().prescribe("dr.kim", "P-2002")
    print(f"  AuditLogger() is AuditLogger() → {AuditLogger() is AuditLogger()}")
    print(f"  기록 {len(AuditLogger().entries)}줄, 어긋난 기록: {AuditLogger().verify()}")

    print("\n[2] 2차 고통: QA가 테스트 A, B를 같은 프로세스에서 차례로 실행한다")
    AuditLogger._reset_for_tests()  # 위 [1]의 흔적을 지우고 시작(이 줄 자체가 냄새)
    print(f"  테스트 A 통과? {test_prescription_writes_one_entry()}")
    print(f"  테스트 B 통과? {test_lab_writes_one_entry()}  ← A가 남긴 기록이 B에 보인다")
    print("  테스트 순서를 바꾸면 이번엔 A가 실패한다 — 결과가 '실행 순서'에 의존한다.")

    print("\n[3] 리셋 훅으로 땜질하면")
    AuditLogger._reset_for_tests()
    a = test_prescription_writes_one_entry()
    AuditLogger._reset_for_tests()
    b = test_lab_writes_one_entry()
    print(f"  A={a}, B={b} — 통과는 하지만, 운영 코드에 테스트용 뒷문이 생겼고")
    print("  스레드 병렬 실행에서는 한 테스트의 리셋이 같은 프로세스의 다른 테스트 상태를 지운다.")
