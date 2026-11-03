#!/usr/bin/env python3
"""요약 판 장의 연습문제 절을 긴 버전(chapters/full/)의 것으로 그대로 바꿔 넣는다.

상황: 요약 판과 긴 버전은 연습문제가 같아야 한다(학생이 어느 판을 읽어도 같은 문제를 푼다).
사람이 복사하면 어긋나므로, 요약 원고에는 빈 `<section id="exercises"></section>` 자리만 두고
이 스크립트가 긴 버전의 `<section id="exercises">…</section>` 전체(제목·문제·해설·시작 코드)를
글자 하나 바꾸지 않고 옮긴다. 여러 번 돌려도 결과가 같다.

사용법:
    python3 sync_exercises.py 03        # 3장
    python3 sync_exercises.py all
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
EX = re.compile(r'<section\s+id="exercises"[^>]*>.*?</section>', re.S)


def sync(nn: str) -> int:
    """장 하나의 연습문제 절을 동기화한다. 문제가 있으면 1."""
    easy = sorted((ROOT / "chapters").glob(f"{nn}-*.html"))
    full = sorted((ROOT / "chapters" / "full").glob(f"{nn}-*.html"))
    if len(easy) != 1 or len(full) != 1:
        print(f"{nn}: 요약 판 {len(easy)}개, 긴 버전 {len(full)}개 — 건너뜀")
        return 1
    src = EX.search(full[0].read_text(encoding="utf-8"))
    text = easy[0].read_text(encoding="utf-8")
    if not src or not EX.search(text):
        print(f"{nn}: 연습문제 절이 없다(요약 판에는 빈 <section id=\"exercises\"></section> 자리가 필요)")
        return 1
    easy[0].write_text(EX.sub(lambda m: src.group(0), text, count=1), encoding="utf-8")
    print(f"{nn}: 연습문제 {src.group(0).count('class=\"exercise\"')}개 동기화")
    return 0


if __name__ == "__main__":
    args = sys.argv[1:]
    if args == ["all"]:
        args = sorted({p.name[:2] for p in (ROOT / "chapters" / "full").glob("*.html")})
    sys.exit(max((sync(a.zfill(2)) for a in args), default=2))
