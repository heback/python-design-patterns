#!/usr/bin/env python3
"""탐구학습 자료 빌드: content/*.py + templates/ → student.html, teacher.html (+ firebase/public, teacher-content.json).

학생용에는 정답·교사 메모·도달 목표 일반화가 들어가지 않는다(키를 빌드 때 제거).
사용: python3 inquiry/build.py
학생 응답은 Firebase 제출로만 받는다(학생 JSON 파일 방식은 없다). inquiry/firebase-config.js 가 없으면 빌드를 멈춘다.
"""
import copy
import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "content"))

import week1, week2, week3, week4, week5  # noqa: E401

WEEKS = [m.WEEK for m in (week1, week2, week3, week4, week5)]
PART_KEY = {"": "intro", "생성 패턴": "create", "구조 패턴": "struct", "행위 패턴": "behave"}   # 교재 chapters 의 part → 분류 키(진도 표의 분류 머리줄)
TEACHER_ONLY_ITEM = {"answer", "note"}
FB_DIR = ROOT.parent / "firebase"
FB_CONFIG = ROOT / "firebase-config.js"      # 필수: 학생 제출·교사 로그인이 모두 Firebase 로 동작한다(gitignore)
PYRUN = ROOT.parent / ".claude" / "skills" / "html-textbook-publishing" / "assets"   # 교재와 공용인 파이썬 실행기
TEACHER_ONLY_STAGE = {"tnote"}
TEACHER_ONLY_WEEK = {"teacher", "target"}
CHAPTERS_DIR = ROOT.parent / "chapters"
TEXTBOOK_DIR = ROOT.parent / "textbook"


def _unwrap(t):
    """머리말 값 전체가 같은 따옴표로 감싸여 있을 때만 그 따옴표를 벗긴다('…'는 부제의 일부일 수 있다)."""
    return t[1:-1] if len(t) > 1 and t[0] == t[-1] and t[0] in "'\"" else t


def load_chapters():
    """교재 원고(chapters/*.html)의 머리말(title·part)을 읽어 장 목록을 만든다. 서론·종합은 part 가 비어 있다."""
    out = []
    for f in sorted(CHAPTERS_DIR.glob("*.html")):
        head = f.read_text(encoding="utf-8").split("-->", 1)[0]
        meta = dict(re.findall(r"^(\w+):[ \t]*(.*)$", head, re.M))
        title = re.sub(r"\s*\(.*?\)\s*$", "", meta.get("title", f.stem)).split(":")[0].strip()    # 영문 병기와 ': 부제' 를 뗀다
        body = f.read_text(encoding="utf-8").split("-->", 1)[-1]
        sections = [{"id": m.group(1), "title": re.sub(r"<[^>]+>", "", m.group(2)).strip()}
                    for m in re.finditer(r'<section\s+id="([\w-]+)"[^>]*>\s*<h2[^>]*>(.*?)</h2>', body, re.S)]       # 교사 화면의 절별 체류 시간 표에 쓴다
        out.append({"slug": f.stem, "sections": sections, "title": title, "full": meta.get("title", f.stem), "subtitle": _unwrap(meta.get("subtitle", "").strip()),
                    "part": meta.get("part", "").strip(), "group": PART_KEY.get(meta.get("part", "").strip(), "intro")})
    return out


CHAPTERS = load_chapters()


