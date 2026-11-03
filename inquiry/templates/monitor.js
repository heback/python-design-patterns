"use strict";
/* 학생용: 진도 자동 전달. 교사가 [진도 수집]을 켜 두었을 때만 동작하고, 켜져 있는 동안은 화면 위쪽에 항상 고지한다.
   전달하는 것: 로그인한 계정의 이름·이메일(학번·성명은 받지 않는다), 주차별 완료 문항 수·ID, 마지막으로 만진 문항, 활동 시간(화면이 보이고 최근 60초 안에 입력·스크롤·클릭이 있던 시간), 마지막 활동 시각.
   이 화면을 보고 있는지(FocusTrack: 탭 가림·창 포커스)와 벗어난 횟수·시간도 전달한다. 학생 고지 줄(updateBar)은 이 목록과 항상 같게 유지한다.
   전달하지 않는 것: 쓴 글의 내용(서버로 보내지 않는다. 브라우저에만 저장된다), 키 입력, 화면, 탭 전환.
   student.js 보다 먼저 실려서, 전역 S·CONTENT·LS_KEY 는 함수가 실제로 불릴 때 읽는다. */
const Mon = (() => {
  const IDLE_MS = 60000, BEAT_MS = 60000, MIN_GAP_MS = 10000;
  let monOn = false, ready = false, sending = false, again = false, barState = "";
  let lastSentAt = 0, lastSig = "", lastInput = 0, lastActiveAt = 0, lastTick = Date.now(), tickCount = 0;
  let activeMs = 0, started = false;
  const lastByWeek = {};
  const K_AMS = () => StudentAuth.key(LS_KEY + "-activeMs");     // 계정(uid)별 활동 시간
  const loggedIn = () => !!StudentAuth.get();
  /* 로그인 안내: 로그인 전에는 버튼, 후에는 계정과 로그아웃(공용 컴퓨터용) */
  function accountBits() {
    const u = StudentAuth.get(), msg = el("span", { class: "monmsg" });
    if (!u) return [msg, "먼저 학교 Google 계정으로 로그인해 주세요. ", el("button", { class: "qbtn", type: "button", onclick: async () => { msg.textContent = (await StudentAuth.login()) || ""; } }, ico("login"), "로그인")];
    return [el("span", { class: "monacct" }, u.email, " "), el("button", { class: "qbtn small", type: "button", onclick: () => StudentAuth.logout() }, "로그아웃")];
  }
  const wkOf = id => { const m = /^w(\d+)-/.exec(id); return m ? Number(m[1]) : 0; };

  /* ---------- 고지 줄 ---------- */
  function updateBar() {
    const b = $("#monbar"); if (!b) return;
    const show = typeof FB !== "undefined" && monOn; b.hidden = !show; if (!show) return;
    b.className = "monbar" + (barState === "err" ? " err" : "");
    const st = !loggedIn() ? ""
      : barState === "err" ? "지금은 전달하지 못했어요(인터넷 연결을 확인해 주세요. 공부에는 영향이 없어요)."
      : lastSentAt ? "전달됨 " + stamp(new Date(lastSentAt)) : "";
    const stIco = barState === "err" ? ico("warning") : lastSentAt && loggedIn() ? ico("check_circle", "fill") : null;
    b.replaceChildren(ico("cell_tower"), el("b", {}, "진행 상황이 선생님께 자동으로 전달돼요. "),
      "어느 문항을 마쳤는지·지금 어느 문항을 하고 있는지·마지막 활동 시각·활동 시간(입력이나 스크롤이 있던 시간)·이 화면을 보고 있는지(다른 탭이나 창으로 옮겼는지)와 벗어난 횟수·시간이 로그인한 계정의 이름·이메일과 함께 전달돼요. "
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
    if (!monOn || !loggedIn() || typeof FB === "undefined") return;
    if (sending) { if (force) again = true; return; }                  // 앞 전송이 끝나면 최신 상태로 한 번 더 보낸다(버리면 서버가 옛 상태에 머문다)
    const weeks = snapshot(), sig = JSON.stringify(weeks) + "|" + FocusTrack.snapshot().view, now = Date.now();      // 화면 상태가 바뀐 것도 '바뀐 것'이다
    if (!force && now - lastSentAt < MIN_GAP_MS) return;
    if (!force && sig === lastSig && !(now - lastInput < IDLE_MS && now - lastSentAt >= BEAT_MS)) return;   // 바뀐 게 없으면 활동 중일 때만 1분마다 하트비트
    sending = true;
    try {
      await FB.reportProgress({ weeks, activeMs, lastActiveAt: lastActiveAt || now, where: whereNow(), focus: FocusTrack.snapshot() });
      lastSig = sig; lastSentAt = Date.now(); barState = "ok"; ready = true;
    } catch (e) { barState = "err"; }
    sending = false; updateBar();
    if (again) { again = false; send(true); }
  }
  /* 지금 어디에 있는지(교사 표의 '마지막 활동 위치'). 마지막으로 만진 문항의 주차를 쓴다. */
  function whereNow() { const ks = Object.keys(lastByWeek); return ks.length ? "학습지 " + ks[ks.length - 1] + "주차" : "학습지"; }
  function tick() {
    const now = Date.now(), dt = now - lastTick; lastTick = now; tickCount++;
    if (document.visibilityState === "visible" && now - lastInput < IDLE_MS && dt < 5000) activeMs += dt;
    if (tickCount % 10 === 0) lsSet(K_AMS(), String(Math.round(activeMs)));
    if (tickCount % 15 === 0) send(false);
  }

  /* ---------- 바깥에서 부르는 함수 ---------- */
  function init() {
    if (typeof FB === "undefined" || started) return; started = true;
    ["pointerdown", "keydown", "input", "scroll", "wheel", "touchstart"].forEach(t =>
      addEventListener(t, () => { lastInput = lastActiveAt = Date.now(); }, { passive: true, capture: true }));
    setInterval(tick, 1000);
    addEventListener("pagehide", () => send(true));
    document.addEventListener("visibilitychange", () => { if (document.visibilityState === "hidden") send(true); });
    FB.watchMonitor(s => { const was = monOn; monOn = !!(s && s.on); if (!monOn) { ready = false; lastSentAt = 0; } if (monOn && !was) send(true); updateBar(); }).catch(() => {});
    FocusTrack.onChange(() => send(true));      // 화면을 벗어나거나 돌아올 때 바로 알린다
    StudentAuth.onChange(() => { ready = false; lastSig = ""; activeMs = Number(lsGet(K_AMS())) || 0; updateBar(); send(true); });
    StudentAuth.init();
  }
  /* 문항을 만질 때마다(student.js renderItem) */
  function note(id) { lastByWeek[wkOf(id)] = id; lastInput = lastActiveAt = Date.now(); }
  /* 화면을 다시 그린 뒤 고지 줄을 맞춘다 */
  function refresh() { updateBar(); }
  return { init, note, refresh };
})();
