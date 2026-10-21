"""[14장 템플릿 메서드 · 파이썬다운 변형] 언어와 표준 라이브러리 속의 템플릿 메서드 읽기.

상황: 코드랩의 채점기가 자리를 잡자, 도윤은 다른 팀원 하은에게 "준비-본문-정리" 골격이
채점기 말고도 여기저기 있다는 이야기를 듣는다. 이 파일은 세 가지를 보인다.

A. `contextlib.contextmanager`: 준비 → (호출자의 본문) → 정리라는 골격을 제너레이터 하나로.
   상속 없이 '정리 단계를 빠뜨릴 수 없는' 구조를 얻는다. 샌드박스 관리에 딱 맞는다.
B. `__init_subclass__`: 하위 클래스가 정의되는 '순간'에 규칙을 검사한다. typing.final은
   타입 검사기만 보지만, 이것은 런타임에 골격 오버라이드와 필수 클래스 속성 누락을 막는다.
C. `unittest.TestCase`: setUp → test_* → tearDown은 우리가 매일 쓰는 템플릿 메서드다.
   프레임워크가 우리 메서드를 부른다(할리우드 원칙).
"""
from __future__ import annotations

import io
import shutil
import tempfile
import unittest
from contextlib import contextmanager
from pathlib import Path
from typing import Callable, ClassVar, Iterator

# ===========================================================================
# A. contextmanager — 함수 하나짜리 템플릿 메서드
# ===========================================================================

@contextmanager
def sandbox(language: str) -> Iterator[Path]:
    """[골격] 준비(디렉터리 생성) → yield(호출자의 본문) → 정리(삭제).

    yield 앞뒤가 템플릿 메서드의 고정 단계이고, with 블록 본문이 '가변 단계'다.
    가변 단계를 하위 클래스 메서드가 아니라 호출자의 코드 블록으로 받는다는 점이 다르다.
    try/finally 덕분에 본문이 예외로 끝나도 정리가 보장된다 — 01의 JavaJudge 버그가 불가능하다.
    """
    path = Path(tempfile.mkdtemp(prefix=f"judge-{language}-"))
    print(f"    [준비] {language} 샌드박스 생성")  # 임시 이름은 실행마다 달라 출력하지 않는다
    try:
        yield path
    finally:
        shutil.rmtree(path, ignore_errors=True)
        print(f"    [정리] {language} 샌드박스 삭제 (exists={path.exists()})")


# ===========================================================================
# B. __init_subclass__ — 하위 클래스 정의 시점 검증
# ===========================================================================

class Judge:
    """[Abstract Class] 하위 클래스가 지켜야 할 규칙을 '정의 시점'에 검사한다.

    ABC의 abstractmethod는 '인스턴스화 시점'에 잡는다. __init_subclass__는 그보다 이른
    '클래스 정의 시점', 즉 import하는 순간에 실패한다. 플러그인처럼 하위 클래스를 다른
    팀이 쓰는 경우, 서버 기동 시점에 바로 잡히는 편이 채점 도중 터지는 것보다 훨씬 낫다.
    """

    language: ClassVar[str]          # 하위 클래스가 반드시 정해야 하는 클래스 속성
    filename: ClassVar[str]
    _FINAL = ("judge",)              # 런타임에서 오버라이드를 금지할 골격 메서드

    def __init_subclass__(cls, **kwargs: object) -> None:
        """하위 클래스가 만들어질 때 파이썬이 자동으로 부른다."""
        super().__init_subclass__(**kwargs)
        for name in cls._FINAL:
            # cls.__dict__로 '이 클래스가 직접 정의했는지'만 본다(상속받은 것은 괜찮다).
            if name in cls.__dict__:
                raise TypeError(f"{cls.__name__}: 골격 메서드 {name}()는 재정의할 수 없습니다")
        missing = [a for a in ("language", "filename") if not hasattr(cls, a)]
        if missing:
            raise TypeError(f"{cls.__name__}: 클래스 속성 {missing} 이(가) 필요합니다")

    def judge(self, solve: Callable[[str], str], tests: list[tuple[str, str]]) -> str:
        """[Template Method] A의 sandbox를 골격 안에서 재사용한다 — 두 기법은 함께 쓰인다."""
        with sandbox(self.language) as box:
            (box / self.filename).write_text("...")
            self.compile(box)
            for inp, expected in tests:
                if solve(inp).strip() != expected.strip():
                    return "WA"
            return "AC"

    def compile(self, box: Path) -> None:
        """훅: 기본은 컴파일 없음."""


