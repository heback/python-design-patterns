"use strict";
const { onCall, HttpsError } = require("firebase-functions/v2/https");
const { defineSecret } = require("firebase-functions/params");
const admin = require("firebase-admin");
const { Timestamp, FieldValue } = require("firebase-admin/firestore");
const { GoogleGenAI, Type } = require("@google/genai");
const { TEACHER_DOMAIN, REGION, MODEL, MAX_ITEMS, ASSISTANT_MODEL, ASSISTANT_CHAPTER_LIMIT, ASSISTANT_LIMIT_MAX, ASSISTANT_MINUTE_LIMIT, CONSENT_VERSION } = require("./config");
const assistant = require("./assistant");
const askTeacher = require("./askteacher");
const { answerText, isBlank, buildPrompt, SYSTEM } = require("./prompt");

admin.initializeApp();
const db = admin.firestore();
const GEMINI_API_KEY = defineSecret("GEMINI_API_KEY");

/** 학교 Google 계정인가(학생·교사 공통). firestore.rules의 isSchoolAccount()와 같은 조건. */
function isSchoolAccount(auth) {
  const t = auth && auth.token;
  return !!(t && t.email && t.email_verified === true && t.firebase && t.firebase.sign_in_provider === "google.com"
    && t.email.toLowerCase().endsWith("@" + TEACHER_DOMAIN));
}

/** 교사 = 학교 계정 + config/teachers 허용 목록. 학생도 같은 도메인이므로 목록이 없거나 비어 있으면 아무도 교사가 아니다(닫힘). */
async function assertTeacher(auth) {
  if (!isSchoolAccount(auth)) throw new HttpsError("permission-denied", `학교 계정(@${TEACHER_DOMAIN})으로 로그인해야 합니다.`);
  const snap = await db.doc("config/teachers").get();
  const raw = snap.exists ? snap.data().emails : undefined;
  // firestore.rules 의 판정과 똑같이 맞춘다: emails 는 문자열 배열이어야 하고 이메일이 글자 그대로(소문자) 들어 있어야 한다.
  // (문자열 필드일 때 includes 가 부분 문자열로 통과해 화면은 열리는데 데이터 규칙에서만 거부되는 어긋남을 막는다)
  if (raw !== undefined && !Array.isArray(raw)) throw new HttpsError("failed-precondition", "config/teachers 의 emails 필드는 '배열(array)' 형식이어야 합니다. 콘솔에서 필드 유형을 배열로 바꾸고 이메일을 각각 문자열로 넣으세요.");
  const emails = Array.isArray(raw) ? raw : [];
  if (!emails.length) throw new HttpsError("failed-precondition", "교사 허용 목록(config/teachers)이 비어 있습니다. Firebase 콘솔에서 교사 이메일을 등록하세요.");
  if (!emails.includes(auth.token.email)) throw new HttpsError("permission-denied", `교사 허용 목록에 없는 계정입니다(${auth.token.email}). 목록의 이메일은 공백 없이 소문자로 정확히 적어야 합니다.`);
}

function loadContent() {
  try { return require("./teacher-content.json"); }
  catch (e) { throw new HttpsError("failed-precondition", "teacher-content.json이 없습니다. python3 inquiry/build.py 후 다시 배포하세요."); }
}

exports.getTeacherContent = onCall({ region: REGION }, async req => {
  await assertTeacher(req.auth);
  return loadContent();
});

const SCHEMA = {
  type: Type.OBJECT,
  properties: {
    items: { type: Type.ARRAY, items: { type: Type.OBJECT, properties: {
      id: { type: Type.STRING }, mark: { type: Type.INTEGER }, comment: { type: Type.STRING } }, required: ["id", "mark", "comment"] } },
    weekComment: { type: Type.STRING },
  },
  required: ["items", "weekComment"],
};

/** 검증: 요청한 id만, mark 1~3, 문자열 코멘트. */
function sanitize(out, ids) {
  const items = [];
  for (const x of (out && out.items) || []) {
    if (!x || !ids.has(x.id)) continue;
    const mark = Number(x.mark);
    if (![1, 2, 3].includes(mark) || typeof x.comment !== "string" || !x.comment.trim()) continue;
    items.push({ id: x.id, mark, comment: x.comment.trim().slice(0, 800) });
  }
  return { items, weekComment: typeof out.weekComment === "string" ? out.weekComment.trim().slice(0, 1200) : "" };
}

