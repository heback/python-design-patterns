"use strict";
/* 교사용 앱(디자인 패턴 학습 관리): 학교 Google 계정으로 로그인한 교사가 학생 진도를 실시간으로 본다.
   학생 응답 본문은 서버로 오지 않으므로 응답 검토·코멘트·제출 관리 화면은 없다. */
const M = { prog: null, mon: undefined, group: "all", sort: "num" };   // 진도 화면의 상태(boot 보다 먼저 있어야 한다)
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
/* 마지막 활동으로부터: <2분 활동 중, <5분 잠시 멈춤, 그 이상 멈춤(자리 비움). 수업 중에만 의미가 있다. */
function liveState(ms) {
  const m = ms ? (Date.now() - ms) / 60000 : Infinity;
  return m < 2 ? ["ok", "활동 중"] : m < 5 ? ["part", "잠시 멈춤"] : ["none", "멈춤"];
}

function renderMonitor(main) {
  const tok = T.liveTok = {};
  const ctl = el("div", { class: "panel" }), tbl = el("div", { class: "panel" });
  main.append(ctl, tbl);

  /* --- 수집 스위치 --- */
  const paintCtl = () => {
    const on = !!(M.mon && M.mon.on);
    fill(ctl, el("h3", {}, "진도 수집"),
      el("p", { class: "lead" }, "켜 두면 학생의 학습지와 교재 화면에 ‘진행 상황이 선생님께 자동으로 전달된다’는 고지가 뜨고, 교재 각 장에서 읽은 절·학습지에서 마친 문항·지금 있는 곳·마지막 활동 시각·활동 시간이 계정의 이름·이메일과 함께 아래 표에 실시간으로 나타납니다. 쓴 글의 내용은 전달되지 않습니다(학생 브라우저에만 저장됩니다). 수업이 끝나면 꺼 두세요."),
      M.mon === undefined ? el("p", { class: "lead" }, "상태를 확인하는 중…") : el("p", { class: on ? "status-open" : "status-closed" }, ico("circle", "fill"), on ? "수집 중 — 학생에게 고지가 표시됩니다" : "꺼짐 — 학생은 진도를 보내지 않습니다"),
      el("div", { style: "display:flex;gap:8px;flex-wrap:wrap" },
        el("button", { class: "btn primary", onclick: async e => { e.target.disabled = true; try { await FB.saveMonitor(!on); } catch (err) { alert("저장하지 못했습니다: " + errText(err)); } } }, on ? [ico("stop"), "수집 중지"] : [ico("play_arrow"), "수집 시작"]),
        el("button", { class: "btn danger", onclick: async () => {
          if (!confirm("서버에 쌓인 모든 학생의 진도 기록을 삭제합니다. 계속할까요?")) return;
          try { toast(`진도 기록 ${await FB.clearProgress()}건을 삭제했습니다`); } catch (err) { alert("삭제하지 못했습니다: " + errText(err)); }
        } }, [ico("delete"), "진도 기록 삭제"])));
  };

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
    fill(tbl, el("h3", {}, "학생 진도 (실시간)"),
      M.prog === null ? el("p", { class: "lead" }, "불러오는 중…") : el("p", { class: "lead" }, `접속 기록 ${rows.length}명 · 활동 중 ${cnt.ok} · 잠시 멈춤 ${cnt.part} · 멈춤 ${cnt.none}`),
      el("p", { class: "lead", style: "font-size:13.5px" }, "칸의 숫자는 그 장에서 읽은 절의 비율입니다(절이 화면 가운데에 2초 이상 머물면 읽은 것으로 셉니다). 교재의 호스팅 사본을 열어 읽을 때만 집계됩니다."),
      el("div", { style: "display:flex;gap:12px;flex-wrap:wrap;margin:6px 0" }, el("label", {}, "분류 ", grpSel), el("label", {}, "정렬 ", sortSel)),
      !rows.length ? el("p", { class: "lead" }, "아직 진도를 보낸 학생이 없습니다. 수집을 켜고, 학생이 학교 Google 계정으로 로그인하면 나타납니다.")
        : el("div", { style: "overflow-x:auto" }, el("table", { class: "ro prog" },
          el("thead", {},
            el("tr", {}, ["학생", "상태", "마지막 활동", "지금 있는 곳", "학습지", "활동 시간"].map(h => el("th", { rowspan: 2 }, h)), groupHead.map(h => el("th", { colspan: h.n, style: "text-align:center" }, GROUP_NAME[h.g]))),
            el("tr", {}, chs.map(c => el("th", { style: "font-weight:600;white-space:nowrap" }, c.title)))),
          el("tbody", {}, rows.map(r => {
            const ms = tsMs(r.lastActiveAt), [cls, lab] = liveState(ms), wp = wsTotal ? Math.round(100 * wsDone(r) / wsTotal) : 0;
            return el("tr", {}, el("td", { style: "white-space:nowrap" }, key(r)),
              el("td", {}, el("span", { class: "pill " + cls }, ico(cls === "ok" ? "check_circle" : cls === "part" ? "pause_circle" : "do_not_disturb_on", "fill"), lab)),
              el("td", { style: "white-space:nowrap" }, ago(ms)), el("td", { style: "white-space:nowrap" }, r.where || "—"), el("td", {}, `${wp}%`), el("td", {}, `${Math.round((r.activeMs || 0) / 60000)}분`),
              chs.map(c => { const f = cell(r, c), pct = Math.round(100 * f); return el("td", { style: `text-align:center;background:linear-gradient(90deg,var(--ok-soft) ${pct}%,transparent ${pct}%)`, title: `${c.title} ${pct}%` }, f ? pct + "%" : "—"); }));
          })))));
  };

  paintCtl(); paintTbl();
  liveSub(FB.watchMonitor(s => { M.mon = s; paintCtl(); }), tok);
  liveSub(FB.watchProgress((rows, err) => { M.prog = rows || []; if (err) toast("진도를 읽지 못했습니다: " + errText(err)); paintTbl(); }), tok);
  const timer = setInterval(paintTbl, 20000); T.live.push(() => clearInterval(timer));
}

/* 시작: 파일 맨 끝에서 부른다(위의 const·함수가 모두 만들어진 뒤여야 한다). */
if (GATED) gate(); else boot();
