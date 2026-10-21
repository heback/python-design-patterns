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

sys.path.insert(0, str(ROOT))
import re
from build import WEEKS

def chapters():
    """chapters/*.html 머리말(title/subtitle/part)에서 목차를 읽는다."""
    rows = []
    for f in sorted((REPO / "chapters").glob("*.html")):
        t = f.read_text(encoding="utf-8")
        g = lambda k: (re.search(rf"^{k}: ?(.*)$", t, re.M) or [None, ""])[1].strip()
        rows.append((f.stem, g("title"), g("subtitle"), g("part")))
    return rows

week_cards = "\n".join(
    f'<a class="card wk" href="inquiry/#w{w["n"]}"><b>{w["n"]}주차 · {w["concept"]}</b><span>{w["title"].split(" — ")[0]}</span>'
    f'<small>{w["subtitle"]}</small></a>' for w in WEEKS)
groups, order = {}, []
for stem, title, sub, part in chapters():
    if stem in ("00-intro", "99-summary"):
        part = "시작과 정리"
    elif not part:
        part = "교재"
    if part not in groups:
        groups[part] = []; order.append(part)
    groups[part].append(f'<li><a href="textbook/{stem}.html"><b>{title}</b></a><small>{sub}</small></li>')
toc = "\n".join(f'<section><h3>{p}</h3><ul>{"".join(groups[p])}</ul></section>' for p in order)

(DOCS / "index.html").write_text(f'''<!doctype html><html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>파이썬 디자인 패턴</title>
<style>
:root{{--bg:#fbfaf7;--s:#fff;--s2:#f3f1ec;--t:#1f2328;--m:#656d76;--b:#dcd8cf;--a:#2c5d8f;--as:#e6eef7}}
@media(prefers-color-scheme:dark){{:root{{--bg:#15171a;--s:#1c1f23;--s2:#23272c;--t:#e6e6e3;--m:#9aa0a6;--b:#33383f;--a:#8ab4e8;--as:#1f2a37}}}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--t);font:16px/1.7 -apple-system,"Apple SD Gothic Neo","Noto Sans KR",sans-serif}}
a{{color:inherit;text-decoration:none}}main{{max-width:1000px;margin:0 auto;padding:40px 16px 80px}}
h1{{font-size:30px;margin:0 0 6px;letter-spacing:-.02em}}h2{{font-size:20px;margin:40px 0 4px}}h3{{font-size:14px;color:var(--a);margin:18px 0 4px}}
.lead{{color:var(--m);margin:0}}.cta{{display:flex;gap:12px;flex-wrap:wrap;margin:22px 0}}
.btn{{padding:12px 20px;border-radius:10px;border:1px solid var(--b);background:var(--s);font-weight:700}}
.btn.p{{background:var(--a);color:var(--bg);border-color:var(--a)}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:10px;margin-top:12px}}
.card{{display:flex;flex-direction:column;gap:2px;padding:14px;border:1px solid var(--b);border-radius:12px;background:var(--s)}}
.card:hover,.btn:hover{{border-color:var(--a)}}.card span{{font-size:14px}}.card small{{color:var(--m)}}
.steps{{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:10px;counter-reset:s;padding:0;list-style:none}}
.steps li{{counter-increment:s;background:var(--as);border-radius:12px;padding:12px 14px 12px 44px;position:relative;font-size:15px}}
.steps li:before{{content:counter(s);position:absolute;left:14px;top:12px;width:22px;height:22px;border-radius:50%;background:var(--a);color:var(--bg);text-align:center;font-size:13px;line-height:22px;font-weight:700}}
.toc{{columns:2 300px;gap:24px}}.toc section{{break-inside:avoid}}.toc ul{{list-style:none;margin:0;padding:0}}
.toc li{{padding:5px 0;border-bottom:1px dashed var(--b)}}.toc small{{display:block;color:var(--m);font-size:13px;line-height:1.4}}.toc a:hover b{{color:var(--a)}}
footer{{margin-top:48px;color:var(--m);font-size:13px}}
</style></head><body><main>
<h1>파이썬으로 배우는 디자인 패턴</h1>
<p class="lead">객체지향 원리를 이미 아는 학생을 위한 교재와, 5주 개념기반 탐구 학습지입니다.</p>
<div class="cta"><a class="btn p" href="inquiry/">🔍 탐구 학습지 시작하기</a><a class="btn" href="textbook/index.html">📘 교재 보기</a><a class="btn" href="textbook/glossary.html">용어집</a></div>

<h2>탐구 학습지 · 5주 과정</h2>
<p class="lead">주차를 누르면 해당 주차 학습지로 바로 들어갑니다.</p>
<div class="grid">{week_cards}</div>
<h3 style="margin-top:22px">학습지 사용 방법</h3>
<ol class="steps">
<li>학습지를 열고 학급·번호·이름을 입력한 뒤 풀이합니다.</li>
<li>쓰는 동안 이 브라우저에 임시 저장됩니다. 수업이 끝나면 <b>💾 저장</b>으로 JSON 파일을 내려받습니다.</li>
<li>JSON 파일을 선생님이 정한 방법으로 제출합니다.</li>
<li>다음 시간에는 <b>📂 불러오기</b>로 파일을 열어 이어서 풀고, 선생님 코멘트 파일도 같은 방법으로 봅니다.</li></ol>

<h2>교재 목차</h2>
<div class="toc">{toc}</div>
<footer>모든 예제 코드는 저장소의 <code>src/</code> 폴더에서 직접 실행할 수 있습니다. 답은 서버로 전송되지 않고 내 브라우저와 내 JSON 파일에만 저장됩니다.</footer>
</main></body></html>''', encoding="utf-8")
print("docs/ 생성 완료", "(교사용 포함!)" if with_teacher else "(교사용 제외)")
