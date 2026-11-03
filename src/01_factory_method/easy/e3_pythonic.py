"""01 팩토리 메서드 — 파이썬다운 변형: 하위 클래스 대신 '만드는 방법'을 넘긴다.

상황: 패턴 코드의 UvVisJob 같은 하위 클래스는 create_reader() 한 줄만 한다.
파이썬에서는 클래스도 함수처럼 호출할 수 있으므로, 그 한 줄을 생성자 인자
reader_factory로 받으면 하위 클래스가 필요 없다. 흐름(run)은 그대로 둔다.
"""
from __future__ import annotations

import json
from functools import partial
from typing import Callable, Protocol


class Reader(Protocol):
    """[Product] 상속하지 않아도 read_samples()만 있으면 리더로 인정된다."""

    def read_samples(self) -> list[float]:
        """세기 목록을 돌려준다."""
        ...


class CsvSpectrumReader:
    """UV-Vis 리더. Protocol이라 아무것도 상속하지 않는다."""

    def read_samples(self) -> list[float]:
        """고정 데이터로 측정을 흉내 낸다."""
        return [0.12, 0.87]


class SerialJsonReader:
    """신형 장비 리더. 생성 인자 port가 필요하다."""

    def __init__(self, port: str) -> None:
        """포트를 받는다."""
        self.port = port

    def read_samples(self) -> list[float]:
        """장비가 보낸 텍스트 배열을 읽는다."""
        return json.loads("[3.2, 6.4, 1.6]")


class AcquisitionJob:
    """흐름을 소유하고, 리더를 만드는 방법은 밖에서 받는다(상속 대신 합성)."""

    # from_config가 조회하는 '장비 이름 → 만드는 방법' 표
    DEVICES: dict[str, Callable[..., Reader]] = {
        "uv-vis": CsvSpectrumReader, "serial-json": SerialJsonReader}

    def __init__(self, sample_id: str, reader_factory: Callable[[], Reader]) -> None:
        """리더 '인스턴스'가 아니라 '만드는 방법'을 받는다.

        인스턴스를 받으면 언제 만들지를 호출자가 정해 버린다. 방법을 받아 두면
        만드는 시점은 여전히 run()이 정한다(장비 연결은 실행할 때까지 미룬다).
        """
        self.sample_id = sample_id
        self.reader_factory = reader_factory

    @classmethod
    def from_config(cls, config: dict[str, str]) -> AcquisitionJob:
        """대체 생성자: 설정 dict에서 작업을 만든다. 속은 표 조회(단순 팩토리)다."""
        options = {k: v for k, v in config.items() if k not in ("device", "sample_id")}
        maker = cls.DEVICES[config["device"]]  # 표에 없는 장비는 KeyError
        return cls(config["sample_id"], partial(maker, **options))

    def run(self) -> list[float]:
        """흐름은 패턴 코드와 같다. 여기서 비로소 리더가 만들어진다."""
        values = self.reader_factory().read_samples()
        result = [round(v / max(values), 2) for v in values]
        print(f"  저장 {self.sample_id}: {result}")
        return result


if __name__ == "__main__":
    print("[1] 클래스 자체를 넘긴다 — 하위 클래스가 필요 없다")
    AcquisitionJob("S-101", CsvSpectrumReader).run()

    print("[2] 인자가 필요한 리더는 partial로 port를 미리 묶어 넘긴다")
    AcquisitionJob("S-103", partial(SerialJsonReader, port="/dev/ttyUSB0")).run()

    print("[3] 만드는 시점은 여전히 run()이 정한다")
    log: list[str] = []

    def spying_factory() -> Reader:
        """불린 순간을 기록하는 평범한 함수. 테스트용 리더 팩토리가 된다."""
        log.append("생성")
        return CsvSpectrumReader()

    job = AcquisitionJob("S-test", spying_factory)
    print("  run() 전:", log)
    job.run()
    print("  run() 후:", log)

    print("[4] from_config: 설정에서 작업 만들기, 표에 없는 장비는 실패")
    AcquisitionJob.from_config({"device": "serial-json", "sample_id": "S-104", "port": "COM7"}).run()
    try:
        AcquisitionJob.from_config({"device": "xrd", "sample_id": "S-105"})
    except KeyError as e:
        print(f"  KeyError {e}: 결국 DEVICES 표를 고쳐야 한다")
