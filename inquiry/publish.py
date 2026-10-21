#!/usr/bin/env python3
"""GitHub Pages용 docs/ 생성: 교재 + 학생용 탐구 학습지(+ 선택: 교사용).

사용: python3 inquiry/publish.py            # 학생에게 공개해도 되는 것만
      python3 inquiry/publish.py --with-teacher   # 교사용(정답 포함)까지 — 공개 저장소에서는 금지
Pages 설정: Settings → Pages → Deploy from a branch → main / docs
"""
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent
DOCS = REPO / "docs"

subprocess.run([sys.executable, str(ROOT / "build.py")], check=True)
if DOCS.exists():
    shutil.rmtree(DOCS)
(DOCS / "inquiry").mkdir(parents=True)
shutil.copytree(REPO / "textbook", DOCS / "textbook")          # 학생 화면의 '../textbook/…' 링크가 열리도록
shutil.copy(ROOT / "student.html", DOCS / "inquiry" / "index.html")
(DOCS / ".nojekyll").write_text("")
with_teacher = "--with-teacher" in sys.argv
if with_teacher:
    shutil.copy(ROOT / "teacher.html", DOCS / "inquiry" / "teacher.html")

links = '<li><a href="inquiry/">탐구 학습지 (학생용)</a> — 이름을 쓰고 풀이한 뒤 JSON 파일로 저장·제출</li>\n<li><a href="textbook/index.html">파이썬 디자인 패턴 교재</a></li>'
(DOCS / "index.html").write_text(f'''<!doctype html><html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>파이썬 디자인 패턴</title>
<style>body{{font:17px/1.8 -apple-system,"Apple SD Gothic Neo","Noto Sans KR",sans-serif;max-width:640px;margin:48px auto;padding:0 16px}}
@media(prefers-color-scheme:dark){{body{{background:#15171a;color:#e6e6e3}}a{{color:#8ab4e8}}}}</style></head>
<body><h1>파이썬 디자인 패턴</h1><ul>{links}</ul></body></html>''', encoding="utf-8")
print("docs/ 생성 완료", "(교사용 포함!)" if with_teacher else "(교사용 제외)")
