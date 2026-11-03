"""06 데코레이터 — 패턴 코드: 같은 Channel 인터페이스를 지키는 래퍼를 겹쳐 쌓는다.

상황: 준호는 기능 하나를 래퍼 클래스 하나로 만든다. 모든 래퍼가 MqttChannel과 같은
Channel 타입이므로 래퍼를 또 감쌀 수 있다. 농장마다 다른 조합은 클래스가 아니라
'감싸는 순서'로 표현된다. 데모는 (1) 조합 조립, (2) 순서가 결과를 바꾼다는 것을 보인다.
"""
from __future__ import annotations

import hashlib
import json
import zlib
from abc import ABC, abstractmethod


def toy_encrypt(data: bytes, key: bytes = b"farm-key") -> bytes:
    """교육용 스트림 암호(순진한 코드와 같다). 실제 제품은 AES-GCM 같은 검증된 방식을 쓴다."""
    stream = b"".join(hashlib.sha256(key + i.to_bytes(4, "big")).digest()
                      for i in range(len(data) // 32 + 1))
    return bytes(a ^ b for a, b in zip(data, stream))


class Channel(ABC):
    """[Component] 실제 채널과 모든 래퍼가 함께 지키는 인터페이스.

    flush()가 여기 있는 이유: 버퍼를 가진 래퍼(배치)가 생기면 '남은 것을 내보내라'는
    요청도 체인 끝까지 전달되어야 한다.
    """

    @abstractmethod
    def send(self, payload: bytes) -> None:
        """페이로드 하나를 보낸다."""

    @abstractmethod
    def flush(self) -> None:
        """버퍼에 남은 것을 모두 내보낸다."""


class MqttChannel(Channel):
    """[Concrete Component] 실제 전송. 브로커 대신 보낸 크기를 기록한다."""

    def __init__(self) -> None:
        """전송 기록."""
        self.sent_sizes: list[int] = []

    def send(self, payload: bytes) -> None:
        """MQTT publish 흉내."""
        self.sent_sizes.append(len(payload))

    def flush(self) -> None:
        """버퍼가 없으니 할 일이 없다."""


class ChannelDecorator(Channel):
    """[Decorator] Channel이면서(상속, 다른 래퍼가 나를 감쌀 수 있게) Channel을 하나 가진다(합성).

    기본 동작은 모두 안쪽으로 넘기기. 구체 래퍼는 바꿀 메서드만 다시 쓴다.
    """

    def __init__(self, inner: Channel) -> None:
        """감쌀 채널. 무엇을 감쌀지는 실행 중에 정한다."""
        self._inner = inner

    def send(self, payload: bytes) -> None:
        """그대로 넘긴다."""
        self._inner.send(payload)

    def flush(self) -> None:
        """flush도 반드시 넘긴다. 빠뜨리면 안쪽 배치 버퍼가 영영 안 비워진다."""
        self._inner.flush()


class CompressingChannel(ChannelDecorator):
    """[Concrete Decorator] 압축. 이 클래스는 zlib 말고는 모른다(SRP)."""

    def send(self, payload: bytes) -> None:
        """압축한 뒤 안쪽으로 넘긴다."""
        self._inner.send(zlib.compress(payload, 9))


class EncryptingChannel(ChannelDecorator):
    """[Concrete Decorator] 암호화."""

    def send(self, payload: bytes) -> None:
        """암호화한 뒤 안쪽으로 넘긴다."""
        self._inner.send(toy_encrypt(payload))


class BatchingChannel(ChannelDecorator):
    """[Concrete Decorator] size건을 모아 한 번에 보낸다. 상태(버퍼)를 가진 래퍼."""

    def __init__(self, inner: Channel, size: int) -> None:
        """배치 크기와 버퍼."""
        super().__init__(inner)
        self._size, self._buffer = size, []

    def send(self, payload: bytes) -> None:
        """버퍼가 차면 묶어서 내보낸다."""
        self._buffer.append(payload)
        if len(self._buffer) >= self._size:
            self.flush()

    def flush(self) -> None:
        """내 버퍼를 먼저 비우고 나서 안쪽에 flush를 전한다(순서가 바뀌면 데이터가 갇힌다)."""
        if self._buffer:
            self._inner.send(b"\n".join(self._buffer))
            self._buffer.clear()
        self._inner.flush()


class LoggingChannel(ChannelDecorator):
    """[Concrete Decorator] 지나가는 크기만 기록한다(관찰형 — 데이터를 바꾸지 않는다)."""

    def __init__(self, inner: Channel, label: str) -> None:
        """label 덕분에 같은 래퍼를 체인의 여러 위치에 꽂을 수 있다."""
        super().__init__(inner)
        self._label = label

    def send(self, payload: bytes) -> None:
        """기록하고 그대로 넘긴다."""
        print(f"    [log:{self._label}] {len(payload)} bytes")
        self._inner.send(payload)


def reading(i: int) -> bytes:
    """토양 수분 측정값 하나(JSON 바이트)."""
    return json.dumps({"sensor": "soil-07", "seq": i, "moisture": 31.5 + i % 3}).encode()


if __name__ == "__main__":
    print("[1] 배치(10) → 로그(압축 전) → 압축 → 로그(압축 후) → 암호화 → MQTT, 15건")
    mqtt = MqttChannel()
    # 바깥 래퍼가 먼저 실행된다. 바깥에서 안쪽으로 읽으면 그것이 처리 순서다.
    farm = BatchingChannel(LoggingChannel(CompressingChannel(LoggingChannel(
        EncryptingChannel(mqtt), "압축 후")), "압축 전"), size=10)
    for i in range(15):
        farm.send(reading(i))
    farm.flush()   # 남은 5건은 flush가 체인을 타고 내려가 내보낸다
    print(f"    MQTT가 받은 크기: {mqtt.sent_sizes}")

    print("[2] 같은 두 래퍼, 순서만 바꾸기 (10건 한 묶음)")
    for name, ch_type in [("압축→암호화", (CompressingChannel, EncryptingChannel)),
                          ("암호화→압축", (EncryptingChannel, CompressingChannel))]:
        sink = MqttChannel()
        outer, inner = ch_type
        chain = BatchingChannel(outer(inner(sink)), size=10)
        for i in range(10):
            chain.send(reading(i))
        print(f"    {name}: {sink.sent_sizes[0]} bytes")
