"use strict";
/* 교사용 앱(디자인 패턴 학습 관리): 학교 Google 계정으로 로그인한 교사가 학생 진도를 실시간으로 보고 돌발 퀴즈를 낸다.
   학생 응답 본문은 서버로 오지 않으므로 응답 검토·코멘트·제출 관리 화면은 없다. */
const M = { prog: null, mon: undefined, qcfg: null, answers: null, qview: null, week: 1, sort: "num" };   // 진도·퀴즈 탭의 상태(boot 보다 먼저 있어야 한다)
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
      CONTENT = { weeks: r.weeks };
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

function weekTabs(cur, onPick, extra) {
  return el("div", { class: "tabs", style: "padding:0 0 12px" }, ...(extra || []), CONTENT.weeks.map((w, i) =>
    el("button", { class: "tab", "aria-selected": String(cur === i), onclick: () => onPick(i) }, el("b", {}, `${w.n}주차 · ${w.concept}`), el("small", {}, w.title))));
}
const errText = e => FB.fbErr(e).replace(/^.*?: /, "");

/* ===================== 진도 수집 · 돌발 퀴즈 (실시간) ===================== */
/* 학생이 보내는 것은 완료 문항 수·ID, 마지막 문항, 활동 시간, 마지막 활동 시각뿐이다(응답 본문 없음). 수집 스위치는 config/monitor. */
function stopLive() { (T.live || []).forEach(f => { try { f(); } catch (e) {} }); T.live = []; T.liveTok = null; M.unAns = null; }
function liveSub(p, tok, onUn) {
  p.then(u => { if (T.liveTok === tok) { T.live.push(u); if (onUn) onUn(u); } else u(); }).catch(() => {});
}
/* 네이티브 replaceChildren 은 배열·null 을 문자열로 바꿔 버리므로, 한 겹 펴고 빈 값을 뺀 뒤 넣는다. */
const fill = (box, ...kids) => box.replaceChildren(...kids.flat().filter(k => k != null && k !== false));
const stripTags = h => String(h || "").replace(/<[^>]+>/g, "");
function itemLabel(id) {
  for (const w of CONTENT.weeks) for (const st of w.stages) {
    let no = 0;
    for (const it of st.items) { if (ANSWERABLE(it)) no++; if (it.id === id) return `${w.n}주차 ${st.title} Q${no}`; }
  }
  return id || "—";
}
const tsMs = x => (x && x.toMillis ? x.toMillis() : null);
function ago(ms) {
  if (!ms) return "—";
  const m = Math.floor((Date.now() - ms) / 60000);
  return m < 1 ? "방금" : m < 60 ? `${m}분 전` : `${Math.floor(m / 60)}시간 ${m % 60}분 전`;
}
/* 마지막 활동으로부터: <2분 활동 중, <5분 잠시 멈춤, 그 이상 멈춤(자리 비움). 수업 중에만 의미가 있다. */
function liveState(ms) {
  const m = ms ? (Date.now() - ms) / 60000 : Infinity;
  return m < 2 ? ["ok", "활동 중"] : m < 5 ? ["part", "잠시 멈춤"] : ["none", "멈춤"];
}

