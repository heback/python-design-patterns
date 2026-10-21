"""[14장 템플릿 메서드 · 합성 버전] 같은 채점 골격을, 상속 대신 단계 객체·함수를 주입해 만든다.

상황: 02에서 부동소수 오차 허용을 훅 재정의로 넣자 FloatTolerantCppJudge가 생겼고,
같은 일을 Python·Java에도 하려면 클래스가 '언어 × 비교 방식'으로 곱해진다는 것이 드러났다.
코드랩 팀은 "특수 저지(답이 여러 개인 문제)"까지 예고했다. 변이의 축이 둘(언어, 비교 방식)이 된 것이다.

이 파일은 골격은 그대로 두고, 가변 단계를 상속 대신 합성으로 공급한다(10장 전략 패턴).
  - 언어 축: `Toolchain` 값 객체(파일명·실행 + 선택적 검증·컴파일). 단계가 여럿이고 함께 움직이므로 객체.
  - 비교 축: `Checker = Callable[[str, str], bool]`. 단계가 하나이고 상태가 없으므로 함수.
골격 `Judge.judge()`는 상속되지 않는 구체 클래스의 메서드다. 하위 클래스 자체가 없으니
'골격을 오버라이드하지 말라'는 규칙(@final)도 필요 없어진다.
"""
from __future__ import annotations

import contextlib
import io
import shutil
import tempfile
import time
from dataclasses import dataclass
from functools import partial
from pathlib import Path
from typing import Any, Callable

TIME_LIMIT = 0.05


@dataclass
class Submission:
    """학생 제출물."""

    language: str
    source: str
    solve: Callable[[str], str]


Tests = list[tuple[str, str]]
Checker = Callable[[str, str], bool]     # (실제 출력, 기대 출력) → 일치 여부


class CompileError(Exception):
    """검증·컴파일 실패."""


@dataclass(frozen=True)
class Toolchain:
    """[Strategy: 언어 축] 언어별 단계 묶음. 클래스 계층 대신 '값'으로 언어를 표현한다.

    기본값 없는 필드(name, filename, run)가 템플릿 메서드의 '추상 단계'에 대응한다. dataclass라서
    빠뜨리면 생성 시점에 TypeError가 난다 — 02의 abstractmethod가 인스턴스화 시점에 잡는 것과 같다.
    validate/compile에 None을 허용한 것이 '훅 기본값'에 대응한다. 상속 버전에서는 기본 구현이
    상위 클래스에 숨어 있었지만, 여기서는 생성 코드에 드러난다.
    """

    name: str
    filename: str
    run: Callable[[Submission, str], str]
    validate: Callable[[str], None] | None = None
    compile: Callable[[str], None] | None = None


def simulate(sub: Submission, stdin: str) -> str:
    """실행 단계 흉내. 실제로는 언어마다 subprocess로 인터프리터/바이너리를 부르는 자리다."""
    return sub.solve(stdin)


def exact(actual: str, expected: str) -> bool:
    """[Strategy: 비교 축] 정확 일치 — 기본 체커."""
    return actual.strip() == expected.strip()


def within(actual: str, expected: str, tol: float) -> bool:
    """[Strategy: 비교 축] 오차 허용. partial로 tol을 묶어 Checker 모양으로 만든다.

    숫자가 아닌 출력("abc")은 float()에서 ValueError가 난다. 그대로 두면 골격의 except가
    학생의 런타임 에러(RE)로 오판하므로, 여기서 '틀린 출력'(False → WA)으로 번역한다.
    """
    try:
        return abs(float(actual) - float(expected)) <= tol
    except ValueError:
        return False


def any_order(actual: str, expected: str) -> bool:
    """[Strategy: 비교 축] 특수 저지 — 공백으로 구분된 답의 순서를 따지지 않는다."""
    return sorted(actual.split()) == sorted(expected.split())


def _need(token: str, msg: str) -> Callable[[str], None]:
    """'소스에 token이 있어야 한다'는 검사 함수를 만든다(컴파일 흉내용 팩토리)."""
    def check(source: str) -> None:
        """token이 없으면 CompileError."""
        if token not in source:
            raise CompileError(msg)
    return check


PYTHON = Toolchain("py", "main.py", simulate)
CPP = Toolchain("cpp", "main.cpp", simulate, compile=_need("int main", "undefined reference to main"))
JAVA = Toolchain("java", "Main.java", simulate, validate=_need("public class Main", "class Main 없음"),
                 compile=_need("static void main", "main 메서드 없음"))


