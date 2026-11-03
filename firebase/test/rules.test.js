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
const student = uid => env.authenticatedContext(uid, { firebase: { sign_in_provider: "anonymous" } }).firestore();   // 옛 제출 기능용(익명)
const pupil = uid => env.authenticatedContext(uid, { email: `${uid}@ts.hs.kr`, email_verified: true, firebase: { sign_in_provider: "google.com" } }).firestore();   // 학생 = 학교 Google 계정
const settings = (over = {}) => env.withSecurityRulesDisabled(async c => { await setDoc(doc(c.firestore(), "config/submission"), Object.assign({ open: true, weeks: { 1: true, 2: false } }, over)); });
const head = (uid, extra = {}) => Object.assign({ student: { name: "홍" }, uid, updatedAt: Timestamp.now() }, extra);
const wk = (extra = {}) => Object.assign({ json: "{}", updatedAt: Timestamp.now() }, extra);

test.before(async () => {
  env = await initializeTestEnvironment({ projectId: "demo-inquiry", firestore: { rules: fs.readFileSync(path.join(__dirname, "../firestore.rules"), "utf8"), host: "127.0.0.1", port: 8080 } });
});
test.after(() => env.cleanup());
test.beforeEach(async () => {
  await env.clearFirestore();
  await env.withSecurityRulesDisabled(c => setDoc(doc(c.firestore(), "config/teachers"), { emails: [T.email] }));    // 교사 허용 목록(필수)
});

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
test("허용 목록이 다르면 목록 밖 학교 계정은 거부, 목록에 넣으면 허용", async () => {
  await env.withSecurityRulesDisabled(c => setDoc(doc(c.firestore(), "config/teachers"), { emails: ["other@ts.hs.kr"] }));
  await assertFails(setDoc(doc(teacher(), "config/submission"), { open: true, weeks: {} }));
  await env.withSecurityRulesDisabled(c => setDoc(doc(c.firestore(), "config/teachers"), { emails: ["teacher@ts.hs.kr"] }));
  await assertSucceeds(setDoc(doc(teacher(), "config/submission"), { open: true, weeks: {} }));
});
test("허용 목록이 없거나 비어 있으면 아무도 교사가 아니다(닫힘) — 학생과 같은 도메인이므로", async () => {
  await env.withSecurityRulesDisabled(c => deleteDoc(doc(c.firestore(), "config/teachers")));
  await assertFails(setDoc(doc(teacher(), "config/monitor"), { on: true }));
  await assertFails(getDocs(collection(teacher(), "progress")));
  await env.withSecurityRulesDisabled(c => setDoc(doc(c.firestore(), "config/teachers"), { emails: [] }));
  await assertFails(setDoc(doc(teacher(), "config/monitor"), { on: true }));
});


/* ---------- 진도 수집(progress) ---------- */
const monitor = (on = true) => env.withSecurityRulesDisabled(c => setDoc(doc(c.firestore(), "config/monitor"), { on }));
const prog = (uid, extra = {}) => Object.assign({ student: { name: "홍" }, uid, weeks: { 1: { n: 2, total: 9, ids: ["w1-e1"], last: "w1-e1" } }, activeMs: 1000, lastActiveAt: Timestamp.now(), updatedAt: Timestamp.now() }, extra);

