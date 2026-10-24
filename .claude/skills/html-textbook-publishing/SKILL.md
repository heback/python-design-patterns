---
name: html-textbook-publishing
description: 디자인패턴 교재를 HTML로 빌드·조립·디자인하는 방법 — build_textbook.py(원고+코드→textbook/), 공통 템플릿(base.html), 스타일(style.css, 라이트/다크, UML 다이어그램 클래스), 목차·내비게이션, 링크 검사. 교재 빌드, 재빌드, HTML 레이아웃/디자인/색상/폰트 수정, 목차 갱신, 다크 모드 문제 수정 요청 시 반드시 사용할 것.
---

# HTML 교재 빌드

## 빌드
```bash
python3 .claude/skills/html-textbook-publishing/scripts/build_textbook.py           # 전체
python3 .claude/skills/html-textbook-publishing/scripts/build_textbook.py --no-run  # 실행 생략, 레이아웃만 빠르게
```
`textbook/`은 매번 지우고 새로 만든다. **결과물을 직접 고치지 않는다** — 고칠 곳은 항상 원고(`chapters/`), 코드(`src/`), 또는 이 스킬의 `assets/`다.

## 스크립트가 하는 일
1. `chapters/{nn}-{slug}.html`의 `<!--meta title/subtitle/part-->`를 읽는다. `part`는 `생성 패턴`/`구조 패턴`/`행위 패턴` 중 하나이거나 비워 둔다(서론·종합).
2. `<pre data-src="경로" [data-lines="a-b"]></pre>` → 파일명 캡션 + 복사 버튼이 붙은 코드 블록.
3. `<pre data-run="경로"></pre>` → 실제로 실행한 stdout(캐시됨). 실패하면 stderr를 붙이고 PROBLEM으로 보고한다.
4. 모든 `<svg>`에 UML 마커 정의(`#triangle` 상속, `#arrow` 연관/의존, `#diamond` 집약, `#diamond-fill` 합성)를 주입한다.
5. `<section id><h2>`로 장 내부 목차(사이드바), 이전/다음 페이저, `index.html`(분류별 카드)을 만든다.
6. `<dfn data-term="id">`에 앵커(`#term-id`)와 툴팁(terms.json의 `short`)을 붙이고, `chapters/terms.json`으로 `glossary.html`(용어집)을 만든다. 상단 바와 index에 용어집 링크가 있다. 등록되지 않은 `<dfn>`이나 정의 위치가 없는 등록 용어는 PROBLEM이다.
7. 내부 링크·앵커를 검사한다. 문제가 있으면 종료 코드 1.

## 디자인 원칙
- 색은 `style.css`의 `:root` 토큰으로만 정의하고, 다크 모드는 `prefers-color-scheme`와 수동 토글(`data-theme`) 두 경로에서 같은 토큰을 바꾼다. 원고나 SVG에 색을 하드코딩하면 이 체계가 깨진다.
- 분류별 강조색: `--part-create`/`--part-struct`/`--part-behave`. `body[data-part]`로 자동 적용된다.
- 본문 폭 72ch, 코드 13.5px JetBrains Mono, 한글 Noto Sans KR + 제목 Noto Serif KR. 900px 이하에서는 사이드 목차를 숨긴다.
- 문법 강조는 자체 `pyhl.js`가 맡는다(Prism 미사용, 오프라인 동작). 토큰 색은 `--tok-*` 변수에만 묶는다. 자세한 규칙은 `syntax-highlighting` 스킬.
- 인쇄 시 해설(`details.solution`)을 펼치고 내비게이션을 숨긴다.

## 원고에서 쓸 수 있는 클래스
| 용도 | 마크업 |
|---|---|
| 코드 앞 맥락 문단 | `<p class="lead-in">` |
| 강조 상자 | `<div class="callout">`, `.callout.warn`(함정), `.callout.ok`(핵심 정리), 제목은 `<span class="label">` |
| UML | `.uml-class`(+`.highlight`), `.uml-name`, `.uml-abstract`, `.uml-stereo`, `.uml-member`, `.uml-assoc`, `.uml-inherit`, `.uml-impl`, `.uml-dep`, `.uml-compose`, `.uml-note`, `.uml-label` |
| 연습문제 | `.exercise`, `.ex-tag`, `details.solution` |
| 표 | 평범한 `<table>` (스크립트가 가로 스크롤 래퍼를 씌운다) |

## 빌드 후 확인
- PROBLEM 줄이 없어야 한다.
- `open textbook/index.html`로 열어 목차 → 장 → 다음 장 흐름, 다크 모드 토글, 좁은 창(모바일 폭)에서 코드 가로 스크롤만 생기고 페이지 전체는 흔들리지 않는지 본다.
