"use strict";
const test = require("node:test");
const assert = require("node:assert");
const { findQuiz, isOpen, validChoice, applyAnswer } = require("./quiz");

const quiz = { id: "create-q1", options: ["가", "나", "다"], answer: { sel: 1 }, explain: "풀이" };
const content = { quizzes: [{ key: "intro", name: "서론·종합", items: [] }, { key: "create", name: "생성 패턴", items: [quiz] }] };

test("findQuiz: 있는 id만 찾고 형식이 틀리면 null", () => {
  assert.equal(findQuiz(content, "create-q1").group.key, "create");
  assert.equal(findQuiz(content, "create-q9"), null);
  assert.equal(findQuiz(content, "w2-q1"), null);          // 옛 주차별 id 는 더 이상 없다
  assert.equal(findQuiz(content, "../create-q1"), null);
  assert.equal(findQuiz(content, 5), null);
  assert.equal(findQuiz(null, "create-q1"), null);
});

test("isOpen: 즉시 출제 id 또는 분류 자동 모드", () => {
  const f = findQuiz(content, "create-q1");
  assert.equal(isOpen(null, f), false);
  assert.equal(isOpen({ liveId: "struct-q1" }, f), false);
  assert.equal(isOpen({ liveId: "create-q1" }, f), true);
  assert.equal(isOpen({ auto: { create: true } }, f), true);
  assert.equal(isOpen({ auto: { struct: true } }, f), false);
});

test("validChoice: 범위 밖·소수·문자열 거부", () => {
  assert.ok(validChoice(quiz, 0) && validChoice(quiz, 2));
  assert.ok(!validChoice(quiz, 3) && !validChoice(quiz, -1) && !validChoice(quiz, 1.5) && !validChoice(quiz, "1"));
});

test("첫 시도 정답: 풀이와 정답을 돌려주고 firstCorrect", () => {
  const { state, result } = applyAnswer(quiz, null, 1, 100);
  assert.deepEqual(result, { correct: true, attempts: 1, done: true, answer: 1, explain: "풀이" });
  assert.equal(state.firstCorrect, true);
});

test("첫 시도 오답: 정답·풀이를 감추고 다시 시도하게 한다", () => {
  const { state, result } = applyAnswer(quiz, null, 0, 100);
  assert.deepEqual(result, { correct: false, attempts: 1, done: false });
  assert.equal(state.firstCorrect, false);
});

test("두 번째 시도 정답이어도 firstCorrect 는 false 로 남는다", () => {
  const a = applyAnswer(quiz, null, 0, 100).state;
  const { state, result } = applyAnswer(quiz, a, 1, 200);
  assert.equal(state.correct, true); assert.equal(state.firstCorrect, false); assert.equal(result.done, true);
  assert.deepEqual(state.choices, [0, 1]);
});

test("두 번 틀리면 정답을 공개하고 더 이상 바뀌지 않는다", () => {
  const a = applyAnswer(quiz, null, 0, 100).state;
  const b = applyAnswer(quiz, a, 2, 200);
  assert.equal(b.result.done, true); assert.equal(b.result.answer, 1); assert.equal(b.result.correct, false);
  const c = applyAnswer(quiz, b.state, 1, 300);          // 시도를 다 쓴 뒤의 응답은 무시
  assert.deepEqual(c.state, b.state);
  assert.equal(c.result.correct, false);
});

test("이미 맞힌 뒤의 응답은 무시한다", () => {
  const a = applyAnswer(quiz, null, 1, 100).state;
  const b = applyAnswer(quiz, a, 0, 200);
  assert.deepEqual(b.state, a); assert.equal(b.result.correct, true);
});

test("isSchoolAccount: 학교 도메인 Google 계정만(확인된 이메일, 익명·외부 도메인 거부)", () => {
  const { isSchoolAccount } = require("./index")._test;
  const tok = (email, provider = "google.com", verified = true) => ({ token: { email, email_verified: verified, firebase: { sign_in_provider: provider } } });
  assert.equal(isSchoolAccount(tok("a@ts.hs.kr")), true);
  assert.equal(isSchoolAccount(tok("A@TS.HS.KR")), true);
  assert.equal(isSchoolAccount(tok("a@gmail.com")), false);
  assert.equal(isSchoolAccount(tok("a@evil.ts.hs.kr.com")), false);
  assert.equal(isSchoolAccount(tok("a@ts.hs.kr", "anonymous")), false);
  assert.equal(isSchoolAccount(tok("a@ts.hs.kr", "google.com", false)), false);
  assert.equal(isSchoolAccount(null), false);
  assert.equal(isSchoolAccount({ token: { firebase: { sign_in_provider: "anonymous" } } }), false);
});
