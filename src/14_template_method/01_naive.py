"""[14장 템플릿 메서드 · 순진한 설계] 언어별 채점기 세 개를 복사-붙여넣기로 만든 온라인 저지.

상황: 코딩 교육 플랫폼 '코드랩'의 개발자 도윤은 파이썬 채점기를 먼저 만들었다.
소스 저장 → 실행 → 테스트 케이스 출력 비교 → 결과 기록. 이어서 C++(컴파일 필요)와
Java(클래스명 규칙 검사 + 컴파일) 채점기를 파이썬 채점기를 복사해 고쳐 만들었다.
그 뒤 '모든 언어'에 시간 제한, 샌드박스 정리, 일부 문제의 부동소수 오차 허용이 추가되었다.
이 파일은 그 결과를 보여 준다. 공통 절차가 세 벌이 되자 하나에서는 정리 단계가 빠졌고,
다른 하나에서는 단계 순서가 어긋나 같은 제출물이 언어에 따라 다른 판정을 받는다.

실행 환경: 교재 예제는 외부 컴파일러 없이 돌아가야 하므로 '컴파일'과 '실행'을 흉내 낸다.
제출물의 실제 동작은 `solve` 함수(입력 문자열 → 출력 문자열)로 표현한다. 샌드박스 디렉터리와
소스 파일 쓰기, 실행 시간 측정은 진짜로 수행한다. 디스크가 차는 버그를 실제로 보이기 위해서다.
"""
from __future__ import annotations

import shutil
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

TIME_LIMIT = 0.05   # 초. 데모가 빨리 끝나도록 작게 잡았다.


@dataclass
class Submission:
    """학생 제출물. solve는 '컴파일된 프로그램의 동작'을 흉내 내는 함수다."""

    language: str
    source: str
    solve: Callable[[str], str]


Tests = list[tuple[str, str]]   # (입력, 기대 출력)


class PythonJudge:
    """파이썬 채점기 — 가장 먼저 만들어졌고, 이후 요구사항이 가장 꼼꼼히 반영된 원본."""

    def judge(self, sub: Submission, tests: Tests, float_tol: float | None = None) -> str:
        """채점 후 판정 문자열(AC/WA/TLE/RE)을 돌려준다."""
        # 준비 단계: 제출물마다 격리된 디렉터리. 이 줄부터 finally까지가 세 클래스에 복제된다.
        sandbox = Path(tempfile.mkdtemp(prefix="judge-py-"))
        try:
            (sandbox / "main.py").write_text(sub.source)
            for i, (inp, expected) in enumerate(tests, 1):
                start = time.perf_counter()
                out = sub.solve(inp)
                elapsed = time.perf_counter() - start
                # 순서: 시간 제한을 '먼저' 본다. 느린 오답은 TLE다.
                if elapsed > TIME_LIMIT:
                    return f"TLE (#{i})"
                # 부동소수 오차 허용은 이 채점기에만 들어갔다.
                if float_tol is not None:
                    if abs(float(out) - float(expected)) > float_tol:
                        return f"WA (#{i})"
                elif out.strip() != expected.strip():
                    return f"WA (#{i})"
            return "AC"
        except Exception as e:                    # 제출물이 던진 예외 = 런타임 에러
            return f"RE ({type(e).__name__})"
        finally:
            shutil.rmtree(sandbox)                # 정리 단계: 나중에 추가되었다


class CppJudge:
    """C++ 채점기 — PythonJudge를 복사해 컴파일 단계를 끼워 넣었다."""

    def judge(self, sub: Submission, tests: Tests, float_tol: float | None = None) -> str:
        """채점. 위 메서드와 80% 같은 코드다."""
        # PythonJudge.judge에서 복사해 온 줄. 파일명만 바뀌었다 — '다른 부분'은 이렇게 작다.
        sandbox = Path(tempfile.mkdtemp(prefix="judge-cpp-"))
        try:
            (sandbox / "main.cpp").write_text(sub.source)
            if "int main" not in sub.source:      # 컴파일 흉내: main이 없으면 링크 실패
                return "CE"
            for i, (inp, expected) in enumerate(tests, 1):
                start = time.perf_counter()
                out = sub.solve(inp)
                elapsed = time.perf_counter() - start
                # ⚠ 문제: 복사한 뒤 출력 비교를 먼저 하도록 순서가 바뀌었다(누군가 "틀린 답이면
                #   시간은 볼 필요 없다"며 고쳤다). 그래서 느린 오답이 여기서는 WA가 된다.
                # ⚠ 문제: float_tol 인자를 받기만 하고 쓰지 않는다. 시그니처만 복사되었다.
                if out.strip() != expected.strip():
                    return f"WA (#{i})"
                if elapsed > TIME_LIMIT:
                    return f"TLE (#{i})"
            return "AC"
        except Exception as e:
            return f"RE ({type(e).__name__})"
        finally:
            shutil.rmtree(sandbox)


