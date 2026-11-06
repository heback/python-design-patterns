"use strict";
// 실행: cd firebase && firebase emulators:exec --only firestore --project demo-inquiry "npm --prefix test test"
const test = require("node:test");
const assert = require("node:assert");
const fs = require("node:fs");
const path = require("node:path");
const { initializeTestEnvironment, assertSucceeds, assertFails } = require("@firebase/rules-unit-testing");
const { doc, setDoc, updateDoc, getDoc, getDocs, collection, deleteDoc, writeBatch, query, where, Timestamp, serverTimestamp } = require("firebase/firestore");

let env;
const T = { email: "teacher@ts.hs.kr", email_verified: true, firebase: { sign_in_provider: "google.com" } };
const teacher = () => env.authenticatedContext("t1", T).firestore();
const student = uid => env.authenticatedContext(uid, { firebase: { sign_in_provider: "anonymous" } }).firestore();   // 옛 제출 기능용(익명)
const pupil = uid => env.authenticatedContext(uid, { email: `${uid}@ts.hs.kr`, email_verified: true, firebase: { sign_in_provider: "google.com" } }).firestore();   // 학생 = 학교 Google 계정
const settings = (over = {}) => env.withSecurityRulesDisabled(async c => { await setDoc(doc(c.firestore(), "config/submission"), Object.assign({ open: true, weeks: { 1: true, 2: false } }, over)); });
const head = (uid, extra = {}) => Object.assign({ student: { name: "홍" }, uid, updatedAt: Timestamp.now() }, extra);
const CONSENT_V = "2026-11-06";      // firestore.rules 의 consentVersion() 과 같아야 한다
const seedConsent = (uid, over = {}) => env.withSecurityRulesDisabled(c => setDoc(doc(c.firestore(), "consents/" + uid),
  Object.assign({ uid, student: { name: "홍", email: `${uid}@ts.hs.kr` }, version: CONSENT_V, ai: false, agreedAt: Timestamp.now() }, over)));
const wk = (extra = {}) => Object.assign({ json: "{}", updatedAt: Timestamp.now() }, extra);

