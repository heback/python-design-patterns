"""순진한 설계: 모듈마다 AuditLogger()를 새로 만들자 감사 로그의 해시 체인이 갈라진다.

상황: 한결종합병원 의료정보팀 개발자 태윤은 "누가 언제 어떤 환자 기록을 열람·수정했는가"를
법적 요건에 맞게 남기는 AuditLogger를 만들었다. 위·변조를 탐지하려고 각 기록에 직전 기록의
해시를 넣는 해시 체인(hash chain)으로 한 파일에 순서대로 쓴다. 처음에는 처방 모듈 하나만
썼다. 이어 검사(Lab)·원무(Billing) 모듈도 감사 로그를 남겨야 했고, 각 모듈 개발자는
자연스럽게 자기 코드에서 AuditLogger()를 생성했다.

읽을 때 주목할 점:
- 해시 체인의 정합성은 '마지막 해시'라는 상태에 달려 있고, 그 상태는 인스턴스마다 따로 있다.
- 세 인스턴스가 같은 파일에 번갈아 쓰면 각 기록의 prev_hash가 실제 직전 기록을 가리키지 않는다.
- 위·변조가 전혀 없었는데도 무결성 검증이 실패한다 — 감사 로그로서의 가치가 사라진다.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass

GENESIS = "0" * 16  # 체인의 첫 기록이 가리키는 가상의 '직전 해시'

# 실제로는 append-only 파일(/var/log/emr/audit.log). 예제에서는 모듈 전역 리스트로 흉내 낸다.
AUDIT_FILE: list[AuditEntry] = []


@dataclass(frozen=True)
class AuditEntry:
    """감사 기록 한 줄. frozen인 이유: 기록은 쓰인 뒤 절대 바뀌면 안 된다(법적 요건)."""

    actor: str
    action: str
    patient_id: str
    prev_hash: str
    hash: str


def digest(prev_hash: str, actor: str, action: str, patient_id: str) -> str:
    """직전 해시와 내용을 함께 해싱한다. 어느 한 줄이라도 고치면 뒤의 모든 해시가 어긋난다."""
    raw = f"{prev_hash}|{actor}|{action}|{patient_id}".encode()
    return hashlib.sha256(raw).hexdigest()[:16]  # 예제 출력을 짧게 하려고 앞 16자만 쓴다


class AuditLogger:
    """감사 로그 기록기. 체인의 '마지막 해시'를 인스턴스 상태로 들고 있다."""

    def __init__(self) -> None:
        """⚠ 문제: 생성될 때마다 체인이 처음(GENESIS)부터 시작한다고 믿는다.
        파일에는 이미 다른 인스턴스가 쓴 기록이 있는데도 그것을 모른다.
        """
        self._last_hash = GENESIS

    def record(self, actor: str, action: str, patient_id: str) -> None:
        """기록 한 줄을 체인에 이어 쓴다."""
        h = digest(self._last_hash, actor, action, patient_id)
        AUDIT_FILE.append(AuditEntry(actor, action, patient_id, self._last_hash, h))
        self._last_hash = h


def verify_chain(entries: list[AuditEntry]) -> list[int]:
    """각 기록의 prev_hash가 '파일상 직전 기록'의 hash와 같은지 본다. 어긋난 줄 번호를 돌려준다."""
    broken = []
    expected = GENESIS
    for i, e in enumerate(entries):
        if e.prev_hash != expected or e.hash != digest(e.prev_hash, e.actor, e.action, e.patient_id):
            broken.append(i)
        expected = e.hash
    return broken


# ---------------------------------------------------------------------------
# 각 진료 모듈 — 서로 다른 팀이 작성했다.
# ---------------------------------------------------------------------------

class PrescriptionModule:
    """처방 모듈."""

    def __init__(self) -> None:
        """⚠ 문제: 모듈마다 자기 AuditLogger를 만든다. 각자는 '올바르게' 동작한다."""
        self.audit = AuditLogger()

    def prescribe(self, doctor: str, patient_id: str) -> None:
        """처방을 내리고 감사 기록을 남긴다."""
        self.audit.record(doctor, "처방 발행", patient_id)


class LabModule:
    """검사 모듈."""

    def __init__(self) -> None:
        """두 번째 AuditLogger."""
        self.audit = AuditLogger()

    def view_result(self, staff: str, patient_id: str) -> None:
        """검사 결과 열람을 기록한다."""
        self.audit.record(staff, "검사 결과 열람", patient_id)


class BillingModule:
    """원무 모듈."""

    def __init__(self) -> None:
        """세 번째 AuditLogger."""
        self.audit = AuditLogger()

    def view_record(self, clerk: str, patient_id: str) -> None:
        """원무 담당자의 진료 기록 열람을 기록한다."""
        self.audit.record(clerk, "진료 기록 열람", patient_id)


if __name__ == "__main__":
    rx, lab, billing = PrescriptionModule(), LabModule(), BillingModule()

    print("[1] 세 모듈이 번갈아 감사 기록을 남긴다")
    rx.prescribe("dr.kim", "P-1001")
    lab.view_result("lab.lee", "P-1001")
    billing.view_record("clerk.park", "P-1001")
    rx.prescribe("dr.kim", "P-2002")
    for i, e in enumerate(AUDIT_FILE):
        print(f"  #{i} {e.actor:10} {e.action:10} prev={e.prev_hash} hash={e.hash}")

    print("\n[2] 위·변조가 전혀 없었는데 무결성 검증 결과는")
    print(f"  어긋난 기록: {verify_chain(AUDIT_FILE)}  (#1, #2는 GENESIS를, #3은 #0을 가리킨다)")
    print("  → 체인이 모듈 수만큼 갈라졌다. 감사에서 '변조 의심'으로 판정된다.")