async function callGemini(apiKey, prompt, ids) {
  const ai = new GoogleGenAI({ apiKey });
  for (let attempt = 0; attempt < 2; attempt++) {
    try {
      const r = await ai.models.generateContent({ model: MODEL, contents: prompt,
        config: { systemInstruction: SYSTEM, responseMimeType: "application/json", responseSchema: SCHEMA, temperature: 0.4 } });
      const res = sanitize(JSON.parse(r.text), ids);
      if (res.items.length) return res;
    } catch (e) { if (attempt) throw e; }
  }
  throw new HttpsError("internal", "AI 응답을 해석하지 못했습니다. 잠시 뒤 다시 시도해 주세요.");
}

exports.generateFeedback = onCall({ region: REGION, secrets: [GEMINI_API_KEY], maxInstances: 5, timeoutSeconds: 180 }, async req => {
  await assertTeacher(req.auth);
  const { submissionId, week } = req.data || {};
  if (typeof submissionId !== "string" || !submissionId || submissionId.includes("/") || !(week >= 1 && week <= 9))
    throw new HttpsError("invalid-argument", "submissionId와 week가 필요합니다.");
  const content = loadContent();
  const w = content.weeks.find(x => x.n === week);
  if (!w) throw new HttpsError("invalid-argument", "없는 주차입니다.");

  const wk = await db.doc(`submissions/${submissionId}/weeks/${week}`).get();
  let answers = {};
  try { answers = wk.exists ? JSON.parse(wk.data().json) : {}; } catch (e) { throw new HttpsError("data-loss", "저장된 응답을 읽지 못했습니다."); }
  const want = Array.isArray(req.data.itemIds) ? new Set(req.data.itemIds) : null;

  const entries = [];
  for (const st of w.stages) for (const it of st.items) {
    if (it.type === "info" || it.type === "scales") continue;
    if (want && !want.has(it.id)) continue;
    const v = answers[it.id];
    if (isBlank(it, v)) continue;
    entries.push({ id: it.id, type: it.type, q: it.q, note: it.note,
      answer: it.answer == null ? "" : answerText(it, it.answer), student: answerText(it, v) });
  }
  if (!entries.length) throw new HttpsError("failed-precondition", "이 주차에 응답한 문항이 없습니다.");
  if (entries.length > MAX_ITEMS) entries.length = MAX_ITEMS;

  const res = await callGemini(GEMINI_API_KEY.value(), buildPrompt(w, entries), new Set(entries.map(e => e.id)));
  const at = new Date().toISOString(), drafts = {};
  const batch = db.batch();
  for (const x of res.items) {
    drafts[x.id] = { mark: x.mark, comment: x.comment, ai: true, model: MODEL, at };
    batch.set(db.doc(`submissions/${submissionId}/drafts/${x.id}`), drafts[x.id]);
  }
  if (res.weekComment) {
    drafts[`week-${week}`] = { comment: res.weekComment, ai: true, model: MODEL, at };
    batch.set(db.doc(`submissions/${submissionId}/drafts/week-${week}`), drafts[`week-${week}`]);
  }
  await batch.commit();
  return { drafts };
});

/** 진도 수집 켜기/끄기. 교사만 부를 수 있고, 스위치(config/monitor)와 변경 이력(monitorEvents)을 한 번에 쓴다.
 *  둘 다 서버 시각(serverTimestamp)이 찍히고 클라이언트는 직접 쓸 수 없다(규칙) — '언제 켜고 껐는지'를 나중에 바꿀 수 없다. */
exports.setMonitor = onCall({ region: REGION, maxInstances: 5 }, async req => {
  await assertTeacher(req.auth);
  if (typeof (req.data || {}).on !== "boolean") throw new HttpsError("invalid-argument", "on 은 true/false 여야 합니다.");
  const on = req.data.on, by = req.auth.token.email, at = FieldValue.serverTimestamp(), batch = db.batch();
  batch.set(db.doc("config/monitor"), { on, updatedBy: by, updatedAt: at });
  batch.set(db.collection("monitorEvents").doc(), { on, by, at });
  await batch.commit();
  return { on };
});

