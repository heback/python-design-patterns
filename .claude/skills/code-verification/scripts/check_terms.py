#!/usr/bin/env python3
"""교재 전체의 용어 정의 순서 검사: "처음 등장하는 곳에서 정의되었는가".

상황: 교재는 00 → 01 … 15 → 99 순서로 읽힌다. 어떤 용어(예: '훅')가 3장에서 처음
쓰이고 14장에서야 정의되면, 3장을 읽는 학생은 뜻을 모른 채 지나간다. 장별 검증
(verify_chapter.py)은 장 하나만 보므로 이런 '책 단위' 순서 문제를 잡지 못한다.

이 스크립트는 독자가 실제로 보는 순서대로 텍스트 흐름을 만든다 — 원고 본문에
<pre data-src>가 가리키는 코드(주석 포함)를 그 자리에 끼워 넣는다 — 그리고
chapters/terms.json 에 등록된 각 용어에 대해 다음을 확인한다.

    1. 원고 어딘가에 <dfn data-term="id">…</dfn> 정의 표시가 정확히 하나 있다.
    2. 그 정의 표시가 책 전체에서 그 용어(별칭 포함)의 '첫 등장'이다.

학습 목표(#goals)와 data-preview 속성을 단 블록은 예고이므로 '첫 등장'에서 제외한다.

사용법:
    python3 check_terms.py            # 검사 (위반 시 종료 코드 1)
    python3 check_terms.py --first    # 모든 용어의 첫 등장 위치 표 (계획 수립용)
    python3 check_terms.py --scan 훅 hook   # 등록 없이 임의 문자열의 첫 등장 위치만 확인
    python3 check_terms.py --chapter 00 05   # 첫 등장 또는 정의가 이 장들에 있는 용어만 검사(분담 작업용)
"""
from __future__ import annotations

import html
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
CHAPTERS, SRC = ROOT / "chapters", ROOT / "src"
TERMS_FILE = CHAPTERS / "terms.json"

# <dfn> 위치를 텍스트 흐름 안에 남기기 위한 표지. 일반 텍스트에 나올 수 없는 제어 문자를 쓴다.
DFN_OPEN, DFN_CLOSE = "\x01", "\x02"


@dataclass
class Segment:
    """텍스트 흐름의 한 조각. 위반 보고 시 '어느 장, 원고/코드 중 어디'인지 알려 주려고 둔다."""

    chapter: str      # 원고 파일명(예: 01-factory-method.html)
    where: str        # "원고" 또는 "코드 src/…"
    start: int        # 전체 흐름에서의 시작 오프셋
    text: str


def chapter_files() -> list[Path]:
    """읽기 순서대로 정렬된 원고 목록. 00 → 01…15 → 99 는 파일명 정렬과 같다."""
    return sorted(CHAPTERS.glob("[0-9][0-9]-*.html"))


def strip_markup(fragment: str) -> str:
    """원고 HTML 조각을 독자가 보는 텍스트로 바꾼다. <dfn>만 표지로 남긴다."""
    fragment = re.sub(r"<!--.*?-->", "", fragment, flags=re.S)            # 메타·저자 주석은 독자에게 안 보인다
    # 미리보기 영역은 '첫 등장'으로 치지 않는다. 학습 목표는 "이 장에서 X를 배운다"는 예고이고,
    # data-preview 를 붙인 블록(예: 서론의 패턴 지도)도 뒤에서 정의될 내용을 미리 훑는 자리다.
    fragment = re.sub(r'<section\s+id="goals".*?</section>', " ", fragment, flags=re.S)
    fragment = re.sub(r"<(section|table|div)\b[^>]*\bdata-preview\b[^>]*>.*?</\1>", " ", fragment, flags=re.S)
    fragment = re.sub(r'<dfn\b[^>]*data-term="([^"]+)"[^>]*>', lambda m: f"{DFN_OPEN}{m.group(1)}{DFN_CLOSE}", fragment)
    fragment = re.sub(r"<svg\b.*?</svg>", lambda m: " " + " ".join(re.findall(r">([^<]+)<", m.group(0))) + " ",
                      fragment, flags=re.S)                             # 다이어그램 안 글자도 독자가 읽는다
    fragment = re.sub(r"<[^>]+>", " ", fragment)
    # 태그 자리에 넣은 공백이 겹치면 "<code>@</code> 문법" 같은 표기가 "@  문법"이 되어 별칭과 안 맞는다.
    return re.sub(r"\s+", " ", html.unescape(fragment))


def build_stream() -> tuple[str, list[Segment]]:
    """책 전체를 읽기 순서의 단일 문자열로 만든다. 코드는 data-src 자리에 끼운다."""
    segments: list[Segment] = []
    pos = 0
    pre = re.compile(r'<pre\s+data-src="([^"]+)"(?:\s+data-lines="(\d+)-(\d+)")?\s*>\s*</pre>')
    for path in chapter_files():
        raw = path.read_text(encoding="utf-8")
        cursor = 0
        for m in pre.finditer(raw):
            # 코드 블록 앞의 원고 부분
            text = strip_markup(raw[cursor:m.start()])
            segments.append(Segment(path.name, "원고", pos, text)); pos += len(text)
            # 코드 블록: 학생은 주석까지 읽으므로 코드 전체를 흐름에 넣는다
            src = SRC / m.group(1)
            if src.exists():
                lines = src.read_text(encoding="utf-8").splitlines()
                if m.group(2):
                    lines = lines[int(m.group(2)) - 1:int(m.group(3))]
                code = " " + re.sub(r"\s+", " ", " ".join(lines)) + " "   # 원고와 같은 공백 규칙
                segments.append(Segment(path.name, f"코드 src/{m.group(1)}", pos, code)); pos += len(code)
            cursor = m.end()
        text = strip_markup(raw[cursor:])
        segments.append(Segment(path.name, "원고", pos, text)); pos += len(text)
    return "".join(s.text for s in segments), segments