test("진도: 수집 스위치가 없거나 꺼져 있으면 학생 쓰기 거부", async () => {
  await assertFails(setDoc(doc(pupil("a"), "progress/a"), prog("a")));
  await monitor(false);
  await assertFails(setDoc(doc(pupil("a"), "progress/a"), prog("a")));
});
test("진도: 켜져 있으면 본인 문서를 쓰고 고칠 수 있다(제출이 닫혀 있어도)", async () => {
  await monitor(true);
  const a = pupil("a");
  await assertSucceeds(setDoc(doc(a, "progress/a"), prog("a")));
  await assertSucceeds(setDoc(doc(a, "progress/a"), prog("a", { activeMs: 5000 })));
});
test("진도: 남의 문서·uid 위조·허용 밖 필드·타입 오류 거부", async () => {
  await monitor(true);
  await assertSucceeds(setDoc(doc(pupil("a"), "progress/a"), prog("a")));
  await assertFails(setDoc(doc(pupil("b"), "progress/a"), prog("b")));                   // 남의 문서 덮어쓰기
  await assertFails(setDoc(doc(pupil("b"), "progress/b"), prog("a")));                   // uid 위조
  await assertFails(setDoc(doc(pupil("a"), "progress/a"), prog("a", { answers: "본문" }))); // 응답 본문 같은 추가 필드
  await assertFails(setDoc(doc(pupil("a"), "progress/a"), prog("a", { activeMs: "많이" })));
  await assertFails(setDoc(doc(pupil("a"), "progress/a"), prog("a", { weeks: [1, 2] })));
});
test("진도: 교재 읽기 진도(chapters·where)도 쓸 수 있고, 형식이 틀리면 거부", async () => {
  await monitor(true);
  const a = pupil("a"), ch = { "10-strategy": { n: 3, total: 8, last: "naive" } };
  await assertSucceeds(setDoc(doc(a, "progress/a"), prog("a", { chapters: ch, where: "교재 전략" })));
  await assertSucceeds(setDoc(doc(a, "progress/a"), { student: { name: "홍" }, uid: "a", chapters: ch, activeMs: 10, lastActiveAt: Timestamp.now(), updatedAt: Timestamp.now() }));   // 학습지 없이 교재만
  await assertFails(setDoc(doc(a, "progress/s3"), prog("a", { chapters: "전부" })));
  await assertFails(setDoc(doc(a, "progress/s4"), prog("a", { where: 7 })));
  await assertFails(setDoc(doc(a, "progress/s5"), prog("a", { where: "가".repeat(81) })));
  await assertFails(setDoc(doc(pupil("b"), "progress/a"), prog("b", { chapters: ch })));      // 남의 문서
});
test("진도: 화면을 보고 있는지(view·viewAt·leaves·awayMs)를 쓸 수 있고, 값이 틀리면 거부", async () => {
  await monitor(true);
  const a = pupil("a"), ok = { view: "hidden", viewAt: Timestamp.now(), leaves: 3, awayMs: 45000 };
  await assertSucceeds(setDoc(doc(a, "progress/a"), prog("a", ok)));
  await assertSucceeds(setDoc(doc(a, "progress/a"), prog("a", Object.assign({}, ok, { view: "blur" }))));
  await assertSucceeds(setDoc(doc(a, "progress/a"), prog("a", Object.assign({}, ok, { view: "on" }))));
  await assertFails(setDoc(doc(a, "progress/a"), prog("a", Object.assign({}, ok, { view: "minimized" }))));         // 모르는 상태
  await assertFails(setDoc(doc(a, "progress/a"), prog("a", Object.assign({}, ok, { leaves: -1 }))));
  await assertFails(setDoc(doc(a, "progress/a"), prog("a", Object.assign({}, ok, { awayMs: "많이" }))));
  await assertFails(setDoc(doc(a, "progress/a"), prog("a", Object.assign({}, ok, { viewAt: 12345 }))));            // 시각 형식이 아님
  await assertFails(setDoc(doc(a, "progress/a"), prog("a", Object.assign({}, ok, { url: "https://x.com" }))));     // 어떤 주소·내용 필드도 허용하지 않는다
});
test("진도: 읽기·삭제는 교사만, 학생은 본인 것도 읽지 못한다", async () => {
  await monitor(true);
  await assertSucceeds(setDoc(doc(pupil("a"), "progress/a"), prog("a")));
  await assertFails(getDoc(doc(pupil("a"), "progress/a")));
  await assertFails(getDocs(collection(pupil("a"), "progress")));
  await assertSucceeds(getDocs(collection(teacher(), "progress")));
  await assertFails(deleteDoc(doc(pupil("a"), "progress/a")));
  await assertSucceeds(deleteDoc(doc(teacher(), "progress/a")));
});
test("설정 문서(monitor): 누구나 읽고 교사만 쓴다", async () => {
  await assertFails(setDoc(doc(pupil("a"), "config/monitor"), { on: true }));
  await assertSucceeds(setDoc(doc(teacher(), "config/monitor"), { on: true }));
  await assertSucceeds(getDoc(doc(pupil("a"), "config/monitor")));
});

test("학생(학교 계정, 허용 목록 밖)은 교사 권한이 없다: 진도 읽기·설정 쓰기 불가", async () => {
  await monitor(true);
  await assertSucceeds(setDoc(doc(pupil("a"), "progress/a"), prog("a")));
  await assertFails(getDocs(collection(pupil("a"), "progress")));
  await assertFails(setDoc(doc(pupil("a"), "config/monitor"), { on: false }));
  await assertFails(setDoc(doc(pupil("a"), "config/teachers"), { emails: ["a@ts.hs.kr"] }));      // 스스로 교사가 될 수 없다
});
test("진도: 익명 로그인·학교 밖 Google 계정은 쓸 수 없다", async () => {
  await monitor(true);
  await assertFails(setDoc(doc(student("a"), "progress/a"), prog("a")));                          // 익명
  const gmail = env.authenticatedContext("g", { email: "g@gmail.com", email_verified: true, firebase: { sign_in_provider: "google.com" } }).firestore();
  await assertFails(setDoc(doc(gmail, "progress/g"), prog("g")));
  const unverified = env.authenticatedContext("u", { email: "u@ts.hs.kr", email_verified: false, firebase: { sign_in_provider: "google.com" } }).firestore();
  await assertFails(setDoc(doc(unverified, "progress/u"), prog("u")));
});

test("진도: 문서 ID 는 본인 uid 여야 한다(다른 ID 로 만들거나 남의 ID 를 선점할 수 없다)", async () => {
  await monitor(true);
  await assertFails(setDoc(doc(pupil("a"), "progress/17_하늘"), prog("a")));          // 이름 같은 임의 ID 불가
  await assertFails(setDoc(doc(pupil("a"), "progress/b"), prog("a")));               // 남의 uid 로 된 ID 불가
  await assertFails(setDoc(doc(pupil("a"), "progress/b"), prog("b")));               // uid 위조도 불가
  await assertSucceeds(setDoc(doc(pupil("a"), "progress/a"), prog("a")));
});

test("AI 도우미 스위치(config/assistant): 누구나 읽고 교사만 쓴다. 사용량(chatUsage)은 클라이언트가 읽지도 쓰지도 못한다", async () => {
  await assertFails(setDoc(doc(pupil("a"), "config/assistant"), { on: true }));
  await assertSucceeds(setDoc(doc(teacher(), "config/assistant"), { on: true }));
  await assertSucceeds(getDoc(doc(pupil("a"), "config/assistant")));
  await env.withSecurityRulesDisabled(c => setDoc(doc(c.firestore(), "chatUsage/a"), { day: "2026-11-03", count: 1 }));
  await assertFails(getDoc(doc(pupil("a"), "chatUsage/a")));
  await assertFails(setDoc(doc(pupil("a"), "chatUsage/a"), { day: "2026-11-03", count: 0 }));       // 한도 초기화 불가
  await assertFails(getDoc(doc(teacher(), "chatUsage/a")));
});
