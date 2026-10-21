"""[15장 연습문제 1 해설] `__iter__`가 self를 반환하는 컬렉션 — 중첩 순회에서 무엇이 깨지는가.

상황: 멜로디의 '크로스페이드 추천' 기능은 앨범의 모든 곡 쌍(a, b)을 비교해 어울리는 전환을 찾는다.
신입 개발자가 만든 `BrokenAlbum`은 커서(_pos)를 컬렉션 자신이 들고 `__iter__`에서 self를 반환한다.
바깥 for와 안쪽 for가 '같은 반복자'를 공유하게 되어, 안쪽 루프가 커서를 끝까지 밀어 버린다.

해결은 이터러블(컬렉션)과 이터레이터(커서)를 분리하는 것이다. 두 가지 방법을 보인다.
  1) `__iter__`를 제너레이터로 — 가장 짧다.
  2) 별도 반복자 클래스 — `collections.abc.Iterator`를 상속해 `__next__`만 쓰고 `__iter__`는 믹스인으로.
"""
from __future__ import annotations

from collections.abc import Iterator


class BrokenAlbum:
    """[잘못된 Aggregate] 컬렉션이 곧 반복자다. 순회 상태가 컬렉션에 하나뿐이다."""

    def __init__(self, titles: list[str]) -> None:
        """곡 목록과 '하나뿐인' 커서."""
        self._titles = titles
        self._pos = 0

    def __iter__(self) -> BrokenAlbum:
        """⚠ self 반환 + 커서 초기화. 중첩 순회 시 안쪽 for가 바깥의 커서를 덮어쓴다."""
        self._pos = 0
        return self

    def __next__(self) -> str:
        """공유 커서를 전진."""
        if self._pos >= len(self._titles):
            raise StopIteration
        self._pos += 1
        return self._titles[self._pos - 1]


class GeneratorAlbum:
    """[Aggregate] 해결 1: __iter__가 제너레이터. 호출마다 독립된 커서(지역 변수)가 생긴다."""

    def __init__(self, titles: list[str]) -> None:
        """곡 목록만 보관. 커서 필드가 없다는 것이 핵심."""
        self._titles = tuple(titles)

    def __iter__(self) -> Iterator[str]:
        """yield가 있으므로 이 메서드를 부르면 새 제너레이터 객체가 나온다."""
        for t in self._titles:
            yield t


class AlbumIterator(Iterator[str]):
    """[Iterator] 해결 2: collections.abc.Iterator 상속 — __next__만 구현하면 __iter__(self 반환)는 믹스인.

    '반복자의 __iter__는 self'가 맞는 규칙이다. 틀린 것은 BrokenAlbum처럼 '컬렉션'이 self를
    반환한 것이다. 같은 return self가 어느 클래스에 있느냐에 따라 정답도 버그도 된다.
    """

    def __init__(self, titles: tuple[str, ...]) -> None:
        """반복자마다 자기 커서."""
        self._titles = titles
        self._pos = 0

    def __next__(self) -> str:
        """전진."""
        if self._pos >= len(self._titles):
            raise StopIteration
        self._pos += 1
        return self._titles[self._pos - 1]


class ClassicAlbum:
    """[Aggregate] 해결 2의 컬렉션: __iter__가 매번 새 AlbumIterator를 만든다(팩토리 메서드)."""

    def __init__(self, titles: list[str]) -> None:
        """곡 목록."""
        self._titles = tuple(titles)

    def __iter__(self) -> AlbumIterator:
        """새 커서."""
        return AlbumIterator(self._titles)


def all_pairs(album) -> list[str]:
    """중첩 순회로 서로 다른 곡 쌍을 모두 만든다. 3곡이면 6쌍이 나와야 한다."""
    return [f"{a}→{b}" for a in album for b in album if a != b]


if __name__ == "__main__":
    titles = ["Intro", "Blue", "Run"]
    print("[1] BrokenAlbum:", all_pairs(BrokenAlbum(titles)), "← 6쌍이어야 하는데 2쌍뿐")
    print("[2] GeneratorAlbum:", len(all_pairs(GeneratorAlbum(titles))), "쌍")
    print("[3] ClassicAlbum:", len(all_pairs(ClassicAlbum(titles))), "쌍")
    it = iter(ClassicAlbum(titles))
    print("[4] 믹스인으로 얻은 __iter__: iter(it) is it →", iter(it) is it)
