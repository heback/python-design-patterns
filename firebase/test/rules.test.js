"use strict";
// 실행: cd firebase && firebase emulators:exec --only firestore --project demo-inquiry "npm --prefix test test"
const test = require("node:test");
const assert = require("node:assert");
const fs = require("node:fs");
const path = require("node:path");
const { initializeTestEnvironment, assertSucceeds, assertFails } = require("@firebase/rules-unit-testing");
const { doc, setDoc, getDoc, getDocs, collection, deleteDoc, Timestamp } = require("firebase/firestore");

let env;
const T = { email: "teacher@ts.hs.kr", email_verified: true, firebase: { sign_in_provider: "google.com" } };
const teacher = () => env.authenticatedContext("t1", T).firestore();
const student = uid => env.authenticatedContext(uid, { firebase: { sign_in_provider: "anonymous" } }).firestore();
const settings = (over = {}) => env.withSecurityRulesDisabled(async c => { await setDoc(doc(c.firestore(), "config/submission"), Object.assign({ open: true, weeks: { 1: true, 2: false } }, over)); });
const head = (uid, extra = {}) => Object.assign({ student: { name: "홍" }, uid, updatedAt: Timestamp.now() }, extra);
const wk = (extra = {}) => Object.assign({ json: "{}", updatedAt: Timestamp.now() }, extra);

test.before(async () => {
  env = await initializeTestEnvironment({ projectId: "demo-inquiry", firestore: { rules: fs.readFileSync(path.join(__dirname, "../firestore.rules"), "utf8"), host: "127.0.0.1", port: 8080 } });
});
test.after(() => env.cleanup());
test.beforeEach(() => env.clearFirestore());

