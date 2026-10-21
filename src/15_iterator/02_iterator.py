"""[15장 반복자 · 패턴 적용] 순회 정책을 반복자 객체로 분리한다 — GoF 구조를 파이썬 프로토콜 위에.

상황: 01_naive.py에서 지안의 `Player`는 인덱스·셔플 순서·반복 모드를 모두 직접 관리했고,
미리보기 화면이 같은 커서를 움직여 재생 위치가 밀렸다. 이 파일은 GoF 반복자 패턴으로 다시 짠다.

  - `Playlist`(Aggregate)는 곡을 보관하고, 순회 방식별 반복자를 '만들어 주기만' 한다.
    반복자를 만드는 메서드(`__iter__`, `iterator()`)는 1장의 팩토리 메서드와 같은 자리다.
  - 반복자(Iterator)는 '어디까지 갔는가'라는 커서 상태를 각자 소유한다. 그래서 같은
    플레이리스트를 재생기와 미리보기가 동시에 순회해도 서로 간섭하지 않는다.
  - 파이썬 반복자 프로토콜(`__iter__`/`__next__`, `StopIteration`)을 구현하므로 모든 반복자가
    `for`, `list()`, `itertools`와 그대로 맞물린다. GoF의 first()/next()/is_done()/current_item()
    네 메서드가 파이썬에서는 `__next__` 하나와 예외 하나로 압축된다.

이 파일은 '클래스로 쓴 반복자'가 무엇을 하는지 드러내려는 교과서적 버전이다. 같은 일을
제너레이터로 하면 얼마나 짧아지는지는 03_pythonic.py에서 본다.
"""
from __future__ import annotations

import random
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class Track:
    """곡 하나."""

    title: str


class PlaylistIterator(ABC):
    """[Iterator] 플레이리스트 순회기의 공통 인터페이스.

    파이썬 반복자 프로토콜의 규칙 두 가지를 지킨다.
      1) `__iter__`는 self를 반환한다 — 반복자도 이터러블이어야 `for x in it:`이 동작한다.
      2) 끝나면 `StopIteration`을 던지고, 그 뒤로도 계속 던진다(한 번 끝난 반복자는 끝난 상태).
    `index`를 공개하는 이유: 모드를 바꿀 때 '지금 몇 번째 곡인가'를 새 반복자에 넘겨야 하기 때문.
    """

    def __init__(self, playlist: Playlist, start: int) -> None:
        """start는 '이미 재생 중인 곡'의 위치. 첫 next()는 start 곡을 돌려준다."""
        self._playlist = playlist
        self.index = start

    def __iter__(self) -> PlaylistIterator:
        """반복자는 자기 자신을 반환한다(프로토콜 규칙 1)."""
        return self

    @abstractmethod
    def __next__(self) -> Track:
        """다음 곡. 끝이면 StopIteration."""


class SequentialIterator(PlaylistIterator):
    """[Concrete Iterator] 순서대로 한 번."""

    def __init__(self, playlist: Playlist, start: int = 0) -> None:
        """첫 next()가 start를 내도록 '다음에 낼 위치'를 따로 둔다."""
        super().__init__(playlist, start)
        self._next = start

    def __next__(self) -> Track:
        """끝에 도달하면 StopIteration — 이후 호출도 계속 같은 예외(프로토콜 규칙 2)."""
        if self._next >= len(self._playlist):
            raise StopIteration
        self.index = self._next
        self._next += 1
        return self._playlist[self.index]


class RepeatAllIterator(PlaylistIterator):
    """[Concrete Iterator] 끝나면 처음으로 — 무한 반복자. list()로 감싸면 영원히 돈다(주의)."""

    def __init__(self, playlist: Playlist, start: int = 0) -> None:
        """첫 next()가 start를 내도록."""
        super().__init__(playlist, start)
        self._next = start

    def __next__(self) -> Track:
        """빈 플레이리스트에서는 무한 루프 대신 즉시 종료해야 한다 — 무한 반복자의 흔한 함정."""
        if len(self._playlist) == 0:
            raise StopIteration
        self.index = self._next % len(self._playlist)
        self._next = self.index + 1
        return self._playlist[self.index]


class RepeatOneIterator(PlaylistIterator):
    """[Concrete Iterator] 한 곡 반복 — 커서가 움직이지 않는 무한 반복자."""

    def __next__(self) -> Track:
        """같은 곡을 계속. 빈 목록 가드는 RepeatAllIterator와 같은 이유(IndexError 대신 종료)."""
        if len(self._playlist) == 0:
            raise StopIteration
        return self._playlist[self.index]


