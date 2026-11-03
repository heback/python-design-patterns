"use strict";
// 교사 판정 설정. 도메인을 바꾸면 firestore.rules의 isTeacher()도 같이 바꾼다.
module.exports = {
  TEACHER_DOMAIN: "ts.hs.kr",
  REGION: "asia-northeast3",
  MODEL: process.env.GEMINI_MODEL || "gemini-flash-latest",   // 운영 시 고정 ID로 바꾸는 것을 권장
  MAX_ITEMS: 40,
  // 학생 AI 도우미(askAssistant) 한도: 비용·남용 방지. 학생 한 명(uid)당 하루·1분 안의 질문 수.
  ASSISTANT_DAILY_LIMIT: 40,
  ASSISTANT_MINUTE_LIMIT: 6,
  ASSISTANT_MAX_TOKENS: 800,
};
