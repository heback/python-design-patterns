# 탐구학습 진도 서버 (Firebase)

> 현재 화면(학생·교사)은 진도 전달만 쓴다(돌발 퀴즈는 삭제했다). 아래 '제출 → Gemini 초안 → 교사 검수 → 공개' 기능의 서버 쪽(`submissions` 규칙, `generateFeedback` 함수)은 남아 있지만 화면에서는 쓰지 않는다.

## (보류) 피드백 생성기 (Firebase + Gemini)

학생 제출 → Gemini 초안 → 교사 검수 → 공개. 교사 화면은 학교 Google 계정(@ts.hs.kr) 로그인이 필요하고, 제출 가능 여부는 교사 화면 [📮 제출 관리]에서 정한다(기본 닫힘). 접근 통제는 모두 서버(`firestore.rules`, `functions`)가 강제한다.

## 1회 설정 (사용자 작업)
1. Firebase 콘솔에서 프로젝트 생성 → 웹 앱 등록 → 설정값을 `inquiry/firebase-config.example.js`를 복사한 `inquiry/firebase-config.js`에 입력
2. Authentication: **Google** 로그인 사용(학생·교사 모두 학교 Google 계정으로 로그인한다. 익명 로그인은 쓰지 않는다). 설정 > 승인된 도메인에 호스팅 도메인 확인
3. Firestore 생성(`asia-northeast3`), 요금제 **Blaze**로 전환(Functions·Secret Manager 필요)
4. `cp firebase/.firebaserc.example firebase/.firebaserc` 후 프로젝트 ID 기입
5. `python3 inquiry/build.py` (정답이 든 `functions/teacher-content.json`, 로그인 게이트 교사 화면 `public/index.html` 생성)
6. `cd firebase && (cd functions && npm install) && firebase functions:secrets:set GEMINI_API_KEY`
7. `firebase deploy --only firestore:rules,functions,hosting`
8. **(필수) 교사 허용 목록**: Firestore 콘솔에서 컬렉션 `config`, 문서 ID `teachers`, 필드 `emails`(배열)에 교사 이메일(`본인@ts.hs.kr` …)을 넣는다. 학생도 같은 도메인의 학교 계정이므로, 목록이 없거나 비어 있으면 **아무도 교사가 아니다**(규칙·함수 모두 닫힘). 규칙으로는 이 문서를 만들 수 없고(교사만 쓸 수 있으므로) 콘솔에서만 만든다. **배포하기 전에** 먼저 만들어 두지 않으면 교사 화면에 들어갈 수 없다.
9. 학생용 `inquiry/student.html`은 기존처럼 배포(`python3 inquiry/publish.py`)

## 진도 자동 전달
교사 화면(한 화면: 진도 수집 스위치·학생 진도 표)에서 쓴다. 배포는 `firebase deploy --only firestore:rules,functions,hosting`(먼저 `python3 inquiry/build.py`로 호스팅 파일을 새로 만든다).

- **로그인**: 학생은 학습지·교재 화면 위쪽 안내 줄에서 [로그인]을 눌러 학교 Google 계정(@ts.hs.kr)으로 로그인한다. 학습지와 교재 사본이 같은 주소라 한 번 로그인하면 둘 다 쓰고, 기기를 바꿔도 같은 계정으로 같은 진도 문서를 잇는다. **학번·성명은 받지 않는다.** 교사 표의 이름은 계정 이름(`displayName`, 없으면 이메일 앞부분)과 이메일이다.
- **진도 문서**: `progress/{uid}` — 문서 ID는 로그인한 학생의 uid여야 한다(규칙이 강제). 한 학생에 문서 하나이고 남의 문서를 선점할 수 없다. 교사가 [수집 시작](`config/monitor.on`)을 켜 둔 동안, 로그인한 학생의 화면이 아래를 보낸다. **쓴 글의 내용은 보내지 않고**(`hasOnly` 규칙으로 강제, 학습지 글은 학생 브라우저에만 남는다) 키 입력·화면·탭 전환도 수집하지 않는다. 켜져 있는 동안 학습지와 교재 화면 위쪽에 고지 줄이 항상 보이고, 학생이 끄는 스위치는 없다. 전달 항목은 `monitor.js`·`textbook-monitor.js`의 `updateBar`와 이 목록을 같게 유지한다.
  - **교재 읽기 진도**(`chapters`): 장별로 읽은 절 수·전체 절 수·마지막 절. 절이 화면 가운데 40% 띠에 2초 이상 머물면(화면이 보이고 최근 60초 안에 입력·스크롤이 있을 때) 읽은 것으로 센다.
  - **학습지 진도**(`weeks`): 주차별 완료 문항 수·ID·마지막 문항.
  - 공통: `student`(이름·이메일), `where`(지금 있는 곳, 예: `교재 전략`, `학습지 2주차`), 활동 시간, 마지막 활동 시각. 두 화면의 쓰기는 `merge`라서 서로의 필드를 덮어쓰지 않는다.
- **교재 사본에서만 집계된다**: 읽기 진도는 Firebase 호스팅에 올라간 교재 사본(`/textbook/…`, `build.py`가 각 장 페이지에 `textbook-monitor.js`·`fb.js`·`student-auth.js`를 넣고 전체 장 목차 `index.html`도 만든다)에서만 모은다. 학습지와 같은 주소여야 로그인 상태가 공유되기 때문이다. GitHub Pages의 교재(`docs/textbook`)는 그대로이며 집계되지 않는다.
- **멈춤 표시**: 마지막 활동 후 2분 미만 활동 중, 5분 미만 잠시 멈춤, 그 이상 멈춤(수업 중에만 의미가 있다).
- **쿼터 추정**: 학생 120명, 50분 수업에서 쓰기·읽기 각 6천 건 안팎(하트비트 60초). 무료 일일 한도 안이다.
- **개인정보**: 진도 문서에는 이름·이메일이 들어 있으므로 학교의 개인정보 방침에 맞게 수집 기간을 정하고, 수업 뒤에는 [진도 기록 삭제]로 지운다.
- **삭제한 기능(돌발 퀴즈)**: 문항 풀(`quiz.py`)·팝업·`answerQuiz` 함수·`config/quiz`·`quizResponses` 규칙을 지웠다. 서버에 이미 쌓인 `config/quiz`·`quizResponses` 문서는 남아 있으니 필요하면 콘솔에서 지운다.

## 모델·도메인
- 모델: 환경 변수 `GEMINI_MODEL`(기본 `gemini-flash-latest`). 운영 시 고정 ID를 권장.
- 교사 도메인은 `firestore.rules`의 `isTeacher()`, `functions/config.js`, `firebase-config.js`의 `TEACHER_DOMAIN`을 함께 바꾼다.

## 개인정보
Gemini에는 학생의 응답 텍스트와 교사용 기준만 보내고 학번·성명은 보내지 않는다. 다만 응답 본문에 개인정보를 쓰지 않도록 학생에게 안내한다.

## 테스트
```bash
cd firebase/functions && npm test                        # 프롬프트·검증·학교 계정 판정 단위 테스트
cd firebase/test && npm install && cd .. && \
  firebase emulators:exec --only firestore --project demo-inquiry "npm --prefix test test"   # 규칙 테스트
```
로컬 시험: `firebase emulators:start --project demo-inquiry` 후 `http://localhost:5005/?emulator`(웹 config의 projectId를 `demo-inquiry`로).
