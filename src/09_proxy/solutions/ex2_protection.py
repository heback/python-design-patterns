"""09 프록시 — 연습문제 2 해설: 서비스 메서드마다 반복되던 권한 검사를 보호 프록시로.

상황: 관측 기관의 문서 관리 시스템(DocumentService)은 update/delete 메서드에
`if user.role != "admin": raise PermissionError` 검사를 복사해 두었고, read는 검사가 '없는 것'으로
"모두 허용"을 표현했다. 새로 추가된 export에서 검사 복사가 빠져 일반 직원이 기밀 보고서를
내보낼 수 있었다 — 검사가 없는 것이 허용인지 누락인지 코드로는 구분되지 않았던 것이다. 여기서는 권한 정책을
ProtectedDocumentService(보호 프록시)로 옮기고, 실제 서비스는 업무 로직만 남긴다.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class User:
    """사용자."""

    name: str
    role: str   # "admin" | "staff"


class DocumentService(ABC):
    """[Subject] 문서 서비스 인터페이스."""

    @abstractmethod
    def read(self, user: User, doc_id: str) -> str:
        """열람."""

    @abstractmethod
    def update(self, user: User, doc_id: str, body: str) -> None:
        """수정."""

    @abstractmethod
    def export(self, user: User, doc_id: str) -> bytes:
        """외부 반출."""


class RealDocumentService(DocumentService):
    """[Real Subject] 업무 로직만 있다. 권한이라는 단어가 한 번도 나오지 않는다(SRP)."""

    def __init__(self) -> None:
        """메모리 저장소."""
        self._docs = {"R-17": "북부 해안 관측 보고서"}

    def read(self, user: User, doc_id: str) -> str:
        """열람."""
        return self._docs[doc_id]

    def update(self, user: User, doc_id: str, body: str) -> None:
        """수정."""
        self._docs[doc_id] = body

    def export(self, user: User, doc_id: str) -> bytes:
        """반출."""
        return self._docs[doc_id].encode()


class ProtectedDocumentService(DocumentService):
    """[Proxy: 보호] 메서드별 허용 역할을 '표 하나'로 선언한다.

    정책이 표로 모이면 "export는 누가 할 수 있나?"를 코드 검색 대신 이 표 하나로 답할 수 있다.
    새 메서드를 추가할 때 표 갱신을 잊으면 _check가 거부하므로(기본 거부) 그 누락은 유출로 이어지지 않는다.
    단, 위임 메서드에서 _check 호출 자체를 빠뜨리는 누락은 막지 못한다(check_policy_complete와 데모 [3] 참조).
    """

    POLICY: dict[str, set[str]] = {
        "read": {"admin", "staff"},
        "update": {"admin"},
        "export": {"admin"},
    }

    def __init__(self, real: DocumentService) -> None:
        """실제 서비스."""
        self._real = real

    def _check(self, action: str, user: User) -> None:
        """표에 없거나 역할이 없으면 거부."""
        if user.role not in self.POLICY.get(action, set()):
            raise PermissionError(f"{user.name}({user.role})은(는) {action} 권한이 없다")

    def read(self, user: User, doc_id: str) -> str:
        """검사 후 위임."""
        self._check("read", user)
        return self._real.read(user, doc_id)

    def update(self, user: User, doc_id: str, body: str) -> None:
        """검사 후 위임."""
        self._check("update", user)
        self._real.update(user, doc_id, body)

    def export(self, user: User, doc_id: str) -> bytes:
        """검사 후 위임."""
        self._check("export", user)
        return self._real.export(user, doc_id)


def check_policy_complete() -> None:
    """정책 완전성 검사: Subject의 모든 추상 메서드가 POLICY 표에 있어야 한다.

    기본 거부는 '표 갱신 누락'을 막는다. 그러나 프록시의 새 위임 메서드에서 _check 호출 자체를
    빠뜨리면 원래 사고와 같은 유출이 생긴다. 그 누락은 (1) 이 검사와 (2) 권한 없는 사용자로
    모든 메서드를 호출해 보는 테스트(데모 [3])로 막는다.
    """
    missing = DocumentService.__abstractmethods__ - ProtectedDocumentService.POLICY.keys()
    # assert가 아니라 명시적 raise: assert는 python -O 실행 시 통째로 사라져 검사가 무력화된다.
    if missing:
        raise RuntimeError(f"정책 표에 없는 메서드: {missing}")


if __name__ == "__main__":
    check_policy_complete()
    svc: DocumentService = ProtectedDocumentService(RealDocumentService())
    admin, staff = User("수아", "admin"), User("민호", "staff")
    print("[1] staff 열람:", svc.read(staff, "R-17"))
    for label, call in [("staff 반출", lambda: svc.export(staff, "R-17")),
                        ("admin 반출", lambda: svc.export(admin, "R-17"))]:
        try:
            print(f"[2] {label}: {len(call())} bytes 반출됨")
        except PermissionError as e:
            print(f"[2] {label}: 거부 — {e}")

    print("[3] 권한 없는 사용자로 각 메서드 호출 — 하나라도 통과하면 _check 누락이다")
    guest = User("방문자", "guest")
    calls = {"update": lambda: svc.update(staff, "R-17", "x"), "export": lambda: svc.export(staff, "R-17"),
             "read(guest)": lambda: svc.read(guest, "R-17")}
    for name, call in calls.items():
        try:
            call()
            print(f"    {name}: ⚠ 통과됨")
        except PermissionError:
            print(f"    {name}: 거부됨")
