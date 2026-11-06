"use strict";
/* 교사용 앱(디자인 패턴 학습 관리): 학교 Google 계정으로 로그인한 교사가 학생 진도를 실시간으로 본다.
   학생 응답 본문은 서버로 오지 않으므로 응답 검토·코멘트·제출 관리 화면은 없다. */
const M = { view: "", events: null, prog: null, consents: null, progErr: "", mon: undefined, ai: undefined, stats: undefined, usage: null, logs: null, logErr: "", tokRange: "today", tokFrom: "", tokTo: "", quota: null, qSel: "", qFind: "", qErr: "",
  lg: { uid: "", kind: "all", size: 20, page: 0, cursors: [null], rows: null, more: false, total: null, err: "", busy: false, seq: 0 },   // 대화기록 쪽 나누기 상태(cursors[n] = n쪽의 시작 커서)
  group: "all", sort: "num",   // 진도 화면의 상태(boot 보다 먼저 있어야 한다)
  code: { students: null, sel: "", blocks: null, err: "", seq: 0 },   // 학생 코드 화면의 상태(학생이 교재 코드 편집기에서 단 주석·고친 코드)
  ask: { threads: null, sel: "", msgs: null, err: "", stats: undefined, draft: {}, via: {}, cau: {}, marking: "", unMsgs: null } };   // 학생 질문 화면의 상태(draft·via·cau: 학생별로 쓰던 답변·AI 추천 사용 여부·AI 확인 사항)
const BASE_TITLE = document.title;
const T = { live: [], liveTok: null };   // 실시간 구독 해제 함수 목록

let booted = false;
function boot() {
  if (booted) return; booted = true;
  initTheme();
  render();
}

/* ---- 로그인 게이트: 학교 Google 계정으로 로그인하고 서버(getTeacherContent)가 교사로 확인해 줘야 화면이 열린다 ---- */
function gate() {
  const g = $("#gate"), app = $("#app"), msg = $("#gate-msg"), btn = $("#btn-google");
  app.hidden = true; g.hidden = false; initTheme();
  btn.addEventListener("click", async () => {
    msg.textContent = "";
    try { await FB.signIn(); } catch (e) { if (e.code !== "auth/popup-closed-by-user" && e.code !== "auth/cancelled-popup-request") msg.textContent = FB.fbErr(e); }
  });
  FB.onAuth(async user => {
    if (!user || user.isAnonymous) { app.hidden = true; g.hidden = false; btn.hidden = false; return; }
    btn.hidden = true; msg.textContent = "권한 확인 중…";
    try {
      const r = await FB.teacherContent();
      CONTENT = { weeks: r.weeks, chapters: r.chapters };
      msg.textContent = ""; g.hidden = true; app.hidden = false;
      $("#who").hidden = false; $("#who").textContent = user.email; $("#btn-logout").hidden = false;
      $("#btn-logout").onclick = async () => { await FB.signOut(); location.reload(); };
      boot();
    } catch (e) {
      await FB.signOut();
      msg.textContent = /permission/i.test(e.code + e.message) ? `학교 계정(@${FB.domain})의 교사 계정으로 로그인해 주세요. (${user.email} 은(는) 권한이 없습니다)` : "오류: " + FB.fbErr(e);
      btn.hidden = false;
    }
  });
}

function render() {
  stopLive();
  const main = $("#main"); main.replaceChildren();
  renderMonitor(main);
}

const errText = e => FB.fbErr(e).replace(/^.*?: /, "");

/* ===================== 진도 수집 (실시간) ===================== */
/* 학생이 보내는 것은 교재 장별 읽은 절 수, 학습지 완료 문항 수·ID, 지금 있는 곳, 활동 시간, 마지막 활동 시각뿐이다(응답 본문 없음). 수집 스위치는 config/monitor.
   교재의 분류(서론·종합 / 생성 / 구조 / 행위)는 CONTENT.chapters 의 group 으로 나눈다. */
const GROUP_NAME = { intro: "서론·종합", create: "생성 패턴", struct: "구조 패턴", behave: "행위 패턴" };
function stopLive() { (T.live || []).forEach(f => { try { f(); } catch (e) {} }); T.live = []; T.liveTok = null; M.unAns = null; if (M.ask.unMsgs) { try { M.ask.unMsgs(); } catch (e) {} M.ask.unMsgs = null; } }
function liveSub(p, tok, onUn) {
  p.then(u => { if (T.liveTok === tok) { T.live.push(u); if (onUn) onUn(u); } else u(); }).catch(() => {});
}
/* 네이티브 replaceChildren 은 배열·null 을 문자열로 바꿔 버리므로, 한 겹 펴고 빈 값을 뺀 뒤 넣는다. */
const fill = (box, ...kids) => box.replaceChildren(...kids.flat().filter(k => k != null && k !== false));
const tsMs = x => (x && x.toMillis ? x.toMillis() : null);
function ago(ms) {
  if (!ms) return "—";
  const m = Math.floor((Date.now() - ms) / 60000);
  return m < 1 ? "방금" : m < 60 ? `${m}분 전` : `${Math.floor(m / 60)}시간 ${m % 60}분 전`;
}
/* 초를 "N분 M초" 로 */
const nf = n => (Number(n) || 0).toLocaleString("ko-KR");
const stuName = l => `${(l.student || {}).name || "(이름 없음)"}${(l.student || {}).email ? " · " + l.student.email.split("@")[0] : ""}`;
const todayKst = () => new Date(Date.now() + 9 * 3600e3).toISOString().slice(0, 10);
const recentChatErr = () => (M.logs || []).find(l => l.error && tsMs(l.at) > Date.now() - 30 * 60000);     // 최근 30분 안의 AI 호출 오류
const errBox = l => el("div", { class: "err-box" }, el("b", {}, ico("error", "fill"), "최근 30분 안에 AI 호출 오류가 있었습니다."), el("div", {}, `${stamp(new Date(tsMs(l.at)))} · ${stuName(l)} — ${l.error}`),
  /credit|billing|prepay|402|quota/i.test(l.error) ? el("div", {}, "Gemini API의 크레딧(요금) 한도 문제로 보입니다. Google AI Studio의 결제 설정에서 크레딧을 충전하거나 한도를 확인하세요.") : null);
const fmtDur = sec => { sec = Math.max(0, Math.round(Number(sec) || 0)); const m = Math.floor(sec / 60), s = sec % 60; return m ? (s ? `${m}분 ${s}초` : `${m}분`) : `${s}초`; };

/* 학생 한 명의 한 장 세부 정보: 읽은 절과 절별·장 체류 시간 */
function openDetail(r, c) {
  const x = (r.chapters || {})[c.slug] || {}, s = x.s || {}, secs = c.sections || [];
  const max = Math.max(1, ...secs.map(z => Number(s[z.id]) || 0));
  const name = `${r.student.name || "(이름 없음)"}${r.student.email ? " · " + r.student.email.split("@")[0] : ""}`;
  const lastTitle = (secs.find(z => z.id === x.last) || {}).title || x.last || "—";
  const close = () => { ov.remove(); document.removeEventListener("keydown", onKey); prev && prev.focus && prev.focus(); };
  const onKey = e => { if (e.key === "Escape") close(); };
  const prev = document.activeElement;
  const rows = secs.map(z => {
    const v = Number(s[z.id]) || 0, read = v >= 2;
    return el("tr", {}, el("td", {}, z.title), el("td", { style: "text-align:center" }, read ? el("span", { class: "pill ok" }, ico("check_circle", "fill"), "읽음") : el("span", { class: "pill none" }, "안 읽음")),
      el("td", { style: "min-width:160px" }, v ? fmtDur(v) : "—", el("div", { class: "bar" }, el("i", { style: `width:${Math.round(100 * v / max)}%` }))));
  });
  const ov = el("div", { class: "dlg-overlay", onclick: e => { if (e.target === ov) close(); } },
    el("div", { class: "dlg", role: "dialog", "aria-modal": "true", "aria-label": "챕터별 세부 정보" },
      el("header", {}, el("h3", {}, `${name}`, el("small", {}, ` ${GROUP_NAME[c.group] || ""} · ${c.title}`)), el("button", { type: "button", class: "btn small", onclick: close, "aria-label": "닫기" }, ico("close"), "닫기")),
      el("div", { class: "dlg-sum" },
        el("div", {}, el("b", {}, "읽은 절 "), `${x.n || 0} / ${x.total || secs.length} (${x.total ? Math.round(100 * (x.n || 0) / x.total) : 0}%)`),
        el("div", {}, el("b", {}, "이 장 체류 시간 "), fmtDur(x.sec)),
        el("div", {}, el("b", {}, "마지막으로 읽은 절 "), lastTitle),
        el("div", {}, el("b", {}, "마지막 활동 "), ago(tsMs(r.lastActiveAt)))),
      secs.length ? el("div", { style: "overflow-x:auto" }, el("table", { class: "ro" }, el("thead", {}, el("tr", {}, ["절", "읽음", "절 체류 시간"].map(h => el("th", {}, h)))), el("tbody", {}, rows))) : el("p", { class: "lead" }, "이 장의 절 정보가 없습니다."),
      el("p", { class: "lead", style: "font-size:13px" }, "체류 시간은 화면이 보이고 최근 60초 안에 입력·스크롤·클릭이 있던 시간만 센 값이며, 서버의 기록과 비교해 큰 쪽만 남기므로 줄어들지 않습니다. 절별 시간은 그 절이 화면 가운데에 있던 시간이라 합이 장 체류 시간보다 작을 수 있습니다.")));
  document.addEventListener("keydown", onKey); document.body.append(ov); $(".dlg .btn", ov).focus();
}

/* 학생이 이 화면을 보고 있는지: 보내온 view(on·hidden·blur)와 그 상태가 된 시각, 벗어난 횟수·시간.
   마지막으로 보낸 값이므로, 보고(updatedAt)가 VIEW_STALE_MS 넘게 끊기면 '신호 없음'으로 바꿔 그린다. */
