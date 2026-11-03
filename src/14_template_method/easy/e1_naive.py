"""14 템플릿 메서드 — 순진한 코드: 채점 절차를 언어마다 복사한 채점기 세 개.

상황: 코드랩의 도윤은 파이썬 채점기를 복사해 C++ 채점기를, 그것을 다시 복사해 Java 채점기를 만들었다.
절차는 "샌드박스 준비 -> 실행 -> 시간 검사 -> 출력 비교 -> 정리"로 같아야 하는데,
사본마다 조금씩 어긋났다. 실행과 시간은 흉내 낸다(seconds = 그 제출물이 걸리는 시간).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

TIME_LIMIT = 1.0   # 초. 모든 언어에 같은 제한을 적용해야 공정하다
open_sandboxes: list[str] = []   # 정리되지 않고 남은 샌드박스(디스크를 채운다)


@dataclass
class Submission:
    """제출물. solve는 프로그램의 동작, seconds는 실행 시간을 흉내 낸다."""
    source: str
    solve: Callable[[str], str]
    seconds: float = 0.1


class PythonJudge:
    """파이썬 채점기 — 원본."""

    def judge(self, sub: Submission, tests: list[tuple[str, str]]) -> str:
        """준비 -> (시간 검사 -> 비교) x N -> 정리."""
        # 이 절차(순서와 정리)는 업무 규칙인데, 이 메서드 안에 '지역적인 선택'처럼 묻혀 있다.
        open_sandboxes.append("py")
        for inp, expected in tests:
            out = sub.solve(inp)
            if sub.seconds > TIME_LIMIT:      # 공정한 판정: 시간 검사가 비교보다 먼저
                # ⚠ 문제: 정리 코드가 출구마다 따로 있다. 출구가 하나 늘면 정리도 하나 더 써야 한다.
                open_sandboxes.remove("py")
                return "TLE"
            if out != expected:
                open_sandboxes.remove("py")
                return "WA"
        open_sandboxes.remove("py")
        return "AC"


class CppJudge:
    """C++ 채점기 — 파이썬 채점기를 복사하고 컴파일을 끼워 넣었다."""

    def judge(self, sub: Submission, tests: list[tuple[str, str]]) -> str:
        """⚠ 문제: 누군가 '틀렸으면 시간은 볼 필요 없다'며 비교를 시간 검사 앞으로 옮겼다."""
        open_sandboxes.append("cpp")
        if "int main" not in sub.source:          # 컴파일 흉내 — 이것만이 진짜 차이다
            open_sandboxes.remove("cpp")
            return "CE"
        for inp, expected in tests:
            out = sub.solve(inp)
            if out != expected:
                open_sandboxes.remove("cpp")
                return "WA"                       # 느린 오답이 여기서는 WA, 파이썬에서는 TLE
            if sub.seconds > TIME_LIMIT:
                open_sandboxes.remove("cpp")
                return "TLE"
        open_sandboxes.remove("cpp")
        return "AC"


class JavaJudge:
    """Java 채점기 — C++ 채점기를 다시 복사했다."""

    def judge(self, sub: Submission, tests: list[tuple[str, str]]) -> str:
        """⚠ 문제: '모든 언어에 정리 추가' 요구를 세 곳에 따로 반영하다가 여기서 빠뜨렸다."""
        open_sandboxes.append("java")
        # 정말로 다른 부분은 이 클래스 이름 검사 한 줄뿐이다. 나머지는 모두 복사본이다.
        if "public class Main" not in sub.source:
            return "CE"                           # 정리 없이 돌아간다 -> 샌드박스가 쌓인다
        for inp, expected in tests:
            # 순서는 파이썬 원본과 같지만, 그것은 우연일 뿐 아무것도 이 순서를 강제하지 않는다.
            if sub.seconds > TIME_LIMIT:
                return "TLE"
            if sub.solve(inp) != expected:
                return "WA"
        return "AC"


if __name__ == "__main__":
    tests = [("1 2", "3")]
    slow_wrong = Submission("int main / public class Main", lambda s: "42", seconds=2.0)
    # 2초 걸리고 답도 틀리는 제출물. 공정하다면 어느 언어든 같은 판정이어야 한다.
    print("[1] 같은 '느린 오답'을 세 언어로 채점")
    for j in (PythonJudge(), CppJudge(), JavaJudge()):
        print(f"    {type(j).__name__}: {j.judge(slow_wrong, tests)}")
    print(f"[2] 정리되지 않고 남은 샌드박스: {open_sandboxes}")
