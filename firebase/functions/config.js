"use strict";
// 교사 판정 설정. 도메인을 바꾸면 firestore.rules의 isTeacher()도 같이 바꾼다.
module.exports = {
  TEACHER_DOMAIN: "ts.hs.kr",
  // 개인정보 수집·이용 동의 문구의 버전. firestore.rules 의 consentVersion(), templates/student-auth.js 의 Consent.VERSION 과 같아야 한다(테스트가 확인).
  CONSENT_VERSION: "2026-11-05",
  REGION: "asia-northeast3",
  MODEL: process.env.GEMINI_MODEL || "gemini-flash-latest",   // AI 코멘트 초안(generateFeedback)용. 운영 시 고정 ID로 바꾸는 것을 권장
  // 학생 AI 도우미(askAssistant)용: 가볍고 저렴한 Flash-Lite. -latest 는 Google 이 가리키는 최신 Flash-Lite 로 바뀌므로, 고정하려면 GEMINI_ASSISTANT_MODEL 에 모델 ID(예: gemini-3.5-flash-lite)를 지정한다.
  ASSISTANT_MODEL: process.env.GEMINI_ASSISTANT_MODEL || "gemini-flash-lite-latest",
  MAX_ITEMS: 40,
  // 학생 AI 도우미(askAssistant) 한도: 비용·남용 방지.
  //  - 장별 한도: 학생 한 명(uid)이 교재의 장(또는 학습지 주차) 하나에서 물을 수 있는 질문 수. 교사가 [AI 질문한도]에서 기본값(config/assistant.limit)과 학생·장별 가감을 바꾼다.
  //  - 분당 한도: 학생 한 명이 1분 안에 보낼 수 있는 질문 수.
  ASSISTANT_CHAPTER_LIMIT: 40,        // 기본 장별 한도(교사가 바꾸지 않았을 때)
  ASSISTANT_LIMIT_MAX: 1000,          // 기본 한도·학생별 가감의 절댓값 상한(잘못된 값 방지)
  ASSISTANT_MINUTE_LIMIT: 6,
  ASSISTANT_MAX_TOKENS: 1500,
};
