"use strict";
/* 돌발 퀴즈 팝업(학생 학습지와 호스팅된 교재 페이지가 함께 쓴다). 채점은 서버(FB.answerQuiz)가 한다.
   필요한 전역: el, ico, $, $$, lsGet, lsSet, FB(fb.js).
   퀴즈 풀(groups)은 [{key, name, items:[{id, chapter, concept, q, options}]}] 이고 정답·풀이는 들어 있지 않다.
   state(답한 퀴즈·미룬 횟수·이미 띄운 즉시 출제·마지막으로 묻은 시각)는 이 브라우저의 localStorage 에 둔다. */
const QuizUI = (() => {
  const COOLDOWN_MS = 10 * 60000;          // 자동 퀴즈는 10분에 한 번까지
  const K = "dp-inquiry-student-quiz";
  let cfg = null, groups = [], getStudent = () => ({}), allowed = () => false, modalOpen = false;

  const empty = () => ({ answered: {}, skipped: {}, seen: {}, last: 0 });
  const load = () => { try { return Object.assign(empty(), JSON.parse(lsGet(K) || "{}")); } catch (e) { return empty(); } };
  const save = st => lsSet(K, JSON.stringify(st));
  const all = () => groups.flatMap(g => g.items.map(q => ({ group: g, quiz: q })));
  const byId = id => all().find(f => f.quiz.id === id) || null;

  function init(o) {
    groups = o.groups || []; getStudent = o.getStudent; allowed = o.allowed;
    FB.watchQuiz(c => { cfg = c || null; showLive(); }).catch(() => {});
  }

  /* 교사가 즉시 출제한 퀴즈: 열 때마다 liveAt 이 새로 찍히므로 (id@liveAt) 단위로 한 번씩만 띄운다. */
  function showLive() {
    const c = cfg; if (modalOpen || !allowed() || !c || !c.liveId) return;
    const key = c.liveId + "@" + (c.liveAt && c.liveAt.toMillis ? c.liveAt.toMillis() : 0), f = byId(c.liveId);
    if (!f || load().seen[key]) return;
    open(f, { kind: "live", key });
  }

  /* 자동 퀴즈: 교재의 한 장을 끝까지 읽거나 학습지의 한 단계를 마친 순간, 교사가 켠 분류에서 안 푼 퀴즈 1개를 낸다.
     chapters: 방금 마친 장 슬러그들, groupKeys: 그 장들의 분류 키. 장에 딸린 퀴즈를 먼저 찾고, 없으면 분류 전체를 묻는 퀴즈(chapter "")를 쓴다. */
  function askAuto(o) {
    if (modalOpen || !allowed() || !cfg) return;
    const on = f => (cfg.auto || {})[f.group.key], st = load();
    if (Date.now() - st.last < COOLDOWN_MS) return;
    const free = f => on(f) && !st.answered[f.quiz.id] && (st.skipped[f.quiz.id] || 0) < 2;
    const pool = all().filter(free);
    const pick = pool.find(f => (o.chapters || []).includes(f.quiz.chapter)) || pool.find(f => !f.quiz.chapter && (o.groupKeys || []).includes(f.group.key));
    if (pick) open(pick, { kind: "auto" });
  }

  function open(f, meta) {
    if (modalOpen) return; modalOpen = true;
    const q = f.quiz, st0 = load(), canDefer = meta.kind === "auto" && !(st0.skipped[q.id] > 0);
    let sel = null, busy = false, finished = false;
    const opts = q.options.map((o, i) => {
      const r = el("input", { type: "radio", name: "qz", value: i, onchange: () => { sel = i; bOk.disabled = false; } });
      return el("label", { class: "qz-opt" }, r, el("span", { html: `${i + 1}. ${o}` }));
    });
    const msg = el("div", { class: "qz-msg", "aria-live": "polite" });
    const bOk = el("button", { class: "qbtn primary", type: "button", disabled: true }, "답 확인");
    const bClose = el("button", { class: "qbtn", type: "button" }, canDefer ? "나중에" : "닫기");
    const panel = el("div", { class: "qz-panel", role: "dialog", "aria-modal": "true", "aria-label": "돌발 퀴즈" },
      el("div", { class: "qz-kicker" }, `돌발 퀴즈 · ${q.concept}`, el("small", {}, " 점수에 들어가지 않아요. 고른 답은 선생님이 수업을 돕는 데만 참고해요. 틀리면 한 번 더 고를 수 있어요.")),
      el("p", { class: "qz-q", html: q.q }), el("div", { class: "qz-opts" }, opts), msg, el("div", { class: "qz-btns" }, bClose, bOk));
    const ov = el("div", { class: "qz-overlay" }, panel);
    const close = () => {
      document.removeEventListener("keydown", onKey); ov.remove(); modalOpen = false;
      const st = load();
      if (finished) st.answered[q.id] = true; else if (meta.kind === "auto") st.skipped[q.id] = (st.skipped[q.id] || 0) + 1;
      if (meta.key) st.seen[meta.key] = true;
      st.last = Date.now(); save(st);
    };
    const onKey = e => { if (e.key === "Escape" && !busy) close(); };
    bClose.addEventListener("click", close);
    bOk.addEventListener("click", async () => {
      if (sel == null || busy) return; busy = true; bOk.disabled = true; msg.className = "qz-msg"; msg.textContent = "채점 중…";
      try {
        const r = await FB.answerQuiz(getStudent(), q.id, sel);
        const labels = $$(".qz-opt", ov);
        if (r.done) {
          finished = true; opts.forEach(l => { $("input", l).disabled = true; });
          labels.forEach((l, i) => l.classList.toggle("right", i === r.answer));
          msg.className = "qz-msg " + (r.correct ? "ok" : "bad");
          msg.replaceChildren(el("b", {}, ico(r.correct ? "check_circle" : "info", "fill"), r.correct ? (r.attempts === 1 ? "정답이에요!" : "정답이에요. 다시 생각해 맞혔네요.") : `아쉬워요. 정답은 ${r.answer + 1}번이에요.`), el("div", { class: "qz-ex", html: r.explain }));
          bOk.hidden = true; bClose.textContent = "닫기"; bClose.focus();
        } else {
          msg.className = "qz-msg bad"; msg.textContent = "아쉬워요. 한 번 더 골라 보세요. 다시 고르고 나면 맞든 틀리든 풀이를 보여 줘요.";
          $$("input", ov).forEach(i => { i.checked = false; }); sel = null;
        }
      } catch (e) {
        msg.className = "qz-msg bad";
        msg.textContent = /permission|denied/i.test(e.code + e.message) ? "이 학번·성명으로는 답할 수 없어요. 학번과 성명을 확인해 주세요."
          : /failed-precondition|precondition/i.test(e.code + e.message) ? "이 퀴즈는 이미 닫혔어요."
          : "채점하지 못했어요. 인터넷 연결을 확인하고 다시 눌러 주세요.";
        if (/precondition/i.test(e.code + e.message)) { bOk.hidden = true; bClose.textContent = "닫기"; }
      }
      busy = false; if (!finished && sel != null) bOk.disabled = false;
    });
    document.addEventListener("keydown", onKey);
    document.body.append(ov); const first = $("input", ov); if (first) first.focus();
  }

  return { init, showLive, askAuto, isOpen: () => modalOpen };
})();
