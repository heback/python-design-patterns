#!/usr/bin/env python3
"""교재 장(章)의 기계적 검증 스크립트.

상황: 교재는 '원고(chapters/*.html)'와 '실행 가능한 코드(src/**.py)'가 분리되어 있고,
빌드 시 원고의 <pre data-src=...> 자리표시자에 코드가 삽입된다. 이 스크립트는 사람이
매번 눈으로 확인하기 어려운 규칙 — 코드가 실제로 실행되는가, 주석이 충분한가,
맥락 설명이 코드보다 먼저 나오는가, 참조 경로가 살아 있는가 — 을 자동으로 확인한다.

사용법:
    python3 verify_chapter.py 03          # 3장 검증
    python3 verify_chapter.py 01 05 10    # 여러 장
    python3 verify_chapter.py all         # chapters/ 에 있는 모든 장

종료 코드: 실패(FAIL) 항목이 하나라도 있으면 1, 아니면 0. 경고(WARN)는 종료 코드에 영향 없음.
"""
from __future__ import annotations

import ast
import io
import re
import subprocess
import sys
import tokenize
from dataclasses import dataclass, field
from pathlib import Path

# 프로젝트 루트: 이 파일은 .claude/skills/code-verification/scripts/ 에 있으므로 4단계 위.
ROOT = Path(__file__).resolve().parents[4]
CHAPTERS = ROOT / "chapters"
SRC = ROOT / "src"

# 패턴 장(01~15)이 반드시 이 순서로 가져야 하는 섹션 id. 서론/종합 장은 goals만 필수.
PATTERN_SECTIONS = ["goals", "context", "naive", "structure", "implementation",
                    "pythonic", "tradeoffs", "exercises"]
COMMENT_RATIO_MIN = 0.30   # (주석 줄 + docstring 줄) / 비어 있지 않은 줄
RUN_TIMEOUT_SEC = 20       # 예제는 데모용이므로 이보다 오래 걸리면 무언가 잘못된 것


@dataclass
class Report:
    """검증 결과 누적기. 장 하나당 하나씩 만든다."""

    chapter: str
    fails: list[str] = field(default_factory=list)
    warns: list[str] = field(default_factory=list)
    oks: list[str] = field(default_factory=list)

    def check(self, cond: bool, ok_msg: str, fail_msg: str, *, warn: bool = False) -> None:
        """조건이 참이면 OK, 거짓이면 FAIL(또는 warn=True면 WARN)으로 기록한다."""
        if cond:
            self.oks.append(ok_msg)
        elif warn:
            self.warns.append(fail_msg)
        else:
            self.fails.append(fail_msg)

    def print(self) -> None:
        """사람이 읽기 좋은 형태로 출력한다. 검증 보고서에 그대로 붙여 넣을 수 있다."""
        print(f"\n=== 장 {self.chapter} ===")
        for m in self.oks:
            print(f"  OK   {m}")
        for m in self.warns:
            print(f"  WARN {m}")
        for m in self.fails:
            print(f"  FAIL {m}")
        verdict = "PASS" if not self.fails else "FAIL"
        print(f"  --> {verdict} (ok {len(self.oks)}, warn {len(self.warns)}, fail {len(self.fails)})")


# ---------------------------------------------------------------------------
# 파이썬 파일 검증
# ---------------------------------------------------------------------------

def docstring_lines(tree: ast.AST) -> set[int]:
    """모듈/클래스/함수 docstring이 차지하는 줄 번호 집합을 돌려준다."""
    lines: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            body = getattr(node, "body", [])
            if body and isinstance(body[0], ast.Expr) and isinstance(getattr(body[0], "value", None), ast.Constant) \
                    and isinstance(body[0].value.value, str):
                lines.update(range(body[0].lineno, (body[0].end_lineno or body[0].lineno) + 1))
    return lines


def comment_lines(source: str) -> set[int]:
    """'#' 주석 토큰이 있는 줄 번호 집합. 행 끝 주석도 그 줄을 '주석이 있는 줄'로 센다."""
    result: set[int] = set()
    for tok in tokenize.generate_tokens(io.StringIO(source).readline):
        if tok.type == tokenize.COMMENT and not tok.string.startswith("#!"):
            result.add(tok.start[0])
    return result


