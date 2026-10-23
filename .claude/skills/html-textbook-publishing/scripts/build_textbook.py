#!/usr/bin/env python3
"""교재 빌드 스크립트: chapters/*.html + src/**.py → textbook/.

상황: 집필자는 장 원고를 '본문 조각'으로 쓰고 코드는 <pre data-src="..."> 자리표시자로만
참조한다. 이 스크립트가 공통 레이아웃(base.html)을 씌우고, 자리표시자를 실제 코드와
실제 실행 결과로 치환한다. 그래서 원고에 적힌 코드/출력이 src/ 의 파일과 어긋날 수 없다.

사용법:
    python3 build_textbook.py            # 전체 빌드
    python3 build_textbook.py --no-run   # data-run 실행 생략(빠른 레이아웃 확인용)

종료 코드: 참조 누락·실행 실패·깨진 링크가 있으면 1.
"""
from __future__ import annotations

import html
import json
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
SKILL = Path(__file__).resolve().parents[1]
CHAPTERS, SRC, OUT = ROOT / "chapters", ROOT / "src", ROOT / "textbook"
PARTS = [("생성 패턴", "create"), ("구조 패턴", "struct"), ("행위 패턴", "behave")]

# SVG 화살표 마커. 원고 작성자는 marker-end="url(#triangle)" 처럼 참조만 하면 된다.
SVG_DEFS = """<defs>
<marker id="triangle" viewBox="0 0 12 12" refX="11" refY="6" markerWidth="12" markerHeight="12" orient="auto-start-reverse"><path class="marker-hollow" d="M1 1 L11 6 L1 11 Z"/></marker>
<marker id="arrow" viewBox="0 0 12 12" refX="11" refY="6" markerWidth="10" markerHeight="10" orient="auto-start-reverse"><path class="marker-fill" d="M1 1 L11 6 L1 11" fill="none" style="fill:none;stroke-width:1.4"/></marker>
<marker id="diamond" viewBox="0 0 16 10" refX="1" refY="5" markerWidth="16" markerHeight="10" orient="auto-start-reverse"><path class="marker-hollow" d="M1 5 L8 1 L15 5 L8 9 Z"/></marker>
<marker id="diamond-fill" viewBox="0 0 16 10" refX="1" refY="5" markerWidth="16" markerHeight="10" orient="auto-start-reverse"><path class="marker-fill" d="M1 5 L8 1 L15 5 L8 9 Z"/></marker>
</defs>"""

problems: list[str] = []          # 빌드 중 발견한 문제. 끝에 모아서 출력한다.
term_locs: dict[str, str] = {}    # 용어 id → 정의(<dfn>)가 있는 출력 파일명. 용어집 링크에 쓴다.


def load_terms() -> dict[str, dict]:
    """chapters/terms.json(용어 등록부)을 id → 항목 사전으로 읽는다. 없으면 빈 사전."""
    path = CHAPTERS / "terms.json"
    if not path.exists():
        return {}
    return {t["id"]: t for t in json.loads(path.read_text(encoding="utf-8"))}


TERMS = load_terms()
run_cache: dict[str, str] = {}    # 같은 파일을 여러 장에서 실행하지 않도록 캐시


@dataclass
class Chapter:
    """원고 하나의 메타데이터와 본문."""

    nn: str
    slug: str
    title: str
    subtitle: str
    part: str
    body: str

    @property
    def out_name(self) -> str:
        """출력 파일명. 원고 파일명과 같게 해 찾기 쉽게 한다."""
        return f"{self.nn}-{self.slug}.html"


