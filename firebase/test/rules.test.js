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
