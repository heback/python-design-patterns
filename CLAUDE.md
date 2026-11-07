# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 프로젝트 개요

객체지향 원리를 이미 깊이 이해한 학생을 위한 **파이썬 디자인패턴 교재(HTML)**. 핵심 패턴 15개 + 서론/종합. 장마다 상황(맥락) → 순진한 코드 → 패턴 구조 → 주석이 풍부한 패턴 코드 → 파이썬다운 변형 → 트레이드오프 → 연습문제·해설 순서를 따른다.

## 구조의 핵심 (여러 파일을 봐야 알 수 있는 것)

- **원고와 코드는 분리되어 있고 빌드 때 합쳐진다.** `chapters/{nn}-{slug}.html`은 본문 조각이며 코드를 직접 담지 않는다. `<pre data-src="{nn}_{slug}/파일.py" data-title="역할 이름">`는 코드로 빌드 시 치환되고, 캡션에는 `data-title`만 나온다. 실행 결과는 싣지 않고 독자가 코드 블록의 [▶ 실행]으로 확인한다. **본문의 예제 코드와 연습문제 시작 코드는 모두 코드 편집기**(`textbook-code.js`가 `PyRun.mountEditor`로 만든다. 연습문제 해설 안의 코드만 읽기 전용)라서 학생이 주석(#)을 달거나 고칠 수 있고([# 주석] 버튼·Ctrl+/), 고친 내용은 입력하는 대로 자동 저장된다(이 브라우저의 localStorage `dp-code:`·`dp-ex:` + 호스팅 사본에서는 서버 `codeNotes`에도, 아래 '교재 코드 저장' 참고). 편집기의 [📌 오른쪽 고정]은 그 편집기를 화면 오른쪽 고정 창으로 올려 본문을 읽으면서 함께 보게 한다(하나만 고정, 좁은 화면에서는 아래쪽 창). 일부 행만 보이는 블록(`data-from`·`data-to`)은 고친 줄을 파일 전체의 같은 자리에 끼워 실행한다. 따라서 코드 수정은 `src/`에서만 하고, `data-lines` 범위가 밀리지 않았는지 확인한다.
- **각 장은 요약 판(기본)과 참고용 긴 버전 두 벌이다.** 학생이 읽는 기본은 `chapters/{nn}-{slug}.html`(요약 판, 글 약 2,500~3,500자·짧은 예제 `src/{nn}_{slug}/easy/e*.py`)이고, 예전의 긴 원고는 `chapters/full/{nn}-{slug}.html`(코드는 기존 `src/{nn}_{slug}/*.py`)로 남아 빌드 때 `{nn}-{slug}-full.html`이 된다. 요약 판 첫머리에 긴 버전 링크, 긴 버전 첫머리에 요약 판 링크가 빌드로 자동 삽입된다(원고에 직접 쓰지 않는다). **섹션 id는 두 판이 같고**(패턴 장 8개) 진도(절 id 집계)는 요약 판의 절 목록이 기준이며 긴 버전 페이지를 읽어도 같은 장으로 집계된다(`textbook-monitor.js`가 `-full`을 떼어 `SLUG`를 구한다). **연습문제 절은 요약 판에 직접 쓰지 않는다**: 요약 원고에 빈 `<section id="exercises"></section>`를 두고 `python3 .claude/skills/pattern-chapter-writing/scripts/sync_exercises.py {nn|all}`가 긴 버전 것을 글자 그대로 복사한다(연습문제를 고칠 때는 `chapters/full/`에서 고치고 다시 sync). 요약 판 본문은 연습문제가 쓰는 이름·용어를 같은 이름으로 가르쳐야 한다. 용어 정의 검사(`check_terms.py`)는 요약 판만 보고, 요약 판에 전혀 나오지 않는 용어는 용어집이 긴 버전의 정의로 잇는다. 학습지가 가리키는 교재 절(5주차 99장 사례 연구 등)은 요약 판에도 있어야 한다. 작성 지침은 `_workspace/20_easy_brief.md`.
- **절 제목 옆 [?] 아이콘(읽기 질문 팝업).** 01~15장의 상황·순진한 설계·구조·적용·파이썬다운 변형·트레이드오프 여섯 절에 "읽으며 생각할 질문"(쉬운 말, 절마다 3~4개)이 있다. 질문은 원고가 아니라 `chapters/focus-questions.json`(`{"nn-slug": {"절id": ["질문", ...]}}`)에 두고, 빌드가 요약 판·긴 버전 모두의 해당 절 `<h2>` 끝에 버튼을 넣는다(`inject_focus`). 팝업은 `assets/focus-questions.js`가 열고 ESC·팝업 밖 클릭·✕로 닫는다. 장을 고쳐 절의 내용이 바뀌면 질문도 함께 고치고, 빠진 절이 있으면 빌드가 PROBLEM으로 알린다. 질문은 요약 판 기준으로 썼으니 "데모 [n]" 같은 번호는 긴 버전과 어긋나지 않는지 확인한다.
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

**진도 자동 전달**: 교사가 `config/monitor`를 켠 동안(스위치는 함수 `setMonitor`로만 바꾸고 이력을 `monitorEvents`에 남기며, 꺼져 있으면 학생 화면에 중지 사실과 시각을 표시하고 서버 규칙이 쓰기를 거부) 학습지(`inquiry/templates/monitor.js`)와 호스팅된 교재 사본(`textbook-monitor.js`, `build.py`가 `firebase/public/textbook/` 각 장에만 주입하고 전체 장 목차 `index.html`도 만든다)이 완료 문항·읽은 절·활동 시간·마지막 활동 시각·화면을 보고 있는지(탭 가림·창 포커스, 벗어난 횟수·시간)만 `progress/{uid}`로 보내고(응답 본문 제외, 항상 고지 줄 표시), 교사 화면(왼쪽 메뉴: 환경설정·진도표·학생 질문·학생 코드·돌발퀴즈·AI 대화기록·AI 사용량·AI 질문한도, 한 번에 한 기능. 환경설정에 진도 수집·AI 도우미 스위치)이 교재 장별(분류: 생성·구조·행위) 읽기 진도 실시간 표를 보여 준다. 학생·교사 모두 학교 Google 계정(@ts.hs.kr)으로 로그인하며 **학번·성명은 받지 않는다**(진도 문서 ID = uid, 이름·이메일 = 계정). 교사는 `config/teachers` 허용 목록(필수, 없으면 아무도 교사가 아님)에 있는 이메일이다. **학생 AI 도우미**(`assistant.js`, 함수 `askAssistant`)는 교사가 `config/assistant`를 켠 동안만 보이고, 질문·사진·현재 화면 글을 Gemini로 보낸다(질문은 학생별·장별 기본 40번까지이고 교사가 [AI 질문한도]에서 기본값과 학생·장별 가감을 바꾼다. 모든 대화를 `chatLogs`에 기록하고(학생은 지우지 못한다, 교사 화면은 쪽 나누기) 토큰 사용량을 학생별·날짜별로 집계한다. 사진 파일은 저장하지 않고, 학생 화면에 기록된다는 사실을 항상 안내한다). 수집 항목을 늘리면 학생 고지 문구·`firestore.rules`의 `progressOk`·`firebase/README.md`를 함께 고친다.
**돌발퀴즈**(패턴별 서술형): 문항 은행은 `inquiry/content/popquiz_{create,struct,behave}.py`(패턴마다 6문항 `{id, kind(개념·상황·비교·코드읽기), minutes, q, key[채점 기준], model[모범 답안]}`, 학생에게는 `q`만 가고 `key`·`model`은 `teacher-content.json`의 `quiz`로만 교사·함수에 간다. `build.py`가 5문항 미만·파일 이름 노출 등을 검사). 교사 메뉴 [돌발퀴즈]는 **[문제 출제·제시]·[결과] 두 탭**이고(문항 목록은 [닫기]·패턴 버튼 재클릭으로 접힘, 진행 중 배너는 두 탭 위에 항상 보이며 제시하면 [결과] 탭으로 넘어감), [문제 출제·제시]에서 패턴·문항·제한 시간을 골라 [제시하기](함수 `startQuiz`)하면 `config/quiz`로 그 패턴 장(요약 판·긴 버전)을 보는 학생의 교재 사본에 팝업(`templates/quiz-ui.js`)이 뜨고, 학생은 제한 시간(서버 시각 `quizNow` 기준) 안에 서술형으로 답한다(시간이 끝나면 자동 제출, 함수 `submitQuiz`가 마감+10초까지만 받음). 마감 뒤 교사는 답안을 보고 [AI 채점](함수 `gradeQuizAnswer`, Gemini, 문항당 0~3점 + 기준별 충족 `hits` + 피드백 초안; **학생이 AI 선택 동의를 한 경우만**, 아니면 직접 채점)이나 직접 채점·수정(`saveQuizGrade`) 뒤 [학생에게 보내기](`releaseQuiz` → `quizResults/{sid}__{uid}`, 내 답·채점 기준별 충족·점수·피드백·총평 포함)로 점수·피드백을 팝업으로 보내고, 학생은 이후 각 패턴 장의 왼쪽 목차 [돌발퀴즈 피드백](팝업이 아니라 그 장 맨 아래 구역으로 이동)에서 언제든 다시 본다(`quiz-ui.js`, 예전 형식 결과는 함수 `quizResultDetail`로 내용을 채움). 기록은 `quizSessions/{sid}`(+`answers`·`grades`, 교사만 읽음). AI 채점 토큰은 [AI 사용량]에 `qz*` 필드로 합산된다. 자세한 규칙은 `firebase/README.md`.
**교재 코드 저장**: 호스팅된 교재 사본에서 학교 계정으로 로그인하고 현재 문구에 동의한 학생이 코드 편집기에서 주석을 달거나 고친 코드는 서버 `codeNotes/{uid}/blocks/{쪽__c|e번호}`(고친 코드 전체 `code`와 원본과 다른 줄 `added`)에도 자동 저장되어 다른 기기에서도 이어지고 교사 메뉴 [학생 코드]에서 보인다(`templates/code-sync.js`가 `DPCode.attach`로 저장 방법을 건네고, 로그인 때 `DPCode.pull`이 서버·로컬 중 나중에 고친 쪽을 택한다. 원본 코드가 바뀌어 해시 `h`가 다르면 옛 저장본은 무시). 학생은 자기 블록을 읽고 쓰고 지울 수 있고(처음 코드로 되돌리면 삭제) 교사는 모두 읽고 지운다(규칙·테스트). **이 항목은 동의 문구(2026-11-06판)의 필수 항목에 적혀 있다**: 수집 항목을 바꾸면 문구·`Consent.VERSION`·규칙 `consentVersion()`·`CONSENT_VERSION`·`firebase/README.md`를 함께 고친다. GitHub Pages 사본에는 서버가 없어 이 브라우저에만 저장된다.
**선생님께 질문**: 학생 화면(학습지·교재 사본) 오른쪽 아래의 아이콘 묶음(`fab-dock`)에서 AI 아이콘 바로 위에 [선생님께 질문] 아이콘이 있다(`templates/ask-teacher.js`, 입력란은 AI 도우미와 같은 `Assistant.composer`). 질문 개수 제한은 없고(함수가 1분에 10번까지만 받음), 학생별 대화 `askThreads/{uid}`(+`msgs`)를 함수 `askTeacher`·`replyToStudent`·`markAskRead`·`suggestReply`만 쓰고 화면은 실시간으로 읽는다. 새 질문은 교사 메뉴 [학생 질문]의 배지(`unread`)와 탭 제목 숫자로, 새 답변은 학생 아이콘 배지(`studentUnread`)로 알린다. 교사는 직접 답하거나 [AI 추천 답변](Gemini 초안, 보내기 전에는 학생에게 안 감)을 고쳐 보낼 수 있다. AI 추천은 학생이 개인정보 동의의 ‘AI 도우미 이용(선택)’에 동의한 경우에만 서버가 허용한다. 자세한 규칙은 `firebase/README.md`.

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
| 2026-11-03 | 교재 요약 판 도입: 장마다 짧고 쉬운 요약 판(기본)과 참고용 긴 버전(`chapters/full/`, `-full.html`) 두 벌, 연습문제는 sync_exercises.py로 동일 복사, 진도는 같은 절 id로 집계(긴 버전 읽기도 같은 장), 빌드가 서로 링크 삽입·용어집은 요약 판 우선 | chapters, chapters/full, src/*/easy, scripts/build_textbook.py·sync_exercises.py, check_terms.py, inquiry/templates/textbook-monitor.js, docs/index.html | 분량이 많아 학생이 힘들어함 |
| 2026-11-04 | AI 도우미 질문 한도를 하루 40번에서 학생별·장별 40번(기본값)으로 변경, 교사 [AI 질문한도] 메뉴(기본값·학생/장별 가감, 함수 setAssistantQuota·getAssistantQuota, chatQuota), 대화기록 쪽 나누기(서버 커서·필터 색인), 학생은 기록 삭제 불가를 규칙 테스트로 고정, 학생 대화창 [대화 지우기]를 [새 대화]로 | firebase/functions·firestore.rules·firestore.indexes.json, inquiry/templates(assistant.js·teacher.js·fb.js) | 비용 통제와 학생별 조정, 기록이 많아져도 볼 수 있게 |
| 2026-11-04 | 코드 실행기 stdout을 batched에서 write 핸들러로 바꿔 print(end=…) 출력 문제 수정 | assets/pyrun.js | end 옵션이 든 출력이 안 나옴 |
| 2026-11-04 | 팩토리 메서드 장의 몽키패치·globals·이음새 설명을 쉬운 말로 고침 | chapters/01-factory-method.html, chapters/full, terms.json, src/01_factory_method | 학생이 용어를 어려워함 |
| 2026-11-04 | 토큰 사용량을 기간(오늘·주간·월간·전체·직접 지정)별로 보기, 학생별 날짜별 집계(chatUsage.byDay) 추가 | inquiry/templates/teacher.js·style.css, firebase/functions/index.js | 기간별 사용량 파악 |
| 2026-11-06 | 절 제목 옆 [?] 아이콘: 클릭하면 그 절을 읽으며 생각할 질문을 팝업으로 표시(ESC·바깥 클릭·✕로 닫기). 01~15장 여섯 절 × 3~4개, 질문은 chapters/focus-questions.json, 서론에 사용법 안내 | assets/focus-questions.js·style.css·base.html, scripts/build_textbook.py, chapters/focus-questions.json, 00-intro | 읽을 때 무엇에 집중할지 학생이 잡도록 |
| 2026-11-06 | 학생 '선생님께 질문' 추가: AI 아이콘 위 아이콘(같은 입력 방식·글/사진, 개수 제한 없음), 교사 [학생 질문] 메뉴(새 질문 배지·직접 답변·AI 추천 답변), 대화 askThreads·함수 4개·규칙·테스트. 오른쪽 아래 아이콘을 묶음(fab-dock)으로 바꾸고 대화창은 묶음 왼쪽에 표시 | inquiry/templates/ask-teacher.js·assistant.js·fb.js·teacher.js, firebase/functions·firestore.rules·test | 학생이 선생님께 직접 질문하고 교사가 한곳에서 답하도록 |
| 2026-11-06 | 교사 메뉴 이름 변경: 대화기록→AI 대화기록, 토큰 사용량→AI 사용량, 질문 한도→AI 질문한도 | inquiry/templates/teacher.js | AI 도우미 관련 메뉴임을 구분 |
| 2026-11-06 | AI 추천 답변의 토큰·횟수를 [AI 사용량]에 합산(학생별 chatUsage·반 전체 stats/assistant의 sug* 필드, 추천 답변 열 추가) | firebase/functions/index.js, inquiry/templates/teacher.js | 추천 답변 비용도 사용량에 반영 |
| 2026-11-06 | 개인정보 동의의 ‘AI 도우미 이용(선택)’에 동의하지 않은 학생이 AI 도우미 창의 [AI 도우미 이용에 동의하기]로 나중에 직접 동의(false→true)할 수 있게 함. 철회(true→false)는 여전히 교사만 | firebase/firestore.rules·test, inquiry/templates/student-auth.js·assistant.js | 선택 항목을 거절한 학생의 재동의 요청 |
| 2026-11-06 | 교사 [진도표]: 학생 상태가 바뀌어 표가 다시 그려져도 가로·세로 스크롤 위치와 동의 현황 펼침 상태를 유지(전에는 표가 맨 왼쪽으로 돌아감). 좁은 화면에서 넓은 표가 페이지 전체를 넓히던 레이아웃(`.shell` 1fr)도 표 안 스크롤로 수정 | inquiry/templates/teacher.js·style.css | 진도를 확인하는 중에 계속 첫 열로 이동 |
| 2026-11-06 | 교재 코드를 모두 편집기로 표시(주석 달기 [# 주석]·Ctrl+/), 입력 즉시 자동 저장(localStorage + 호스팅 사본은 서버 codeNotes), [📌 오른쪽 고정] 고정 창, 교사 메뉴 [학생 코드]. 동의 문구를 2026-11-06판으로 올림(교재 코드 저장·선생님께 질문 항목 추가 → 학생은 다시 동의) | assets/pyrun.js·textbook-code.js·style.css·pyrun.css, build_textbook.py(data-from/to), inquiry/templates(code-sync.js·fb.js·teacher.js·student-auth.js), firebase/firestore.rules·functions/config.js·test | 학생이 코드에 주석을 달고 서버에 남기며, 읽으면서 코드를 곁에 고정 |
| 2026-11-07 | 교사 메뉴 [돌발퀴즈] 추가(패턴별 서술형 6문항×15패턴, 제시 → 학생 팝업·제한 시간 → 답안 조회 → AI 채점·직접 채점 → 학생에게 피드백). 예전에 삭제한 객관식 돌발 퀴즈와 다른 기능 | inquiry/content/popquiz_*.py·templates(quiz-ui.js·teacher-quiz.js·fb.js·teacher.js·mon-ui.css)·build.py, firebase/functions(quiz.js·quiz-model.js·index.js)·firestore.rules·test | 패턴별 핵심 개념 이해를 수업 중 확인 |
| 2026-11-07 | 학생 AI 대화(8명·42건, 서론·1장 중심)를 분석해 얻은 특징(막힘은 개념보다 예제의 파이썬 문법, 상황 이야기 없는 쉬운 개념 설명·우선순위·'왜 더 단순한 방법은 안 되나' 요구, 원칙↔패턴·4절↔5절 혼동, 출력 따라가기 어려움)을 전 장에 반영: 장마다 '처음이라면 이 그림부터'(일상 비유)·'이 장에서 무엇을 챙길까'(꼭/알면 좋은/처음엔 몰라도)·'왜 더 단순한 방법이면 안 될까'·'4절과 5절의 차이' callout, 낯선 문법(Callable·dataclass·데코레이터·yield 등) 읽는 법, 어려운 데모를 '한 줄씩 풀면'. 서론에 '원칙은 목표·패턴은 방법', '코드가 막히면 이렇게 읽는다', `//=` 추가, 용어집 callable 보강·floor-division 추가 | chapters/00~15(요약 판), chapters/terms.json, docs/textbook | 학생이 패턴을 어려워함 |
| 2026-11-07 | 돌발퀴즈 피드백 다시 보기: 각 패턴 장 왼쪽 목차에 [돌발퀴즈 피드백] 메뉴(좁은 화면은 상단 바), 교사 화면과 같은 내용(문제·내 답·채점 기준별 충족·점수·피드백·총평)을 언제든 열람. releaseQuiz 가 답안·채점 기준 충족 여부를 결과에 담음 | inquiry/templates/quiz-ui.js·mon-ui.css, firebase/functions/index.js | 팝업을 닫으면 피드백을 다시 볼 수 없었음 |
| 2026-11-07 | 돌발퀴즈 피드백 메뉴를 팝업이 아니라 각 패턴 장 맨 아래 구역(#qz-feedback)으로 바꾸고, 내 답·채점 기준별 충족·점수·피드백·총평이 모두 보이게 함(예전 형식으로 보낸 결과는 함수 quizResultDetail 로 채움) | inquiry/templates/quiz-ui.js·fb.js·mon-ui.css, firebase/functions/index.js | 메뉴가 팝업으로 뜨고 내용이 부실해 보였음 |
| 2026-11-07 | 교사 [돌발퀴즈] 화면을 [문제 출제·제시]·[결과] 탭으로 분리하고 문항 목록에 [닫기] 추가 | inquiry/templates/teacher-quiz.js·style.css | 문항을 연 뒤 닫을 수 없고 결과가 그 아래로 이어져 나왔음 |
