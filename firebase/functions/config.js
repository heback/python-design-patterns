"use strict";
// 교사 판정 설정. 도메인을 바꾸면 firestore.rules의 isTeacher()도 같이 바꾼다.
module.exports = {
  TEACHER_DOMAIN: "ts.hs.kr",
  REGION: "asia-northeast3",
  MODEL: process.env.GEMINI_MODEL || "gemini-flash-latest",   // 운영 시 고정 ID로 바꾸는 것을 권장
  MAX_ITEMS: 40,
};