class JavaJudge:
    """Java 채점기 — CppJudge를 복사해 클래스명 검사를 추가했다."""

    def judge(self, sub: Submission, tests: Tests, float_tol: float | None = None) -> str:
        """채점."""
        # ⚠ 문제: try가 없다. 이 아래에서 무엇이 실패하든 샌드박스는 남는다.
        sandbox = Path(tempfile.mkdtemp(prefix="judge-java-"))
        (sandbox / "Main.java").write_text(sub.source)
        if "public class Main" not in sub.source:  # Java 규칙: 파일명과 공개 클래스명 일치
            return "CE (class Main 없음)"
        if "static void main" not in sub.source:
            return "CE"
        for i, (inp, expected) in enumerate(tests, 1):
            start = time.perf_counter()
            out = sub.solve(inp)
            elapsed = time.perf_counter() - start
            if out.strip() != expected.strip():
                return f"WA (#{i})"
            if elapsed > TIME_LIMIT:
                return f"TLE (#{i})"
        # ⚠ 문제: 샌드박스 정리(try/finally + rmtree)가 '모든 언어에 추가'될 때 이 파일만
        #   빠졌다. 채점할 때마다 임시 디렉터리가 남고, 몇 주 뒤 채점 서버 디스크가 가득 찬다.
        # ⚠ 문제: 예외 처리(RE 판정)도 빠져 제출물의 예외가 채점 서버까지 전파된다.
        return "AC"


def slow_wrong(inp: str) -> str:
    """시간 제한을 넘기면서 답도 틀리는 제출물."""
    time.sleep(0.08)
    return "42"


def leftover(prefix: str) -> int:
    """임시 디렉터리에 남은 샌드박스 수. 디스크 누수의 증거."""
    return len(list(Path(tempfile.gettempdir()).glob(prefix + "*")))


if __name__ == "__main__":
    # 두 수의 합 문제. 모든 데모가 같은 테스트를 써서 '채점기 차이'만 드러나게 한다.
    tests: Tests = [("1 2", "3"), ("10 20", "30")]
    add = lambda s: str(sum(map(int, s.split())))   # 정답 제출물의 동작

    print("[1] 세 언어 모두 정답 제출물은 AC")
    print("    Python:", PythonJudge().judge(Submission("py", "print(...)", add), tests))
    print("    C++   :", CppJudge().judge(Submission("cpp", "int main(){}", add), tests))
    java_src = "public class Main { public static void main(String[] a){} }"
    print("    Java  :", JavaJudge().judge(Submission("java", java_src, add), tests))

    print("[2] 같은 '느린 오답'인데 언어마다 판정이 다르다 — 단계 순서가 어긋났기 때문")
    print("    Python:", PythonJudge().judge(Submission("py", "...", slow_wrong), tests))
    print("    C++   :", CppJudge().judge(Submission("cpp", "int main(){}", slow_wrong), tests))

    print("[3] 부동소수 문제(1/3): Python만 오차 허용, C++은 인자를 무시한다")
    third = lambda s: "0.3333333"
    ftests: Tests = [("1 3", "0.333333333")]
    print("    Python:", PythonJudge().judge(Submission("py", "...", third), ftests, float_tol=1e-6))
    print("    C++   :", CppJudge().judge(Submission("cpp", "int main(){}", third), ftests, float_tol=1e-6))

    print("[4] 샌드박스 정리 누락: 채점 후 남은 임시 디렉터리 수")
    # 이전 실행의 잔여물과 섞이지 않도록 '증가분'만 센다.
    before = leftover("judge-java-")
    for _ in range(5):
        JavaJudge().judge(Submission("java", java_src, add), tests)
    print(f"    judge-java-*: {leftover('judge-java-') - before}개 증가 (python/cpp: "
          f"{leftover('judge-py-')}/{leftover('judge-cpp-')}개)")
    # 데모가 실제 디스크를 더럽히지 않도록 뒷정리한다(교재 독자의 /tmp를 위해).
    for d in Path(tempfile.gettempdir()).glob("judge-java-*"):
        shutil.rmtree(d, ignore_errors=True)
