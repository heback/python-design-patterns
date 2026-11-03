"use strict";
const test = require("node:test");
const assert = require("node:assert");
const { validate, buildContents, checkLimit, cleanReply, LIMITS } = require("./assistant");

test("validate: 질문도 사진도 없으면 거부, 사진만 있으면 허용", () => {
  assert.match(validate({}).error, /질문/);
  assert.match(validate({ question: "   " }).error, /질문/);
  const r = validate({ image: { mime: "image/png", data: "AAAA" } });
  assert.ok(r.value && r.value.image && r.value.question.includes("사진"));
});
test("validate: 사진 형식·크기·문자 검사", () => {
  assert.match(validate({ question: "q", image: { mime: "image/gif", data: "AAAA" } }).error, /사진 형식/);
  assert.match(validate({ question: "q", image: { mime: "image/png", data: "not base64!!" } }).error, /사진 형식/);
  assert.match(validate({ question: "q", image: { mime: "image/png", data: "A".repeat(Math.ceil(LIMITS.imageBytes * 4 / 3) + 8) } }).error, /너무 커/);
  assert.ok(validate({ question: "q", image: { mime: "image/jpeg", data: "QUJD" } }).value);
});
test("validate: 길이 제한과 맥락 정리, 대화는 학생 발화로 시작", () => {
  const v = validate({ question: "가".repeat(5000), context: { kind: "worksheet", title: "t".repeat(999), text: "x".repeat(99999), selection: "s".repeat(9999) },
    history: [{ role: "model", text: "앞의 답" }, { role: "user", text: "질문1" }, { role: "model", text: "답1" }, { role: "system", text: "무시" }, { role: "user", text: "" }] }).value;
  assert.equal(v.question.length, LIMITS.question);
  assert.equal(v.context.kind, "worksheet");
  assert.equal(v.context.title.length, LIMITS.ctxTitle); assert.equal(v.context.text.length, LIMITS.ctxText); assert.equal(v.context.selection.length, LIMITS.ctxSel);
  assert.deepEqual(v.history.map(h => h.role), ["user", "model"]);
  assert.equal(validate({ question: "q", context: { kind: "이상한값" } }).value.context.kind, "textbook");
});
test("buildContents: 맥락은 마지막 학생 발화에 붙고 사진은 inlineData", () => {
  const v = validate({ question: "이게 뭐야?", image: { mime: "image/png", data: "AAAA" }, context: { kind: "textbook", title: "전략", text: "전략 패턴 본문", selection: "선택한 문장" },
    history: [{ role: "user", text: "이전 질문" }, { role: "model", text: "이전 답" }] }).value;
  const c = buildContents(v);
  assert.equal(c.length, 3); assert.equal(c[2].role, "user");
  assert.match(c[2].parts[0].text, /<screen>\n전략 패턴 본문\n<\/screen>/); assert.match(c[2].parts[0].text, /<selected>\n선택한 문장\n<\/selected>/);
  assert.match(c[2].parts[0].text, /\[학생 질문\]\n이게 뭐야\?/);
  assert.deepEqual(c[2].parts[1], { inlineData: { mimeType: "image/png", data: "AAAA" } });
});
test("checkLimit: 분당·일일 한도, 날짜가 바뀌면 초기화", () => {
  const L = { daily: 3, minute: 2 }, t0 = Date.UTC(2026, 10, 3, 1, 0, 0);
  let r = checkLimit(null, t0, L); assert.ok(r.ok); assert.equal(r.next.count, 1);
  r = checkLimit(r.next, t0 + 1000, L); assert.ok(r.ok);
  const blocked = checkLimit(r.next, t0 + 2000, L); assert.equal(blocked.ok, false); assert.equal(blocked.reason, "minute");
  const later = checkLimit(r.next, t0 + 61000, L); assert.ok(later.ok); assert.equal(later.next.count, 3);
  assert.equal(checkLimit(later.next, t0 + 130000, L).reason, "daily");
  const nextDay = checkLimit(later.next, t0 + 24 * 3600e3, L); assert.ok(nextDay.ok); assert.equal(nextDay.next.count, 1);
});
test("cleanReply: 마크다운 기호 제거", () => {
  assert.equal(cleanReply("## 제목\n**중요** 내용\n```python\nx = 1\n```"), "제목\n중요 내용\nx = 1");
  assert.equal(cleanReply(null), "");
});