class ShuffleIterator(PlaylistIterator):
    """[Concrete Iterator] 지금 곡을 맨 앞에 두고 나머지를 섞은 순서로 한 번씩.

    셔플 순서(_order)는 이 반복자만의 상태다. 01에서는 Player의 shuffle_order 필드였다.
    seed를 받는 이유: 테스트와 교재 출력이 실행마다 같아야 하기 때문(실서비스는 None).
    """

    def __init__(self, playlist: Playlist, start: int = 0, seed: int | None = None) -> None:
        """순서를 미리 섞어 둔다. O(n)이지만 플레이리스트는 메모리에 있는 컬렉션이다."""
        super().__init__(playlist, start)
        rest = [i for i in range(len(playlist)) if i != start]
        random.Random(seed).shuffle(rest)
        # 빈 목록이면 순서도 비운다 — [start]를 넣으면 첫 next()가 IndexError를 낸다.
        self._order = [start] + rest if len(playlist) else []
        self._pos = 0

    def __next__(self) -> Track:
        """섞인 순서를 따라간다."""
        if self._pos >= len(self._order):
            raise StopIteration
        self.index = self._order[self._pos]
        self._pos += 1
        return self._playlist[self.index]


class Playlist:
    """[Aggregate] 곡을 보관하고 반복자를 만든다. 내부 표현(tuple)은 바깥에 드러나지 않는다.

    `__iter__`는 호출될 때마다 '새' 반복자를 만든다. 이것이 이터러블과 이터레이터의 분리다.
    그래서 같은 Playlist를 두 번 for 돌려도, 두 화면이 동시에 돌려도 서로 영향이 없다.
    """

    MODES = {
        "normal": SequentialIterator,
        "repeat_all": RepeatAllIterator,
        "repeat_one": RepeatOneIterator,
    }

    def __init__(self, tracks: list[Track]) -> None:
        """tuple로 복사해 보관한다 — 순회 중 컬렉션이 바뀌는 문제를 원천 차단."""
        self._tracks = tuple(tracks)

    def __len__(self) -> int:
        """곡 수."""
        return len(self._tracks)

    def __getitem__(self, i: int) -> Track:
        """반복자들이 쓰는 접근자."""
        return self._tracks[i]

    def __iter__(self) -> PlaylistIterator:
        """[팩토리 메서드] 기본 순회 = 순서대로. for track in playlist: 가 이것을 부른다."""
        return SequentialIterator(self)

    def iterator(self, mode: str, start: int = 0, seed: int | None = None) -> PlaylistIterator:
        """모드별 반복자 생성. 새 모드는 반복자 클래스 하나 + 이 등록 한 줄."""
        if mode == "shuffle":
            return ShuffleIterator(self, start, seed)
        return self.MODES[mode](self, start)


class Player:
    """[Client] 이제 커서를 직접 다루지 않는다. 반복자 하나를 들고 next()만 부른다."""

    def __init__(self, playlist: Playlist) -> None:
        """기본 모드로 시작하고 첫 곡을 꺼내 둔다."""
        self.playlist = playlist
        self._it = playlist.iterator("normal")
        self.current: Track | None = next(self._it, None)

    def set_mode(self, mode: str, seed: int | None = 7) -> None:
        """모드 변경 = 반복자 교체. 현재 위치(index)를 넘겨 '지금 곡 유지'를 보장한다."""
        new_it = self.playlist.iterator(mode, start=self._it.index, seed=seed)
        next(new_it, None)      # 새 반복자의 첫 곡은 지금 곡이므로 소비해 둔다(빈 목록이면 None)
        self._it = new_it

    def skip(self) -> Track | None:
        """다음 곡. next()의 기본값 인자로 StopIteration을 None으로 바꾼다."""
        self.current = next(self._it, None)
        return self.current


if __name__ == "__main__":
    album = Playlist([Track(t) for t in ("Intro", "Blue", "Run", "Echo", "Outro")])

    print("[1] Playlist는 이터러블이다: for와 list()가 그대로 동작하고, 두 번 돌려도 된다")
    print("    ", [t.title for t in album])
    print("    ", [t.title for t in album], "← 매번 새 반복자")

    print("[2] 재생기와 미리보기가 같은 플레이리스트를 '독립적으로' 순회한다")
    player = Player(album)
    preview = iter(album)                       # 미리보기 화면만의 반복자
    print("    재생 중:", player.current.title)
    print("    다른 화면의 독립 순회(앨범 앞 3곡):", [next(preview).title for _ in range(3)])
    print("    그 뒤 재생 중:", player.current.title, "← 01의 버그가 사라졌다")

    print("[3] 모드 전환: Blue에서 셔플 → 전체 반복으로 바꿔도 현재 곡이 유지된다")
    player.skip()
    player.set_mode("shuffle")
    print("    셔플:", player.current.title, "→", [player.skip().title for _ in range(2)])
    player.set_mode("repeat_all")
    print("    전체 반복:", player.current.title, "→", [player.skip().title for _ in range(5)])

    print("[4] 한 곡 반복과 순서대로 재생의 종료")
    player.set_mode("repeat_one")
    print("    한 곡 반복:", [player.skip().title for _ in range(3)])
    seq = album.iterator("normal", start=3)
    print("    Echo부터 순서대로:", [t.title for t in seq], "/ 끝난 뒤 next:", next(seq, "StopIteration"))