def verify_py(path: Path, rep: Report) -> None:
    """파이썬 파일 하나를 실행·구문·docstring·주석 비율 측면에서 검사한다."""
    rel = path.relative_to(SRC)
    source = path.read_text(encoding="utf-8")
    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        rep.fails.append(f"{rel}: 구문 오류 {e}")
        return

    # 1) 모듈 docstring — 파일만 열어도 '어떤 상황의 코드인지' 보여야 한다.
    rep.check(ast.get_docstring(tree) is not None,
              f"{rel}: 모듈 docstring 있음", f"{rel}: 모듈 docstring(상황 요약) 없음")

    # 2) 모든 클래스/함수에 docstring
    missing = [f"{n.name}(L{n.lineno})" for n in ast.walk(tree)
               if isinstance(n, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))
               and ast.get_docstring(n) is None]
    rep.check(not missing, f"{rel}: 모든 클래스/함수에 docstring",
              f"{rel}: docstring 없음 → {', '.join(missing[:8])}{' …' if len(missing) > 8 else ''}")

    # 3) 주석 비율
    nonblank = {i for i, line in enumerate(source.splitlines(), 1) if line.strip()}
    commented = (comment_lines(source) | docstring_lines(tree)) & nonblank
    ratio = len(commented) / max(1, len(nonblank))
    rep.check(ratio >= COMMENT_RATIO_MIN, f"{rel}: 주석 비율 {ratio:.0%}",
              f"{rel}: 주석 비율 {ratio:.0%} < {COMMENT_RATIO_MIN:.0%}")

    # 4) __main__ 데모 존재 (경고만 — 해설 코드 중 일부는 데모가 짧을 수 있음)
    rep.check('__name__ == "__main__"' in source or "__name__ == '__main__'" in source,
              f"{rel}: __main__ 데모 있음", f"{rel}: __main__ 데모 없음", warn=True)

    # 5) 실제 실행. cwd를 파일 위치로 두어 상대 경로 의존을 드러낸다.
    try:
        proc = subprocess.run([sys.executable, path.name], cwd=path.parent, capture_output=True,
                              text=True, timeout=RUN_TIMEOUT_SEC)
        tail = (proc.stderr or "").strip().splitlines()[-3:]
        rep.check(proc.returncode == 0, f"{rel}: 실행 성공",
                  f"{rel}: 실행 실패(exit {proc.returncode}) {' | '.join(tail)}")
        rep.check(bool(proc.stdout.strip()), f"{rel}: 데모 출력 있음", f"{rel}: 실행 출력이 비어 있음", warn=True)
    except subprocess.TimeoutExpired:
        rep.fails.append(f"{rel}: 실행 시간 초과({RUN_TIMEOUT_SEC}s)")


# ---------------------------------------------------------------------------
# 원고(HTML) 검증
# ---------------------------------------------------------------------------

def strip_details(html: str) -> str:
    """해설(<details>)과 연습문제 섹션을 지운다. lead-in 규칙은 본문 설명 흐름의 코드에만 적용한다
    (연습문제는 문제 서술 자체가 코드의 맥락이므로)."""
    html = re.sub(r"<details\b.*?</details>", "", html, flags=re.S)
    return re.sub(r'<section\s+id="exercises".*?</section>', "", html, flags=re.S)