test("설정이 없으면 학생 제출 거부(기본 닫힘)", async () => {
  await assertFails(setDoc(doc(student("a"), "submissions/s1"), head("a")));
});
test("열린 주차만 제출 가능, 닫힌 주차는 거부", async () => {
  await settings();
  const db = student("a");
  await assertSucceeds(setDoc(doc(db, "submissions/s1"), head("a")));
  await assertSucceeds(setDoc(doc(db, "submissions/s1/weeks/1"), wk()));
  await assertFails(setDoc(doc(db, "submissions/s1/weeks/2"), wk()));
  await assertFails(setDoc(doc(db, "submissions/s1/weeks/9"), wk()));
});
test("전체 닫힘(open:false)이면 열린 주차 표시여도 거부", async () => {
  await settings({ open: false });
  await assertFails(setDoc(doc(student("a"), "submissions/s1"), head("a")));
});
test("마감·시작 시각 강제", async () => {
  await settings({ closesAt: Timestamp.fromMillis(Date.now() - 1000) });
  await assertFails(setDoc(doc(student("a"), "submissions/s1"), head("a")));
  await settings({ opensAt: Timestamp.fromMillis(Date.now() + 3600e3) });
  await assertFails(setDoc(doc(student("a"), "submissions/s1"), head("a")));
  await settings({ opensAt: Timestamp.fromMillis(Date.now() - 3600e3), closesAt: Timestamp.fromMillis(Date.now() + 3600e3) });
  await assertSucceeds(setDoc(doc(student("a"), "submissions/s1"), head("a")));
});
test("제출 코드 불일치 거부·일치 허용", async () => {
  await settings(); await env.withSecurityRulesDisabled(c => setDoc(doc(c.firestore(), "config/submissionSecret"), { code: "1234" }));
  const db = student("a");
  await assertFails(setDoc(doc(db, "submissions/s1"), head("a")));
  await assertFails(setDoc(doc(db, "submissions/s1"), head("a", { code: "0000" })));
  await assertSucceeds(setDoc(doc(db, "submissions/s1"), head("a", { code: "1234" })));
  await assertFails(setDoc(doc(db, "submissions/s1/weeks/1"), wk()));
  await assertSucceeds(setDoc(doc(db, "submissions/s1/weeks/1"), wk({ code: "1234" })));
});
test("다른 학생(uid)은 남의 제출 읽기·쓰기 불가, uid 위조 불가", async () => {
  await settings();
  await assertSucceeds(setDoc(doc(student("a"), "submissions/s1"), head("a")));
  await assertFails(setDoc(doc(student("b"), "submissions/s1"), head("b")));
  await assertFails(setDoc(doc(student("b"), "submissions/s1/weeks/1"), wk()));
  await assertFails(getDoc(doc(student("b"), "submissions/s1")));
  await assertFails(setDoc(doc(student("b"), "submissions/s2"), head("a")));
  await assertSucceeds(getDoc(doc(student("a"), "submissions/s1")));
});
test("학생은 목록 조회·초안 읽기·설정 쓰기·공개본 쓰기 불가, 본인 공개본 읽기는 가능", async () => {
  await settings();
  await env.withSecurityRulesDisabled(async c => { const d = c.firestore();
    await setDoc(doc(d, "submissions/s1"), head("a")); await setDoc(doc(d, "submissions/s1/drafts/w1-e1"), { comment: "초안", ai: true });
    await setDoc(doc(d, "submissions/s1/published/w1-e1"), { comment: "공개" }); });
  const a = student("a");
  await assertFails(getDocs(collection(a, "submissions")));
  await assertFails(getDoc(doc(a, "submissions/s1/drafts/w1-e1")));
  await assertSucceeds(getDoc(doc(a, "submissions/s1/published/w1-e1")));
  await assertSucceeds(getDocs(collection(a, "submissions/s1/published")));
  await assertFails(getDoc(doc(student("b"), "submissions/s1/published/w1-e1")));
  await assertFails(setDoc(doc(a, "submissions/s1/published/x"), { comment: "자작" }));
  await assertFails(setDoc(doc(a, "config/submission"), { open: true, weeks: { 1: true } }));
  await assertFails(getDoc(doc(a, "config/submissionSecret")));
  await assertSucceeds(getDoc(doc(a, "config/submission")));
});
test("학교 계정 교사는 모두 가능", async () => {
  const t = teacher();
  await assertSucceeds(setDoc(doc(t, "config/submission"), { open: true, weeks: { 1: true } }));
  await assertSucceeds(setDoc(doc(t, "submissions/s1/drafts/k"), { comment: "c", ai: true }));
  await assertSucceeds(getDocs(collection(t, "submissions")));
  await assertSucceeds(setDoc(doc(t, "submissions/s1/published/k"), { comment: "c" }));
  await assertSucceeds(deleteDoc(doc(t, "submissions/s1")));
});
test("외부 도메인·미인증 이메일·비 Google 로그인은 교사 불가", async () => {
  const mk = tok => env.authenticatedContext("x", tok).firestore();
  await assertFails(setDoc(doc(mk({ email: "x@gmail.com", email_verified: true, firebase: { sign_in_provider: "google.com" } }), "config/submission"), { open: true }));
  await assertFails(setDoc(doc(mk({ email: "t@ts.hs.kr", email_verified: false, firebase: { sign_in_provider: "google.com" } }), "config/submission"), { open: true }));
  await assertFails(setDoc(doc(mk({ email: "t@ts.hs.kr", email_verified: true, firebase: { sign_in_provider: "password" } }), "config/submission"), { open: true }));
  await assertFails(setDoc(doc(mk({ email: "t@evil.ts.hs.kr.com", email_verified: true, firebase: { sign_in_provider: "google.com" } }), "config/submission"), { open: true }));
  await assertFails(setDoc(doc(env.unauthenticatedContext().firestore(), "config/submission"), { open: true }));
});
test("허용 목록이 있으면 목록 밖 학교 계정은 거부", async () => {
  await env.withSecurityRulesDisabled(c => setDoc(doc(c.firestore(), "config/teachers"), { emails: ["other@ts.hs.kr"] }));
  await assertFails(setDoc(doc(teacher(), "config/submission"), { open: true, weeks: {} }));
  await env.withSecurityRulesDisabled(c => setDoc(doc(c.firestore(), "config/teachers"), { emails: ["teacher@ts.hs.kr"] }));
  await assertSucceeds(setDoc(doc(teacher(), "config/submission"), { open: true, weeks: {} }));
});

/* ---------- 진도 수집(progress) · 돌발 퀴즈(quizResponses) ---------- */
const monitor = (on = true) => env.withSecurityRulesDisabled(c => setDoc(doc(c.firestore(), "config/monitor"), { on }));
const prog = (uid, extra = {}) => Object.assign({ student: { name: "홍" }, uid, weeks: { 1: { n: 2, total: 9, ids: ["w1-e1"], last: "w1-e1" } }, activeMs: 1000, lastActiveAt: Timestamp.now(), updatedAt: Timestamp.now() }, extra);

