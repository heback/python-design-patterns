"""06 데코레이터 — 순진한 코드: 플래그 하나하나를 send() 안의 if로 처리한다.

상황: 들빛팜의 수집 장치는 센서 측정값을 MqttChannel로 보낸다. 압축·암호화·배치·로그
요구가 쌓이자 준호는 send()에 플래그를 하나씩 늘렸다. 조합마다 서브클래스를 만드는
방법은 이미 포기했다(기능 넷이면 클래스 16개). 이 코드는 플래그 방식의 문제를 보여 준다.
"""
from __future__ import annotations

import hashlib
import json
import zlib


def toy_encrypt(data: bytes, key: bytes = b"farm-key") -> bytes:
    """교육용 스트림 암호. 출력이 무작위처럼 보여 압축이 안 된다는 성질만 필요하다."""
    stream = b"".join(hashlib.sha256(key + i.to_bytes(4, "big")).digest()
                      for i in range(len(data) // 32 + 1))
    return bytes(a ^ b for a, b in zip(data, stream))


class FlagMqttChannel:
    """기능을 플래그로 켜고 끄는 전송 채널."""

    def __init__(self, compress: bool = False, encrypt: bool = False,
                 batch_size: int = 1, log: bool = False) -> None:
        """플래그를 받는다. 기능이 하나 늘 때마다 이 목록도 는다."""
        # ⚠ 문제: 새 기능(재시도 등)이 오면 이 클래스를 열어 고쳐야 한다(OCP 위반).
        self.compress, self.encrypt, self.log = compress, encrypt, log
        self.batch_size = batch_size
        self._buffer: list[bytes] = []
        self.sent_sizes: list[int] = []

    def send(self, payload: bytes) -> None:
        """배치 → 압축 → 암호화 → 로그 → 전송을 한 메서드에서 한다."""
        # 배치: batch_size건이 찰 때까지 모아 두기만 한다.
        self._buffer.append(payload)
        if len(self._buffer) < self.batch_size:
            return
        data = b"\n".join(self._buffer)
        self._buffer.clear()
        # ⚠ 문제: "압축은 암호화보다 먼저"라는 규칙이 아래 두 if의 줄 순서에만 숨어 있다.
        if self.compress:
            data = zlib.compress(data)
        if self.encrypt:
            data = toy_encrypt(data)
        # ⚠ 문제: 로그 위치가 고정되어 '압축 전 크기'를 보고 싶어도 볼 수 없다.
        if self.log:
            print(f"    [log] {len(data)} bytes")
        self.sent_sizes.append(len(data))   # MQTT 전송 흉내


def reading(i: int) -> bytes:
    """토양 수분 측정값 하나(JSON 바이트)."""
    return json.dumps({"sensor": "soil-07", "seq": i, "moisture": 31.5 + i % 3}).encode()


if __name__ == "__main__":
    print("[1] 조합마다 서브클래스를 만들면 필요한 클래스 수:", 2 ** 4)
    # 호출하는 쪽은 플래그 네 개의 뜻과 조합 규칙을 모두 알아야 한다.
    ch = FlagMqttChannel(compress=True, encrypt=True, batch_size=10, log=True)
    print("[2] 배치+압축+암호화+로그로 20건 전송 — 동작은 한다")
    for i in range(20):
        ch.send(reading(i))
    print(f"    전송 크기: {ch.sent_sizes}")
