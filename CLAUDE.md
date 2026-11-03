# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 프로젝트 개요

객체지향 원리를 이미 깊이 이해한 학생을 위한 **파이썬 디자인패턴 교재(HTML)**. 핵심 패턴 15개 + 서론/종합. 장마다 상황(맥락) → 순진한 코드 → 패턴 구조 → 주석이 풍부한 패턴 코드 → 파이썬다운 변형 → 트레이드오프 → 연습문제·해설 순서를 따른다.

## 구조의 핵심 (여러 파일을 봐야 알 수 있는 것)

- **원고와 코드는 분리되어 있고 빌드 때 합쳐진다.** `chapters/{nn}-{slug}.html`은 본문 조각이며 코드를 직접 담지 않는다. `<pre data-src="{nn}_{slug}/파일.py" data-title="역할 이름">`는 코드로 빌드 시 치환되고, 캡션에는 `data-title`만 나온다. 실행 결과는 싣지 않고 독자가 코드 블록의 [▶ 실행]으로 확인하며, 편집기는 연습문제 시작 코드에만 있다(교재는 내 코드를 저장하지 않는다). 따라서 코드 수정은 `src/`에서만 하고, `data-lines` 범위가 밀리지 않았는지 확인한다.
- `textbook/`은 빌드 산출물이라 매번 삭제 후 재생성된다. 직접 수정하지 말고 `chapters/`, `src/`, `.claude/skills/html-textbook-publishing/assets/`를 고친다.
- 장 구조·섹션 id·주석 규칙은 `.claude/skills/pattern-chapter-writing/SKILL.md`, 검증 규칙은 `.claude/skills/code-verification/` 이 기준이다.
- `src/` 예제는 표준 라이브러리만 쓰고, 파일 간 import 없이 단독 실행된다.
- **코드 폰트 합자는 항상 꺼 둔다.** JetBrains Mono의 합자가 `->`를 `→`로, `!=`를 `≠`로 그려 소스와 화면이 달라진다. `style.css`·`pyrun.css`·`inquiry/templates/style.css`의 `font-variant-ligatures: none !important` 규칙을 지우지 말고, 코드를 보여 주는 CSS를 새로 만들 때도 이 규칙이 적용되는지 확인한다. 소스의 `->`·비교 연산자는 ASCII 그대로 둔다(문자를 `→`·`≠`로 바꾸지 않는다). 이 규칙은 이미 반영되어 있으므로 코드 예제를 보여 줄 때마다 따로 언급하지 않는다.
- **학생에게 코드 저장소를 드러내지 않는다.** 학생은 `src/`나 파일 이름을 모른다. 코드는 화면의 코드 블록(▶ 실행)으로만 본다. 원고·코드 주석·SVG·캡션에 `01_naive.py`, `src/…`, "저장소에 있다", "파일 앞부분" 같은 말을 쓰지 않고 역할 이름(순진한 코드·패턴 코드·파이썬다운 변형 등)만 쓴다. 세부 규칙은 `pattern-chapter-writing` 스킬.
- **GitHub Pages는 `docs/`의 사본을 서비스한다.** `textbook/`만 고치면 배포 화면은 그대로다. 교재를 재빌드한 뒤 배포하려면 `rsync -a --delete textbook/ docs/textbook/`로 동기화한다(`docs/textbook/`은 `textbook/`의 순수 복사본이다). `docs/index.html`(표지, `https://heback.github.io/python-design-patterns/`)이 교재의 첫 화면이며 별도 파일이라 빌드가 건드리지 않는다. `textbook/index.html`(목차)은 만들지 않고 쓰지 않는다(Firebase 호스팅용 교재 사본에만 `build.py`가 `index.html` 목차를 만들어 넣는다). 교재의 상단 바 링크는 위 주소로 간다. 탐구 학습지(`inquiry/`)는 배포하지 않는다.

## 탐구학습 자료 (`inquiry/`)

