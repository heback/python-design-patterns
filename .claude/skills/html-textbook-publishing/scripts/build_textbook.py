#!/usr/bin/env python3
"""교재 빌드 스크립트: chapters/*.html + src/**.py → textbook/.

상황: 집필자는 장 원고를 '본문 조각'으로 쓰고 코드는 <pre data-src="..."> 자리표시자로만
참조한다. 이 스크립트가 공통 레이아웃(base.html)을 씌우고, 자리표시자를 실제 코드로
치환한다. 그래서 원고에 적힌 코드가 src/ 의 파일과 어긋날 수 없다. 실행 결과는 미리 싣지
않는다. 독자가 브라우저에서 [▶ 실행]으로 직접 확인한다.

사용법:
    python3 build_textbook.py

종료 코드: 참조 누락·깨진 링크가 있으면 1.
"""
from __future__ import annotations

import html
import json
import re
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
SKILL = Path(__file__).resolve().parents[1]
CHAPTERS, SRC, OUT = ROOT / "chapters", ROOT / "src", ROOT / "textbook"
FULL = CHAPTERS / "full"    # 참고용 긴 버전 원고. 요약 판(chapters/{nn}-{slug}.html)이 기본이고 긴 버전은 {nn}-{slug}-full.html 로 나간다

# SVG 화살표 마커. 원고 작성자는 marker-end="url(#triangle)" 처럼 참조만 하면 된다.
SVG_DEFS = """<defs>
<marker id="triangle" viewBox="0 0 12 12" refX="11" refY="6" markerWidth="12" markerHeight="12" orient="auto-start-reverse"><path class="marker-hollow" d="M1 1 L11 6 L1 11 Z"/></marker>
<marker id="arrow" viewBox="0 0 12 12" refX="11" refY="6" markerWidth="10" markerHeight="10" orient="auto-start-reverse"><path class="marker-fill" d="M1 1 L11 6 L1 11" fill="none" style="fill:none;stroke-width:1.4"/></marker>
<marker id="diamond" viewBox="0 0 16 10" refX="1" refY="5" markerWidth="16" markerHeight="10" orient="auto-start-reverse"><path class="marker-hollow" d="M1 5 L8 1 L15 5 L8 9 Z"/></marker>
<marker id="diamond-fill" viewBox="0 0 16 10" refX="1" refY="5" markerWidth="16" markerHeight="10" orient="auto-start-reverse"><path class="marker-fill" d="M1 5 L8 1 L15 5 L8 9 Z"/></marker>
</defs>"""

problems: list[str] = []          # 빌드 중 발견한 문제. 끝에 모아서 출력한다.
term_locs: dict[str, str] = {}    # 용어 id → 정의(<dfn>)가 있는 출력 파일명(요약 판). 용어집 링크에 쓴다.
full_locs: dict[str, str] = {}    # 용어 id → 긴 버전의 정의 위치. 요약 판에 없는 용어의 용어집 링크로만 쓴다.


def load_terms() -> dict[str, dict]:
    """chapters/terms.json(용어 등록부)을 id → 항목 사전으로 읽는다. 없으면 빈 사전."""
    path = CHAPTERS / "terms.json"
    if not path.exists():
        return {}
    return {t["id"]: t for t in json.loads(path.read_text(encoding="utf-8"))}


TERMS = load_terms()


@dataclass
class Chapter:
    """원고 하나의 메타데이터와 본문."""

    nn: str
    slug: str
    title: str
    subtitle: str
    part: str
    body: str
    full: bool = False    # True면 참고용 긴 버전

    @property
    def out_name(self) -> str:
        """출력 파일명. 요약 판은 원고 파일명과 같고, 긴 버전은 -full 을 붙인다."""
        return f"{self.nn}-{self.slug}{'-full' if self.full else ''}.html"


