# 탐구학습지 피드백 생성기 (Firebase + Gemini)

학생 제출 → Gemini 초안 → 교사 검수 → 공개. 교사 화면은 학교 Google 계정(@ts.hs.kr) 로그인이 필요하고, 제출 가능 여부는 교사 화면 [📮 제출 관리]에서 정한다(기본 닫힘). 접근 통제는 모두 서버(`firestore.rules`, `functions`)가 강제한다.

## 1회 설정 (사용자 작업)
1. Firebase 콘솔에서 프로젝트 생성 → 웹 앱 등록 → 설정값을 `inquiry/firebase-config.example.js`를 복사한 `inquiry/firebase-config.js`에 입력
2. Authentication: **익명**과 **Google** 로그인 사용. 설정 > 승인된 도메인에 호스팅 도메인 확인
3. Firestore 생성(`asia-northeast3`), 요금제 **Blaze**로 전환(Functions·Secret Manager 필요)
4. `cp firebase/.firebaserc.example firebase/.firebaserc` 후 프로젝트 ID 기입
5. `python3 inquiry/build.py` (정답이 든 `functions/teacher-content.json`, 로그인 게이트 교사 화면 `public/index.html` 생성)
6. `cd firebase && (cd functions && npm install) && firebase functions:secrets:set GEMINI_API_KEY`
7. `firebase deploy --only firestore:rules,functions,hosting`
8. (권장) Firestore에 `config/teachers` 문서 `{emails: ["본인@ts.hs.kr", ...]}` 생성 — 없으면 같은 도메인의 모든 계정(학생 포함)이 교사 권한을 갖는다.
9. 학생용 `inquiry/student.html`은 기존처럼 배포(`python3 inquiry/publish.py`)

## 모델·도메인
- 모델: 환경 변수 `GEMINI_MODEL`(기본 `gemini-flash-latest`). 운영 시 고정 ID를 권장.
- 교사 도메인은 `firestore.rules`의 `isTeacher()`, `functions/config.js`, `firebase-config.js`의 `TEACHER_DOMAIN`을 함께 바꾼다.

## 개인정보
Gemini에는 학생의 응답 텍스트와 교사용 기준만 보내고 학번·성명은 보내지 않는다. 다만 응답 본문에 개인정보를 쓰지 않도록 학생에게 안내한다.

## 테스트
```bash
cd firebase/functions && npm test                        # 프롬프트·검증 단위 테스트
cd firebase/test && npm install && cd .. && \
  firebase emulators:exec --only firestore --project demo-inquiry "npm --prefix test test"   # 규칙 테스트
```
로컬 시험: `firebase emulators:start --project demo-inquiry` 후 `http://localhost:5005/?emulator`(웹 config의 projectId를 `demo-inquiry`로).
