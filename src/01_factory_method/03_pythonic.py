"""파이썬다운 변형 1: 상속 대신 '생성 함수'를 주입하고, 설정에서 작업을 만드는 대체 생성자.

상황: 02_factory_method.py에서는 장비가 하나 늘 때마다 Concrete Creator(XrdJob 등)를
하나씩 만들어야 했다. 그런데 그 하위 클래스들이 하는 일은 create_reader() 한 줄뿐이다.
파이썬에서는 클래스 자체가 호출 가능한 객체(callable)이므로, "리더를 만드는 방법"을
값으로 넘기면 하위 클래스 계층 없이 같은 분담(흐름은 프레임워크, 선택은 바깥)을 얻는다.

이 파일이 보여주는 것:
1. reader_factory: Callable[[], Reader] 주입 — 클래스, functools.partial, 람다 모두 팩토리가 된다.
2. Reader를 Protocol로 — 장비 리더가 프레임워크 클래스를 상속할 필요조차 없어진다.
3. @classmethod from_config() — 흔히 '팩토리 메서드'라 불리지만 GoF의 의도와는 다른 것.
"""
from __future__ import annotations

import csv
import io
import json
from dataclasses import dataclass
from functools import partial
from typing import Any, Callable, ClassVar, Protocol


@dataclass(frozen=True)
class Sample:
    """측정점 하나(불변)."""

    x: float
    intensity: float


class Reader(Protocol):
    """[Product] 구조적 인터페이스.

    ABC 대신 Protocol을 쓴 이유: 생성 함수 주입 방식에서는 프레임워크가 리더 계층을
    '소유'하지 않는다. 벤더가 준 SDK 클래스든 연구실이 쓴 클래스든 connect()와
    read_samples()만 있으면 된다. 대가는 누락 검사가 런타임 인스턴스화가 아니라
    정적 타입 검사기(mypy 등)로 옮겨 간다는 것이다.
    """

    def connect(self) -> str:
        """장비에 연결하고 설명을 돌려준다."""
        ...

    def read_samples(self) -> list[Sample]:
        """공통 Sample 목록을 돌려준다."""
        ...


class CsvSpectrumReader:
    """[Concrete Product] UV-Vis CSV 리더. Reader를 상속하지 않는다 — Protocol이므로."""

    RAW = "wavelength_nm,absorbance\n220,0.12\n260,0.87\n280,0.45\n"

    def connect(self) -> str:
        """연결을 흉내 낸다."""
        return "UV-Vis 분광광도계"

    def read_samples(self) -> list[Sample]:
        """CSV를 파싱한다."""
        rows = csv.DictReader(io.StringIO(self.RAW))
        return [Sample(float(r["wavelength_nm"]), float(r["absorbance"])) for r in rows]


class SerialJsonReader:
    """[Concrete Product] 시리얼 JSON 리더. 생성 인자(port)가 필요한 리더의 예."""

    RAW = '{"points": [{"t": 0.0, "v": 3.2}, {"t": 0.5, "v": 6.4}, {"t": 1.0, "v": 1.6}]}'

    def __init__(self, port: str) -> None:
        """포트를 보관한다."""
        self.port = port

    def connect(self) -> str:
        """연결을 흉내 낸다."""
        return f"시리얼 JSON 장비({self.port})"

    def read_samples(self) -> list[Sample]:
        """JSON 프레임을 파싱한다."""
        return [Sample(p["t"], p["v"]) for p in json.loads(self.RAW)["points"]]


# 리더를 만드는 '방법'의 타입. 인자 없는 호출로 Reader를 돌려주는 모든 것.
ReaderFactory = Callable[[], Reader]


