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
from quiz import QUIZ

WEEKS = [m.WEEK for m in (week1, week2, week3, week4, week5)]
for _w in WEEKS:
    _w["quiz"] = QUIZ.get(_w["n"], [])          # 돌발 퀴즈 풀(학생용 빌드에서는 정답·풀이를 제거한다)
TEACHER_ONLY_QUIZ = {"answer", "explain"}
TEACHER_ONLY_ITEM = {"answer", "note"}
FB_DIR = ROOT.parent / "firebase"
FB_CONFIG = ROOT / "firebase-config.js"      # 필수: 학생 제출·교사 로그인이 모두 Firebase 로 동작한다(gitignore)
PYRUN = ROOT.parent / ".claude" / "skills" / "html-textbook-publishing" / "assets"   # 교재와 공용인 파이썬 실행기
TEACHER_ONLY_STAGE = {"tnote"}
TEACHER_ONLY_WEEK = {"teacher", "target"}


def validate_quiz(seen, errs):
    """돌발 퀴즈: id 모양·중복, 선택지 개수, 정답 범위, 풀이 누락."""
    for w in WEEKS:
        for q in w["quiz"]:
            i = q["id"]
            if i in seen:
                errs.append(f"id 중복: {i}")
            seen.add(i)
            if not re.fullmatch(rf"w{w['n']}-q\d+", i):
                errs.append(f"{i}: 퀴즈 id 형식은 w{w['n']}-q번호")
            if not 2 <= len(q.get("options", [])) <= 5:
                errs.append(f"{i}: 선택지는 2~5개")
            elif not (isinstance(q.get("answer", {}).get("sel"), int) and 0 <= q["answer"]["sel"] < len(q["options"])):
                errs.append(f"{i}: 퀴즈 정답 범위 오류")
            for k in ("q", "explain", "concept"):
                if not q.get(k):
                    errs.append(f"{i}: {k} 누락")


def validate():
    """문항 id 중복, 정답의 모양, 선택지 범위를 검사한다."""
    seen, errs = set(), []
    validate_quiz(seen, errs)
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
        for q in w.get("quiz", []):
            for k in TEACHER_ONLY_QUIZ:
                q.pop(k, None)           # 퀴즈 채점은 서버(answerQuiz)가 한다
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
    return (page.replace("/*@STYLE@*/", (t / "style.css").read_text(encoding="utf-8"))
                .replace("/*@PYRUN_CSS@*/", (PYRUN / "pyrun.css").read_text(encoding="utf-8"))
                .replace("/*@PYHL@*/", (PYRUN / "pyhl.js").read_text(encoding="utf-8"))
                .replace("/*@PYRUN@*/", (PYRUN / "pyrun.js").read_text(encoding="utf-8"))
                .replace("/*@FB@*/", fb_snippet())
                .replace("/*@MONITOR@*/", (t / "monitor.js").read_text(encoding="utf-8") if tpl_name.startswith("student") else "")
                .replace("/*@CONTENT@*/", content_js)
                .replace("/*@CORE@*/", (t / "core.js").read_text(encoding="utf-8"))
                .replace("/*@APP@*/", (t / app_js).read_text(encoding="utf-8")))


def main():
    errs = validate()
    if errs:
        print("콘텐츠 오류:\n  " + "\n  ".join(errs))
        sys.exit(1)
    if not FB_CONFIG.exists():
        print("inquiry/firebase-config.js 가 없습니다. 학생 제출과 교사 로그인이 Firebase 로 동작하므로 필요합니다.\n"
              "  cp inquiry/firebase-config.example.js inquiry/firebase-config.js 후 값을 채우세요(firebase/README.md 1회 설정).")
        sys.exit(1)
    student = render("student.html.tpl", "const CONTENT = " + js({"weeks": strip(WEEKS)}) + ";", "student.js")
    # 호스팅되는 교사 화면에는 정답·교사 메모·운영 안내를 넣지 않는다. 로그인 후 getTeacherContent()가 내려준다.
    teacher = render("teacher.html.tpl", "let CONTENT = " + js({"weeks": strip(WEEKS, keep_code_answer=False)}) + ";\nconst GATED = true;", "teacher.js")
    (FB_DIR / "public").mkdir(parents=True, exist_ok=True)
    (FB_DIR / "public" / "index.html").write_text(teacher, encoding="utf-8")
    # 학생용도 같은 사이트의 /inquiry/ 에 둔다(교재 링크 ../textbook/ 가 열리도록 textbook도 복사). 교재가 빌드돼 있을 때만.
    (FB_DIR / "public" / "inquiry").mkdir(parents=True, exist_ok=True)
    (FB_DIR / "public" / "inquiry" / "index.html").write_text(student, encoding="utf-8")
    if (ROOT.parent / "textbook").exists():
        shutil.rmtree(FB_DIR / "public" / "textbook", ignore_errors=True)
        shutil.copytree(ROOT.parent / "textbook", FB_DIR / "public" / "textbook")
    (FB_DIR / "functions").mkdir(parents=True, exist_ok=True)
    (FB_DIR / "functions" / "teacher-content.json").write_text(json.dumps({"weeks": WEEKS}, ensure_ascii=False), encoding="utf-8")
    (ROOT / "student.html").write_text(student, encoding="utf-8")
    (ROOT / "teacher.html").write_text(teacher, encoding="utf-8")
    n_items = sum(1 for w in WEEKS for st in w["stages"] for it in st["items"] if it["type"] != "info")
    print(f"완료: student.html({len(student)//1024}KB), teacher.html({len(teacher)//1024}KB) · 주차 {len(WEEKS)} · 응답 문항 {n_items}")


if __name__ == "__main__":
    main()
