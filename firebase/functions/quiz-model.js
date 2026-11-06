"use strict";
// 돌발 퀴즈 AI 채점의 모델 호출. index.js(gradeQuizAnswer)에서만 쓴다.
const { GoogleGenAI, Type } = require("@google/genai");
const { MODEL } = require("./config");
const assistant = require("./assistant");
const quiz = require("./quiz");

const SCHEMA = { type: Type.OBJECT, properties: {
  items: { type: Type.ARRAY, items: { type: Type.OBJECT, properties: { id: { type: Type.STRING }, hits: { type: Type.ARRAY, items: { type: Type.BOOLEAN } }, score: { type: Type.INTEGER }, feedback: { type: Type.STRING } }, required: ["id", "hits", "score", "feedback"] } },
  summary: { type: Type.STRING } }, required: ["items", "summary"] };

/** questions = [{id, q, key, model}], answers = {qid: 글}. 반환 {ok, items, summary, total, max, usage}. usage 는 재시도까지 합친 토큰 수. */
async function grade(apiKey, title, questions, answers) {
  const ai = new GoogleGenAI({ apiKey });
  let usage = assistant.emptyUsage();
  for (let attempt = 0; attempt < 2; attempt++) {
    const r = await ai.models.generateContent({ model: MODEL, contents: quiz.buildGradeContents(title, questions, answers),
      config: { systemInstruction: quiz.SYSTEM, temperature: 0.2, maxOutputTokens: 4000, responseMimeType: "application/json", responseSchema: SCHEMA } });
    usage = assistant.addUsage(usage, assistant.usageFrom(r.usageMetadata));
    const f = quiz.finalizeGrade(r.text, questions);
    if (f.ok) return Object.assign(f, { usage });
  }
  return { ok: false, usage };
}

module.exports = { grade, SCHEMA };