def load_chapters() -> list[Chapter]:
    """chapters/ 의 원고를 번호순으로 읽어 메타 주석을 파싱한다."""
    result = []
    for path in sorted(CHAPTERS.glob("[0-9][0-9]-*.html")):
        text = path.read_text(encoding="utf-8")
        meta: dict[str, str] = {}
        m = re.search(r"<!--meta(.*?)-->", text, re.S)
        if m:
            for line in m.group(1).strip().splitlines():
                key, _, val = line.partition(":")
                meta[key.strip()] = val.strip()
            text = text[:m.start()] + text[m.end():]
        else:
            problems.append(f"{path.name}: 메타 주석 없음")
        nn, slug = path.stem.split("-", 1)
        result.append(Chapter(nn, slug, meta.get("title", slug), meta.get("subtitle", ""),
                              meta.get("part", ""), text.strip()))
    return result


def render_src(match: re.Match, chapter: Chapter) -> str:
    """<pre data-src="x.py" [data-lines="a-b"]></pre> 를 캡션 달린 코드 블록으로 바꾼다."""
    rel, lines = match.group("path"), match.group("lines")
    path = SRC / rel
    if not path.exists():
        problems.append(f"{chapter.out_name}: data-src 대상 없음 src/{rel}")
        return f'<div class="missing-src">⚠ 코드 파일 없음: src/{html.escape(rel)}</div>'
    code_lines = path.read_text(encoding="utf-8").rstrip("\n").splitlines()
    full = ""    # 일부 행만 보여 줄 때, 브라우저에서 실행·편집하려면 파일 전체가 필요하다
    caption = f"src/{rel}"
    if lines:
        full = f' data-full="{html.escape(chr(10).join(code_lines))}"'
        a, b = (int(x) for x in lines.split("-"))
        code_lines = code_lines[a - 1:b]
        caption += f"  ({a}–{b}행)"
    code = html.escape("\n".join(code_lines))
    return (f'<figure class="code"{full}><figcaption>{html.escape(caption)}</figcaption>'
            f'<pre><code class="language-python">{code}</code></pre></figure>')


def render_run(match: re.Match, chapter: Chapter, do_run: bool) -> str:
    """<pre data-run="x.py"></pre> 를 실제 실행 출력으로 바꾼다."""
    rel = match.group("path")
    path = SRC / rel
    if not path.exists():
        problems.append(f"{chapter.out_name}: data-run 대상 없음 src/{rel}")
        return f'<div class="missing-src">⚠ 실행 파일 없음: src/{html.escape(rel)}</div>'
    if not do_run:
        out = "(--no-run: 실행 생략)"
    elif rel in run_cache:
        out = run_cache[rel]
    else:
        proc = subprocess.run([sys.executable, path.name], cwd=path.parent,
                              capture_output=True, text=True, timeout=30)
        out = proc.stdout.rstrip()
        if proc.returncode != 0:
            problems.append(f"{chapter.out_name}: 실행 실패 src/{rel} — {proc.stderr.strip().splitlines()[-1:]}")
            out += "\n" + proc.stderr.rstrip()
        run_cache[rel] = out
    return (f'<figure class="output"><figcaption>$ python3 {html.escape(Path(rel).name)}</figcaption>'
            f'<pre><code>{html.escape(out)}</code></pre></figure>')


def process_body(ch: Chapter, do_run: bool) -> tuple[str, str]:
    """본문 자리표시자 치환, SVG 마커 주입, 장 내부 목차 생성. (본문, 목차 HTML)을 돌려준다."""
    body = re.sub(r'<pre\s+data-src="(?P<path>[^"]+)"(?:\s+data-lines="(?P<lines>\d+-\d+)")?\s*>\s*</pre>',
                  lambda m: render_src(m, ch), ch.body)
    body = re.sub(r'<pre\s+data-run="(?P<path>[^"]+)"\s*>\s*</pre>',
                  lambda m: render_run(m, ch, do_run), body)
    # 원고에 직접 쓴 표는 좁은 화면에서 가로 스크롤되도록 감싼다.
    body = re.sub(r"(<table\b.*?</table>)", r'<div class="table-wrap">\1</div>', body, flags=re.S)
    body = re.sub(r"(<svg\b[^>]*>)", lambda m: m.group(1) + SVG_DEFS, body)
    body = re.sub(r'<dfn\b[^>]*data-term="([^"]+)"[^>]*>', lambda m: render_dfn(m.group(1), ch), body)
    toc = []
    for sid, h2 in re.findall(r'<section\s+id="([\w-]+)"[^>]*>\s*<h2[^>]*>(.*?)</h2>', body, re.S):
        toc.append(f'<li><a href="#{sid}">{re.sub(r"<[^>]+>", "", h2).strip()}</a></li>')
    return body, f"<ol>{''.join(toc)}</ol>"


