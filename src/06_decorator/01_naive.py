"""06 데코레이터 — 순진한 설계: 상속 조합 폭발과 플래그 if 지옥.

상황: 스마트 농장 IoT 게이트웨이를 만드는 임베디드 개발자 준호는 토양 수분 센서 값을
MQTT 브로커로 보내는 MqttChannel.send(payload)를 만들었다. 그 뒤 요구가 쌓였다.
LTE 요금 때문에 압축, 보안 감사 때문에 암호화, 배터리 때문에 10건씩 묶는 배치,
장애 진단용 전송 로그. 농장마다 필요한 조합이 다르다.
준호가 시도한 두 방법을 차례로 본다.
  (A) 조합마다 서브클래스를 만든다 → 기능 n개면 클래스 2^n개.
  (B) 하나의 send()에 플래그를 넣는다 → if가 얽히고, 순서 규칙이 코드에 숨는다.
"""
from __future__ import annotations

import hashlib
import json
import zlib
from itertools import combinations


def toy_encrypt(data: bytes, key: bytes = b"farm-key") -> bytes:
    """교육용 스트림 암호(SHA-256 카운터 키스트림 XOR). 실제 제품에서는 AES-GCM 등을 써야 한다.

    여기서 중요한 성질은 하나뿐이다: 출력이 '무작위처럼' 보여서 더 이상 압축되지 않는다.
    """
    stream = b"".join(hashlib.sha256(key + i.to_bytes(4, "big")).digest()
                      for i in range(len(data) // 32 + 1))
    return bytes(a ^ b for a, b in zip(data, stream))


class MqttChannel:
    """원래의 전송 채널. 브로커 대신 보낸 바이트 수를 기록한다."""

    def __init__(self) -> None:
        """보낸 메시지 크기 목록을 기록할 리스트를 만든다."""
        self.sent_sizes: list[int] = []

    def send(self, payload: bytes) -> None:
        """MQTT publish를 흉내 낸다."""
        self.sent_sizes.append(len(payload))


# --- (A) 상속으로 조합하기 --------------------------------------------------

class CompressedMqttChannel(MqttChannel):
    """압축 기능을 상속으로 추가."""

    def send(self, payload: bytes) -> None:
        """압축 후 부모에게 넘긴다."""
        super().send(zlib.compress(payload))


class CompressedEncryptedMqttChannel(CompressedMqttChannel):
    """압축 + 암호화. ⚠ 문제: 이 순서를 지키려면 상속 계층 자체가 순서를 인코딩해야 한다."""

    def send(self, payload: bytes) -> None:
        """압축(부모)보다 '먼저' 실행되면 안 되므로 순서를 맞추느라 부모 호출을 비튼다."""
        # ⚠ 문제: 부모가 압축을 먼저 하게 하려면 여기서는 암호화를 '나중에' 해야 하는데,
        # super().send()는 압축 후 바로 브로커로 보내 버린다. 결국 압축 로직을 복제하게 된다.
        MqttChannel.send(self, toy_encrypt(zlib.compress(payload)))

# ⚠ 문제: EncryptedMqttChannel, BatchedMqttChannel, LoggedCompressedMqttChannel ...
# 기능 4개(압축·암호화·배치·로그)의 모든 부분집합마다 클래스가 하나씩 필요하다.


# --- (B) 플래그로 조합하기 --------------------------------------------------

class FlagMqttChannel:
    """한 클래스에 모든 옵션을 넣은 채널."""

    def __init__(self, *, compress: bool = False, encrypt: bool = False,
                 batch_size: int = 1, log: bool = False) -> None:
        """현장 설정 파일의 플래그를 그대로 받는다."""
        self.compress, self.encrypt, self.batch_size, self.log = compress, encrypt, batch_size, log
        self._buffer: list[bytes] = []
        self.sent_sizes: list[int] = []

    def send(self, payload: bytes) -> None:
        """모든 기능이 한 메서드 안에서 얽힌다."""
        # ⚠ 문제: 배치·압축·암호화·로그가 한 메서드에 섞여 있다. 새 기능(예: 재시도)을
        # 넣으려면 이 메서드를 다시 열어야 하고(OCP 위반), 어느 줄이 어느 기능인지 흐려진다.
        if self.batch_size > 1:
            self._buffer.append(payload)
            if len(self._buffer) < self.batch_size:
                return
            payload = b"\n".join(self._buffer)
            self._buffer.clear()
        if self.compress:
            payload = zlib.compress(payload)
        if self.encrypt:
            # ⚠ 문제: "압축은 반드시 암호화보다 먼저"라는 핵심 규칙이 if 두 개의 '줄 순서'에만
            # 암묵적으로 들어 있다. 누가 이 두 블록 순서를 바꿔도 테스트는 깨지지 않는다(크기만 커진다).
            payload = toy_encrypt(payload)
        if self.log:
            print(f"    [log] {len(payload)} bytes 전송")
        self.sent_sizes.append(len(payload))

    # ⚠ 문제: 농장 B는 "로그는 압축 전 원본 크기로" 찍고 싶어 한다. 플래그 방식으로는
    # 로그 위치를 바꿀 수 없다. 또 플래그가 하나 늘 때마다 검증해야 할 조합은 두 배가 된다.


def reading(i: int) -> bytes:
    """토양 수분 센서 측정값 하나(JSON). 필드 이름이 반복되어 압축이 잘 된다."""
    return json.dumps({"sensor": "soil-07", "seq": i, "moisture": 31.5 + i % 3, "unit": "%"}).encode()


if __name__ == "__main__":
    features = ["압축", "암호화", "배치", "로그"]
    combos = sum(1 for r in range(len(features) + 1) for _ in combinations(features, r))
    print(f"[1] 상속 방식: 기능 {len(features)}개 → 필요한 클래스 {combos}개 (2^{len(features)}, 기본 채널 포함)")

    print("[2] 상속 방식의 압축+암호화 채널")
    ch_a = CompressedEncryptedMqttChannel()
    ch_a.send(reading(0) * 5)
    print(f"    전송 크기: {ch_a.sent_sizes}")

    print("[3] 플래그 방식: 압축+암호화+배치(10)+로그")
    ch_b = FlagMqttChannel(compress=True, encrypt=True, batch_size=10, log=True)
    for i in range(10):
        ch_b.send(reading(i))
    print(f"    원본 합계 {sum(len(reading(i)) for i in range(10))} bytes → 전송 {ch_b.sent_sizes}")
    print("    (동작은 한다. 문제는 기능을 하나 더하거나 순서를 바꿀 때 드러난다)")
