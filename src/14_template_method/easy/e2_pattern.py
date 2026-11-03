"""14 템플릿 메서드 — 패턴 코드: 채점 절차의 골격을 Judge.judge() 한 곳에 고정한다.

상황: 도윤은 세 사본의 공통 절차를 상위 클래스 Judge로 끌어올린다. 순서와 정리는 골격이 정하고,
언어마다 반드시 다른 단계(run)는 추상 단계로, 있을 수도 없을 수도 있는 단계(validate, compile,
outputs_match)는 기본 구현이 있는 훅으로 연다.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Callable, final

TIME_LIMIT = 1.0
open_sandboxes: list[str] = []


@dataclass
class Submission:
    """제출물(순진한 코드와 같다)."""
    source: str
    solve: Callable[[str], str]
    seconds: float = 0.1


class CompileError(Exception):
    """훅은 이 예외를 던지기만 한다. 판정 문자열(CE)로 바꾸는 일은 골격이 맡는다."""


class Judge(ABC):
    """[Abstract Class] 채점 알고리즘의 골격을 소유한다.

    할리우드 원칙: 하위 클래스는 judge()를 부르지 않고, 단계를 언제 부를지도 정하지 않는다.
    """
    language = "?"

    @final
    def judge(self, sub: Submission, tests: list[tuple[str, str]]) -> str:
        """[Template Method] 순서는 여기서만 정한다. @final = '재정의하지 말라'는 표시."""
        open_sandboxes.append(self.language)
        try:
            self.validate(sub)                       # 훅: 기본은 통과
            self.compile(sub)                        # 훅: 기본은 '컴파일 없음'
            for inp, expected in tests:
                out = self.run(sub, inp)             # 추상 단계
                if sub.seconds > TIME_LIMIT:         # 시간 검사가 비교보다 먼저 — 모든 언어에서
                    return "TLE"
                if not self.outputs_match(out, expected):
                    return "WA"
            return "AC"
        except CompileError:
            return "CE"
        except Exception:
            return "RE"                              # 제출물이 실행 중 예외를 냈다
        finally:
            open_sandboxes.remove(self.language)     # 정리는 골격이 보장한다. 빠뜨릴 수 없다.

    @abstractmethod
    def run(self, sub: Submission, stdin: str) -> str:
        """[추상 단계] 실행. 합리적인 기본값이 없으니 하위 클래스가 반드시 채운다."""

    def validate(self, sub: Submission) -> None:
        """[훅] 소스 규칙 검사. 대부분 언어에는 없어서 기본은 no-op."""

    def compile(self, sub: Submission) -> None:
        """[훅] 컴파일. 인터프리터 언어에는 없어서 기본은 no-op."""

    def outputs_match(self, actual: str, expected: str) -> bool:
        """[훅] 출력 비교. 기본은 앞뒤 공백을 무시한 정확 일치."""
        return actual.strip() == expected.strip()


class PythonJudge(Judge):
    """[Concrete Class] 훅을 하나도 재정의하지 않는다. 기본값이 파이썬에 맞다."""
    language = "py"

    def run(self, sub: Submission, stdin: str) -> str:
        """실행 흉내."""
        return sub.solve(stdin)


class CppJudge(Judge):
    """[Concrete Class] compile 훅만 재정의한다."""
    language = "cpp"

    def run(self, sub: Submission, stdin: str) -> str:
        """실행 흉내."""
        return sub.solve(stdin)

    def compile(self, sub: Submission) -> None:
        """컴파일 흉내."""
        if "int main" not in sub.source:
            raise CompileError("main 없음")


class JavaJudge(Judge):
    """[Concrete Class] validate 훅만 재정의한다. 컴파일 '전'에 불린다는 순서는 골격이 보장한다."""
    language = "java"

    def run(self, sub: Submission, stdin: str) -> str:
        """실행 흉내."""
        return sub.solve(stdin)

    def validate(self, sub: Submission) -> None:
        """공개 클래스 이름 규칙."""
        if "public class Main" not in sub.source:
            raise CompileError("class Main 없음")


if __name__ == "__main__":
    tests = [("1 2", "3")]
    judges = [PythonJudge(), CppJudge(), JavaJudge()]
    print("[1] 느린 오답은 이제 모든 언어에서 TLE")
    for j in judges:
        print(f"    {j.language}: {j.judge(Submission('int main / public class Main', lambda s: '42', 2.0), tests)}")
    print("[2] 빈 소스: 컴파일 언어는 CE, 파이썬은 정상 채점(AC)")
    for j in judges:
        print(f"    {j.language}: {j.judge(Submission('', lambda s: '3'), tests)}")
    print(f"[3] 남은 샌드박스: {open_sandboxes}")
    print("[4] run을 빠뜨린 채점기는 객체를 만들 때 거부된다")
    class GoJudge(Judge):
        """run()을 깜빡한 채점기."""
        language = "go"
    try:
        GoJudge()
    except TypeError as e:
        print(f"    {e}")
