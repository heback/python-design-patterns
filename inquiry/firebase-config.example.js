// 이 파일을 firebase-config.js 로 복사해 Firebase 콘솔의 웹 앱 설정값을 채운 뒤 `python3 inquiry/build.py` 를 실행하세요.
// (웹 앱 config는 비밀이 아니지만, 접근 통제는 firestore.rules·functions가 맡습니다.)
window.FIREBASE_CONFIG = {
  apiKey: "...",
  authDomain: "프로젝트ID.firebaseapp.com",
  projectId: "프로젝트ID",
  appId: "..."
};
window.FIREBASE_REGION = "asia-northeast3";   // Functions 지역(firebase/functions/config.js의 REGION과 같아야 함)
window.TEACHER_DOMAIN = "ts.hs.kr";           // 교사 학교 계정 도메인(firestore.rules·functions/config.js와 같게)
