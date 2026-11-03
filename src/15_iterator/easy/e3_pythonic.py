"""15 반복자 — 파이썬다운 변형: 반복자 클래스가 제너레이터 함수 몇 줄이 된다.

상황: 리뷰어 태오가 말한다. "반복자 클래스들, 전부 제너레이터 함수 한두 줄씩이에요."
yield가 있는 함수를 부르면 반복자가 나온다. 커서는 지역 변수가 되고, 함수가 끝나면
StopIteration은 파이썬이 던진다. 모드는 '(플레이리스트, 시작 위치) -> (위치, 곡) 반복자' 함수다.
"""
from __future__ import annotations

import random
from collections.abc import Iterator, Sequence
from dataclasses import dataclass
from itertools import repeat


@dataclass(frozen=True)
class Track:
    """곡 하나."""
    title: str


class Playlist(Sequence[Track]):
    """[Aggregate] Sequence 믹스인: 두 메서드만 쓰면 __iter__·in·reversed를 물려받는다."""

    def __init__(self, tracks: list[Track]) -> None:
        """tuple로 보관한다."""
        self._tracks = tuple(tracks)

    # 이 두 메서드만 쓰면 Sequence가 0부터 IndexError까지 __getitem__을 부르는 __iter__를 준다.
    def __getitem__(self, i):  # type: ignore[override]
        """정수와 slice를 모두 받는다(Sequence 계약)."""
        return self._tracks[i]

    def __len__(self) -> int:
        """곡 수."""
        return len(self._tracks)


# 모드 = 제너레이터 함수. (위치, 곡) 쌍을 내는 이유: 모드를 바꿀 때 Player가 위치를 넘겨야 하므로.
def sequential(pl: Playlist, start: int = 0) -> Iterator[tuple[int, Track]]:
    """패턴 코드의 SequentialIterator 전체가 이 두 줄이다. 커서는 range가, 끝은 함수의 끝이 맡는다."""
    for i in range(start, len(pl)):
        yield i, pl[i]


def repeat_one(pl: Playlist, start: int = 0) -> Iterator[tuple[int, Track]]:
    """한 곡 반복: itertools.repeat가 같은 값을 끝없이 낸다. 클래스가 필요 없다."""
    return repeat((start, pl[start]))


def shuffled(pl: Playlist, start: int = 0, seed: int | None = None) -> Iterator[tuple[int, Track]]:
    """지금 곡을 먼저, 나머지는 섞어서. 첫 next() 전까지는 섞지도 않는다."""
    yield start, pl[start]
    rest = [i for i in range(len(pl)) if i != start]
    random.Random(seed).shuffle(rest)
    for i in rest:
        yield i, pl[i]


MODES = {"normal": sequential, "repeat_one": repeat_one}   # 새 모드 = 함수 하나 + 이 dict에 한 줄


class Player:
    """[Client] 반복자 클래스 대신 제너레이터 객체를 들고 있다. 모드 분기가 없다."""

    def __init__(self, pl: Playlist) -> None:
        """순서대로 모드로 시작한다."""
        self.pl = pl
        self._it = sequential(pl)
        self.index, self.current = next(self._it)

    def set_mode(self, mode: str) -> None:
        """지금 위치에서 새 제너레이터를 시작하고, 첫 값(= 지금 곡)은 소비해 둔다."""
        # shuffle만 seed가 필요해 lambda로 감쌌다(데모 출력을 매번 같게 하려는 것).
        factory = (lambda p, s: shuffled(p, s, seed=7)) if mode == "shuffle" else MODES[mode]
        self._it = factory(self.pl, self.index)
        next(self._it)              # 모드 함수는 지금 곡을 첫 값으로 낸다 — 버려야 skip()이 다음 곡을 준다

    def skip(self) -> Track | None:
        """다음 곡. 끝이면 None."""
        pair = next(self._it, None)
        if pair is None:
            return None
        self.index, self.current = pair
        return self.current


if __name__ == "__main__":
    album = Playlist([Track(t) for t in ("Intro", "Blue", "Run", "Echo", "Outro")])
    print("[1] Sequence 믹스인: __iter__와 in을 직접 쓰지 않았다")
    print(f"    {[t.title for t in album]}, {Track('Run') in album}")
    print("[2] 패턴 코드와 같은 시나리오: Blue에서 셔플, 다시 한 곡 반복")
    p = Player(album)
    p.skip()
    p.set_mode("shuffle")
    print(f"    셔플: {p.current.title} -> {[p.skip().title for _ in range(2)]}")
    p.set_mode("repeat_one")
    print(f"    한 곡 반복: {[p.skip().title for _ in range(3)]}")
    print("[3] 제너레이터 객체는 이터레이터다 — 한 번 돌면 끝난다")
    gen = sequential(album, 3)
    print(f"    첫 순회: {[t.title for _, t in gen]}, 두 번째: {[t.title for _, t in gen]}")
