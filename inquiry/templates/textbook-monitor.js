"use strict";
/* 호스팅된 교재 페이지(각 장)용: 읽기 진도 자동 전달. 학습지의 monitor.js 와 같은 규칙이다.
   교사가 [진도 수집]을 켜 두었고 학생이 학교 Google 계정(@ts.hs.kr)으로 로그인했을 때만 보내며, 켜져 있는 동안은 화면 위쪽에 항상 고지한다.
   전달하는 것: 로그인한 계정의 이름·이메일(학번·성명은 따로 받지 않고 계정에 등록된 이름을 쓴다. 학생이 개인정보 수집·이용에 동의한 경우에만 — StudentAuth.get() 이 동의 전에는 null), 이 장에서 읽은 절 수·마지막 절, 이 장과 절별 체류 시간(초),
   활동 시간(화면이 보이고 최근 60초 안에 입력·스크롤·클릭이 있던 시간), 마지막 활동 시각,
   이 화면을 보고 있는지(FocusTrack: 탭 가림·창 포커스)와 벗어난 횟수·시간.
   이 목록과 고지 줄(updateBar)의 문구는 항상 같게 유지한다. 전달하지 않는 것: 키 입력, 화면, 탭 전환.
   체류 시간은 화면이 보이고 최근 60초 안에 조작이 있던 시간만 센다(절별: 그 절이 화면 가운데 띠에 있던 시간). 값은 줄어들지 않는다:
   서버의 내 기록과 비교해 큰 쪽만 쓰므로 기기를 바꾸거나 이 브라우저 기록이 지워져도 줄지 않는다.
   읽은 절·체류 시간·활동 시간은 이 브라우저의 localStorage 에 계정(uid)별로도 둔다. 서버 규칙이 도메인과 uid 를 다시 확인한다.
   필요한 전역: core.js(el, ico, $, $$, lsGet, lsSet, stamp), fb.js(FB), student-auth.js(StudentAuth), 빌드가 넣는 TB_DATA = {chapters}. */
