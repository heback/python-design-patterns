"use strict";
/* 호스팅된 교재 페이지(각 장)용: 읽기 진도 자동 전달. 학습지의 monitor.js 와 같은 규칙이다.
   교사가 [진도 수집]을 켜 두었고 학생이 학교 Google 계정(@ts.hs.kr)으로 로그인했을 때만 보내며, 켜져 있는 동안은 화면 위쪽에 항상 고지한다.
   전달하는 것: 로그인한 계정의 이름·이메일(학번·성명은 받지 않는다), 이 장에서 읽은 절 수·마지막 절,
   활동 시간(화면이 보이고 최근 60초 안에 입력·스크롤·클릭이 있던 시간), 마지막 활동 시각,
   이 화면을 보고 있는지(FocusTrack: 탭 가림·창 포커스)와 벗어난 횟수·시간.
   이 목록과 고지 줄(updateBar)의 문구는 항상 같게 유지한다. 전달하지 않는 것: 키 입력, 화면, 탭 전환.
   읽은 절·활동 시간은 이 브라우저의 localStorage 에 계정(uid)별로 둔다. 서버 규칙이 도메인과 uid 를 다시 확인한다.
   필요한 전역: core.js(el, ico, $, $$, lsGet, lsSet, stamp), fb.js(FB), student-auth.js(StudentAuth), 빌드가 넣는 TB_DATA = {chapters}. */
