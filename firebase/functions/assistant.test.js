"use strict";
const test = require("node:test");
const assert = require("node:assert");
const { consentGate, validate, buildContents, checkLimit, chapterKey, limitFor, cleanReply, finalize, REFUSAL, SYSTEM, LIMITS } = require("./assistant");

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
  assert.equal(validate({ question: "q", context: { chapter: " 05-singleton " } }).value.context.chapter, "05-singleton");
  assert.equal(validate({ question: "q", context: { chapter: "c".repeat(500) } }).value.context.chapter.length, LIMITS.ctxChapter);
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
test("chapterKey: 서버가 아는 장만 인정하고 그 밖의 값은 모두 etc 한 칸으로 모은다(키를 바꿔 한도를 피할 수 없다)", () => {
  const allowed = new Set(["05-singleton", "week1", "etc"]);
  assert.equal(chapterKey("05-singleton", allowed), "05-singleton"); assert.equal(chapterKey("week1", allowed), "week1");
  for (const bad of ["99-fake", "", undefined, null, 5, "../x", "05-singleton ", {}]) assert.equal(chapterKey(bad, allowed), "etc", String(bad));
  assert.equal(chapterKey("05-singleton", new Set()), "etc");
});
test("limitFor: 기본 40 + 모든 장 가감 + 그 장 가감, 0 아래로는 내려가지 않고 이상한 값은 무시", () => {
  const D = 40, MAX = 1000, f = (b, q, k) => limitFor(b, q, k, D, MAX);
  assert.equal(f(undefined, null, "a"), 40); assert.equal(f(25, null, "a"), 25);          // 교사가 기본값을 바꾸면 그 값
  assert.equal(f(undefined, { all: 10 }, "a"), 50); assert.equal(f(undefined, { chapters: { a: -15 } }, "a"), 25);
  assert.equal(f(undefined, { all: 10, chapters: { a: -15 } }, "a"), 35);
  assert.equal(f(undefined, { all: 10, chapters: { a: -15 } }, "b"), 50);                 // 다른 장에는 그 장 가감이 적용되지 않는다
  assert.equal(f(undefined, { all: -100 }, "a"), 0);                                       // 음수로 내려가지 않는다
  assert.equal(f(0, null, "a"), 0);                                                        // 기본 0 = 쓰지 못하게 막기
  assert.equal(f("abc", { all: "x", chapters: { a: 1.5 } }, "a"), 40);                    // 잘못된 값은 무시하고 기본값
  assert.equal(f(99999, null, "a"), 40);                                                   // 상한을 넘는 기본값도 무시
});
test("checkLimit: 장별로 따로 세고, 한도에서 막히며, 분당 한도는 따로 적용", () => {
  const t0 = Date.UTC(2026, 10, 3, 1, 0, 0), L = (key, chapter) => ({ minute: 2, chapter, key });
  let r = checkLimit(null, t0, L("a", 3)); assert.ok(r.ok); assert.equal(r.used, 1); assert.equal(r.limit, 3);
  assert.deepEqual(r.next.chapters, { a: 1 });
  let u = { chapters: { a: 1 }, minute: r.next.minute, minuteCount: 1 };
  r = checkLimit(u, t0 + 1000, L("a", 3)); assert.ok(r.ok); assert.equal(r.used, 2);
  u = { chapters: { a: 2 }, minute: r.next.minute, minuteCount: 2 };
  const blocked = checkLimit(u, t0 + 2000, L("a", 3)); assert.equal(blocked.ok, false); assert.equal(blocked.reason, "minute");
  const later = checkLimit(u, t0 + 61000, L("a", 3)); assert.ok(later.ok); assert.equal(later.used, 3);      // 1분 뒤 가능
  const full = checkLimit({ chapters: { a: 3 } }, t0 + 130000, L("a", 3)); assert.equal(full.ok, false); assert.equal(full.reason, "chapter"); assert.equal(full.used, 3);
  const other = checkLimit({ chapters: { a: 3 } }, t0 + 130000, L("b", 3)); assert.ok(other.ok); assert.equal(other.used, 1);      // 다른 장은 새로 센다
  assert.equal(checkLimit({ chapters: { a: 3 } }, t0, L("a", 4)).ok, true);                // 교사가 한도를 올리면 바로 다시 쓸 수 있다
  assert.equal(checkLimit({ chapters: { a: 3 } }, t0, L("a", 2)).reason, "chapter");       // 한도를 사용량보다 낮춰도 막힌다(이미 쓴 것은 그대로)
  assert.equal(checkLimit(null, t0, L("a", 0)).reason, "chapter");                          // 한도 0
  const next = checkLimit({ chapters: { a: 1 } }, t0, L("b", 3)).next; assert.deepEqual(next.chapters, { b: 1 });      // merge 로 쓰므로 다른 장 횟수를 건드리지 않는다
  assert.equal(checkLimit({ day: "2026-11-03", count: 40 }, t0, L("a", 3)).ok, true);        // 예전 '하루 횟수' 필드는 더 이상 한도에 쓰이지 않는다
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

test("usageFrom·addUsage: Gemini usageMetadata 를 토큰 수로 바꾸고 합친다", () => {
  const { usageFrom, addUsage, emptyUsage, logEntry } = require("./assistant");
  assert.deepEqual(usageFrom({ promptTokenCount: 120, candidatesTokenCount: 30, thoughtsTokenCount: 10, totalTokenCount: 160 }), { prompt: 120, output: 30, thoughts: 10, total: 160 });
  assert.deepEqual(usageFrom({ promptTokenCount: 5, candidatesTokenCount: 2 }), { prompt: 5, output: 2, thoughts: 0, total: 7 });     // total 이 없으면 합
  assert.deepEqual(usageFrom(undefined), emptyUsage()); assert.deepEqual(usageFrom({ promptTokenCount: -3, candidatesTokenCount: "x" }), emptyUsage());
  assert.deepEqual(addUsage({ prompt: 1, output: 2, thoughts: 3, total: 6 }, { prompt: 10, output: 20, thoughts: 30, total: 60 }), { prompt: 11, output: 22, thoughts: 33, total: 66 });
  const e = logEntry({ uid: "u", student: { name: "김", email: "a@ts.hs.kr" }, kind: "worksheet", where: "t".repeat(500), v: { question: "질문", image: { data: "A".repeat(400) } }, reply: "답", refused: false, usage: usageFrom({ totalTokenCount: 9 }), ms: 123.7, model: "m", at: 1, day: "2026-11-03" });
  assert.equal(e.hasImage, true); assert.equal(e.imageBytes, 300); assert.equal(e.where.length, 200); assert.equal(e.ms, 124); assert.equal(e.kind, "worksheet");
  assert.ok(!("image" in e) && !JSON.stringify(e).includes("AAAA"), "사진 자체는 기록에 없어야 한다");
  assert.equal(e.failed, false); assert.equal(logEntry({ uid: "u", student: {}, v: { question: "q" }, error: "boom", at: 1, day: "d" }).failed, true);      // 오류만 걸러 보는 쿼리용
});

test("consentGate: 현재 버전 + AI 선택 항목에 동의해야 통과", () => {
  assert.equal(consentGate({ version: "v1", ai: true }, "v1"), null);
  assert.match(consentGate(undefined, "v1"), /동의가 필요/);                 // 동의한 적 없음
  assert.match(consentGate({ version: "v0", ai: true }, "v1"), /동의가 필요/);   // 옛 문구에 동의 → 다시 동의
  assert.match(consentGate({ version: "v1", ai: false }, "v1"), /AI 도우미 이용/);    // 필수만 동의
  assert.match(consentGate({ version: "v1" }, "v1"), /AI 도우미 이용/);
});
test("동의 문구 버전: 규칙·함수·학생 화면 세 곳이 같다", () => {
  const fs = require("node:fs"), path = require("node:path"), { CONSENT_VERSION } = require("./config");
  const rules = /consentVersion\(\) \{ return '([^']+)'/.exec(fs.readFileSync(path.join(__dirname, "../firestore.rules"), "utf8"));
  const ui = /VERSION = "([^"]+)"/.exec(fs.readFileSync(path.join(__dirname, "../../inquiry/templates/student-auth.js"), "utf8"));
  assert.ok(rules && ui, "버전 상수를 찾지 못했다");
  assert.equal(rules[1], CONSENT_VERSION); assert.equal(ui[1], CONSENT_VERSION);
});