const VIEW = { on: ["ok", "check_circle", "보는 중"], hidden: ["bad", "tab_unselected", "다른 탭"], blur: ["part", "open_in_new", "다른 창"] };
const VIEW_STALE_MS = 3 * 60000;   // 하트비트는 1분마다 오므로 3분 넘게 보고가 없으면 탭을 닫았거나 접속이 끊긴 것으로 본다
function viewCell(r) {
  const v = VIEW[r.view]; if (!v) return "—";
  const rep = tsMs(r.updatedAt), lag = rep ? Date.now() - rep : Infinity;
  if (lag > VIEW_STALE_MS) {      // 마지막으로 보낸 값('보는 중' 등)을 그대로 그리면 실제와 다르다
    const away = (r.leaves || 0) ? ` · 벗어남 ${r.leaves}회 · ${Math.round((r.awayMs || 0) / 60000)}분` : "";
    return el("span", {}, el("span", { class: "pill none", title: "최근 3분 넘게 학생 화면에서 보고가 없습니다(탭을 닫았거나 접속이 끊김). 아래는 마지막으로 받은 값입니다." }, ico("signal_disconnected", "fill"), "신호 없음"),
      el("small", { style: "color:var(--dim)" }, ` · 마지막 보고 ${rep ? Math.floor(lag / 60000) + "분 전" : "없음"} (${v[2]})${away}`));
  }
  const since = tsMs(r.viewAt), mins = since ? Math.floor((Date.now() - since) / 60000) : 0;
  const away = (r.leaves || 0) ? ` · 벗어남 ${r.leaves}회 · ${Math.round((r.awayMs || 0) / 60000)}분` : "";
  return el("span", {}, el("span", { class: "pill " + v[0] }, ico(v[1], "fill"), v[2] + (r.view !== "on" && mins >= 1 ? ` ${mins}분째` : "")), el("small", { style: "color:var(--dim)" }, away));
}
/* 마지막 활동으로부터: <2분 활동 중, <5분 잠시 멈춤, 그 이상 멈춤(자리 비움). 수업 중에만 의미가 있다. */
function liveState(ms) {
  const m = ms ? (Date.now() - ms) / 60000 : Infinity;
  return m < 2 ? ["ok", "활동 중"] : m < 5 ? ["part", "잠시 멈춤"] : ["none", "멈춤"];
}

/* 진도표의 '상태'·'화면' 열이 어떤 조건으로 정해지는지 설명한다. 조건을 바꾸면(liveState·VIEW·VIEW_STALE_MS) 이 설명도 함께 고친다. */
function statusLegend() {
  const pill = (cls, icon, label) => el("span", { class: "pill " + cls, style: "margin-right:6px" }, ico(icon, "fill"), label);
  const row = (p, text) => el("li", { style: "margin:3px 0" }, p, text);
  /* 기본은 접어 둔다. 진도표는 실시간으로 다시 그려지므로 교사가 펼친 상태를 M.legendOpen 에 기억해 두었다가 되살린다. */
  return el("details", { ...(M.legendOpen ? { open: "" } : {}), ontoggle: e => { M.legendOpen = e.target.open; }, style: "margin:6px 0;font-size:13.5px" },
    el("summary", { style: "cursor:pointer;font-weight:700" }, "상태·화면 표시 기준"),
    el("div", { style: "display:flex;gap:28px;flex-wrap:wrap;margin-top:4px" },
      el("div", { style: "flex:1;min-width:260px" }, el("b", {}, "상태"), " — 학생이 마지막으로 조작(클릭·키 입력·스크롤)한 때부터 지난 시간",
        el("ul", { style: "list-style:none;padding:0;margin:4px 0" },
          row(pill("ok", "check_circle", "활동 중"), "2분 미만"),
          row(pill("part", "pause_circle", "잠시 멈춤"), "2분 이상 5분 미만"),
          row(pill("none", "do_not_disturb_on", "멈춤"), "5분 이상 (자리 비움·탭 닫음, 또는 화면만 켜 둔 채 조작 없음)"))),
      el("div", { style: "flex:1;min-width:260px" }, el("b", {}, "화면"), " — 학생 브라우저가 알려 주는 탭 상태(무엇을 보는지는 알 수 없음). 조작이 없어도 1분마다 갱신",
        el("ul", { style: "list-style:none;padding:0;margin:4px 0" },
          row(pill("ok", "check_circle", "보는 중"), "이 탭이 보이고 창에 포커스가 있음"),
          row(pill("part", "open_in_new", "다른 창"), "탭은 보이지만 다른 창·프로그램을 눌러 포커스를 잃음"),
          row(pill("bad", "tab_unselected", "다른 탭"), "다른 탭으로 옮기거나 창을 최소화해 이 탭이 가려짐"),
          row(pill("none", "signal_disconnected", "신호 없음"), "최근 3분 넘게 보고가 없음(탭을 닫았거나 접속 끊김). 마지막으로 받은 값을 참고로 함께 표시"),
          row(el("span", { style: "margin-right:6px" }, "—"), "아직 화면 정보를 보낸 적 없음")))),
    el("p", { style: "color:var(--dim);margin:4px 0 0" }, "두 열은 서로 다른 것을 잽니다. '멈춤'인데 '보는 중'이면 탭은 열어 둔 채 5분 넘게 조작이 없는 것이고, '멈춤'인데 '신호 없음'이면 탭을 닫았거나 접속이 끊긴 것입니다."));
}

