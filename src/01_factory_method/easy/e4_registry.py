"""01 팩토리 메서드 — 레지스트리 변형: 클래스를 정의하는 순간 등록된다.

상황: 파이썬다운 변형의 from_config()는 공용 코드가 DEVICES 표를 쥐고 있어서,
새 장비를 붙이려면 그 표를 고쳐야 했다. 여기서는 Reader의 하위 클래스가
class 문의 device="xrd" 인자로 스스로 등록부에 올라간다. 공용 코드는 조회만 한다.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, ClassVar


class Reader(ABC):
    """[Product] 리더의 공통 타입이자 등록부의 주인."""

    # 장비 이름 → 리더 클래스. 인스턴스마다가 아니라 클래스 전체가 하나를 공유한다.
    _registry: ClassVar[dict[str, type[Reader]]] = {}

    def __init_subclass__(cls, device: str | None = None, **kwargs: Any) -> None:
        """하위 클래스가 '정의될 때' 파이썬이 부른다(인스턴스를 만들 때가 아니다)."""
        super().__init_subclass__(**kwargs)  # 부모 쪽 처리도 이어지게 위로 넘긴다
        if device is None:
            return  # device 없이 상속한 중간 클래스는 등록하지 않는다
        if device in Reader._registry:
            # 조용히 덮어쓰면 두 연구실의 리더가 서로를 가린다. 정의 시점에 막는다.
            raise ValueError(f"{device!r}는 이미 등록됨")
        Reader._registry[device] = cls

    @classmethod
    def for_device(cls, device: str) -> Reader:
        """등록부에서 클래스를 찾아 인스턴스를 만든다."""
        if device not in Reader._registry:
            raise LookupError(f"등록되지 않은 장비 {device!r}, 등록됨: {sorted(Reader._registry)}")
        return Reader._registry[device]()

    @abstractmethod
    def read_samples(self) -> list[float]:
        """세기 목록을 돌려준다."""


class CsvSpectrumReader(Reader, device="uv-vis"):
    """[Concrete Product] class 문 한 줄이 곧 등록이다."""

    def read_samples(self) -> list[float]:
        """고정 데이터로 측정을 흉내 낸다."""
        return [0.12, 0.87]


class AcquisitionJob:
    """흐름만 안다. 어떤 장비가 있는지는 전혀 모른다."""

    def __init__(self, sample_id: str, device: str) -> None:
        """장비 이름만 보관한다. 리더는 run()에서 만든다."""
        self.sample_id, self.device = sample_id, device

    def run(self) -> list[float]:
        """분기 대신 등록부를 조회한다."""
        values = Reader.for_device(self.device).read_samples()
        result = [round(v / max(values), 2) for v in values]
        print(f"  저장 {self.sample_id}: {result}")
        return result


if __name__ == "__main__":
    print("[1] 등록된 장비:", sorted(Reader._registry))
    AcquisitionJob("S-101", "uv-vis").run()

    print("[2] 새 장비 리더가 정의되기 전")
    try:
        AcquisitionJob("S-201", "xrd").run()
    except LookupError as e:
        print(f"  LookupError: {e}")

    print("[3] 옆 연구실이 클래스를 정의만 한다 (공용 코드 수정 0줄)")

    class XrdReader(Reader, device="xrd"):
        """[Concrete Product] 정의되는 순간 등록된다."""

        def read_samples(self) -> list[float]:
            """고정 데이터."""
            return [150.0, 980.0, 410.0]

    print("  등록된 장비:", sorted(Reader._registry))
    AcquisitionJob("S-201", "xrd").run()

    print("[4] 함정: 등록은 그 클래스가 든 모듈이 import될 때 일어난다")
    print("  아무도 import하지 않으면 코드가 있는데도 [2]처럼 '없는 장비'가 된다")
