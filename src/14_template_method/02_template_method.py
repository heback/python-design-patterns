"""[14장 템플릿 메서드 · 패턴 적용] 채점 절차의 골격을 상위 클래스 한 곳에 고정한다.

상황: 01_naive.py에서 도윤의 채점기 세 개는 같은 절차를 세 벌로 가졌다. 그 결과 Java 채점기는
샌드박스를 정리하지 않았고, C++ 채점기는 시간 검사와 출력 비교의 순서가 뒤바뀌어 같은
제출물이 언어마다 다른 판정을 받았다. 이 파일은 GoF 템플릿 메서드로 다시 짠 버전이다.

  - `Judge.judge()`가 템플릿 메서드다. 준비 → 검증 → 컴파일 → (실행 → 시간 검사 → 비교)×N
    → 정리 → 기록이라는 '순서'를 여기서만 정의한다. 하위 클래스는 이 순서를 바꿀 수 없다.
  - 언어마다 반드시 달라야 하는 단계(소스 파일명, 실행)는 추상 메서드(abstract step)다.
  - 언어에 따라 있을 수도 없을 수도 있는 단계(검증, 컴파일, 출력 비교 방식)는 기본 구현이 있는
    훅(hook)이다.

외부 컴파일러 없이 돌아가도록 컴파일·실행은 흉내 낸다(01과 같은 방식).
"""
from __future__ import annotations

import shutil
import tempfile
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, final

TIME_LIMIT = 0.05


@dataclass
class Submission:
    """학생 제출물. solve는 컴파일된 프로그램의 동작을 흉내 낸다."""

    language: str
    source: str
    solve: Callable[[str], str]


Tests = list[tuple[str, str]]


class CompileError(Exception):
    """검증·컴파일 단계의 실패. 훅이 이 예외를 던지면 골격이 CE 판정으로 번역한다."""


class Judge(ABC):
    """[Abstract Class] 채점 알고리즘의 골격을 소유한다.

    할리우드 원칙("우리에게 전화하지 마라, 우리가 전화하겠다"): 하위 클래스는 judge()를
    부르지도, 단계를 부르는 순서를 정하지도 않는다. 하위 클래스는 단계만 채우고, 언제
    불릴지는 이 클래스가 정한다. 제어가 역전되어 있다.
    """

    def __init__(self) -> None:
        """채점 기록. 기록 단계가 골격에 있으므로 어느 언어든 빠짐없이 쌓인다."""
        self.records: list[str] = []

    # ---------------------------------------------------------------------
    # 템플릿 메서드
    # ---------------------------------------------------------------------
    @final
    def judge(self, sub: Submission, tests: Tests) -> str:
        """[Template Method] 채점 절차. @final: 하위 클래스가 '순서'를 재정의하지 말라는 선언.

        typing.final은 런타임에는 아무것도 막지 않는다. mypy·pyright 같은 타입 검사기가
        오버라이드를 오류로 잡아 줄 뿐이다. 런타임 강제가 필요하면 04의 __init_subclass__를 보라.
        """
        sandbox = Path(tempfile.mkdtemp(prefix=f"judge-{self.language()}-"))
        try:
            src = sandbox / self.source_filename()
            src.write_text(sub.source)
            self.validate(sub)                       # 훅: 기본은 통과
            self.compile(src, sub)                   # 훅: 기본은 '컴파일 없음'
            verdict = self._run_tests(src, sub, tests)
        except CompileError as e:
            verdict = f"CE ({e})"
        except Exception as e:                       # 제출물 예외 = 런타임 에러
            verdict = f"RE ({type(e).__name__})"
        finally:
            # 정리는 골격이 보장한다. 01의 JavaJudge처럼 '빠뜨릴' 하위 클래스가 존재할 수 없다.
            shutil.rmtree(sandbox, ignore_errors=True)
        self.records.append(f"{self.language()}: {verdict}")
        return verdict

    @final
    def _run_tests(self, src: Path, sub: Submission, tests: Tests) -> str:
        """테스트 루프도 골격의 일부다. 시간 검사 → 출력 비교 순서가 모든 언어에서 같다."""
        for i, (inp, expected) in enumerate(tests, 1):
            start = time.perf_counter()
            out = self.run(src, sub, inp)
            if time.perf_counter() - start > TIME_LIMIT:
                return f"TLE (#{i})"                 # 느린 오답은 어느 언어든 TLE
            if not self.outputs_match(out, expected):
                return f"WA (#{i})"
        return "AC"

    # ---------------------------------------------------------------------
    # 추상 단계: 하위 클래스가 반드시 채워야 한다
    # ---------------------------------------------------------------------
    @abstractmethod
    def language(self) -> str:
        """언어 식별자(샌드박스 이름·기록에 쓰인다)."""

    @abstractmethod
    def source_filename(self) -> str:
        """샌드박스에 저장할 파일명. 언어마다 규칙이 다르므로 기본값이 있을 수 없다."""

    @abstractmethod
    def run(self, src: Path, sub: Submission, stdin: str) -> str:
        """프로그램 실행. 실제로는 subprocess로 인터프리터/바이너리를 부르는 자리다."""

    # ---------------------------------------------------------------------
    # 훅: 기본 구현이 있고, 필요한 하위 클래스만 재정의한다
    # ---------------------------------------------------------------------
    def validate(self, sub: Submission) -> None:
        """소스 규칙 검사. 대부분 언어에는 없으므로 기본은 아무것도 하지 않는다."""

    def compile(self, src: Path, sub: Submission) -> None:
        """컴파일. 인터프리터 언어에는 없으므로 기본은 no-op."""

    def outputs_match(self, actual: str, expected: str) -> bool:
        """출력 비교. 기본은 앞뒤 공백을 무시한 정확 일치."""
        return actual.strip() == expected.strip()


