"use strict";
// 학생 AI 도우미의 모델 호출. index.js(askAssistant)와 scripts/check-assistant-scope.js 가 같은 경로를 쓴다.
const { GoogleGenAI, Type } = require("@google/genai");
const { ASSISTANT_MODEL, ASSISTANT_MAX_TOKENS } = require("./config");
const assistant = require("./assistant");

const SCHEMA = { type: Type.OBJECT, properties: { onTopic: { type: Type.BOOLEAN }, reply: { type: Type.STRING } }, required: ["onTopic", "reply"] };

/** v 는 assistant.validate 의 value. 반환: {ok, reply, refused, usage}. usage 는 재시도까지 합친 토큰 수. */
async function answer(apiKey, v) {
  const ai = new GoogleGenAI({ apiKey });
  let usage = assistant.emptyUsage();
  for (let attempt = 0; attempt < 2; attempt++) {                                  // 형식이 틀리면 한 번 더 시도한다
    const r = await ai.models.generateContent({ model: ASSISTANT_MODEL, contents: assistant.buildContents(v),
      config: { systemInstruction: assistant.SYSTEM, temperature: 0.3, maxOutputTokens: ASSISTANT_MAX_TOKENS,
        responseMimeType: "application/json", responseSchema: SCHEMA } });
    usage = assistant.addUsage(usage, assistant.usageFrom(r.usageMetadata));       // 실패한 시도도 토큰은 쓴 것이므로 센다
    const f = assistant.finalize(r.text);
    if (f.ok) return Object.assign(f, { usage });
  }
  return { ok: false, usage };
}

module.exports = { answer, SCHEMA };
