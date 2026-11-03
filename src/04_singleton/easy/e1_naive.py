"""04 싱글턴 — 순진한 코드: 모듈마다 감사 로그 기록기를 따로 만든다.

상황: 각 기록은 "직전 기록 번호(prev)"를 담아 한 줄로 이어진 체인을 이룬다. 체인이
하나여야 중간 기록을 지우거나 고친 흔적이 드러난다. 그런데 처방·검사·원무 모듈이
각자 AuditLogger()를 만들어 같은 파일에 쓰자 체인이 갈라졌다.
"""
from __future__ import annotations

FILE: list[dict[str, object]] = []  # 모든 기록기가 함께 쓰는 감사 로그 파일(흉내)


class AuditLogger:
    """기록기 하나. 혼자 쓸 때는 완벽하게 정확하다."""

    def __init__(self) -> None:
        """이 기록기가 마지막으로 쓴 기록 번호. 체인을 잇는 데 필요한 상태다."""
        self._last: int | None = None  # ⚠ 문제: 이 상태가 인스턴스마다 따로 있다

    def record(self, who: str, action: str) -> None:
        """새 기록에 '내가 마지막으로 쓴 번호'를 prev로 담아 파일 끝에 덧붙인다."""
        no = len(FILE)
        FILE.append({"no": no, "prev": self._last, "who": who, "action": action})
        self._last = no


if __name__ == "__main__":
    print("[1] 세 모듈이 각자 기록기를 만든다")
    prescription, lab, billing = AuditLogger(), AuditLogger(), AuditLogger()  # ⚠ 문제
    prescription.record("김의사", "처방")
    lab.record("이기사", "검사 결과 열람")
    billing.record("박원무", "수납")
    prescription.record("김의사", "처방 수정")

    print("[2] prev를 위에서 아래로 따라가 보라 — 직전 줄을 가리키지 않는다")
    for e in FILE:
        print(f"  #{e['no']} prev={e['prev']}  {e['who']} {e['action']}")
    # #1, #2의 prev가 None인 것은 각 기록기가 "내가 첫 기록"이라 믿었기 때문이다.
    # #3은 파일상 직전인 #2가 아니라 처방 기록기가 마지막으로 쓴 #0을 가리킨다.
    print("  → 체인이 세 갈래로 갈라졌다. 변조가 없는데도 검증 도구는 '변조 의심'을 낸다")
