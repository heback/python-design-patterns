"use strict";
/* 호스팅된 교재 페이지(각 장)용: 읽기 진도 자동 전달과 돌발 퀴즈. 학습지의 monitor.js 와 같은 규칙이다.
   교사가 [진도 수집]을 켜 두었고 학번·성명이 있을 때만 보내며, 켜져 있는 동안은 화면 위쪽에 항상 고지한다.
   전달하는 것: 학번·성명, 이 장에서 읽은 절 수·마지막 절, 활동 시간(화면이 보이고 최근 60초 안에 입력·스크롤·클릭이 있던 시간), 마지막 활동 시각.
   퀴즈를 풀면 고른 답과 시도 횟수가 서버에 기록된다. 이 목록과 고지 줄(updateBar)의 문구는 항상 같게 유지한다.
   보내려면 학교 Google 계정으로 로그인해야 한다(StudentAuth, quiz-ui.js). 서버 규칙이 도메인과 uid 를 다시 확인한다.
   전달하지 않는 것: 키 입력, 화면, 탭 전환.
   학번·성명은 학습지와 같은 브라우저 저장소(dp-inquiry-student)에서 읽는다. 학습지와 같은 주소(origin)의 교재 사본에서만 공유된다.
   필요한 전역: core.js(el, ico, $, $$, lsGet, lsSet, stamp), fb.js(FB), quiz-ui.js(QuizUI), 빌드가 넣는 TB_DATA = {chapters, quizzes}. */
