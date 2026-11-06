"use strict";
/* 교재 사본(Firebase 호스팅) 전용: 돌발 퀴즈 팝업과 피드백 팝업.
   - 교사가 [제시]하면(config/quiz) 그 패턴의 장(요약 판·긴 버전 모두)을 보고 있는 학생 화면에 팝업이 뜬다. 다른 장을 보던 학생은 그 장으로 가면 남은 시간만큼 뜬다.
   - 학생은 제한 시간 안에 서술형으로 답한다. 시간 안에는 고쳐서 다시 제출할 수 있고, 시간이 끝나면 쓴 글이 자동 제출된다. 남은 시간은 서버 시각(quizNow)에 맞춘다.
   - 교사가 채점 결과를 보내면(quizResults) 어느 장에서든 피드백 팝업이 한 번 뜬다. 필요한 전역: el, ico, FB(fb.js), StudentAuth(student-auth.js), 빌드가 넣는 TB_DATA = {chapters}. */
const QuizUI = (() => {
  const SLUG = (location.pathname.split("/").pop() || "").replace(/\.html$/, "").replace(/-full$/, "");
  const DRAFT = sid => "dp-quiz-draft:" + sid, SEEN = "dp-quiz-seen";
  let cfg = null, offset = 0, offsetFor = "", uid = null, unCfg = null, unRes = null, results = [], quiz = null, fb = null, tick = null;
  const store = { get: k => { try { return localStorage.getItem(k); } catch (e) { return null; } }, set: (k, v) => { try { localStorage.setItem(k, v); } catch (e) {} } };
  const now = () => Date.now() + offset;
  const seenIds = () => { try { return new Set(JSON.parse(store.get(SEEN) || "[]")); } catch (e) { return new Set(); } };
  const markSeen = id => { const s = seenIds(); s.add(id); store.set(SEEN, JSON.stringify([...s].slice(-50))); };
  const mmss = ms => { const s = Math.max(0, Math.ceil(ms / 1000)); return Math.floor(s / 60) + ":" + String(s % 60).padStart(2, "0"); };
  const msg = e => { const c = String(e.code || ""), m = String(e.message || ""); return /failed-precondition/.test(c) ? m.replace(/^.*?: /, "") || "제출 시간이 끝났어요." : /invalid-argument/.test(c) ? m.replace(/^.*?: /, "") : "제출하지 못했어요. 인터넷 연결을 확인하고 다시 눌러 주세요."; };

  /* ---------- 퀴즈 팝업 ---------- */
  function closeQuiz() { if (quiz) { quiz.ov.remove(); document.body.classList.remove("qz-lock"); if (quiz.pill) quiz.pill.remove(); quiz = null; } }
  function openQuiz(c) {
    if (quiz && quiz.sid === c.sid) return;
    closeQuiz();
    const sid = c.sid, saved = (() => { try { return JSON.parse(store.get(DRAFT(sid)) || "{}"); } catch (e) { return {}; } })();
    const tas = {}, status = el("div", { class: "qz-status", role: "status" }), timeEl = el("span", { class: "qz-time" }), bar = el("div", { class: "qz-bar" }, el("i"));
    const state = { submitted: !!saved.__done, dirty: false, final: false, busy: false };
    const body = el("div", { class: "qz-body" }, c.questions.map((q, i) => {
      const ta = el("textarea", { class: "qz-ta", rows: 4, maxlength: 1500, spellcheck: "false", placeholder: "여기에 답을 써요. 아는 만큼 자기 말로 써도 좋아요.", "aria-label": `${i + 1}번 답` }); ta.value = saved[q.id] || "";
      ta.addEventListener("input", () => { state.dirty = true; persist(); fit(ta); });
      tas[q.id] = ta;
      return el("section", { class: "qz-q" }, el("div", { class: "qz-qt" }, el("b", {}, `${i + 1}.`), " ", q.q), ta);
    }));
    const fit = ta => { ta.style.height = "auto"; ta.style.height = Math.min(ta.scrollHeight + 2, 320) + "px"; };
    const answers = () => Object.fromEntries(c.questions.map(q => [q.id, tas[q.id].value.trim()]));
    const hasAny = () => Object.values(answers()).some(Boolean);
    const persist = () => store.set(DRAFT(sid), JSON.stringify(Object.assign({}, answers(), state.submitted ? { __done: 1 } : {})));
    const bSubmit = el("button", { type: "button", class: "qbtn primary" }, ico("send"), "제출하기"), bFold = el("button", { type: "button", class: "qbtn", hidden: true }, "접기"), bClose = el("button", { type: "button", class: "qbtn primary", hidden: true }, "닫기");
    async function submit(final) {
      if (state.busy) return;
      if (!hasAny()) { if (!final) status.textContent = "답을 하나 이상 써 주세요."; return; }
      state.busy = true; bSubmit.disabled = true; status.textContent = "제출하는 중…";
      try { await FB.submitQuiz(sid, answers()); state.submitted = true; state.dirty = false; persist();
        status.textContent = final ? "" : "제출했어요! 시간이 남았으니 고쳐서 [다시 제출]해도 돼요."; bSubmit.lastChild.textContent = "다시 제출"; bFold.hidden = false; }
      catch (e) { status.textContent = msg(e); }
      state.busy = false; bSubmit.disabled = state.final;
    }
    bSubmit.addEventListener("click", () => submit(false));
    bFold.addEventListener("click", () => { quiz.ov.hidden = true; document.body.classList.remove("qz-lock"); quiz.pill.hidden = false; });
    bClose.addEventListener("click", closeQuiz);
    const box = el("div", { class: "qz-box", role: "dialog", "aria-modal": "true", "aria-labelledby": "qz-title" },
      el("div", { class: "qz-head" }, el("h3", { id: "qz-title" }, ico("quiz", "fill"), `돌발 퀴즈 · ${c.title}`), el("span", { class: "qz-grow" }), el("span", { class: "qz-timewrap" }, ico("timer"), timeEl)), bar,
      el("p", { class: "qz-note" }, "배운 내용을 자기 말로 써 보세요. 모르는 것은 아는 데까지만 써도 괜찮아요. 시간이 끝나면 쓴 글이 자동으로 제출돼요. 쓴 글은 선생님이 보고, AI 채점에 쓰일 수 있어요."),
      body, status, el("div", { class: "qz-btns" }, bSubmit, bFold, el("span", { class: "qz-grow" }), bClose));
    const ov = el("div", { class: "qz-overlay" }, box), pill = el("button", { type: "button", class: "qz-pill", hidden: true, onclick: () => { ov.hidden = false; pill.hidden = true; document.body.classList.add("qz-lock"); } }, ico("quiz", "fill"), "돌발 퀴즈 열기 ", el("b", {}));
    document.body.append(ov, pill); document.body.classList.add("qz-lock");
    quiz = { sid, ov, pill, tas, state, tickUI() {
      const left = c.endsAt - now(), total = c.seconds * 1000;
      timeEl.textContent = mmss(left); bar.firstChild.style.width = Math.max(0, Math.min(100, 100 * left / total)) + "%"; box.classList.toggle("qz-warn", left <= 60000);
      pill.lastChild.textContent = mmss(left);
      if (left <= 0 && !state.final) finish();
    } };
    Object.values(tas).forEach(fit); (Object.values(tas)[0] || {}).focus && Object.values(tas)[0].focus();
    if (state.submitted) { bSubmit.lastChild.textContent = "다시 제출"; bFold.hidden = false; }
    /* 시간이 끝났다: 아직 안 낸 글이 있으면 자동 제출하고 잠근다 */
    async function finish() {
      state.final = true; Object.values(tas).forEach(t => { t.readOnly = true; }); bSubmit.hidden = true; bFold.hidden = true; ov.hidden = false; pill.hidden = true; document.body.classList.add("qz-lock");
      if (state.dirty || !state.submitted) await submit(true);
      status.textContent = state.submitted ? "시간이 끝났어요. 제출 완료! 선생님이 채점해서 피드백을 보내면 알려 드릴게요." : "시간이 끝났어요. 쓴 답이 없어 제출하지 않았어요.";
      bClose.hidden = false; box.classList.remove("qz-warn");
    }
    quiz.finish = finish;
  }

  /* ---------- 피드백 팝업 ---------- */
  function closeFb() { if (fb) { fb.remove(); fb = null; } }
  const pips = (n, max) => el("span", { class: "qz-pips", title: `${n}/${max}점`, "aria-label": `${n}점 / ${max}점` }, Array.from({ length: max }, (_, i) => el("i", { class: i < n ? "on" : "" })));
  function showFeedback(r) {
    if (fb) return;
    const max = 3;
    const bOk = el("button", { type: "button", class: "qbtn primary" }, ico("check"), "확인했어요");
    bOk.addEventListener("click", () => { markSeen(r.id); closeFb(); next(); });
    const box = el("div", { class: "qz-box qz-fb", role: "dialog", "aria-modal": "true", "aria-labelledby": "qz-fb-title" },
      el("div", { class: "qz-head" }, el("h3", { id: "qz-fb-title" }, ico("rate_review", "fill"), `돌발 퀴즈 피드백 · ${r.title}`)),
      el("div", { class: "qz-score" }, el("b", {}, `총점 ${r.total} / ${r.max}`)),
      r.summary ? el("p", { class: "qz-sum" }, r.summary) : null,
      el("div", { class: "qz-body" }, r.items.map((x, i) => el("section", { class: "qz-q" }, el("div", { class: "qz-qt" }, el("b", {}, `${i + 1}.`), " ", x.q, pips(x.score, max)), x.feedback ? el("div", { class: "qz-fbtxt" }, x.feedback) : null))),
      el("div", { class: "qz-btns" }, el("span", { class: "qz-grow" }), bOk));
    fb = el("div", { class: "qz-overlay" }, box); document.body.append(fb); bOk.focus();
  }
  /* 아직 안 본 결과가 있고 퀴즈를 풀고 있지 않으면 하나씩 보인다 */
  function next() {
    if (fb || (quiz && !quiz.state.final)) return;
    const seen = seenIds(), r = results.filter(x => !seen.has(x.id)).sort((a, b) => ((a.releasedAt && a.releasedAt.toMillis ? a.releasedAt.toMillis() : 0) - (b.releasedAt && b.releasedAt.toMillis ? b.releasedAt.toMillis() : 0)))[0];
    if (r) showFeedback(r);
  }

  /* ---------- 서버와 연결 ---------- */
  async function syncClock(c) {
    if (offsetFor === c.sid) return; offsetFor = c.sid;
    try { const t0 = Date.now(), r = await FB.quizNow(), t1 = Date.now(); offset = r.now - (t0 + t1) / 2; } catch (e) { offset = 0; }
    update();
  }
  function update() {
    const c = cfg;
    if (c && c.state === "open" && c.slug === SLUG && c.endsAt > now()) openQuiz(c);
    else if (quiz && c && quiz.sid === c.sid && !quiz.state.final) quiz.finish();       // 시간이 끝났거나 교사가 마감했다
    next();
  }
  function stop() { [unCfg, unRes].forEach(f => { try { f && f(); } catch (e) {} }); unCfg = unRes = null; cfg = null; results = []; closeQuiz(); closeFb(); }
  function syncUser() {
    const u = StudentAuth.get(), nextUid = u ? u.uid : null;
    if (nextUid === uid) return; stop(); uid = nextUid; if (!uid) return;
    const me = uid;
    FB.watchQuiz(c => { if (uid !== me) return; cfg = c || null; if (cfg && cfg.state === "open") syncClock(cfg); update(); }).then(f => { if (uid === me && !unCfg) unCfg = f; else f(); }).catch(() => {});
    FB.watchMyQuizResults(me, rows => { if (uid !== me || !rows) return; results = rows; next(); }).then(f => { if (uid === me && !unRes) unRes = f; else f(); }).catch(() => {});
  }
  function init() {
    if (typeof FB === "undefined" || typeof StudentAuth === "undefined") return;
    tick = setInterval(() => { if (quiz) quiz.tickUI(); else if (cfg && cfg.state === "open" && cfg.slug === SLUG) update(); }, 500);
    StudentAuth.onChange(syncUser); syncUser();
  }
  return { init };
})();
QuizUI.init();
