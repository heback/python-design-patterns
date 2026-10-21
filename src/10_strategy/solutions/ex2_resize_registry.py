"""연습문제 2 해설: if mode == ... 로 고르던 보간 방식을 함수 전략 + 등록부로.

상황: 사진 편집 서비스의 리사이즈 함수가 mode 문자열로 보간 알고리즘을 고르고 있었다.
보간 방식은 '입력(픽셀 행, 목표 길이) → 출력(픽셀 행)'만 있는 순수 계산이고 설정
상태가 없다. 그래서 클래스 계층이 아니라 함수 전략이 가장 알맞다.

설명을 단순하게 하려고 이미지를 '회색조 픽셀 한 줄(list[int])'로 줄였다. 2차원으로
가도 전략의 구조는 같다.
"""
from __future__ import annotations

from typing import Callable

# [Strategy] 보간 함수의 모양. 원본 행과 목표 길이를 받아 새 행을 돌려준다.
Interpolator = Callable[[list[int], int], list[int]]

# 이름 → 보간 함수 등록부. 원래 함수의 if/elif 사슬이 이 dict 조회 한 번으로 바뀐다.
INTERPOLATORS: dict[str, Interpolator] = {}


def interpolator(name: str) -> Callable[[Interpolator], Interpolator]:
    """보간 함수를 등록부에 올리는 데코레이터. 새 방식 추가 = 함수 하나 + 이 줄 하나."""

    def deco(fn: Interpolator) -> Interpolator:
        """등록 후 원래 함수를 그대로 돌려준다(직접 호출·단위 테스트 가능)."""
        INTERPOLATORS[name] = fn
        return fn

    return deco


@interpolator("nearest")
def nearest(row: list[int], size: int) -> list[int]:
    """[Concrete Strategy] 최근접 이웃. 가장 빠르고, 계단 현상이 생긴다."""
    # 목표 좌표 i를 원본 좌표로 되돌려 가장 가까운 픽셀을 고른다.
    return [row[min(len(row) - 1, round(i * (len(row) - 1) / max(1, size - 1)))] for i in range(size)]


@interpolator("linear")
def linear(row: list[int], size: int) -> list[int]:
    """[Concrete Strategy] 선형 보간. 이웃 두 픽셀을 거리 비율로 섞는다."""
    out = []
    for i in range(size):
        x = i * (len(row) - 1) / max(1, size - 1)   # 원본 위의 실수 좌표
        lo = int(x)
        hi = min(lo + 1, len(row) - 1)
        t = x - lo                                   # lo에서 hi 쪽으로 간 비율
        out.append(round(row[lo] * (1 - t) + row[hi] * t))
    return out


@interpolator("box")
def box(row: list[int], size: int) -> list[int]:
    """[Concrete Strategy] 구간 평균. 축소할 때 앨리어싱이 적다."""
    step = len(row) / size
    return [round(sum(row[int(i * step):max(int(i * step) + 1, int((i + 1) * step))])
                  / max(1, int((i + 1) * step) - int(i * step))) for i in range(size)]


def resize(row: list[int], size: int, mode: str = "linear") -> list[int]:
    """[Context] 보간 방식을 이름으로 받아 위임한다. 이 함수에는 더 이상 분기가 없다.

    mode를 문자열로 받는 공개 API는 그대로 유지했다 — 호출하는 쪽 코드를 깨지 않기 위해서다.
    등록된 보간 함수(nearest, linear, box)는 모듈 함수로 남아 있어 직접 호출·단위 테스트할 수 있다.
    """
    try:
        algo = INTERPOLATORS[mode]
    except KeyError:
        raise ValueError(f"지원하지 않는 mode: {mode!r} (가능: {sorted(INTERPOLATORS)})") from None
    return algo(row, size)


if __name__ == "__main__":
    row = [0, 100, 200, 100, 0, 50, 250, 50]
    print("원본       :", row)
    for mode in INTERPOLATORS:
        print(f"{mode:8s} 4칸:", resize(row, 4, mode))
    print("linear  11칸:", resize(row, 11, "linear"))

    # 새 방식을 추가해도 resize()는 손대지 않는다(OCP). 런타임 등록도 가능하다.
    interpolator("max")(lambda r, n: [max(r[i * len(r) // n:(i + 1) * len(r) // n]) for i in range(n)])
    print("max     4칸:", resize(row, 4, "max"), "← resize() 수정 없이 추가된 전략")

    try:
        resize(row, 4, "bicubic")
    except ValueError as e:
        print("ValueError:", e)
