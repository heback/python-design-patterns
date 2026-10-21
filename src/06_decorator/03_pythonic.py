"""06 데코레이터 — 파이썬다운 변형: 함수 데코레이터, @ 문법, reduce 조립, __getattr__ 위임의 함정.

상황: 게이트웨이 펌웨어 팀의 선배 미정은 준호의 클래스 체인을 보고 묻는다. "send 하나뿐인
인터페이스라면 그냥 함수를 감싸면 되지 않아? 파이썬엔 @ 데코레이터도 있잖아."
이 파일은 그 질문을 따라가며 네 가지를 확인한다.
  (1) 함수 래퍼로 같은 의도(같은 시그니처 유지 + 책임 추가 + 중첩)를 구현할 수 있다.
  (2) @ 문법은 '정의 시점에 이름을 다시 묶는' 설탕일 뿐이며, GoF 패턴이 아닌 용도로도 쓰인다.
  (3) 현장 설정 파일의 목록으로부터 런타임에 체인을 조립하려면 functools.reduce가 알맞다.
  (4) 메서드가 많은 객체를 __getattr__로 투명하게 감싸면 특수 메서드·isinstance에서 구멍이 난다.
"""
from __future__ import annotations

import hashlib
import zlib
from functools import reduce, wraps
from typing import Any, Callable

Send = Callable[[bytes], None]
"""[Component] 함수 버전의 '인터페이스'. 메서드가 send 하나뿐이면 타입은 곧 함수 시그니처다."""