function renderMonitor(main) {
  const tok = T.liveTok = {};
  /* 메뉴: 왼쪽(좁은 화면에서는 위쪽)에 메뉴를 두고, 한 번에 한 가지 기능만 보여 준다. 선택한 화면은 주소 해시(#progress …)와 이 브라우저에 기억한다. */
  /* 메뉴: 환경설정 · 진도표 · 학생 질문 · 학생 코드 · AI 대화기록 · AI 사용량 · AI 질문한도 */
  const ctl = el("div", { class: "setrow" }), vAi = el("div", { class: "setrow" }), tbl = el("div", {});
  const vSet = el("section", { class: "panel", id: "v-settings" }, el("h3", {}, "환경설정"), ctl, vAi), vProg = el("section", { class: "panel", id: "v-progress" }, tbl),
    vLog = el("section", { class: "panel", id: "v-logs" }), vTok = el("section", { class: "panel", id: "v-tokens" }), vQuota = el("section", { class: "panel", id: "v-quota" }), vAsk = el("section", { class: "panel", id: "v-ask" }), vCode = el("section", { class: "panel", id: "v-code" });
  const VIEWS = [["settings", "settings", "환경설정", vSet], ["progress", "monitoring", "진도표", vProg], ["ask", "contact_support", "학생 질문", vAsk], ["code", "code", "학생 코드", vCode], ["logs", "forum", "AI 대화기록", vLog], ["tokens", "data_usage", "AI 사용량", vTok], ["quota", "tune", "AI 질문한도", vQuota]];
  const known = k => VIEWS.some(v => v[0] === k);
  if (!known(M.view)) { const h = location.hash.slice(1); M.view = known(h) ? h : "progress";   /* 처음 열면 항상 진도표. 마지막에 본 메뉴를 기억하지 않는다(주소 해시가 있을 때만 그 메뉴) */ }
  const nav = el("nav", { class: "side", "aria-label": "교사 메뉴" });
  const paintNav = () => {
    const act = (M.prog || []).filter(r => liveState(tsMs(r.lastActiveAt))[0] === "ok").length, aiOn = !!(M.ai && M.ai.on), monOn = !!(M.mon && M.mon.on), err = !!recentChatErr();
    const badge = k => k === "progress" ? el("span", { class: "nb " + (monOn ? "ok" : "off"), title: monOn ? "수집 중(활동 중인 학생 수)" : "진도 수집이 꺼져 있어요" }, monOn ? `${act}명` : "수집 꺼짐")
      : k === "settings" ? (err ? el("span", { class: "nb bad", title: "최근 AI 호출 오류" }, "오류") : null)
      : k === "ask" ? (askUnread() ? el("span", { class: "nb bad", title: `선생님이 아직 보지 않은 새 질문 ${askUnread()}건` }, `새 질문 ${askUnread()}`) : null)
      : null;
    document.title = askUnread() ? `(${askUnread()}) ${BASE_TITLE}` : BASE_TITLE;       // 다른 탭에 있어도 새 질문이 보이도록
    fill(nav, VIEWS.map(([k, ic, lab]) => el("button", { type: "button", class: "side-item", "aria-current": M.view === k ? "page" : null, onclick: () => go(k) }, ico(ic, M.view === k ? "fill" : ""), el("span", { class: "side-lab" }, lab), badge(k))));
  };
  const go = k => { M.view = k; try { history.replaceState(null, "", "#" + k); } catch (e) {} VIEWS.forEach(v => { v[3].hidden = v[0] !== k; }); if (k === "quota") paintQuota(); if (k === "ask") { paintAsk(); markAskRead(); } paintNav(); scrollTo(0, 0); };
  main.append(el("div", { class: "shell" }, nav, el("div", { class: "view" }, VIEWS.map(v => v[3]))));
  VIEWS.forEach(v => { v[3].hidden = v[0] !== M.view; });

  /* --- 환경설정 1: 진도 수집 --- */
  const paintCtl = () => {
    const on = !!(M.mon && M.mon.on);
    fill(ctl, el("h4", {}, "진도 수집"),
      el("p", { class: "lead" }, "켜 두면 학생의 학습지와 교재 화면에 ‘진행 상황이 선생님께 자동으로 전달된다’는 고지가 뜨고, 교재 각 장에서 읽은 절·학습지에서 마친 문항·지금 있는 곳·마지막 활동 시각·활동 시간·이 화면을 보고 있는지(다른 탭이나 창으로 옮겼는지)가 계정의 이름·이메일과 함께 [진도표]에 실시간으로 나타납니다. 쓴 글의 내용은 전달되지 않습니다(학생 브라우저에만 저장됩니다). 수업이 끝나면 꺼 두세요."),
      M.mon === undefined ? el("p", { class: "lead" }, "상태를 확인하는 중…") : el("p", { class: on ? "status-open" : "status-closed" }, ico("circle", "fill"), on ? "수집 중 — 학생에게 고지가 표시됩니다" : "꺼짐 — 학생은 진도를 보내지 않습니다"),
      el("div", { style: "display:flex;gap:8px;flex-wrap:wrap" },
        el("button", { class: "btn primary", onclick: async e => { e.target.disabled = true; try { await FB.saveMonitor(!on); } catch (err) { alert("저장하지 못했습니다: " + errText(err)); } } }, on ? [ico("stop"), "수집 중지"] : [ico("play_arrow"), "수집 시작"]),
        el("button", { class: "btn danger", onclick: async () => {
          if (!confirm("서버에 쌓인 모든 학생의 진도 기록을 삭제합니다. 계속할까요?")) return;
          try { toast(`진도 기록 ${await FB.clearProgress()}건을 삭제했습니다`); } catch (err) { alert("삭제하지 못했습니다: " + errText(err)); }
        } }, [ico("delete"), "진도 기록 삭제"])),
      monitorProof(on));
  };
  /* 켜고 끈 이력(서버 시각·변경한 교사)과, 꺼진 뒤 새로 들어온 진도가 없다는 확인. 학생 화면에도 중지 사실과 시각이 표시된다. */
  const monitorProof = on => {
    const ev = M.events || [], lastOff = !on ? ev.find(e => e.on === false) : null, offAt = lastOff ? tsMs(lastOff.at) : (M.mon && M.mon.updatedAt && !on ? tsMs(M.mon.updatedAt) : null);
    const after = offAt ? (M.prog || []).filter(r => (tsMs(r.updatedAt) || 0) > offAt).length : null;
    return el("div", { style: "margin-top:12px" },
      after !== null ? el("p", { class: after ? "status-closed" : "status-open", style: "font-size:14px" }, ico(after ? "warning" : "verified", "fill"),
        after ? `중지(${stamp(new Date(offAt))}) 이후에 서버가 받은 진도 갱신이 ${after}건 있습니다. 서버 규칙상 있을 수 없는 값이니 확인이 필요합니다.` : `중지(${stamp(new Date(offAt))}) 이후 서버가 받은 진도 갱신: 0건. 서버 규칙이 수집이 꺼진 동안의 쓰기를 거부합니다.`) : null,
      el("details", { class: "fold" }, el("summary", {}, `켜고 끈 이력 (서버 기록 ${ev.length}건)`),
        ev.length ? el("table", { class: "ro" }, el("thead", {}, el("tr", {}, ["시각", "상태", "변경한 교사"].map(h => el("th", {}, h)))),
          el("tbody", {}, ev.slice(0, 15).map(e => el("tr", {}, el("td", {}, stamp(new Date(tsMs(e.at)))), el("td", {}, e.on ? "켬(수집 시작)" : "끔(수집 중지)"), el("td", {}, e.by || "—")))))
          : el("p", { class: "lead" }, "아직 이력이 없습니다."),
        el("p", { class: "lead", style: "font-size:13px" }, "이력과 스위치는 서버 함수가 서버 시각으로 기록하며, 교사 화면에서도 직접 고치거나 지울 수 없습니다. 학생 화면에는 수집이 중지된 상태와 중지한 시각이 항상 표시됩니다.")));
  };

  /* --- 학생 AI 도우미 스위치 --- */
  const paintAi = () => {
    const on = !!(M.ai && M.ai.on);
    const re = recentChatErr();
    fill(vAi, el("h4", {}, "학생 AI 도우미"),
      re ? errBox(re) : null,
      el("p", { class: "lead" }, "켜면 학생의 학습지·교재 화면 오른쪽 아래에 AI 아이콘이 나타납니다. 학생은 글이나 사진으로 질문하고, AI는 학생이 지금 보고 있는 화면(교재의 절·학습지 문항)과 고른 글을 참고해 글로 답합니다. 학습지 문항은 정답을 바로 알려 주지 않고 힌트를 줍니다. 질문 횟수는 학생 한 명이 장(학습지는 주차)마다 기본 40번, 1분에 6번까지이며 기본값과 학생·장별 가감은 [AI 질문한도] 메뉴에서 바꿉니다. 학생과 AI가 주고받은 질문·답은 [AI 대화기록] 메뉴에 기록되고 [AI 사용량] 메뉴에 집계됩니다(사진 파일은 저장하지 않고, 사진을 보냈는지만 남깁니다). 질문·사진·화면의 글은 Google Gemini로 전달되고, 학생 화면에 그 사실과 기록된다는 사실이 안내됩니다."),
      M.ai === undefined ? el("p", { class: "lead" }, "상태를 확인하는 중…") : el("p", { class: on ? "status-open" : "status-closed" }, ico("circle", "fill"), on ? "켜짐 — 학생 화면에 AI 아이콘이 보입니다" : "꺼짐 — 학생 화면에 AI 아이콘이 없습니다"),
      el("button", { class: "btn primary", onclick: async e => { e.target.disabled = true; try { await FB.saveAssistant(!on); } catch (err) { alert("저장하지 못했습니다: " + errText(err)); } } }, on ? [ico("stop"), "AI 도우미 끄기"] : [ico("play_arrow"), "AI 도우미 켜기"]));
  };

  /* --- AI 사용량 화면: 기간(오늘·주간·월간·전체·직접 지정)별 반 전체·날짜별·학생별 --- */
  const SUM_KEYS = ["count", "refused", "errors", "images", "promptTokens", "outputTokens", "thoughtTokens", "totalTokens", "sugCount", "sugPrompt", "sugOutput", "sugThought", "sugTotal"];
  /* 토큰은 AI 도우미 질문(promptTokens…)과 교사의 AI 추천 답변(sug*)을 합쳐 보여 준다. count 는 질문 수, sugCount 는 추천 답변 수. */
  const fold = v => Object.assign({}, v, { promptTokens: v.promptTokens + v.sugPrompt, outputTokens: v.outputTokens + v.sugOutput, thoughtTokens: v.thoughtTokens + v.sugThought, totalTokens: v.totalTokens + v.sugTotal });
  const addDays = (d, n) => new Date(Date.parse(d + "T00:00:00Z") + n * 86400e3).toISOString().slice(0, 10);       // YYYY-MM-DD(한국 날짜 문자열)에 일수를 더한다
  const emptySum = () => Object.fromEntries(SUM_KEYS.map(k => [k, 0]));
  const sumDays = (byDay, from, to) => { const t = emptySum(); for (const [d, v] of Object.entries(byDay || {})) if (d >= from && d <= to) SUM_KEYS.forEach(k => { t[k] += Number(v[k]) || 0; }); return t; };
  const tokRange = () => {          // 현재 선택한 기간 → {all, from, to, label}
    const today = todayKst(), m = M.tokRange || "today";
    if (m === "all") return { all: true, from: "0000-00-00", to: "9999-99-99", label: "전체 기간" };
    if (m === "week") return { from: addDays(today, -6), to: today, label: "주간 (오늘 포함 최근 7일)" };
    if (m === "month") return { from: addDays(today, -29), to: today, label: "월간 (오늘 포함 최근 30일)" };
    if (m === "custom") { let f = M.tokFrom || today, t = M.tokTo || today; if (f > t) [f, t] = [t, f]; return { from: f, to: t, label: "지정한 기간" }; }
    return { from: today, to: today, label: "오늘" };
  };
  /* 예상 비용: 100만 토큰당 요금(USD, Gemini API 유료·표준, 2026-11 확인 https://aistudio.google.com/docs/pricing).
     학생 AI 도우미 모델(gemini-flash-lite-latest = Gemini 3.5 Flash-Lite 로 가정): 입력 $0.30, 출력(생각 토큰 포함) $2.50.
     요금·모델이 바뀌면 이 값과 안내 문구를 함께 고친다. 환율은 임의 가정값이다. */
  const PRICE = { model: "Gemini 3.5 Flash-Lite", inUsd: 0.30, outUsd: 2.50, krwPerUsd: 1450 };
  const costUsd = v => (v.promptTokens * PRICE.inUsd + (v.outputTokens + v.thoughtTokens) * PRICE.outUsd) / 1e6;
  const usd = x => "$" + (x >= 1 ? x.toFixed(2) : x.toFixed(4));
  const money = x => `${usd(x)} (약 ${nf(Math.round(x * PRICE.krwPerUsd))}원)`;
  const paintTok = () => {
    const st = M.stats || {}, today = todayKst(), R = tokRange();
    const tot = fold(R.all ? Object.fromEntries(SUM_KEYS.map(k => [k, Number(st[k]) || 0])) : sumDays(st.byDay, R.from, R.to));
    const days = Object.entries(st.byDay || {}).filter(([d]) => d >= R.from && d <= R.to).map(([d, v]) => [d, fold(Object.fromEntries(SUM_KEYS.map(k => [k, Number(v[k]) || 0])))]).sort((a, b) => b[0].localeCompare(a[0]));
    const rows = (M.usage || []).map(u => { const v = fold(R.all ? Object.fromEntries(SUM_KEYS.map(k => [k, Number(u["total_" + k]) || 0])) : sumDays(u.byDay, R.from, R.to)); return { u, v }; })
      .filter(r => r.v.count + r.v.sugCount > 0).sort((a, b) => b.v.totalTokens - a.v.totalTokens);
    // 학생별 날짜 집계는 이 기능을 넣은 뒤부터 쌓인다. 반 전체 합계와의 차이는 '날짜별 학생 집계가 없는 이전 사용량'으로 따로 보여 준다.
    const sumStu = rows.reduce((t, r) => { SUM_KEYS.forEach(k => { t[k] += r.v[k]; }); return t; }, emptySum());
    const older = R.all ? null : Object.fromEntries(SUM_KEYS.map(k => [k, Math.max(0, tot[k] - sumStu[k])]));
    const calls = v => v.count + v.sugCount;
    const seg = [["today", "오늘"], ["week", "주간"], ["month", "월간"], ["all", "전체"], ["custom", "기간 지정"]];
    const setRange = k => { M.tokRange = k; if (k === "custom") { M.tokFrom = M.tokFrom || addDays(today, -6); M.tokTo = M.tokTo || today; } paintTok(); };
    const dateIn = (key, val) => el("input", { type: "date", value: val, max: today, "aria-label": key === "tokFrom" ? "시작 날짜" : "끝 날짜", onchange: e => { if (e.target.value) { M[key] = e.target.value; paintTok(); } } });
    fill(vTok, el("h3", {}, "AI 사용량"),
      el("p", { class: "lead" }, "Gemini가 응답마다 알려 주는 입력·출력·생각 토큰 수를 학생별·날짜별로 쌓은 값입니다. 학생의 AI 도우미 질문과, 교사가 [학생 질문]에서 쓴 AI 추천 답변(그 학생 몫으로 집계)을 합친 값입니다. 날짜는 한국 시간 기준입니다."),
      el("p", { class: "lead", style: "font-size:13px" }, `예상 비용은 ${PRICE.model} 요금(100만 토큰당 입력 $${PRICE.inUsd.toFixed(2)} · 출력과 생각 토큰 $${PRICE.outUsd.toFixed(2)}, 2026년 11월 Google 공시 기준)으로 계산한 추정치이고 원화는 1달러=${nf(PRICE.krwPerUsd)}원으로 가정했습니다. 실제 청구액과 다를 수 있으니 Google AI Studio의 결제 화면으로 확인하세요.`),
      M.logErr ? el("div", { class: "err-box" }, el("b", {}, ico("error", "fill"), "집계를 읽지 못했습니다."), el("div", {}, M.logErr)) : null,
      el("div", { class: "seg", role: "group", "aria-label": "기간 선택" }, seg.map(([k, l]) => el("button", { type: "button", class: "seg-b", "aria-pressed": String((M.tokRange || "today") === k), onclick: () => setRange(k) }, l))),
      (M.tokRange || "today") === "custom" ? el("div", { style: "display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin:8px 0" }, dateIn("tokFrom", R.from), "부터", dateIn("tokTo", R.to), "까지") : null,
      el("p", { class: "lead", style: "margin:8px 0" }, R.all ? "기간: 전체 (지금까지 쌓인 모든 사용량)" : R.from === R.to ? `기간: ${R.label} (${R.from})` : `기간: ${R.label} — ${R.from} ~ ${R.to}`),
      el("div", { class: "dlg-sum" },
        el("div", {}, el("b", {}, "AI 도우미 질문"), `${nf(tot.count)}건 (거절 ${nf(tot.refused)} · 오류 ${nf(tot.errors)} · 사진 ${nf(tot.images)})`),
        el("div", {}, el("b", {}, "AI 추천 답변"), `${nf(tot.sugCount)}건 (토큰 ${nf(tot.sugTotal)})`),
        el("div", {}, el("b", {}, "토큰 합계"), `${nf(tot.totalTokens)} (입력 ${nf(tot.promptTokens)} · 출력 ${nf(tot.outputTokens)} · 생각 ${nf(tot.thoughtTokens)})`),
        el("div", {}, el("b", {}, "AI를 쓴 학생"), R.all ? `${nf(rows.length)}명` : `${nf(rows.length)}명${older && calls(older) ? " 이상" : ""}`),
        el("div", {}, el("b", {}, "AI 호출 1건당 토큰"), calls(tot) ? nf(Math.round(tot.totalTokens / calls(tot))) : "—"),
        el("div", {}, el("b", {}, "예상 비용"), money(costUsd(tot))),
        el("div", {}, el("b", {}, "AI 호출 1건당 예상 비용"), calls(tot) ? money(costUsd(tot) / calls(tot)) : "—")),
      el("h4", {}, "날짜별"),
      days.length ? el("div", { style: "overflow-x:auto" }, el("table", { class: "ro" }, el("thead", {}, el("tr", {}, ["날짜", "질문", "추천 답변", "입력 토큰", "출력 토큰", "합계 토큰", "예상 비용"].map(h => el("th", {}, h)))),
        el("tbody", {}, days.slice(0, 120).map(([d, v]) => el("tr", {}, el("td", {}, d + (d === today ? " (오늘)" : "")), el("td", {}, nf(v.count)), el("td", {}, nf(v.sugCount)), el("td", {}, nf(v.promptTokens)), el("td", {}, nf(v.outputTokens)), el("td", {}, nf(v.totalTokens)), el("td", {}, usd(costUsd(v)))))))) : el("p", { class: "lead" }, "이 기간의 기록이 없습니다."),
      days.length > 120 ? el("p", { class: "lead" }, "최근 120일만 표시합니다.") : null,
      el("h4", {}, "학생별"),
      rows.length || (older && calls(older)) ? el("div", { style: "overflow-x:auto" }, el("table", { class: "ro" }, el("thead", {}, el("tr", {}, ["학생", "질문", "추천 답변", "거절", "입력 토큰", "출력 토큰", "합계 토큰", "예상 비용", "마지막 사용"].map(h => el("th", {}, h)))),
        el("tbody", {}, rows.map(({ u, v }) => el("tr", {}, el("td", {}, `${(u.student || {}).name || u.id}${(u.student || {}).email ? " · " + u.student.email.split("@")[0] : ""}`), el("td", {}, nf(v.count)), el("td", {}, nf(v.sugCount)), el("td", {}, nf(v.refused)),
          el("td", {}, nf(v.promptTokens)), el("td", {}, nf(v.outputTokens)), el("td", {}, nf(v.totalTokens)), el("td", {}, usd(costUsd(v))), el("td", {}, ago(tsMs(u.lastAt))))),
          older && calls(older) ? el("tr", { class: "tok-older" }, el("td", {}, "날짜별 학생 집계가 없는 이전 사용량"), el("td", {}, nf(older.count)), el("td", {}, nf(older.sugCount)), el("td", {}, nf(older.refused)), el("td", {}, nf(older.promptTokens)), el("td", {}, nf(older.outputTokens)), el("td", {}, nf(older.totalTokens)), el("td", {}, usd(costUsd(older))), el("td", {}, "—")) : null))) : el("p", { class: "lead" }, R.all ? "아직 AI 도우미를 쓴 학생이 없습니다." : "이 기간에 AI 도우미를 쓴 학생이 없습니다."),
      !R.all ? el("p", { class: "lead", style: "font-size:13px" }, "학생별 날짜 집계는 2026-11-04 이후의 사용량부터 쌓입니다. 그 전의 사용량은 반 전체 날짜별 집계에만 있어 위 표에 한 줄로 따로 나타나며, 학생별로는 [전체]에서만 볼 수 있습니다.") : null);
  };

  /* --- 대화 기록 화면: 쪽 나누기(서버 커서) + 학생·거절·오류·사진 필터(서버 쿼리) --- */
  const lg = M.lg;
  const resetLogs = () => { lg.page = 0; lg.cursors = [null]; lg.total = null; lg.rows = null; loadLogs(true); };
  async function loadLogs(withTotal) {
    const seq = ++lg.seq; lg.busy = true; lg.err = ""; paintLog();
    try {
      const o = { uid: lg.uid, kind: lg.kind, size: lg.size, after: lg.cursors[lg.page] };
      const [r, total] = await Promise.all([FB.chatLogsPage(o), withTotal ? FB.chatLogsCount(o) : Promise.resolve(undefined)]);
      if (seq !== lg.seq) return;                                  // 더 새 요청이 있으면 이 결과는 버린다
      lg.rows = r.rows; lg.more = r.more; if (r.more) lg.cursors[lg.page + 1] = r.last; if (total !== undefined) lg.total = total;
    } catch (e) {
      if (seq !== lg.seq) return;
      lg.rows = []; lg.more = false; lg.err = errText(e);
      if (/index/i.test(lg.err)) lg.err += " — 이 조건에 쓰는 색인을 만드는 중이거나 아직 배포하지 않았습니다. `firebase deploy --only firestore:indexes` 후 몇 분 뒤 다시 시도하세요.";
    }
    lg.busy = false; paintLog();
  }
  const goPage = n => { lg.page = n; loadLogs(false); scrollTo(0, 0); };
  const pager = () => {
    const pages = lg.total != null ? Math.max(1, Math.ceil(lg.total / lg.size)) : null, from = lg.page * lg.size + 1, n = (lg.rows || []).length;
    return el("div", { class: "pager" },
      el("button", { class: "btn small", disabled: lg.busy || lg.page === 0, onclick: () => goPage(0) }, ico("first_page"), "처음"),
      el("button", { class: "btn small", disabled: lg.busy || lg.page === 0, onclick: () => goPage(lg.page - 1) }, ico("chevron_left"), "이전"),
      el("span", { class: "pg-info" }, pages ? `${lg.page + 1} / ${pages}쪽` : `${lg.page + 1}쪽`, n ? ` · ${nf(from)}–${nf(from + n - 1)}번째` : "", lg.total != null ? ` · 총 ${nf(lg.total)}건` : ""),
      el("button", { class: "btn small", disabled: lg.busy || !lg.more, onclick: () => goPage(lg.page + 1) }, "다음", ico("chevron_right")));
  };
  const paintLog = () => {
    const rows = lg.rows || [], usage = (M.usage || []).filter(u => u.total_count > 0).slice().sort((a, b) => (b.total_totalTokens || 0) - (a.total_totalTokens || 0));
    const stuSel = el("select", { onchange: e => { lg.uid = e.target.value; resetLogs(); } }, el("option", { value: "" }, "전체 학생"),
      usage.map(u => el("option", { value: u.id, ...(u.id === lg.uid ? { selected: "" } : {}) }, `${(u.student || {}).name || u.id} (${u.total_count || 0}건)`)));
    const fltSel = el("select", { onchange: e => { lg.kind = e.target.value; resetLogs(); } }, [["all", "전체"], ["refused", "범위 밖(거절)만"], ["error", "오류만"], ["image", "사진 포함만"]].map(([v, l]) => el("option", { value: v, ...(v === lg.kind ? { selected: "" } : {}) }, l)));
    const sizeSel = el("select", { onchange: e => { lg.size = Number(e.target.value); resetLogs(); } }, [20, 50, 100].map(n => el("option", { value: n, ...(n === lg.size ? { selected: "" } : {}) }, `${n}건씩`)));
    fill(vLog, el("h3", {}, "AI 대화기록"),
      lg.err ? el("div", { class: "err-box" }, el("b", {}, ico("error", "fill"), "기록을 읽지 못했습니다."), el("div", {}, lg.err)) : null,
      el("div", { style: "display:flex;gap:12px;flex-wrap:wrap;align-items:center;margin:6px 0 10px" }, el("label", {}, "학생 ", stuSel), el("label", {}, "보기 ", fltSel), el("label", {}, "쪽당 ", sizeSel),
        el("button", { class: "btn small", disabled: lg.busy, onclick: () => loadLogs(true) }, ico("refresh"), "새로고침"),
        el("button", { class: "btn small danger", style: "margin-left:auto", onclick: async () => {
          if (!confirm("서버에 저장된 모든 AI 대화 기록을 삭제합니다(토큰 집계는 그대로 남습니다). 계속할까요?")) return;
          try { toast(`대화 기록 ${await FB.clearChatLogs()}건을 삭제했습니다`); resetLogs(); } catch (err) { alert("삭제하지 못했습니다: " + errText(err)); }
        } }, ico("delete"), "AI 대화기록 삭제")),
      el("p", { class: "lead", style: "font-size:13px" }, "최신 질문부터 보여 줍니다. 학생은 이 기록을 지우거나 고칠 수 없고(서버 규칙), 삭제는 교사만 할 수 있습니다. 오류만 걸러 보기는 이 기능을 넣은 뒤에 쌓인 기록부터 적용됩니다."),
      rows.length || lg.page > 0 ? pager() : null,
      lg.rows === null ? el("p", { class: "lead" }, "불러오는 중…") : null,
      rows.map(l => el("details", { class: "chatlog" + (l.error ? " bad" : "") },
        el("summary", {}, el("span", { class: "cl-time" }, stamp(new Date(tsMs(l.at)))), el("b", {}, stuName(l)), el("span", { class: "cl-q" }, l.question),
          l.refused ? el("span", { class: "pill part" }, "범위 밖") : null, l.error ? el("span", { class: "pill bad" }, "오류") : null, l.hasImage ? el("span", { class: "pill none" }, ico("image"), "사진") : null,
          el("small", { class: "cl-tok" }, `${nf((l.usage || {}).total)} 토큰`)),
        el("div", { class: "cl-body" },
          el("div", { class: "cl-meta" }, `${l.kind === "worksheet" ? "학습지" : "교재"} · ${l.where || "—"} · 입력 ${nf((l.usage || {}).prompt)} / 출력 ${nf((l.usage || {}).output)} / 생각 ${nf((l.usage || {}).thoughts)} · ${l.ms || 0}ms${l.hasImage ? ` · 사진 ${Math.round((l.imageBytes || 0) / 1024)}KB(파일은 저장하지 않음)` : ""}`),
          el("div", { class: "cl-row" }, el("b", {}, "학생 "), l.question),
          l.error ? el("div", { class: "cl-row err" }, el("b", {}, "오류 "), l.error) : el("div", { class: "cl-row" }, el("b", {}, "AI "), l.reply)))),
      lg.rows !== null && !rows.length && !lg.err ? el("p", { class: "lead" }, lg.page ? "이 쪽에는 기록이 없습니다." : lg.uid || lg.kind !== "all" ? "조건에 맞는 기록이 없습니다." : "아직 기록이 없습니다.") : null,
      rows.length > 8 ? pager() : null);
  };

  /* --- AI 질문한도 화면: 기본값 + 학생·장별 가감 --- */
  const MAXQ = 1000, DEFQ = 40;
  const CAPS = () => [...(CONTENT.chapters || []).map(c => [c.slug, c.title]), ...CONTENT.weeks.map(w => ["week" + w.n, `학습지 ${w.n}주차`]), ["etc", "기타 화면"]];
  const baseLimit = () => { const n = M.ai && M.ai.limit; return Number.isInteger(n) && n >= 0 && n <= MAXQ ? n : DEFQ; };
  const signed = n => (n > 0 ? "+" : n < 0 ? "−" : "") + Math.abs(n);
  const quotaOf = uid => ((M.quota || []).find(q => q.id === uid)) || {};
  const limitOf = (q, slug) => Math.max(0, baseLimit() + (Number(q.all) || 0) + (Number((q.chapters || {})[slug]) || 0));
  async function adjustQuota(uid, cap, cur, step, btn) {
    const v = step === null ? 0 : Math.max(-MAXQ, Math.min(MAXQ, cur + step));
    if (v === cur) return;
    btn.disabled = true;
    try { await FB.setAssistantQuota(uid, cap, v); } catch (err) { alert("바꾸지 못했습니다: " + errText(err)); btn.disabled = false; }      // 성공하면 실시간 구독이 화면을 다시 그린다
  }
  function quotaBody(uid, u) {
    const q = quotaOf(uid), used = (u && u.chapters) || {};
    const btns = (cap, cur) => el("span", { class: "qbtns" }, [[-10, "−10"], [-1, "−1"], [1, "+1"], [10, "+10"]].map(([d, t]) => el("button", { type: "button", class: "btn small", onclick: e => adjustQuota(uid, cap, cur, d, e.currentTarget) }, t)),
      el("button", { type: "button", class: "btn small", disabled: !cur, title: "가감을 없애고 기본 한도로", onclick: e => adjustQuota(uid, cap, cur, null, e.currentTarget) }, "초기화"));
    const row = (cap, label, usedN, lim, cur) => el("tr", {}, el("td", {}, label), el("td", {}, usedN == null ? "—" : nf(usedN)), el("td", {}, lim == null ? "—" : `${nf(lim)}${usedN != null && usedN >= lim ? " (소진)" : ""}`),
      el("td", { class: cur ? "qdelta" : "" }, cur ? signed(cur) : "0"), el("td", {}, btns(cap, cur)));
    const all = Number(q.all) || 0;
    return el("div", { style: "overflow-x:auto" }, el("table", { class: "ro" }, el("thead", {}, el("tr", {}, ["장(주차)", "쓴 횟수", "한도", "가감", "가감 바꾸기"].map(h => el("th", {}, h)))),
      el("tbody", {}, row("all", "모든 장 (전체에 더함)", null, baseLimit() + all, all), CAPS().map(([slug, title]) => row(slug, title, used[slug] || 0, limitOf(q, slug), Number((q.chapters || {})[slug]) || 0)))),
      el("p", { class: "lead", style: "font-size:12.5px" }, `한도 = 기본 ${baseLimit()}번 + 모든 장 가감 + 그 장 가감(0보다 작아지지 않음). 쓴 횟수는 줄지 않으므로 이미 다 쓴 학생에게는 가감을 + 로 올려 주면 바로 더 물을 수 있습니다.`));
  }
  const paintQuota = () => {
    const stu = new Map();
    (M.usage || []).forEach(u => stu.set(u.id, { student: u.student || {}, u }));
    (M.prog || []).forEach(r => { if (!stu.has(r.id)) stu.set(r.id, { student: r.student || {}, u: null }); });
    (M.quota || []).forEach(q => { if (!stu.has(q.id)) stu.set(q.id, { student: {}, u: null }); });
    const list = [...stu].map(([uid, v]) => ({ uid, ...v })).sort((a, b) => stuName(a).localeCompare(stuName(b), "ko", { numeric: true }));
    const limIn = el("input", { type: "number", min: 0, max: MAXQ, step: 1, value: baseLimit(), style: "width:90px", "aria-label": "장별 기본 질문 한도" });
    const nameOf = x => (stuName({ student: x.student }) === "(이름 없음)" ? x.uid : stuName({ student: x.student }));
    if (!list.some(x => x.uid === M.qSel)) M.qSel = "";                                               // 선택한 학생이 목록에 없으면 선택 해제
    const find = el("input", { type: "search", placeholder: "학생 이름·이메일 찾기", value: M.qFind, style: "width:100%", oninput: () => { M.qFind = find.value; applyFind(); } });
    const applyFind = () => { const t = M.qFind.trim().toLowerCase(); vQuota.querySelectorAll(".qlist [data-name]").forEach(b => { b.hidden = !!t && !b.dataset.name.includes(t); }); };
    const detail = el("div", { class: "qdetail" });
    const paintDetail = () => {
      const x = list.find(y => y.uid === M.qSel);
      if (!x) { fill(detail, el("p", { class: "lead" }, "왼쪽에서 학생을 고르면 그 학생의 한도를 바꾸는 화면이 여기에 나타납니다.")); return; }
      const q = quotaOf(x.uid), all = Number(q.all) || 0, caps = Object.values(q.chapters || {}).filter(Boolean).length;
      fill(detail, el("h4", {}, nameOf(x)), x.student && x.student.email ? el("p", { class: "lead", style: "font-size:12.5px;margin:0 0 6px" }, x.student.email) : null,
        el("p", { class: "lead", style: "font-size:12.5px" }, `모든 장 ${signed(all)}${caps ? ` · 장별 가감 ${caps}곳` : ""}`), quotaBody(x.uid, x.u));
    };
    const items = list.map(x => {
      const q = quotaOf(x.uid), all = Number(q.all) || 0, caps = Object.values(q.chapters || {}).filter(Boolean).length;
      const mark = all || caps ? "가감 있음" : "";
      return el("button", { type: "button", class: "qitem" + (x.uid === M.qSel ? " on" : ""), "data-name": (nameOf(x) + " " + ((x.student && x.student.email) || "")).toLowerCase(), "aria-pressed": x.uid === M.qSel ? "true" : "false",
        onclick: () => { M.qSel = x.uid; items.forEach(b => { const on = b === items[list.indexOf(x)]; b.classList.toggle("on", on); b.setAttribute("aria-pressed", on ? "true" : "false"); }); paintDetail(); } },
        el("span", {}, nameOf(x)), el("small", {}, mark));
    });
    fill(vQuota, el("h3", {}, "AI 질문한도"),
      el("p", { class: "lead" }, "학생 한 명이 AI 도우미에게 물을 수 있는 횟수를 장(교재의 한 장, 학습지의 한 주차)마다 따로 정합니다. 기본값은 모든 학생에게 같고, 학생별로 모든 장 또는 한 장의 한도를 늘리거나 줄일 수 있습니다. 1분에 6번까지라는 속도 제한은 따로 있습니다."),
      M.qErr ? el("div", { class: "err-box" }, el("b", {}, ico("error", "fill"), "한도 정보를 읽지 못했습니다."), el("div", {}, M.qErr)) : null,
      el("div", { class: "setrow" }, el("h4", {}, "기본 한도"),
        el("div", { style: "display:flex;gap:8px;align-items:center;flex-wrap:wrap" }, el("label", {}, "장마다 학생 한 명이 ", limIn, " 번까지"),
          el("button", { class: "btn primary", onclick: async e => {
            const n = Number(limIn.value); if (!Number.isInteger(n) || n < 0 || n > MAXQ) { alert(`0~${MAXQ} 사이의 정수를 입력하세요.`); return; }
            e.currentTarget.disabled = true; try { await FB.saveAssistantLimit(n); toast(`기본 한도를 ${n}번으로 저장했습니다`); } catch (err) { alert("저장하지 못했습니다: " + errText(err)); } e.currentTarget.disabled = false;
          } }, ico("save"), "저장")),
        el("p", { class: "lead", style: "font-size:13px" }, `기본값을 바꾸면 모든 학생에게 바로 적용됩니다(학생별 가감은 그대로 더해집니다). 0 으로 하면 AI 도우미를 쓸 수 없게 됩니다. 정하지 않으면 ${DEFQ}번입니다.`)),
      el("h4", {}, `학생별 (${list.length}명)`),
      list.length ? el("div", { class: "qsplit" }, el("div", { class: "qpick" }, find, el("div", { class: "qlist" }, items)), detail) : el("p", { class: "lead" }, "아직 AI 도우미를 쓰거나 진도를 보낸 학생이 없습니다."));
    paintDetail(); applyFind();
  };
  /* --- 학생 질문(선생님께 질문): 왼쪽 학생별 대화 목록(새 질문 배지), 오른쪽 대화와 답변 ---
     학생이 보낸 질문은 askThreads/{학생 uid} 에 쌓이고, 선생님이 열어 보면 '새 질문'이 읽음으로 바뀐다. 답변은 직접 쓰거나 [AI 추천 답변]으로 초안을 받아 고쳐서 보낸다(보내기 전에는 학생에게 가지 않는다). */
  const A = M.ask;
  function askUnread() { return (A.threads || []).reduce((n, t) => n + (Number(t.unread) || 0), 0); }
  const askThread = () => (A.threads || []).find(x => x.id === A.sel);
  const askSorted = () => [...(A.threads || [])].sort((a, b) => ((Number(b.unread) > 0) - (Number(a.unread) > 0)) || ((tsMs(b.lastAt) || 0) - (tsMs(a.lastAt) || 0)));
  const askListBox = el("div", { class: "ask-list", role: "list" }), askConvBox = el("div", { class: "ask-conv" }), askFoot = el("p", { class: "lead", style: "font-size:13px" });
  fill(vAsk, el("h3", {}, "학생 질문"),
    el("p", { class: "lead" }, "학생이 화면 오른쪽 아래의 [선생님께 질문] 아이콘으로 보낸 질문이 학생별 대화로 쌓입니다. 새 질문은 이 메뉴의 빨간 배지와 브라우저 탭 제목의 숫자로 알려 주고, 질문 개수에는 제한이 없습니다(도배를 막으려고 1분에 10번까지만 받습니다). 직접 답하거나 [AI 추천 답변]으로 초안을 받아 고쳐서 보낼 수 있고, 보내기 전에는 학생에게 전달되지 않습니다. AI 추천 답변은 질문 내용(이름·이메일 제외)을 Gemini로 보내므로 개인정보 동의에서 ‘AI 도우미 이용(선택)’에 동의한 학생에게만 쓸 수 있습니다."),
    el("div", { class: "ask-shell" }, el("div", {}, askListBox, askFoot), askConvBox));
  let conv = null;       // 열려 있는 대화의 화면 요소(답변 입력란은 대화를 고를 때 한 번만 만들어, 실시간 갱신에도 쓰던 글이 지워지지 않게 한다)

  const lightbox = src => {
    const close = () => { ov.remove(); document.removeEventListener("keydown", onKey); };
    const onKey = e => { if (e.key === "Escape") close(); };
    const ov = el("div", { class: "dlg-overlay", onclick: close }, el("img", { src, alt: "학생이 보낸 사진", class: "ask-big" }));
    document.addEventListener("keydown", onKey); document.body.append(ov);
  };
  function markAskRead() {      // 선택한 대화에 새 질문이 있고 이 화면을 보고 있으면 읽음으로 바꾼다
    const t = askThread();
    if (!t || !(Number(t.unread) > 0) || M.view !== "ask" || document.visibilityState !== "visible") return;
    const key = `${t.id}:${t.unread}`; if (A.marking === key) return;
    A.marking = key; FB.markAskRead(t.id).catch(() => { if (A.marking === key) A.marking = ""; });
  }
  function selectAsk(uid) {
    A.sel = uid; A.msgs = null; A.err = ""; A.marking = ""; conv = null;
    if (A.unMsgs) { try { A.unMsgs(); } catch (e) {} A.unMsgs = null; }
    paintAskList(); paintAsk();
    if (!uid) return;
    FB.watchAskMsgs(uid, (rows, err) => { if (A.sel !== uid) return; A.msgs = rows || []; A.err = err ? errText(err) : ""; paintAskMsgs(); })
      .then(f => { if (A.sel === uid && !A.unMsgs) A.unMsgs = f; else f(); }).catch(() => {});
    markAskRead();
  }
  function paintAskList() {
    const rows = askSorted();
    fill(askListBox, rows.length ? rows.map(t => {
      const un = Number(t.unread) || 0, wait = t.lastFrom === "student";
      return el("button", { type: "button", role: "listitem", class: "ask-item" + (A.sel === t.id ? " on" : ""), onclick: () => selectAsk(t.id) },
        el("span", { class: "ask-item-top" }, el("b", {}, stuName(t)), un ? el("span", { class: "nb bad" }, `새 질문 ${un}`) : wait ? el("span", { class: "nb" }, "답변 대기") : null),
        el("span", { class: "ask-item-last" }, (t.lastFrom === "teacher" ? "나: " : "") + (t.lastText || "")),
        el("small", {}, ago(tsMs(t.lastAt))));
    }) : el("p", { class: "lead", style: "padding:6px 8px" }, A.threads === null ? "불러오는 중…" : "아직 학생이 보낸 질문이 없어요."));
    const st = A.stats;
    askFoot.textContent = st ? `AI 추천 답변 사용 ${nf(st.suggestions)}회 · 토큰 ${nf(st.totalTokens)} (입력 ${nf(st.promptTokens)} · 출력 ${nf(st.outputTokens)} · 생각 ${nf(st.thoughtTokens)})` : "";
  }
  function paintAskMsgs() {
    if (!conv) return;
    const near = conv.box.scrollHeight - conv.box.scrollTop - conv.box.clientHeight < 80, first = !conv.shown; conv.shown = true;
    fill(conv.box, A.err ? el("div", { class: "err-box" }, A.err) : null,
      A.msgs === null ? el("p", { class: "lead" }, "불러오는 중…") : A.msgs.map(m => {
        if (m.from === "teacher") return el("div", { class: "ask-msg t" }, el("div", { class: "ask-meta" }, `${(m.by || "").split("@")[0] || "선생님"} · ${stamp(new Date(tsMs(m.at) || Date.now()))}`, m.viaAi ? el("span", { class: "nb", title: "AI 추천 답변을 바탕으로 보낸 답변입니다(학생 화면에는 표시되지 않습니다)" }, "AI 추천 사용") : null), el("div", { class: "ask-txt" }, m.text));
        const im = m.image && m.image.data ? `data:${m.image.mime};base64,${m.image.data}` : "";
        return el("div", { class: "ask-msg s" }, el("div", { class: "ask-meta" }, `학생 · ${stamp(new Date(tsMs(m.at) || Date.now()))}`),
          m.where ? el("div", { class: "ask-where" }, ico("visibility"), `${m.kind === "worksheet" ? "학습지" : "교재"} · ${m.where}`) : null,
          m.selection ? el("blockquote", { class: "ask-sel" }, m.selection) : null,
          im ? el("img", { src: im, alt: "학생이 보낸 사진(눌러서 크게 보기)", class: "ask-img", title: "눌러서 크게 보기", onclick: () => lightbox(im) }) : m.hasImage ? el("div", { class: "lead" }, "(사진)") : null,
          m.text ? el("div", { class: "ask-txt" }, m.text) : null);
      }));
    if (first || near) conv.box.scrollTop = conv.box.scrollHeight;
  }
  function paintAsk() {
    const t = askThread();
    if (!A.sel || !t) { conv = null; fill(askConvBox, el("p", { class: "lead" }, A.sel ? "대화를 찾을 수 없어요(삭제되었을 수 있어요)." : "왼쪽에서 학생을 고르면 질문과 답변이 보여요.")); return; }
    if (conv && conv.uid === A.sel) { conv.sync(); return; }
    const uid = A.sel, box = el("div", { class: "ask-msgs", role: "log" }), note = el("p", { class: "ask-ai-note", hidden: true });
    const ta = el("textarea", { class: "ask-ta", rows: 4, placeholder: "답변을 입력하세요. (Ctrl+Enter: 보내기)", "aria-label": "답변 입력" });
    ta.value = A.draft[uid] || "";
    ta.addEventListener("input", () => { A.draft[uid] = ta.value; if (!ta.value.trim()) { A.via[uid] = false; A.cau[uid] = ""; } c.sync(); });
    ta.addEventListener("keydown", e => { if (e.key === "Enter" && (e.ctrlKey || e.metaKey) && !e.isComposing) { e.preventDefault(); sendReply(); } });
    const aiBtn = el("button", { type: "button", class: "btn", onclick: () => suggest() }, ico("auto_awesome"), "AI 추천 답변");
    const sendBtn = el("button", { type: "button", class: "btn primary", onclick: () => sendReply() }, ico("send"), "답변 보내기");
    const c = conv = { uid, box, ta, shown: false, sync() {
      const th = (A.threads || []).find(x => x.id === uid);
      aiBtn.disabled = c.busyAi || !th || th.lastFrom !== "student";
      aiBtn.title = th && th.lastFrom !== "student" ? "학생의 새 질문이 없어서 추천 답변을 만들 수 없어요" : "학생과 주고받은 대화로 답변 초안을 만들어 입력란에 넣어 줘요(보내기 전에 고칠 수 있어요)";
      sendBtn.disabled = c.busySend || !ta.value.trim();
      note.hidden = !A.via[uid]; fill(note, ico("auto_awesome", "fill"), "AI 추천 답변을 바탕으로 한 글이에요. 보내기 전에 내용이 맞는지 읽고 고쳐 주세요.", A.cau[uid] ? el("div", { class: "ask-caution" }, ico("warning", "fill"), "AI가 짚은 확인 사항: " + A.cau[uid]) : null);
    } };
    async function suggest() {
      if (ta.value.trim() && !confirm("입력한 내용을 AI 추천 답변으로 바꿀까요?")) return;
      c.busyAi = true; aiBtn.disabled = true; aiBtn.replaceChildren(ico("hourglass_top"), "만드는 중…");
      try { const r = await FB.suggestReply(uid); A.draft[uid] = r.draft; A.via[uid] = true; A.cau[uid] = r.caution || ""; if (conv === c) ta.value = r.draft; }
      catch (e) { alert("AI 추천 답변을 만들지 못했습니다: " + errText(e)); }
      c.busyAi = false; aiBtn.replaceChildren(ico("auto_awesome"), "AI 추천 답변"); if (conv === c) c.sync();
    }
    async function sendReply() {
      const text = ta.value.trim(); if (!text || c.busySend) return;
      c.busySend = true; c.sync();
      try { await FB.replyToStudent(uid, text, !!A.via[uid]); A.draft[uid] = ""; A.via[uid] = false; A.cau[uid] = ""; if (conv === c) ta.value = ""; toast("답변을 보냈습니다"); }
      catch (e) { alert("답변을 보내지 못했습니다: " + errText(e)); }
      c.busySend = false; if (conv === c) c.sync();
    }
    fill(askConvBox,
      el("div", { class: "ask-head" }, el("h4", { style: "margin:0" }, stuName(t)),
        el("button", { type: "button", class: "btn small danger", title: "이 학생과의 질문·답변 기록을 모두 지웁니다", onclick: async () => {
          if (!confirm(`${(t.student || {}).name || uid}(${(t.student || {}).email || ""})와 주고받은 질문·답변을 모두 삭제합니다. 학생 화면에서도 사라지며 되돌릴 수 없습니다. 계속할까요?`)) return;
          try { await FB.deleteAskThread(uid); toast("대화를 삭제했습니다"); } catch (e) { alert("삭제하지 못했습니다: " + errText(e)); }
        } }, ico("delete"), "대화 삭제")),
      box, note, ta, el("div", { class: "ask-actions" }, aiBtn, sendBtn));
    c.sync(); paintAskMsgs();
  }

  const paintChat = () => { paintTok(); paintLog(); paintAi(); if (M.view === "quota") paintQuota(); paintNav(); };

  /* --- 진도 표: 교재 장별 읽기 진도(분류별로 묶음) + 학습지 진행 --- */
  /* --- 학생 코드 화면: 학생이 교재 코드 편집기에서 단 주석·고친 코드(codeNotes) --- */
  const C = M.code;
  const chapterLabel = page => { const slug = page.replace(/-full$/, ""), ch = (CONTENT.chapters || []).find(c => c.slug === slug); return (ch ? ch.title : page) + (/-full$/.test(page) ? " (긴 버전)" : ""); };
  async function loadCode(uid) {
    const seq = ++C.seq; C.blocks = null; C.err = ""; paintCode();
    try { const rows = await FB.loadStudentCode(uid); if (seq !== C.seq) return; C.blocks = rows; }
    catch (e) { if (seq !== C.seq) return; C.blocks = []; C.err = errText(e); }
    paintCode();
  }
  const selectCode = uid => { C.sel = uid; if (uid) loadCode(uid); else { C.seq++; C.blocks = null; paintCode(); } };
  function paintCode() {
    const list = (C.students || []).slice().sort((a, b) => (tsMs(b.updatedAt) || 0) - (tsMs(a.updatedAt) || 0)), cur = list.find(x => x.id === C.sel);
    const blocks = (C.blocks || []).slice().sort((a, b) => a.page.localeCompare(b.page) || (a.kind === b.kind ? a.idx - b.idx : a.kind === "code" ? -1 : 1));
    const marked = blocks.filter(b => b.addedN > 0).length;
    const block = b => el("details", { class: "code-blk", ...(b.addedN > 0 ? { open: "" } : {}) },
      el("summary", {}, el("b", {}, chapterLabel(b.page)), " · ", b.kind === "exercise" ? "연습문제 " : "", b.title, " ", b.addedN > 0 ? el("span", { class: "nb ok" }, `고치거나 쓴 줄 ${b.addedN}`) : el("span", { class: "nb" }, "원본과 같음"), el("small", { style: "margin-left:8px;color:var(--dim)" }, ago(tsMs(b.updatedAt)))),
      b.addedN > 0 ? el("div", {}, el("div", { class: "code-cap" }, "학생이 새로 쓰거나 고친 줄"), el("pre", { class: "code-added" }, b.added)) : null,
      el("details", { class: "code-full" }, el("summary", {}, "고친 코드 전체 보기"), el("pre", { class: "code-all" }, b.code)));
    fill(vCode, el("h3", {}, "학생 코드"),
      el("p", { class: "lead" }, "학생이 교재의 코드 편집기에서 주석(#)을 달거나 고친 코드입니다. 입력하는 대로 자동 저장되어 이 화면에 나타납니다(학생이 학교 계정으로 로그인하고 개인정보 동의를 한 경우). 원본과 다른 줄만 따로 보여 주고, 코드 전체는 펼쳐서 봅니다. 학생이 [처음 코드]로 되돌리면 그 블록의 기록은 사라집니다."),
      C.students === null ? el("p", { class: "lead" }, "불러오는 중…") : null,
      el("div", { class: "ask-shell" },
        el("div", { class: "ask-list", role: "list", "aria-label": "코드를 고친 학생" }, list.length ? list.map(x => el("button", { type: "button", role: "listitem", class: "ask-item" + (C.sel === x.id ? " on" : ""), onclick: () => selectCode(x.id) },
          el("span", { class: "ask-item-top" }, el("b", {}, stuName(x))), el("small", {}, "마지막 저장 " + ago(tsMs(x.updatedAt))))) : el("p", { class: "lead", style: "padding:6px 8px" }, C.students === null ? "" : "아직 코드를 저장한 학생이 없어요.")),
        el("div", {}, !cur ? el("p", { class: "lead" }, "왼쪽에서 학생을 고르세요.")
          : [el("div", { style: "display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin-bottom:8px" }, el("b", {}, stuName(cur)),
              C.blocks ? el("span", { class: "nb" }, `블록 ${blocks.length}개 · 고친 곳 ${marked}개`) : null, el("span", { style: "flex:1" }),
              el("button", { type: "button", class: "btn small", title: "이 학생의 코드 저장 기록을 모두 지웁니다(수업이 끝난 뒤 개인정보 삭제용).", onclick: async () => {
                if (!confirm(`${stuName(cur)} 학생의 코드 저장 기록을 모두 지울까요? 되돌릴 수 없습니다.`)) return;
                try { await FB.deleteStudentCode(cur.id); toast("지웠습니다."); selectCode(""); } catch (e) { alert("지우지 못했습니다: " + errText(e)); }
              } }, ico("delete"), "코드 기록 삭제")),
            C.err ? el("div", { class: "err-box" }, C.err) : null,
            C.blocks === null ? el("p", { class: "lead" }, "불러오는 중…") : blocks.length ? el("div", {}, blocks.map(block)) : el("p", { class: "lead" }, "저장된 블록이 없어요.")])));
  }

  const paintTbl = () => {
    const rows = (M.prog || []).slice(), chs = (CONTENT.chapters || []).filter(c => M.group === "all" || c.group === M.group);
    const key = r => `${r.student.name || "(이름 없음)"}${r.student.email ? " · " + r.student.email.split("@")[0] : ""}`;       // 학생 = 로그인 계정(이름·이메일)
    const cell = (r, c) => { const x = (r.chapters || {})[c.slug]; return x && x.total ? Math.min(1, x.n / x.total) : 0; };
    const readAvg = r => { const all = CONTENT.chapters || []; return all.length ? all.reduce((a, c) => a + cell(r, c), 0) / all.length : 0; };
    const wsTotal = CONTENT.weeks.reduce((a, w) => a + weekProgress(w, {}).total, 0);
    const wsDone = r => Object.values(r.weeks || {}).reduce((a, w) => a + (w.n || 0), 0);
    rows.sort(M.sort === "slow" ? (a, b) => readAvg(a) - readAvg(b)
      : M.sort === "idle" ? (a, b) => (tsMs(a.lastActiveAt) || 0) - (tsMs(b.lastActiveAt) || 0)
      : (a, b) => key(a).localeCompare(key(b), "ko", { numeric: true }));
    // 개인정보 동의 기록(consents/{uid}): 진도 행의 id(uid)로 찾는다. 동의가 없는 학생의 행은 동의 제도 이전에 쌓인 기록이거나 철회한 경우다.
    const cons = new Map((M.consents || []).map(c => [c.id, c])), consOk = r => cons.has(r.id);
    const consList = (M.consents || []).slice().sort((a, b) => (tsMs(b.agreedAt) || 0) - (tsMs(a.agreedAt) || 0));
    const cnt = { ok: 0, part: 0, none: 0 }; rows.forEach(r => { cnt[liveState(tsMs(r.lastActiveAt))[0]]++; });
    const grpSel = el("select", { onchange: e => { M.group = e.target.value; paintTbl(); } }, [["all", "전체"], ...Object.entries(GROUP_NAME)].map(([v, l]) => el("option", { value: v, ...(v === M.group ? { selected: "" } : {}) }, l)));
    const sortSel = el("select", { onchange: e => { M.sort = e.target.value; paintTbl(); } }, [["num", "번호순"], ["slow", "교재 진도 느린 순"], ["idle", "활동 오래된 순"]].map(([v, l]) => el("option", { value: v, ...(v === M.sort ? { selected: "" } : {}) }, l)));
    // 분류 머리줄: 같은 분류의 장을 한 칸으로 묶는다
    const groupHead = []; chs.forEach(c => { const last = groupHead[groupHead.length - 1]; if (last && last.g === c.group) last.n++; else groupHead.push({ g: c.group, n: 1 }); });
    // 상태가 바뀔 때마다 표를 새로 그리므로, 그리기 전의 가로·세로 스크롤 위치와 '동의 현황' 펼침 상태를 기억했다가 되돌린다(안 그러면 표가 맨 왼쪽으로 돌아간다).
    const shown = !vProg.hidden, oldWrap = tbl.querySelector(".prog-wrap"), keepX = oldWrap ? oldWrap.scrollLeft : 0, keepY = window.scrollY, keepPX = window.scrollX, keepOpen = !!tbl.querySelector("details[open]");
    fill(tbl, el("h3", {}, "진도표"),
      M.mon !== undefined && !(M.mon && M.mon.on) ? el("div", { class: "note-box" }, ico("info"), "진도 수집이 꺼져 있어 새 진도는 들어오지 않습니다. ", el("button", { type: "button", class: "btn small", onclick: () => go("settings") }, "환경설정으로 가기")) : null,
      M.progErr ? el("div", { class: "err-box" }, el("b", {}, ico("error", "fill"), "진도를 읽지 못했습니다."), el("div", {}, M.progErr),
        /permission|insufficient/i.test(M.progErr) ? el("div", {}, "Firestore 규칙이 이 계정을 교사로 인정하지 않는 경우입니다. 콘솔에서 config/teachers 문서의 emails 가 ‘배열(array)’ 유형인지, 지금 로그인한 이메일이 소문자·공백 없이 들어 있는지 확인하세요.") : null) : null,
      M.prog === null ? el("p", { class: "lead" }, "불러오는 중…") : el("p", { class: "lead" }, `접속 기록 ${rows.length}명 · 활동 중 ${cnt.ok} · 잠시 멈춤 ${cnt.part} · 멈춤 ${cnt.none}`),
      M.consents === null ? null : el("p", { class: "lead" }, `개인정보 동의 ${consList.length}명 (AI 도우미 선택 동의 ${consList.filter(c => c.ai === true).length}명)` + (rows.some(r => !consOk(r)) ? ` · 동의 없는 진도 기록 ${rows.filter(r => !consOk(r)).length}건` : "")),
      consList.length ? el("details", { style: "margin:4px 0 8px;font-size:13.5px", ...(keepOpen ? { open: "" } : {}) }, el("summary", { style: "cursor:pointer;font-weight:700" }, "개인정보 동의 현황"),
        el("div", { style: "overflow-x:auto" }, el("table", { class: "ro" }, el("thead", {}, el("tr", {}, ["학생", "이메일", "동의 일시", "AI 도우미(선택)", "문구 버전", "관리"].map(h => el("th", {}, h)))),
          el("tbody", {}, consList.map(c => el("tr", {}, el("td", {}, (c.student || {}).name || c.id), el("td", {}, (c.student || {}).email || ""), el("td", {}, tsMs(c.agreedAt) ? stamp(new Date(tsMs(c.agreedAt))) : "—"), el("td", {}, c.ai === true ? "동의" : "동의 안 함"), el("td", {}, c.version || ""),
            el("td", {}, el("button", { type: "button", class: "btn small", title: "이 학생의 동의 기록을 지웁니다. 학생은 다시 동의해야 하고, 그 전까지 진도 전송과 AI 질문이 막힙니다.", onclick: async () => {
              if (!confirm(`${(c.student || {}).name || c.id}(${(c.student || {}).email || ""})의 개인정보 동의를 초기화할까요?\n학생은 다시 동의해야 하고, 그 전까지 이 학생의 새 진도와 AI 질문은 서버가 받지 않습니다. 이미 쌓인 진도·대화 기록은 그대로입니다.`)) return;
              try { await FB.resetConsent(c.id); toast("동의를 초기화했습니다."); } catch (err) { alert("초기화하지 못했습니다: " + errText(err)); }
            } }, "동의 초기화")))))))) : null,
      consList.length ? el("p", { class: "lead", style: "font-size:13px;margin-top:0" }, "학생은 한 번 동의하면 스스로 철회할 수 없습니다(철회는 여기서 [동의 초기화]로 처리). 다만 ‘AI 도우미 이용(선택)’에 동의하지 않은 학생은 AI 도우미 창의 [AI 도우미 이용에 동의하기]로 나중에 직접 동의할 수 있습니다.") : null,
      el("p", { class: "lead", style: "font-size:13.5px" }, "칸의 숫자는 그 장에서 읽은 절의 비율이고 아래 작은 글씨는 그 장의 체류 시간입니다. 숫자를 누르면 절별 세부 정보를 볼 수 있습니다. 절이 화면 가운데에 2초 이상 머물면 읽은 것으로 세고, 체류 시간은 화면이 보이고 최근 60초 안에 조작이 있던 시간만 셉니다(줄어들지 않는 값). 교재의 호스팅 사본을 열어 읽을 때만 집계됩니다."),
      statusLegend(),
      el("div", { style: "display:flex;gap:12px;flex-wrap:wrap;margin:6px 0" }, el("label", {}, "분류 ", grpSel), el("label", {}, "정렬 ", sortSel)),
      !rows.length ? el("p", { class: "lead" }, "아직 진도를 보낸 학생이 없습니다. 수집을 켜고, 학생이 학교 Google 계정으로 로그인하면 나타납니다.")
        : el("div", { class: "prog-wrap", style: "overflow-x:auto" }, el("table", { class: "ro prog" },
          el("thead", {},
            el("tr", {}, ["학생", "동의", "상태", "화면", "마지막 활동", "지금 있는 곳", "학습지", "활동 시간"].map(h => el("th", { rowspan: 2 }, h)), groupHead.map(h => el("th", { colspan: h.n, style: "text-align:center" }, GROUP_NAME[h.g]))),
            el("tr", {}, chs.map(c => el("th", { style: "font-weight:600;white-space:nowrap" }, c.title)))),
          el("tbody", {}, rows.map(r => {
            const ms = tsMs(r.lastActiveAt), [cls, lab] = liveState(ms), wp = wsTotal ? Math.round(100 * wsDone(r) / wsTotal) : 0;
            const cs = cons.get(r.id);
            return el("tr", {}, el("td", { style: "white-space:nowrap" }, key(r)),
              el("td", { style: "white-space:nowrap" }, M.consents === null ? "…" : cs ? el("span", { class: "pill ok", title: `개인정보 수집·이용 동의 ${tsMs(cs.agreedAt) ? stamp(new Date(tsMs(cs.agreedAt))) : ""} · AI 도우미(선택) ${cs.ai === true ? "동의" : "동의 안 함"}` }, ico("verified_user", "fill"), cs.ai === true ? "동의 · AI" : "동의")
                : el("span", { class: "pill bad", title: "동의 기록이 없습니다(동의 제도 이전에 쌓인 기록이거나 철회). 이 학생의 새 진도는 서버가 받지 않습니다." }, ico("gpp_maybe", "fill"), "동의 없음")),
              el("td", {}, el("span", { class: "pill " + cls }, ico(cls === "ok" ? "check_circle" : cls === "part" ? "pause_circle" : "do_not_disturb_on", "fill"), lab)),
              el("td", { style: "white-space:nowrap" }, viewCell(r)),
              el("td", { style: "white-space:nowrap" }, ago(ms)), el("td", { style: "white-space:nowrap" }, r.where || "—"), el("td", {}, `${wp}%`), el("td", {}, `${Math.round((r.activeMs || 0) / 60000)}분`),
              chs.map(c => {
                const f = cell(r, c), pct = Math.round(100 * f), x = (r.chapters || {})[c.slug];
                return el("td", { style: `text-align:center;background:linear-gradient(90deg,var(--ok-soft) ${pct}%,transparent ${pct}%)` },
                  x ? el("button", { type: "button", class: "pct", title: `${c.title} 세부 정보 보기`, onclick: () => openDetail(r, c) }, f ? pct + "%" : "0%", x.sec ? el("small", {}, fmtDur(x.sec)) : null) : "—");
              }));
          })))));
    // html 에 scroll-behavior:smooth 가 있어 그냥 scrollTo 는 천천히 움직이므로 behavior 를 instant 로 준다.
    if (shown) { const w = tbl.querySelector(".prog-wrap"); if (w) w.scrollLeft = keepX; if (window.scrollY !== keepY || window.scrollX !== keepPX) window.scrollTo({ left: keepPX, top: keepY, behavior: "instant" }); }
  };

  paintCtl(); paintAi(); paintTok(); paintLog(); paintTbl(); paintCode(); paintAskList(); paintAsk(); paintNav(); if (M.view === "quota") paintQuota(); loadLogs(true);
  document.addEventListener("visibilitychange", markAskRead);
  liveSub(FB.watchMonitor(s => { M.mon = s; paintCtl(); paintNav(); }), tok);
  liveSub(FB.watchAskThreads((rows, err) => {
    A.threads = rows || []; if (err) A.err = errText(err);
    if (A.sel && !askThread()) selectAsk("");                                      // 선택한 대화가 삭제되었다
    const t = askThread(); if (t && !(Number(t.unread) > 0)) A.marking = "";
    paintAskList(); paintAsk(); paintNav(); markAskRead();
  }), tok);
  liveSub(FB.watchAskStats(s => { A.stats = s; paintAskList(); }), tok);
  liveSub(FB.watchCodeStudents((rows, err) => {
    const prev = (C.students || []).find(x => x.id === C.sel);
    C.students = rows || []; if (err) { C.err = errText(err); }
    const now = C.students.find(x => x.id === C.sel);
    if (C.sel && !now) selectCode(""); else if (now && prev && tsMs(now.updatedAt) !== tsMs(prev.updatedAt)) loadCode(C.sel);      // 선택한 학생이 새로 저장하면 다시 읽는다
    else paintCode();
  }), tok);
  liveSub(FB.watchMonitorEvents((rows, err) => { M.events = rows || []; paintCtl(); }), tok);
  liveSub(FB.watchAssistant(s => { M.ai = s; paintAi(); paintNav(); }), tok);
  liveSub(FB.watchStats((s, err) => {
    M.stats = s; if (err) M.logErr = errText(err);
    const c = s && s.count; if (c !== M.statCount) { const first = M.statCount === undefined; M.statCount = c; if (!first && lg.page === 0 && !lg.busy && lg.rows !== null) loadLogs(true); }      // 새 질문이 들어오면 첫 쪽을 자동으로 새로 읽는다
    paintChat();
  }), tok);
  liveSub(FB.watchChatQuota((rows, err) => { M.quota = rows || []; M.qErr = err ? errText(err) : ""; if (M.view === "quota") paintQuota(); }), tok);
  liveSub(FB.watchChatUsage((rows, err) => { M.usage = rows || []; if (err) M.logErr = errText(err); paintChat(); }), tok);
  liveSub(FB.watchChatLogs((rows, err) => { M.logs = rows || []; M.logErr = err ? errText(err) : ""; paintChat(); }, 30), tok);      // 최근 30건: 오류 알림용(전체 목록은 쪽 나누기로 따로 읽는다)
  liveSub(FB.watchConsents((rows, err) => { M.consents = rows || []; if (err) M.progErr = M.progErr || errText(err); paintTbl(); }), tok);
  liveSub(FB.watchProgress((rows, err) => { M.prog = rows || []; M.progErr = err ? errText(err) : ""; paintTbl(); paintNav(); paintCtl(); }), tok);
  const timer = setInterval(paintTbl, 20000); T.live.push(() => clearInterval(timer));
}

/* 시작: 파일 맨 끝에서 부른다(위의 const·함수가 모두 만들어진 뒤여야 한다). */
if (GATED) gate(); else boot();
