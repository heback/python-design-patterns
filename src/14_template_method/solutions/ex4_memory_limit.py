"""[14장 연습문제 4 해설] 모든 언어에 메모리 제한을 추가한다 — 골격 한 곳만 고치면 끝나는가?

상황: 코드랩에 "리스트에 10만 개를 쌓는 풀이가 채점 서버를 죽였다"는 장애가 났다.
모든 언어에 메모리 제한(MLE 판정)을 넣어야 한다. 01의 복붙 구조였다면 세 파일을 고치고
그중 하나를 빠뜨렸을 것이다. 템플릿 메서드에서는 골격의 테스트 루프만 고친다.

메모리 측정은 `tracemalloc`으로 제출물(solve 함수)의 파이썬 할당 최대치를 잰다.
실제 채점기라면 cgroup이나 setrlimit로 프로세스 메모리를 제한하겠지만, 골격의 어느 자리에
들어가는지가 이 문제의 요점이다. 언어별로 측정 방식이 달라야 한다면 그것을 훅으로 연다.
"""
from __future__ import annotations

import tracemalloc
import time
from typing import Callable, final

MEMORY_LIMIT = 1_000_000   # 바이트. 데모용으로 작게.
TIME_LIMIT = 0.5           # 초. tracemalloc이 실행을 느리게 하므로 02보다 넉넉히.


class Judge:
    """[Abstract Class] 02의 골격을 축약하고 메모리 검사를 추가했다.

    축약판이라 추상 단계(언어·파일명)는 생략했다. 남은 가변 단계는 모두 기본값이 있는 훅이다.
    """

    @final
    def judge(self, solve: Callable[[str], str], tests: list[tuple[str, str]]) -> str:
        """[Template Method] 순서: 실행 → 시간 검사 → [메모리 검사] → 비교. 추가된 것은 가운데 한 줄이다.

        MLE를 TLE 다음, 출력 비교 앞에 둔 이유: 자원 제한 위반은 답의 정오와 무관하게 판정되어야
        하고(느리거나 무거운 오답은 TLE/MLE), 두 제한 사이의 우선순위도 언어마다 같아야 한다.
        """
        self.compile()
        for i, (inp, expected) in enumerate(tests, 1):
            start = time.perf_counter()
            out, peak = self.measure(solve, inp)
            if time.perf_counter() - start > TIME_LIMIT:
                return f"TLE (#{i})"
            if peak > MEMORY_LIMIT:                    # [추가] 모든 언어에 자동 적용
                return f"MLE (#{i}, {peak // 1000}KB)"
            if out.strip() != expected.strip():
                return f"WA (#{i})"
        return "AC"

    def measure(self, solve: Callable[[str], str], inp: str) -> tuple[str, int]:
        """[새 훅] 실행 + 최대 메모리. 기본은 tracemalloc. JVM처럼 측정 방식이 다른 언어는 재정의한다.

        훅으로 연 이유: 'MLE 판정 규칙'은 모든 언어에서 같아야 하지만(골격), '측정 방법'은
        언어 런타임마다 다를 수 있다(가변 단계). 판정과 측정을 분리하면 규칙이 갈라지지 않는다.
        """
        tracemalloc.start()
        try:
            out = solve(inp)
            _, peak = tracemalloc.get_traced_memory()
        finally:
            tracemalloc.stop()
        return out, peak

    def compile(self) -> None:
        """훅: 기본은 컴파일 없음(02와 같다). 인터프리터 언어는 재정의하지 않는다."""


class PythonJudge(Judge):
    """[Concrete Class] 본문이 비어 있다 — 메모리 제한을 공짜로 얻고, compile 보일러플레이트도 없다."""


class JavaJudge(Judge):
    """[Concrete Class] JVM 힙 기준 측정을 흉내 내 measure 훅을 재정의한다."""

    def compile(self) -> None:
        """컴파일 흉내 — 컴파일 언어만 훅을 재정의한다."""

    def measure(self, solve: Callable[[str], str], inp: str) -> tuple[str, int]:
        """JVM은 기본 힙 오버헤드가 있다고 보고 측정값에 더한다(흉내). 판정 규칙은 골격 그대로."""
        out, peak = super().measure(solve, inp)
        return out, peak + 200_000


def hungry(inp: str) -> str:
    """정답이지만 메모리를 낭비하는 풀이: 필요 없는 리스트를 크게 만든다."""
    waste = list(range(100_000))
    return str(sum(map(int, inp.split()))) if waste else ""


if __name__ == "__main__":
    lean = lambda s: str(sum(map(int, s.split())))
    tests = [("1 2", "3")]
    for judge in (PythonJudge(), JavaJudge()):
        name = type(judge).__name__
        print(f"    {name:<11} 절약형: {judge.judge(lean, tests):<6} 낭비형: {judge.judge(hungry, tests)}")
    print("    PythonJudge·JavaJudge 본문에 메모리 판정 코드는 한 줄도 없다")