/** 장 키 → 이름. 교재의 장 slug 와 학습지 주차(week1~)를 teacher-content.json 에서 읽고, 목록에 없는 화면은 'etc' 한 칸으로 모은다. */
let CH_TABLE = null;
function chapterTable() {
  if (CH_TABLE) return CH_TABLE;
  const m = new Map();
  try {
    const c = require("./teacher-content.json");
    for (const x of c.chapters || []) m.set(x.slug, x.title);
    for (const w of c.weeks || []) m.set("week" + w.n, `학습지 ${w.n}주차`);
  } catch (e) { /* 내용 파일이 없으면 모든 화면이 '기타' 한 칸을 쓴다 */ }
  m.set(assistant.ETC, "기타 화면");
  return (CH_TABLE = m);
}

/** 학생 AI 도우미. 학교 Google 계정(학생·교사)만, 교사가 켠 동안만, 학생별·장별 사용 한도 안에서 답한다.
 *  한도 = 기본(config/assistant.limit, 없으면 40) + 교사가 학생별로 가감한 값(chatQuota/{uid}). 쓴 횟수는 chatUsage/{uid}.chapters 에 센다.
 *  질문·사진·현재 화면의 글이 Gemini 로 전달된다. */
async function askModel(apiKey, v) {
  if (!apiKey && process.env.FUNCTIONS_EMULATOR) {            // 에뮬레이터에는 키가 없다: 시험용 답(범위 판정은 질문에 '[범위밖]'이 있으면 거절로 흉내 낸다)
    const off = v.question.includes("[범위밖]"), reply = off ? assistant.REFUSAL : "(에뮬레이터 시험 답변) " + v.question.slice(0, 60);
    return { ok: true, reply, refused: off, usage: { prompt: v.question.length * 2, output: reply.length, thoughts: 0, total: v.question.length * 2 + reply.length } };      // 토큰 집계 시험용 가짜 사용량
  }
  return require("./assistant-model").answer(apiKey, v);
}

