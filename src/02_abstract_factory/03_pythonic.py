"""파이썬다운 변형: Protocol 제품 + frozen dataclass '생성 함수 번들' + composition root.

상황: 02_abstract_factory.py는 추상 팩토리 1개, 구체 팩토리 3개, 추상 제품 3개, 구체 제품 9개로
제품군을 표현했다. 도현의 팀은 "클래스가 너무 많다"고 느꼈다. 파이썬에서는
(1) 벤더 SDK 래퍼가 우리 ABC를 상속하지 않아도 되도록 제품 인터페이스를 Protocol로 두고,
(2) 팩토리를 클래스 계층 대신 '생성 함수 세 개를 묶은 불변 값'으로 표현할 수 있다.

이 파일이 함께 보여주는 비판적 지점: 번들은 '데이터'라서 누구나 필드를 섞어 새 번들을
만들 수 있다. 클래스 계층이 구조로 보장하던 제품군 일관성이 사라지므로, 그 보장을
__post_init__ 검증으로 되찾아야 한다. 이 비용이 클래스 계층이 여전히 필요한 이유이기도 하다.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, replace
from typing import Callable, Protocol


# ---------------------------------------------------------------------------
# Abstract Product — 구조적 타이핑. 벤더 래퍼는 아무것도 상속하지 않는다.
# ---------------------------------------------------------------------------

class BlobStorage(Protocol):
    """[Abstract Product] 저장소. provider 속성으로 소속 제품군을 밝힌다."""

    provider: str

    def put(self, key: str, data: bytes) -> str:
        """저장하고 URL을 돌려준다."""
        ...

    def get(self, url: str) -> bytes:
        """URL로 읽는다."""
        ...


class MessageQueue(Protocol):
    """[Abstract Product] 큐."""

    provider: str

    def publish(self, message: dict[str, str]) -> None:
        """메시지를 넣는다."""
        ...

    def pull(self) -> dict[str, str]:
        """메시지를 꺼낸다."""
        ...


# ---------------------------------------------------------------------------
# Concrete Product — 예제를 짧게 하려고 제품 종류를 저장소·큐 두 가지로 줄였다.
# ---------------------------------------------------------------------------

class SchemeStorage:
    """[Concrete Product] URL 형식(s3/gs/file)만 다른 저장소. Protocol을 상속하지 않는다."""

    def __init__(self, provider: str, scheme: str) -> None:
        """provider는 검증용 소속 표시, scheme은 이 제품군이 쓰는 URL 형식."""
        self.provider, self.scheme = provider, scheme
        self._bucket: dict[str, bytes] = {}

    def put(self, key: str, data: bytes) -> str:
        """저장한다."""
        self._bucket[key] = data
        return f"{self.scheme}://uploads/{key}"

    def get(self, url: str) -> bytes:
        """자기 형식의 URL만 읽는다."""
        prefix = f"{self.scheme}://uploads/"
        if not url.startswith(prefix):
            raise ValueError(f"{self.provider} 저장소는 이 URL을 읽을 수 없음: {url}")
        return self._bucket[url.removeprefix(prefix)]


class ListQueue:
    """[Concrete Product] 리스트 기반 큐(SQS·Pub/Sub·인메모리를 흉내 냄)."""

    def __init__(self, provider: str) -> None:
        """소속 제품군을 기록한다."""
        self.provider = provider
        self._items: list[dict[str, str]] = []

    def publish(self, message: dict[str, str]) -> None:
        """넣는다."""
        self._items.append(message)

    def pull(self) -> dict[str, str]:
        """꺼낸다."""
        return self._items.pop(0)


# ---------------------------------------------------------------------------
# Abstract Factory 대신: 생성 함수 번들
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class CloudKit:
    """[Abstract Factory 역할을 값으로] 제품군 하나의 생성 함수 묶음.

    frozen=True인 이유: 실행 중에 kit.storage만 다른 클라우드로 갈아 끼우는 일을 막는다.
    필드 타입이 Callable이라 클래스, 람다, partial, 클로저 무엇이든 생성 함수가 될 수 있다.
    """

    provider: str
    storage: Callable[[], BlobStorage]
    queue: Callable[[], MessageQueue]

    def __post_init__(self) -> None:
        """제품군 일관성 검증 — 클래스 계층에서는 '구조'가 하던 일을 여기서 '검사'로 한다.

        생성 함수를 한 번씩 호출해 시험 제품의 provider를 확인한다. 생성이 비싸거나
        부수 효과가 있다면 이 방식은 쓸 수 없다는 점도 이 변형의 한계다.
        """
        for name in ("storage", "queue"):
            made = getattr(self, name)()
            if made.provider != self.provider:
                raise ValueError(f"제품군 불일치: {self.provider} 키트에 {made.provider} {name}")


def aws_kit() -> CloudKit:
    """[Concrete Factory 역할] AWS 제품군. 클래스 대신 함수 하나가 번들을 만든다.

    저장소·큐 인스턴스를 클로저로 하나씩 공유해, 같은 키트에서 나온 제품들이 같은
    '계정'을 보게 한다(02의 CloudAccount 공유와 같은 효과).
    """
    storage, queue = SchemeStorage("aws", "s3"), ListQueue("aws")
    return CloudKit("aws", storage=lambda: storage, queue=lambda: queue)


def gcp_kit() -> CloudKit:
    """[Concrete Factory 역할] GCP 제품군."""
    storage, queue = SchemeStorage("gcp", "gs"), ListQueue("gcp")
    return CloudKit("gcp", storage=lambda: storage, queue=lambda: queue)


def local_kit() -> CloudKit:
    """[Concrete Factory 역할] 로컬 제품군."""
    storage, queue = SchemeStorage("local", "file"), ListQueue("local")
    return CloudKit("local", storage=lambda: storage, queue=lambda: queue)


# 환경 이름 → 키트 생성 함수. 새 환경 추가는 함수 하나 + 이 표의 한 줄.
KITS: dict[str, Callable[[], CloudKit]] = {"aws": aws_kit, "gcp": gcp_kit, "local": local_kit}


def composition_root() -> CloudKit:
    """[Composition Root] 환경 변수를 읽는 곳은 프로그램 전체에서 여기 하나다.

    서비스 코드가 os.environ을 직접 읽으면 01_naive.py의 '생성 지점마다 분기'가 되살아난다.
    기본값을 local로 둔 이유: 설정을 빠뜨린 개발자가 실수로 운영 클라우드를 건드리지 않게.
    """
    return KITS[os.environ.get("CLOUD_ENV", "local")]()


def upload_and_process(kit: CloudKit, key: str) -> str:
    """[Client] 업로드 → 큐 → 처리. 서비스 클래스 대신 함수로 줄였다(관심은 키트에 있으므로)."""
    storage, queue = kit.storage(), kit.queue()
    queue.publish({"url": storage.put(key, b"\x89PNG....")})
    return f"{len(storage.get(queue.pull()['url']))} bytes 처리"


if __name__ == "__main__":
    print("[1] composition root가 환경 변수로 키트를 고른다")
    for env in ("aws", "gcp", "local"):
        os.environ["CLOUD_ENV"] = env
        kit = composition_root()
        print(f"  CLOUD_ENV={env:5} → {kit.provider} 키트, {upload_and_process(kit, 'cat.png')}")

    print("\n[2] 번들은 데이터라 누구나 섞을 수 있다 — 검증이 없었다면 01_naive.py로 돌아간다")
    aws, gcp = aws_kit(), gcp_kit()
    try:
        CloudKit("gcp", storage=gcp.storage, queue=aws.queue)  # GCP 저장소 + AWS 큐
    except ValueError as e:
        print(f"  __post_init__이 막음: {e}")

    print("\n[3] dataclasses.replace로 '하나만 바꾼' 키트도 같은 검증을 거친다")
    try:
        replace(aws, storage=gcp.storage)
    except ValueError as e:
        print(f"  replace도 막힘: {e}")
    print("  → 클래스 계층이 '구조'로 하던 보장을, 번들은 '실행 시 검사'로 흉내 낼 뿐이다")
