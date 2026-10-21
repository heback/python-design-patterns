"""파이썬다운 변형 2: __init_subclass__로 '정의하는 순간 등록되는' 리더 레지스트리.

상황: 03_pythonic.py의 from_config()는 DEVICES 표를 프레임워크가 직접 들고 있어서,
옆 연구실이 XRD 리더를 추가하려면 결국 공용 코드의 표를 고쳐야 했다(단순 팩토리의 한계).
여기서는 Reader의 하위 클래스가 정의될 때 class 문의 키워드 인자(device="xrd")로
스스로 레지스트리에 등록되게 한다. 프레임워크는 등록부만 조회한다.

비판적으로 볼 점: 이것은 더 이상 엄밀한 GoF 팩토리 메서드가 아니다. '무엇을 만들지'를
Creator의 하위 클래스가 아니라 '문자열 키 → 클래스' 등록부가 결정한다. 대신
"확장은 추가만으로"라는 팩토리 메서드의 핵심 이득(OCP)은 그대로 유지하면서,
설정 파일 같은 데이터로 장비를 고를 수 있게 된다. 플러그인 시스템이 흔히 쓰는 모양이다.
"""
from __future__ import annotations

import csv
import io
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, ClassVar


@dataclass(frozen=True)
class Sample:
    """측정점 하나(불변)."""

    x: float
    intensity: float


class Reader(ABC):
    """[Product] 리더 공통 인터페이스이자 등록부의 주인.

    등록부를 여기에 둔 이유: '리더 종류의 목록'은 리더 계층에 대한 지식이므로
    Reader가 소유하는 것이 응집도가 높다. AcquisitionJob은 Reader.for_device()만 부른다.
    """

    # 장비 이름 → 리더 클래스. ClassVar로 표시해 인스턴스 속성이 아님을 타입 검사기에 알린다.
    _registry: ClassVar[dict[str, type[Reader]]] = {}
    # 등록된 하위 클래스가 자기 장비 이름을 알 수 있도록 __init_subclass__가 채운다(아래 참고).
    device: ClassVar[str]

    def __init_subclass__(cls, *, device: str | None = None, **kwargs: Any) -> None:
        """하위 클래스가 '정의될 때' 파이썬이 호출한다(인스턴스 생성 때가 아님).

        device를 키워드 전용 인자로 받는 이유: class XrdReader(Reader, device="xrd")처럼
        클래스 정의 줄에 등록 정보가 함께 보여 선언적이다. device 없이 상속하면
        (예: 공통 기능을 모은 중간 추상 클래스) 등록하지 않는다.
        메타클래스로도 같은 일을 할 수 있지만, __init_subclass__는 메타클래스 충돌
        (ABC는 이미 ABCMeta를 쓴다) 없이 훨씬 가볍게 같은 효과를 낸다.
        """
        super().__init_subclass__(**kwargs)  # 협력적 다중 상속을 위해 반드시 위로 넘긴다
        if device is None:
            return
        if device in Reader._registry:
            # 조용히 덮어쓰면 두 연구실의 리더가 서로를 가리는 버그가 런타임 한참 뒤에야 드러난다.
            raise ValueError(f"장비 {device!r}가 이미 {Reader._registry[device].__name__}로 등록됨")
        Reader._registry[device] = cls
        cls.device = device

    @classmethod
    def for_device(cls, device: str, **options: Any) -> Reader:
        """등록부에서 클래스를 찾아 인스턴스를 만든다. 실패 메시지에 등록된 목록을 담는다."""
        try:
            reader_cls = Reader._registry[device]
        except KeyError:
            known = ", ".join(sorted(Reader._registry))
            raise LookupError(f"등록되지 않은 장비 {device!r} (등록됨: {known})") from None
        return reader_cls(**options)

    @abstractmethod
    def connect(self) -> str:
        """장비에 연결한다."""

    @abstractmethod
    def read_samples(self) -> list[Sample]:
        """공통 Sample 목록을 돌려준다."""