개념기반 탐구학습 5주 과정. `inquiry/content/week{1-5}.py`(문항·예시 정답·교사 메모)와 `templates/`를 `python3 inquiry/build.py`로 합쳐 `student.html`(정답 제거)과 `teacher.html`(교사용 진도 화면)을 만든다. 산출물 HTML은 직접 수정하지 말고 content/templates를 고친다. **학생이 쓴 글은 서버로 받지 않는다.** JSON 저장·불러오기·내보내기도, 학생 [제출]·[코멘트 확인]도, 교사용 수업 가이드·예시 정답·응답 코멘트·제출 관리 화면도 없다(쓴 내용은 그 브라우저의 localStorage에만 저장). 서버로 가는 것은 진도와 퀴즈 응답뿐이다.

탐구학습지를 점검·개선할 때는 `inquiry-review` 스킬(개념기반 탐구수업 8개 렌즈)을 따르고, 수정 후 `inquiry-reviewer` 에이전트로 독립 재점검한다. 학생 화면의 `optional`(선택, 진행률 제외)·`recall`(앞서 쓴 글 표시)·`compare`(이전 척도 응답 표시) 문항 필드는 `inquiry/templates/`가 처리한다. 코드 실행·편집은 `.claude/skills/html-textbook-publishing/assets/pyrun.js`(교재·학습지 공용, Pyodide)가 맡는다.

### 진도 서버 (`firebase/`)

`inquiry/firebase-config.js`(gitignore, 예시는 `firebase-config.example.js`)가 필수다(없으면 `build.py`가 멈춘다). `build.py`가 `templates/fb.js`를 합쳐 진도 전달과 교사 로그인을 켠다. 교사 화면은 학교 Google 계정 로그인 게이트이고 정답·교사 메모는 빌드물에 없다(로그인 후 `getTeacherContent` 함수가 내려줌). 접근·제출 가능 여부는 `firebase/firestore.rules`와 `firebase/functions`가 서버에서 강제하므로 클라이언트 검사만 고치지 말 것. 응답은 `submissions/{id}/weeks/{n}`에 JSON 문자열로 저장한다(중첩 배열 불가 + 주차별 규칙 때문). 규칙·함수 수정 후 `firebase/README.md`의 테스트를 돌린다.

**진도 자동 전달**: 교사가 `config/monitor`를 켠 동안(스위치는 함수 `setMonitor`로만 바꾸고 이력을 `monitorEvents`에 남기며, 꺼져 있으면 학생 화면에 중지 사실과 시각을 표시하고 서버 규칙이 쓰기를 거부) 학습지(`inquiry/templates/monitor.js`)와 호스팅된 교재 사본(`textbook-monitor.js`, `build.py`가 `firebase/public/textbook/` 각 장에만 주입하고 전체 장 목차 `index.html`도 만든다)이 완료 문항·읽은 절·활동 시간·마지막 활동 시각·화면을 보고 있는지(탭 가림·창 포커스, 벗어난 횟수·시간)만 `progress/{uid}`로 보내고(응답 본문 제외, 항상 고지 줄 표시), 교사 화면(왼쪽 메뉴: 환경설정·진도표·대화기록·토큰 사용량, 한 번에 한 기능. 환경설정에 진도 수집·AI 도우미 스위치)이 교재 장별(분류: 생성·구조·행위) 읽기 진도 실시간 표를 보여 준다. 학생·교사 모두 학교 Google 계정(@ts.hs.kr)으로 로그인하며 **학번·성명은 받지 않는다**(진도 문서 ID = uid, 이름·이메일 = 계정). 교사는 `config/teachers` 허용 목록(필수, 없으면 아무도 교사가 아님)에 있는 이메일이다. **학생 AI 도우미**(`assistant.js`, 함수 `askAssistant`)는 교사가 `config/assistant`를 켠 동안만 보이고, 질문·사진·현재 화면 글을 Gemini로 보낸다(모든 대화를 `chatLogs`에 기록하고 토큰 사용량을 학생별·날짜별로 집계한다. 사진 파일은 저장하지 않고, 학생 화면에 기록된다는 사실을 항상 안내한다). 수집 항목을 늘리면 학생 고지 문구·`firestore.rules`의 `progressOk`·`firebase/README.md`를 함께 고친다.