(() => {
  if (typeof FB === "undefined" || typeof TB_DATA === "undefined") return;
  const SLUG = (/\/(\d\d-[\w-]+)\.html/.exec(location.pathname) || [])[1];
  const CH = (TB_DATA.chapters || []).find(c => c.slug === SLUG);
  if (!CH) return;                                  // 장 페이지가 아니면(용어집 등) 아무것도 하지 않는다
  const IDLE_MS = 60000, BEAT_MS = 60000, MIN_GAP_MS = 10000, READ_SECS = 2;
  let monOn = false, ready = false, sending = false, barState = "", lastSentAt = 0, lastSig = "";
  let lastInput = 0, lastActiveAt = 0, lastTick = Date.now(), tickCount = 0, activeMs = 0;
  const loggedIn = () => !!StudentAuth.get();
  const K_READ = () => StudentAuth.key("dp-textbook-read"), K_AMS = () => StudentAuth.key("dp-inquiry-student-activeMs");
  const jget = k => { try { return JSON.parse(lsGet(k) || "{}"); } catch (e) { return {}; } };

  /* ---------- 읽은 절(계정별) ---------- */
  const sections = $$("main.content section[id]");
  const total = sections.length;
  let read = new Set(), lastSec = "";
  const dwell = {}, visible = new Set();
  function loadMine() {                              // 로그인(또는 계정 전환) 때 이 계정의 기록을 불러온다
    const mine = (jget(K_READ())[SLUG] || []); read = new Set(mine); lastSec = mine.slice(-1)[0] || "";
    activeMs = Number(lsGet(K_AMS())) || 0;
  }
  if (total && typeof IntersectionObserver !== "undefined") {
    // 화면 가운데 40% 띠에 걸쳐 있는 절을 '읽는 중'으로 본다(긴 절도 한 번에 읽은 것으로 세지 않도록)
    const io = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) visible.add(e.target.id); else visible.delete(e.target.id); }), { rootMargin: "-30% 0px -30% 0px" });
    sections.forEach(s => io.observe(s));
  }
  function markRead(id) {
    if (read.has(id)) return false;
    read.add(id); lastSec = id;
    const all = jget(K_READ()); all[SLUG] = [...read]; lsSet(K_READ(), JSON.stringify(all));
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
    const st = barState === "err" ? "지금은 전달하지 못했어요(인터넷 연결을 확인해 주세요. 공부에는 영향이 없어요)."
      : loggedIn() && lastSentAt ? "전달됨 " + stamp(new Date(lastSentAt)) : "";
    const stIco = barState === "err" ? ico("warning") : loggedIn() && lastSentAt ? ico("check_circle", "fill") : null;
    const kids = [ico("cell_tower"), el("b", {}, "진행 상황이 선생님께 자동으로 전달돼요. "),
      "어느 장의 어느 절까지 읽었는지·마지막 활동 시각·활동 시간(입력이나 스크롤이 있던 시간)·이 화면을 보고 있는지(다른 탭이나 창으로 옮겼는지)와 벗어난 횟수·시간이 로그인한 계정의 이름·이메일과 함께 전달돼요. 키 입력 내용이나 화면 내용은 보내지 않아요. "];
    if (!loggedIn()) {
      const msg = el("span", { class: "monmsg" });
      kids.push(msg, "먼저 학교 Google 계정으로 로그인해 주세요. ", el("button", { class: "qbtn", type: "button", onclick: async () => { msg.textContent = (await StudentAuth.login()) || ""; } }, ico("login"), "로그인"));
    } else {
      kids.push(el("span", { class: "monacct" }, StudentAuth.get().email, " "), el("button", { class: "qbtn small", type: "button", onclick: () => StudentAuth.logout() }, "로그아웃"), " ");
    }
    kids.push(el("span", { class: "monst" }, stIco, st));
    b.replaceChildren(...kids);
  }

  /* ---------- 전송 ---------- */
  const snapshot = () => ({ [SLUG]: { n: read.size, total, last: lastSec } });
  async function send(force) {
    if (!monOn || !loggedIn() || sending) return;
    const chapters = snapshot(), sig = JSON.stringify(chapters), now = Date.now();
    if (!force && now - lastSentAt < MIN_GAP_MS) return;
    if (!force && sig === lastSig && !(now - lastInput < IDLE_MS && now - lastSentAt >= BEAT_MS)) return;   // 바뀐 게 없으면 활동 중일 때만 1분마다 하트비트
    sending = true;
    try {
      await FB.reportProgress({ chapters, activeMs, lastActiveAt: lastActiveAt || now, where: "교재 " + CH.title, focus: FocusTrack.snapshot() });
      lastSig = sig; lastSentAt = Date.now(); barState = "ok"; ready = true;
    } catch (e) { barState = "err"; }
    sending = false; updateBar();
  }

  /* ---------- 1초마다: 활동 시간과 읽은 절 ---------- */
  function tick() {
    const now = Date.now(), dt = now - lastTick; lastTick = now; tickCount++;
    if (!loggedIn()) return;
    const active = document.visibilityState === "visible" && now - lastInput < IDLE_MS;
    if (active && dt < 5000) activeMs += dt;
    let changed = false;
    if (active) visible.forEach(id => { dwell[id] = (dwell[id] || 0) + 1; if (dwell[id] >= READ_SECS && markRead(id)) changed = true; });
    if (tickCount % 10 === 0) lsSet(K_AMS(), String(Math.round(activeMs)));
    if (changed || tickCount % 15 === 0) send(false);
  }

  ["pointerdown", "keydown", "input", "scroll", "wheel", "touchstart"].forEach(t =>
    addEventListener(t, () => { lastInput = lastActiveAt = Date.now(); }, { passive: true, capture: true }));
  setInterval(tick, 1000);
  addEventListener("pagehide", () => send(true));
  document.addEventListener("visibilitychange", () => { if (document.visibilityState === "hidden") send(true); });
  FB.watchMonitor(s => { const was = monOn; monOn = !!(s && s.on); if (!monOn) { ready = false; lastSentAt = 0; } if (monOn && !was) send(true); updateBar(); }).catch(() => {});
  /* AI 도우미가 참고하는 화면: 지금 화면 가운데에 있는 절의 글과, 학생이 드래그해 고른 글 */
  if (typeof Assistant !== "undefined") Assistant.init({ getContext: () => {
    const cur = Assistant.nearestMid(sections), h = cur && cur.querySelector("h2");
    return { kind: "textbook", title: `${CH.title}${h ? " · " + h.textContent.trim() : ""}`, text: cur ? Assistant.readable(cur, 6000) : "", selection: Assistant.selectedText() };
  } });
  FocusTrack.onChange(() => send(true));      // 화면을 벗어나거나 돌아올 때 바로 알린다
  StudentAuth.onChange(() => { ready = false; lastSig = ""; loadMine(); updateBar(); send(true); });
  StudentAuth.init();
})();