class TextColumnReader(Reader):
    """중간 추상 클래스: '두 열짜리 텍스트'를 읽는 공통 로직. device가 없으므로 등록되지 않는다."""

    RAW: ClassVar[str] = ""
    DELIMITER: ClassVar[str | None] = None

    def read_samples(self) -> list[Sample]:
        """구분자로 두 열을 나눠 읽는다. 하위 클래스는 RAW와 DELIMITER만 정한다."""
        # 숫자로 시작하지 않는 줄(예: CSV 헤더 "wavelength_nm,absorbance")은 데이터가 아니므로 건너뛴다.
        lines = [ln for ln in self.RAW.splitlines() if ln and not ln[0].isalpha()]
        return [Sample(*map(float, ln.split(self.DELIMITER))) for ln in lines]


class CsvSpectrumReader(TextColumnReader, device="uv-vis"):
    """[Concrete Product] class 문 한 줄이 곧 등록이다."""

    RAW = "wavelength_nm,absorbance\n220,0.12\n260,0.87\n280,0.45\n"
    DELIMITER = ","

    def connect(self) -> str:
        """연결을 흉내 낸다."""
        return "UV-Vis 분광광도계"


class AcquisitionJob:
    """[Client] 흐름만 안다. 어떤 장비가 존재하는지는 전혀 모른다."""

    def __init__(self, sample_id: str, device: str, **options: Any) -> None:
        """장비 이름과 리더 생성 옵션을 보관만 한다(생성은 run()에서)."""
        self.sample_id = sample_id
        self.device = device
        self.options = options

    def run(self) -> list[Sample]:
        """연결 → 읽기 → 정규화 → 저장. 생성은 등록부 조회로 대체되었다."""
        reader = Reader.for_device(self.device, **self.options)
        print(f"  연결: {reader.connect()}")
        samples = reader.read_samples()
        peak = max(s.intensity for s in samples)
        normalized = [Sample(s.x, round(s.intensity / peak, 3)) for s in samples]
        print(f"  저장: {self.sample_id} → {[s.intensity for s in normalized]}")
        return normalized


if __name__ == "__main__":
    print("[1] 프레임워크가 아는 장비:", sorted(Reader._registry))
    AcquisitionJob("S-101", "uv-vis").run()

    print("\n[2] XRD 리더가 정의되기 전에는 찾을 수 없다")
    try:
        AcquisitionJob("S-201", "xrd").run()
    except LookupError as e:
        print(f"  LookupError: {e}")

    print("\n[3] 옆 연구실이 자기 모듈에서 클래스를 '정의'만 한다 (프레임워크 수정 0줄)")

    class XrdReader(TextColumnReader, device="xrd"):
        """[Concrete Product] 공백 구분 텍스트(2θ, counts)."""

        RAW = "20.0 150\n28.4 980\n47.3 410\n"

        def connect(self) -> str:
            """연결을 흉내 낸다."""
            return "X선 회절계(옆 연구실)"

    print("  이제 등록된 장비:", sorted(Reader._registry))
    AcquisitionJob("S-201", "xrd").run()

    print("\n[4] 같은 이름으로 두 번 등록하면 정의 시점에 실패한다")
    try:
        class AnotherXrdReader(TextColumnReader, device="xrd"):
            """다른 연구실이 같은 키를 쓴 경우."""

            def connect(self) -> str:
                """연결을 흉내 낸다."""
                return "충돌"
    except ValueError as e:
        print(f"  ValueError: {e}")

    print("\n[5] 함정: 등록은 '모듈이 import될 때' 일어난다")
    print("  XrdReader가 든 모듈을 아무도 import하지 않으면, 코드가 분명히 있는데도 [2]처럼 '없는 장비'로 실패한다.")
    print("  그래서 플러그인 시스템은 진입점(entry points)이나 명시적 import 목록을 함께 둔다.")