def load_chapters(directory: Path = CHAPTERS, full: bool = False) -> list[Chapter]:
    """directory 의 원고를 번호순으로 읽어 메타 주석을 파싱한다. full=True면 참고용 긴 버전(chapters/full/)."""
    result = []
    for path in sorted(directory.glob("[0-9][0-9]-*.html")):
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
                              meta.get("part", ""), text.strip(), full))
    return result


def render_src(match: re.Match, chapter: Chapter, part: tuple[int, int] = (1, 1)) -> str:
    """<pre data-src="x.py" [data-lines="a-b"] [data-title="제목"]></pre> 를 캡션 달린 코드 블록으로 바꾼다.

    캡션에는 파일 경로·행 번호를 싣지 않는다. 학생은 코드 저장소의 존재를 알 필요가 없으므로
    원고가 정한 제목(data-title)만 보이고, 같은 코드를 나눠 싣는 경우에만 "(2/3)" 같은 순서를 덧붙인다.
    """
    rel, lines, title = match.group("path"), match.group("lines"), match.group("title")
    path = SRC / rel
    if not path.exists():
        problems.append(f"{chapter.out_name}: data-src 대상 없음 src/{rel}")
        return '<div class="missing-src">⚠ 코드를 불러오지 못했다</div>'
    if not title:
        problems.append(f"{chapter.out_name}: data-title 없음 ({rel})")
        title = "코드"
    code_lines = path.read_text(encoding="utf-8").rstrip("\n").splitlines()
    full = ""    # 일부 행만 보여 줄 때, 브라우저에서 실행·편집하려면 코드 전체가 필요하다
    caption = title
    if lines:
        full = f' data-full="{html.escape(chr(10).join(code_lines))}"'
        a, b = (int(x) for x in lines.split("-"))
        code_lines = code_lines[a - 1:b]
    if part[1] > 1:
        caption += f" ({part[0]}/{part[1]})"
    code = html.escape("\n".join(code_lines))
    return (f'<figure class="code"{full}><figcaption>{html.escape(caption)}</figcaption>'
            f'<pre><code class="language-python">{code}</code></pre></figure>')


SRC_PRE = re.compile(r'<pre\s+data-src="(?P<path>[^"]+)"(?:\s+data-lines="(?P<lines>\d+-\d+)")?'
                     r'(?:\s+data-title="(?P<title>[^"]*)")?\s*>\s*</pre>')


def process_body(ch: Chapter) -> tuple[str, str]:
    """본문 자리표시자 치환, SVG 마커 주입, 장 내부 목차 생성. (본문, 목차 HTML)을 돌려준다."""
    totals: dict[str, int] = {}     # 같은 파일을 몇 조각으로 나눠 싣는가
    for m in SRC_PRE.finditer(ch.body):
        totals[m.group("path")] = totals.get(m.group("path"), 0) + 1
    seen: dict[str, int] = {}

    def place(m: re.Match) -> str:
        path = m.group("path")
        seen[path] = seen.get(path, 0) + 1
        return render_src(m, ch, (seen[path], totals[path]))

    body = SRC_PRE.sub(place, ch.body)
    # 원고에 직접 쓴 표는 좁은 화면에서 가로 스크롤되도록 감싼다.
    body = re.sub(r"(<table\b.*?</table>)", r'<div class="table-wrap">\1</div>', body, flags=re.S)
    body = re.sub(r"(<svg\b[^>]*>)", lambda m: m.group(1) + SVG_DEFS, body)
    body = re.sub(r'<dfn\b[^>]*data-term="([^"]+)"[^>]*>', lambda m: render_dfn(m.group(1), ch), body)
    if ch.full:    # 긴 버전 안의 장 사이 링크는 긴 버전끼리 잇는다(요약 판에 없는 절 앵커로 가지 않도록)
        body = re.sub(r'href="(\d\d-[\w-]+)\.html', r'href="\1-full.html', body)
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
    (full_locs if ch.full else term_locs)[term_id] = ch.out_name
    return (f'<dfn class="term" id="term-{term_id}" data-term="{term_id}" '
            f'title="{html.escape(entry.get("short", ""))}">')