class AcquisitionJob:
    """[Creator 역할을 합성으로] 흐름은 그대로 소유하고, 생성 방법은 주입받는다.

    02의 create_reader() 오버라이드가 생성자 인자 reader_factory로 바뀌었다.
    구조적으로는 '생성 전략'을 들고 있는 Context — 10장 전략 패턴과 같은 모양이다.
    상속 대신 합성을 고른 이유: 변하는 것이 '메서드 하나'뿐이라면 그 하나를 값으로
    넘기는 편이 클래스 계층을 늘리는 것보다 싸고, 런타임에 바꿀 수도 있다.
    """

    # from_config가 쓰는 '장비 이름 → 생성 방법' 표. 클래스 속성이라 하위 클래스가 덮어쓸 수 있다.
    DEVICES: ClassVar[dict[str, Callable[..., Reader]]] = {
        "uv-vis": CsvSpectrumReader,
        "serial-json": SerialJsonReader,
    }

    def __init__(self, sample_id: str, reader_factory: ReaderFactory) -> None:
        """리더 인스턴스가 아니라 '만드는 방법'을 받는다.

        왜 인스턴스를 바로 받지 않는가? run()이 '언제' 만들지 결정한다는 분담을 지키기 위해서다.
        연결은 비싸고(장비 점유) 작업이 실제로 실행될 때까지 미뤄야 한다. 인스턴스를 받으면
        생성 시점이 호출자에게 넘어가 버린다.
        """
        self.sample_id = sample_id
        self._reader_factory = reader_factory

    @classmethod
    def from_config(cls, config: dict[str, Any]) -> AcquisitionJob:
        """대체 생성자(alternative constructor): 설정 dict에서 작업을 만든다.

        주의: 이것도 흔히 '팩토리 메서드'라 부르지만 GoF 팩토리 메서드가 아니다.
        - GoF: Creator의 다른 연산(run)이 호출하는 훅이며, '무엇을 만들지'를 하위 클래스가 결정.
        - 이것: 클래스 밖에서 호출하는 생성 진입점이며, '무엇을 만들지'를 데이터(device 키)가 결정.
        내부는 사실상 단순 팩토리(표 조회)다. cls(...)를 쓰므로 하위 클래스에서 호출하면 그
        하위 클래스 인스턴스가 나온다는 점만 다형적이다.
        """
        options = {k: v for k, v in config.items() if k not in ("device", "sample_id")}
        maker = cls.DEVICES[config["device"]]
        # partial로 장비별 인자(port 등)를 미리 묶어 '인자 없는 팩토리'로 맞춘다.
        return cls(config["sample_id"], partial(maker, **options))

    def run(self) -> list[Sample]:
        """흐름은 02와 동일하다. 생성 지점이 self.create_reader()에서 주입된 함수로 바뀌었을 뿐."""
        reader = self._reader_factory()
        print(f"  연결: {reader.connect()}")
        samples = reader.read_samples()
        peak = max(s.intensity for s in samples)
        normalized = [Sample(s.x, round(s.intensity / peak, 3)) for s in samples]
        print(f"  저장: {self.sample_id} → {[s.intensity for s in normalized]}")
        return normalized


if __name__ == "__main__":
    print("[1] 클래스 자체가 팩토리다 — 하위 클래스 없이 UV-Vis 작업")
    AcquisitionJob("S-101", CsvSpectrumReader).run()

    print("\n[2] 생성 인자가 필요한 리더는 partial로 인자를 미리 묶는다")
    AcquisitionJob("S-103", partial(SerialJsonReader, port="/dev/ttyUSB0")).run()

    print("\n[3] 테스트: 평범한 함수 하나가 가짜 리더 팩토리가 된다 (FakeJob 클래스도 필요 없음)")

    class FakeReader:
        """테스트용 리더. Protocol이라 아무것도 상속하지 않는다."""

        def connect(self) -> str:
            """가짜 연결."""
            return "가짜 장비"

        def read_samples(self) -> list[Sample]:
            """정규화 결과가 0.5, 1.0이 되도록 고른 값."""
            return [Sample(1, 2.0), Sample(2, 4.0)]

    created: list[str] = []

    def spying_factory() -> Reader:
        """팩토리가 '언제' 호출되는지 기록한다 — run() 전에는 리더가 만들어지지 않아야 한다."""
        created.append("생성됨")
        return FakeReader()

    job = AcquisitionJob("S-test", spying_factory)
    print(f"  run() 전 생성 기록: {created}")
    job.run()
    print(f"  run() 후 생성 기록: {created}  ← 생성 시점은 여전히 프레임워크가 결정")

    print("\n[4] from_config: 설정 파일 한 줄에서 작업 만들기 (대체 생성자)")
    AcquisitionJob.from_config({"device": "serial-json", "sample_id": "S-104", "port": "COM7"}).run()
    try:
        AcquisitionJob.from_config({"device": "xrd", "sample_id": "S-105"})
    except KeyError as e:
        print(f"  KeyError {e}: 표에 없는 장비 — 확장하려면 DEVICES를 고쳐야 한다 (단순 팩토리의 한계)")
