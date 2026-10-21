"""[15장 반복자 · 파이썬다운 변형] 제너레이터와 itertools가 반복자 클래스를 흡수한다.

상황: 02_iterator.py의 반복자 클래스 네 개는 각자 커서 필드, `__iter__`, `__next__`,
`StopIteration`을 손으로 관리했다. 리뷰어 태오가 지안에게 말한다. "그거 전부 제너레이터
함수 한두 줄씩이에요." 파이썬은 반복자 패턴을 언어 차원에서 흡수했다.

  - 제너레이터 함수: `yield`가 있는 함수를 부르면 반복자 객체가 나온다. 커서 상태는
    지역 변수와 '멈춘 실행 위치'로 표현되고, 함수가 끝나면 StopIteration이 자동으로 난다.
  - itertools: 반복자를 조립하는 부품 상자. cycle(전체 반복), repeat(한 곡 반복),
    islice(앞 n개 미리보기), chain(사용자 대기열 + 플레이리스트).
  - yield from: 하위 반복자에 순회를 위임한다. 폴더 안에 폴더가 있는 재생목록(7장 컴포지트)을
    재귀 순회하는 코드가 몇 줄이 된다.
  - collections.abc: `Sequence`를 상속하고 `__getitem__`/`__len__`만 구현하면 `__iter__`,
    `__contains__`, `__reversed__`, `index`, `count`를 믹스인으로 얻는다.
"""
from __future__ import annotations

import random
from collections.abc import Iterator, Sequence
from dataclasses import dataclass
from itertools import chain, cycle, islice, repeat


@dataclass(frozen=True)
class Track:
    """곡 하나."""

    title: str


class Playlist(Sequence[Track]):
    """[Aggregate] Sequence 믹스인: 두 메서드만 쓰고 나머지 순회 관련 연산을 물려받는다.

    02에서 손으로 썼던 __iter__가 없다는 점에 주목하라. Sequence가 __getitem__을 0부터
    IndexError가 날 때까지 부르는 __iter__를 제공한다. 'in'도, reversed()도 공짜다.
    """

    def __init__(self, tracks: list[Track]) -> None:
        """tuple로 보관 — 순회 중 변경 방지."""
        self._tracks = tuple(tracks)

    def __getitem__(self, i):  # type: ignore[override]
        """정수와 slice를 모두 받는다(Sequence 계약)."""
        return self._tracks[i]

    def __len__(self) -> int:
        """곡 수."""
        return len(self._tracks)


# ---------------------------------------------------------------------------
# 모드별 반복자 = 제너레이터 함수. 반환값은 (위치, 곡) 쌍 — 모드 전환 시 위치를 넘기기 위해.
# ---------------------------------------------------------------------------

def sequential(pl: Playlist, start: int = 0) -> Iterator[tuple[int, Track]]:
    """02 SequentialIterator 전체가 이 두 줄이다. 커서는 range가, 종료는 함수의 끝이 맡는다."""
    for i in range(start, len(pl)):
        yield i, pl[i]


def repeat_all(pl: Playlist, start: int = 0) -> Iterator[tuple[int, Track]]:
    """cycle로 무한 반복하되 start에서 시작하도록 islice로 앞을 잘라 낸다."""
    if not pl:                                   # 빈 목록이면 cycle도 즉시 끝나지만 의도를 명시한다
        return
    yield from islice(cycle(enumerate(pl)), start, None)


def repeat_one(pl: Playlist, start: int = 0) -> Iterator[tuple[int, Track]]:
    """itertools.repeat: 같은 값을 무한히. 클래스가 필요 없는 가장 극적인 예."""
    return repeat((start, pl[start]))


def shuffled(pl: Playlist, start: int = 0, seed: int | None = None) -> Iterator[tuple[int, Track]]:
    """지금 곡을 먼저, 나머지를 섞어서. 섞는 시점이 '첫 next()' 이후라는 점이 제너레이터의 지연성이다."""
    yield start, pl[start]
    rest = [i for i in range(len(pl)) if i != start]
    random.Random(seed).shuffle(rest)
    for i in rest:
        yield i, pl[i]


MODES = {"normal": sequential, "repeat_all": repeat_all, "repeat_one": repeat_one}