def render_glossary() -> str:
    """용어 등록부로 용어집 본문을 만든다. 각 항목은 처음 정의된 자리로 이어진다."""
    rows = []
    for t in sorted(TERMS.values(), key=lambda t: t["term"]):
        en = f' <span class="gl-en">{html.escape(t["en"])}</span>' if t.get("en") else ""
        loc, ref = term_locs.get(t["id"]), full_locs.get(t["id"])
        if loc is None and ref is None:
            problems.append(f"용어집: '{t['term']}'({t['id']})의 <dfn> 정의 위치가 원고에 없음")
            where = "—"
        else:
            note = "" if loc else " (긴 버전)"       # 요약 판에서 쓰지 않는 용어는 긴 버전의 정의로 잇는다
            loc = loc or ref
            where = f'<a href="{loc}#term-{t["id"]}">{loc.split("-", 1)[0]}장에서 처음 정의{note}</a>'.replace(
                "00장", "서론").replace("99장", "종합")
        rows.append(f'<tr id="gl-{t["id"]}"><th scope="row">{html.escape(t["term"])}{en}</th>'
                    f'<td>{html.escape(t.get("short", ""))}</td><td class="gl-where">{where}</td></tr>')
    return ('<section id="glossary"><p>교재에서 처음 정의하는 용어를 모았다. 오른쪽 링크는 그 용어가 '
            '처음 등장해 정의되는 자리로 이어진다. 본문에서 점선 밑줄이 있는 용어에 마우스를 올리면 같은 뜻이 보인다.</p>'
            f'<table class="glossary"><thead><tr><th>용어</th><th>뜻</th><th>위치</th></tr></thead>'
            f'<tbody>{"".join(rows)}</tbody></table></section>')


COURSE_LABEL = "객체지향프로그래밍.대구과학고등학교.2학기"    # 학생 교재의 과목명: 상단 바와 브라우저 탭 제목에 표시한다


def fill(template: str, **kw: str) -> str:
    """{{key}} 치환. 값이 없으면 빈 문자열."""
    kw.setdefault("course", COURSE_LABEL)
    return re.sub(r"\{\{(\w+)\}\}", lambda m: kw.get(m.group(1), ""), template)


def chapter_label(ch: Chapter) -> str:
    """'3장' 같은 짧은 라벨. 서론/종합은 번호 대신 이름."""
    return {"00": "서론", "99": "종합"}.get(ch.nn, f"{int(ch.nn)}장")


