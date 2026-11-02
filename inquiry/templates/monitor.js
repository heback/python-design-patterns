"use strict";
/* 학생용: 진도 자동 전달과 돌발 퀴즈. 교사가 [진도 수집]을 켜 두었을 때만 동작하고, 켜져 있는 동안은 화면 위쪽에 항상 고지한다.
   전달하는 것: 학번·성명, 주차별 완료 문항 수·ID, 마지막으로 만진 문항, 활동 시간(화면이 보이고 최근 60초 안에 입력·스크롤·클릭이 있던 시간), 마지막 활동 시각.
   퀴즈를 풀면 고른 답과 시도 횟수가 서버(answerQuiz)에 기록된다. 학생 고지 줄(updateBar)은 이 목록과 항상 같게 유지한다.
   전달하지 않는 것: 쓴 글의 내용(서버로 보내지 않는다. 브라우저에만 저장된다), 키 입력, 화면, 탭 전환.
   student.js 보다 먼저 실려서, 전역 S·CONTENT·LS_KEY 는 함수가 실제로 불릴 때 읽는다. */
const Mon = (() => {
  const IDLE_MS = 60000, BEAT_MS = 60000, MIN_GAP_MS = 10000, AUTO_COOLDOWN_MS = 10 * 60000;
  let monOn = false, quizCfg = null, ready = false, sending = false, barState = "";
  let lastSentAt = 0, lastSig = "", lastInput = 0, lastActiveAt = 0, lastTick = Date.now(), tickCount = 0;
  let activeMs = 0, modalOpen = false, doneStages = null, started = false, idKey = "", idSince = 0;
  const lastByWeek = {};
  const K_AMS = () => LS_KEY + "-activeMs", K_QZ = () => LS_KEY + "-quiz";
  const hasId = () => !!(S.student.number || "").trim() && !!(S.student.name || "").trim();
  const ID_SETTLE_MS = 4000;     // 학번·성명을 한 글자씩 치는 중간 값으로 진도 문서가 여러 개 생기지 않도록, 입력이 멈춘 뒤에 보낸다
  const wkOf = id => { const m = /^w(\d+)-/.exec(id); return m ? Number(m[1]) : 0; };

  /* ---------- 고지 줄 ---------- */
  function updateBar() {
    const b = $("#monbar"); if (!b) return;
    const show = typeof FB !== "undefined" && monOn; b.hidden = !show; if (!show) return;
    b.className = "monbar" + (barState === "err" ? " err" : "");
    const st = !hasId() ? " 학번과 성명을 입력하면 시작돼요."
      : barState === "err" ? "지금은 전달하지 못했어요(인터넷 연결이나 학번·성명을 확인해 주세요. 공부에는 영향이 없어요)."
      : lastSentAt ? "전달됨 " + stamp(new Date(lastSentAt)) : "";
    const stIco = barState === "err" ? ico("warning") : lastSentAt && hasId() ? ico("check_circle", "fill") : null;
    b.replaceChildren(ico("cell_tower"), el("b", {}, "진행 상황이 선생님께 자동으로 전달돼요. "),
      "어느 문항을 마쳤는지·지금 어느 문항을 하고 있는지·마지막 활동 시각·활동 시간(입력이나 스크롤이 있던 시간)이 학번·성명과 함께 전달되고, 돌발 퀴즈에서 고른 답도 기록돼요. "
      + "쓴 글의 내용과 키 입력, 화면은 보내지 않아요.", el("span", { class: "monst" }, stIco, st));
  }

  /* ---------- 진도 ---------- */
  function snapshot() {
    const weeks = {};
    CONTENT.weeks.forEach(w => {
      const ids = []; let total = 0;
      for (const st of w.stages) for (const it of st.items) if (ANSWERABLE(it) && !it.optional) { total++; if (isAnswered(it, S.answers[it.id])) ids.push(it.id); }
      if (ids.length) weeks[w.n] = { n: ids.length, total, ids, last: lastByWeek[w.n] || ids[ids.length - 1] };
    });
    return weeks;
  }
  async function send(force) {
    if (!monOn || !hasId() || typeof FB === "undefined" || sending || Date.now() - idSince < ID_SETTLE_MS) return;
    const weeks = snapshot(), sig = JSON.stringify(weeks) + "|" + S.student.number + "|" + S.student.name, now = Date.now();
    if (!force && now - lastSentAt < MIN_GAP_MS) return;
    if (!force && sig === lastSig && !(now - lastInput < IDLE_MS && now - lastSentAt >= BEAT_MS)) return;   // 바뀐 게 없으면 활동 중일 때만 1분마다 하트비트
    sending = true;
    try {
      await FB.reportProgress(S.student, { weeks, activeMs, lastActiveAt: lastActiveAt || now });
      lastSig = sig; lastSentAt = Date.now(); barState = "ok"; const first = !ready; ready = true;
      if (first) maybeShowLive();
    } catch (e) { barState = "err"; }
    sending = false; updateBar();
  }
  function tick() {
    const now = Date.now(), dt = now - lastTick; lastTick = now; tickCount++;
    if (document.visibilityState === "visible" && now - lastInput < IDLE_MS && dt < 5000) activeMs += dt;
    if (tickCount % 10 === 0) lsSet(K_AMS(), String(Math.round(activeMs)));
    if (tickCount % 15 === 0) send(false);
  }

  /* ---------- 퀴즈 상태(이 브라우저의 기록) ---------- */
  const qls = () => { try { return Object.assign({ answered: {}, skipped: {}, seen: {}, last: 0 }, JSON.parse(lsGet(K_QZ()) || "{}")); } catch (e) { return { answered: {}, skipped: {}, seen: {}, last: 0 }; } };
  const qsave = st => lsSet(K_QZ(), JSON.stringify(st));
  function quizById(id) {
    for (const w of CONTENT.weeks) { const q = (w.quiz || []).find(x => x.id === id); if (q) return { week: w, quiz: q }; }
    return null;
  }
  const canAsk = () => monOn && ready && hasId() && !modalOpen && typeof FB !== "undefined";

  /* 교사가 즉시 출제한 퀴즈: 열 때마다 liveAt 이 새로 찍히므로 (id@liveAt) 단위로 한 번씩만 띄운다. */
  function maybeShowLive() {
    const c = quizCfg; if (!canAsk() || !c || !c.liveId) return;
    const key = c.liveId + "@" + (c.liveAt && c.liveAt.toMillis ? c.liveAt.toMillis() : 0), f = quizById(c.liveId);
    if (!f || qls().seen[key]) return;
    openQuiz(f, { kind: "live", key });
  }

  /* 자동 퀴즈: 한 탐구 단계를 마치는 순간, 그 주차의 자동 모드가 켜져 있으면 아직 안 푼 퀴즈 1개를 낸다. */
  const stageDone = st => { let any = false; for (const it of st.items) if (ANSWERABLE(it) && !it.optional) { any = true; if (!isAnswered(it, S.answers[it.id])) return false; } return any; };
  function completedSet() { const s = new Set(); CONTENT.weeks.forEach(w => w.stages.forEach((st, i) => { if (stageDone(st)) s.add(w.n + "-" + i); })); return s; }
  function rebase() { doneStages = completedSet(); }          // 불러오기·초기화처럼 한꺼번에 바뀐 완료 단계는 '방금 끝낸 것'으로 치지 않는다
  function checkStages() {
    if (!doneStages) { rebase(); return; }
    const now = completedSet(), fresh = [...now].filter(k => !doneStages.has(k)); doneStages = now;
    if (fresh.length) tryAuto(Number(fresh[0].split("-")[0]));
  }
  function tryAuto(wn) {
    if (!canAsk() || !quizCfg || !(quizCfg.auto || {})[wn]) return;
    const st = qls(), w = CONTENT.weeks.find(x => x.n === wn); if (!w || Date.now() - st.last < AUTO_COOLDOWN_MS) return;
    const q = (w.quiz || []).find(x => !st.answered[x.id] && (st.skipped[x.id] || 0) < 2);
    if (q) openQuiz({ week: w, quiz: q }, { kind: "auto" });
  }

  /* ---------- 팝업 ---------- */
  function openQuiz(f, meta) {
    if (modalOpen) return; modalOpen = true;
    const q = f.quiz, st0 = qls(), canDefer = meta.kind === "auto" && !(st0.skipped[q.id] > 0);
    let sel = null, busy = false, finished = false;
    const opts = q.options.map((o, i) => {
      const r = el("input", { type: "radio", name: "qz", value: i, onchange: () => { sel = i; bOk.disabled = false; } });
      return el("label", { class: "qz-opt" }, r, el("span", { html: `${i + 1}. ${o}` }));
    });
    const msg = el("div", { class: "qz-msg", "aria-live": "polite" });
    const bOk = el("button", { class: "btn primary", type: "button", disabled: true }, "답 확인");
    const bClose = el("button", { class: "btn", type: "button" }, canDefer ? "나중에" : "닫기");
    const panel = el("div", { class: "qz-panel", role: "dialog", "aria-modal": "true", "aria-label": "돌발 퀴즈" },
      el("div", { class: "qz-kicker" }, `돌발 퀴즈 · ${f.week.concept}`, el("small", {}, " 점수에 들어가지 않아요. 고른 답은 선생님이 수업을 돕는 데만 참고해요. 틀리면 한 번 더 고를 수 있어요.")),
      el("p", { class: "qz-q", html: q.q }), el("div", { class: "qz-opts" }, opts), msg, el("div", { class: "qz-btns" }, bClose, bOk));
    const ov = el("div", { class: "qz-overlay" }, panel);
    const close = () => {
      document.removeEventListener("keydown", onKey); ov.remove(); modalOpen = false;
      const st = qls();
      if (finished) st.answered[q.id] = true; else if (meta.kind === "auto") st.skipped[q.id] = (st.skipped[q.id] || 0) + 1;
      if (meta.key) st.seen[meta.key] = true;
      st.last = Date.now(); qsave(st);
    };
    const onKey = e => { if (e.key === "Escape" && !busy) close(); };
    bClose.addEventListener("click", close);
    bOk.addEventListener("click", async () => {
      if (sel == null || busy) return; busy = true; bOk.disabled = true; msg.className = "qz-msg"; msg.textContent = "채점 중…";
      try {
        const r = await FB.answerQuiz(S.student, q.id, sel);
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

  /* ---------- 바깥에서 부르는 함수 ---------- */
  function init() {
    if (typeof FB === "undefined" || started) return; started = true;
    activeMs = Number(lsGet(K_AMS())) || 0;
    idKey = (S.student.number || "").trim() + "|" + (S.student.name || "").trim();
    ["pointerdown", "keydown", "input", "scroll", "wheel", "touchstart"].forEach(t =>
      addEventListener(t, () => { lastInput = lastActiveAt = Date.now(); }, { passive: true, capture: true }));
    setInterval(tick, 1000);
    addEventListener("pagehide", () => send(true));
    document.addEventListener("visibilitychange", () => { if (document.visibilityState === "hidden") send(true); });
    FB.watchMonitor(s => { const was = monOn; monOn = !!(s && s.on); if (!monOn) { ready = false; lastSentAt = 0; } if (monOn && !was) { rebase(); send(true); } updateBar(); }).catch(() => {});
    FB.watchQuiz(c => { quizCfg = c || null; maybeShowLive(); }).catch(() => {});
  }
  /* 문항을 만질 때마다(student.js renderItem) */
  function note(id) {
    lastByWeek[wkOf(id)] = id; lastInput = lastActiveAt = Date.now();
    if (monOn) checkStages();
  }
  /* 학번·성명이 바뀌었을 때 */
  function refresh() {
    const k = (S.student.number || "").trim() + "|" + (S.student.name || "").trim();
    if (k !== idKey) { idKey = k; idSince = Date.now(); ready = false; lastSig = ""; setTimeout(() => send(false), ID_SETTLE_MS + 100); }
    updateBar();
  }
  return { init, note, rebase, refresh };
})();