# ---------------------------------------------------------------------------
# 구체 채점기: 각자 '다른 부분'만 쓴다. 공통 절차는 한 줄도 없다.
# ---------------------------------------------------------------------------

class PythonJudge(Judge):
    """[Concrete Class] 훅을 하나도 재정의하지 않는다 — 기본값이 파이썬에 맞게 설계되었다."""

    def language(self) -> str:
        """언어 식별자."""
        return "py"

    def source_filename(self) -> str:
        """파일명."""
        return "main.py"

    def run(self, src: Path, sub: Submission, stdin: str) -> str:
        """실행 흉내."""
        return sub.solve(stdin)


class CppJudge(Judge):
    """[Concrete Class] compile 훅만 재정의한다."""

    def language(self) -> str:
        """언어 식별자."""
        return "cpp"

    def source_filename(self) -> str:
        """파일명."""
        return "main.cpp"

    def compile(self, src: Path, sub: Submission) -> None:
        """컴파일 흉내: main이 없으면 링크 실패."""
        if "int main" not in src.read_text():
            raise CompileError("undefined reference to main")

    def run(self, src: Path, sub: Submission, stdin: str) -> str:
        """실행 흉내."""
        return sub.solve(stdin)


class JavaJudge(Judge):
    """[Concrete Class] validate와 compile 두 훅을 재정의한다."""

    def language(self) -> str:
        """언어 식별자."""
        return "java"

    def source_filename(self) -> str:
        """Java는 공개 클래스명과 파일명이 같아야 한다."""
        return "Main.java"

    def validate(self, sub: Submission) -> None:
        """클래스명 규칙 검사. 컴파일 '전'에 불린다는 순서는 골격이 보장한다."""
        if "public class Main" not in sub.source:
            raise CompileError("class Main 없음")

    def compile(self, src: Path, sub: Submission) -> None:
        """컴파일 흉내."""
        if "static void main" not in src.read_text():
            raise CompileError("main 메서드 없음")

    def run(self, src: Path, sub: Submission, stdin: str) -> str:
        """실행 흉내."""
        return sub.solve(stdin)


