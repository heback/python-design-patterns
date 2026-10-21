"""순진한 설계: 측정 흐름 안에서 장비 리더를 직접 만드는 AcquisitionJob.

상황: 화학과 박사과정 서윤은 UV-Vis 분광광도계 한 대의 CSV 출력을 읽어
정규화하고 저장하는 AcquisitionJob을 만들었다. 공동 연구실에서 질량분석기(바이너리
포맷)와 신형 장비(시리얼로 JSON 전송)가 들어오자, 서윤은 가장 빠른 방법으로
run() 안에 `if device == ...` 분기를 추가했다. 이 파일은 그 결과를 보여준다.

읽을 때 주목할 점:
- "언제 만들 것인가(흐름)"와 "무엇을 만들 것인가(구체 클래스 선택)"가 run() 한 메서드에 엉켜 있다.
- 새 장비를 지원하려면 공용 프레임워크 파일(이 파일)을 열어 고쳐야 한다.
- 테스트에서 가짜 리더를 끼울 이음새(seam)가 없어 모듈 전역을 바꿔치기해야 한다.
"""
from __future__ import annotations

import csv
import io
import json
import struct
from dataclasses import dataclass


@dataclass(frozen=True)
class Sample:
    """측정점 하나. x는 장비에 따라 파장(nm)·질량 대 전하비(m/z)·시간(s)이다.

    frozen=True로 둔 이유: 정규화 단계가 원본 측정점을 제자리에서 바꾸면
    "원시 데이터 보존"이라는 연구실 데이터 관리 원칙이 깨지기 때문이다.
    """

    x: float
    intensity: float


# ---------------------------------------------------------------------------
# 장비별 리더. 이 부분 자체는 문제가 아니다 — 문제는 이들을 '누가, 어디서' 만드는가다.
# ---------------------------------------------------------------------------

class CsvSpectrumReader:
    """UV-Vis 분광광도계가 내보내는 CSV(파장, 흡광도)를 읽는다."""

    # 실제 장비 대신 장비가 내보낼 법한 원시 출력을 상수로 둔다(예제를 단독 실행 가능하게).
    RAW = "wavelength_nm,absorbance\n220,0.12\n260,0.87\n280,0.45\n"

    def connect(self) -> str:
        """장비 연결을 흉내 내고 연결 설명을 돌려준다."""
        return "UV-Vis 분광광도계(USB, CSV 내보내기)"

    def read_samples(self) -> list[Sample]:
        """CSV 텍스트를 Sample 목록으로 바꾼다."""
        rows = csv.DictReader(io.StringIO(self.RAW))
        return [Sample(float(r["wavelength_nm"]), float(r["absorbance"])) for r in rows]


class MassSpecBinaryReader:
    """질량분석기 고유 바이너리 포맷(리틀엔디언 float64 쌍: m/z, counts)을 읽는다."""

    RAW = struct.pack("<6d", 18.0, 1200.0, 44.0, 5300.0, 92.0, 800.0)

    def connect(self) -> str:
        """장비 연결을 흉내 낸다."""
        return "질량분석기(이더넷, 고유 바이너리)"

    def read_samples(self) -> list[Sample]:
        """8바이트 float64를 모두 풀어 두 개씩 묶어 (m/z, counts) 쌍으로 해석한다."""
        values = struct.unpack(f"<{len(self.RAW) // 8}d", self.RAW)
        return [Sample(values[i], values[i + 1]) for i in range(0, len(values), 2)]


class SerialJsonReader:
    """신형 장비가 시리얼 포트로 보내는 JSON 프레임을 읽는다."""

    RAW = '{"points": [{"t": 0.0, "v": 3.2}, {"t": 0.5, "v": 6.4}, {"t": 1.0, "v": 1.6}]}'

    def __init__(self, port: str) -> None:
        """시리얼 장비는 포트 이름이 필요하다 — 리더마다 생성 인자가 다르다는 점에 주목."""
        self.port = port

    def connect(self) -> str:
        """장비 연결을 흉내 낸다."""
        return f"시리얼 JSON 장비({self.port})"

    def read_samples(self) -> list[Sample]:
        """JSON 프레임의 points 배열을 Sample 목록으로 바꾼다."""
        frame = json.loads(self.RAW)
        return [Sample(p["t"], p["v"]) for p in frame["points"]]