class Player:
    """[Client] 02와 같은 역할. 반복자 클래스 대신 제너레이터 객체를 들고 있다."""

    def __init__(self, pl: Playlist) -> None:
        """기본 모드로 시작."""
        self.pl = pl
        self._it = sequential(pl)
        self.index, self.current = next(self._it)

    def set_mode(self, mode: str) -> None:
        """현재 위치에서 새 제너레이터를 시작하고, 첫 값(=지금 곡)은 소비해 둔다."""
        factory = (lambda p, s: shuffled(p, s, seed=7)) if mode == "shuffle" else MODES[mode]
        self._it = factory(self.pl, self.index)
        next(self._it)

    def skip(self) -> Track | None:
        """다음 곡. 끝이면 None."""
        pair = next(self._it, None)
        if pair is None:
            return None
        self.index, self.current = pair
        return self.current

    def up_next(self, queue: list[Track], n: int) -> list[str]:
        """'다음에 재생' 미리보기: 사용자 대기열 뒤에 플레이리스트 나머지를 이어 붙인다.

        chain과 islice는 어느 쪽도 끝까지 펼치지 않는다. 재생 중인 반복자(self._it)를
        건드리지 않기 위해 같은 위치에서 '새' 반복자를 만들어 미리 본다 — 01의 버그를 피하는 방법.
        한계: '순서대로' 모드 기준이다. 셔플·한 곡 반복의 실제 다음 곡과는 다를 수 있다. 현재 반복자를
        itertools.tee로 복제하거나 peek를 지원하는 반복자 클래스(5.1절 끝)가 필요한 이유다.
        """
        rest = (t for _, t in sequential(self.pl, self.index + 1))
        return [t.title for t in islice(chain(queue, rest), n)]


# ---------------------------------------------------------------------------
# yield from과 컴포지트: 폴더 안의 폴더
# ---------------------------------------------------------------------------

@dataclass
class Folder:
    """[Composite] 재생목록 폴더. 하위 항목은 Playlist 또는 Folder."""

    name: str
    children: list[Playlist | Folder]

    def __iter__(self) -> Iterator[Track]:
        """깊이 우선 순회. 하위 항목이 무엇이든 '이터러블'이라는 사실 하나에만 의존한다.

        yield from은 하위 반복자의 값을 그대로 흘려보낸다. 재귀 깊이만큼 스택을 쓰지만,
        스택을 직접 관리하는 클래스형 반복자(__next__ 안에서 '어느 폴더의 몇 번째'를 쌓아 두는 코드)보다 훨씬 읽기 쉽다.
        """
        for child in self.children:
            yield from child


if __name__ == "__main__":
    album = Playlist([Track(t) for t in ("Intro", "Blue", "Run", "Echo", "Outro")])

    print("[1] Sequence 믹스인: __iter__·in·reversed를 직접 쓰지 않았다")
    print("    ", [t.title for t in album], Track("Run") in album,
          [t.title for t in reversed(album)][:2])

    print("[2] 02와 같은 시나리오를 제너레이터로")
    p = Player(album)
    p.skip()
    p.set_mode("shuffle")
    print("    셔플:", p.current.title, "→", [p.skip().title for _ in range(2)])
    p.set_mode("repeat_all")
    print("    전체 반복:", p.current.title, "→", [p.skip().title for _ in range(5)])
    p.set_mode("repeat_one")
    print("    한 곡 반복:", [p.skip().title for _ in range(3)])

    print("[3] 다음 곡 미리보기: 대기열 + 나머지, 재생 위치는 그대로")
    q = Player(album)
    print("    ", q.up_next([Track("친구가 추천한 곡")], 3), "/ 재생 중:", q.current.title)

    print("[4] yield from: 폴더 안의 폴더를 하나의 for로")
    lib = Folder("내 음악", [Playlist([Track("A1"), Track("A2")]),
                            Folder("드라이브", [Playlist([Track("D1")]), Playlist([Track("D2")])])])
    print("    ", [t.title for t in lib])

    print("[5] 제너레이터 객체는 이터레이터다 — 한 번 쓰면 끝난다")
    gen = sequential(album, 3)
    print("    첫 순회:", [t.title for _, t in gen], "/ 두 번째:", [t.title for _, t in gen])