def toy_encrypt(data: bytes, key: bytes) -> bytes:
    """교육용 스트림 암호(02와 같은 SHA-256 카운터 키스트림 XOR). 실제로는 검증된 암호 라이브러리를 쓴다.

    02와 같은 방식을 쓰는 이유: 출력이 무작위처럼 보여야 build_send로 순서를 바꿔 실험할 때
    "암호문은 압축되지 않는다"는 본문의 관찰이 그대로 재현된다. 반복 키 XOR은 출력이 주기적이라 압축된다.
    """
    stream = b"".join(hashlib.sha256(key + i.to_bytes(4, "big")).digest()
                      for i in range(len(data) // 32 + 1))
    return bytes(a ^ b for a, b in zip(data, stream))


# --- (1) 함수 래퍼: 같은 시그니처를 받아 같은 시그니처를 돌려준다 ------------

def compressed(send: Send) -> Send:
    """[Concrete Decorator] 압축. Send를 받아 Send를 돌려주므로 몇 겹이든 중첩된다.

    @wraps를 쓰는 이유: 래퍼 함수가 원래 함수의 __name__, __doc__을 물려받고
    __wrapped__로 원본에 접근할 수 있게 된다. 디버깅·로그에서 'wrapper'만 보이는 일을 막는다.
    """
    @wraps(send)
    def wrapper(payload: bytes) -> None:
        """압축 후 원래 send 호출."""
        send(zlib.compress(payload))
    return wrapper


def encrypted(key: bytes) -> Callable[[Send], Send]:
    """[Concrete Decorator 팩토리] 설정(키)이 필요한 래퍼는 '래퍼를 만드는 함수'가 된다.

    클래스 버전의 EncryptingChannel(inner, key)에서 생성자 인자였던 것이
    함수 버전에서는 바깥 클로저 한 겹으로 옮겨간다. @encrypted(b"k")처럼 괄호가 붙는 이유다.
    """
    def decorate(send: Send) -> Send:
        """키를 기억하는 래퍼를 만든다."""
        @wraps(send)
        def wrapper(payload: bytes) -> None:
            """암호화 후 원래 send 호출."""
            send(toy_encrypt(payload, key))
        return wrapper
    return decorate


def logged(label: str) -> Callable[[Send], Send]:
    """[Concrete Decorator 팩토리] 크기 로그."""
    def decorate(send: Send) -> Send:
        """라벨을 기억하는 래퍼를 만든다."""
        @wraps(send)
        def wrapper(payload: bytes) -> None:
            """크기를 출력하고 그대로 넘긴다."""
            print(f"    [log:{label}] {len(payload)} bytes")
            send(payload)
        return wrapper
    return decorate


# --- (2) @ 문법: 정의 시점에 한 번 적용되고 이름이 다시 묶인다 ----------------

@logged("debug")
@compressed
def send_to_debug_port(payload: bytes) -> None:
    """시리얼 디버그 포트로 내보낸다(흉내).

    위 두 줄은 정확히 send_to_debug_port = logged("debug")(compressed(send_to_debug_port))다.
    아래쪽(@compressed)이 먼저 적용되어 안쪽이 되고, 위쪽(@logged)이 바깥이 된다.
    따라서 호출 시에는 위에서 아래 순서로 실행된다 — 객체 체인을 바깥→안쪽으로 읽는 것과 같다.
    """
    print(f"    (debug port) {len(payload)} bytes 기록")


PARSERS: dict[str, Callable[[bytes], dict]] = {}


def register(kind: str) -> Callable[[Callable[[bytes], dict]], Callable[[bytes], dict]]:
    """@ 문법이지만 GoF 데코레이터가 '아닌' 예: 함수를 감싸지 않고 등록만 하고 그대로 돌려준다.

    @ 는 '함수를 받아 무언가를 돌려주는 호출'을 정의 지점에 붙이는 문법일 뿐이다.
    감싸기(책임 추가)를 하든, 등록만 하든, 전혀 다른 객체(property 등)를 돌려주든 문법은 상관하지 않는다.
    """
    def deco(fn: Callable[[bytes], dict]) -> Callable[[bytes], dict]:
        """레지스트리에 넣고 원본을 그대로 반환한다."""
        PARSERS[kind] = fn
        return fn
    return deco


@register("soil")
def parse_soil(raw: bytes) -> dict:
    """토양 센서 원시값 파서(등록 데코레이터의 대상)."""
    return {"moisture": int(raw) / 10}


# --- (3) 런타임 조립: 설정 파일의 목록 → reduce로 체인 -----------------------

DECORATORS: dict[str, Callable[[Send], Send]] = {
    "compress": compressed,
    "encrypt": encrypted(b"farm-c"),
    "log": logged("cfg"),
}


def build_send(config: list[str], base: Send) -> Send:
    """설정의 목록 순서 = 처리 순서(바깥 → 안쪽)가 되도록 조립한다.

    reduce는 왼쪽부터 접으므로, 목록을 뒤집어 '가장 안쪽'부터 감싸야 첫 항목이 가장 바깥이 된다.
    @ 문법은 소스 코드에 순서가 고정되지만, 이 방식은 현장 설정 파일만 바꾸면 순서가 바뀐다.
    이것이 '정의 시점'(@)과 '런타임'(GoF 객체 합성)의 차이를 함수로도 메울 수 있는 지점이다.
    """
    return reduce(lambda inner, name: DECORATORS[name](inner), reversed(config), base)


# --- (4) 인터페이스가 넓을 때의 __getattr__ 투명 위임과 그 함정 ---------------

class MqttClient:
    """메서드가 많은 실제 클라이언트(흉내). send 외에도 connect, 컨텍스트 매니저, len을 지원한다."""

    def __init__(self) -> None:
        """대기열."""
        self.queue: list[bytes] = []

    def connect(self) -> str:
        """연결."""
        return "connected"

    def send(self, payload: bytes) -> None:
        """대기열에 넣는다."""
        self.queue.append(payload)

    def __len__(self) -> int:
        """대기 중인 메시지 수."""
        return len(self.queue)

    def __enter__(self) -> MqttClient:
        """with 블록 진입."""
        return self

    def __exit__(self, *exc: object) -> None:
        """with 블록 종료."""


class TransparentLogging:
    """[Decorator] send만 가로채고 나머지는 __getattr__로 넘기는 '투명' 래퍼.

    메서드를 일일이 위임하지 않아도 되어 편하지만, 두 군데서 투명하지 않다.
      - len(), with 같은 특수 메서드는 인스턴스가 아니라 '타입'에서 찾으므로 __getattr__을 타지 않는다.
      - 상속 관계가 없으므로 isinstance(wrapper, MqttClient)가 거짓이다.
    """

    def __init__(self, inner: MqttClient) -> None:
        """감쌀 클라이언트."""
        self._inner = inner

    def send(self, payload: bytes) -> None:
        """로그를 남기고 위임."""
        print(f"    [log] {len(payload)} bytes")
        self._inner.send(payload)

    def __getattr__(self, name: str) -> Any:
        """정의되지 않은 '일반' 속성 조회만 여기로 온다."""
        return getattr(self._inner, name)


if __name__ == "__main__":
    sent: list[int] = []

    def mqtt_send(payload: bytes) -> None:
        """기본 전송 함수(Concrete Component)."""
        sent.append(len(payload))

    data = b'{"sensor":"soil-07","moisture":31.5}' * 10

    print("[1] 함수 래퍼 중첩: logged(compressed(encrypted(mqtt_send)))")
    chain = logged("in")(compressed(encrypted(b"k")(mqtt_send)))
    chain(data)
    print(f"    MQTT 수신 크기 {sent}, 바깥 래퍼의 __name__ = {chain.__name__!r} (wraps 덕분)")

    print("[2] @ 문법은 정의 시점 1회 적용 — 이름 send_to_debug_port가 래퍼를 가리킨다")
    send_to_debug_port(data)
    print(f"    __wrapped__ 로 한 겹 벗기면: {send_to_debug_port.__wrapped__.__name__} (compressed 래퍼)")
    print(f"    등록 데코레이터: PARSERS = {list(PARSERS)}, parse_soil은 감싸지지 않음 → {PARSERS['soil'] is parse_soil}")

    print("[3] 설정 목록으로 런타임 조립 — 순서만 바꿔 본다")
    for cfg in (["log", "compress", "encrypt"], ["compress", "log", "encrypt"]):
        sent.clear()
        print(f"    config={cfg}")
        build_send(cfg, mqtt_send)(data)

    print("[4] __getattr__ 투명 래퍼의 구멍")
    w = TransparentLogging(MqttClient())
    print(f"    w.connect() → {w.connect()}  (일반 메서드는 위임된다)")
    w.send(b"x" * 40)
    try:
        len(w)
    except TypeError as e:
        print(f"    len(w) 실패 → TypeError: {e}")
    try:
        with w:   # 내부적으로 type(w).__enter__ 를 찾는다 — 인스턴스의 __getattr__은 무시된다
            pass
    except TypeError as e:
        print(f"    with w: 실패 → TypeError: {e}")
    print(f"    isinstance(w, MqttClient) = {isinstance(w, MqttClient)}")