def validate():
    """문항 id 중복, 정답의 모양, 선택지 범위를 검사한다."""
    seen, errs = set(), []
    for w in WEEKS:
        for st in w["stages"]:
            for it in st["items"]:
                i, t = it["id"], it["type"]
                if i in seen:
                    errs.append(f"id 중복: {i}")
                seen.add(i)
                if not i.startswith(f"w{w['n']}-"):
                    errs.append(f"{i}: 주차 접두사 불일치")
                a = it.get("answer")
                if t in ("choice", "multi"):
                    sels = a["sel"] if t == "multi" else [a["sel"]]
                    if any(not 0 <= s < len(it["options"]) for s in sels):
                        errs.append(f"{i}: 정답 선택지 범위 오류")
                elif t == "sort":
                    for k, v in a.items():
                        if not (0 <= int(k) < len(it["cards"]) and 0 <= v < len(it["buckets"])):
                            errs.append(f"{i}: sort 정답 범위 오류")
                    if len(a) != len(it["cards"]):
                        errs.append(f"{i}: sort 정답 개수 불일치")
                elif t == "table":
                    if len(a) != len(it["rows"]) or any(len(r) != len(it["cols"]) for r in a):
                        errs.append(f"{i}: table 정답 크기 불일치")
                elif t == "triples":
                    if any(len(r) != 3 for r in a):
                        errs.append(f"{i}: triples 정답 형식 오류")
                elif t in ("text", "code") and a is not None and not isinstance(a, str):
                    errs.append(f"{i}: {t} 정답은 문자열")
                elif t == "list" and a is not None and not isinstance(a, list):
                    errs.append(f"{i}: list 정답은 배열")
                if t not in ("info", "scales") and a is None and st["key"] != "reflect":
                    errs.append(f"{i}: 정답 누락")
                if t != "info" and "q" not in it:
                    errs.append(f"{i}: q 누락")
    return errs


def strip(weeks, keep_code_answer=True):
    out = copy.deepcopy(weeks)
    for w in out:
        for k in TEACHER_ONLY_WEEK:
            w.pop(k, None)
        for st in w["stages"]:
            for k in TEACHER_ONLY_STAGE:
                st.pop(k, None)
            for it in st["items"]:
                for k in TEACHER_ONLY_ITEM:
                    if k == "answer" and it["type"] == "code" and keep_code_answer:
                        continue        # 코드 문항의 정답은 학생에게 '예시 코드' 팝업으로 보여 준다
                    it.pop(k, None)
    return out


def js(obj):
    """<script> 안에 안전하게 넣을 JSON."""
    return json.dumps(obj, ensure_ascii=False).replace("</", "<\\/").replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")


def fb_snippet():
    """firebase-config.js + fb.js. 설정 파일이 없으면 빈 문자열."""
    if not FB_CONFIG.exists():
        return ""
    return FB_CONFIG.read_text(encoding="utf-8") + "\n" + (ROOT / "templates" / "fb.js").read_text(encoding="utf-8")


def render(tpl_name, content_js, app_js):
    t = ROOT / "templates"
    page = (t / tpl_name).read_text(encoding="utf-8")
    return (page.replace("/*@STYLE@*/", (t / "style.css").read_text(encoding="utf-8") + "\n" + (t / "mon-ui.css").read_text(encoding="utf-8") + "\n" + (t / "assistant.css").read_text(encoding="utf-8"))
                .replace("/*@PYRUN_CSS@*/", (PYRUN / "pyrun.css").read_text(encoding="utf-8"))
                .replace("/*@PYHL@*/", (PYRUN / "pyhl.js").read_text(encoding="utf-8"))
                .replace("/*@PYRUN@*/", (PYRUN / "pyrun.js").read_text(encoding="utf-8"))
                .replace("/*@FB@*/", fb_snippet())
                .replace("/*@MONITOR@*/", (t / "monitor.js").read_text(encoding="utf-8") if tpl_name.startswith("student") else "")
                .replace("/*@ASSISTANT@*/", (t / "assistant.js").read_text(encoding="utf-8") if tpl_name.startswith("student") else "")
                .replace("/*@ASKTEACHER@*/", (t / "ask-teacher.js").read_text(encoding="utf-8") if tpl_name.startswith("student") else "")
                .replace("/*@STUDENTAUTH@*/", (t / "student-auth.js").read_text(encoding="utf-8") if tpl_name.startswith("student") else "")
                .replace("/*@CONTENT@*/", content_js)
                .replace("/*@CORE@*/", (t / "core.js").read_text(encoding="utf-8"))
                .replace("/*@APP@*/", (t / app_js).read_text(encoding="utf-8")))


GF_ICONS = ('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
            '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@24,400,0..1,0&display=block">')