def render_dfn(term_id: str, ch: Chapter) -> str:
    """원고의 <dfn data-term="id">를 앵커·툴팁이 달린 정의 표시로 바꾸고 위치를 기록한다."""
    entry = TERMS.get(term_id)
    if entry is None:
        problems.append(f"{ch.out_name}: 등록되지 않은 용어 <dfn data-term=\"{term_id}\">")
        return f'<dfn class="term" data-term="{term_id}">'
    term_locs[term_id] = ch.out_name
    return (f'<dfn class="term" id="term-{term_id}" data-term="{term_id}" '
            f'title="{html.escape(entry.get("short", ""))}">')


def render_glossary() -> str:
    """용어 등록부로 용어집 본문을 만든다. 각 항목은 처음 정의된 자리로 이어진다."""
    rows = []
    for t in sorted(TERMS.values(), key=lambda t: t["term"]):
        en = f' <span class="gl-en">{html.escape(t["en"])}</span>' if t.get("en") else ""
        loc = term_locs.get(t["id"])
        if loc is None:
            problems.append(f"용어집: '{t['term']}'({t['id']})의 <dfn> 정의 위치가 원고에 없음")
            where = "—"
        else:
            where = f'<a href="{loc}#term-{t["id"]}">{loc.split("-", 1)[0]}장에서 처음 정의</a>'.replace(
                "00장", "서론").replace("99장", "종합")
        rows.append(f'<tr id="gl-{t["id"]}"><th scope="row">{html.escape(t["term"])}{en}</th>'
                    f'<td>{html.escape(t.get("short", ""))}</td><td class="gl-where">{where}</td></tr>')
    return ('<section id="glossary"><p>교재에서 처음 정의하는 용어를 모았다. 오른쪽 링크는 그 용어가 '
            '처음 등장해 정의되는 자리로 이어진다. 본문에서 점선 밑줄이 있는 용어에 마우스를 올리면 같은 뜻이 보인다.</p>'
            f'<table class="glossary"><thead><tr><th>용어</th><th>뜻</th><th>위치</th></tr></thead>'
            f'<tbody>{"".join(rows)}</tbody></table></section>')


def fill(template: str, **kw: str) -> str:
    """{{key}} 치환. 값이 없으면 빈 문자열."""
    return re.sub(r"\{\{(\w+)\}\}", lambda m: kw.get(m.group(1), ""), template)


def chapter_label(ch: Chapter) -> str:
    """'3장' 같은 짧은 라벨. 서론/종합은 번호 대신 이름."""
    return {"00": "서론", "99": "종합"}.get(ch.nn, f"{int(ch.nn)}장")


