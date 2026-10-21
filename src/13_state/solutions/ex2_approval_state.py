"""[13장 연습문제 2 해설] 문서 결재 흐름(작성 중/상신/승인/반려)을 상태 패턴으로 리팩터링한다.

상황: 사내 전자결재 모듈의 `Document`가 edit/submit/approve/reject 네 메서드마다
`if self.status == ...`를 반복하고, 반려 사유(reject_reason)가 재상신 뒤에도 남아 있었다.
킥보드 예제와 같은 방식 — 기본은 거부, 허용 동작만 오버라이드, 상태별 데이터는 상태 객체가
소유 — 을 그대로 적용한다. 원래 코드에 있던 '승인된 문서도 edit 가능' 버그도 함께 사라진다.
"""
from __future__ import annotations

from abc import ABC, abstractmethod


class IllegalTransition(Exception):
    """현재 결재 단계에서 허용되지 않는 동작."""


class DocState(ABC):
    """[State] 결재 단계. 네 동작 모두 기본은 거부다."""

    def edit(self, doc: Document, text: str) -> None:
        """본문 수정."""
        raise IllegalTransition(f"[{self.name()}] 수정 불가")

    def submit(self, doc: Document) -> None:
        """상신."""
        raise IllegalTransition(f"[{self.name()}] 상신 불가")

    def approve(self, doc: Document, approver: str) -> None:
        """승인."""
        raise IllegalTransition(f"[{self.name()}] 승인 불가")

    def reject(self, doc: Document, reason: str) -> None:
        """반려."""
        raise IllegalTransition(f"[{self.name()}] 반려 불가")

    @abstractmethod
    def name(self) -> str:
        """단계 이름."""


class Draft(DocState):
    """[Concrete State] 작성 중. 수정과 상신만 가능."""

    def edit(self, doc: Document, text: str) -> None:
        """본문 수정은 이 상태에서만 허용된다 — 원래 코드의 '승인 후 수정' 버그가 구조적으로 불가능해진다."""
        doc.body = text

    def submit(self, doc: Document) -> None:
        """빈 문서 상신을 막는 가드도 상태 안에 둔다."""
        if not doc.body.strip():
            raise IllegalTransition("빈 문서는 상신할 수 없습니다")
        doc.change_state(Submitted())

    def name(self) -> str:
        """단계 이름."""
        return "작성 중"


class Submitted(DocState):
    """[Concrete State] 상신됨. 결재자의 승인/반려만 받는다."""

    def approve(self, doc: Document, approver: str) -> None:
        """승인자는 Approved 상태의 데이터다."""
        doc.change_state(Approved(approver))

    def reject(self, doc: Document, reason: str) -> None:
        """반려 사유는 Rejected 상태의 데이터다."""
        doc.change_state(Rejected(reason))

    def name(self) -> str:
        """단계 이름."""
        return "상신"


class Approved(DocState):
    """[Concrete State] 최종 상태. 어떤 동작도 오버라이드하지 않는다 = 모든 동작 거부."""

    def __init__(self, approver: str) -> None:
        """승인자 기록."""
        self.approver = approver

    def name(self) -> str:
        """단계 이름에 승인자를 포함한다."""
        return f"승인({self.approver})"


class Rejected(DocState):
    """[Concrete State] 반려됨. 수정하면 작성 중으로 돌아가며, 그때 반려 사유는 자연히 사라진다."""

    def __init__(self, reason: str) -> None:
        """반려 사유."""
        self.reason = reason

    def edit(self, doc: Document, text: str) -> None:
        """수정 = 재작성 시작. 본문을 고치고 Draft로 전이한다."""
        doc.body = text
        doc.change_state(Draft())

    def name(self) -> str:
        """반려 사유를 표시."""
        return f"반려: {self.reason}"


class Document:
    """[Context] 네 동작 모두 한 줄 위임. status 문자열과 reject_reason 필드가 없어졌다."""

    def __init__(self, title: str) -> None:
        """작성 중으로 시작."""
        self.title = title
        self.body = ""
        self._state: DocState = Draft()

    def change_state(self, new: DocState) -> None:
        """상태 객체 전용 전이 창구."""
        print(f"      ({self._state.name()} → {new.name()})")
        self._state = new

    def edit(self, text: str) -> None:
        """위임."""
        self._state.edit(self, text)

    def submit(self) -> None:
        """위임."""
        self._state.submit(self)

    def approve(self, approver: str) -> None:
        """위임."""
        self._state.approve(self, approver)

    def reject(self, reason: str) -> None:
        """위임."""
        self._state.reject(self, reason)

    @property
    def status(self) -> str:
        """화면 표시용."""
        return self._state.name()


if __name__ == "__main__":
    doc = Document("3분기 장비 구매 요청")
    print("[1] 빈 문서 상신 → 거부")
    try:
        doc.submit()
    except IllegalTransition as e:
        print("    ", e)
    print("[2] 작성 → 상신 → 반려 → 수정 → 재상신 → 승인")
    doc.edit("노트북 3대")
    doc.submit()
    doc.reject("견적서 누락")
    print("    현재:", doc.status)
    doc.edit("노트북 3대 + 견적서 첨부")
    doc.submit()
    doc.approve("박 팀장")
    print("    현재:", doc.status)
    print("[3] 승인된 문서 수정 시도 → 거부 (원래 코드에서는 허용되던 버그)")
    try:
        doc.edit("노트북 30대")
    except IllegalTransition as e:
        print("    ", e, "/ 본문 유지:", doc.body)
