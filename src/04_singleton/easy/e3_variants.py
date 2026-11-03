"""04 싱글턴 — 구현 비교 코드: 메타클래스와 모듈 수준 객체.

상황: 패턴 코드의 __new__ 방식은 __init__ 재호출을 가드로 막아야 했다. 파이썬에는
'하나'를 만드는 다른 길도 있다. 각 방식에서 유일성을 보장하는 주체가 누구인지 보라.
"""
from __future__ import annotations


class SingletonMeta(type):
    """메타클래스 방식: 클래스 호출 Cls() 자체를 가로챈다."""

    _instances: dict[type, object] = {}

    def __call__(cls, *args: object, **kwargs: object) -> object:
        """처음에만 원래 절차(__new__ → __init__)를 밟는다. 이후에는 그 절차를 건너뛴다.

        그래서 __init__ 재호출 함정이 원천적으로 없다. 대가: 메타클래스는 상속 계층 전체에
        퍼지고, 다른 메타클래스(예: ABC가 쓰는 것)와 섞으면 충돌을 직접 풀어야 한다.
        """
        if cls not in SingletonMeta._instances:
            SingletonMeta._instances[cls] = super().__call__(*args, **kwargs)
        return SingletonMeta._instances[cls]


class MetaLogger(metaclass=SingletonMeta):
    """메타클래스로 만든 싱글턴. __init__에 가드가 없어도 된다."""

    def __init__(self) -> None:
        """처음 한 번만 불린다."""
        self.entries: list[str] = []


class PlainLogger:
    """평범한 클래스. 유일성 로직이 클래스에서 빠졌다."""

    def __init__(self) -> None:
        """기록 목록."""
        self.entries: list[str] = []


# 모듈 수준 객체: 모듈은 첫 import 때 한 번만 실행되므로 이 변수는 프로세스에 하나다.
# 유일성은 "이 변수를 쓴다"는 관례로 지키고, 테스트는 언제든 PlainLogger()를 새로 만든다.
audit_logger = PlainLogger()


if __name__ == "__main__":
    print("[1] 메타클래스: 두 번 불러도 같은 객체, 기록도 그대로")
    a = MetaLogger()
    a.entries.append("처방")
    print("  같은 객체인가:", a is MetaLogger(), "/ 기록:", MetaLogger().entries)

    print("[2] 모듈 수준 객체: 운영에서는 audit_logger 하나를, 테스트는 새 객체를 쓴다")
    audit_logger.entries.append("처방")
    print("  운영:", audit_logger.entries, "/ 테스트용 새 객체:", PlainLogger().entries)