exports.askAssistant = onCall({ region: REGION, secrets: [GEMINI_API_KEY], maxInstances: 10, timeoutSeconds: 60 }, async req => {
  if (!req.auth) throw new HttpsError("unauthenticated", "로그인이 필요합니다.");
  if (!isSchoolAccount(req.auth)) throw new HttpsError("permission-denied", `학교 계정(@${TEACHER_DOMAIN})으로 로그인해야 합니다.`);
  const cfg = (await db.doc("config/assistant").get()).data();
  if (!cfg || cfg.on !== true) throw new HttpsError("failed-precondition", "지금은 AI 도우미를 쓸 수 없어요. 선생님이 켜 주면 쓸 수 있어요.");
  const noConsent = assistant.consentGate((await db.doc(`consents/${req.auth.uid}`).get()).data(), CONSENT_VERSION);      // 개인정보 동의(필수+AI 선택 항목)가 없으면 질문·사진을 Gemini 로 보내지 않는다
  if (noConsent) throw new HttpsError("failed-precondition", noConsent);
  const v = assistant.validate(req.data);
  if (v.error) throw new HttpsError("invalid-argument", v.error);

  const ref = db.doc(`chatUsage/${req.auth.uid}`), quotaRef = db.doc(`chatQuota/${req.auth.uid}`), key = assistant.chapterKey(v.value.context.chapter, new Set(chapterTable().keys()));
  const used = await db.runTransaction(async tx => {                      // 모델을 부르기 전에 한도를 확인하고 한 번 센다
    const [snap, qs] = await Promise.all([tx.get(ref), tx.get(quotaRef)]);
    const limit = assistant.limitFor(cfg.limit, qs.exists ? qs.data() : null, key, ASSISTANT_CHAPTER_LIMIT, ASSISTANT_LIMIT_MAX);
    const r = assistant.checkLimit(snap.exists ? snap.data() : null, Date.now(), { minute: ASSISTANT_MINUTE_LIMIT, chapter: limit, key });
    if (r.ok) tx.set(ref, r.next, { merge: true });          // merge: 같은 문서의 누적 토큰·횟수(total_*)와 다른 장의 횟수를 지우지 않는다
    return r;
  });
  const chTitle = chapterTable().get(key);
  if (!used.ok) throw new HttpsError("resource-exhausted", used.reason === "minute" ? "질문이 너무 빨라요. 잠시 뒤에 다시 물어봐 주세요."
    : used.limit === 0 ? `이 장(${chTitle})에서는 AI 도우미를 쓸 수 없어요. 선생님께 물어보세요.` : `이 장(${chTitle})에서 쓸 수 있는 질문 ${used.limit}번을 모두 썼어요. 더 필요하면 선생님께 말씀드려 보세요.`);

  const t0 = Date.now(), day = new Date(t0 + 9 * 3600e3).toISOString().slice(0, 10);
  const tk = req.auth.token, student = { name: (tk.name || "").trim() || (tk.email || "").split("@")[0], email: (tk.email || "").toLowerCase() };
  const base = { uid: req.auth.uid, student, kind: v.value.context.kind, where: v.value.context.title, v: v.value, model: ASSISTANT_MODEL, at: Timestamp.now(), day };
  try {
    const r = await askModel(GEMINI_API_KEY.value(), v.value);
    await recordChat(Object.assign({}, base, { reply: r.ok ? r.reply : "", refused: !!r.refused, error: r.ok ? "" : "답 형식 오류", usage: r.usage, ms: Date.now() - t0 }))
      .catch(err => console.error("대화 기록 실패:", err && err.message));          // 기록이 실패해도 학생의 답은 막지 않는다
    if (!r.ok) throw new Error("답 형식 오류");
    return { reply: r.reply, refused: !!r.refused, left: Math.max(0, used.limit - used.used), limit: used.limit, chapter: key, chapterTitle: chTitle };
  } catch (e) {
    if (!(e && e.message === "답 형식 오류")) await recordChat(Object.assign({}, base, { error: String(e && e.message || e).slice(0, 200), ms: Date.now() - t0 })).catch(() => {});     // 호출 실패도 기록한다
    await db.runTransaction(async tx => { const snap = await tx.get(ref), n = snap.exists ? ((snap.data().chapters || {})[key] || 0) : 0; if (n > 0) tx.set(ref, { chapters: { [key]: n - 1 } }, { merge: true }); }).catch(() => {});   // 실패한 질문은 그 장의 사용 횟수에서 뺀다
    console.error("askAssistant 실패:", e && e.message);
    const exhausted = /credit|billing|prepay|quota|RESOURCE_EXHAUSTED|"code":\s*(402|429)/i.test(String(e && e.message || e));       // 모델 쪽 크레딧·요금 한도 소진
    throw new HttpsError("unavailable", exhausted ? "AI 도우미의 사용량(크레딧)이 모두 소진되어 지금은 쓸 수 없어요. 선생님께 알려 주세요." : "지금은 답을 만들지 못했어요. 잠시 뒤에 다시 시도해 주세요.");
  }
});

/** 학생이 자기 화면의 장에서 남은 질문 수를 본다(대화창을 열거나 장을 옮길 때). 한도 계산은 askAssistant 와 같다. */
exports.getAssistantQuota = onCall({ region: REGION, maxInstances: 10 }, async req => {
  if (!isSchoolAccount(req.auth)) throw new HttpsError("permission-denied", `학교 계정(@${TEACHER_DOMAIN})으로 로그인해야 합니다.`);
  const key = assistant.chapterKey(((req.data || {}).chapter || "").toString().slice(0, 60), new Set(chapterTable().keys()));
  const [cfg, qs, us] = await Promise.all([db.doc("config/assistant").get(), db.doc(`chatQuota/${req.auth.uid}`).get(), db.doc(`chatUsage/${req.auth.uid}`).get()]);
  const limit = assistant.limitFor((cfg.data() || {}).limit, qs.exists ? qs.data() : null, key, ASSISTANT_CHAPTER_LIMIT, ASSISTANT_LIMIT_MAX);
  const used = us.exists ? ((us.data().chapters || {})[key] || 0) : 0;
  return { chapter: key, chapterTitle: chapterTable().get(key), limit, used, left: Math.max(0, limit - used) };
});