# ---------------------------------------------------------------------------
# 공용 프레임워크 — 모든 연구실이 함께 쓰는 저장소의 코드라고 가정한다.
# ---------------------------------------------------------------------------

class AcquisitionJob:
    """측정 작업: 연결 → 읽기 → 정규화 → 저장. 흐름 자체는 모든 장비에 공통이다."""

    def __init__(self, sample_id: str, device: str, port: str = "COM3") -> None:
        """device 문자열로 장비 종류를 고른다.

        ⚠ 문제: port는 시리얼 장비에만 의미가 있는데 모든 작업의 생성자에 붙어 있다.
        장비별 생성 인자가 늘어날수록 이 생성자는 '모든 장비의 합집합'이 된다.
        """
        self.sample_id = sample_id
        self.device = device
        self.port = port

    def run(self) -> list[Sample]:
        """측정 흐름 전체를 실행하고 정규화된 측정점을 돌려준다."""
        # ⚠ 문제: 흐름(run)과 생성(어떤 리더인가)이 한 메서드에 엉켜 있다.
        #   새 장비가 생길 때마다 이 분기를 고쳐야 한다 → OCP 위반.
        #   또 run()이 구체 클래스 세 개를 이름으로 직접 안다 → DIP 위반.
        if self.device == "uv-vis":
            reader = CsvSpectrumReader()
        elif self.device == "mass-spec":
            reader = MassSpecBinaryReader()
        elif self.device == "serial-json":
            reader = SerialJsonReader(self.port)
        else:
            # ⚠ 문제: 다른 연구실의 XRD 장비는 여기서 막힌다. 그 연구실은
            #   공용 저장소에 이 분기를 추가하는 PR을 보내는 것 외에는 방법이 없다.
            raise ValueError(f"지원하지 않는 장비: {self.device!r} (프레임워크 수정 필요)")

        print(f"  연결: {reader.connect()}")
        samples = reader.read_samples()
        normalized = self.normalize(samples)
        self.save(normalized)
        return normalized

    def normalize(self, samples: list[Sample]) -> list[Sample]:
        """최대 세기를 1.0으로 맞춘다(장비마다 세기 단위가 달라 비교하려면 필요)."""
        peak = max(s.intensity for s in samples)
        return [Sample(s.x, round(s.intensity / peak, 3)) for s in samples]

    def save(self, samples: list[Sample]) -> None:
        """저장을 흉내 낸다. 실제로는 연구실 데이터 아카이브에 기록한다."""
        print(f"  저장: {self.sample_id} → {len(samples)}개 측정점, 첫 점 {samples[0]}")


if __name__ == "__main__":
    print("[1] 세 장비 모두 '일단은' 잘 돌아간다")
    for device in ("uv-vis", "mass-spec", "serial-json"):
        AcquisitionJob(f"S-{device}", device).run()

    print("\n[2] 옆 연구실이 XRD 회절계를 붙이려 하면")
    try:
        AcquisitionJob("S-xrd", "xrd").run()
    except ValueError as e:
        print(f"  실패: {e}")

    print("\n[3] 정규화 로직만 테스트하고 싶은데, 실제 리더를 피할 방법이 없다")
    # ⚠ 문제: run()이 CsvSpectrumReader를 '이름으로' 직접 생성하므로,
    #   가짜 리더를 넣으려면 모듈 전역 이름 자체를 바꿔치기(monkeypatch)해야 한다.
    #   이 방식은 같은 모듈을 쓰는 다른 테스트와 간섭하고, 복원을 잊으면 오염이 남는다.
    class FakeReader:
        """테스트용 가짜 리더: 결과를 손으로 계산할 수 있는 고정 데이터."""

        def connect(self) -> str:
            """가짜 연결."""
            return "가짜 장비"

        def read_samples(self) -> list[Sample]:
            """세기 2와 4 → 정규화하면 0.5와 1.0이어야 한다."""
            return [Sample(1, 2.0), Sample(2, 4.0)]

    original = CsvSpectrumReader
    globals()["CsvSpectrumReader"] = FakeReader  # 전역 바꿔치기 — 냄새가 나는 지점
    try:
        result = AcquisitionJob("S-test", "uv-vis").run()
        print(f"  정규화 결과: {[s.intensity for s in result]}  (기대값 [0.5, 1.0])")
    finally:
        globals()["CsvSpectrumReader"] = original
    print("  → 테스트는 통과했지만, 전역 상태를 건드려야만 가능했다")