test("진도: 수집 스위치가 없거나 꺼져 있으면 학생 쓰기 거부", async () => {
  await assertFails(setDoc(doc(student("a"), "progress/s1"), prog("a")));
  await monitor(false);
  await assertFails(setDoc(doc(student("a"), "progress/s1"), prog("a")));
});
test("진도: 켜져 있으면 본인 문서를 쓰고 고칠 수 있다(제출이 닫혀 있어도)", async () => {
  await monitor(true);
  const a = student("a");
  await assertSucceeds(setDoc(doc(a, "progress/s1"), prog("a")));
  await assertSucceeds(setDoc(doc(a, "progress/s1"), prog("a", { activeMs: 5000 })));
});
test("진도: 남의 문서·uid 위조·허용 밖 필드·타입 오류 거부", async () => {
  await monitor(true);
  await assertSucceeds(setDoc(doc(student("a"), "progress/s1"), prog("a")));
  await assertFails(setDoc(doc(student("b"), "progress/s1"), prog("b")));                   // 남의 문서 덮어쓰기
  await assertFails(setDoc(doc(student("b"), "progress/s2"), prog("a")));                   // uid 위조
  await assertFails(setDoc(doc(student("a"), "progress/s3"), prog("a", { answers: "본문" }))); // 응답 본문 같은 추가 필드
  await assertFails(setDoc(doc(student("a"), "progress/s4"), prog("a", { activeMs: "많이" })));
  await assertFails(setDoc(doc(student("a"), "progress/s5"), prog("a", { weeks: [1, 2] })));
});
test("진도: 교재 읽기 진도(chapters·where)도 쓸 수 있고, 형식이 틀리면 거부", async () => {
  await monitor(true);
  const a = student("a"), ch = { "10-strategy": { n: 3, total: 8, last: "naive" } };
  await assertSucceeds(setDoc(doc(a, "progress/s1"), prog("a", { chapters: ch, where: "교재 전략" })));
  await assertSucceeds(setDoc(doc(a, "progress/s2"), { student: { name: "홍" }, uid: "a", chapters: ch, activeMs: 10, lastActiveAt: Timestamp.now(), updatedAt: Timestamp.now() }));   // 학습지 없이 교재만
  await assertFails(setDoc(doc(a, "progress/s3"), prog("a", { chapters: "전부" })));
  await assertFails(setDoc(doc(a, "progress/s4"), prog("a", { where: 7 })));
  await assertFails(setDoc(doc(a, "progress/s5"), prog("a", { where: "가".repeat(81) })));
  await assertFails(setDoc(doc(student("b"), "progress/s1"), prog("b", { chapters: ch })));      // 남의 문서
});
test("진도: 읽기·삭제는 교사만, 학생은 본인 것도 읽지 못한다", async () => {
  await monitor(true);
  await assertSucceeds(setDoc(doc(student("a"), "progress/s1"), prog("a")));
  await assertFails(getDoc(doc(student("a"), "progress/s1")));
  await assertFails(getDocs(collection(student("a"), "progress")));
  await assertSucceeds(getDocs(collection(teacher(), "progress")));
  await assertFails(deleteDoc(doc(student("a"), "progress/s1")));
  await assertSucceeds(deleteDoc(doc(teacher(), "progress/s1")));
});
test("설정 문서(monitor·quiz): 누구나 읽고 교사만 쓴다", async () => {
  await assertFails(setDoc(doc(student("a"), "config/monitor"), { on: true }));
  await assertFails(setDoc(doc(student("a"), "config/quiz"), { liveId: "w1-q1" }));
  await assertSucceeds(setDoc(doc(teacher(), "config/monitor"), { on: true }));
  await assertSucceeds(setDoc(doc(teacher(), "config/quiz"), { liveId: "w1-q1", auto: { 1: true } }));
  await assertSucceeds(getDoc(doc(student("a"), "config/monitor")));
  await assertSucceeds(getDoc(doc(student("a"), "config/quiz")));
});
test("퀴즈 응답: 학생은 쓰기·읽기 모두 불가(정답·점수 위조 방지), 교사는 읽기·삭제 가능", async () => {
  await env.withSecurityRulesDisabled(c => setDoc(doc(c.firestore(), "quizResponses/w1-q1/answers/s1"), { correct: false, attempts: 1 }));
  await assertFails(setDoc(doc(student("a"), "quizResponses/w1-q1/answers/s1"), { correct: true, attempts: 1 }));
  await assertFails(getDoc(doc(student("a"), "quizResponses/w1-q1/answers/s1")));
  await assertSucceeds(getDocs(collection(teacher(), "quizResponses/w1-q1/answers")));
  await assertFails(setDoc(doc(teacher(), "quizResponses/w1-q1/answers/s1"), { correct: true }));   // 교사도 직접 쓰지 않는다(삭제만)
  await assertSucceeds(deleteDoc(doc(teacher(), "quizResponses/w1-q1/answers/s1")));
});
