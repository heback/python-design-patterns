"""08 퍼사드 — 파이썬다운 변형: 함수 퍼사드, contextmanager 퍼사드, 표준 라이브러리 속 퍼사드.

상황: 02_facade.py의 CheckInFacade는 상태가 없다. 서브시스템 참조만 들고 있을 뿐,
check_in() 호출 사이에 기억하는 것이 없다. 지호의 동료 서윤은 묻는다. "그럼 클래스일 이유가 있어?"
이 파일은 세 가지를 보인다.
  (1) 함수 퍼사드: 모듈 수준 함수 check_in() 하나. 파이썬에서는 '모듈'이 곧 퍼사드가 될 수 있다
      (패키지의 __init__.py가 __all__로 공개 API를 좁히는 것이 그 형태다).
  (2) contextmanager 퍼사드: 키오스크 하드웨어의 "열기 → 작업 → 반드시 닫기"를 with 한 줄로 감싼다.
  (3) subprocess.run: 표준 라이브러리가 Popen·파이프·대기·종료코드 확인을 하나로 감싼 퍼사드다.
"""
from __future__ import annotations

import subprocess
import sys
from contextlib import contextmanager
from typing import Iterator

__all__ = ["check_in", "kiosk_session"]
# __all__: 'from 이모듈 import *'로 노출할 이름. 이 파일이 패키지의 __init__.py라면
# 클라이언트가 보는 공개 표면은 이 두 이름뿐이고, 아래 서브시스템 클래스는 '내부'로 읽힌다.


# --- 축약한 서브시스템 --------------------------------------------------------

class _PassportReader:
    """[Subsystem] 여권 판독기 하드웨어. 열고 닫아야 하는 자원이다.

    이름 앞 밑줄: 파이썬 관례상 '모듈 내부용'. 접근을 막지는 않지만 공개 API가 아님을 알린다.
    퍼사드가 서브시스템을 '숨기지 않는다'는 원칙과도 맞는다 — 필요한 사람은 여전히 쓸 수 있다.
    """

    def open(self) -> None:
        """장치 연결."""
        print("    (판독기) 연결")

    def close(self) -> None:
        """장치 해제. 빠뜨리면 다음 승객이 판독기를 못 쓴다."""
        print("    (판독기) 해제")

    def verify(self, last_name: str, mrz: str) -> bool:
        """MRZ의 성 일치 여부."""
        return last_name.upper() in mrz


class _Printer:
    """[Subsystem] 탑승권 프린터. 역시 열고 닫는 자원."""

    def open(self) -> None:
        """용지 확인 및 연결."""
        print("    (프린터) 연결")

    def close(self) -> None:
        """해제."""
        print("    (프린터) 해제")

    def issue(self, text: str) -> str:
        """출력."""
        return f"[탑승권] {text}"


# --- (1) 함수 퍼사드 ----------------------------------------------------------

def check_in(pnr: str, last_name: str, mrz: str, *,
             reader: _PassportReader, printer: _Printer) -> str:
    """[Facade] 상태가 없는 퍼사드는 함수 하나로 충분하다.

    서브시스템을 키워드 인자로 받는 이유: 테스트에서 가짜를 넣기 위해서다(클래스 퍼사드의
    생성자 주입과 같은 역할). 기본값을 모듈 전역 인스턴스로 두면 더 짧아지지만, 그 순간
    숨은 전역 상태가 생긴다(4장 싱글턴의 함정).
    """
    if not reader.verify(last_name, mrz):
        raise ValueError("여권 불일치")
    return printer.issue(f"{last_name} {pnr}")


# --- (2) contextmanager 퍼사드 -----------------------------------------------

@contextmanager
def kiosk_session() -> Iterator[tuple[_PassportReader, _Printer]]:
    """[Facade] '장치 열기 → 작업 → 예외가 나도 닫기'라는 순서 규칙을 with 한 줄로 감싼다.

    순서 규칙(프린터는 판독기보다 나중에 열고 먼저 닫는다)과 정리 보장(finally)이
    이 함수 안에만 있다. 클라이언트는 open/close를 아예 몰라도 된다.
    """
    reader, printer = _PassportReader(), _Printer()
    reader.open()
    try:
        printer.open()
        try:
            yield reader, printer
        finally:
            printer.close()
    finally:
        reader.close()


if __name__ == "__main__":
    print("[1] with 한 줄 + 함수 하나로 체크인")
    with kiosk_session() as (reader, printer):
        print("    " + check_in("NR11AB", "Lee", "P<KORLEE<<MINA", reader=reader, printer=printer))

    print("[2] 작업 중 예외가 나도 장치는 닫힌다")
    try:
        with kiosk_session() as (reader, printer):
            check_in("NR11AB", "Lee", "P<KORPARK<<MINA", reader=reader, printer=printer)
    except ValueError as e:
        print(f"    예외 전파: {e}")

    print("[3] 표준 라이브러리의 퍼사드: subprocess.run")
    # run() 한 줄 = Popen 생성 + 파이프 연결 + communicate() + wait() + (check=True면) 종료코드 검사.
    done = subprocess.run([sys.executable, "-c", "print('hello from child')"],
                          capture_output=True, text=True, check=True)
    print(f"    run(): {done.stdout.strip()!r}, returncode={done.returncode}")
    # 퍼사드는 하위 API를 막지 않는다: 스트리밍이 필요하면 여전히 Popen을 직접 쓴다.
    with subprocess.Popen([sys.executable, "-c", "print('streamed')"],
                          stdout=subprocess.PIPE, text=True) as proc:
        assert proc.stdout is not None
        print(f"    Popen 직접: {proc.stdout.readline().strip()!r}")