/** 교사가 한 학생의 장별 한도를 가감한다(기본 한도에 더하거나 뺀다). chapter 는 "all"(모든 장)이나 장 키, value 는 가감할 값(정수, 0 이면 가감 없음). 교사만. */
exports.setAssistantQuota = onCall({ region: REGION, maxInstances: 5 }, async req => {
  await assertTeacher(req.auth);
  const { uid, chapter, value } = req.data || {};
  if (typeof uid !== "string" || !uid || uid.includes("/") || uid.length > 128) throw new HttpsError("invalid-argument", "학생(uid)이 필요합니다.");
  const n = assistant.int(value, -ASSISTANT_LIMIT_MAX, ASSISTANT_LIMIT_MAX);
  if (n === null) throw new HttpsError("invalid-argument", `가감 값은 -${ASSISTANT_LIMIT_MAX} ~ ${ASSISTANT_LIMIT_MAX} 사이의 정수여야 합니다.`);
  const meta = { updatedBy: req.auth.token.email, updatedAt: FieldValue.serverTimestamp() }, v = n === 0 ? FieldValue.delete() : n;
  if (chapter === "all") await db.doc(`chatQuota/${uid}`).set({ all: v, ...meta }, { merge: true });
  else if (typeof chapter === "string" && chapterTable().has(chapter)) await db.doc(`chatQuota/${uid}`).set({ chapters: { [chapter]: v }, ...meta }, { merge: true });
  else throw new HttpsError("invalid-argument", "알 수 없는 장입니다.");
  return { uid, chapter, value: n };
});

/** 대화 한 건을 chatLogs 에 남기고, 학생별(chatUsage, 누적 total_* 와 날짜별 byDay)·반 전체(stats/assistant, 날짜별) 토큰·횟수를 센다. 교사만 읽을 수 있다(규칙).
 *  사진 파일은 저장하지 않는다(있었는지와 크기만). 한도용 chatUsage 의 day/count 필드와 같은 문서를 쓰되 merge 로 서로 덮어쓰지 않는다. */
async function recordChat(e) {
  const entry = assistant.logEntry(e), u = entry.usage, inc = FieldValue.increment;
  const sums = { count: inc(1), refused: inc(entry.refused ? 1 : 0), errors: inc(entry.error ? 1 : 0), images: inc(entry.hasImage ? 1 : 0), promptTokens: inc(u.prompt), outputTokens: inc(u.output), thoughtTokens: inc(u.thoughts), totalTokens: inc(u.total) };
  const batch = db.batch();
  batch.set(db.collection("chatLogs").doc(), entry);
  batch.set(db.doc(`chatUsage/${e.uid}`), Object.assign({ student: e.student, lastAt: e.at }, Object.fromEntries(Object.entries(sums).map(([k, f]) => ["total_" + k, f])), { byDay: { [e.day]: sums } }), { merge: true });      // byDay: 학생별 날짜별 집계(교사 화면의 기간별 토큰 사용량)
  batch.set(db.doc("stats/assistant"), Object.assign({ updatedAt: e.at }, sums, { byDay: { [e.day]: sums } }), { merge: true });
  await batch.commit();
}

/* ===================== 선생님께 질문 (askThreads) =====================
   학생 한 명당 대화 하나: askThreads/{uid}(목록용 요약·안 읽음 수)와 그 아래 msgs/{id}(질문·답변 한 건씩).
   쓰기는 모두 아래 함수만 한다(규칙: 클라이언트는 읽기만, 학생은 자기 대화만). 질문 개수 제한은 없고 1분에 10번까지만 받는다(도배 방지).
   unread = 선생님이 아직 안 본 학생 질문 수(교사 화면 배지), studentUnread = 학생이 아직 안 본 선생님 답변 수(학생 화면 배지). */
const threadRef = uid => db.doc(`askThreads/${uid}`);

