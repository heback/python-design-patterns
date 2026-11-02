"use strict";
/* 학생용: 진도 자동 전달과 돌발 퀴즈. 교사가 [진도 수집]을 켜 두었을 때만 동작하고, 켜져 있는 동안은 화면 위쪽에 항상 고지한다.
   전달하는 것: 학번·성명, 주차별 완료 문항 수·ID, 마지막으로 만진 문항, 활동 시간(화면이 보이고 최근 60초 안에 입력·스크롤·클릭이 있던 시간), 마지막 활동 시각.
   퀴즈를 풀면 고른 답과 시도 횟수가 서버(answerQuiz)에 기록된다. 학생 고지 줄(updateBar)은 이 목록과 항상 같게 유지한다.
   전달하지 않는 것: 쓴 글의 내용(서버로 보내지 않는다. 브라우저에만 저장된다), 키 입력, 화면, 탭 전환.
   student.js 보다 먼저 실려서, 전역 S·CONTENT·LS_KEY 는 함수가 실제로 불릴 때 읽는다. */
const Mon = (() => {
  const IDLE_MS = 60000, BEAT_MS = 60000, MIN_GAP_MS = 10000;
  let monOn = false, ready = false, sending = false, barState = "";
  let lastSentAt = 0, lastSig = "", lastInput = 0, lastActiveAt = 0, lastTick = Date.now(), tickCount = 0;
  let activeMs = 0, doneStages = null, started = false, idKey = "", idSince = 0;
  const lastByWeek = {};
  const K_AMS = () => LS_KEY + "-activeMs";
  const loggedIn = () => !!StudentAuth.get();
  /* 로그인 안내: 로그인 전에는 버튼, 후에는 계정과 로그아웃(공용 컴퓨터용) */
  function accountBits() {
    const u = StudentAuth.get(), msg = el("span", { class: "monmsg" });
    if (!u) return [msg, "먼저 학교 Google 계정으로 로그인해 주세요. ", el("button", { class: "qbtn", type: "button", onclick: async () => { msg.textContent = (await StudentAuth.login()) || ""; } }, ico("login"), "로그인")];
    return [el("span", { class: "monacct" }, u.email, " "), el("button", { class: "qbtn small", type: "button", onclick: () => StudentAuth.logout() }, "로그아웃")];
  }
  const hasId = () => !!(S.student.number || "").trim() && !!(S.student.name || "").trim();
  const ID_SETTLE_MS = 4000;     // 학번·성명을 한 글자씩 치는 중간 값으로 진도 문서가 여러 개 생기지 않도록, 입력이 멈춘 뒤에 보낸다
  const wkOf = id => { const m = /^w(\d+)-/.exec(id); return m ? Number(m[1]) : 0; };

  /* ---------- 고지 줄 ---------- */
  function updateBar() {
    const b = $("#monbar"); if (!b) return;
    const show = typeof FB !== "undefined" && monOn; b.hidden = !show; if (!show) return;
    b.className = "monbar" + (barState === "err" ? " err" : "");
    const st = !loggedIn() ? ""
      : !hasId() ? " 위쪽에 학번과 성명을 입력하면 시작돼요."
      : barState === "err" ? "지금은 전달하지 못했어요(인터넷 연결이나 학번·성명을 확인해 주세요. 공부에는 영향이 없어요)."
      : lastSentAt ? "전달됨 " + stamp(new Date(lastSentAt)) : "";
    const stIco = barState === "err" ? ico("warning") : lastSentAt && hasId() && loggedIn() ? ico("check_circle", "fill") : null;
    b.replaceChildren(ico("cell_tower"), el("b", {}, "진행 상황이 선생님께 자동으로 전달돼요. "),
      "어느 문항을 마쳤는지·지금 어느 문항을 하고 있는지·마지막 활동 시각·활동 시간(입력이나 스크롤이 있던 시간)이 학번·성명과 함께 전달되고, 돌발 퀴즈에서 고른 답도 기록돼요. "
      + "쓴 글의 내용과 키 입력, 화면은 보내지 않아요. ", ...accountBits(), el("span", { class: "monst" }, stIco, st));
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
    if (!monOn || !loggedIn() || !hasId() || typeof FB === "undefined" || sending || Date.now() - idSince < ID_SETTLE_MS) return;
    const weeks = snapshot(), sig = JSON.stringify(weeks) + "|" + S.student.number + "|" + S.student.name, now = Date.now();
    if (!force && now - lastSentAt < MIN_GAP_MS) return;
    if (!force && sig === lastSig && !(now - lastInput < IDLE_MS && now - lastSentAt >= BEAT_MS)) return;   // 바뀐 게 없으면 활동 중일 때만 1분마다 하트비트
    sending = true;
    try {
      await FB.reportProgress(S.student, { weeks, activeMs, lastActiveAt: lastActiveAt || now, where: whereNow() });
      lastSig = sig; lastSentAt = Date.now(); barState = "ok"; const first = !ready; ready = true;
      if (first) QuizUI.showLive();
    } catch (e) { barState = "err"; }
    sending = false; updateBar();
  }
  /* 지금 어디에 있는지(교사 표의 '마지막 활동 위치'). 마지막으로 만진 문항의 주차를 쓴다. */
  function whereNow() { const ks = Object.keys(lastByWeek); return ks.length ? "학습지 " + ks[ks.length - 1] + "주차" : "학습지"; }
  function tick() {
    const now = Date.now(), dt = now - lastTick; lastTick = now; tickCount++;
    if (document.visibilityState === "visible" && now - lastInput < IDLE_MS && dt < 5000) activeMs += dt;
    if (tickCount % 10 === 0) lsSet(K_AMS(), String(Math.round(activeMs)));
    if (tickCount % 15 === 0) send(false);
  }

  /* ---------- 돌발 퀴즈: 팝업·채점은 QuizUI(quiz-ui.js), 여기서는 언제 물을지만 정한다 ---------- */
  const canAsk = () => monOn && ready && loggedIn() && hasId() && typeof FB !== "undefined";
  const slugsOf = w => (w.patterns || []).map(p => (/\/textbook\/([\w-]+)\.html/.exec(p.href) || [])[1]).filter(Boolean);
  const groupOf = slug => ((CONTENT.chapters || []).find(c => c.slug === slug) || {}).group;

  /* 자동 퀴즈: 한 탐구 단계를 마치는 순간, 그 주차에서 함께 읽는 교재 장에 딸린 퀴즈를 낸다(교사가 켠 분류만). */
  const stageDone = st => { let any = false; for (const it of st.items) if (ANSWERABLE(it) && !it.optional) { any = true; if (!isAnswered(it, S.answers[it.id])) return false; } return any; };
  function completedSet() { const s = new Set(); CONTENT.weeks.forEach(w => w.stages.forEach((st, i) => { if (stageDone(st)) s.add(w.n + "-" + i); })); return s; }
  function rebase() { doneStages = completedSet(); }          // 불러오기·초기화처럼 한꺼번에 바뀐 완료 단계는 '방금 끝낸 것'으로 치지 않는다
  function checkStages() {
    if (!doneStages) { rebase(); return; }
    const now = completedSet(), fresh = [...now].filter(k => !doneStages.has(k)); doneStages = now;
    if (!fresh.length) return;
    const w = CONTENT.weeks.find(x => x.n === Number(fresh[0].split("-")[0])); if (!w) return;
    const chapters = slugsOf(w);
    QuizUI.askAuto({ chapters, groupKeys: [...new Set(chapters.map(groupOf).filter(Boolean))] });
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
    QuizUI.init({ groups: CONTENT.quizzes || [], getStudent: () => S.student, allowed: canAsk });
    StudentAuth.onChange(() => { ready = false; lastSig = ""; updateBar(); send(true); });
    StudentAuth.init();
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