(() => {
  if (typeof FB === "undefined" || typeof TB_DATA === "undefined") return;
  const FILE = (/\/(\d\d-[\w-]+)\.html/.exec(location.pathname) || [])[1] || "";
  const LONG = /-full$/.test(FILE);                  // 참고용 긴 버전 페이지: 같은 장의 읽기로 센다(절 id가 요약 판과 같다)
  const SLUG = FILE.replace(/-full$/, "");
  const CH = (TB_DATA.chapters || []).find(c => c.slug === SLUG);
  if (!CH) return;                                  // 장 페이지가 아니면(용어집 등) 아무것도 하지 않는다
  const IDLE_MS = 60000, BEAT_MS = 60000, MIN_GAP_MS = 10000, READ_SECS = 2;
  let monOn = false, monKnown = false, monAt = 0, ready = false, sending = false, again = false, barState = "", lastSentAt = 0, lastSig = "";
  let lastInput = 0, lastActiveAt = 0, lastTick = Date.now(), tickCount = 0, activeMs = 0, seeding = false;
  const loggedIn = () => !!StudentAuth.get();
  const K_READ = () => StudentAuth.key("dp-textbook-read"), K_DWELL = () => StudentAuth.key("dp-textbook-dwell"), K_AMS = () => StudentAuth.key("dp-inquiry-student-activeMs");
  const jget = k => { try { return JSON.parse(lsGet(k) || "{}"); } catch (e) { return {}; } };

  /* ---------- 읽은 절·체류 시간(계정별) ---------- */
  const sections = $$("main.content section[id]");
  const secIds = (CH.sections || []).map(s => s.id);                        // 진도의 기준은 요약 판의 절 목록이다. 긴 버전 페이지에서도 같은 절만 센다
  const ids = new Set(secIds.length ? secIds : sections.map(s => s.id)), total = ids.size;
  let secBy = {}, chMs = 0, lastSec = "";            // secBy: 절 id → 그 절이 화면 가운데에 있던 초, chMs: 이 장에서 보낸 시간(ms)
  const visible = new Set();
  const nRead = () => Object.keys(secBy).filter(id => ids.has(id) && secBy[id] >= READ_SECS).length;
  const saveDwell = () => { const all = jget(K_DWELL()); all[SLUG] = { c: Math.round(chMs / 1000), s: secBy, l: lastSec }; lsSet(K_DWELL(), JSON.stringify(all)); };
  function loadMine() {                              // 로그인(또는 계정 전환) 때 이 계정의 기록을 불러온다
    const d = jget(K_DWELL())[SLUG] || {}, old = jget(K_READ())[SLUG] || [];      // old: 예전 버전이 저장한 '읽은 절 목록'(이어받는다)
    secBy = Object.assign({}, d.s || {}); chMs = (Number(d.c) || 0) * 1000; lastSec = d.l || old.slice(-1)[0] || "";
    old.forEach(id => { secBy[id] = Math.max(secBy[id] || 0, READ_SECS); });
    activeMs = Number(lsGet(K_AMS())) || 0;
  }
  /* 서버의 내 기록과 합친다: 절별·장별로 큰 쪽만 쓴다(줄어들지 않는다). 읽을 수 없으면 이 브라우저의 값만 쓴다. */
  async function seed() {
    seeding = true;
    try {
      const d = await FB.readMyProgress(), c = d && d.chapters && d.chapters[SLUG];
      if (c) {
        Object.entries(c.s || {}).forEach(([id, v]) => { if (ids.has(id) && Number(v) > (secBy[id] || 0)) secBy[id] = Number(v); });
        if (Number(c.sec) * 1000 > chMs) chMs = Number(c.sec) * 1000;
        if (!lastSec && c.last) lastSec = c.last;
      }
    } catch (e) {}
    seeding = false; saveDwell();
  }
  if (total && typeof IntersectionObserver !== "undefined") {
    // 화면 가운데 40% 띠에 걸쳐 있는 절을 '읽는 중'으로 본다(긴 절도 한 번에 읽은 것으로 세지 않도록)
    const io = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) visible.add(e.target.id); else visible.delete(e.target.id); }), { rootMargin: "-30% 0px -30% 0px" });
    sections.forEach(s => io.observe(s));
  }

  /* ---------- 고지 줄 ---------- */
  function ensureBar() {
    let b = $("#monbar"); if (b) return b;
    b = el("div", { class: "monbar", id: "monbar", hidden: true });
    const top = $(".topbar"); if (top) top.after(b); else document.body.prepend(b);
    return b;
  }
  function updateBar() {
    const b = ensureBar(), show = monKnown; b.hidden = !show; if (!show) return;               // 스위치 상태를 아직 모르면(불러오는 중·오프라인) 아무 말도 하지 않는다
    if (!monOn) {                                                                       // 수집이 중지된 상태도 학생에게 분명히 알린다(나중에 서로 다른 말이 나오지 않도록)
      b.className = "monbar off";
      b.replaceChildren(ico("pause_circle", "fill"), el("b", {}, "진도 수집이 중지된 상태예요. "),
        "지금은 읽은 곳·활동 시간·이 화면을 보고 있는지 같은 학습 활동 정보가 선생님께 전달되거나 서버에 기록되지 않아요" + (monAt ? ` (선생님이 ${stamp(new Date(monAt))}에 중지했어요)` : "") + ". AI 도우미를 쓸 때의 질문·답 기록은 이와 별개예요.");
      return;
    }
    b.className = "monbar" + (barState === "err" ? " err" : "");
    const st = barState === "err" ? "지금은 전달하지 못했어요(인터넷 연결을 확인해 주세요. 공부에는 영향이 없어요)."
      : loggedIn() && lastSentAt ? "전달됨 " + stamp(new Date(lastSentAt)) : "";
    const stIco = barState === "err" ? ico("warning") : loggedIn() && lastSentAt ? ico("check_circle", "fill") : null;
    const kids = [ico("cell_tower"), el("b", {}, "진행 상황이 선생님께 자동으로 전달돼요. "),
      "어느 장의 어느 절까지 읽었는지·마지막 활동 시각·활동 시간(입력이나 스크롤이 있던 시간)·이 화면을 보고 있는지(다른 탭이나 창으로 옮겼는지)와 벗어난 횟수·시간이 로그인한 계정의 이름·이메일과 함께 전달돼요(개인정보 수집·이용에 동의한 경우에만). 키 입력 내용이나 화면 내용은 보내지 않아요. "];
    if (!loggedIn()) {
      const msg = el("span", { class: "monmsg" });
      kids.push(msg, "먼저 학교 Google 계정으로 로그인해 주세요. ", el("button", { class: "qbtn", type: "button", onclick: async () => { msg.textContent = (await StudentAuth.login()) || ""; } }, ico("login"), "로그인"));
    } else {
      kids.push(el("span", { class: "monacct" }, StudentAuth.get().email, " "), el("button", { class: "qbtn small", type: "button", onclick: () => StudentAuth.manageConsent() }, ico("verified_user"), "개인정보 동의"), " ", el("button", { class: "qbtn small", type: "button", onclick: () => StudentAuth.logout() }, "로그아웃"), " ");
    }
    kids.push(el("span", { class: "monst" }, stIco, st));
    b.replaceChildren(...kids);
  }

  /* ---------- 전송 ---------- */
  /* 서버로 보내는 이 장의 기록. sec(장 체류 초)와 s(절별 초)는 계속 늘어나는 값이라 변경 판정(sig)에는 넣지 않는다 — 하트비트·상태 변화 때 함께 간다. */
  const snapshot = () => ({ [SLUG]: { n: nRead(), total, last: lastSec, sec: Math.round(chMs / 1000), s: Object.fromEntries(Object.entries(secBy).filter(([id, v]) => ids.has(id) && v > 0)) } });
  const keyOf = c => JSON.stringify({ n: c[SLUG].n, total: c[SLUG].total, last: c[SLUG].last });
  async function send(force) {
    if (!monOn || !loggedIn() || seeding) return;
    if (sending) { if (force) again = true; return; }                  // 앞 전송이 끝나면 최신 상태로 한 번 더 보낸다(버리면 서버가 옛 상태에 머문다)
    const chapters = snapshot(), sig = keyOf(chapters) + "|" + FocusTrack.snapshot().view, now = Date.now();      // 화면 상태가 바뀐 것도 '바뀐 것'이다
    if (!force && now - lastSentAt < MIN_GAP_MS) return;
    if (!force && sig === lastSig && now - lastSentAt < BEAT_MS) return;   // 바뀐 게 없어도 1분마다 하트비트(조작이 없어도 보낸다 — 교사 화면이 '이 화면을 아직 열어 둔 상태'를 믿으려면 신호가 계속 와야 한다. 탭을 닫으면 끊긴다)
    sending = true;
    try {
      await FB.reportProgress({ chapters, activeMs, lastActiveAt: lastActiveAt || now, where: "교재 " + CH.title + (LONG ? " (긴 버전)" : ""), focus: FocusTrack.snapshot() });
      lastSig = sig; lastSentAt = Date.now(); barState = "ok"; ready = true;
    } catch (e) { barState = "err"; }
    sending = false; updateBar();
    if (again) { again = false; send(true); }
  }

  /* ---------- 1초마다: 활동 시간과 읽은 절 ---------- */
  function tick() {
    const now = Date.now(), dt = now - lastTick; lastTick = now; tickCount++;
    if (!loggedIn() || seeding) return;
    const active = document.visibilityState === "visible" && now - lastInput < IDLE_MS;
    if (active && dt < 5000) { activeMs += dt; chMs += dt; }
    let changed = false;
    if (active) visible.forEach(id => { if (!ids.has(id)) return; secBy[id] = (secBy[id] || 0) + 1; if (secBy[id] === READ_SECS) { lastSec = id; changed = true; } });
    if (tickCount % 10 === 0 || changed) { lsSet(K_AMS(), String(Math.round(activeMs))); saveDwell(); }
    if (changed || tickCount % 15 === 0) send(false);
  }

  ["pointerdown", "keydown", "input", "scroll", "wheel", "touchstart"].forEach(t =>
    addEventListener(t, () => { lastInput = lastActiveAt = Date.now(); }, { passive: true, capture: true }));
  setInterval(tick, 1000);
  addEventListener("pagehide", () => { saveDwell(); send(true); });
  document.addEventListener("visibilitychange", () => { if (document.visibilityState === "hidden") send(true); });
  FB.watchMonitor(s => { const was = monOn; monKnown = s !== undefined; monAt = s && s.updatedAt && s.updatedAt.toMillis ? s.updatedAt.toMillis() : 0; monOn = !!(s && s.on); if (!monOn) { ready = false; lastSentAt = 0; } if (monOn && !was) send(true); updateBar(); }).catch(() => {});
  /* AI 도우미가 참고하는 화면: 지금 화면 가운데에 있는 절의 글과, 학생이 드래그해 고른 글 */
  if (typeof Assistant !== "undefined") Assistant.init({ getContext: () => {
    const cur = Assistant.nearestMid(sections), h = cur && cur.querySelector("h2");
    return { kind: "textbook", chapter: SLUG, title: `${CH.title}${LONG ? " (긴 버전)" : ""}${h ? " · " + h.textContent.trim() : ""}`, text: cur ? Assistant.readable(cur, 6000) : "", selection: Assistant.selectedText() };
  } });
  FocusTrack.onChange(() => send(true));      // 화면을 벗어나거나 돌아올 때 바로 알린다
  StudentAuth.onChange(() => { ready = false; lastSig = ""; loadMine(); seed().then(() => { updateBar(); send(true); }); updateBar(); });
  StudentAuth.init();
})();