test.before(async () => {
  env = await initializeTestEnvironment({ projectId: "demo-inquiry", firestore: { rules: fs.readFileSync(path.join(__dirname, "../firestore.rules"), "utf8"), host: "127.0.0.1", port: 8080 } });
});
test.after(() => env.cleanup());
test.beforeEach(async () => {
  await env.clearFirestore();
  await env.withSecurityRulesDisabled(c => setDoc(doc(c.firestore(), "config/teachers"), { emails: [T.email] }));    // 교사 허용 목록(필수)
  await Promise.all(["a", "b"].map(u => seedConsent(u)));       // 진도 시험의 학생 a·b 는 개인정보 동의를 마친 학생(동의 시험은 맨 아래에서 따로 한다)
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
test("진도: 학생은 본인 문서 한 건만 읽는다(목록·남의 문서·삭제는 불가), 교사는 목록·삭제", async () => {
  await monitor(true);
  await assertSucceeds(setDoc(doc(pupil("a"), "progress/a"), prog("a")));
  await assertSucceeds(getDoc(doc(pupil("a"), "progress/a")));                 // 본인 것(체류 시간을 서버 값과 비교하려고)
  await assertFails(getDoc(doc(pupil("b"), "progress/a")));                    // 남의 것
  await assertFails(getDocs(collection(pupil("a"), "progress")));
  await assertSucceeds(getDocs(collection(teacher(), "progress")));
  await assertFails(deleteDoc(doc(pupil("a"), "progress/a")));
  await assertSucceeds(deleteDoc(doc(teacher(), "progress/a")));
});
test("진도: 장별 체류 시간(sec)·절별 체류 시간(s)이 든 chapters 를 쓸 수 있다", async () => {
  await monitor(true);
  const s = Object.fromEntries(["goals", "context", "naive", "structure", "implementation", "pythonic", "tradeoffs", "exercises"].map((k, i) => [k, 30 + i]));
  const ch = Object.fromEntries(["01-factory-method", "10-strategy", "99-summary"].map(k => [k, { n: 8, total: 8, last: "exercises", sec: 612, s }]));
  await assertSucceeds(setDoc(doc(pupil("a"), "progress/a"), prog("a", { chapters: ch })));
  await assertSucceeds(setDoc(doc(pupil("a"), "progress/a"), { uid: "a", student: { name: "홍" }, activeMs: 1, updatedAt: Timestamp.now(), lastActiveAt: Timestamp.now(), chapters: { "10-strategy": { sec: 700 } } }, { merge: true }));   // 병합 쓰기
});
test("진도 수집 스위치(config/monitor): 누구나 읽지만 아무도 직접 쓰지 못한다(교사도). 변경 이력(monitorEvents)은 교사만 읽는다", async () => {
  await assertFails(setDoc(doc(pupil("a"), "config/monitor"), { on: true }));
  await assertFails(setDoc(doc(teacher(), "config/monitor"), { on: true }));            // 함수(setMonitor)로만 바꾼다
  await monitor(true);
  await assertSucceeds(getDoc(doc(pupil("a"), "config/monitor")));
  await assertFails(setDoc(doc(teacher(), "config/monitor"), { on: false }));
  await env.withSecurityRulesDisabled(c => setDoc(doc(c.firestore(), "monitorEvents/e1"), { on: true, by: "teacher@ts.hs.kr" }));
  await assertSucceeds(getDoc(doc(teacher(), "monitorEvents/e1")));
  await assertFails(getDoc(doc(pupil("a"), "monitorEvents/e1")));
  await assertFails(setDoc(doc(teacher(), "monitorEvents/e2"), { on: false }));          // 이력을 새로 쓰거나
  await assertFails(deleteDoc(doc(teacher(), "monitorEvents/e1")));                      // 지울 수도 없다
  await assertFails(setDoc(doc(teacher(), "monitorEvents/e1"), { on: false }));          // 고칠 수도 없다
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

test("AI 도우미: 스위치는 누구나 읽고 교사만 쓴다. 대화 기록·사용량·집계는 교사만 읽고 학생은 읽지도 쓰지도 못한다", async () => {
  await assertFails(setDoc(doc(pupil("a"), "config/assistant"), { on: true }));
  await assertSucceeds(setDoc(doc(teacher(), "config/assistant"), { on: true }));
  await assertSucceeds(getDoc(doc(pupil("a"), "config/assistant")));
  await env.withSecurityRulesDisabled(async c => { const d = c.firestore();
    await setDoc(doc(d, "chatUsage/a"), { day: "2026-11-03", count: 1, total_totalTokens: 500 });
    await setDoc(doc(d, "chatLogs/x1"), { uid: "a", question: "질문", reply: "답" });
    await setDoc(doc(d, "stats/assistant"), { totalTokens: 500 }); });
  for (const path of ["chatUsage/a", "chatLogs/x1", "stats/assistant"]) {
    await assertFails(getDoc(doc(pupil("a"), path)));                                  // 본인 기록도 학생은 못 읽는다
    await assertFails(setDoc(doc(pupil("a"), path), { total_totalTokens: 0, count: 0 }));      // 한도·집계를 지울 수 없다
    await assertSucceeds(getDoc(doc(teacher(), path)));
    await assertFails(setDoc(doc(teacher(), path), { x: 1 }));                          // 교사도 직접 쓰지 않는다(함수만)
  }
  await assertSucceeds(getDocs(collection(teacher(), "chatLogs")));
  await assertFails(getDocs(collection(pupil("a"), "chatLogs")));
  await assertFails(deleteDoc(doc(pupil("a"), "chatLogs/x1")));                        // 학생은 자기 대화 기록도 지울 수 없다
  await assertFails(deleteDoc(doc(pupil("b"), "chatLogs/x1")));                        // 남의 기록은 더더욱
  await assertFails(updateDoc(doc(pupil("a"), "chatLogs/x1"), { question: "" }));       // 고칠 수도 없다
  await assertFails(deleteDoc(doc(pupil("a"), "stats/assistant")));
  await assertSucceeds(deleteDoc(doc(teacher(), "chatLogs/x1")));                      // 교사는 기록을 지울 수 있다
  await assertFails(deleteDoc(doc(pupil("a"), "chatUsage/a")));
});

test("AI 도우미 질문 한도 가감(chatQuota): 교사만 읽고, 아무도 직접 쓰지 못한다(함수만). 학생은 자기 한도를 올리거나 지울 수 없다", async () => {
  await env.withSecurityRulesDisabled(async c => { await setDoc(doc(c.firestore(), "chatQuota/a"), { all: 10, chapters: { "05-singleton": -5 } }); });
  await assertFails(getDoc(doc(pupil("a"), "chatQuota/a")));
  await assertSucceeds(getDoc(doc(teacher(), "chatQuota/a")));
  await assertFails(setDoc(doc(pupil("a"), "chatQuota/a"), { all: 1000 }));
  await assertFails(updateDoc(doc(pupil("a"), "chatQuota/a"), { all: 1000 }));
  await assertFails(deleteDoc(doc(pupil("a"), "chatQuota/a")));
  await assertFails(setDoc(doc(teacher(), "chatQuota/a"), { all: 1000 }));
  await assertFails(deleteDoc(doc(teacher(), "chatQuota/a")));
});

test("선생님께 질문(askThreads): 학생은 본인 대화·메시지만 읽고, 아무도 직접 쓰지 못한다(함수만). 교사는 모두 읽고 지울 수 있다", async () => {
  await env.withSecurityRulesDisabled(async c => { const d = c.firestore();
    await setDoc(doc(d, "askThreads/a"), { uid: "a", unread: 1, studentUnread: 0, lastText: "질문" });
    await setDoc(doc(d, "askThreads/a/msgs/m1"), { from: "student", text: "질문", at: Timestamp.now() });
    await setDoc(doc(d, "askThreads/b"), { uid: "b", unread: 0 });
    await setDoc(doc(d, "askThreads/b/msgs/m1"), { from: "student", text: "b의 질문", at: Timestamp.now() }); });
  // 학생 a: 자기 것만 읽는다
  await assertSucceeds(getDoc(doc(pupil("a"), "askThreads/a")));
  await assertSucceeds(getDocs(collection(pupil("a"), "askThreads/a/msgs")));
  await assertFails(getDoc(doc(pupil("a"), "askThreads/b")));
  await assertFails(getDocs(collection(pupil("a"), "askThreads/b/msgs")));
  await assertFails(getDocs(collection(pupil("a"), "askThreads")));                         // 목록은 교사만
  // 아무도 직접 쓰지 못한다(안 읽음 수·답변 위조 불가)
  await assertFails(setDoc(doc(pupil("a"), "askThreads/a"), { uid: "a", unread: 0 }));
  await assertFails(updateDoc(doc(pupil("a"), "askThreads/a"), { studentUnread: 0 }));
  await assertFails(setDoc(doc(pupil("a"), "askThreads/a/msgs/m2"), { from: "teacher", text: "합격입니다" }));
  await assertFails(updateDoc(doc(pupil("a"), "askThreads/a/msgs/m1"), { text: "고침" }));
  await assertFails(setDoc(doc(teacher(), "askThreads/a/msgs/m2"), { from: "teacher", text: "교사도 직접은 못 씀" }));
  await assertFails(updateDoc(doc(teacher(), "askThreads/a"), { unread: 0 }));
  // 학생은 지울 수 없다. 로그인하지 않았거나 학교 계정이 아니면 읽지 못한다
  await assertFails(deleteDoc(doc(pupil("a"), "askThreads/a/msgs/m1")));
  await assertFails(deleteDoc(doc(pupil("a"), "askThreads/a")));
  await assertFails(getDoc(doc(env.unauthenticatedContext().firestore(), "askThreads/a")));
  await assertFails(getDoc(doc(env.authenticatedContext("a", { email: "a@gmail.com", email_verified: true, firebase: { sign_in_provider: "google.com" } }).firestore(), "askThreads/a")));
  // 교사: 모두 읽고 지운다
  await assertSucceeds(getDocs(collection(teacher(), "askThreads")));
  await assertSucceeds(getDocs(collection(teacher(), "askThreads/b/msgs")));
  await assertSucceeds(deleteDoc(doc(teacher(), "askThreads/a/msgs/m1")));
  await assertSucceeds(deleteDoc(doc(teacher(), "askThreads/a")));
});

/* ---------- 개인정보 수집·이용 동의(consents) ---------- */
const cdoc = (uid, extra = {}) => Object.assign({ uid, student: { name: "홍", email: `${uid}@ts.hs.kr` }, version: CONSENT_V, ai: true, agreedAt: serverTimestamp() }, extra);

test("동의: 동의가 없으면 진도를 서버에 쓸 수 없고, 동의하면 쓸 수 있다", async () => {
  await monitor(true);
  const c = pupil("c");
  await assertFails(setDoc(doc(c, "progress/c"), prog("c")));
  await assertSucceeds(setDoc(doc(c, "consents/c"), cdoc("c")));
  await assertSucceeds(setDoc(doc(c, "progress/c"), prog("c")));
});
test("동의: 옛 문구(버전)에 동의한 학생은 다시 동의하기 전까지 진도를 쓸 수 없다", async () => {
  await monitor(true); await seedConsent("c", { version: "2000-01-01" });
  await assertFails(setDoc(doc(pupil("c"), "progress/c"), prog("c")));
  await assertSucceeds(setDoc(doc(pupil("c"), "consents/c"), cdoc("c")));                 // 새 문구에 다시 동의(덮어쓰기)
  await assertSucceeds(setDoc(doc(pupil("c"), "progress/c"), prog("c")));
});
test("동의: 학생은 한번 한 동의를 스스로 지우거나(철회) 고칠 수 없고, 교사가 초기화하면 진도 쓰기가 다시 막힌다", async () => {
  await monitor(true);
  const a = pupil("a");
  await assertSucceeds(setDoc(doc(a, "progress/a"), prog("a")));
  await assertFails(deleteDoc(doc(a, "consents/a")));                                      // 학생 철회 불가
  await assertFails(setDoc(doc(a, "consents/a"), cdoc("a", { ai: false })));               // 같은 내용으로 덮어쓸 수 없다(현재 버전 기록)
  await assertSucceeds(setDoc(doc(a, "consents/a"), cdoc("a", { ai: true })));             // 선택 항목에 동의하지 않았던 학생은 나중에 동의(false → true)만 할 수 있다
  await assertFails(setDoc(doc(a, "consents/a"), cdoc("a", { ai: false })));               // 철회(true → false) 불가
  await assertSucceeds(setDoc(doc(a, "progress/a"), prog("a", { activeMs: 2000 })));       // 그대로 계속 쓸 수 있다
  await assertSucceeds(deleteDoc(doc(teacher(), "consents/a")));                           // 교사 초기화
  await assertFails(setDoc(doc(a, "progress/a"), prog("a", { activeMs: 9999 })));          // 다시 동의하기 전까지 막힘
  await assertSucceeds(setDoc(doc(a, "consents/a"), cdoc("a")));                           // 다시 동의
  await assertSucceeds(setDoc(doc(a, "progress/a"), prog("a", { activeMs: 9999 })));
  await assertFails(setDoc(doc(pupil("b"), "consents/c"), cdoc("c")));                     // 남이 대신 동의할 수 없다
});
test("동의: 본인 uid·서버 시각·허용된 필드·본인 이메일만 쓸 수 있다", async () => {
  const c = pupil("c");
  await assertFails(setDoc(doc(c, "consents/d"), cdoc("d")));                              // 남의 문서
  await assertFails(setDoc(doc(c, "consents/c"), cdoc("d")));                              // uid 위조
  await assertFails(setDoc(doc(c, "consents/c"), cdoc("c", { agreedAt: Timestamp.fromMillis(0) })));   // 클라이언트가 정한 시각
  await assertFails(setDoc(doc(c, "consents/c"), cdoc("c", { extra: 1 })));                // 허용 밖 필드
  await assertFails(setDoc(doc(c, "consents/c"), cdoc("c", { ai: "yes" })));               // 선택 항목은 true/false
  await assertFails(setDoc(doc(c, "consents/c"), cdoc("c", { version: "1999" })));         // 현재 문구가 아닌 버전
  await assertFails(setDoc(doc(c, "consents/c"), cdoc("c", { student: { name: "홍", email: "x@ts.hs.kr" } })));   // 다른 사람 이메일
  await assertFails(setDoc(doc(c, "consents/c"), cdoc("c", { student: { name: "홍", email: "c@ts.hs.kr", number: "10101" } })));
  const noAi = cdoc("c"); delete noAi.ai;
  await assertFails(setDoc(doc(c, "consents/c"), noAi));
  await assertSucceeds(setDoc(doc(c, "consents/c"), cdoc("c", { ai: false })));            // 필수만 동의(첫 동의)
  await assertSucceeds(setDoc(doc(c, "consents/c"), cdoc("c", { ai: true })));             // 선택 항목에 동의하지 않았던 학생은 나중에 동의(false → true)할 수 있다
  await assertFails(setDoc(doc(c, "consents/c"), cdoc("c", { ai: false })));               // 동의한 선택 항목의 철회(true → false)는 학생이 못 한다
  await assertFails(deleteDoc(doc(c, "consents/c")));                                      // 지우기도 불가
});
/* ---------- 교재 코드 편집기에서 학생이 단 주석·고친 코드(codeNotes) ---------- */
const cHead = (uid, extra = {}) => Object.assign({ uid, student: { name: "홍", email: `${uid}@ts.hs.kr` }, updatedAt: serverTimestamp() }, extra);
const cBlk = (extra = {}) => Object.assign({ page: "01-factory-method", kind: "code", idx: 0, title: "순진한 코드", h: "abc123", code: "x = 1\n# 내 주석\n", added: "# 내 주석", addedN: 1, updatedAt: serverTimestamp() }, extra);
const saveCode = (db, uid, bid, blk, head) => { const b = writeBatch(db); b.set(doc(db, "codeNotes/" + uid), head || cHead(uid)); b.set(doc(db, `codeNotes/${uid}/blocks/${bid}`), blk || cBlk()); return b.commit(); };
test("학생 코드: 동의한 학생은 본인의 코드 블록을 저장·읽기·지울 수 있고, 동의가 없으면 저장할 수 없다", async () => {
  const c = pupil("c");
  await assertFails(saveCode(c, "c", "p__c0"));                                             // 동의 전
  await seedConsent("c", { version: CONSENT_V });
  await assertSucceeds(saveCode(c, "c", "p__c0"));
  await assertSucceeds(saveCode(c, "c", "p__c0", cBlk({ code: "y = 2", added: "y = 2" })));  // 같은 블록 다시 저장(덮어쓰기)
  await assertSucceeds(getDoc(doc(c, "codeNotes/c/blocks/p__c0")));
  await assertSucceeds(getDocs(collection(c, "codeNotes/c/blocks")));
  await assertSucceeds(getDoc(doc(c, "codeNotes/c")));
  await assertSucceeds(deleteDoc(doc(c, "codeNotes/c/blocks/p__c0")));                      // 처음 코드로 되돌리면 지운다
  await assertFails(deleteDoc(doc(c, "codeNotes/c")));                                       // 요약 문서는 교사만 지운다
});
test("학생 코드: 옛 문구에만 동의했거나 남의 문서·잘못된 모양·클라이언트 시각은 거부한다", async () => {
  const c = pupil("c");
  await seedConsent("c", { version: "2000-01-01" });
  await assertFails(saveCode(c, "c", "p__c0"));                                              // 옛 문구
  await seedConsent("c", { version: CONSENT_V });
  await assertFails(saveCode(c, "d", "p__c0"));                                              // 남의 uid
  await assertFails(saveCode(c, "c", "p__c0", cBlk({ extra: 1 })));                          // 허용 밖 필드
  await assertFails(saveCode(c, "c", "p__c0", cBlk({ updatedAt: Timestamp.fromMillis(0) })));  // 클라이언트가 정한 시각
  await assertFails(saveCode(c, "c", "p__c0", cBlk({ kind: "other" })));
  await assertFails(saveCode(c, "c", "p__c0", cBlk({ code: "x".repeat(30001) })));            // 너무 긺
  await assertFails(saveCode(c, "c", "bad.id", cBlk()));                                      // 블록 id 모양
  await assertFails(saveCode(c, "c", "p__c0", cBlk(), cHead("c", { student: { name: "홍", email: "x@ts.hs.kr" } })));   // 다른 사람 이메일
  await assertSucceeds(saveCode(c, "c", "p__c0"));
});
test("학생 코드: 교사는 모두 읽고 지우고, 다른 학생은 읽지·지우지 못하며 익명은 쓰지 못한다", async () => {
  await seedConsent("c", { version: CONSENT_V });
  await assertSucceeds(saveCode(pupil("c"), "c", "p__c0"));
  await assertSucceeds(getDocs(collection(teacher(), "codeNotes")));
  await assertSucceeds(getDocs(collection(teacher(), "codeNotes/c/blocks")));
  await assertFails(getDocs(collection(pupil("c"), "codeNotes")));                           // 학생은 목록을 못 읽는다
  await assertFails(getDoc(doc(pupil("b"), "codeNotes/c/blocks/p__c0")));
  await assertFails(deleteDoc(doc(pupil("b"), "codeNotes/c/blocks/p__c0")));
  await assertFails(saveCode(student("c"), "c", "p__c1"));                                    // 익명
  await assertSucceeds(deleteDoc(doc(teacher(), "codeNotes/c/blocks/p__c0")));
  await assertSucceeds(deleteDoc(doc(teacher(), "codeNotes/c")));
});
/* ---------- 돌발 퀴즈 ---------- */
test("돌발 퀴즈: 누구나 현재 퀴즈 정보를 읽되 쓰기는 불가, 답안·채점은 교사만, 결과는 본인만", async () => {
  await env.withSecurityRulesDisabled(async c => {
    const f = c.firestore();
    await setDoc(doc(f, "config/quiz"), { sid: "s1", state: "open", questions: [{ id: "q1", q: "?" }] });
    await setDoc(doc(f, "quizSessions/s1"), { slug: "x", state: "open" });
    await setDoc(doc(f, "quizSessions/s1/answers/a"), { uid: "a", answers: { q1: "답" } });
    await setDoc(doc(f, "quizSessions/s1/answers/b"), { uid: "b", answers: { q1: "답" } });
    await setDoc(doc(f, "quizSessions/s1/grades/a"), { uid: "a", total: 3 });
    await setDoc(doc(f, "quizResults/s1__a"), { uid: "a", total: 3 });
    await setDoc(doc(f, "quizResults/s1__b"), { uid: "b", total: 1 });
  });
  const a = pupil("a");
  await assertSucceeds(getDoc(doc(a, "config/quiz")));
  await assertFails(setDoc(doc(a, "config/quiz"), { state: "closed" }));
  await assertFails(setDoc(doc(teacher(), "config/quiz"), { state: "closed" }));           // 교사도 직접 못 쓴다(함수만)
  await assertFails(getDoc(doc(a, "quizSessions/s1")));
  await assertSucceeds(getDoc(doc(a, "quizSessions/s1/answers/a")));                       // 본인 답안
  await assertFails(getDoc(doc(a, "quizSessions/s1/answers/b")));
  await assertFails(getDocs(collection(a, "quizSessions/s1/answers")));
  await assertFails(setDoc(doc(a, "quizSessions/s1/answers/a"), { uid: "a", answers: { q1: "고침" } }));   // 답안은 함수로만
  await assertFails(getDoc(doc(a, "quizSessions/s1/grades/a")));                            // 채점 초안은 교사만
  await assertSucceeds(getDoc(doc(a, "quizResults/s1__a")));
  await assertFails(getDoc(doc(a, "quizResults/s1__b")));
  await assertSucceeds(getDocs(query(collection(a, "quizResults"), where("uid", "==", "a"))));
  await assertFails(getDocs(collection(a, "quizResults")));                                  // 남의 결과까지 훑는 조회는 불가
  await assertFails(setDoc(doc(a, "quizResults/s1__a"), { uid: "a", total: 99 }));
  const t = teacher();
  await assertSucceeds(getDoc(doc(t, "quizSessions/s1")));
  await assertSucceeds(getDocs(collection(t, "quizSessions/s1/answers")));
  await assertSucceeds(getDoc(doc(t, "quizSessions/s1/grades/a")));
  await assertSucceeds(getDocs(collection(t, "quizResults")));
  await assertFails(setDoc(doc(t, "quizSessions/s1/grades/a"), { total: 9 }));              // 교사도 직접 쓰지 못한다
  await assertSucceeds(deleteDoc(doc(t, "quizResults/s1__a")));
});

test("동의: 익명·학교 밖 계정은 동의 문서를 쓸 수 없다", async () => {
  await assertFails(setDoc(doc(student("c"), "consents/c"), cdoc("c")));
  const gmail = env.authenticatedContext("g", { email: "g@gmail.com", email_verified: true, firebase: { sign_in_provider: "google.com" } }).firestore();
  await assertFails(setDoc(doc(gmail, "consents/g"), cdoc("g", { student: { name: "홍", email: "g@gmail.com" } })));
});
test("동의: 읽기는 본인(한 건)과 교사(목록·삭제)만, 학생은 목록·남의 것을 못 본다", async () => {
  await seedConsent("c");
  await assertSucceeds(getDoc(doc(pupil("c"), "consents/c")));
  await assertFails(getDoc(doc(pupil("b"), "consents/c")));
  await assertFails(getDocs(collection(pupil("c"), "consents")));
  await assertSucceeds(getDocs(collection(teacher(), "consents")));
  await assertFails(deleteDoc(doc(pupil("b"), "consents/c")));
  await assertFails(deleteDoc(doc(pupil("c"), "consents/c")));                             // 본인도 철회 불가
  await assertSucceeds(deleteDoc(doc(teacher(), "consents/c")));
});
