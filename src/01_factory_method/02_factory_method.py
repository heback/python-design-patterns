"""팩토리 메서드 적용: 흐름은 상위 클래스가, 리더 선택은 하위 클래스가 결정한다.

상황: 01_naive.py에서 AcquisitionJob.run()은 측정 흐름과 리더 생성 분기를 함께 품고
있었다. 그래서 새 장비마다 공용 프레임워크를 고쳐야 했고, 테스트하려면 전역을
바꿔치기해야 했다. 여기서는 run()의 "리더를 만든다"는 한 단계를 추상 메서드
create_reader()로 떼어 내고, 장비별 작업 클래스가 그것을 오버라이드한다.

GoF 의도(intent): "객체를 생성하기 위한 인터페이스를 정의하되, 어떤 클래스의 인스턴스를
만들지는 서브클래스가 결정하게 한다. 팩토리 메서드는 클래스의 인스턴스화를
서브클래스로 미룬다."

역할 대응:
- [Product]          Reader
- [Concrete Product] CsvSpectrumReader, MassSpecBinaryReader, SerialJsonReader, XrdReader
- [Creator]          AcquisitionJob      (run()이 '언제' 만들지 결정)
- [Concrete Creator] UvVisJob, MassSpecJob, SerialJsonJob, XrdJob (create_reader()가 '무엇을' 결정)
"""
from __future__ import annotations

import csv
import io
import json
import struct
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class Sample:
    """측정점 하나. 불변으로 두어 정규화가 원시 데이터를 덮어쓰지 못하게 한다."""

    x: float
    intensity: float


# ---------------------------------------------------------------------------
# Product 계층
# ---------------------------------------------------------------------------

class Reader(ABC):
    """[Product] 장비 리더의 공통 인터페이스.

    AcquisitionJob.run()은 이 추상 타입만 안다(DIP). Protocol이 아니라 ABC를 쓴 이유:
    이 계층은 '프레임워크가 정의하고 연구실들이 상속해 채우는' 명목적 계약이며,
    메서드를 빠뜨린 리더를 인스턴스화 시점에 TypeError로 즉시 잡아 주기 때문이다.
    """

    @abstractmethod
    def connect(self) -> str:
        """장비에 연결하고 사람이 읽을 연결 설명을 돌려준다."""

    @abstractmethod
    def read_samples(self) -> list[Sample]:
        """장비 고유 포맷을 공통 Sample 목록으로 번역한다."""


class CsvSpectrumReader(Reader):
    """[Concrete Product] UV-Vis 분광광도계의 CSV(파장, 흡광도)."""

    RAW = "wavelength_nm,absorbance\n220,0.12\n260,0.87\n280,0.45\n"

    def connect(self) -> str:
        """연결을 흉내 낸다."""
        return "UV-Vis 분광광도계(USB, CSV 내보내기)"

    def read_samples(self) -> list[Sample]:
        """CSV 텍스트를 Sample 목록으로 바꾼다."""
        rows = csv.DictReader(io.StringIO(self.RAW))
        return [Sample(float(r["wavelength_nm"]), float(r["absorbance"])) for r in rows]


class MassSpecBinaryReader(Reader):
    """[Concrete Product] 질량분석기 고유 바이너리(리틀엔디언 float64 쌍: m/z, counts)."""

    RAW = struct.pack("<6d", 18.0, 1200.0, 44.0, 5300.0, 92.0, 800.0)

    def connect(self) -> str:
        """연결을 흉내 낸다."""
        return "질량분석기(이더넷, 고유 바이너리)"

    def read_samples(self) -> list[Sample]:
        """8바이트 float64를 두 개씩 묶어 (m/z, counts) 쌍으로 해석한다."""
        values = struct.unpack(f"<{len(self.RAW) // 8}d", self.RAW)
        return [Sample(values[i], values[i + 1]) for i in range(0, len(values), 2)]


class SerialJsonReader(Reader):
    """[Concrete Product] 신형 장비의 시리얼 JSON 프레임."""

    RAW = '{"points": [{"t": 0.0, "v": 3.2}, {"t": 0.5, "v": 6.4}, {"t": 1.0, "v": 1.6}]}'

    def __init__(self, port: str) -> None:
        """시리얼 포트가 필요하다. 이 인자를 아는 것은 이제 SerialJsonJob 하나뿐이다."""
        self.port = port

    def connect(self) -> str:
        """연결을 흉내 낸다."""
        return f"시리얼 JSON 장비({self.port})"

    def read_samples(self) -> list[Sample]:
        """JSON 프레임의 points 배열을 Sample 목록으로 바꾼다."""
        return [Sample(p["t"], p["v"]) for p in json.loads(self.RAW)["points"]]


# ---------------------------------------------------------------------------
# Creator 계층 — 공용 프레임워크
# ---------------------------------------------------------------------------

