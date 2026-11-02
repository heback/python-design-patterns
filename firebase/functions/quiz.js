"use strict";
// 돌발 퀴즈 채점. Firestore·Firebase 없이 단위 테스트할 수 있도록 순수 함수로 분리했다.
const MAX_ATTEMPTS = 2;                       // 처음 시도 + 다시 생각해 보기 1회
const QUIZ_ID = /^(intro|create|struct|behave)-q\d{1,2}$/;       // {교재 분류}-q{번호}

/** teacher-content.json 의 quizzes(교재 분류별 묶음)에서 퀴즈를 찾는다. {group, quiz} 또는 null. */
function findQuiz(content, id) {
  if (typeof id !== "string" || !QUIZ_ID.test(id)) return null;
  for (const group of (content && content.quizzes) || []) {
    const quiz = (group.items || []).find(q => q.id === id);
    if (quiz) return { group, quiz };
  }
  return null;
}

/** 지금 이 퀴즈를 받을 수 있는가: 교사가 즉시 출제로 열었거나, 그 분류(생성·구조·행위·서론종합)의 자동 퀴즈가 켜져 있을 때. */
function isOpen(cfg, found) {
  cfg = cfg || {};
  return cfg.liveId === found.quiz.id || !!(cfg.auto && cfg.auto[found.group.key]);
}

/** 선택지 번호가 범위 안의 정수인가 */
const validChoice = (quiz, c) => Number.isInteger(c) && c >= 0 && c < quiz.options.length;

/**
 * 한 번의 응답을 반영한다. prev 는 이 학생의 기존 응답 문서(없으면 null).
 * 이미 맞혔거나 시도를 다 썼으면 상태를 바꾸지 않는다.
 * 반환: {state, result}. state 는 저장할 문서, result 는 학생에게 돌려줄 값이다.
 * 정답·풀이는 맞혔거나 마지막 시도를 마친 뒤에만 돌려준다.
 */
function applyAnswer(quiz, prev, choice, now) {
  const before = prev || { attempts: 0, choices: [], correct: false, firstCorrect: false };
  let state = before;
  if (!before.correct && before.attempts < MAX_ATTEMPTS) {
    const correct = choice === quiz.answer.sel;
    state = {
      attempts: before.attempts + 1, choices: [...before.choices, choice], correct,
      firstCorrect: before.attempts === 0 ? correct : before.firstCorrect, at: now,
    };
  }
  const done = state.correct || state.attempts >= MAX_ATTEMPTS;
  const result = { correct: state.correct, attempts: state.attempts, done };
  if (done) { result.answer = quiz.answer.sel; result.explain = quiz.explain; }
  return { state, result };
}

module.exports = { MAX_ATTEMPTS, findQuiz, isOpen, validChoice, applyAnswer };