class FloatTolerantCppJudge(CppJudge):
    """[Concrete Class] 부동소수 문제용 C++ 채점기 — 상속 기반 설계의 한계가 드러나는 지점.

    오차 허용은 '언어'가 아니라 '문제'의 속성이다. 그런데 상속 축은 언어 하나뿐이라,
    오차 허용을 훅 재정의로 넣으려면 FloatTolerantPythonJudge, FloatTolerantJavaJudge…
    언어 수만큼 클래스가 곱해진다. 변이의 축이 둘이 되는 순간 템플릿 메서드는 버거워진다.
    03_strategy_version.py가 이 문제를 합성으로 푼다.
    """

    tolerance = 1e-6

    def outputs_match(self, actual: str, expected: str) -> bool:
        """훅 재정의: 절대 오차 비교. 숫자가 아닌 출력은 ValueError → 골격이 RE로 오판한다(03의 within은 WA로 처리)."""
        return abs(float(actual) - float(expected)) <= self.tolerance


def slow_wrong(inp: str) -> str:
    """시간 제한을 넘기면서 답도 틀리는 제출물."""
    time.sleep(0.08)
    return "42"


if __name__ == "__main__":
    tests: Tests = [("1 2", "3"), ("10 20", "30")]
    add = lambda s: str(sum(map(int, s.split())))
    java_src = "public class Main { public static void main(String[] a){} }"
    py, cpp, java = PythonJudge(), CppJudge(), JavaJudge()
    # 같은 머신의 다른 채점·이전 실행 잔여물과 섞이지 않도록 '증가분'만 센다([6]).
    before = len(list(Path(tempfile.gettempdir()).glob("judge-*")))

    print("[1] 정답 제출물")
    print("    ", py.judge(Submission("py", "...", add), tests),
          cpp.judge(Submission("cpp", "int main(){}", add), tests),
          java.judge(Submission("java", java_src, add), tests))

    print("[2] 느린 오답: 이제 모든 언어가 같은 판정")
    print("    ", py.judge(Submission("py", "...", slow_wrong), tests),
          "/", cpp.judge(Submission("cpp", "int main(){}", slow_wrong), tests))

    print("[3] 컴파일 오류는 훅이 던지고 골격이 CE로 번역한다")
    print("    ", java.judge(Submission("java", "class Solution {}", add), tests))
    print("    ", cpp.judge(Submission("cpp", "void f(){}", add), tests))

    print("[4] 런타임 에러도 골격이 처리 — 하위 클래스는 try/except를 쓰지 않았다")
    print("    ", java.judge(Submission("java", java_src, lambda s: str(1 // 0)), tests))

    print("[5] 부동소수 문제: 훅 재정의로 해결했지만 클래스가 '언어 × 비교방식'으로 곱해진다")
    third = lambda s: "0.3333333"
    print("    ", FloatTolerantCppJudge().judge(Submission("cpp", "int main(){}", third),
                                                [("1 3", "0.333333333")]))

    print("[6] 정리 보장: 이 데모가 남긴 샌드박스 수 =",
          len(list(Path(tempfile.gettempdir()).glob("judge-*"))) - before)
    print("    기록:", java.records)

    print("[7] abstractmethod가 잡는 것과 못 잡는 것")
    try:
        class GoJudge(Judge):
            """run을 빠뜨린 채점기."""

            def language(self) -> str:
                """언어 식별자."""
                return "go"

            def source_filename(self) -> str:
                """파일명."""
                return "main.go"
        GoJudge()
    except TypeError as e:
        print("     run 누락 → 인스턴스화 시점 TypeError:", e)

    class SloppyJudge(PythonJudge):
        """run의 '이름'은 있지만 시그니처가 틀렸다. abstractmethod는 이름만 보므로 통과한다."""

        def run(self) -> str:  # type: ignore[override]
            """인자를 빠뜨린 실행 단계 — mypy는 override 오류로 잡지만 런타임은 모른다."""
            return ""
    print("     시그니처가 틀린 run →", SloppyJudge().judge(Submission("py", "...", add), tests),
          "← 채점기 결함이 학생의 런타임 에러로 오판된다")
