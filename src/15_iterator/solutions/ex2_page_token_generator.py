"""[15장 연습문제 2 해설] 페이지 토큰 while 루프를 제너레이터 기반 반복자로 바꾼다.

상황: 멜로디의 팟캐스트 탭은 '구독 중인 에피소드' API를 커서 토큰으로 페이지 단위로 받는다.
원래 코드(원고의 문제)는 토큰 루프 안에서 '안 들은 에피소드 5개 찾기'라는 업무 로직까지 처리했다.
그래서 같은 토큰 루프가 '전체 재생 시간 합계', '검색' 기능마다 복제되었다.

리팩터링 원칙: 순회(어떻게 가져오는가)와 소비(무엇을 할 것인가)를 분리한다.
  - `episodes(client)`: 토큰 루프만 아는 제너레이터.
  - 업무 로직: 평범한 for / itertools / 내장 함수. 토큰이라는 단어가 등장하지 않는다.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import islice
from typing import Iterator


@dataclass(frozen=True)
class Episode:
    """에피소드."""

    title: str
    minutes: int
    played: bool


class FakePodcastClient:
    """커서 기반 API 흉내. 페이지당 4개, 총 10개."""

    def __init__(self) -> None:
        """에피소드 데이터와 요청 카운터."""
        self._data = [Episode(f"EP{i}", 30 + i, played=(i % 3 == 0)) for i in range(10)]
        self.calls = 0

    def list_episodes(self, cursor: str | None) -> dict:
        """{'items': [...], 'next_cursor': str | None} 형태의 응답."""
        self.calls += 1
        start = int(cursor or 0)
        end = start + 4
        return {"items": self._data[start:end],
                "next_cursor": str(end) if end < len(self._data) else None}


def episodes(client: FakePodcastClient) -> Iterator[Episode]:
    """[Iterator] 토큰 루프는 프로그램 전체에서 여기 한 곳에만 있다."""
    cursor: str | None = None
    while True:
        resp = client.list_episodes(cursor)
        # 소비자가 이 페이지를 다 당겨 가기 전에는 아래 줄로 내려가지 않는다 → 다음 요청도 없다.
        yield from resp["items"]
        cursor = resp["next_cursor"]
        if cursor is None:
            return


def unplayed(client: FakePodcastClient, n: int) -> list[str]:
    """업무 로직 1: 안 들은 에피소드 n개. 필터는 제너레이터 식, 개수 제한은 islice."""
    return [e.title for e in islice((e for e in episodes(client) if not e.played), n)]


def total_minutes(client: FakePodcastClient) -> int:
    """업무 로직 2: 전체 재생 시간. sum()이 반복자를 끝까지 소비한다 — 이 경우엔 모든 페이지가 필요하다."""
    return sum(e.minutes for e in episodes(client))


if __name__ == "__main__":
    # 두 소비자가 같은 생산자(episodes)를 쓴다. 요청 수 차이는 소비자가 '얼마나 당겼는가'에서만 나온다.
    c = FakePodcastClient()
    print("[1] 안 들은 에피소드 3개:", unplayed(c, 3), f"/ API 호출 {c.calls}번 (전체 3페이지 중)")
    c.calls = 0
    print("[2] 전체 재생 시간:", total_minutes(c), f"분 / API 호출 {c.calls}번")
