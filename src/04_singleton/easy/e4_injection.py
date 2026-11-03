"""04 싱글턴 — 주입 코드: 유일성은 조립 지점이, 기록기는 생성자로.

상황: 싱글턴은 유일성(하나여야 한다)과 전역 접근(어디서든 얻는다)을 묶어 팔았다.
필요한 것은 유일성뿐이다. AuditLogger는 평범한 클래스로 돌아가고, build_app()
한 곳이 하나를 만들어 모든 모듈에 생성자로 넘긴다.
"""
from __future__ import annotations


class AuditLogger:
    """평범한 기록기. 몇 개를 만들든 클래스는 상관하지 않는다."""

    def __init__(self) -> None:
        """기록 목록."""
        self.entries: list[str] = []

    def record(self, who: str, action: str) -> None:
        """기록을 덧붙인다."""
        self.entries.append(f"{who} {action}")


class PrescriptionModule:
    """처방 모듈. 의존성이 생성자 시그니처에 드러난다."""

    def __init__(self, audit: AuditLogger) -> None:
        """기록기를 받아 들고 있다. 그래서 호출자가 바꿔 넣을 수 있다."""
        self.audit = audit

    def prescribe(self, doctor: str) -> None:
        """받은 기록기에 쓴다."""
        self.audit.record(doctor, "처방")


class LabModule:
    """검사 모듈. 같은 방식으로 기록기를 받는다."""

    def __init__(self, audit: AuditLogger) -> None:
        """기록기를 받는다."""
        self.audit = audit

    def view(self, staff: str) -> None:
        """열람을 기록한다."""
        self.audit.record(staff, "검사 결과 열람")


def build_app() -> tuple[PrescriptionModule, LabModule]:
    """composition root: 운영 코드에서 AuditLogger()를 부르는 유일한 곳.

    주의: 이 '하나'는 프로세스당 하나다. 웹 서버가 프로세스를 넷 띄우면 기록기도 넷이다.
    싱글턴도 마찬가지다. 프로세스를 넘는 유일성은 데이터베이스 같은 바깥 장치가 맡는다.
    """
    audit = AuditLogger()
    return PrescriptionModule(audit), LabModule(audit)


if __name__ == "__main__":
    print("[1] 운영: 모든 모듈이 같은 기록기를 공유한다 — 체인은 하나")
    rx, lab = build_app()
    rx.prescribe("김의사")
    lab.view("이기사")
    print("  같은 기록기인가:", rx.audit is lab.audit, "/", rx.audit.entries)

    print("[2] 테스트: 각자 새 기록기를 넣는다 — 순서를 바꿔도 간섭이 없고 리셋 뒷문도 없다")
    for name in ["테스트A", "테스트B"]:
        fresh = AuditLogger()
        PrescriptionModule(fresh).prescribe(name)
        print(f"  {name}: 기록 {len(fresh.entries)}줄")

    print("[3] 대가: 누군가 build_app() 밖에서 AuditLogger()를 하나 더 만드는 것은 막지 못한다")
    print("  → 코드 리뷰나 검색으로 지키는 규칙이다. 싱글턴은 이것을 실행 중에 강제한다")