def render_textbook_index():
    """호스팅 교재 사본의 목차 페이지(전체 장을 분류별로). GitHub Pages 표지(docs/index.html)가 없는 사본의 첫 화면이다."""
    import html as H
    course = "객체지향프로그래밍.대구과학고등학교.2학기"
    groups = [("intro", "시작과 정리"), ("create", "생성 패턴"), ("struct", "구조 패턴"), ("behave", "행위 패턴")]
    secs = []
    for key, name in groups:
        items = "".join(
            f'<li><a href="{c["slug"]}.html"><b>{H.escape(c["full"])}</b>'
            + (f'<small>{H.escape(c["subtitle"])}</small>' if c["subtitle"] else "") + "</a></li>"
            for c in CHAPTERS if c["group"] == key)
        if items:
            secs.append(f'<section><h2>{name}</h2><ul class="toc-list">{items}</ul></section>')
    return f"""<!doctype html>
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>목차 — 파이썬 디자인 패턴 · {course}</title>
<link rel="stylesheet" href="assets/style.css">
<style>.toc-list{{list-style:none;margin:0;padding:0}}.toc-list li{{border-bottom:1px dashed var(--border)}}.toc-list a{{display:block;padding:10px 4px;text-decoration:none;color:var(--text)}}
.toc-list a:hover b{{color:var(--accent)}}.toc-list small{{display:block;color:var(--muted);font-size:.85em;line-height:1.5}}.toc-groups{{columns:2 320px;column-gap:40px}}.toc-groups section{{break-inside:avoid;margin-bottom:24px}}.toc-groups h2{{font-size:1.1em;margin:0 0 6px}}
.start{{display:inline-block;margin:6px 0 22px;padding:8px 18px;border-radius:8px;background:var(--accent);color:#fff;text-decoration:none;font-weight:700}}</style>
<script>try{{var t=localStorage.getItem("dp-theme");if(t)document.documentElement.dataset.theme=t;}}catch(e){{}}</script></head>
<body class="index"><header class="topbar"><a class="brand" href="index.html">파이썬 디자인 패턴</a><span class="course">{course}</span><span class="crumb">목차</span>
<a class="glossary-link" href="glossary.html">용어집</a></header>
<div class="layout"><main class="content"><header class="cover"><h1>파이썬으로 배우는 디자인 패턴</h1><p class="subtitle">객체지향 원리를 이미 아는 학생을 위한 교재입니다. 서론 → 생성 → 구조 → 행위 → 종합 순서로 읽습니다. 각 장은 핵심만 간추린 요약 판이 기본이고, 장 첫머리의 링크로 참고용 긴 버전을 볼 수 있습니다.</p></header>
<a class="start" href="00-intro.html">서론부터 읽기</a><div class="toc-groups">{"".join(secs)}</div></main></div></body></html>
"""


