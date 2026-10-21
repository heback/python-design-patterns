"""[15장 반복자 · 순진한 설계] 플레이어가 인덱스·셔플 순서·페이지 토큰을 모두 직접 관리한다.

상황: 음악 스트리밍 앱 '멜로디'의 클라이언트 개발자 지안은 처음에 플레이리스트를 `list[Track]`으로
받아 `for i in range(len(tracks))`로 재생했다. 이후 셔플·한 곡 반복·전체 반복 모드가 생겼고
(모드를 바꿔도 지금 듣는 곡은 유지), 수만 곡짜리 '좋아요 표시한 곡'은 서버가 50곡씩 페이지로 준다.
이 파일은 그 요구를 모두 `Player` 한 클래스에 밀어 넣은 결과다.

데모가 보여 주는 문제:
  [2] '좋아요 표시한 곡'은 첫 곡을 틀기 전에 모든 페이지를 받아야 한다(요청 수로 측정).
  [3] '다음 곡 미리보기' 화면이 같은 인덱스를 움직여 재생 위치가 밀린다.
"""
from __future__ import annotations

import random
from dataclasses import dataclass


@dataclass(frozen=True)
class Track:
    """곡 하나. frozen: 재생 순서 로직이 곡 데이터를 바꿀 일은 없어야 한다."""

    title: str


class FakeLikedSongsAPI:
    """서버의 페이지네이션 API 흉내. 요청 수를 세어 '얼마나 받아 왔는가'를 측정한다."""

    PAGE_SIZE = 50

    def __init__(self, total: int) -> None:
        """total곡짜리 '좋아요' 목록."""
        self.total = total
        self.requests = 0

    def fetch_page(self, token: int | None) -> tuple[list[Track], int | None]:
        """(이번 페이지 곡들, 다음 페이지 토큰). 마지막 페이지면 토큰이 None."""
        self.requests += 1
        start = token or 0
        end = min(start + self.PAGE_SIZE, self.total)
        items = [Track(f"좋아요 #{i}") for i in range(start, end)]
        return items, (end if end < self.total else None)


class Player:
    """재생기. 재생·순서 정책·데이터 출처를 모두 안다 — 세 가지 이유로 바뀌는 클래스(SRP 위반)."""

    def __init__(self, tracks: list[Track]) -> None:
        """리스트를 그대로 받는다."""
        # ⚠ 문제: 플레이어가 컬렉션의 내부 표현(list)에 묶여 있다. 페이지 API가 오면
        #   전부 받아 list로 바꿔야만 이 클래스를 쓸 수 있다(아래 from_api).
        self.tracks = tracks
        self.index = 0                          # 현재 위치 — 이 '커서'가 Player의 공개 필드다
        self.mode = "normal"
        self.shuffle_order: list[int] = []      # 셔플 모드에서만 의미 있는 상태
        self.shuffle_pos = 0

    @classmethod
    def from_api(cls, api: FakeLikedSongsAPI) -> Player:
        """페이지 API에서 만들기."""
        tracks: list[Track] = []
        token: int | None = None
        # ⚠ 문제: 첫 곡을 틀기 전에 모든 페이지를 받는다. 2만 곡이면 요청 400번.
        #   사용자는 대개 앞의 몇 곡만 듣고 끈다.
        while True:
            page, token = api.fetch_page(token)
            tracks.extend(page)
            if token is None:
                break
        return cls(tracks)

    def current(self) -> Track:
        """지금 곡."""
        return self.tracks[self.index]

    def set_mode(self, mode: str) -> None:
        """모드 변경. 현재 곡은 유지해야 한다."""
        self.mode = mode
        if mode == "shuffle":
            # ⚠ 문제: 순서 정책마다 별도의 상태(shuffle_order, shuffle_pos)가 Player에 쌓인다.
            rest = [i for i in range(len(self.tracks)) if i != self.index]
            random.Random(7).shuffle(rest)
            self.shuffle_order = [self.index] + rest
            self.shuffle_pos = 0

    def next_track(self) -> Track | None:
        """다음 곡으로 이동. 끝이면 None."""
        # ⚠ 문제: 순회 정책이 모드 분기로 한 메서드에 엉켜 있다. 모드 하나 추가 = 이 메서드 수정.
        if self.mode == "normal":
            if self.index + 1 >= len(self.tracks):
                return None
            self.index += 1
        elif self.mode == "repeat_one":
            pass
        elif self.mode == "repeat_all":
            self.index = (self.index + 1) % len(self.tracks)
        elif self.mode == "shuffle":
            if self.shuffle_pos + 1 >= len(self.shuffle_order):
                return None
            self.shuffle_pos += 1
            self.index = self.shuffle_order[self.shuffle_pos]
        return self.current()


class UpNextPreview:
    """'다음에 재생될 곡' 미리보기 화면 — 같은 Player를 공유한다."""

    def __init__(self, player: Player) -> None:
        """재생기 참조."""
        self.player = player

    def peek(self, n: int) -> list[str]:
        """다음 n곡 제목."""
        # ⚠ 문제: '다음 곡 계산'이 next_track()에만 있으니 그걸 불러 볼 수밖에 없다.
        #   그 순간 공유 커서(index)가 움직인다. 순회 상태가 컬렉션/재생기와 분리되지 않아
        #   두 화면이 동시에 순회할 수 없다.
        return [t.title for _ in range(n) if (t := self.player.next_track())]


if __name__ == "__main__":
    album = [Track(t) for t in ("Intro", "Blue", "Run", "Echo", "Outro")]

    print("[1] 모드 전환: Blue에서 셔플로 바꿔도 Blue가 유지된다 — 동작은 한다")
    p = Player(album)
    p.next_track()
    p.set_mode("shuffle")
    print("    ", p.current().title, "→", [p.next_track().title for _ in range(3)])

    print("[2] 2만 곡 '좋아요' 목록: 첫 곡 재생까지 필요한 요청 수")
    api = FakeLikedSongsAPI(total=20_000)
    liked = Player.from_api(api)
    print(f"    첫 곡 '{liked.current().title}' 재생 전 요청 {api.requests}번, 메모리에 {len(liked.tracks):,}곡")

    print("[3] 미리보기 화면이 재생 위치를 밀어낸다")
    q = Player(album)
    print("    재생 중:", q.current().title)
    print("    미리보기:", UpNextPreview(q).peek(2))
    print("    미리보기 후 재생 중:", q.current().title, "← 사용자는 아무것도 누르지 않았다")