exports.askTeacher = onCall({ region: REGION, maxInstances: 10, timeoutSeconds: 30 }, async req => {
  if (!req.auth) throw new HttpsError("unauthenticated", "로그인이 필요합니다.");
  if (!isSchoolAccount(req.auth)) throw new HttpsError("permission-denied", `학교 계정(@${TEACHER_DOMAIN})으로 로그인해야 합니다.`);
  const noConsent = askTeacher.consentGate((await db.doc(`consents/${req.auth.uid}`).get()).data(), CONSENT_VERSION);
  if (noConsent) throw new HttpsError("failed-precondition", noConsent);
  const v = askTeacher.validateQuestion(req.data);
  if (v.error) throw new HttpsError("invalid-argument", v.error);
  const uid = req.auth.uid, tk = req.auth.token, student = { name: (tk.name || "").trim() || (tk.email || "").split("@")[0], email: (tk.email || "").toLowerCase() };
  const ref = threadRef(uid), msgRef = ref.collection("msgs").doc();
  const ok = await db.runTransaction(async tx => {
    const snap = await tx.get(ref), r = askTeacher.checkRate(snap.exists ? snap.data() : null, Date.now(), askTeacher.LIMITS.minute);
    if (!r.ok) return false;
    const at = Timestamp.now();
    tx.set(msgRef, askTeacher.studentMessage(v.value, at));
    tx.set(ref, Object.assign({ uid, student }, askTeacher.threadHead("student", v.value.text, !!v.value.image, at), r.next, { unread: FieldValue.increment(1), msgCount: FieldValue.increment(1) }), { merge: true });
    return true;
  });
  if (!ok) throw new HttpsError("resource-exhausted", "질문이 너무 빨라요. 잠시 뒤에 다시 보내 주세요.");
  return { id: msgRef.id };
});

/** 교사가 학생에게 답한다. 직접 쓴 답이든 AI 추천을 고친 답이든 같은 경로이고, viaAi 로 AI 추천을 거쳤는지만 남긴다. */
exports.replyToStudent = onCall({ region: REGION, maxInstances: 5 }, async req => {
  await assertTeacher(req.auth);
  const v = askTeacher.validateReply(req.data);
  if (v.error) throw new HttpsError("invalid-argument", v.error);
  const ref = threadRef(v.value.uid);
  if (!(await ref.get()).exists) throw new HttpsError("not-found", "이 학생의 질문 대화가 없습니다.");
  const at = Timestamp.now(), msgRef = ref.collection("msgs").doc(), batch = db.batch();
  batch.set(msgRef, askTeacher.teacherMessage(v.value, req.auth.token.email, at));
  batch.set(ref, Object.assign(askTeacher.threadHead("teacher", v.value.text, false, at), { unread: 0, studentUnread: FieldValue.increment(1), msgCount: FieldValue.increment(1) }), { merge: true });
  await batch.commit();
  return { id: msgRef.id };
});

/** 읽음 처리. 교사가 uid 를 주면 그 학생의 '새 질문' 배지를, 학생은(uid 없이) 자기 '새 답변' 배지를 0 으로 한다. 대화가 없으면 아무것도 하지 않는다. */
exports.markAskRead = onCall({ region: REGION, maxInstances: 10 }, async req => {
  if (!isSchoolAccount(req.auth)) throw new HttpsError("permission-denied", `학교 계정(@${TEACHER_DOMAIN})으로 로그인해야 합니다.`);
  const target = (req.data || {}).uid;
  let uid = req.auth.uid, field = "studentUnread";
  if (target != null) {
    await assertTeacher(req.auth);
    if (typeof target !== "string" || !target || target.includes("/") || target.length > 128) throw new HttpsError("invalid-argument", "학생(uid)이 필요합니다.");
    uid = target; field = "unread";
  }
  const ref = threadRef(uid);
  await db.runTransaction(async tx => { const s = await tx.get(ref); if (s.exists && (s.data()[field] || 0) !== 0) tx.update(ref, { [field]: 0 }); });
  return { ok: true };
});