class PythonJudge(Judge):
    """[Concrete Class] 클래스 속성 두 개만으로 끝나는 채점기."""

    language = "py"
    filename = "main.py"


# ===========================================================================
# C. unittest.TestCase — 표준 라이브러리의 템플릿 메서드
# ===========================================================================

class SandboxTest(unittest.TestCase):
    """[Concrete Class] TestCase.run()이 템플릿 메서드이고, 우리는 훅 세 개를 채운다.

    run()의 골격: setUp() → 테스트 메서드 → tearDown(), 그리고 setUp이 성공했다면
    테스트가 실패해도 tearDown을 부른다. 우리는 run()을 부르지 않는다. 러너가 부른다.
    """

    calls: ClassVar[list[str]] = []

    def setUp(self) -> None:
        """훅: 기본은 no-op. 테스트마다 새 샌드박스를 준비한다."""
        self.box = Path(tempfile.mkdtemp(prefix="judge-test-"))
        self.calls.append("setUp")

    def tearDown(self) -> None:
        """훅: 테스트가 실패해도 불린다 — 정리 보장이라는 골격의 약속."""
        shutil.rmtree(self.box, ignore_errors=True)
        self.calls.append("tearDown")

    def test_passes(self) -> None:
        """가변 단계 1."""
        self.calls.append("test_passes")
        self.assertTrue(self.box.exists())

    def test_fails(self) -> None:
        """가변 단계 2 — 일부러 실패한다. 그래도 tearDown이 불리는지 본다."""
        self.calls.append("test_fails")
        self.assertEqual(1, 2)


if __name__ == "__main__":
    print("[A] contextmanager: 본문이 예외로 끝나도 정리된다")
    try:
        with sandbox("cpp") as box:
            (box / "main.cpp").write_text("int main(){}")
            raise RuntimeError("컴파일러 충돌")
    except RuntimeError as e:
        print(f"    예외는 호출자에게 전파: {e}")

    print("[B-1] 규칙을 지킨 하위 클래스는 평범하게 동작한다")
    print("    ", PythonJudge().judge(lambda s: "3", [("1 2", "3")]))

    print("[B-2] 골격을 재정의하는 하위 클래스는 '정의하는 순간' 거부된다")
    try:
        class SneakyJudge(Judge):
            """골격을 덮어써 시간 제한을 건너뛰려는 하위 클래스."""

            language, filename = "rb", "main.rb"

            def judge(self, solve, tests):  # type: ignore[override]
                """정리 단계를 생략한 '빠른' 채점."""
                return "AC"
    except TypeError as e:
        print("    TypeError:", e)

    print("[B-3] 필수 클래스 속성 누락도 정의 시점에 잡힌다")
    try:
        class KotlinJudge(Judge):
            """filename을 깜빡한 채점기."""

            language = "kt"
    except TypeError as e:
        print("    TypeError:", e)

    print("[C] unittest의 골격: 호출 순서를 기록해 본다")
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(SandboxTest)
    result = unittest.TextTestRunner(stream=io.StringIO(), verbosity=0).run(suite)
    print("    호출 순서:", " → ".join(SandboxTest.calls))
    print(f"    실행 {result.testsRun}개, 실패 {len(result.failures)}개 — 실패한 테스트 뒤에도 tearDown이 불렸다")
