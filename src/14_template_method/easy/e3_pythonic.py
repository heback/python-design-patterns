"""14 템플릿 메서드 — 전략 버전: 골격은 그대로, 가변 단계를 상속 대신 주입한다.

상황: 부동소수 문제에 '오차 허용 비교'가 필요해졌다. 상속으로 하면 언어마다
FloatTolerantCppJudge 같은 클래스가 생겨 언어 수 x 비교 방식 수만큼 곱해진다.
파이썬에서는 단계가 함수이므로, 언어 단계 묶음(Toolchain)과 비교 함수(Checker)를 골라 끼운다.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

TIME_LIMIT = 1.0
Checker = Callable[[str, str], bool]   # (실제 출력, 기대 출력) -> 일치 여부. 메서드 하나라 함수로 충분


@dataclass
class Submission:
    """제출물(순진한 코드와 같다)."""
    source: str
    solve: Callable[[str], str]
    seconds: float = 0.1


@dataclass(frozen=True)
class Toolchain:
    """[언어 축] 한 언어의 단계 묶음. 단계가 여럿이고 함께 움직이므로 객체로 묶는다.

    compile이 None이면 '컴파일 없음'이다. 편하지만, 컴파일 언어에서 깜빡해도 아무도 알려 주지 않는다.
    """
    language: str
    compile: Callable[[str], None] | None = None


def exact(actual: str, expected: str) -> bool:
    """[비교 축] 정확 일치."""
    return actual.strip() == expected.strip()


def approx(actual: str, expected: str) -> bool:
    """[비교 축] 오차 허용. 패턴 코드라면 언어마다 하위 클래스가 하나씩 필요했다."""
    return abs(float(actual) - float(expected)) <= 1e-6


def need_main(source: str) -> None:
    """C++ 컴파일 흉내."""
    if "int main" not in source:
        raise ValueError("main 없음")


# 언어는 값으로 정의된다. 새 언어는 클래스가 아니라 Toolchain 값 하나를 더하는 일이다.
PYTHON = Toolchain("py")
CPP = Toolchain("cpp", compile=need_main)


class Judge:
    """[Context] 골격(순서)은 패턴 코드의 judge()와 같고, 단계만 바깥에서 받는다.

    비교를 짧게 하려고 샌드박스 정리와 validate·run 단계는 줄였다.
    """

    def __init__(self, toolchain: Toolchain, checker: Checker = exact) -> None:
        """두 축을 따로 고른다. 문제 설정에 따라 실행 중에 checker를 바꿀 수도 있다."""
        self.toolchain, self.checker = toolchain, checker

    def judge(self, sub: Submission, tests: list[tuple[str, str]]) -> str:
        """시간 검사 -> 비교 순서는 여전히 여기 한 곳에 있다."""
        # None 검사가 '훅의 기본값' 역할을 한다. 상속에서는 빈 메서드가 하던 일이다.
        if self.toolchain.compile is not None:
            try:
                self.toolchain.compile(sub.source)
            except ValueError:
                return "CE"
        for inp, expected in tests:
            out = sub.solve(inp)
            if sub.seconds > TIME_LIMIT:
                return "TLE"
            # 비교 방식은 언어와 무관한 두 번째 축이다. 그래서 따로 끼운다.
            if not self.checker(out, expected):
                return "WA"
        return "AC"


if __name__ == "__main__":
    tests = [("1 3", "0.333333")]
    sub = Submission("int main", lambda s: "0.3333334")
    print("[1] 언어 2 x 비교 2 = 채점기 4개, 추가 클래스 없이")
    for tc in (PYTHON, CPP):
        for ck in (exact, approx):
            print(f"    {tc.language} + {ck.__name__}: {Judge(tc, ck).judge(sub, tests)}")
    print("[2] C++인데 compile을 깜빡한 Toolchain — 빈 소스가 조용히 통과한다")
    forgot = Toolchain("cpp")
    print(f"    {Judge(forgot, approx).judge(Submission('', lambda s: '0.333333'), tests)}")
