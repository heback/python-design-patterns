"""06 데코레이터 — 연습문제 1 해설: 감싸는 순서에 따라 전송 크기가 어떻게 달라지는가.

상황: 준호의 게이트웨이 설정 파일에서 누군가 compress와 encrypt의 순서를 바꿨다.
테스트는 모두 통과했지만 그달 LTE 요금이 여섯 배로 뛰었다. 이 파일은 두 순서를
실제로 실행해 크기를 비교하고, 덤으로 '배치를 압축 바깥에 두느냐 안쪽에 두느냐'도 비교한다.
"""
from __future__ import annotations

import hashlib
import json
import zlib
from abc import ABC, abstractmethod
from typing import Callable


def toy_encrypt(data: bytes, key: bytes = b"k") -> bytes:
    """교육용 스트림 암호. 출력이 무작위처럼 보인다는 성질만 필요하다."""
    stream = b"".join(hashlib.sha256(key + i.to_bytes(4, "big")).digest()
                      for i in range(len(data) // 32 + 1))
    return bytes(a ^ b for a, b in zip(data, stream))


class Channel(ABC):
    """[Component] 전송 채널."""

    @abstractmethod
    def send(self, payload: bytes) -> None:
        """전송."""

    def flush(self) -> None:
        """기본은 할 일 없음. 데코레이터가 재정의해 위임한다."""


class Sink(Channel):
    """[Concrete Component] 보낸 크기를 합산한다."""

    def __init__(self) -> None:
        """누적 바이트 수."""
        self.total = 0

    def send(self, payload: bytes) -> None:
        """크기만 기록."""
        self.total += len(payload)


class Wrapper(Channel):
    """[Decorator] 위임 기반 클래스."""

    def __init__(self, inner: Channel) -> None:
        """감쌀 채널."""
        self._inner = inner

    def send(self, payload: bytes) -> None:
        """기본 위임."""
        self._inner.send(payload)

    def flush(self) -> None:
        """flush 위임."""
        self._inner.flush()


class Compress(Wrapper):
    """[Concrete Decorator] 압축."""

    def send(self, payload: bytes) -> None:
        """압축 후 위임."""
        self._inner.send(zlib.compress(payload, 9))


class Encrypt(Wrapper):
    """[Concrete Decorator] 암호화."""

    def send(self, payload: bytes) -> None:
        """암호화 후 위임."""
        self._inner.send(toy_encrypt(payload))


class Batch(Wrapper):
    """[Concrete Decorator] n건 묶음."""

    def __init__(self, inner: Channel, n: int) -> None:
        """버퍼 크기와 버퍼."""
        super().__init__(inner)
        self._n = n
        self._buf: list[bytes] = []

    def send(self, payload: bytes) -> None:
        """n건이 차면 한 번에."""
        self._buf.append(payload)
        if len(self._buf) == self._n:
            self._emit()

    def _emit(self) -> None:
        """버퍼를 한 페이로드로 묶어 안쪽에 넘긴다. '내보내기'만 하고 flush는 전파하지 않는다(02와 같은 구조)."""
        if self._buf:
            self._inner.send(b"\n".join(self._buf))
            self._buf.clear()

    def flush(self) -> None:
        """내 버퍼를 비운 뒤 안쪽으로 flush 전파."""
        self._emit()
        self._inner.flush()


def reading(i: int) -> bytes:
    """센서 측정값 JSON."""
    return json.dumps({"sensor": "soil-07", "seq": i, "moisture": 31.5 + i % 3, "unit": "%"}).encode()


def measure(build: Callable[[Channel], Channel], n: int = 100) -> int:
    """build(sink)로 체인을 만들고 n건을 보낸 뒤 총 전송 바이트를 돌려준다."""
    sink = Sink()
    chain = build(sink)
    for i in range(n):
        chain.send(reading(i))
    chain.flush()
    return sink.total


if __name__ == "__main__":
    # 기준선: 래퍼 없이 보낸 원본 크기. 이후 비율은 모두 이것에 대한 백분율이다.
    raw = measure(lambda s: s)
    print(f"[0] 아무 래퍼 없음: {raw} bytes (100건)")
    print("[1] 압축과 암호화의 순서 (배치 10건이 가장 바깥)")
    # 바깥 → 안쪽이 처리 순서다. (가)는 평문을 압축한 뒤 암호화하고,
    # (나)는 암호문을 압축하려 한다 — 암호문에는 압축기가 찾을 반복이 없다.
    a = measure(lambda s: Batch(Compress(Encrypt(s)), 10))
    b = measure(lambda s: Batch(Encrypt(Compress(s)), 10))
    print(f"    압축→암호화: {a} bytes  ({a / raw:.0%})")
    print(f"    암호화→압축: {b} bytes  ({b / raw:.0%})")
    print("[2] 배치의 위치 (압축→암호화 고정)")
    # 배치가 압축 '안쪽'이면 압축기는 62바이트짜리 측정값 하나씩만 본다.
    # 건 사이의 반복(같은 필드 이름)을 활용할 기회가 없어 헤더 비용만 남는다.
    c = measure(lambda s: Compress(Encrypt(Batch(s, 10))))
    print(f"    배치가 바깥(묶은 뒤 압축): {a} bytes")
    print(f"    배치가 안쪽(건별 압축 뒤 묶음): {c} bytes")
