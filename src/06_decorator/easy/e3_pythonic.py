"""06 데코레이터 — 파이썬다운 변형: 함수 래퍼, @ 문법, 설정 목록으로 체인 조립.

상황: 선배 미정이 묻는다. "send 하나짜리면 함수를 감싸면 되잖아. 파이썬엔 @도 있고."
이 코드는 (1) 같은 의도를 함수로 구현하고, (2) @ 문법이 그 함수를 정의 시점에
적용한다는 것, (3) 설정 파일의 이름 목록을 reduce로 접어 실행 중에 체인을 만드는 것을 보인다.
"""
from __future__ import annotations

import zlib
from functools import reduce
from typing import Callable

Send = Callable[[bytes], None]   # [Component] 메서드 하나짜리 인터페이스면 '함수 타입'이 곧 인터페이스다


def compressed(send: Send) -> Send:
    """[Concrete Decorator] Send를 받아 Send를 돌려준다. 같은 모양이라 몇 겹이든 감쌀 수 있다."""
    def wrapper(payload: bytes) -> None:
        """압축한 뒤 안쪽 함수에 넘긴다."""
        send(zlib.compress(payload))
    return wrapper


def logged(label: str) -> Callable[[Send], Send]:
    """설정(label)이 필요한 래퍼는 '래퍼를 만드는 함수'가 된다 — 한 겹 더 감싼다."""
    def deco(send: Send) -> Send:
        """label을 기억하는 래퍼를 만든다."""
        def wrapper(payload: bytes) -> None:
            """크기를 기록하고 그대로 넘긴다."""
            print(f"    [log:{label}] {len(payload)} bytes")
            send(payload)
        return wrapper
    return deco


def mqtt_send(payload: bytes) -> None:
    """[Concrete Component] 실제 전송 흉내."""
    print(f"    MQTT ← {len(payload)} bytes")


# (2) @ 문법: 아래 정의는 debug_send = logged("debug")(compressed(debug_send))와 같다.
@logged("debug")
@compressed
def debug_send(payload: bytes) -> None:
    """디버그 포트로 보내기. 조합이 소스 코드에 고정된다."""
    mqtt_send(payload)


# (3) 설정 파일의 문자열 목록 → 래퍼 함수. 새 기능은 함수 하나 + 항목 하나로 끝난다.
DECORATORS: dict[str, Callable[[Send], Send]] = {
    "compress": compressed, "log": logged("config"),
}


def build_chain(names: list[str], sink: Send) -> Send:
    """목록의 첫 이름이 가장 바깥이 되도록 뒤집어서 안쪽부터 감싼다."""
    return reduce(lambda inner, name: DECORATORS[name](inner), reversed(names), sink)


if __name__ == "__main__":
    data = b'{"sensor": "soil-07", "moisture": 31.5}' * 10
    print("[1] 함수 래퍼를 직접 겹치기: 로그 → 압축 → 전송")
    logged("raw")(compressed(mqtt_send))(data)
    print("[2] @ 문법으로 정의 시점에 감싼 함수")
    debug_send(data)
    print("[3] 설정 ['log', 'compress']로 실행 중에 체인 조립")
    build_chain(["log", "compress"], mqtt_send)(data)
