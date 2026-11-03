"""15 반복자 — 순진한 코드: 재생기가 리스트, 커서, 모드 분기를 모두 직접 들고 있다.

상황: 음악 앱 '멜로디'의 지안은 플레이리스트를 list로 받아 index 하나로 재생했다.
재생 모드(셔플, 한 곡 반복)가 생기자 next_track()이 모드 분기로 찼고,
'다음 곡 미리보기' 화면이 같은 index를 움직여 곡이 건너뛰어졌다.
"""
from __future__ import annotations

import random


class Player:
    """재생기. 무엇을(리스트) + 어디까지(index) + 어떤 순서로(mode)를 혼자 안다."""

    def __init__(self, tracks: list[str]) -> None:
        """리스트를 그대로 받는다."""
        # ⚠ 문제: 재생기가 'list'라는 내부 표현에 묶였다. 다른 모양의 원천은 list로 바꿔야 쓸 수 있다.
        self.tracks = tracks
        self.index = 0                       # ⚠ 문제: 순회 위치(커서)가 하나뿐이고, 공개 필드다
        self.mode = "normal"
        self.order: list[int] = []           # 셔플 모드에서만 뜻이 있는 상태

    def set_mode(self, mode: str) -> None:
        """모드 변경. 지금 곡은 유지하고, 셔플이면 나머지 순서를 섞어 둔다."""
        self.mode = mode
        if mode == "shuffle":
            rest = [i for i in range(len(self.tracks)) if i != self.index]
            random.Random(7).shuffle(rest)
            self.order = rest

    def next_track(self) -> str | None:
        """다음 곡으로 이동한다. 끝이면 None."""
        # ⚠ 문제: 순회 정책이 모드 분기로 엉켜 있다. 모드 하나 추가 = 이 메서드 수정.
        if self.mode == "normal":
            if self.index + 1 >= len(self.tracks):
                return None
            self.index += 1
        elif self.mode == "shuffle":
            if not self.order:
                return None
            self.index = self.order.pop(0)
        # repeat_one은 index를 그대로 둔다
        return self.tracks[self.index]


class UpNextPreview:
    """'다음에 재생될 곡' 미리보기 화면. 같은 Player를 함께 쓴다."""

    def __init__(self, player: Player) -> None:
        """재생기 참조."""
        self.player = player

    def peek(self, n: int) -> list[str | None]:
        """다음 n곡 제목."""
        # ⚠ 문제: '다음 곡'을 아는 곳이 next_track()뿐이라 그것을 부른다. 그 순간 공유 커서가 움직인다.
        return [self.player.next_track() for _ in range(n)]


if __name__ == "__main__":
    album = ["Intro", "Blue", "Run", "Echo", "Outro"]
    print("[1] Blue에서 셔플로 — 지금 곡은 유지된다(동작은 한다)")
    p = Player(album)
    p.next_track()
    p.set_mode("shuffle")
    print(f"    {p.tracks[p.index]} -> {[p.next_track() for _ in range(2)]}")
    print("[2] 미리보기를 열었을 뿐인데 재생 곡이 바뀐다")
    q = Player(album)
    print(f"    재생 중: {q.tracks[q.index]}, 미리보기: {UpNextPreview(q).peek(2)}")
    print(f"    미리보기 후 재생 중: {q.tracks[q.index]}   <- 아무것도 누르지 않았다")
