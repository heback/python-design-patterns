"""15 반복자 — 패턴 코드: 순회 상태(커서)를 컬렉션에서 떼어 반복자 객체에 담는다.

상황: 지안은 Playlist(Aggregate)가 반복자를 '만들기만' 하게 바꾼다. 커서는 반복자마다 따로 있어서
미리보기 화면이 자기 반복자를 가져도 재생기의 위치는 움직이지 않는다.
모드 전환은 '반복자 교체'가 된다.
"""
from __future__ import annotations

import random
from dataclasses import dataclass


@dataclass(frozen=True)
class Track:
    """곡 하나."""
    title: str


class PlaylistIterator:
    """[Iterator] 파이썬 반복자 프로토콜: __next__로 다음 값, 끝나면 StopIteration.

    GoF의 first/next/is_done/current_item 네 메서드를 파이썬은 __next__ 하나와 예외 하나로 줄였다.
    """

    def __iter__(self) -> PlaylistIterator:
        """반복자도 이터러블이어야 `for x in it:`이 동작한다. 그래서 self를 돌려준다."""
        return self

    def __next__(self) -> Track:
        """하위 클래스가 순회 방식을 정한다."""
        raise NotImplementedError


class SequentialIterator(PlaylistIterator):
    """[Concrete Iterator] 순서대로. 커서(index)는 이 객체의 것이다."""

    def __init__(self, tracks: tuple[Track, ...], start: int = 0) -> None:
        """start부터 시작한다 — 모드를 바꿔도 지금 곡이 끊기지 않게."""
        self.tracks, self.index = tracks, start

    def __next__(self) -> Track:
        """끝나면 StopIteration. 한 번 끝난 반복자는 계속 StopIteration을 던진다."""
        if self.index >= len(self.tracks):
            raise StopIteration
        self.index += 1
        return self.tracks[self.index - 1]


class ShuffleIterator(PlaylistIterator):
    """[Concrete Iterator] 지금 곡을 먼저, 나머지는 섞어서. 섞은 순서도 이 객체만의 상태다."""

    def __init__(self, tracks: tuple[Track, ...], start: int = 0) -> None:
        """나머지 위치를 섞어 둔다."""
        rest = [i for i in range(len(tracks)) if i != start]
        random.Random(7).shuffle(rest)
        # 섞은 순서는 반복자 안에만 있다. 순진한 코드처럼 재생기에 shuffle 상태가 쌓이지 않는다.
        self.tracks, self._order = tracks, [start] + rest

    def __next__(self) -> Track:
        """섞인 순서대로 꺼낸다."""
        if not self._order:
            raise StopIteration
        return self.tracks[self._order.pop(0)]


class Playlist:
    """[Aggregate] 곡을 담기만 한다. 커서가 없다."""

    def __init__(self, tracks: list[Track]) -> None:
        """tuple로 보관해 순회 중에 바뀌지 않게 한다."""
        self._tracks = tuple(tracks)

    def __iter__(self) -> PlaylistIterator:
        """[이터러블] 부를 때마다 '새' 반복자. 그래서 몇 번이든, 몇 화면이든 따로 순회한다."""
        return SequentialIterator(self._tracks)

    def shuffled(self, start: int = 0) -> PlaylistIterator:
        """다른 순회 방식은 다른 반복자를 만드는 메서드로 연다."""
        return ShuffleIterator(self._tracks, start)


if __name__ == "__main__":
    album = Playlist([Track(t) for t in ("Intro", "Blue", "Run", "Echo", "Outro")])
    print("[1] 같은 Playlist를 두 번 돌려도 매번 처음부터")
    print(f"    {[t.title for t in album][:2]} / {[t.title for t in album][:2]}")
    print("[2] 재생기와 미리보기가 각자 반복자를 가진다 — 서로의 위치를 건드리지 않는다")
    playing = iter(album)
    now = next(playing)
    preview = iter(album)                          # 미리보기 화면의 자기 커서
    print(f"    미리보기: {[next(preview).title for _ in range(3)]}, 재생 중: {now.title}")
    print(f"    재생기 다음 곡: {next(playing).title}")
    print("[3] 셔플 모드 = 반복자 교체. 지금 곡(Blue, 위치 1)부터 시작한다")
    print(f"    {[t.title for t in album.shuffled(start=1)]}")
    print("[4] 끝난 반복자는 계속 StopIteration — 두 번째 next도 기본값이 나온다")
    it = iter(Playlist([Track("Intro")]))
    print(f"    {next(it).title}, {next(it, '끝')}, {next(it, '끝')}")