/** 교사용 AI 추천 답변. 학생과 주고받은 최근 대화(이름·이메일 제외)와 마지막 질문의 사진·화면 정보를 Gemini 로 보내 초안을 받는다. 초안은 교사 화면의 입력란에만 들어가고, 교사가 보내기 전에는 학생에게 가지 않는다. */
async function suggestModel(apiKey, msgs) {
  if (!apiKey && process.env.FUNCTIONS_EMULATOR) {            // 에뮬레이터에는 키가 없다: 시험용 초안
    const last = [...msgs].reverse().find(m => m.from === "student"), draft = "(에뮬레이터 시험 추천 답변) " + ((last && last.text) || "").slice(0, 60);
    return { ok: true, draft, caution: "시험용 답변입니다.", usage: { prompt: 10, output: draft.length, thoughts: 0, total: 10 + draft.length } };
  }
  return require("./askteacher-model").suggest(apiKey, msgs);
}

exports.suggestReply = onCall({ region: REGION, secrets: [GEMINI_API_KEY], maxInstances: 5, timeoutSeconds: 60 }, async req => {
  await assertTeacher(req.auth);
  const uid = (req.data || {}).uid;
  if (typeof uid !== "string" || !uid || uid.includes("/") || uid.length > 128) throw new HttpsError("invalid-argument", "학생(uid)이 필요합니다.");
  const noAi = askTeacher.aiConsentGate((await db.doc(`consents/${uid}`).get()).data(), CONSENT_VERSION);      // AI(선택 항목)에 동의하지 않은 학생의 질문은 Gemini 로 보내지 않는다
  if (noAi) throw new HttpsError("failed-precondition", noAi);
  const snap = await threadRef(uid).collection("msgs").orderBy("at", "desc").limit(askTeacher.LIMITS.hist).get();
  const msgs = snap.docs.map(d => d.data()).reverse();
  if (!msgs.length || msgs[msgs.length - 1].from !== "student") throw new HttpsError("failed-precondition", "답할 새 질문이 없습니다(마지막 메시지가 이미 선생님의 답변입니다).");
  let r;
  try { r = await suggestModel(GEMINI_API_KEY.value(), msgs); }
  catch (e) {
    console.error("suggestReply 실패:", e && e.message);
    const exhausted = /credit|billing|prepay|quota|RESOURCE_EXHAUSTED|"code":\s*(402|429)/i.test(String(e && e.message || e));
    throw new HttpsError("unavailable", exhausted ? "AI의 사용량(크레딧)이 모두 소진되어 추천 답변을 만들 수 없습니다. Google AI Studio의 결제 설정을 확인하세요." : "추천 답변을 만들지 못했습니다. 잠시 뒤에 다시 시도해 주세요.");
  }
  const u = r.usage, inc = FieldValue.increment, day = new Date(Date.now() + 9 * 3600e3).toISOString().slice(0, 10);
  const sums = { suggestions: inc(1), failed: inc(r.ok ? 0 : 1), promptTokens: inc(u.prompt), outputTokens: inc(u.output), thoughtTokens: inc(u.thoughts), totalTokens: inc(u.total) };
  const sug = { sugCount: inc(1), sugPrompt: inc(u.prompt), sugOutput: inc(u.output), sugThought: inc(u.thoughts), sugTotal: inc(u.total) };      // [AI 사용량] 화면용: AI 도우미 질문과 같은 문서에 sug* 로 따로 쌓아 합산해 보여 준다(질문 수 count 와 섞이지 않게)
  const stu = ((await threadRef(uid).get()).data() || {}).student || null;
  const batch = db.batch(), now = Timestamp.now();
  batch.set(db.doc("stats/askTeacher"), Object.assign({ updatedAt: now }, sums, { byDay: { [day]: sums } }), { merge: true });
  batch.set(db.doc(`chatUsage/${uid}`), Object.assign({ lastAt: now }, stu ? { student: stu } : {}, Object.fromEntries(Object.entries(sug).map(([k, f]) => ["total_" + k, f])), { byDay: { [day]: sug } }), { merge: true });
  batch.set(db.doc("stats/assistant"), Object.assign({ updatedAt: now }, sug, { byDay: { [day]: sug } }), { merge: true });
  await batch.commit().catch(err => console.error("추천 답변 집계 실패:", err && err.message));
  if (!r.ok) throw new HttpsError("internal", "AI 응답을 해석하지 못했습니다. 잠시 뒤 다시 시도해 주세요.");
  return { draft: r.draft, caution: r.caution };
});

exports._test = { sanitize, isSchoolAccount };
