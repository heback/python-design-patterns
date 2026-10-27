# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 프로젝트 개요

객체지향 원리를 이미 깊이 이해한 학생을 위한 **파이썬 디자인패턴 교재(HTML)**. 핵심 패턴 15개 + 서론/종합. 장마다 상황(맥락) → 순진한 코드 → 패턴 구조 → 주석이 풍부한 패턴 코드 → 파이썬다운 변형 → 트레이드오프 → 연습문제·해설 순서를 따른다.

## 구조의 핵심 (여러 파일을 봐야 알 수 있는 것)

- **원고와 코드는 분리되어 있고 빌드 때 합쳐진다.** `chapters/{nn}-{slug}.html`은 본문 조각이며 코드를 직접 담지 않는다. `<pre data-src="{nn}_{slug}/파일.py">`는 코드로, `<pre data-run="...">`는 실제 실행 출력으로 빌드 시 치환된다. 따라서 코드 수정은 `src/`에서만 하고, `data-lines` 범위가 밀리지 않았는지 확인한다.
- `textbook/`은 빌드 산출물이라 매번 삭제 후 재생성된다. 직접 수정하지 말고 `chapters/`, `src/`, `.claude/skills/html-textbook-publishing/assets/`를 고친다.
- 장 구조·섹션 id·주석 규칙은 `.claude/skills/pattern-chapter-writing/SKILL.md`, 검증 규칙은 `.claude/skills/code-verification/` 이 기준이다.
- `src/` 예제는 표준 라이브러리만 쓰고, 파일 간 import 없이 단독 실행된다.

## 탐구학습 자료 (`inquiry/`)

개념기반 탐구학습 5주 과정. `inquiry/content/week{1-5}.py`(문항·예시 정답·교사 메모)와 `templates/`를 `python3 inquiry/build.py`로 합쳐 `student.html`(정답 제거)과 `teacher.html`(가이드·JSON 불러와 코멘트)을 만든다. 산출물 HTML은 직접 수정하지 말고 content/templates를 고친다. `sample/`은 교사 화면 체험용 학생 JSON.

탐구학습지를 점검·개선할 때는 `inquiry-review` 스킬(개념기반 탐구수업 8개 렌즈)을 따르고, 수정 후 `inquiry-reviewer` 에이전트로 독립 재점검한다. 학생 화면의 `optional`(선택, 진행률 제외)·`recall`(앞서 쓴 글 표시)·`compare`(이전 척도 응답 표시) 문항 필드는 `inquiry/templates/`가 처리한다. 코드 실행·편집은 `.claude/skills/html-textbook-publishing/assets/pyrun.js`(교재·학습지 공용, Pyodide)가 맡는다.

### 피드백 생성기 (`firebase/`)

`inquiry/firebase-config.js`(gitignore, 예시는 `firebase-config.example.js`)가 있을 때만 `build.py`가 `templates/fb.js`를 합쳐 학생 [제출]·교사 [제출 관리/AI 초안/공개]를 켠다. 없으면 기존 JSON 방식 그대로다. 이 모드의 교사 화면은 학교 Google 계정 로그인 게이트이고 정답·교사 메모는 빌드물에 없다(로그인 후 `getTeacherContent` 함수가 내려줌). 접근·제출 가능 여부는 `firebase/firestore.rules`와 `firebase/functions`가 서버에서 강제하므로 클라이언트 검사만 고치지 말 것. 응답은 `submissions/{id}/weeks/{n}`에 JSON 문자열로 저장한다(중첩 배열 불가 + 주차별 규칙 때문). 규칙·함수 수정 후 `firebase/README.md`의 테스트를 돌린다.

## 명령

```bash
# 장 검증 (코드 실행, docstring/주석 비율 ≥30%, 섹션 순서, 맥락 선행, 참조 무결성, 연습문제)
python3 .claude/skills/code-verification/scripts/verify_chapter.py 03     # 한 장
python3 .claude/skills/code-verification/scripts/verify_chapter.py all    # 전체

# 예제 하나 실행
python3 src/03_builder/02_builder.py

# HTML 빌드 → textbook/  (--no-run: 실행 출력 생략, 빠른 레이아웃 확인)
python3 .claude/skills/html-textbook-publishing/scripts/build_textbook.py
open textbook/index.html
```

코드 문법 강조(신택스 하이라이팅)는 `.claude/skills/html-textbook-publishing/assets/pyhl.js`(공용, 외부 의존 없음)가 맡는다. 정적 코드 블록·편집기·예시 팝업·탐구 학습지 모두 적용되며, 수정 시 `syntax-highlighting` 스킬을 따른다.

## 하네스: 파이썬 디자인패턴 교재

**목표:** 커리큘럼 설계 → 장 병렬 집필 → 점진적 검증 → HTML 빌드로 교재를 제작·유지보수한다.

**트리거:** 교재 제작, 장 추가/수정/재집필, 연습문제 보강, 교재 검증, 재빌드 등 이 교재 관련 작업 요청 시 `textbook-orchestrator` 스킬을 사용하라. 단순 질문은 직접 응답 가능.

**변경 이력:**
| 날짜 | 변경 내용 | 대상 | 사유 |
|------|----------|------|------|
| 2026-10-08 | 초기 구성 | 전체 | - |
| 2026-10-08 | 동시 실행 2개 제한, 중단 시 SendMessage 재개, 검증 보고서 장별 즉시 기록, 사실 오류성 권장은 필수 취급 | skills/textbook-orchestrator | 초기 실행 중 사용량 한도 3회·검증자 정지 2회, 권장 항목에 사실 오류 다수 |
| 2026-10-24 | 코드 실행·편집(Pyodide)·예시 코드 팝업·내 코드 JSON 저장/불러오기 추가 | assets/pyrun.*, textbook-code.js, inquiry/templates | 학생이 웹페이지만으로 실습·제출하도록 |
| 2026-10-24 | 탐구학습지 점검·개선 하네스 추가(inquiry-review 스킬, inquiry-reviewer 에이전트), 일반화 수정본·논쟁 문항·주 간 연결 도입, 시간 100분 정렬, 리커트·개수 채우기 정리 | skills/inquiry-review, agents/inquiry-reviewer, inquiry/content | 사고력 중심 점검 요청: 논쟁 질문 미회수, 일반화 검증 루프 부재, 분량 과다 |
| 2026-10-25 | 파이썬 문법 강조 추가: Prism 대신 자체 pyhl.js, 편집기 오버레이·예시 팝업·학습지 적용, syntax-highlighting 스킬 | assets/pyhl.js, pyrun.*, inquiry/templates, skills/syntax-highlighting | 편집기·팝업·학습지 코드에 색이 없었음 |
| 2026-10-27 | Firebase 피드백 생성기 추가: 학생 제출, 교사 학교 계정 로그인 게이트, 제출 가능 설정, Gemini AI 초안→교사 검수→공개 | firebase/, inquiry/templates/fb.js, build.py | 교사의 수동 코멘트 부담 완화 |
