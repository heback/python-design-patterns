"""[15장 반복자 · 지연 평가] 서버의 페이지 API를 '그냥 이터러블'로 보이게 한다.

상황: '좋아요 표시한 곡'은 수만 곡이고, 서버는 50곡씩 페이지 토큰과 함께 준다. 01에서는
첫 곡을 틀기 전에 400번 요청해 2만 곡을 메모리에 올렸다. 사용자는 대개 앞의 몇 곡만 듣는다.

이 파일의 설계:
  - `pages()`: 페이지 토큰 루프를 감춘 제너레이터. 다음 페이지는 '필요해진 순간'에만 요청한다.
  - `LikedSongs`: `__iter__`가 제너레이터인 이터러블. for를 돌 때마다 처음부터 새로 순회한다.
    Player는 이것이 리스트인지 페이지 API인지 모른다 — 반복자 패턴의 원래 목적(내부 표현 은닉).
  - 데모 후반은 '제너레이터 객체를 변수에 담아 두 번 쓰는' 고갈(exhaustion) 버그와
    `in` 연산자가 반복자를 소비하는 함정을 재현한다.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import islice
from typing import Iterable, Iterator


@dataclass(frozen=True)
class Track:
    """곡 하나."""

    title: str


class FakeLikedSongsAPI:
    """서버 페이지네이션 API 흉내. 요청 수를 센다."""

    PAGE_SIZE = 50

    def __init__(self, total: int) -> None:
        """total곡짜리 목록."""
        self.total = total
        self.requests = 0

    def fetch_page(self, token: int | None) -> tuple[list[Track], int | None]:
        """(곡들, 다음 토큰). 마지막이면 토큰 None."""
        self.requests += 1
        start = token or 0
        end = min(start + self.PAGE_SIZE, self.total)
        return [Track(f"좋아요 #{i}") for i in range(start, end)], (end if end < self.total else None)


def pages(api: FakeLikedSongsAPI) -> Iterator[Track]:
    """페이지 토큰 루프를 감춘 제너레이터. 01의 while 루프와 거의 같은 모양이다.

    차이는 '모으기(extend)' 대신 '흘려보내기(yield from)'라는 한 단어다. 그 한 단어 덕분에
    소비자가 멈추면 생산도 멈춘다 — 다음 페이지 요청은 이전 페이지를 다 소비한 뒤에야 일어난다.
    """
    token: int | None = None
    while True:
        items, token = api.fetch_page(token)
        yield from items
        if token is None:
            return                      # 함수가 끝나면 StopIteration은 파이썬이 대신 던진다


class LikedSongs:
    """[Aggregate] 재사용 가능한 이터러블. __iter__가 매번 새 제너레이터를 만든다.

    제너레이터 함수 pages()를 바로 넘기지 않고 이 클래스로 감싸는 이유: 제너레이터 '객체'는
    이터레이터라서 한 번만 순회할 수 있다. 재생 화면과 '전체 재생 시간 계산' 같은 두 소비자가
    각자 처음부터 돌 수 있어야 한다면, 반복자를 '만드는 것'을 넘겨야 한다.
    """

    def __init__(self, api: FakeLikedSongsAPI) -> None:
        """API 클라이언트를 보관한다. 데이터는 보관하지 않는다."""
        self.api = api

    def __iter__(self) -> Iterator[Track]:
        """[팩토리 메서드] 호출마다 새 순회 — 그래서 for를 몇 번 돌려도 된다."""
        return pages(self.api)


def play_first(tracks: Iterable[Track], n: int) -> list[str]:
    """[Client] 이 함수는 tracks가 list인지, 페이지 API인지, 제너레이터인지 모른다.

    타입 힌트가 list가 아니라 Iterable이라는 점이 곧 설계다. 01의 Player가 list에 묶였던 것과 대비.
    """
    return [t.title for t in islice(tracks, n)]


if __name__ == "__main__":
    print("[1] 지연 평가: 앞의 3곡만 들으면 요청은 1번")
    api = FakeLikedSongsAPI(total=20_000)
    liked = LikedSongs(api)
    print("    ", play_first(liked, 3), f"/ 요청 {api.requests}번 (01에서는 400번)")

    print("[2] 120곡까지 들으면 그때 필요한 만큼만 더 받는다")
    api.requests = 0
    play_first(liked, 120)
    print(f"     요청 {api.requests}번 (50곡 × 3페이지)")

    print("[3] 같은 클라이언트 함수가 리스트에도 그대로 동작한다 — 내부 표현 은닉")
    print("    ", play_first([Track("Intro"), Track("Blue")], 3))

    print("[4] LikedSongs는 이터러블: 두 번 돌려도 매번 처음부터")
    small = LikedSongs(FakeLikedSongsAPI(total=3))
    print("    ", [t.title for t in small], [t.title for t in small])

    print("[5] 고갈 버그: 제너레이터 '객체'를 담아 두고 두 번 쓰면 두 번째는 비어 있다")
    gen = pages(FakeLikedSongsAPI(total=3))
    total = sum(1 for _ in gen)                  # 첫 소비자: 곡 수 세기
    titles = [t.title for t in gen]              # 두 번째 소비자: 이미 고갈됨
    print(f"     곡 수 {total}, 제목 목록 {titles} ← 예외 없이 조용히 빈 결과")

    print("[6] 함정: 'in'도 반복자를 소비한다")
    gen = pages(FakeLikedSongsAPI(total=5))
    found = Track("좋아요 #1") in gen            # #0, #1을 소비하며 찾는다
    print(f"     #1 포함? {found} → 남은 곡: {[t.title for t in gen]} (#0, #1은 사라졌다)")
