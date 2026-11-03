"""15 반복자 — 지연 페이지 로딩 코드: 서버의 페이지 API를 '그냥 이터러블'로 보이게 한다.

상황: '좋아요 표시한 곡'은 2만 곡이고, 서버는 50곡씩 페이지 토큰과 함께 준다.
모두 받아 리스트로 만들면 첫 곡 전에 요청이 400번 오간다. 사용자는 대개 앞의 몇 곡만 듣는다.
pages()는 같은 토큰 루프를 '모으기' 대신 '흘려보내기'로 바꿔, 필요한 페이지만 요청한다.
"""
from __future__ import annotations

from collections.abc import Iterable, Iterator
from itertools import islice


class FakeLikedSongsAPI:
    """서버 흉내. 요청 수를 센다."""

    def __init__(self, total: int) -> None:
        """total곡짜리 목록."""
        self.total, self.requests = total, 0

    def fetch_page(self, token: int | None) -> tuple[list[str], int | None]:
        """(이번 페이지 곡들, 다음 페이지 토큰). 마지막 페이지면 토큰이 None."""
        self.requests += 1
        start = token or 0
        end = min(start + 50, self.total)
        return [f"좋아요 #{i}" for i in range(start, end)], (end if end < self.total else None)


def all_at_once(api: FakeLikedSongsAPI) -> list[str]:
    """순진한 방식: 모든 페이지를 받아 리스트로 모은다."""
    songs: list[str] = []
    token: int | None = None
    while True:
        items, token = api.fetch_page(token)
        songs.extend(items)                  # 모으기
        if token is None:
            return songs


def pages(api: FakeLikedSongsAPI) -> Iterator[str]:
    """같은 루프, 한 단어 차이: extend 대신 yield from. 소비자가 멈추면 다음 요청도 멈춘다."""
    token: int | None = None
    while True:
        items, token = api.fetch_page(token)
        yield from items                     # 흘려보내기
        if token is None:
            return                           # 함수가 끝나면 StopIteration은 파이썬이 던진다


class LikedSongs:
    """[Aggregate] 다시 돌 수 있는 이터러블. __iter__가 부를 때마다 새 제너레이터를 만든다."""

    def __init__(self, api: FakeLikedSongsAPI) -> None:
        """API만 보관한다. 곡 데이터는 보관하지 않는다."""
        self.api = api

    def __iter__(self) -> Iterator[str]:
        """호출마다 새 순회 — 제너레이터 '객체'를 넘기면 한 번밖에 못 돈다."""
        return pages(self.api)


def play_first(tracks: Iterable[str], n: int) -> list[str]:
    """[Client] 매개변수 타입이 list가 아니라 Iterable이다. 리스트든 페이지 API든 모른다."""
    return list(islice(tracks, n))           # islice는 n개를 받으면 더 묻지 않는다


if __name__ == "__main__":
    print("[1] 앞의 3곡만 듣는다: 모두 받기 vs 흘려보내기")
    a, b = FakeLikedSongsAPI(20_000), FakeLikedSongsAPI(20_000)
    play_first(all_at_once(a), 3)
    play_first(LikedSongs(b), 3)
    print(f"    요청 수: 모두 받기 {a.requests}번, 흘려보내기 {b.requests}번")
    print("[2] LikedSongs는 두 번 돌려도 매번 처음부터")
    small = LikedSongs(FakeLikedSongsAPI(3))
    print(f"    {list(small)} / {list(small)}")
    print("[3] 제너레이터 객체를 담아 두고 두 번 쓰면, 두 번째는 조용히 비어 있다")
    gen = pages(FakeLikedSongsAPI(3))
    print(f"    곡 수 {sum(1 for _ in gen)}, 제목 목록 {list(gen)}")
