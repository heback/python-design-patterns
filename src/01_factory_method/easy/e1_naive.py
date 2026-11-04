"""01 팩토리 메서드 — 순진한 코드: 측정 흐름 안에서 리더를 직접 고르고 만든다.

상황: 서윤의 AcquisitionJob.run()은 "읽기 → 정규화 → 저장" 흐름을 가진다.
장비가 늘 때마다 run() 안에 if 분기를 하나씩 붙였다. 흐름(언제 만들지)과
리더 선택(무엇을 만들지)이 한 메서드에 엉켜 있다.
"""
from __future__ import annotations

import json


class CsvSpectrumReader:
    """UV-Vis 장비의 표 형식 출력을 읽는다. 리더 자체는 문제가 없다."""

    def read_samples(self) -> list[float]:
        """'x,세기' 줄에서 세기만 꺼낸다."""
        return [float(ln.split(",")[1]) for ln in "220,0.12\n260,0.87".splitlines()]


class SerialJsonReader:
    """포트로 연결하는 신형 장비의 리더. 포트 이름이 필요하다."""

    def __init__(self, port: str) -> None:
        """이 장비만 port가 필요하다."""
        self.port = port

    def read_samples(self) -> list[float]:
        """장비가 보낸 텍스트 배열을 읽는다."""
        return json.loads("[3.2, 6.4, 1.6]")


class AcquisitionJob:
    """모든 연구실이 함께 쓰는 측정 작업."""

    def __init__(self, sample_id: str, device: str, port: str = "COM3") -> None:
        """⚠ 문제: 신형 장비만 쓰는 port가 모든 작업의 생성자에 붙었다."""
        self.sample_id, self.device, self.port = sample_id, device, port

    def run(self) -> list[float]:
        """측정 흐름. 첫 단계에서 장비 이름으로 리더를 고른다."""
        # ⚠ 문제: 새 장비마다 공용 코드인 이 if 사슬을 고쳐야 한다.
        if self.device == "uv-vis":
            reader = CsvSpectrumReader()  # ⚠ 문제: 구체 클래스 이름에 직접 묶였다
        elif self.device == "serial-json":
            reader = SerialJsonReader(self.port)
        else:
            raise ValueError(f"지원하지 않는 장비: {self.device}")
        values = reader.read_samples()
        peak = max(values)  # 정규화: 최댓값을 1.0으로 맞춘다
        result = [round(v / peak, 2) for v in values]
        print(f"  저장 {self.sample_id}: {result}")
        return result


if __name__ == "__main__":
    print("[1] 두 장비는 일단 잘 돌아간다")
    AcquisitionJob("S-101", "uv-vis").run()
    AcquisitionJob("S-103", "serial-json", port="/dev/ttyUSB0").run()

    print("[2] 옆 연구실이 새 장비 'xrd'를 붙이려 하면")
    try:
        AcquisitionJob("S-201", "xrd").run()
    except ValueError as e:
        print(f"  실패: {e} → 공용 run()을 고쳐 달라고 요청해야 한다")

    print("[3] 정규화만 테스트하려면 리더의 이름 자체를 가짜로 바꿔치기해야 한다")

    class FakeReader:
        """테스트용 가짜 리더. 끼워 넣을 자리가 없어 진짜 이름을 덮어쓴다."""

        def read_samples(self) -> list[float]:
            """세기 2, 4 → 기대 결과 0.5, 1.0."""
            return [2.0, 4.0]

    original = CsvSpectrumReader
    globals()["CsvSpectrumReader"] = FakeReader  # ⚠ 문제: 이 파일 전체의 이름표를 건드린다
    AcquisitionJob("S-test", "uv-vis").run()
    globals()["CsvSpectrumReader"] = original  # 되돌리기를 잊으면 다른 코드도 가짜를 쓴다
