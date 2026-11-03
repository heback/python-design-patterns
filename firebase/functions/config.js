"use strict";
// 교사 판정 설정. 도메인을 바꾸면 firestore.rules의 isTeacher()도 같이 바꾼다.
module.exports = {
  TEACHER_DOMAIN: "ts.hs.kr",
  REGION: "asia-northeast3",
  MODEL: process.env.GEMINI_MODEL || "gemini-flash-latest",   // AI 코멘트 초안(generateFeedback)용. 운영 시 고정 ID로 바꾸는 것을 권장
  // 학생 AI 도우미(askAssistant)용: 가볍고 저렴한 Flash-Lite. -latest 는 Google 이 가리키는 최신 Flash-Lite 로 바뀌므로, 고정하려면 GEMINI_ASSISTANT_MODEL 에 모델 ID(예: gemini-3.5-flash-lite)를 지정한다.
  ASSISTANT_MODEL: process.env.GEMINI_ASSISTANT_MODEL || "gemini-flash-lite-latest",
  MAX_ITEMS: 40,
  // 학생 AI 도우미(askAssistant) 한도: 비용·남용 방지. 학생 한 명(uid)당 하루·1분 안의 질문 수.
  ASSISTANT_DAILY_LIMIT: 40,
  ASSISTANT_MINUTE_LIMIT: 6,
  ASSISTANT_MAX_TOKENS: 1500,
};