def build(do_run: bool) -> int:
    """전체 빌드를 수행하고 종료 코드를 돌려준다."""
    template = (SKILL / "assets" / "base.html").read_text(encoding="utf-8")
    chapters = load_chapters()
    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "assets").mkdir(parents=True)
    for asset in ("style.css", "pyrun.css", "pyrun.js", "textbook-code.js"):    # 코드 실행·편집(Pyodide) 자산 포함
        shutil.copy(SKILL / "assets" / asset, OUT / "assets" / asset)

    for i, ch in enumerate(chapters):
        body, toc = process_body(ch, do_run)
        prev_ch = chapters[i - 1] if i > 0 else None
        next_ch = chapters[i + 1] if i + 1 < len(chapters) else None
        pager = '<nav class="pager">'
        if prev_ch:
            pager += f'<a class="prev" href="{prev_ch.out_name}"><small>← 이전 · {chapter_label(prev_ch)}</small>{prev_ch.title}</a>'
        if next_ch:
            pager += f'<a class="next" href="{next_ch.out_name}"><small>다음 · {chapter_label(next_ch)} →</small>{next_ch.title}</a>'
        pager += "</nav>"
        hero = (f'<header class="hero"><span class="part">{chapter_label(ch)}'
                f'{" · " + ch.part if ch.part else ""}</span><h1>{ch.title}</h1>'
                f'<p class="subtitle">{ch.subtitle}</p></header>')
        page = fill(template, page_title=f"{chapter_label(ch)} {re.sub(r'<[^>]+>', '', ch.title)} — 파이썬 디자인 패턴",
                    body_class="chapter", part=ch.part, crumb=f"{chapter_label(ch)} · {ch.title}",
                    toc=toc, hero=hero, content=body, pager=pager)
        (OUT / ch.out_name).write_text(page, encoding="utf-8")
        print(f"  built {ch.out_name}")

    # ---- 용어집 ----
    if TERMS:
        glossary = fill(template, page_title="용어집 — 파이썬 디자인 패턴", body_class="index", crumb="용어집",
                        hero='<header class="cover"><h1>용어집</h1></header>',
                        content=re.sub(r"(<table\b.*?</table>)", r'<div class="table-wrap">\1</div>',
                                       render_glossary(), flags=re.S))
        (OUT / "glossary.html").write_text(glossary, encoding="utf-8")
        print(f"  built glossary.html ({len(TERMS)} terms)")

    # ---- 목차 페이지 ----
    def card(ch: Chapter) -> str:
        return (f'<a class="card" href="{ch.out_name}"><span class="num">{chapter_label(ch)}</span>'
                f'<span class="t">{ch.title}</span><span class="s">{ch.subtitle}</span></a>')

    blocks = []
    intro = [c for c in chapters if not c.part]
    if intro:
        blocks.append(f'<section class="part-block"><h2>시작과 정리</h2><div class="cards">{"".join(card(c) for c in intro)}</div></section>')
    for name, cls in PARTS:
        group = [c for c in chapters if c.part == name]
        if group:
            blocks.append(f'<section class="part-block {cls}"><h2>{name}</h2><div class="cards">{"".join(card(c) for c in group)}</div></section>')
    cover = ('<header class="cover"><h1>파이썬으로 배우는<br>디자인 패턴</h1>'
             '<p>객체지향 원리를 이미 아는 학생을 위한 교재. 장마다 실제 상황에서 출발해, '
             '순진한 설계가 무너지는 지점을 확인하고, 패턴과 파이썬다운 대안을 비교한다.</p></header>')
    if TERMS:
        blocks.append('<section class="part-block"><h2>부록</h2><div class="cards"><a class="card" href="glossary.html">'
                      f'<span class="num">용어집</span><span class="t">용어 {len(TERMS)}개</span>'
                      '<span class="s">교재에서 정의하는 용어와 처음 정의되는 위치</span></a></div></section>')
    index = fill(template, page_title="파이썬 디자인 패턴", body_class="index", crumb="목차",
                 hero=cover, content="".join(blocks))
    (OUT / "index.html").write_text(index, encoding="utf-8")
    print("  built index.html")

    # ---- 링크 검사 ----
    for page in OUT.glob("*.html"):
        text = page.read_text(encoding="utf-8")
        for href in re.findall(r'href="([^"#:]+\.html)', text):
            if not (OUT / href).exists():
                problems.append(f"{page.name}: 깨진 링크 {href}")
        ids = set(re.findall(r'id="([^"]+)"', text))
        for frag in re.findall(r'href="#([^"]+)"', text):
            if frag not in ids:
                problems.append(f"{page.name}: 없는 앵커 #{frag}")

    print(f"\n{len(chapters)}개 장 빌드 → {OUT.relative_to(ROOT)}/")
    for p in problems:
        print(f"  PROBLEM {p}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(build(do_run="--no-run" not in sys.argv))