class Judge:
    """[Context] 골격을 가진 구체 클래스. 상속받을 일이 없으므로 '닫혀 있음'이 구조로 보장된다.

    02와 비교하면 judge() 본문은 거의 같다. 다른 점은 self.compile(...) 같은 자기 호출이
    self.toolchain.compile(...) 같은 협력 객체 호출로 바뀐 것뿐이다. 그 작은 차이 덕분에
    언어와 체커를 독립적으로 조합할 수 있다(3 × 3 = 9가지 채점기를 클래스 0개로).
    """

    def __init__(self, toolchain: Toolchain, checker: Checker = exact) -> None:
        """두 축을 주입받는다."""
        self.toolchain = toolchain
        self.checker = checker

    def judge(self, sub: Submission, tests: Tests) -> str:
        """[골격] 02의 Judge.judge와 같은 순서. 바뀌는 것은 '누구에게 묻는가'뿐이다."""
        tc = self.toolchain                            # 지역 별칭: 골격이 '언어 축'에게 묻는 곳이 한눈에 보이게
        sandbox = Path(tempfile.mkdtemp(prefix=f"judge-{tc.name}-"))
        try:
            (sandbox / tc.filename).write_text(sub.source)
            if tc.validate:                            # 훅 = None 체크. 단순하지만 명시적이다.
                tc.validate(sub.source)
            if tc.compile:
                tc.compile(sub.source)
            for i, (inp, expected) in enumerate(tests, 1):
                start = time.perf_counter()
                out = tc.run(sub, inp)                 # 실행 단계도 언어 축에 묻는다
                if time.perf_counter() - start > TIME_LIMIT:
                    return f"TLE (#{i})"
                if not self.checker(out, expected):
                    return f"WA (#{i})"
            return "AC"
        except CompileError as e:
            return f"CE ({e})"
        except Exception as e:
            return f"RE ({type(e).__name__})"
        finally:
            shutil.rmtree(sandbox, ignore_errors=True)


if __name__ == "__main__":
    # 제출물 동작 두 가지: 부동소수 답(1/3)과, 답이 여러 개라 순서가 자유로운 문제의 답.
    third = lambda s: "0.3333333"
    pair = lambda s: "7 3"
    java_src = "public class Main { public static void main(String[] a){} }"
    cases = [
        ("Python + 정확 일치", Judge(PYTHON), Submission("py", "...", third), "0.333333333"),
        ("C++ + 오차 허용", Judge(CPP, partial(within, tol=1e-6)),
         Submission("cpp", "int main(){}", third), "0.333333333"),
        ("Java + 오차 허용", Judge(JAVA, partial(within, tol=1e-6)),
         Submission("java", java_src, third), "0.333333333"),
        ("Java + 순서 무관(특수 저지)", Judge(JAVA, any_order),
         Submission("java", java_src, pair), "3 7"),
    ]
    print("[1] 언어 축과 비교 축을 자유롭게 조합한다 — 추가 클래스 없음")
    # 각 채점기는 Judge 하나에 (Toolchain, Checker) 조합만 다르다. 02라면 클래스 네 개가 필요했다.
    for label, judge, sub, expected in cases:
        print(f"    {label:<24}: {judge.judge(sub, [('in', expected)])}")

    print("[2] 런타임에 체커를 바꿀 수도 있다(문제 설정을 DB에서 읽는 경우)")
    # DB에서 읽은 설정은 값 타입이 섞이므로 dict[str, Any]로 받는다(예: 문제 #1042의 설정).
    problem_config: dict[str, Any] = {"checker": "within", "tol": 1e-3}
    checker = partial(within, tol=problem_config["tol"])
    print("    ", Judge(PYTHON, checker).judge(Submission("py", "...", lambda s: "3.1416"),
                                              [("pi", "3.14159")]))

    print("[3] 검사가 어디까지 되는가 — 세 가지 시나리오((a)(b)는 02 데모 [7]과 대응)")
    # (a) 필수 단계 누락: run을 빼면 dataclass가 생성 시점에 거부한다(02의 abstractmethod와 같은 효과).
    try:
        Toolchain("go", "main.go")  # type: ignore[call-arg]
    except TypeError as e:
        print("     (a) run 누락 → 생성 시점 TypeError:", e)
    # (b) 시그니처 불일치: 인자 0개짜리 compile. 생성은 통과하고, 채점하면 골격의 except가
    #     '학생의 런타임 에러'로 오판한다. mypy는 arg-type 오류로 잡는다(실행 전 검사만이 잡는다).
    bad_sig = Toolchain("go", "main.go", simulate, compile=lambda: None)  # type: ignore[arg-type, misc]
    print("     (b) compile=lambda: None →", Judge(bad_sig).judge(
        Submission("go", "...", lambda s: "3"), [("1 2", "3")]), "← 채점기 결함인데 학생 탓이 된다")
    # (c) 시그니처는 맞지만 의미가 틀린 콜러블: print는 Callable[[str], None]과 호환된다.
    #     mypy도 통과하고 런타임에도 실패하지 않는다. 컴파일 검사 없이 AC가 나온다 — 아무도 못 잡는다.
    with contextlib.redirect_stdout(io.StringIO()):          # print가 소스를 찍는 소음을 숨긴다
        verdict = Judge(Toolchain("go", "main.go", simulate, compile=print)).judge(
            Submission("go", "no main here", lambda s: "3"), [("1 2", "3")])
    print("     (c) compile=print →", verdict, "← 타입 검사기도 런타임도 잡지 못한다(테스트의 몫)")