def inject_textbook_monitor(dest):
    """Firebase 호스팅에 올리는 교재 사본(각 장 페이지)에만 읽기 진도 모니터를 넣는다. GitHub Pages 의 docs/textbook 은 건드리지 않는다.
    학번·성명은 학습지와 같은 저장소를 쓰므로 학습지와 같은 주소(origin)의 사본이어야 한다."""
    t = ROOT / "templates"
    tail = ("<style>" + (t / "mon-ui.css").read_text(encoding="utf-8") + (t / "assistant.css").read_text(encoding="utf-8") + "</style>\n"
            "<script>" + FB_CONFIG.read_text(encoding="utf-8") + "</script>\n"
            "<script>" + (t / "fb.js").read_text(encoding="utf-8") + "</script>\n"
            "<script>" + (t / "core.js").read_text(encoding="utf-8") + "</script>\n"
            "<script>const TB_DATA = " + js({"chapters": CHAPTERS}) + ";</script>\n"
            "<script>" + (t / "student-auth.js").read_text(encoding="utf-8") + "</script>\n"
            "<script>" + (t / "assistant.js").read_text(encoding="utf-8") + "</script>\n"
            "<script>" + (t / "ask-teacher.js").read_text(encoding="utf-8") + "</script>\n"
            "<script>" + (t / "textbook-monitor.js").read_text(encoding="utf-8") + "</script>\n"
            "<script>" + (t / "code-sync.js").read_text(encoding="utf-8") + "</script>\n")
    n = 0
    (dest / "index.html").write_text(render_textbook_index(), encoding="utf-8")
    for f in sorted(dest.glob("[0-9][0-9]-*.html")) + [dest / "glossary.html"]:
        h = f.read_text(encoding="utf-8")
        if f.name == "glossary.html":
            f.write_text(h.replace("https://heback.github.io/python-design-patterns/", "index.html"), encoding="utf-8")
            continue
        if "</body>" not in h or "TB_DATA" in h:
            continue
        # 이 사본에서는 '파이썬 디자인 패턴' 로고가 GitHub Pages 표지가 아니라 이 사본의 목차로 간다(진도가 집계되는 곳에 머물도록)
        h = h.replace("https://heback.github.io/python-design-patterns/", "index.html")
        h = h.replace("</head>", GF_ICONS + "</head>", 1).replace("</body>", tail + "</body>", 1)
        f.write_text(h, encoding="utf-8"); n += 1
    return n


def main():
    errs = validate()
    if errs:
        print("콘텐츠 오류:\n  " + "\n  ".join(errs))
        sys.exit(1)
    if not FB_CONFIG.exists():
        print("inquiry/firebase-config.js 가 없습니다. 학생 제출과 교사 로그인이 Firebase 로 동작하므로 필요합니다.\n"
              "  cp inquiry/firebase-config.example.js inquiry/firebase-config.js 후 값을 채우세요(firebase/README.md 1회 설정).")
        sys.exit(1)
    student = render("student.html.tpl", "const CONTENT = " + js({"weeks": strip(WEEKS), "chapters": CHAPTERS}) + ";", "student.js")
    # 호스팅되는 교사 화면에는 정답·교사 메모·운영 안내를 넣지 않는다. 로그인 후 getTeacherContent()가 내려준다.
    teacher = render("teacher.html.tpl", "let CONTENT = " + js({"weeks": strip(WEEKS, keep_code_answer=False), "chapters": CHAPTERS}) + ";\nconst GATED = true;", "teacher.js")
    (FB_DIR / "public").mkdir(parents=True, exist_ok=True)
    (FB_DIR / "public" / "index.html").write_text(teacher, encoding="utf-8")
    # 학생용도 같은 사이트의 /inquiry/ 에 둔다(교재 링크 ../textbook/ 가 열리도록 textbook도 복사). 교재가 빌드돼 있을 때만.
    (FB_DIR / "public" / "inquiry").mkdir(parents=True, exist_ok=True)
    (FB_DIR / "public" / "inquiry" / "index.html").write_text(student, encoding="utf-8")
    if (ROOT.parent / "textbook").exists():
        shutil.rmtree(FB_DIR / "public" / "textbook", ignore_errors=True)
        shutil.copytree(ROOT.parent / "textbook", FB_DIR / "public" / "textbook")
        print(f"교재 사본 {inject_textbook_monitor(FB_DIR / 'public' / 'textbook')}개 장에 읽기 진도 모니터를 넣었다")
    (FB_DIR / "functions").mkdir(parents=True, exist_ok=True)
    (FB_DIR / "functions" / "teacher-content.json").write_text(json.dumps({"weeks": WEEKS, "chapters": CHAPTERS}, ensure_ascii=False), encoding="utf-8")
    (ROOT / "student.html").write_text(student, encoding="utf-8")
    (ROOT / "teacher.html").write_text(teacher, encoding="utf-8")
    n_items = sum(1 for w in WEEKS for st in w["stages"] for it in st["items"] if it["type"] != "info")
    print(f"완료: student.html({len(student)//1024}KB), teacher.html({len(teacher)//1024}KB) · 주차 {len(WEEKS)} · 응답 문항 {n_items}")


if __name__ == "__main__":
    main()