class AcquisitionJob(ABC):
    """[Creator] 측정 작업의 고정된 흐름을 소유한다.

    핵심 분담: run()은 리더가 '언제' 필요한지(연결 직전)를 결정하고,
    create_reader()를 구현한 하위 클래스가 '무엇을' 만들지 결정한다.
    run() 본문에는 구체 리더 이름이 하나도 없다 — 이것이 01_naive.py와의 차이 전부다.
    """

    def __init__(self, sample_id: str) -> None:
        """장비별 생성 인자(port 등)는 더 이상 여기 없다. 그것은 Concrete Creator의 몫이다."""
        self.sample_id = sample_id

    @abstractmethod
    def create_reader(self) -> Reader:
        """[Factory Method] 이 작업이 쓸 리더를 만든다.

        반환 타입이 구체 클래스가 아니라 Reader인 점이 중요하다. 호출자인 run()은
        이 타입에만 의존하므로, 하위 클래스가 무엇을 돌려주든 흐름은 그대로다.
        GoF는 Creator가 기본 구현을 줄 수도 있다고 하지만, 여기서는 '기본 장비'라는
        개념이 없으므로 추상으로 두어 구현 누락을 인스턴스화 시점에 잡는다.
        """

    def run(self) -> list[Sample]:
        """측정 흐름: 연결 → 읽기 → 정규화 → 저장.

        이 메서드는 하위 클래스가 오버라이드하지 않는 것을 전제로 한다(흐름은 프레임워크 소유).
        구조적으로 템플릿 메서드(14장)와 같다 — 그 한 단계가 '생성'일 뿐이다.
        """
        reader = self.create_reader()  # 생성 결정은 다형성으로 하위 클래스에 위임된다
        print(f"  연결: {reader.connect()}")
        normalized = self.normalize(reader.read_samples())
        self.save(normalized)
        return normalized

    def normalize(self, samples: list[Sample]) -> list[Sample]:
        """최대 세기를 1.0으로 맞춘다. 장비와 무관한 공통 로직이라 Creator에 둔다."""
        peak = max(s.intensity for s in samples)
        return [Sample(s.x, round(s.intensity / peak, 3)) for s in samples]

    def save(self, samples: list[Sample]) -> None:
        """저장을 흉내 낸다."""
        print(f"  저장: {self.sample_id} → {len(samples)}개 측정점, 첫 점 {samples[0]}")


class UvVisJob(AcquisitionJob):
    """[Concrete Creator] UV-Vis 측정 작업."""

    def create_reader(self) -> Reader:
        """CSV 리더를 고른다 — 이 결정을 아는 곳은 프로그램 전체에서 여기 한 곳이다."""
        return CsvSpectrumReader()


class MassSpecJob(AcquisitionJob):
    """[Concrete Creator] 질량분석 측정 작업."""

    def create_reader(self) -> Reader:
        """바이너리 리더를 고른다."""
        return MassSpecBinaryReader()


class SerialJsonJob(AcquisitionJob):
    """[Concrete Creator] 시리얼 JSON 장비 측정 작업.

    포트처럼 특정 장비에만 필요한 생성 인자는 이 하위 클래스가 받는다.
    naive 버전에서 모든 작업 생성자에 붙어 있던 port가 제자리를 찾은 것이다.
    """

    def __init__(self, sample_id: str, port: str) -> None:
        """상위 생성자에 공통 인자를 넘기고 장비 고유 인자는 스스로 보관한다."""
        super().__init__(sample_id)
        self.port = port

    def create_reader(self) -> Reader:
        """보관해 둔 포트로 리더를 만든다."""
        return SerialJsonReader(self.port)


# ---------------------------------------------------------------------------
# 다른 연구실의 코드 — 실제로는 별도 저장소에 있다고 가정한다.
# 공용 프레임워크(위)를 한 줄도 고치지 않고 새 장비를 붙인다: OCP.
# ---------------------------------------------------------------------------

class XrdReader(Reader):
    """[Concrete Product] 옆 연구실의 X선 회절계(공백 구분 텍스트: 2θ, counts)."""

    RAW = "20.0 150\n28.4 980\n47.3 410\n"

    def connect(self) -> str:
        """연결을 흉내 낸다."""
        return "X선 회절계(옆 연구실 자체 리더)"

    def read_samples(self) -> list[Sample]:
        """공백으로 구분된 두 열을 읽는다."""
        return [Sample(*map(float, line.split())) for line in self.RAW.splitlines()]


class XrdJob(AcquisitionJob):
    """[Concrete Creator] 옆 연구실이 '추가'만으로 만든 작업."""

    def create_reader(self) -> Reader:
        """자기 연구실의 리더를 고른다."""
        return XrdReader()


if __name__ == "__main__":
    print("[1] 장비별 작업 클래스를 고르면 리더는 각 클래스가 알아서 만든다")
    jobs: list[AcquisitionJob] = [
        UvVisJob("S-101"),
        MassSpecJob("S-102"),
        SerialJsonJob("S-103", port="/dev/ttyUSB0"),
    ]
    for job in jobs:
        job.run()  # 호출자 코드는 장비 종류를 모른다

    print("\n[2] 옆 연구실은 프레임워크를 고치지 않고 XrdJob을 추가했다")
    XrdJob("S-201").run()

    print("\n[3] 테스트: 가짜 리더를 돌려주는 하위 클래스 하나면 이음새가 생긴다")

    class FakeReader(Reader):
        """[Concrete Product] 테스트 전용. 손으로 검산 가능한 고정 데이터."""

        def connect(self) -> str:
            """가짜 연결."""
            return "가짜 장비"

        def read_samples(self) -> list[Sample]:
            """세기 2, 4 → 정규화 결과 0.5, 1.0."""
            return [Sample(1, 2.0), Sample(2, 4.0)]

    class FakeJob(AcquisitionJob):
        """[Concrete Creator] 테스트 전용. 전역 상태를 건드리지 않는다."""

        def create_reader(self) -> Reader:
            """가짜 리더를 만든다."""
            return FakeReader()

    result = FakeJob("S-test").run()
    assert [s.intensity for s in result] == [0.5, 1.0]
    print("  정규화 검증 통과 — monkeypatch 없이")

    print("\n[4] create_reader()를 빠뜨린 하위 클래스는 만들 때 바로 걸린다")

    class ForgetfulJob(AcquisitionJob):
        """구현을 잊은 Concrete Creator — ABC가 이것을 잡아낸다."""

    try:
        ForgetfulJob("S-oops")
    except TypeError as e:
        print(f"  TypeError: {e}")
