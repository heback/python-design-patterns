"use strict";
/* 교사용 앱(디자인 패턴 학습 관리): 학교 Google 계정으로 로그인한 교사가 학생 진도를 실시간으로 본다.
   학생 응답 본문은 서버로 오지 않으므로 응답 검토·코멘트·제출 관리 화면은 없다. */
const M = { view: "", events: null, prog: null, progErr: "", mon: undefined, ai: undefined, stats: undefined, usage: null, logs: null, logErr: "", logStu: "", logFilter: "all", group: "all", sort: "num" };   // 진도 화면의 상태(boot 보다 먼저 있어야 한다)
const T = { live: [], liveTok: null };   // 실시간 구독 해제 함수 목록

let booted = false;
function boot() {
  if (booted) return; booted = true;
  initTheme();
  $("#btn-print").addEventListener("click", () => print());
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
function stopLive() { (T.live || []).forEach(f => { try { f(); } catch (e) {} }); T.live = []; T.liveTok = null; M.unAns = null; }
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
   마지막으로 보낸 값이므로, 학생이 오래 아무것도 하지 않으면(상태 '멈춤') 실제와 다를 수 있다. */
const VIEW = { on: ["ok", "check_circle", "보는 중"], hidden: ["bad", "tab_unselected", "다른 탭"], blur: ["part", "open_in_new", "다른 창"] };
function viewCell(r) {
  const v = VIEW[r.view]; if (!v) return "—";
  const since = tsMs(r.viewAt), mins = since ? Math.floor((Date.now() - since) / 60000) : 0;
  const away = (r.leaves || 0) ? ` · 벗어남 ${r.leaves}회 · ${Math.round((r.awayMs || 0) / 60000)}분` : "";
  return el("span", {}, el("span", { class: "pill " + v[0] }, ico(v[1], "fill"), v[2] + (r.view !== "on" && mins >= 1 ? ` ${mins}분째` : "")), el("small", { style: "color:var(--dim)" }, away));
}
/* 마지막 활동으로부터: <2분 활동 중, <5분 잠시 멈춤, 그 이상 멈춤(자리 비움). 수업 중에만 의미가 있다. */
function liveState(ms) {
  const m = ms ? (Date.now() - ms) / 60000 : Infinity;
  return m < 2 ? ["ok", "활동 중"] : m < 5 ? ["part", "잠시 멈춤"] : ["none", "멈춤"];
}

function renderMonitor(main) {
  const tok = T.liveTok = {};
  /* 메뉴: 왼쪽(좁은 화면에서는 위쪽)에 메뉴를 두고, 한 번에 한 가지 기능만 보여 준다. 선택한 화면은 주소 해시(#progress …)와 이 브라우저에 기억한다. */
  /* 메뉴: 환경설정 · 진도표 · 대화기록 · 토큰 사용량 */
  const ctl = el("div", { class: "setrow" }), vAi = el("div", { class: "setrow" }), tbl = el("div", {});
  const vSet = el("section", { class: "panel", id: "v-settings" }, el("h3", {}, "환경설정"), ctl, vAi), vProg = el("section", { class: "panel", id: "v-progress" }, tbl),
    vLog = el("section", { class: "panel", id: "v-logs" }), vTok = el("section", { class: "panel", id: "v-tokens" });
  const VIEWS = [["settings", "settings", "환경설정", vSet], ["progress", "monitoring", "진도표", vProg], ["logs", "forum", "대화기록", vLog], ["tokens", "data_usage", "토큰 사용량", vTok]];
  const known = k => VIEWS.some(v => v[0] === k);
  if (!known(M.view)) { const h = location.hash.slice(1), saved = lsGet("dp-teacher-view"); M.view = known(h) ? h : known(saved) ? saved : "progress"; }
  const nav = el("nav", { class: "side", "aria-label": "교사 메뉴" });
  const paintNav = () => {
    const act = (M.prog || []).filter(r => liveState(tsMs(r.lastActiveAt))[0] === "ok").length, aiOn = !!(M.ai && M.ai.on), monOn = !!(M.mon && M.mon.on), err = !!recentChatErr();
    const badge = k => k === "progress" ? el("span", { class: "nb " + (monOn ? "ok" : "off"), title: monOn ? "수집 중(활동 중인 학생 수)" : "진도 수집이 꺼져 있어요" }, monOn ? `${act}명` : "수집 꺼짐")
      : k === "settings" ? (err ? el("span", { class: "nb bad", title: "최근 AI 호출 오류" }, "오류") : null)
      : k === "logs" ? (M.logs && M.logs.length ? el("span", { class: "nb" }, String(M.logs.length)) : null) : null;
    fill(nav, VIEWS.map(([k, ic, lab]) => el("button", { type: "button", class: "side-item", "aria-current": M.view === k ? "page" : null, onclick: () => go(k) }, ico(ic, M.view === k ? "fill" : ""), el("span", { class: "side-lab" }, lab), badge(k))));
  };
  const go = k => { M.view = k; lsSet("dp-teacher-view", k); try { history.replaceState(null, "", "#" + k); } catch (e) {} VIEWS.forEach(v => { v[3].hidden = v[0] !== k; }); paintNav(); scrollTo(0, 0); };
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
      el("p", { class: "lead" }, "켜면 학생의 학습지·교재 화면 오른쪽 아래에 AI 아이콘이 나타납니다. 학생은 글이나 사진으로 질문하고, AI는 학생이 지금 보고 있는 화면(교재의 절·학습지 문항)과 고른 글을 참고해 글로 답합니다. 학습지 문항은 정답을 바로 알려 주지 않고 힌트를 줍니다. 학생 한 명당 하루 40번·1분에 6번까지이며, 학생과 AI가 주고받은 질문·답은 [대화기록] 메뉴에 기록되고 [토큰 사용량] 메뉴에 집계됩니다(사진 파일은 저장하지 않고, 사진을 보냈는지만 남깁니다). 질문·사진·화면의 글은 Google Gemini로 전달되고, 학생 화면에 그 사실과 기록된다는 사실이 안내됩니다."),
      M.ai === undefined ? el("p", { class: "lead" }, "상태를 확인하는 중…") : el("p", { class: on ? "status-open" : "status-closed" }, ico("circle", "fill"), on ? "켜짐 — 학생 화면에 AI 아이콘이 보입니다" : "꺼짐 — 학생 화면에 AI 아이콘이 없습니다"),
      el("button", { class: "btn primary", onclick: async e => { e.target.disabled = true; try { await FB.saveAssistant(!on); } catch (err) { alert("저장하지 못했습니다: " + errText(err)); } } }, on ? [ico("stop"), "AI 도우미 끄기"] : [ico("play_arrow"), "AI 도우미 켜기"]));
  };

  /* --- 토큰 사용량 화면: 반 전체·오늘·날짜별·학생별 --- */
  const paintTok = () => {
    const st = M.stats || {}, today = todayKst(), td = (st.byDay || {})[today] || {};
    const usage = (M.usage || []).slice().sort((a, b) => (b.total_totalTokens || 0) - (a.total_totalTokens || 0));
    const days = Object.entries(st.byDay || {}).sort((a, b) => b[0].localeCompare(a[0]));
    fill(vTok, el("h3", {}, "토큰 사용량"),
      el("p", { class: "lead" }, "Gemini가 응답마다 알려 주는 입력·출력·생각 토큰 수를 학생별·날짜별로 쌓은 값입니다. 요금은 모델과 시점마다 달라 토큰 수만 보여 줍니다."),
      M.logErr ? el("div", { class: "err-box" }, el("b", {}, ico("error", "fill"), "집계를 읽지 못했습니다."), el("div", {}, M.logErr)) : null,
      el("div", { class: "dlg-sum" },
        el("div", {}, el("b", {}, "전체 질문"), `${nf(st.count)}건 (거절 ${nf(st.refused)} · 오류 ${nf(st.errors)} · 사진 ${nf(st.images)})`),
        el("div", {}, el("b", {}, "전체 토큰"), `${nf(st.totalTokens)} (입력 ${nf(st.promptTokens)} · 출력 ${nf(st.outputTokens)} · 생각 ${nf(st.thoughtTokens)})`),
        el("div", {}, el("b", {}, `오늘(${today.slice(5)})`), `${nf(td.count)}건 · ${nf(td.totalTokens)} 토큰`)),
      el("h4", {}, "날짜별"),
      days.length ? el("div", { style: "overflow-x:auto" }, el("table", { class: "ro" }, el("thead", {}, el("tr", {}, ["날짜", "질문", "입력 토큰", "출력 토큰", "합계 토큰"].map(h => el("th", {}, h)))),
        el("tbody", {}, days.map(([d, v]) => el("tr", {}, el("td", {}, d), el("td", {}, nf(v.count)), el("td", {}, nf(v.promptTokens)), el("td", {}, nf(v.outputTokens)), el("td", {}, nf(v.totalTokens))))))) : el("p", { class: "lead" }, "아직 기록이 없습니다."),
      el("h4", {}, "학생별"),
      usage.length ? el("div", { style: "overflow-x:auto" }, el("table", { class: "ro" }, el("thead", {}, el("tr", {}, ["학생", "질문", "거절", "입력 토큰", "출력 토큰", "합계 토큰", "마지막 사용"].map(h => el("th", {}, h)))),
        el("tbody", {}, usage.map(u => el("tr", {}, el("td", {}, `${(u.student || {}).name || u.id}${(u.student || {}).email ? " · " + u.student.email.split("@")[0] : ""}`), el("td", {}, nf(u.total_count)), el("td", {}, nf(u.total_refused)),
          el("td", {}, nf(u.total_promptTokens)), el("td", {}, nf(u.total_outputTokens)), el("td", {}, nf(u.total_totalTokens)), el("td", {}, ago(tsMs(u.lastAt)))))))) : el("p", { class: "lead" }, "아직 AI 도우미를 쓴 학생이 없습니다."));
  };

  /* --- 대화 기록 화면: 학생·거절·오류·사진으로 걸러 보기 --- */
  const paintLog = () => {
    const logs = M.logs || [], usage = (M.usage || []).slice().sort((a, b) => (b.total_totalTokens || 0) - (a.total_totalTokens || 0));
    const shown = logs.filter(l => (!M.logStu || l.uid === M.logStu) && (M.logFilter === "all" || (M.logFilter === "refused" ? l.refused : M.logFilter === "error" ? l.error : l.hasImage)));
    const stuSel = el("select", { onchange: e => { M.logStu = e.target.value; paintLog(); } }, el("option", { value: "" }, "전체 학생"),
      usage.map(u => el("option", { value: u.id, ...(u.id === M.logStu ? { selected: "" } : {}) }, `${(u.student || {}).name || u.id} (${u.total_count || 0}건)`)));
    const fltSel = el("select", { onchange: e => { M.logFilter = e.target.value; paintLog(); } }, [["all", "전체"], ["refused", "범위 밖(거절)만"], ["error", "오류만"], ["image", "사진 포함만"]].map(([v, l]) => el("option", { value: v, ...(v === M.logFilter ? { selected: "" } : {}) }, l)));
    fill(vLog, el("h3", {}, "대화기록"),
      M.logErr ? el("div", { class: "err-box" }, el("b", {}, ico("error", "fill"), "기록을 읽지 못했습니다."), el("div", {}, M.logErr)) : null,
      el("div", { style: "display:flex;gap:12px;flex-wrap:wrap;align-items:center;margin:6px 0 10px" }, el("label", {}, "학생 ", stuSel), el("label", {}, "보기 ", fltSel),
        el("small", { class: "lead" }, `최근 ${logs.length}건 중 ${shown.length}건`),
        el("button", { class: "btn small danger", style: "margin-left:auto", onclick: async () => {
          if (!confirm("서버에 저장된 모든 AI 대화 기록을 삭제합니다(토큰 집계는 그대로 남습니다). 계속할까요?")) return;
          try { toast(`대화 기록 ${await FB.clearChatLogs()}건을 삭제했습니다`); } catch (err) { alert("삭제하지 못했습니다: " + errText(err)); }
        } }, ico("delete"), "대화기록 삭제")),
      shown.length ? shown.slice(0, 60).map(l => el("details", { class: "chatlog" + (l.error ? " bad" : "") },
        el("summary", {}, el("span", { class: "cl-time" }, stamp(new Date(tsMs(l.at)))), el("b", {}, stuName(l)), el("span", { class: "cl-q" }, l.question),
          l.refused ? el("span", { class: "pill part" }, "범위 밖") : null, l.error ? el("span", { class: "pill bad" }, "오류") : null, l.hasImage ? el("span", { class: "pill none" }, ico("image"), "사진") : null,
          el("small", { class: "cl-tok" }, `${nf((l.usage || {}).total)} 토큰`)),
        el("div", { class: "cl-body" },
          el("div", { class: "cl-meta" }, `${l.kind === "worksheet" ? "학습지" : "교재"} · ${l.where || "—"} · 입력 ${nf((l.usage || {}).prompt)} / 출력 ${nf((l.usage || {}).output)} / 생각 ${nf((l.usage || {}).thoughts)} · ${l.ms || 0}ms${l.hasImage ? ` · 사진 ${Math.round((l.imageBytes || 0) / 1024)}KB(파일은 저장하지 않음)` : ""}`),
          el("div", { class: "cl-row" }, el("b", {}, "학생 "), l.question),
          l.error ? el("div", { class: "cl-row err" }, el("b", {}, "오류 "), l.error) : el("div", { class: "cl-row" }, el("b", {}, "AI "), l.reply)))) : el("p", { class: "lead" }, logs.length ? "조건에 맞는 기록이 없습니다." : "아직 기록이 없습니다."),
      shown.length > 60 ? el("p", { class: "lead" }, `최근 60건만 표시합니다(필터로 좁혀 보세요).`) : null);
  };
  const paintChat = () => { paintTok(); paintLog(); paintAi(); paintNav(); };

  /* --- 진도 표: 교재 장별 읽기 진도(분류별로 묶음) + 학습지 진행 --- */
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
    const cnt = { ok: 0, part: 0, none: 0 }; rows.forEach(r => { cnt[liveState(tsMs(r.lastActiveAt))[0]]++; });
    const grpSel = el("select", { onchange: e => { M.group = e.target.value; paintTbl(); } }, [["all", "전체"], ...Object.entries(GROUP_NAME)].map(([v, l]) => el("option", { value: v, ...(v === M.group ? { selected: "" } : {}) }, l)));
    const sortSel = el("select", { onchange: e => { M.sort = e.target.value; paintTbl(); } }, [["num", "번호순"], ["slow", "교재 진도 느린 순"], ["idle", "활동 오래된 순"]].map(([v, l]) => el("option", { value: v, ...(v === M.sort ? { selected: "" } : {}) }, l)));
    // 분류 머리줄: 같은 분류의 장을 한 칸으로 묶는다
    const groupHead = []; chs.forEach(c => { const last = groupHead[groupHead.length - 1]; if (last && last.g === c.group) last.n++; else groupHead.push({ g: c.group, n: 1 }); });
    fill(tbl, el("h3", {}, "진도표"),
      M.mon !== undefined && !(M.mon && M.mon.on) ? el("div", { class: "note-box" }, ico("info"), "진도 수집이 꺼져 있어 새 진도는 들어오지 않습니다. ", el("button", { type: "button", class: "btn small", onclick: () => go("settings") }, "환경설정으로 가기")) : null,
      M.progErr ? el("div", { class: "err-box" }, el("b", {}, ico("error", "fill"), "진도를 읽지 못했습니다."), el("div", {}, M.progErr),
        /permission|insufficient/i.test(M.progErr) ? el("div", {}, "Firestore 규칙이 이 계정을 교사로 인정하지 않는 경우입니다. 콘솔에서 config/teachers 문서의 emails 가 ‘배열(array)’ 유형인지, 지금 로그인한 이메일이 소문자·공백 없이 들어 있는지 확인하세요.") : null) : null,
      M.prog === null ? el("p", { class: "lead" }, "불러오는 중…") : el("p", { class: "lead" }, `접속 기록 ${rows.length}명 · 활동 중 ${cnt.ok} · 잠시 멈춤 ${cnt.part} · 멈춤 ${cnt.none}`),
      el("p", { class: "lead", style: "font-size:13.5px" }, "칸의 숫자는 그 장에서 읽은 절의 비율이고 아래 작은 글씨는 그 장의 체류 시간입니다. 숫자를 누르면 절별 세부 정보를 볼 수 있습니다. 절이 화면 가운데에 2초 이상 머물면 읽은 것으로 세고, 체류 시간은 화면이 보이고 최근 60초 안에 조작이 있던 시간만 셉니다(줄어들지 않는 값). 교재의 호스팅 사본을 열어 읽을 때만 집계됩니다."),
      el("div", { style: "display:flex;gap:12px;flex-wrap:wrap;margin:6px 0" }, el("label", {}, "분류 ", grpSel), el("label", {}, "정렬 ", sortSel)),
      !rows.length ? el("p", { class: "lead" }, "아직 진도를 보낸 학생이 없습니다. 수집을 켜고, 학생이 학교 Google 계정으로 로그인하면 나타납니다.")
        : el("div", { style: "overflow-x:auto" }, el("table", { class: "ro prog" },
          el("thead", {},
            el("tr", {}, ["학생", "상태", "화면", "마지막 활동", "지금 있는 곳", "학습지", "활동 시간"].map(h => el("th", { rowspan: 2 }, h)), groupHead.map(h => el("th", { colspan: h.n, style: "text-align:center" }, GROUP_NAME[h.g]))),
            el("tr", {}, chs.map(c => el("th", { style: "font-weight:600;white-space:nowrap" }, c.title)))),
          el("tbody", {}, rows.map(r => {
            const ms = tsMs(r.lastActiveAt), [cls, lab] = liveState(ms), wp = wsTotal ? Math.round(100 * wsDone(r) / wsTotal) : 0;
            return el("tr", {}, el("td", { style: "white-space:nowrap" }, key(r)),
              el("td", {}, el("span", { class: "pill " + cls }, ico(cls === "ok" ? "check_circle" : cls === "part" ? "pause_circle" : "do_not_disturb_on", "fill"), lab)),
              el("td", { style: "white-space:nowrap" }, viewCell(r)),
              el("td", { style: "white-space:nowrap" }, ago(ms)), el("td", { style: "white-space:nowrap" }, r.where || "—"), el("td", {}, `${wp}%`), el("td", {}, `${Math.round((r.activeMs || 0) / 60000)}분`),
              chs.map(c => {
                const f = cell(r, c), pct = Math.round(100 * f), x = (r.chapters || {})[c.slug];
                return el("td", { style: `text-align:center;background:linear-gradient(90deg,var(--ok-soft) ${pct}%,transparent ${pct}%)` },
                  x ? el("button", { type: "button", class: "pct", title: `${c.title} 세부 정보 보기`, onclick: () => openDetail(r, c) }, f ? pct + "%" : "0%", x.sec ? el("small", {}, fmtDur(x.sec)) : null) : "—");
              }));
          })))));
  };

  paintCtl(); paintAi(); paintTok(); paintLog(); paintTbl(); paintNav();
  liveSub(FB.watchMonitor(s => { M.mon = s; paintCtl(); paintNav(); }), tok);
  liveSub(FB.watchMonitorEvents((rows, err) => { M.events = rows || []; paintCtl(); }), tok);
  liveSub(FB.watchAssistant(s => { M.ai = s; paintAi(); paintNav(); }), tok);
  liveSub(FB.watchStats((s, err) => { M.stats = s; if (err) M.logErr = errText(err); paintChat(); }), tok);
  liveSub(FB.watchChatUsage((rows, err) => { M.usage = rows || []; if (err) M.logErr = errText(err); paintChat(); }), tok);
  liveSub(FB.watchChatLogs((rows, err) => { M.logs = rows || []; M.logErr = err ? errText(err) : ""; paintChat(); }, 200), tok);
  liveSub(FB.watchProgress((rows, err) => { M.prog = rows || []; M.progErr = err ? errText(err) : ""; paintTbl(); paintNav(); paintCtl(); }), tok);
  const timer = setInterval(paintTbl, 20000); T.live.push(() => clearInterval(timer));
}

/* 시작: 파일 맨 끝에서 부른다(위의 const·함수가 모두 만들어진 뒤여야 한다). */
if (GATED) gate(); else boot();
