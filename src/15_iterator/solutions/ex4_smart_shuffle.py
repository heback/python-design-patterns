"""[15장 연습문제 4 해설] 새 순회 방식 추가: 같은 아티스트가 연달아 나오지 않는 '스마트 셔플'.

상황: 멜로디 사용자 설문에서 "셔플인데 같은 가수 노래가 연속으로 나온다"는 불만이 1위였다.
기획자는 '같은 아티스트 연속 금지' 셔플을 요구한다. 반복자 패턴 덕분에 순회 방식(제너레이터 함수)
하나만 추가하면 된다 — 단, 03_pythonic.py의 모드 계약을 정확히 지켜야 한다.

03의 MODES 계약: `(pl, start) -> Iterator[tuple[int, Track]]`
  - start(지금 듣는 곡의 위치)를 받아 그 곡을 '첫 값'으로 낸다(모드를 바꿔도 지금 곡 유지).
  - 곡이 아니라 (위치, 곡) 쌍을 낸다(다음 모드 전환 때 Player가 위치를 넘겨야 하므로).
이 파일은 그 계약을 지키는 smart_shuffle을 만들고, 03의 Player·MODES를 축약 재현해(03 set_mode의 shuffle 특수 처리 lambda는 빼고 모든 모드를 partial로 등록)
'등록 한 줄'로 동작하는 것을 보인다(교재 규칙상 파일끼리 import하지 않는다).

03에 실제로 넣을 때 필요한 변경: ① 03의 Track에 artist 필드를 기본값과 함께 추가한다(artist: str = ""
— 기본값이 없으면 03의 기존 Track("Intro") 호출이 깨진다).
② MODES에 한 줄 등록한다. ③ 03의 set_mode는 shuffle만 seed를 넘기는 lambda로 특수 처리하므로,
seed가 필요하면 같은 처리를 하나 더 하거나 MODES 값에 partial(smart_shuffle, seed=7)을 넣는다.
Player의 재생 로직과 Playlist는 고치지 않는다.

알고리즘(지연 평가, 매 next()마다 한 곡 선택):
  - 남은 곡 중 가장 많은 아티스트가 '남은 곡의 과반'이면, 지금 그 아티스트를 내야 나중에
    연속이 강제되지 않는다 → 직전 아티스트와 다르다면 그 곡을 고른다.
  - 그렇지 않으면 섞어 둔 풀에서 직전 아티스트와 다른 첫 곡을 고른다.
  - 그런 곡이 없으면(남은 곡이 전부 같은 아티스트) 연속은 피할 수 없으므로 그냥 꺼낸다.
이 규칙은 시작 곡이 정해진 조건에서 가능한 최소 연속 횟수를 낸다(2~7곡 무작위 1,500회를
전수 탐색 결과와 대조해 확인). 단 시작 곡이 이미 과반 아티스트라면 0회는 불가능할 수 있다.
"""
from __future__ import annotations

import random
from collections import Counter
from dataclasses import dataclass
from functools import partial
from typing import Iterator, Sequence


@dataclass(frozen=True)
class Track:
    """곡과 아티스트. 03의 Track에 artist 필드를 더한 형태(변경 ①)."""

    title: str
    artist: str


def sequential(pl: Sequence[Track], start: int = 0) -> Iterator[tuple[int, Track]]:
    """03의 sequential과 같은 계약 — 비교용 기존 모드."""
    for i in range(start, len(pl)):
        yield i, pl[i]


def smart_shuffle(pl: Sequence[Track], start: int = 0,
                  seed: int | None = None) -> Iterator[tuple[int, Track]]:
    """[Concrete Iterator] 03의 모드 계약을 지키는 스마트 셔플. 상태(풀, 직전 아티스트)는 지역 변수다."""
    yield start, pl[start]                       # 계약: 지금 곡을 먼저 — 모드 전환 시 곡이 끊기지 않는다
    last = pl[start].artist
    pool = [i for i in range(len(pl)) if i != start]
    random.Random(seed).shuffle(pool)
    while pool:
        top, count = Counter(pl[i].artist for i in pool).most_common(1)[0]
        if top != last and 2 * count > len(pool):
            # 과반 아티스트를 지금 소진하지 않으면 뒤에서 연속이 강제된다.
            idx = next(k for k, i in enumerate(pool) if pl[i].artist == top)
        else:
            # 직전과 다른 첫 곡. 없으면 0(피할 수 없는 연속).
            idx = next((k for k, i in enumerate(pool) if pl[i].artist != last), 0)
        i = pool.pop(idx)
        last = pl[i].artist
        yield i, pl[i]


def plain_shuffle(pl: Sequence[Track], start: int = 0,
                  seed: int | None = None) -> Iterator[tuple[int, Track]]:
    """비교용 평범한 셔플(03의 shuffled와 같은 동작)."""
    yield start, pl[start]
    rest = [i for i in range(len(pl)) if i != start]
    random.Random(seed).shuffle(rest)
    for i in rest:
        yield i, pl[i]


# 03의 MODES와 같은 모양의 등록표. seed가 필요한 모드는 partial로 묶어 (pl, start) 모양을 맞춘다.
MODES = {"normal": sequential, "shuffle": partial(plain_shuffle, seed=5)}
MODES["smart_shuffle"] = partial(smart_shuffle, seed=5)      # ← 변경 ②: 추가는 이 한 줄


class Player:
    """[Client] 03의 Player를 축약 재현. 모드 이름으로 MODES에서 제너레이터를 골라 쓸 뿐이다."""

    def __init__(self, pl: Sequence[Track]) -> None:
        """순서대로 재생으로 시작."""
        self.pl = pl
        self._it = MODES["normal"](pl)
        self.index, self.current = next(self._it)

    def set_mode(self, mode: str) -> None:
        """현재 위치에서 새 제너레이터를 시작하고 첫 값(=지금 곡)은 소비한다. 모드 종류를 모른다."""
        self._it = MODES[mode](self.pl, self.index)
        next(self._it)

    def skip(self) -> Track | None:
        """다음 곡."""
        pair = next(self._it, None)
        if pair is None:
            return None
        self.index, self.current = pair
        return self.current


def repeats(artists: list[str]) -> int:
    """같은 아티스트가 연달아 나온 횟수."""
    return sum(a == b for a, b in zip(artists, artists[1:]))


if __name__ == "__main__":
    # 한 아티스트가 절반을 차지하는 편향된 목록 — 평범한 셔플이 연속을 만들기 쉬운 조건.
    artists = ("아이유", "잔나비", "아이유", "새소년", "아이유", "잔나비")
    lib = [Track(f"{a}-{n}", a) for n, a in enumerate(artists)]

    print("[1] 등록 한 줄 뒤 Player.set_mode로 동작한다 — 지금 곡(2번째 곡)이 유지된다")
    for mode in ("shuffle", "smart_shuffle"):
        p = Player(lib)
        p.skip()                                 # 잔나비-1 재생 중
        p.set_mode(mode)
        order = [p.current.artist] + [t.artist for t in iter(p.skip, None)]
        print(f"    {mode:<13}: {order} / 연속 {repeats(order)}회")

    print("[2] 여러 seed로 비교: 연속이 생긴 재생 순서의 수(시작 곡 0번, 100가지 seed)")
    for name, fn in (("평범한 셔플", plain_shuffle), ("스마트 셔플", smart_shuffle)):
        bad = sum(repeats([t.artist for _, t in fn(lib, 0, seed=s)]) > 0 for s in range(100))
        print(f"    {name}: {bad}/100")
