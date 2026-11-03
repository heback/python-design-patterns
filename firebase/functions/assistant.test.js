"use strict";
const test = require("node:test");
const assert = require("node:assert");
const { validate, buildContents, checkLimit, cleanReply, finalize, REFUSAL, SYSTEM, LIMITS } = require("./assistant");

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

test("finalize: 범위 안이면 모델의 답을, 범위 밖이면 모델의 reply 를 버리고 정해진 안내문만", () => {
  const ok = finalize(JSON.stringify({ onTopic: true, reply: "## 전략\n**알고리즘**을 갈아 끼웁니다." }));
  assert.deepEqual(ok, { ok: true, reply: "전략\n알고리즘을 갈아 끼웁니다.", refused: false });
  // 범위 밖: 모델이 reply 에 무엇을 써 두었든(심지어 범위 밖 내용이 길게 있어도) 학생에게는 안내문만 나간다
  const off = finalize(JSON.stringify({ onTopic: false, reply: "이차방정식의 근은 x = (-b ± √(b²-4ac)) / 2a 입니다. 오늘 급식은..." }));
  assert.deepEqual(off, { ok: true, reply: REFUSAL, refused: true });
  assert.ok(!off.reply.includes("이차방정식"));
});
test("finalize: onTopic 이 true 가 아니면(없음·문자열·null) 모두 거절로 처리, 형식이 깨졌으면 실패", () => {
  for (const bad of [{ reply: "답" }, { onTopic: "true", reply: "답" }, { onTopic: null, reply: "답" }, { onTopic: 1, reply: "답" }])
    assert.equal(finalize(JSON.stringify(bad)).refused === true || finalize(JSON.stringify(bad)).ok === false, true, JSON.stringify(bad));
  assert.equal(finalize("그냥 글입니다").ok, false);
  assert.equal(finalize("").ok, false);
  assert.equal(finalize(JSON.stringify({ onTopic: true, reply: "   " })).ok, false);            // 빈 답
  assert.deepEqual(finalize("```json\n" + JSON.stringify({ onTopic: true, reply: "코드블록으로 감싼 JSON" }) + "\n```"), { ok: true, reply: "코드블록으로 감싼 JSON", refused: false });
});
test("시스템 프롬프트: 허용 범위 세 가지와 범위 밖 예시, 주입 방어가 명시돼 있다", () => {
  for (const w of ["파이썬", "객체지향프로그래밍", "디자인 패턴", "onTopic", "이전 지시를 무시해", "다른 과목", "사진이 범위 밖"]) assert.ok(SYSTEM.includes(w), w);
});