def build() -> int:
    """전체 빌드를 수행하고 종료 코드를 돌려준다."""
    template = (SKILL / "assets" / "base.html").read_text(encoding="utf-8")
    chapters = load_chapters()
    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "assets").mkdir(parents=True)
    for asset in ("style.css", "pyrun.css", "pyhl.js", "pyrun.js", "textbook-code.js"):    # 코드 실행·편집(Pyodide) 자산 포함
        shutil.copy(SKILL / "assets" / asset, OUT / "assets" / asset)

    fulls = [c for c in load_chapters(FULL, full=True) if (CHAPTERS / f"{c.nn}-{c.slug}.html").exists()]
    for c in load_chapters(FULL, full=True):
        if c not in fulls:
            problems.append(f"{c.out_name}: 대응하는 요약 판 chapters/{c.nn}-{c.slug}.html 없음")
    for group in (chapters, fulls):                  # 요약 판을 먼저 만든다(용어집이 요약 판의 정의 위치를 우선한다)
        for i, ch in enumerate(group):
            body, toc = process_body(ch)
            prev_ch = group[i - 1] if i > 0 else None
            next_ch = group[i + 1] if i + 1 < len(group) else None
            pager = '<nav class="pager">'
            if prev_ch:
                pager += f'<a class="prev" href="{prev_ch.out_name}"><small>← 이전 · {chapter_label(prev_ch)}</small>{prev_ch.title}</a>'
            if next_ch:
                pager += f'<a class="next" href="{next_ch.out_name}"><small>다음 · {chapter_label(next_ch)} →</small>{next_ch.title}</a>'
            pager += "</nav>"
            tag = " · 참고용 긴 버전" if ch.full else ""
            hero = (f'<header class="hero"><span class="part">{chapter_label(ch)}'
                    f'{" · " + ch.part if ch.part else ""}{tag}</span><h1>{ch.title}</h1>'
                    f'<p class="subtitle">{ch.subtitle}</p></header>')
            tabs = ""
            if ch.full:
                short = f"{ch.nn}-{ch.slug}.html"
                pager = pager.replace('<nav class="pager">', f'<nav class="pager"><a class="prev" href="{short}"><small>↑ 요약 판</small>{chapter_label(ch)} {ch.title}</a>', 1)
            if ch.full or (FULL / f"{ch.nn}-{ch.slug}.html").exists():
                # 요약 판 ↔ 원문(긴 버전) 탭. 상단 바에 고정되고, 누르면 읽던 절 위치로 같은 절 id를 따라 이동한다(textbook-code.js).
                short, long_ = f"{ch.nn}-{ch.slug}.html", f"{ch.nn}-{ch.slug}-full.html"
                tabs = ('<nav class="ver-tabs" aria-label="요약 판과 원문 전환">'
                        f'<a href="{short}" class="{"" if ch.full else "on"}" data-ver="short"{"" if ch.full else " aria-current=\"page\""} title="핵심만 간추린 글(기본)">요약 판</a>'
                        f'<a href="{long_}" class="{"on" if ch.full else ""}" data-ver="long"{" aria-current=\"page\"" if ch.full else ""} title="더 자세한 설명과 여러 변형(읽지 않아도 연습문제를 풀 수 있다)">원문 (긴 버전)</a></nav>')
            page = fill(template, page_title=f"{chapter_label(ch)} {re.sub(r'<[^>]+>', '', ch.title)}{' (참고용 긴 버전)' if ch.full else ' (요약)'} — 파이썬 디자인 패턴 · {COURSE_LABEL}",
                        body_class="chapter", part=ch.part, crumb=f"{chapter_label(ch)} · {ch.title}{tag}",
                        toc=toc, hero=hero, content=body, pager=pager, tabs=tabs, tabs_class=" has-tabs" if tabs else "")
            (OUT / ch.out_name).write_text(page, encoding="utf-8")
            print(f"  built {ch.out_name}")

    # ---- 용어집 ----
    if TERMS:
        glossary = fill(template, page_title=f"용어집 — 파이썬 디자인 패턴 · {COURSE_LABEL}", body_class="index", crumb="용어집",
                        hero='<header class="cover"><h1>용어집</h1></header>',
                        content=re.sub(r"(<table\b.*?</table>)", r'<div class="table-wrap">\1</div>',
                                       render_glossary(), flags=re.S))
        (OUT / "glossary.html").write_text(glossary, encoding="utf-8")
        print(f"  built glossary.html ({len(TERMS)} terms)")

    # 목차 페이지(index.html)는 만들지 않는다. 첫 화면은 배포 사이트의 표지(docs/index.html)가 맡는다.

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
        for href, frag in re.findall(r'href="([^"#:]+\.html)#([^"]+)"', text):       # 다른 장의 절·용어로 가는 링크
            target = OUT / href
            if target.exists() and frag not in set(re.findall(r'id="([^"]+)"', target.read_text(encoding="utf-8"))):
                problems.append(f"{page.name}: {href} 에 없는 앵커 #{frag}")

    print(f"\n{len(chapters)}개 장(요약 판) + 긴 버전 {len(fulls)}개 빌드 → {OUT.relative_to(ROOT)}/")
    for p in problems:
        print(f"  PROBLEM {p}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(build())
