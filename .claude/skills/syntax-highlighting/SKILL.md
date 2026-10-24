---
name: syntax-highlighting
description: 교재(textbook/)와 탐구 학습지(inquiry/)의 파이썬 코드에 문법 강조(신택스 하이라이팅)를 적용·유지하는 방법 — pyhl.js(공용 하이라이터), --tok-* 색 토큰, 편집기 오버레이, 예시 코드 팝업. 코드 색상 수정, 토큰 추가, 새 코드 표시 위치 추가, 다크 모드 코드 색 문제, 하이라이트가 안 보이거나 편집기 글자가 어긋나는 문제 요청 시 반드시 사용할 것.
---

# 파이썬 문법 강조

## 구성 (모두 `.claude/skills/html-textbook-publishing/assets/`)
| 파일 | 역할 |
|---|---|
| `pyhl.js` | 외부 라이브러리·네트워크 없는 파이썬 토크나이저. `PyHL.html(code)` → 색칠된 HTML, `PyHL.apply(root)` → `code.language-python` 일괄 색칠 |
| `pyrun.css` | `.token.*` 규칙과 편집기 오버레이(`.pr-stack`, `.pr-hl`) — 교재·학습지 공용 |
| `style.css` (교재) / `inquiry/templates/style.css` (학습지) | `--tok-*` 색 변수의 라이트/다크 값 |
| `pyrun.js` | 편집기(`mountEditor`)와 예시 팝업(`showExample`)이 PyHL을 호출 |

토큰 클래스 이름은 Prism과 같다(`keyword`, `string`, `triple-quoted-string`, `string-interpolation`, `comment`, `function`, `class-name`, `builtin`, `number`, `boolean`, `decorator`, `operator`, `punctuation`). Prism(CDN)은 쓰지 않는다.

## 적용 위치
1. **교재 정적 코드 블록** — `base.html`이 `pyhl.js`를 읽고 `PyHL.apply(document)`를 호출한다. 연습문제 시작 코드·해설 코드도 같은 `code.language-python`이다.
2. **편집기** — 글자를 투명하게 한 `textarea` 뒤에 색칠된 `pre.pr-hl`을 깔고 스크롤을 맞춘다. 입력·Tab·자동 들여쓰기·되돌리기·`setValue` 뒤에 `paint()`가 다시 칠한다.
3. **예시 코드 팝업** — `code.language-python`으로 만들어 `PyHL.apply`로 칠한다.
4. **탐구 학습지** — `inquiry/build.py`가 `pyhl.js`를 `/*@PYHL@*/` 자리에 인라인한다(student·teacher 템플릿). 학습지 코드는 모두 편집기·팝업을 거치므로 별도 작업이 없다.

## 지켜야 할 규칙
- **색은 `--tok-*` 변수로만** 정한다. 하드코딩하면 다크 모드(시스템 설정·수동 토글 두 경로)가 깨진다. 새 페이지에는 라이트/다크 두 벌의 `--tok-*`를 정의한다.
- **편집기 오버레이의 글꼴·크기·줄 높이·패딩·`tab-size`·`white-space`는 `pre.pr-hl`과 `textarea.pr-ta`가 같아야 한다.** 한쪽만 바꾸면 색칠된 글자와 커서가 어긋난다(`pyrun.css`의 묶음 규칙 하나로 관리).
- 새로 코드를 보여 주는 곳은 `<code class="language-python">`으로 마크업하고 `PyHL.apply(root)`를 부르거나, `PyRun.mountEditor`/`showExample`을 쓴다. 바깥에서 `innerHTML`로 직접 칠하지 않는다.
- `PyHL.html`은 태그를 벗기면 원문과 정확히 같아야 한다(왕복 무결성). 정규식을 고칠 때마다 검증한다.
- 산출물(`textbook/`, `docs/`, `inquiry/student.html`)은 직접 고치지 않는다. 자산을 고친 뒤 재빌드한다.

## 수정 후 검증
```bash
# 1) 왕복 무결성: src/ 모든 .py 를 칠한 뒤 태그를 벗겨 원문과 비교 (불일치 0이어야 함)
node -e '
const fs=require("fs");const H=new Function(fs.readFileSync(".claude/skills/html-textbook-publishing/assets/pyhl.js","utf8")+";return PyHL;")();
let bad=0;for(const f of fs.readdirSync("src",{recursive:true}).filter(f=>f.endsWith(".py"))){const c=fs.readFileSync("src/"+f,"utf8");
const o=H.html(c).replace(/<[^>]+>/g,"").replace(/&lt;/g,"<").replace(/&gt;/g,">").replace(/&amp;/g,"&");if(o!==c){bad++;console.log("BAD",f)}}console.log("mismatch",bad)'

# 2) 재빌드 (교재 → 학습지 → GitHub Pages용 docs/)
python3 .claude/skills/html-textbook-publishing/scripts/build_textbook.py
python3 inquiry/publish.py
```
3) 눈으로 확인: 코드 블록, 편집기(▶ 실행·편집), 💡 예시 코드 팝업을 라이트·다크 모드에서 본다. 헤드리스 Chrome은 `--screenshot`으로 로컬 `python3 -m http.server`의 작은 테스트 페이지를 찍으면 빠르다(`file://`은 막혀 있을 수 있음).
