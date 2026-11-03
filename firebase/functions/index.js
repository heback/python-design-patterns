"use strict";
const { onCall, HttpsError } = require("firebase-functions/v2/https");
const { defineSecret } = require("firebase-functions/params");
const admin = require("firebase-admin");
const { GoogleGenAI, Type } = require("@google/genai");
const { TEACHER_DOMAIN, REGION, MODEL, MAX_ITEMS, ASSISTANT_DAILY_LIMIT, ASSISTANT_MINUTE_LIMIT } = require("./config");
const assistant = require("./assistant");
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

/** 학생 AI 도우미. 학교 Google 계정(학생·교사)만, 교사가 켠 동안만, 학생별 사용 한도 안에서 답한다.
 *  질문·답은 저장하지 않는다(사용 횟수만 chatUsage/{uid} 에 센다). 질문·사진·현재 화면의 글이 Gemini 로 전달된다. */
async function askModel(apiKey, v) {
  if (!apiKey && process.env.FUNCTIONS_EMULATOR) {            // 에뮬레이터에는 키가 없다: 시험용 답(범위 판정은 질문에 '[범위밖]'이 있으면 거절로 흉내 낸다)
    return v.question.includes("[범위밖]") ? { ok: true, reply: assistant.REFUSAL, refused: true } : { ok: true, reply: "(에뮬레이터 시험 답변) " + v.question.slice(0, 60), refused: false };
  }
  return require("./assistant-model").answer(apiKey, v);
}

exports.askAssistant = onCall({ region: REGION, secrets: [GEMINI_API_KEY], maxInstances: 10, timeoutSeconds: 60 }, async req => {
  if (!req.auth) throw new HttpsError("unauthenticated", "로그인이 필요합니다.");
  if (!isSchoolAccount(req.auth)) throw new HttpsError("permission-denied", `학교 계정(@${TEACHER_DOMAIN})으로 로그인해야 합니다.`);
  const cfg = (await db.doc("config/assistant").get()).data();
  if (!cfg || cfg.on !== true) throw new HttpsError("failed-precondition", "지금은 AI 도우미를 쓸 수 없어요. 선생님이 켜 주면 쓸 수 있어요.");
  const v = assistant.validate(req.data);
  if (v.error) throw new HttpsError("invalid-argument", v.error);

  const ref = db.doc(`chatUsage/${req.auth.uid}`), limits = { daily: ASSISTANT_DAILY_LIMIT, minute: ASSISTANT_MINUTE_LIMIT };
  const used = await db.runTransaction(async tx => {                      // 모델을 부르기 전에 한도를 확인하고 한 번 센다
    const snap = await tx.get(ref), r = assistant.checkLimit(snap.exists ? snap.data() : null, Date.now(), limits);
    if (r.ok) tx.set(ref, r.next);
    return r;
  });
  if (!used.ok) throw new HttpsError("resource-exhausted", used.reason === "minute" ? "질문이 너무 빨라요. 잠시 뒤에 다시 물어봐 주세요." : `오늘 질문은 ${ASSISTANT_DAILY_LIMIT}번까지예요. 내일 다시 물어봐 주세요.`);

  try {
    const r = await askModel(GEMINI_API_KEY.value(), v.value);
    if (!r.ok) throw new Error("답 형식 오류");
    return { reply: r.reply, refused: !!r.refused, left: Math.max(0, ASSISTANT_DAILY_LIMIT - used.next.count) };
  } catch (e) {
    await db.runTransaction(async tx => { const snap = await tx.get(ref); if (snap.exists && snap.data().count > 0) tx.update(ref, { count: snap.data().count - 1 }); }).catch(() => {});   // 실패한 질문은 세지 않는다
    console.error("askAssistant 실패:", e && e.message);
    throw new HttpsError("unavailable", "지금은 답을 만들지 못했어요. 잠시 뒤에 다시 시도해 주세요.");
  }
});

exports._test = { sanitize, isSchoolAccount };
