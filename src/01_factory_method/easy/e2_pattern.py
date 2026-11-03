"""01 팩토리 메서드 — 패턴 코드: 흐름은 상위 클래스가, 리더 선택은 하위 클래스가.

상황: 순진한 코드의 run()에서 "리더를 만든다"는 한 단계만 떼어 추상 메서드
create_reader()로 만들었다. 장비별 작업 클래스가 이 메서드를 오버라이드한다.
[Product] Reader / [Creator] AcquisitionJob / [Concrete Creator] UvVisJob 등.
"""
from __future__ import annotations

import json
from abc import ABC, abstractmethod


class Reader(ABC):
    """[Product] run()이 아는 유일한 리더 타입."""

    @abstractmethod
    def read_samples(self) -> list[float]:
        """세기 목록을 돌려준다."""


class CsvSpectrumReader(Reader):
    """[Concrete Product] UV-Vis 리더."""

    def read_samples(self) -> list[float]:
        """'x,세기' 줄에서 세기만 꺼낸다."""
        return [float(ln.split(",")[1]) for ln in "220,0.12\n260,0.87".splitlines()]


class SerialJsonReader(Reader):
    """[Concrete Product] 신형 장비 리더. port가 필요하다."""

    def __init__(self, port: str) -> None:
        """포트를 받는다."""
        self.port = port

    def read_samples(self) -> list[float]:
        """장비가 보낸 텍스트 배열을 읽는다."""
        return json.loads("[3.2, 6.4, 1.6]")


class AcquisitionJob(ABC):
    """[Creator] 측정 흐름을 소유한다. 구체 리더 이름은 하나도 모른다."""

    def __init__(self, sample_id: str) -> None:
        """장비별 인자(port)는 더 이상 여기 없다."""
        self.sample_id = sample_id

    @abstractmethod
    def create_reader(self) -> Reader:
        """[Factory Method] '무엇을' 만들지는 하위 클래스가 정한다."""

    def run(self) -> list[float]:
        """'언제' 만들지는 여기서 정한다: 흐름의 첫 단계."""
        values = self.create_reader().read_samples()
        peak = max(values)
        result = [round(v / peak, 2) for v in values]
        print(f"  저장 {self.sample_id}: {result}")
        return result


class UvVisJob(AcquisitionJob):
    """[Concrete Creator] UV-Vis 작업."""

    def create_reader(self) -> Reader:
        """UV-Vis 리더를 고른다. 이 결정은 프로그램 전체에서 여기 한 곳에만 있다."""
        return CsvSpectrumReader()


class SerialJsonJob(AcquisitionJob):
    """[Concrete Creator] 신형 장비 작업. port가 제자리를 찾았다."""

    def __init__(self, sample_id: str, port: str) -> None:
        """공통 인자는 위로 넘기고, 장비 고유 인자는 그 뒤에 직접 보관한다."""
        super().__init__(sample_id)
        self.port = port

    def create_reader(self) -> Reader:
        """보관한 포트로 리더를 만든다."""
        return SerialJsonReader(self.port)


# --- 옆 연구실의 코드: 위쪽 공용 코드는 한 줄도 고치지 않고 추가만 한다(OCP) ---
class XrdReader(Reader):
    """[Concrete Product] 옆 연구실의 새 장비 리더."""

    def read_samples(self) -> list[float]:
        """고정 데이터로 측정을 흉내 낸다."""
        return [150.0, 980.0, 410.0]


class XrdJob(AcquisitionJob):
    """[Concrete Creator] 추가만으로 생긴 작업."""

    def create_reader(self) -> Reader:
        """자기 연구실의 리더를 만든다."""
        return XrdReader()


class FakeReader(Reader):
    """테스트용 리더. 손으로 검산할 수 있는 세기 2, 4를 낸다."""

    def read_samples(self) -> list[float]:
        """기대 결과는 [0.5, 1.0]."""
        return [2.0, 4.0]


class FakeJob(AcquisitionJob):
    """테스트 전용 작업. create_reader()가 곧 이음새라 전역을 건드리지 않는다."""

    def create_reader(self) -> Reader:
        """가짜 리더를 만든다."""
        return FakeReader()


if __name__ == "__main__":
    print("[1] 작업 클래스를 고르면 리더는 각 클래스가 만든다")
    for job in [UvVisJob("S-101"), SerialJsonJob("S-103", "/dev/ttyUSB0")]:
        job.run()
    print("[2] 옆 연구실이 추가한 XrdJob도 같은 흐름으로 돈다")
    XrdJob("S-201").run()
    print("[3] 테스트: 가짜 리더로 정규화만 확인한다")
    assert FakeJob("S-test").run() == [0.5, 1.0]  # 틀리면 AssertionError
    print("  통과 — 전역을 바꾸지 않았다")
