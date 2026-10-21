"""06 데코레이터 — 패턴 적용: 같은 Channel 인터페이스를 지키는 래퍼들을 겹쳐 쌓는다.

상황: 준호는 상속 조합(2^n 클래스)과 플래그 if 지옥을 버리고, 기능 하나를 래퍼 클래스
하나로 만들기로 한다. 모든 래퍼는 MqttChannel과 '같은' Channel 인터페이스를 가지므로
래퍼를 또 감쌀 수 있다. 농장마다 다른 조합은 클래스가 아니라 '감싸는 순서'로 표현된다.
이 파일의 데모는 (1) 조합 조립, (2) 감싸는 순서가 의미를 바꾼다는 것(압축↔암호화),
(3) 로그 래퍼를 체인의 다른 위치에 꽂아 '압축 전/후 크기'를 모두 보는 것을 보여준다.
"""
from __future__ import annotations

import hashlib
import json
import zlib
from abc import ABC, abstractmethod


def toy_encrypt(data: bytes, key: bytes = b"farm-key") -> bytes:
    """교육용 스트림 암호(SHA-256 카운터 키스트림 XOR). 실제로는 AES-GCM 같은 검증된 방식을 쓴다.

    이 예제에 필요한 성질은 '출력이 무작위처럼 보여 압축되지 않는다'는 것 하나다.
    """
    stream = b"".join(hashlib.sha256(key + i.to_bytes(4, "big")).digest()
                      for i in range(len(data) // 32 + 1))
    return bytes(a ^ b for a, b in zip(data, stream))


class Channel(ABC):
    """[Component] 텔레메트리 전송 채널의 공통 인터페이스.

    데코레이터 패턴의 전제 조건이 바로 이 클래스다. 실제 채널과 모든 래퍼가 이 타입이므로
    클라이언트(센서 수집 루프)는 자기가 받은 것이 '맨 채널'인지 '다섯 겹 감싼 채널'인지 모른다.
    flush()를 인터페이스에 둔 이유: 배치처럼 내부에 데이터를 쥐고 있는 래퍼가 생기는 순간,
    '남은 것을 내보내라'는 요청도 체인 끝까지 전달되어야 하기 때문이다.
    """

    @abstractmethod
    def send(self, payload: bytes) -> None:
        """페이로드 하나를 전송한다."""

    @abstractmethod
    def flush(self) -> None:
        """버퍼에 남은 것을 모두 내보낸다. 버퍼가 없는 채널은 아무것도 하지 않는다."""


class MqttChannel(Channel):
    """[Concrete Component] 실제 전송. 데모를 위해 브로커 대신 보낸 크기를 기록한다."""

    def __init__(self) -> None:
        """전송 기록용 리스트."""
        self.sent_sizes: list[int] = []

    def send(self, payload: bytes) -> None:
        """MQTT publish를 흉내 낸다."""
        self.sent_sizes.append(len(payload))

    def flush(self) -> None:
        """MQTT 클라이언트 자체는 버퍼가 없다고 가정한다."""


class ChannelDecorator(Channel):
    """[Decorator] 다른 Channel을 감싸고, 기본적으로 모든 호출을 그대로 넘긴다.

    두 가지가 동시에 성립한다는 것이 핵심이다.
      - is-a Channel   (상속) → 다른 래퍼가 나를 다시 감쌀 수 있다(재귀적 합성).
      - has-a Channel  (합성) → 무엇을 감쌀지는 런타임에 정한다.
    상속은 '타입을 맞추려고' 쓰고, 기능 재사용은 합성으로 한다. 이 구분이 상속 조합 폭발과의 차이다.
    """

    def __init__(self, inner: Channel) -> None:
        """감쌀 채널. 구체 타입이 아니라 Channel 추상에 의존한다."""
        self._inner = inner

    def send(self, payload: bytes) -> None:
        """기본 동작은 위임. 서브클래스는 전/후에 자기 책임 하나만 덧붙인다."""
        self._inner.send(payload)

    def flush(self) -> None:
        """flush도 반드시 위임한다. 이걸 빠뜨리면 체인 안쪽의 배치 버퍼가 영원히 안 비워진다."""
        self._inner.flush()


class CompressingChannel(ChannelDecorator):
    """[Concrete Decorator] 압축. SRP: 이 클래스는 zlib 말고는 아무것도 모른다."""

    def send(self, payload: bytes) -> None:
        """압축한 뒤 안쪽으로 넘긴다(전처리형 데코레이터)."""
        self._inner.send(zlib.compress(payload, level=9))


class EncryptingChannel(ChannelDecorator):
    """[Concrete Decorator] 암호화. 키는 래퍼 인스턴스마다 다르게 줄 수 있다."""

    def __init__(self, inner: Channel, key: bytes) -> None:
        """래퍼가 자기 설정(키)을 가질 수 있다는 점이 함수 플래그보다 나은 점이다."""
        super().__init__(inner)
        self._key = key

    def send(self, payload: bytes) -> None:
        """암호화 후 안쪽으로."""
        self._inner.send(toy_encrypt(payload, self._key))


class BatchingChannel(ChannelDecorator):
    """[Concrete Decorator] n건을 모아 한 번에 보낸다. 상태(버퍼)를 가진 데코레이터의 예.

    상태를 가진 래퍼는 flush()를 '자기 일을 한 뒤' 위임해야 한다. 순서가 바뀌면
    안쪽이 먼저 비워진 뒤에 내가 데이터를 내려보내 그 데이터가 다시 갇힌다.
    """

    def __init__(self, inner: Channel, size: int) -> None:
        """배치 크기와 버퍼."""
        super().__init__(inner)
        self._size = size
        self._buffer: list[bytes] = []

    def send(self, payload: bytes) -> None:
        """버퍼가 차면 줄바꿈으로 이어 붙여 한 번에 보낸다."""
        self._buffer.append(payload)
        if len(self._buffer) >= self._size:
            self._emit()

    def _emit(self) -> None:
        """버퍼 내용을 하나의 페이로드로 묶어 안쪽에 넘긴다."""
        if self._buffer:
            self._inner.send(b"\n".join(self._buffer))
            self._buffer.clear()

    def flush(self) -> None:
        """내 버퍼를 먼저 비우고, 그다음 안쪽에 flush를 전파한다."""
        self._emit()
        self._inner.flush()


class LoggingChannel(ChannelDecorator):
    """[Concrete Decorator] 통과하는 페이로드 크기를 기록한다.

    label을 받는 이유: 같은 래퍼를 체인의 여러 위치에 꽂아 '압축 전'과 '압축 후'를
    동시에 관찰할 수 있다. 플래그 방식에서는 로그 위치가 코드에 고정되어 불가능했다.
    """

    def __init__(self, inner: Channel, label: str) -> None:
        """로그 접두어."""
        super().__init__(inner)
        self._label = label

    def send(self, payload: bytes) -> None:
        """기록 후 그대로 위임(관찰형 데코레이터 — 데이터를 바꾸지 않는다)."""
        print(f"    [log:{self._label}] {len(payload)} bytes")
        self._inner.send(payload)


def reading(i: int) -> bytes:
    """토양 수분 센서 측정값 하나(JSON)."""
    return json.dumps({"sensor": "soil-07", "seq": i, "moisture": 31.5 + i % 3, "unit": "%"}).encode()


def collect(channel: Channel, n: int) -> None:
    """[Client] 센서 수집 루프. channel이 몇 겹으로 감싸였는지 전혀 모른다."""
    for i in range(n):
        channel.send(reading(i))
    channel.flush()


if __name__ == "__main__":
    print("[1] 농장 A: 배치(10) → 로그(원본) → 압축 → 로그(압축 후) → 암호화 → MQTT")
    mqtt = MqttChannel()
    # 바깥쪽 래퍼가 '먼저' 실행된다. 코드를 바깥→안쪽으로 읽으면 곧 처리 순서다.
    farm_a = BatchingChannel(
        LoggingChannel(
            CompressingChannel(
                LoggingChannel(
                    EncryptingChannel(mqtt, key=b"farm-a"),
                    label="압축 후")),
            label="배치 원본"),
        size=10)
    collect(farm_a, 25)   # 10 + 10 + 5(flush로 내보냄)
    print(f"    MQTT가 받은 크기: {mqtt.sent_sizes}")

    print("[2] 농장 B: 로그만 필요 — 같은 클래스들로 다른 조합, 새 클래스 없음")
    mqtt_b = MqttChannel()
    collect(LoggingChannel(mqtt_b, label="raw"), 2)

    print("[3] 순서가 의미를 바꾼다: 압축→암호화 vs 암호화→압축 (배치 10건 1묶음)")
    for name, build in [
        ("압축→암호화", lambda m: CompressingChannel(EncryptingChannel(m, b"k"))),
        ("암호화→압축", lambda m: EncryptingChannel(CompressingChannel(m), b"k")),
    ]:
        sink = MqttChannel()
        collect(BatchingChannel(build(sink), size=10), 10)
        print(f"    {name}: {sink.sent_sizes[0]} bytes")
    raw = sum(len(reading(i)) for i in range(10)) + 9   # 줄바꿈 9개
    print(f"    (원본 {raw} bytes. 암호문은 무작위처럼 보여 압축이 거의 안 된다)")
