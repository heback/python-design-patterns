"""02 추상 팩토리 — 파이썬다운 변형: 팩토리 계층 대신 '생성 함수 묶음' 하나.

상황: 패턴 코드는 추상 4개, 구체 팩토리 3개, 구체 제품 9개로 무겁다. 여기서는
팩토리를 생성 함수 두 개를 담은 frozen 데이터클래스 CloudKit으로 바꾼다.
대가: 묶음은 데이터라 누구나 섞어 만들 수 있으므로, 검사를 직접 넣어야 한다.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


class SchemeStorage:
    """저장소 하나. 어느 클라우드 것인지(provider)를 스스로 밝힌다."""

    def __init__(self, provider: str, scheme: str) -> None:
        """provider는 아래 검사에 쓰인다. 제품이 정직하게 밝힌다는 약속에 기댄다."""
        self.provider, self.scheme = provider, scheme

    def put(self, key: str) -> str:
        """파일을 올리고 주소를 돌려준다."""
        return f"{self.scheme}://bucket/{key}"


class ListQueue:
    """큐 하나. 역시 provider를 밝힌다."""

    def __init__(self, provider: str) -> None:
        """어느 클라우드의 큐인지 기록한다."""
        self.provider = provider


@dataclass(frozen=True)
class CloudKit:
    """[Abstract Factory 역할] 한 클라우드의 생성 함수 묶음."""

    provider: str
    storage: Callable[[], SchemeStorage]
    queue: Callable[[], ListQueue]

    def __post_init__(self) -> None:
        """클래스 계층이 '타입'으로 막던 섞임을 여기서 실행 중에 검사한다."""
        made = {self.storage().provider, self.queue().provider}  # 검사하려면 한 번 만들어 봐야 한다
        if made != {self.provider}:
            raise ValueError(f"{self.provider} 묶음에 다른 클라우드 제품이 섞임: {sorted(made)}")


def aws_kit() -> CloudKit:
    """[Concrete Factory 역할] AWS 묶음을 만든다."""
    return CloudKit("aws", lambda: SchemeStorage("aws", "s3"), lambda: ListQueue("aws"))


def gcp_kit() -> CloudKit:
    """[Concrete Factory 역할] GCP 묶음을 만든다."""
    return CloudKit("gcp", lambda: SchemeStorage("gcp", "gs"), lambda: ListQueue("gcp"))


if __name__ == "__main__":
    print("[1] 묶음 하나를 고르면 제품이 모두 같은 클라우드다")
    kit = gcp_kit()
    print(f"  {kit.provider}: {kit.storage().put('cat.png')}")

    print("[2] 묶음은 데이터라 섞어 만들 수 있다 — 검사가 없으면 순진한 코드로 돌아간다")
    try:
        CloudKit("gcp", storage=gcp_kit().storage, queue=aws_kit().queue)
    except ValueError as e:
        print(f"  __post_init__이 막음: {e}")
