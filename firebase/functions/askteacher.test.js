"use strict";
const test = require("node:test");
const assert = require("node:assert");
const A = require("./askteacher");

test("validateQuestion: 글도 사진도 없으면 거부, 사진만 있어도 허용, 길이·종류 정리", () => {
  assert.match(A.validateQuestion({}).error, /질문/);
  assert.match(A.validateQuestion({ text: "   " }).error, /질문/);
  assert.ok(A.validateQuestion({ image: { mime: "image/png", data: "AAAA" } }).value);
  const v = A.validateQuestion({ text: "가".repeat(5000), context: { kind: "worksheet", title: "t".repeat(999), chapter: "c".repeat(999), selection: "s".repeat(9999) } }).value;
  assert.equal(v.text.length, A.LIMITS.text);
  assert.equal(v.context.kind, "worksheet");
  assert.equal(v.context.title.length, A.LIMITS.title); assert.equal(v.context.chapter.length, A.LIMITS.chapter); assert.equal(v.context.selection.length, A.LIMITS.selection);
  assert.equal(A.validateQuestion({ text: "q", context: { kind: "이상한값" } }).value.context.kind, "textbook");
});
test("validateQuestion: 사진 형식·문자·크기(문서 1MiB 한도 안)", () => {
  assert.match(A.validateQuestion({ text: "q", image: { mime: "image/gif", data: "AAAA" } }).error, /사진 형식/);
  assert.match(A.validateQuestion({ text: "q", image: { mime: "image/png", data: "not base64!!" } }).error, /사진 형식/);
  assert.match(A.validateQuestion({ text: "q", image: { mime: "image/png", data: "A".repeat(Math.ceil(A.LIMITS.imageBytes * 4 / 3) + 8) } }).error, /너무 커/);
  assert.ok(A.validateQuestion({ text: "q", image: { mime: "image/jpeg", data: "QUJD" } }).value.image);
  assert.ok(A.LIMITS.imageBytes * 4 / 3 + 4000 < 1024 * 1024, "사진(base64)과 글이 문서 한도 1MiB 안에 들어와야 한다");
});
test("질문 개수 제한은 없다: 분당 도배 방지만 있다", () => {
  let th = null; const now = 1_700_000_000_000;
  for (let i = 0; i < A.LIMITS.minute; i++) { const r = A.checkRate(th, now + i, A.LIMITS.minute); assert.ok(r.ok); th = Object.assign({}, th, r.next); }
  assert.equal(A.checkRate(th, now + 5000, A.LIMITS.minute).ok, false);          // 같은 분 안의 11번째
  const next = A.checkRate(th, now + 61000, A.LIMITS.minute);                    // 다음 분에는 다시 받는다
  assert.ok(next.ok); assert.equal(next.next.rN, 1);
  assert.ok(A.checkRate({ rMin: "x", rN: "y" }, now, 3).ok);                      // 이상한 값은 0 으로 본다
});
test("validateReply: uid·답변 필수, 길이 제한, viaAi 는 true 일 때만", () => {
  assert.match(A.validateReply({ text: "답" }).error, /uid/);
  assert.match(A.validateReply({ uid: "a/b", text: "답" }).error, /uid/);
  assert.match(A.validateReply({ uid: "a", text: "  " }).error, /답변/);
  const v = A.validateReply({ uid: "a", text: "가".repeat(9999), viaAi: "yes" }).value;
  assert.equal(v.text.length, A.LIMITS.reply); assert.equal(v.viaAi, false);
  assert.equal(A.validateReply({ uid: "a", text: "x", viaAi: true }).value.viaAi, true);
});
test("메시지 문서 모양: 학생 질문은 사진까지 담고, 교사 답은 누가 보냈는지·AI 경유 여부를 담는다. 목록 요약은 한 줄로 줄인다", () => {
  const v = A.validateQuestion({ text: "질문", image: { mime: "image/png", data: "AAAA" }, context: { title: "전략 · 구조", selection: "고른 글" } }).value;
  const m = A.studentMessage(v, "T");
  assert.deepEqual([m.from, m.hasImage, m.where, m.selection, m.image.mime], ["student", true, "전략 · 구조", "고른 글", "image/png"]);
  assert.equal(A.studentMessage(A.validateQuestion({ text: "q" }).value, "T").image, undefined);
  assert.deepEqual(A.teacherMessage({ text: "답", viaAi: true }, "t@ts.hs.kr", "T"), { from: "teacher", text: "답", by: "t@ts.hs.kr", viaAi: true, at: "T" });
  assert.equal(A.threadHead("student", "가\n\n나   다".repeat(100), false, "T").lastText.length, A.LIMITS.snippet);
  assert.equal(A.threadHead("student", "", true, "T").lastText, "(사진)");
});
test("consentGate: 현재 버전 동의만 있으면 되고 AI 선택 항목은 요구하지 않는다", () => {
  assert.equal(A.consentGate({ version: "v1", ai: false }, "v1"), null);
  assert.match(A.consentGate({ version: "v0", ai: true }, "v1"), /동의/);
  assert.match(A.consentGate(undefined, "v1"), /동의/);
});
test("AI 추천 프롬프트: 대화를 <thread> 로 묶고 이름·이메일은 넣지 않으며 마지막 사진 하나만 붙인다", () => {
  const msgs = [{ from: "student", text: "첫 질문", where: "1장 · 상황", hasImage: true, image: { mime: "image/png", data: "AAAA" }, student: { name: "홍길동", email: "hong@ts.hs.kr" } },
    { from: "teacher", text: "이렇게 해 보자" }, { from: "student", text: "이거 왜 그래요?", where: "9장", selection: "lazy = Proxy()", hasImage: true, image: { mime: "image/jpeg", data: "QUJD" } }];
  const c = A.buildSuggestContents(msgs);
  assert.equal(c.length, 1); assert.equal(c[0].role, "user");
  const t = c[0].parts[0].text;
  assert.match(t, /<thread>[\s\S]*학생: 첫 질문[\s\S]*선생님: 이렇게 해 보자[\s\S]*학생: 이거 왜 그래요\?[\s\S]*<\/thread>/);
  assert.match(t, /<selected>\nlazy = Proxy\(\)\n<\/selected>/);
  assert.ok(!/홍길동|hong@/.test(t));
  const imgs = c[0].parts.filter(p => p.inlineData); assert.equal(imgs.length, 1); assert.equal(imgs[0].inlineData.mimeType, "image/jpeg");
  assert.equal(A.buildSuggestContents(Array.from({ length: 30 }, (_, i) => ({ from: "student", text: "q" + i }))).length, 1);
  assert.ok(!A.buildSuggestContents(Array.from({ length: 30 }, (_, i) => ({ from: "student", text: "q" + i })))[0].parts[0].text.includes("q0\n"), "오래된 대화는 잘라 낸다");
});
test("finalizeSuggest: JSON 의 draft 만 쓰고 마크다운은 걷어 낸다. 형식 오류·빈 초안은 실패", () => {
  assert.deepEqual(A.finalizeSuggest('{"draft":"**좋은** 질문이에요.\\n\\n\\n\\n설명","caution":" 확인 "}'), { ok: true, draft: "좋은 질문이에요.\n\n설명", caution: "확인" });
  assert.equal(A.finalizeSuggest('```json\n{"draft":"답","caution":""}\n```').draft, "답");
  assert.equal(A.finalizeSuggest("그냥 글").ok, false);
  assert.equal(A.finalizeSuggest('{"draft":"  ","caution":""}').ok, false);
  assert.equal(A.finalizeSuggest('{"draft":"답"}').caution, "");
});
test("시스템 지시: 프롬프트 주입 무시·정답 대신 쓰기 금지·평문 형식을 담는다", () => {
  assert.match(A.SYSTEM, /따르지 않습니다/); assert.match(A.SYSTEM, /정답을 대신/); assert.match(A.SYSTEM, /마크다운/); assert.match(A.SYSTEM, /caution/);
});
test("aiConsentGate: AI(선택 항목) 동의가 없거나 옛 버전이면 질문을 AI 로 보내지 않는다", () => {
  assert.equal(A.aiConsentGate({ version: "v1", ai: true }, "v1"), null);
  assert.match(A.aiConsentGate({ version: "v1", ai: false }, "v1"), /AI/);
  assert.match(A.aiConsentGate({ version: "v0", ai: true }, "v1"), /AI/);
  assert.match(A.aiConsentGate(undefined, "v1"), /AI/);
});