function renderMonitor(main) {
  const tok = T.liveTok = {};
  const ctl = el("div", { class: "panel" }), tbl = el("div", { class: "panel" }), qz = el("div", { class: "panel" });
  main.append(ctl, tbl, qz);

  /* --- 수집 스위치 --- */
  const paintCtl = () => {
    const on = !!(M.mon && M.mon.on);
    fill(ctl, el("h3", {}, "진도 수집"),
      el("p", { class: "lead" }, "켜 두면 학생 화면에 ‘진행 상황이 선생님께 자동으로 전달된다’는 고지가 뜨고, 어느 문항을 마쳤는지·마지막으로 푼 문항·마지막 활동 시각·활동 시간이 학번·성명과 함께 아래 표에 실시간으로 나타납니다. 쓴 글의 내용은 전달되지 않습니다(학생 브라우저에만 저장됩니다). 퀴즈에서 고른 답은 서버에 기록됩니다. 수업이 끝나면 꺼 두세요."),
      M.mon === undefined ? el("p", { class: "lead" }, "상태를 확인하는 중…") : el("p", { class: on ? "status-open" : "status-closed" }, ico("circle", "fill"), on ? "수집 중 — 학생에게 고지가 표시됩니다" : "꺼짐 — 학생은 진도를 보내지 않습니다"),
      el("div", { style: "display:flex;gap:8px;flex-wrap:wrap" },
        el("button", { class: "btn primary", onclick: async e => { e.target.disabled = true; try { await FB.saveMonitor(!on); } catch (err) { alert("저장하지 못했습니다: " + errText(err)); } } }, on ? [ico("stop"), "수집 중지"] : [ico("play_arrow"), "수집 시작"]),
        el("button", { class: "btn danger", onclick: async () => {
          if (!confirm("서버에 쌓인 모든 학생의 진도 기록을 삭제합니다(퀴즈 응답은 그대로). 계속할까요?")) return;
          try { toast(`진도 기록 ${await FB.clearProgress()}건을 삭제했습니다`); } catch (err) { alert("삭제하지 못했습니다: " + errText(err)); }
        } }, [ico("delete"), "진도 기록 삭제"])));
  };

  /* --- 진도 표 --- */
  const paintTbl = () => {
    const rows = (M.prog || []).slice();
    const wkObj = r => (r.weeks || {})[M.week] || { n: 0, total: 0, ids: [] };
    const total = (CONTENT.weeks.find(w => w.n === M.week) || {}).stages ? weekProgress(CONTENT.weeks.find(w => w.n === M.week), {}).total : 0;
    const key = r => [r.student.klass, r.student.number, r.student.name].join(" ");
    rows.sort(M.sort === "slow" ? (a, b) => wkObj(a).n - wkObj(b).n
      : M.sort === "idle" ? (a, b) => (tsMs(a.lastActiveAt) || 0) - (tsMs(b.lastActiveAt) || 0)
      : (a, b) => key(a).localeCompare(key(b), "ko", { numeric: true }));
    const cnt = { ok: 0, part: 0, none: 0 }; rows.forEach(r => { cnt[liveState(tsMs(r.lastActiveAt))[0]]++; });
    const weekSel = el("select", { onchange: e => { M.week = Number(e.target.value); paintTbl(); } }, CONTENT.weeks.map(w => el("option", { value: w.n, ...(w.n === M.week ? { selected: "" } : {}) }, `${w.n}주차 · ${w.concept}`)));
    const sortSel = el("select", { onchange: e => { M.sort = e.target.value; paintTbl(); } }, [["num", "번호순"], ["slow", "진도 느린 순"], ["idle", "활동 오래된 순"]].map(([v, l]) => el("option", { value: v, ...(v === M.sort ? { selected: "" } : {}) }, l)));
    fill(tbl, el("h3", {}, "학생 진도 (실시간)"),
      M.prog === null ? el("p", { class: "lead" }, "불러오는 중…") : el("p", { class: "lead" }, `접속 기록 ${rows.length}명 · 활동 중 ${cnt.ok} · 잠시 멈춤 ${cnt.part} · 멈춤 ${cnt.none}`),
      el("div", { style: "display:flex;gap:12px;flex-wrap:wrap;margin:6px 0" }, el("label", {}, "주차 ", weekSel), el("label", {}, "정렬 ", sortSel)),
      !rows.length ? el("p", { class: "lead" }, "아직 진도를 보낸 학생이 없습니다. 수집을 켜고, 학생이 학번·성명을 입력하면 나타납니다.")
        : el("div", { style: "overflow-x:auto" }, el("table", { class: "ro" },
          el("thead", {}, el("tr", {}, ["학생", `${M.week}주차 진도`, "마지막으로 푼 문항", "마지막 활동", "활동 시간", "상태"].map(h => el("th", {}, h)))),
          el("tbody", {}, rows.map(r => {
            const w = wkObj(r), pct = total ? Math.round(100 * w.n / total) : 0, ms = tsMs(r.lastActiveAt), [cls, lab] = liveState(ms);
            return el("tr", {}, el("td", {}, key(r)),
              el("td", {}, el("div", { class: "bar", style: "min-width:90px" }, el("i", { style: `width:${pct}%` })), el("small", {}, `${w.n}/${total || w.total || "?"} (${pct}%)`)),
              el("td", {}, w.last ? itemLabel(w.last) : "—"), el("td", {}, ago(ms)), el("td", {}, `${Math.round((r.activeMs || 0) / 60000)}분`),
              el("td", {}, el("span", { class: "pill " + cls }, ico(cls === "ok" ? "check_circle" : cls === "part" ? "pause_circle" : "do_not_disturb_on", "fill"), lab)));
          })))));
  };

  /* --- 퀴즈 --- */
  const quizCard = (q, cfg) => {
    const isLive = cfg.liveId === q.id;
    return el("div", { class: "item", style: "margin:8px 0" },
      el("p", { class: "q" }, el("span", { class: "opt-tag" }, q.concept), isLive ? el("span", { class: "pill ok", style: "margin-right:6px" }, ico("circle", "fill"), "출제 중") : null, el("span", { html: q.q })),
      q.options.map((o, i) => el("div", { class: "ro-opt" + (i === q.answer.sel ? " key" : "") }, `${i + 1}. ${stripTags(o)}`)),
      el("p", { class: "lead", style: "margin:6px 0", html: "풀이: " + q.explain }),
      el("div", { style: "display:flex;gap:8px;flex-wrap:wrap" },
        isLive
          ? el("button", { class: "btn", onclick: () => saveQ({ liveId: "", liveAt: cfg.liveAt }, "퀴즈를 닫았습니다") }, [ico("stop"), "닫기"])
          : el("button", { class: "btn primary", onclick: () => { M.qview = q.id; saveQ({ liveId: q.id, liveAt: undefined }, "학생 화면에 퀴즈를 냈습니다"); } }, [ico("campaign"), "지금 출제"]),
        el("button", { class: "btn", onclick: () => { M.qview = q.id; subAnswers(); paintQz(); } }, [ico("bar_chart"), "결과 보기"])));
  };
  const saveQ = async (patch, msg) => {
    const cfg = M.qcfg || { liveId: "", auto: {} };
    try { await FB.saveQuizCfg(Object.assign({ liveId: cfg.liveId, liveAt: cfg.liveAt, auto: cfg.auto || {} }, patch)); toast(msg); }
    catch (err) { alert("저장하지 못했습니다: " + errText(err)); }
  };
  const resultBox = cfg => {
    const q = CONTENT.weeks.flatMap(w => w.quiz || []).find(x => x.id === M.qview);
    if (!q) return null;
    const a = M.answers || [], n = a.length, first = a.filter(x => x.firstCorrect).length, fin = a.filter(x => x.correct).length;
    const dist = q.options.map((_, i) => a.filter(x => (x.choices || [])[0] === i).length);
    const online = (M.prog || []).filter(r => liveState(tsMs(r.lastActiveAt))[0] === "ok").length;
    return el("div", { class: "sample", style: "margin-top:10px" }, el("b", {}, `결과 · ${q.id} (${q.concept})`),
      el("p", {}, `응답 ${n}명` + (online ? ` / 활동 중 ${online}명` : "") + ` · 첫 시도 정답 ${first}명${n ? ` (${Math.round(100 * first / n)}%)` : ""} · 최종 정답 ${fin}명`),
      q.options.map((o, i) => el("div", { class: "ro-opt" + (i === q.answer.sel ? " key" : "") },
        `${i + 1}. ${stripTags(o)}`, el("span", { style: "float:right" }, `첫 선택 ${dist[i]}명`),
        el("div", { class: "bar" }, el("i", { style: `width:${n ? Math.round(100 * dist[i] / n) : 0}%` })))),
      el("button", { class: "btn small", onclick: async () => {
        if (!confirm(`${q.id}의 학생 응답 ${n}건을 지웁니다. 다시 출제해도 이전에 푼 학생이 다시 풀 수 있게 됩니다. 계속할까요?`)) return;
        try { toast(`응답 ${await FB.resetQuizAnswers(q.id)}건을 지웠습니다`); } catch (err) { alert("지우지 못했습니다: " + errText(err)); }
      } }, "응답 지우기"));
  };
  const paintQz = () => {
    const cfg = M.qcfg || { liveId: "", auto: {} }, w = CONTENT.weeks.find(x => x.n === M.qweek) || CONTENT.weeks[0];
    M.qweek = w.n;
    const auto = el("div", { class: "wk-toggles" }, CONTENT.weeks.map(x => {
      const c = el("input", { type: "checkbox", ...((cfg.auto || {})[x.n] ? { checked: "" } : {}) });
      c.onchange = () => saveQ({ auto: Object.assign({}, cfg.auto || {}, { [x.n]: c.checked }) }, `${x.n}주차 자동 퀴즈를 ${c.checked ? "켰" : "껐"}습니다`);
      return el("label", {}, c, `${x.n}주차`);
    }));
    fill(qz, el("h3", {}, "돌발 퀴즈"),
      el("p", { class: "lead" }, "한 문항이 학생 화면에 팝업으로 뜨고, 채점은 서버가 합니다(정답은 학생 화면에 들어 있지 않습니다). 점수에 들어가지 않는 형성평가이며, 틀리면 한 번 더 시도할 수 있습니다. 수집이 켜져 있고 학번·성명을 입력한 학생에게만 나갑니다."),
      el("p", {}, el("b", {}, "자동 퀴즈 "), "— 켠 주차에서 학생이 탐구 단계 하나를 마칠 때 아직 안 푼 퀴즈 1개를 냅니다(10분에 한 번까지, 학생은 한 번 미룰 수 있음)."), auto,
      weekTabs(CONTENT.weeks.indexOf(w), i => { M.qweek = CONTENT.weeks[i].n; paintQz(); }),
      (w.quiz || []).length ? (w.quiz || []).map(q => quizCard(q, cfg)) : el("p", { class: "lead" }, "이 주차에는 퀴즈가 없습니다."),
      resultBox(cfg));
  };
  const subAnswers = () => {
    if (M.unAns) { M.unAns(); M.unAns = null; } M.answers = null;
    if (!M.qview) return;
    liveSub(FB.watchQuizAnswers(M.qview, (rows, err) => { M.answers = rows || []; paintQz(); }), tok, u => { M.unAns = u; });
  };

  paintCtl(); paintTbl(); paintQz();
  liveSub(FB.watchMonitor(s => { M.mon = s; paintCtl(); }), tok);
  liveSub(FB.watchProgress((rows, err) => { M.prog = rows || []; if (err) toast("진도를 읽지 못했습니다: " + errText(err)); paintTbl(); }), tok);
  liveSub(FB.watchQuiz(c => { M.qcfg = c; if (c && c.liveId && !M.qview) { M.qview = c.liveId; subAnswers(); } paintQz(); }), tok);
  if (M.qview) subAnswers();
  const timer = setInterval(paintTbl, 20000); T.live.push(() => clearInterval(timer));
}

/* 시작: 파일 맨 끝에서 부른다(위의 const·함수가 모두 만들어진 뒤여야 한다). */
if (GATED) gate(); else boot();
