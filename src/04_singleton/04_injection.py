"""더 나은 대안: 싱글턴 대신 composition root에서 '하나만 만들어' 생성자로 주입한다.

상황: 02_singleton.py의 싱글턴은 해시 체인 분기(1차 고통)를 해결했지만 숨은 의존성, 테스트 오염,
테스트용 리셋 뒷문(2차 고통)을 만들었다. 태윤은 GoF 의도의 두 요구를 분리했다.
- 유일성("기록기는 하나여야 한다") → 애플리케이션을 조립하는 단 한 곳(composition root)이 책임진다.
- 전역 접근("어디서든 얻는다") → 버린다. 필요한 객체는 생성자로 받는다.
AuditLogger는 평범한 클래스로 돌아가고, 테스트는 자기만의 기록기를 마음대로 만든다.
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
    """평범한 클래스. 유일성 로직(__new__, _instance, 리셋 훅)이 전부 사라졌다.

    '몇 개 만들어도 되는가'는 이 클래스가 결정할 문제가 아니라 이 클래스를 '쓰는 애플리케이션'이
    결정할 문제라는 관점이다. 운영 앱은 하나, 테스트는 테스트마다 하나.
    """

    def __init__(self) -> None:
        """__init__ 재호출 함정도 없다 — 생성자는 평범하게 한 번 불린다."""
        self.entries: list[AuditEntry] = []
        self._last_hash = GENESIS
        self._lock = threading.Lock()  # 기록 순서 보호는 여전히 필요하다(인스턴스 하나를 여러 스레드가 공유)

    def record(self, actor: str, action: str, patient_id: str) -> None:
        """기록 한 줄을 체인에 잇는다."""
        with self._lock:
            h = digest(self._last_hash, actor, action, patient_id)
            self.entries.append(AuditEntry(actor, action, patient_id, self._last_hash, h))
            self._last_hash = h

    def verify(self) -> list[int]:
        """체인 무결성 검사."""
        broken, expected = [], GENESIS
        for i, e in enumerate(self.entries):
            if e.prev_hash != expected or e.hash != digest(e.prev_hash, e.actor, e.action, e.patient_id):
                broken.append(i)
            expected = e.hash
        return broken


class PrescriptionModule:
    """처방 모듈. 의존성이 생성자 시그니처에 드러난다."""

    def __init__(self, audit: AuditLogger) -> None:
        """'이 모듈은 감사 로그에 쓴다'는 사실이 이제 문서가 아니라 시그니처로 표현된다."""
        self.audit = audit

    def prescribe(self, doctor: str, patient_id: str) -> None:
        """처방을 내리고 기록한다."""
        self.audit.record(doctor, "처방 발행", patient_id)


class LabModule:
    """검사 모듈."""

    def __init__(self, audit: AuditLogger) -> None:
        """감사 기록기를 주입받는다."""
        self.audit = audit

    def view_result(self, staff: str, patient_id: str) -> None:
        """검사 결과 열람을 기록한다."""
        self.audit.record(staff, "검사 결과 열람", patient_id)


@dataclass
class EmrApp:
    """조립된 애플리케이션. 어떤 모듈들이 어떤 공유 객체를 쓰는지 한눈에 보인다."""

    audit: AuditLogger
    prescription: PrescriptionModule
    lab: LabModule


def build_app() -> EmrApp:
    """[Composition Root] 프로그램 시작 시 단 한 번 호출되어 객체 그래프를 조립한다.

    유일성 보장은 여기 있다: AuditLogger()를 부르는 운영 코드는 이 함수 하나뿐이다.
    이 규칙은 언어가 강제하지 않는다 — 대신 grep 한 번이면 검증되고, 코드 리뷰 규칙으로 지킨다.
    주의: 싱글턴이든 이 방식이든 '프로세스당 하나'일 뿐이다. 웹 서버가 워커 프로세스를 4개 띄우면
    기록기도 4개다. 프로세스를 넘는 유일성은 단일 기록 프로세스나 DB 시퀀스 같은 외부 장치가 맡아야 한다.
    """
    audit = AuditLogger()
    # 같은 audit 객체를 두 모듈에 넘기는 것이 곧 '공유'다. 싱글턴의 유일성이 여기서는 변수 하나로 표현된다.
    return EmrApp(audit=audit, prescription=PrescriptionModule(audit), lab=LabModule(audit))


def test_prescription_writes_one_entry() -> bool:
    """테스트 A: 자기 전용 기록기를 만든다. 전역 상태가 없으니 리셋할 것도 없다."""
    audit = AuditLogger()
    PrescriptionModule(audit).prescribe("dr.test", "P-T1")
    return len(audit.entries) == 1


def test_lab_writes_one_entry() -> bool:
    """테스트 B: A와 완전히 독립적이다."""
    audit = AuditLogger()
    LabModule(audit).view_result("lab.test", "P-T2")
    return len(audit.entries) == 1


if __name__ == "__main__":
    print("[1] 운영: composition root가 기록기를 하나 만들어 모든 모듈에 나눠 준다")
    # 운영 진입점(main)이 하는 일은 이 한 줄뿐이다: 그래프를 조립하고, 나머지는 객체들에게 맡긴다.
    app = build_app()
    app.prescription.prescribe("dr.kim", "P-1001")
    app.lab.view_result("lab.lee", "P-1001")
    app.prescription.prescribe("dr.kim", "P-2002")
    print(f"  모듈들이 같은 기록기를 공유? {app.prescription.audit is app.lab.audit}")
    print(f"  기록 {len(app.audit.entries)}줄, 어긋난 기록: {app.audit.verify()}")

    print("\n[2] 테스트: 순서를 바꿔도, 동시에 돌려도 서로 간섭하지 않는다")
    print(f"  A→B: {test_prescription_writes_one_entry()}, {test_lab_writes_one_entry()}")
    print(f"  B→A: {test_lab_writes_one_entry()}, {test_prescription_writes_one_entry()}")
    # 테스트 러너의 병렬 실행을 흉내 낸다. 각 테스트가 자기 기록기를 만들므로 공유 상태가 없다.
    # f=f 기본 인자는 반복문 변수를 람다가 '현재 값'으로 붙잡게 하려는 관용구다(늦은 바인딩 방지).
    results: list[bool] = []
    threads = [threading.Thread(target=lambda f=f: results.append(f()))
               for f in (test_prescription_writes_one_entry, test_lab_writes_one_entry) * 4]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    print(f"  8개 테스트 병렬 실행: 모두 통과? {all(results)} (리셋 훅 없음)")

    print("\n[3] 대가: 실수로 두 번째 기록기를 만드는 것을 언어가 막지는 않는다")
    rogue = LabModule(AuditLogger())  # composition root 밖에서 생성 — 리뷰에서 잡아야 한다
    rogue.view_result("lab.oops", "P-1001")
    print(f"  운영 기록기 줄 수는 그대로 {len(app.audit.entries)}줄 — 이 기록은 다른 체인으로 새어 나갔다")