def alias_pattern(alias: str) -> re.Pattern[str]:
    """별칭 검색 패턴. 영문/식별자는 단어 경계를 요구해 'hook'이 'webhook'에 걸리지 않게 한다.
    한글은 조사가 붙으므로('훅을', '훅이') 경계 없이 부분 문자열로 찾는다."""
    if re.fullmatch(r"[\x00-\x7f]+", alias):
        return re.compile(r"(?<![A-Za-z0-9_])" + re.escape(alias) + r"(?![A-Za-z0-9_])")
    return re.compile(re.escape(alias))


def locate(stream: str, segments: list[Segment], offset: int) -> str:
    """흐름 오프셋을 '장 · 원고/코드 · 앞뒤 문맥'으로 바꾼다."""
    seg = next(s for s in reversed(segments) if s.start <= offset)
    lo, hi = max(seg.start, offset - 40), min(seg.start + len(seg.text), offset + 40)
    ctx = re.sub(r"\s+", " ", stream[lo:hi]).replace(DFN_OPEN, "⟦").replace(DFN_CLOSE, "⟧")
    return f"{seg.chapter} · {seg.where} · …{ctx}…"


_MARKER = re.compile(DFN_OPEN + r"[^" + DFN_CLOSE + r"]*" + DFN_CLOSE)


def mask_markers(stream: str) -> str:
    """<dfn> 표지 안의 용어 id 텍스트를 같은 길이의 공백으로 지운다.

    표지는 "\x01dependency-injection\x02"처럼 하이픈으로 이어진 id를 그대로 담고 있어서,
    ASCII 별칭('injection' 같은)이 그 id 안의 부분 문자열에 걸려 '가짜 첫 등장'을 만든다.
    길이를 그대로 유지해야 locate()가 계산하는 오프셋이 어긋나지 않는다.
    """
    return _MARKER.sub(lambda m: " " * len(m.group(0)), stream)


def first_hit(stream: str, aliases: list[str]) -> int:
    """별칭 중 가장 먼저 나오는 위치. 없으면 -1. <dfn> 표지 내부의 id 텍스트는 검색에서 제외한다."""
    masked = mask_markers(stream)
    hits = [m.start() for a in aliases for m in [alias_pattern(a).search(masked)] if m]
    return min(hits) if hits else -1


def main(argv: list[str]) -> int:
    """명령행 진입점."""
    stream, segments = build_stream()
    if argv[:1] == ["--scan"]:
        for a in argv[1:]:
            p = first_hit(stream, [a])
            print(f"{a}: " + (locate(stream, segments, p) if p >= 0 else "등장하지 않음"))
        return 0

    terms = json.loads(TERMS_FILE.read_text(encoding="utf-8")) if TERMS_FILE.exists() else []
    only: set[str] = set()
    if argv[:1] == ["--chapter"]:
        only, argv = {a.zfill(2) for a in argv[1:]}, []

    def in_scope(*offsets: int) -> bool:
        """--chapter 필터: 주어진 오프셋 중 하나라도 대상 장에 있으면 검사한다."""
        if not only:
            return True
        return any(o >= 0 and locate(stream, segments, o)[:2] in only for o in offsets)
    ids = [t["id"] for t in terms]
    problems: list[str] = []
    dup = {i for i in ids if ids.count(i) > 1}
    if dup:
        problems.append(f"terms.json에 중복 id: {sorted(dup)}")

    # 원고의 <dfn>이 모두 등록된 용어인지 (오타 id는 용어집에서 사라진다)
    for d in set(re.findall(DFN_OPEN + r"([^" + DFN_CLOSE + r"]+)" + DFN_CLOSE, stream)) - set(ids):
        problems.append(f"<dfn data-term=\"{d}\"> 가 terms.json에 없음")

    for t in terms:
        aliases = t.get("aliases") or [t["term"]]
        marker = f"{DFN_OPEN}{t['id']}{DFN_CLOSE}"
        dfn_positions = [m.start() for m in re.finditer(re.escape(marker), stream)]
        first = first_hit(stream, aliases)
        if argv[:1] == ["--first"]:
            where = locate(stream, segments, first) if first >= 0 else "등장하지 않음"
            print(f"{t['id']:<28} {where}")
            continue
        if not in_scope(first, *dfn_positions):
            continue
        if len(dfn_positions) != 1:
            problems.append(f"[{t['id']}] <dfn data-term> 가 {len(dfn_positions)}개 (정확히 1개여야 함)"
                            + (f" — 첫 등장: {locate(stream, segments, first)}" if first >= 0 else ""))
            continue
        if first >= 0 and first < dfn_positions[0]:
            problems.append(f"[{t['id']}] 정의보다 먼저 등장\n      첫 등장: {locate(stream, segments, first)}"
                            f"\n      정의:    {locate(stream, segments, dfn_positions[0])}")
    if argv[:1] == ["--first"]:
        return 0
    for p in problems:
        print("FAIL", p)
    print(f"\n용어 {len(terms)}개 검사, 위반 {len(problems)}건")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
