"""08 퍼사드 — 파이썬다운 변형: 함수 퍼사드와 contextmanager 퍼사드.

상황: CheckInFacade는 상태가 없다. 동료 서윤이 묻는다. "그럼 클래스일 이유가 있어?"
이 코드는 (1) 모듈 수준 함수 하나로 된 퍼사드와, (2) 키오스크 장치의 "열기 → 작업 →
반드시 역순으로 닫기"를 with 한 줄로 감싸는 contextmanager 퍼사드를 보인다.
"""
from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator


class _Device:
    """[Subsystem] 열고 닫아야 하는 키오스크 장치(판독기·프린터). 이름 앞 밑줄은 '내부용' 표시."""

    def __init__(self, name: str) -> None:
        """장치 이름."""
        self.name = name

    def open(self) -> None:
        """연결."""
        print(f"    ({self.name}) 연결")

    def close(self) -> None:
        """해제. 빠뜨리면 다음 승객이 장치를 못 쓴다."""
        print(f"    ({self.name}) 해제")


# (1) 상태 없는 퍼사드는 함수 하나면 된다. 장치는 키워드 인자로 받아 테스트에서 바꿔 끼운다.
def check_in(last_name: str, passport_name: str, *, reader: _Device, printer: _Device) -> str:
    """[Facade] 여권 확인 → 발권. 쓰는 쪽은 순서를 몰라도 된다."""
    # 순서 규칙(여권 먼저)은 이 함수 안에만 있다.
    if last_name.upper() != passport_name.upper():
        raise ValueError("여권 불일치")
    return f"[탑승권] {last_name} ({reader.name}·{printer.name} 사용)"


# (2) 자원의 순서 규칙(열기 순서, 역순 닫기, 예외에도 닫기)을 with 뒤에 숨긴다.
@contextmanager
def kiosk_session() -> Iterator[tuple[_Device, _Device]]:
    """[Facade] 판독기 → 프린터 순으로 열고, 끝나면(예외가 나도) 역순으로 닫는다."""
    reader, printer = _Device("판독기"), _Device("프린터")
    reader.open()
    try:   # 판독기를 연 뒤에는 무슨 일이 있어도 닫는다
        printer.open()
        try:   # 프린터도 마찬가지. 안쪽 finally가 먼저 돌아 닫는 순서가 역순이 된다
            yield reader, printer   # 여기서 with 블록의 본문이 실행된다
        finally:
            printer.close()
    finally:
        reader.close()


if __name__ == "__main__":
    print("[1] with 한 줄 + 함수 퍼사드로 체크인")
    with kiosk_session() as (r, p):
        print("   ", check_in("Lee", "LEE", reader=r, printer=p))
    print("[2] 중간에 예외가 나도 장치는 역순으로 닫힌다")
    try:
        with kiosk_session() as (r, p):
            check_in("Lee", "PARK", reader=r, printer=p)
    except ValueError as e:
        print(f"    거절: {e}")
