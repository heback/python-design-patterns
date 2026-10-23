#!/usr/bin/env python3
"""탐구학습 자료 빌드: content/*.py + templates/ → student.html, teacher.html (+ sample/*.json).

학생용에는 정답·교사 메모·도달 목표 일반화가 들어가지 않는다(키를 빌드 때 제거).
사용: python3 inquiry/build.py
"""
import copy
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "content"))

import week1, week2, week3, week4, week5  # noqa: E401
from course import COURSE

WEEKS = [m.WEEK for m in (week1, week2, week3, week4, week5)]
TEACHER_ONLY_ITEM = {"answer", "note"}
PYRUN = ROOT.parent / ".claude" / "skills" / "html-textbook-publishing" / "assets"   # 교재와 공용인 파이썬 실행기
TEACHER_ONLY_STAGE = {"tnote"}
TEACHER_ONLY_WEEK = {"teacher", "target"}


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


def strip(weeks):
    out = copy.deepcopy(weeks)
    for w in out:
        for k in TEACHER_ONLY_WEEK:
            w.pop(k, None)
        for st in w["stages"]:
            for k in TEACHER_ONLY_STAGE:
                st.pop(k, None)
            for it in st["items"]:
                for k in TEACHER_ONLY_ITEM:
                    if k == "answer" and it["type"] == "code":
                        continue        # 코드 문항의 정답은 학생에게 '예시 코드' 팝업으로 보여 준다
                    it.pop(k, None)
    return out


def js(obj):
    """<script> 안에 안전하게 넣을 JSON."""
    return json.dumps(obj, ensure_ascii=False).replace("</", "<\\/").replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")


def render(tpl_name, content_js, app_js):
    t = ROOT / "templates"
    page = (t / tpl_name).read_text(encoding="utf-8")
    return (page.replace("/*@STYLE@*/", (t / "style.css").read_text(encoding="utf-8"))
                .replace("/*@PYRUN_CSS@*/", (PYRUN / "pyrun.css").read_text(encoding="utf-8"))
                .replace("/*@PYRUN@*/", (PYRUN / "pyrun.js").read_text(encoding="utf-8"))
                .replace("/*@CONTENT@*/", content_js)
                .replace("/*@CORE@*/", (t / "core.js").read_text(encoding="utf-8"))
                .replace("/*@APP@*/", (t / app_js).read_text(encoding="utf-8")))


def make_samples():
    """교사용 화면을 체험·시험할 수 있는 예시 학생 JSON 두 개."""
    out = ROOT / "sample"
    out.mkdir(exist_ok=True)

    def answers(through, flip=False):
        a = {}
        for w in WEEKS[:through]:
            for st in w["stages"]:
                for it in st["items"]:
                    ans, t = it.get("answer"), it["type"]
                    if t == "info":
                        continue
                    if ans is None and t != "scales":
                        continue
                    if t == "scales":
                        a[it["id"]] = [4 if not flip else 2] * len(it["items"])
                    elif t == "choice":
                        a[it["id"]] = {"sel": (ans["sel"] + (1 if flip else 0)) % len(it["options"]),
                                       "why": ans["why"] if not flip else "더 자연스러워 보여서요."}
                    elif t == "multi":
                        a[it["id"]] = {"sel": ans["sel"] if not flip else ans["sel"][:1] + [len(it["options"]) - 1], "why": ans["why"] if not flip else ""}
                    elif t == "sort":
                        a[it["id"]] = {k: (v if not (flip and int(k) % 3 == 0) else (v + 1) % len(it["buckets"])) for k, v in ans.items()}
                    elif t == "table":
                        a[it["id"]] = [row[:] for row in ans] if not flip else [[(c.split(".")[0][:24] if j == 0 else "") for j, c in enumerate(row)] for row in ans]
                    elif t == "list":
                        a[it["id"]] = ans[: (len(ans) if not flip else 2)]
                    elif t == "triples":
                        a[it["id"]] = [r[:] for r in ans] if not flip else [r[:] for r in ans[:2]]
                    elif t in ("text", "code"):
                        if flip and t == "code":
                            continue
                        a[it["id"]] = ans if not flip else ans.split(".")[0][:60] + "."
        return a

    samples = [("2-3", "17", "김하늘", answers(2, False)), ("2-3", "18", "박도윤", answers(3, True))]
    for klass, num, name, ans in samples:
        d = {"app": "dp-inquiry", "schema": 1, "student": {"klass": klass, "number": num, "name": name},
             "saved": "2026-10-21T05:00:00.000Z", "answers": ans, "feedback": {}}
        (out / f"{klass}_{num}_{name}_탐구학습.json").write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")


def main():
    errs = validate()
    if errs:
        print("콘텐츠 오류:\n  " + "\n  ".join(errs))
        sys.exit(1)
    student = render("student.html.tpl", "const CONTENT = " + js({"weeks": strip(WEEKS)}) + ";", "student.js")
    teacher = render("teacher.html.tpl", "const CONTENT = " + js({"weeks": WEEKS}) + ";\nconst COURSE = " + js(COURSE) + ";", "teacher.js")
    (ROOT / "student.html").write_text(student, encoding="utf-8")
    (ROOT / "teacher.html").write_text(teacher, encoding="utf-8")
    make_samples()
    n_items = sum(1 for w in WEEKS for st in w["stages"] for it in st["items"] if it["type"] != "info")
    print(f"완료: student.html({len(student)//1024}KB), teacher.html({len(teacher)//1024}KB) · 주차 {len(WEEKS)} · 응답 문항 {n_items}")


if __name__ == "__main__":
    main()
