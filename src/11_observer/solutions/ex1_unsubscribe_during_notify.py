"""연습문제 1 해설: 통지 도중 관찰자가 자기 자신을 해제하면 무엇이 깨지는가.

상황: 목표가 알림처럼 '한 번 울리고 스스로 구독을 해제하는' 관찰자가 있다. 주체가
구독자 리스트를 '원본 그대로' 순회하면, 해제로 리스트가 한 칸 당겨지면서 바로 뒤의
관찰자가 이번 통지를 받지 못한다. 예외도 경고도 없이 조용히 빠진다는 점이 위험하다.

이 파일은 같은 시나리오를 두 주체(원본 순회 / 복사본 순회)로 실행해 차이를 보인다.
"""
from __future__ import annotations

from typing import Callable


class NaiveSubject:
    """[Subject] 원본 리스트를 직접 순회하는 주체 — 버그 재현용."""

    def __init__(self) -> None:
        """구독자 목록."""
        self.observers: list[Callable[[int], None]] = []

    def notify(self, price: int) -> None:
        """⚠ 문제: for 문이 내부 인덱스로 리스트를 걷는 동안 리스트가 줄어든다.

        인덱스 0의 관찰자가 자신을 지우면 인덱스 1의 관찰자가 0으로 당겨지고,
        for 문은 다음 차례로 인덱스 1을 보므로 당겨진 관찰자를 건너뛴다.
        """
        for obs in self.observers:
            obs(price)


class SafeSubject(NaiveSubject):
    """[Subject] 복사본을 순회하는 주체. 바뀐 것은 list(...) 한 단어뿐이다."""

    def notify(self, price: int) -> None:
        """통지 시작 '순간'의 구독자 집합에 모두 통지한다. 도중의 추가·해제는 다음 통지부터 반영."""
        for obs in list(self.observers):
            obs(price)


def run(subject: NaiveSubject) -> None:
    """같은 구독 구성으로 통지 한 번을 실행해, 누가 통지를 받았는지 출력한다."""

    def one_shot_alert(price: int) -> None:
        """[Concrete Observer] 한 번 울리고 스스로 해제."""
        print(f"    알림: {price:,}원 도달 (구독 해제)")
        subject.observers.remove(one_shot_alert)

    def chart(price: int) -> None:
        """[Concrete Observer] 매번 갱신되어야 하는 차트."""
        print(f"    차트: {price:,}원으로 갱신")

    subject.observers += [one_shot_alert, chart]
    subject.notify(72000)


if __name__ == "__main__":
    print("[원본 순회] — 차트가 통지를 받지 못한다")
    run(NaiveSubject())
    print("[복사본 순회] — 알림이 빠져도 차트는 이번 통지를 받는다")
    run(SafeSubject())