def verify_html(nn: str, path: Path, rep: Report) -> set[str]:
    """원고 구조 규칙을 검사하고, 원고가 참조한 src 상대 경로 집합을 돌려준다."""
    html = path.read_text(encoding="utf-8")
    is_pattern = nn not in ("00", "99")

    meta = re.search(r"<!--meta(.*?)-->", html, re.S)
    rep.check(bool(meta and re.search(r"^\s*title:\s*\S", meta.group(1), re.M)),
              "메타 주석(title) 있음", "맨 위 <!--meta title: ... --> 블록 없음")

    # 섹션 존재와 순서
    ids = re.findall(r'<section\s+id="([\w-]+)"', html)
    required = PATTERN_SECTIONS if is_pattern else ["goals"]
    missing = [s for s in required if s not in ids]
    rep.check(not missing, "필수 섹션 모두 있음", f"필수 섹션 누락: {missing}")
    if is_pattern and not missing:
        order = [ids.index(s) for s in PATTERN_SECTIONS]
        rep.check(order == sorted(order), "섹션 순서 올바름", f"섹션 순서 틀림: {ids}")

    # 맥락 선행: #context에는 코드가 없어야 하고, 첫 코드 블록보다 앞에 있어야 한다.
    if is_pattern:
        ctx = re.search(r'<section\s+id="context".*?</section>', html, re.S)
        rep.check(bool(ctx) and "<pre" not in ctx.group(0), "#context 에 코드 없음 (맥락만)",
                  "#context 섹션 안에 코드 블록이 있음 — 상황 설명은 코드 없이")
        first_pre = html.find("<pre")
        rep.check(ctx is not None and (first_pre == -1 or ctx.start() < first_pre),
                  "상황 설명이 첫 코드보다 앞", "첫 코드 블록이 #context 보다 먼저 나옴")

    # 모든 본문 코드 블록 앞에 lead-in 문단 (해설 영역 제외, data-run 제외)
    body = strip_details(html)
    no_lead = []
    for m in re.finditer(r"<pre(?![^>]*data-run)[^>]*>", body):
        prev_end = max(body.rfind("</pre>", 0, m.start()), body.rfind("<section", 0, m.start()), 0)
        if 'class="lead-in"' not in body[prev_end:m.start()]:
            line = body.count("\n", 0, m.start()) + 1
            no_lead.append(f"~L{line}")
    rep.check(not no_lead, "모든 본문 코드 앞에 lead-in 문단", f"lead-in 없는 코드 블록: {no_lead}")

    # 참조 경로 무결성
    refs: set[str] = set()
    for attr, rel, lines in re.findall(r'data-(src|run)="([^"]+)"(?:\s+data-lines="([^"]+)")?', html):
        refs.add(rel)
        target = SRC / rel
        if not target.exists():
            rep.fails.append(f"data-{attr} 대상 없음: src/{rel}")
            continue
        if lines:
            a, _, b = lines.partition("-")
            n = len(target.read_text(encoding="utf-8").splitlines())
            if not (a.isdigit() and b.isdigit() and 1 <= int(a) <= int(b) <= n):
                rep.fails.append(f"data-lines 범위 오류: {rel} {lines} (파일 {n}줄)")
    rep.oks.append(f"코드 참조 {len(refs)}개 확인")

    # 원고에 직접 쓴 파이썬 코드(연습문제용)도 주석이 있어야 한다.
    for m in re.finditer(r'<code class="language-python">(.*?)</code>', html, re.S):
        code = m.group(1)
        if code.count("\n") >= 4 and "#" not in code:
            rep.warns.append("원고에 직접 쓴 코드 블록에 주석이 없음: " + code.strip().splitlines()[0][:50])

    if is_pattern:
        # 다이어그램
        struct = re.search(r'<section\s+id="structure".*?</section>', html, re.S)
        rep.check(bool(struct and "<svg" in struct.group(0)), "#structure 에 SVG 다이어그램 있음",
                  "#structure 에 SVG 다이어그램 없음")
        hard = re.findall(r'(?:fill|stroke)="#[0-9a-fA-F]{3,6}"', html)
        rep.check(not hard, "SVG 색 하드코딩 없음", f"SVG 색 하드코딩 {len(hard)}곳 (다크 모드 깨짐)", warn=True)
        # 연습문제
        exercises = re.findall(r'<div class="exercise".*?(?=<div class="exercise"|</section>)', html, re.S)
        rep.check(len(exercises) >= 3, f"연습문제 {len(exercises)}개", f"연습문제 {len(exercises)}개 (<3)")
        unsolved = [i + 1 for i, ex in enumerate(exercises) if 'class="solution"' not in ex]
        rep.check(not unsolved, "모든 연습문제에 해설", f"해설 없는 연습문제: {unsolved}")
    return refs


def verify(nn: str) -> Report:
    """장 하나를 검증한다."""
    rep = Report(nn)
    chapter = sorted(CHAPTERS.glob(f"{nn}-*.html"))
    rep.check(len(chapter) == 1, f"원고 {chapter[0].name if chapter else ''}",
              f"chapters/{nn}-*.html 원고가 {len(chapter)}개")
    refs: set[str] = set()
    if len(chapter) == 1:
        refs = verify_html(nn, chapter[0], rep)

    src_dirs = sorted(SRC.glob(f"{nn}_*"))
    if nn not in ("00", "99"):
        rep.check(len(src_dirs) == 1, "코드 디렉터리 있음", f"src/{nn}_*/ 디렉터리가 {len(src_dirs)}개")
    for d in src_dirs:
        for py in sorted(d.rglob("*.py")):
            verify_py(py, rep)
            rel = str(py.relative_to(SRC))
            rep.check(rel in refs, f"{rel}: 원고에서 참조됨", f"{rel}: 원고에서 참조되지 않음", warn=True)
    return rep


def main(argv: list[str]) -> int:
    """명령행 진입점."""
    if not argv:
        print(__doc__)
        return 2
    if argv == ["all"]:
        argv = sorted({p.name[:2] for p in CHAPTERS.glob("*.html")})
    reports = [verify(a.zfill(2)) for a in argv]
    for r in reports:
        r.print()
    failed = [r.chapter for r in reports if r.fails]
    print(f"\n총 {len(reports)}장, 실패 {len(failed)}장 {failed if failed else ''}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