(() => {
  if (typeof FB === "undefined" || typeof TB_DATA === "undefined") return;
  const SLUG = (/\/(\d\d-[\w-]+)\.html/.exec(location.pathname) || [])[1];
  const CH = (TB_DATA.chapters || []).find(c => c.slug === SLUG);
  if (!CH) return;                                  // 장 페이지가 아니면(용어집 등) 아무것도 하지 않는다
  const KEY_STU = "dp-inquiry-student", KEY_AMS = "dp-inquiry-student-activeMs", KEY_READ = "dp-textbook-read";
  const IDLE_MS = 60000, BEAT_MS = 60000, MIN_GAP_MS = 10000, READ_SECS = 2, DONE_RATIO = 0.8;
  let monOn = false, ready = false, sending = false, barState = "", lastSentAt = 0, lastSig = "";
  let lastInput = 0, lastActiveAt = 0, lastTick = Date.now(), tickCount = 0, activeMs = Number(lsGet(KEY_AMS)) || 0;

  /* ---------- 학번·성명(학습지와 같은 저장소) ---------- */
  const readStu = () => { try { return JSON.parse(lsGet(KEY_STU) || "{}"); } catch (e) { return {}; } };
  const student = () => Object.assign({ klass: "", number: "", name: "" }, readStu().student);
  const hasId = () => !!(student().number || "").trim() && !!(student().name || "").trim();
  const loggedIn = () => !!StudentAuth.get();
  function saveId(number, name) {
    const d = readStu(); d.app = d.app || "dp-inquiry"; d.schema = d.schema || 1; d.answers = d.answers || {}; d.feedback = d.feedback || {};
    d.student = Object.assign({ klass: "", number: "", name: "" }, d.student, { number: number.trim(), name: name.trim() });
    lsSet(KEY_STU, JSON.stringify(d));
  }

  /* ---------- 읽은 절 ---------- */
  const sections = $$("main.content section[id]");
  const total = sections.length;
  const jget = k => { try { return JSON.parse(lsGet(k) || "{}"); } catch (e) { return {}; } };
  const readAll = jget(KEY_READ), read = new Set(readAll[SLUG] || []);
  const dwell = {}, visible = new Set();
  let lastSec = (readAll[SLUG] || []).slice(-1)[0] || "";
  if (total && typeof IntersectionObserver !== "undefined") {
    // 화면 가운데 40% 띠에 걸쳐 있는 절을 '읽는 중'으로 본다(긴 절도 한 번에 읽은 것으로 세지 않도록)
    const io = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) visible.add(e.target.id); else visible.delete(e.target.id); }), { rootMargin: "-30% 0px -30% 0px" });
    sections.forEach(s => io.observe(s));
  }
  function markRead(id) {
    if (read.has(id)) return false;
    read.add(id); lastSec = id;
    const all = jget(KEY_READ); all[SLUG] = [...read]; lsSet(KEY_READ, JSON.stringify(all));
    return true;
  }

  /* ---------- 고지 줄 ---------- */
  function ensureBar() {
    let b = $("#monbar"); if (b) return b;
    b = el("div", { class: "monbar", id: "monbar", hidden: true });
    const top = $(".topbar"); if (top) top.after(b); else document.body.prepend(b);
    return b;
  }
  function updateBar() {
    const b = ensureBar(), show = monOn; b.hidden = !show; if (!show) return;
    b.className = "monbar" + (barState === "err" ? " err" : "");
    const st = barState === "err" ? "지금은 전달하지 못했어요(인터넷 연결이나 학번·성명을 확인해 주세요. 공부에는 영향이 없어요)."
      : loggedIn() && hasId() && lastSentAt ? "전달됨 " + stamp(new Date(lastSentAt)) : "";
    const stIco = barState === "err" ? ico("warning") : loggedIn() && hasId() && lastSentAt ? ico("check_circle", "fill") : null;
    const kids = [ico("cell_tower"), el("b", {}, "진행 상황이 선생님께 자동으로 전달돼요. "),
      "어느 장의 어느 절까지 읽었는지·마지막 활동 시각·활동 시간(입력이나 스크롤이 있던 시간)이 학번·성명과 함께 전달되고, 돌발 퀴즈에서 고른 답도 기록돼요. 키 입력 내용이나 화면은 보내지 않아요. "];
    if (!loggedIn()) {
      const msg = el("span", { class: "monmsg" });
      kids.push(msg, "먼저 학교 Google 계정으로 로그인해 주세요. ", el("button", { class: "qbtn", type: "button", onclick: async () => { msg.textContent = (await StudentAuth.login()) || ""; } }, ico("login"), "로그인"));
    } else {
      kids.push(el("span", { class: "monacct" }, StudentAuth.get().email, " "), el("button", { class: "qbtn small", type: "button", onclick: () => StudentAuth.logout() }, "로그아웃"), " ");
    }
    if (loggedIn() && !hasId()) {
      const n = el("input", { type: "text", placeholder: "학번", "aria-label": "학번", inputmode: "numeric" }), m = el("input", { type: "text", placeholder: "성명", "aria-label": "성명" });
      const ok = el("button", { class: "qbtn", type: "button", onclick: () => { if (!n.value.trim() || !m.value.trim()) return; saveId(n.value, m.value); lastSig = ""; updateBar(); send(true); } }, "시작");
      kids.push("학번과 성명을 입력하면 시작돼요. ", el("span", { class: "monid" }, n, m, ok));
    }
    kids.push(el("span", { class: "monst" }, stIco, st));
    b.replaceChildren(...kids);
  }

  /* ---------- 전송 ---------- */
  const snapshot = () => ({ [SLUG]: { n: read.size, total, last: lastSec } });
  async function send(force) {
    if (!monOn || !loggedIn() || !hasId() || sending) return;
    const chapters = snapshot(), sig = JSON.stringify(chapters) + "|" + student().number + "|" + student().name, now = Date.now();
    if (!force && now - lastSentAt < MIN_GAP_MS) return;
    if (!force && sig === lastSig && !(now - lastInput < IDLE_MS && now - lastSentAt >= BEAT_MS)) return;   // 바뀐 게 없으면 활동 중일 때만 1분마다 하트비트
    sending = true;
    try {
      await FB.reportProgress(student(), { chapters, activeMs, lastActiveAt: lastActiveAt || now, where: "교재 " + CH.title });
      lastSig = sig; lastSentAt = Date.now(); barState = "ok"; const first = !ready; ready = true;
      if (first) QuizUI.showLive();
    } catch (e) { barState = "err"; }
    sending = false; updateBar();
  }

  /* ---------- 1초마다: 활동 시간과 읽은 절 ---------- */
  let asked = false;          // 이 페이지를 연 동안 한 번만 묻는다(이미 푼 것·미룬 횟수·간격은 QuizUI 가 기억한다)
  function checkDone() {
    if (asked || !total || read.size / total < DONE_RATIO) return;
    asked = true;
    QuizUI.askAuto({ chapters: [SLUG], groupKeys: [CH.group] });        // 이 장을 다 읽은 순간, 이 장의 퀴즈(교사가 켠 분류만)
  }
  function tick() {
    const now = Date.now(), dt = now - lastTick; lastTick = now; tickCount++;
    const active = document.visibilityState === "visible" && now - lastInput < IDLE_MS;
    if (active && dt < 5000) activeMs += dt;
    let changed = false;
    if (active) visible.forEach(id => { dwell[id] = (dwell[id] || 0) + 1; if (dwell[id] >= READ_SECS && markRead(id)) changed = true; });
    if (tickCount % 10 === 0) lsSet(KEY_AMS, String(Math.round(activeMs)));
    if (changed) { send(false); if (monOn && ready) checkDone(); }
    else if (tickCount % 15 === 0) send(false);
  }

  ["pointerdown", "keydown", "input", "scroll", "wheel", "touchstart"].forEach(t =>
    addEventListener(t, () => { lastInput = lastActiveAt = Date.now(); }, { passive: true, capture: true }));
  setInterval(tick, 1000);
  addEventListener("pagehide", () => send(true));
  document.addEventListener("visibilitychange", () => { if (document.visibilityState === "hidden") send(true); });
  FB.watchMonitor(s => { const was = monOn; monOn = !!(s && s.on); if (!monOn) { ready = false; lastSentAt = 0; } if (monOn && !was) send(true); updateBar(); }).catch(() => {});
  QuizUI.init({ groups: TB_DATA.quizzes || [], getStudent: student, allowed: () => monOn && ready && loggedIn() && hasId() });
  StudentAuth.onChange(() => { ready = false; lastSig = ""; updateBar(); send(true); });
  StudentAuth.init();
})();