## 명령

```bash
# 장 검증 (코드 실행, docstring/주석 비율 ≥30%, 섹션 순서, 맥락 선행, 참조 무결성, 연습문제)
python3 .claude/skills/code-verification/scripts/verify_chapter.py 03     # 한 장
python3 .claude/skills/code-verification/scripts/verify_chapter.py all    # 전체

# 예제 하나 실행
python3 src/03_builder/02_builder.py

# HTML 빌드 → textbook/
python3 .claude/skills/html-textbook-publishing/scripts/build_textbook.py
open textbook/00-intro.html
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
| 2026-10-30 | 교재: 연습문제 편집기에 행 번호·점선·Tab/Shift+Tab, 예제 코드는 실행 전용(미리 실린 출력 `data-run` 삭제), 내 코드 저장/불러오기 제거(평가 문제는 별도 제작 예정) | assets/pyrun.*, textbook-code.js, base.html, build_textbook.py, chapters | 편집이 필요 없는 코드는 실행만, 결과는 학생이 직접 확인 |
| 2026-10-27 | Firebase 피드백 생성기 추가: 학생 제출, 교사 학교 계정 로그인 게이트, 제출 가능 설정, Gemini AI 초안→교사 검수→공개 | firebase/, inquiry/templates/fb.js, build.py | 교사의 수동 코멘트 부담 완화 |
| 2026-11-03 | 진도 자동 전달(교사가 켠 동안, 학생 화면에 고지)·돌발 퀴즈(1문항 팝업, 서버 채점)·교사 진도 탭 추가. student.js의 `let SET` 선언을 boot 앞으로 옮겨 Firebase 모드에서 제출 버튼이 안 뜨던 오류 수정 | inquiry/templates/monitor.js·fb.js·teacher.js·student.js, inquiry/content/quiz.py, firebase/ | 수업 중 진도 파악 요청. 규칙·함수 테스트 추가 |
| 2026-11-03 | 학생 JSON 파일 방식 전면 제거(학생 저장·불러오기, 교사 JSON 불러오기·코멘트 내보내기, 예시 JSON 생성). Firebase 설정 없이는 빌드하지 않음 | inquiry/templates, build.py, content/course.py | 학생 파일을 받지 않고 서버 제출만 사용 |
| 2026-11-03 | 교사 수업 가이드·응답 코멘트·제출 관리 화면, 학생 [제출]·[코멘트 확인], course.py 제거. 서버 규칙·함수(제출·AI 초안)는 남겨 둠(미사용). 두 화면 제목을 '디자인 패턴 학습 관리'로, 학습활동 자료 디자인 시스템·Material Symbols 적용 | inquiry/templates, build.py | 학생 글은 서버로 받지 않고 진도·퀴즈만 관리 |
| 2026-11-03 | 교재가 주차가 아니라 생성·구조·행위 분류라는 점을 반영: 퀴즈를 교재 분류별(문항마다 교재 장)로 재구성·4문항 추가(19문항), 교재 사본에 읽기 진도·퀴즈 모니터 주입(textbook-monitor.js), 교사 진도 표를 교재 장별로, 퀴즈 팝업을 quiz-ui.js로 공용화, 규칙에 chapters·where 추가 | inquiry/content/quiz.py, inquiry/templates, build.py, firebase/ | 교재 구조에 맞춘 진도·퀴즈 관리 |
| 2026-11-03 | 학생 교재 상단 바·탭 제목·표지에 과목명 '객체지향프로그래밍.대구과학고등학교.2학기' 표시(build_textbook.py의 COURSE_LABEL) | scripts/build_textbook.py, assets/base.html·style.css, docs/index.html | 과목 구분 표시 |
| 2026-11-03 | 학생도 학교 Google 계정(@ts.hs.kr)으로 로그인(익명 로그인 폐지). 교사 판정을 config/teachers 허용 목록 필수(없으면 닫힘)로 변경 — 학생과 같은 도메인이므로. 학번·성명은 학생이 직접 입력 | firebase/firestore.rules·functions, inquiry/templates(quiz-ui.js의 StudentAuth, fb.js, monitor.js, textbook-monitor.js) | 익명 로그인 설정 오류(auth/admin-restricted-operation)와 기기·이름 도용 방지 |
| 2026-11-03 | 학번·성명 입력 폐지(로그인 계정으로만 식별, 진도 문서 ID = uid). 돌발 퀴즈 기능 전체 삭제(quiz.py·팝업·answerQuiz 함수·규칙·교사 퀴즈 패널), 학생 로그인 코드는 student-auth.js로 분리 | inquiry/templates, build.py, firebase/ | 학번·성명 입력 단계에서 진도가 보고되지 않던 문제 해소, 퀴즈 기능 불필요 |
| 2026-11-03 | 진도에 '이 화면을 보고 있는지'(탭 가림·창 포커스, 벗어난 횟수·시간) 추가, 학생 고지 문구·규칙·교사 표(화면 열) 반영. 교사 화면에 진도 읽기 오류를 지속 표시, 함수의 허용 목록 검사를 규칙과 일치시킴 | inquiry/templates(student-auth.js FocusTrack), firebase/firestore.rules·functions | 수업 중 이탈 파악 |
| 2026-11-03 | 학생 AI 도우미 추가: 학습지·교재 사본에 AI 아이콘(글·사진 질문, 현재 화면 맥락 참조, 글 답변), askAssistant 함수(Gemini), 교사 켜기/끄기(config/assistant)·학생별 하루/분당 한도 | inquiry/templates/assistant.js·assistant.css, firebase/functions/assistant.js, firestore.rules | 학생 질문에 바로 답변 |
| 2026-11-03 | 챕터별 체류 시간(장·절별 초, 서버 값과 비교해 줄어들지 않게) 기록·교사 표 숫자 클릭 세부 조회, AI 도우미 대화 전체 기록·토큰 집계(교사 화면)·크레딧 소진 안내, 대화 입력란 4줄·클립보드 이미지 붙여넣기(Ctrl+V, 붙여넣기 버튼, 끌어다 놓기) | inquiry/templates(textbook-monitor.js, assistant.js, teacher.js), firebase/functions·firestore.rules | 학습 체류 파악과 AI 사용 관리 |
| 2026-11-03 | 교사 화면을 왼쪽 메뉴(환경설정·진도표·대화기록·토큰 사용량) 방식으로 재구조화: 한 번에 한 기능만 표시(환경설정에 진도 수집·AI 도우미 스위치), 선택 화면을 주소 해시·브라우저에 기억, 메뉴에 상태 배지(수집 중 인원·AI 오류·기록 수), 좁은 화면은 위쪽 메뉴 | inquiry/templates/teacher.js·style.css·teacher.html.tpl | 한 화면에 모두 표시되던 교사 화면 정리 |
| 2026-11-03 | 진도 수집 중지 시 학생 화면에 중지 사실·시각을 항상 표시, 스위치를 서버 함수(setMonitor)로만 바꾸고 켜고 끈 이력(monitorEvents)을 서버 시각으로 기록(교사 직접 쓰기·이력 수정 불가), 교사 환경설정에 이력과 중지 이후 수신 0건 확인 | firebase/functions·firestore.rules, inquiry/templates | 수집 여부를 나중에 다투지 않도록 |

