"use strict";
// 교사용 AI 추천 답변의 모델 호출. index.js(suggestReply)에서만 쓴다.
const { GoogleGenAI, Type } = require("@google/genai");
const { MODEL } = require("./config");
const assistant = require("./assistant");
const ask = require("./askteacher");

const SCHEMA = { type: Type.OBJECT, properties: { draft: { type: Type.STRING }, caution: { type: Type.STRING } }, required: ["draft", "caution"] };

/** msgs 는 오래된 순서의 대화. 반환: {ok, draft, caution, usage}. usage 는 재시도까지 합친 토큰 수. */
async function suggest(apiKey, msgs) {
  const ai = new GoogleGenAI({ apiKey });
  let usage = assistant.emptyUsage();
  for (let attempt = 0; attempt < 2; attempt++) {                                  // 형식이 틀리면 한 번 더 시도한다
    const r = await ai.models.generateContent({ model: MODEL, contents: ask.buildSuggestContents(msgs),
      config: { systemInstruction: ask.SYSTEM, temperature: 0.4, maxOutputTokens: 1500, responseMimeType: "application/json", responseSchema: SCHEMA } });
    usage = assistant.addUsage(usage, assistant.usageFrom(r.usageMetadata));
    const f = ask.finalizeSuggest(r.text);
    if (f.ok) return Object.assign(f, { usage });
  }
  return { ok: false, usage };
}

module.exports = { suggest, SCHEMA };
