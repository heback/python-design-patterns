"use strict";
/* 교사 화면 [돌발퀴즈]: 패턴별 서술형 문항을 골라 제시하고(학생 교재 화면에 팝업), 제출된 답안을 보고, AI 로 채점해 피드백을 학생에게 보낸다.
   문항 은행(질문·채점 기준·모범 답안)은 로그인 뒤 getTeacherContent 가 내려주는 CONTENT.quiz[패턴 slug] 에 있다(학생 빌드에는 없다).
   teacher.js 보다 먼저 실려 있어야 한다(teacher.js 맨 끝에서 화면을 시작하므로). 필요한 전역: el, ico, fill, ago, tsMs, stamp, toast, errText, nf, liveState, GROUP_NAME, T, FB, CONTENT. */
const TeacherQuiz = (() => {
  const Q = { tab: "present", sel: "", picked: null, min: 0, cfg: undefined, sessions: null, sid: "", answers: null, grades: null, err: "", draft: {}, open: new Set(), ai: null, unA: null, unG: null };
  let root = null, tok = null, ctx = null, timeEl = null, dirty = false;
  const bank = slug => ((typeof CONTENT !== "undefined" && CONTENT.quiz) || {})[slug] || [];
  const MIN_CHOICES = [1, 2, 3, 5, 7, 10, 15, 20, 25, 30];
  const nearest = m => MIN_CHOICES.reduce((a, b) => Math.abs(b - m) < Math.abs(a - m) ? b : a, 5);
  const isActive = () => !!(Q.cfg && Q.cfg.state === "open" && Q.cfg.endsAt > Date.now());
  const session = () => (Q.sessions || []).find(s => s.id === Q.sid);
  const mmss = ms => { const s = Math.max(0, Math.ceil(ms / 1000)); return Math.floor(s / 60) + ":" + String(s % 60).padStart(2, "0"); };
  /* 지금 이 패턴 장을 보고 있는 학생 수(진도 문서의 '지금 있는 곳' + 최근 활동). 팝업이 실제로 뜨는 학생 수의 어림값이다. */
  const viewers = title => (ctx.prog() || []).filter(r => typeof r.where === "string" && r.where.startsWith("교재 " + title) && liveState(tsMs(r.lastActiveAt))[0] !== "none").length;
  const aiOk = uid => { const c = (ctx.consents() || []).find(x => x.id === uid); return !!(c && c.ai === true); };
  const grade = uid => (Q.grades || []).find(g => g.id === uid);
  const answerOf = uid => (Q.answers || []).find(a => a.id === uid);

  /* 편집 중인 글을 잃지 않도록, 글칸에 커서가 있는 동안에는 다시 그리지 않고 나중에 그린다. 그릴 때 스크롤 위치는 지킨다. */
  function paint() {
    if (!root) return;
    const ae = document.activeElement;
    if (ae && root.contains(ae) && ae.tagName === "TEXTAREA") { dirty = true; return; }
    dirty = false; const y = window.scrollY, x = window.scrollX, shown = !root.hidden;
    render();
    if (shown && window.scrollY !== y) window.scrollTo({ left: x, top: y, behavior: "instant" });
  }
  document.addEventListener("focusout", () => { if (dirty) setTimeout(() => { if (dirty && !(document.activeElement && root && root.contains(document.activeElement) && document.activeElement.tagName === "TEXTAREA")) paint(); }, 0); });

  /* ---------- 제시 ---------- */
  async function present() {
    const bk = bank(Q.sel), ch = (CONTENT.chapters || []).find(c => c.slug === Q.sel), picked = bk.filter(q => Q.picked.has(q.id)).map(q => q.id);
    if (!picked.length) { alert("문항을 하나 이상 고르세요."); return; }
    const v = viewers(ch.title);
    if (!confirm(`‘${ch.title}’ 장을 보고 있는 학생(지금 ${v}명)에게 ${picked.length}문항을 ${Q.min}분 제한으로 제시할까요?\n다른 장을 보던 학생도 그 장으로 들어가면 남은 시간만큼 팝업이 뜹니다.`)) return;
    try { const r = await FB.startQuiz({ slug: Q.sel, qids: picked, seconds: Q.min * 60 }); toast("퀴즈를 제시했어요."); select(r.sid); }
    catch (e) { alert("제시하지 못했습니다: " + errText(e)); }
  }
  async function closeNow() {
    if (!Q.cfg || !confirm("지금 퀴즈를 마감할까요? 학생 화면의 시간이 끝난 것으로 처리되고, 쓴 글은 자동 제출됩니다.")) return;
    try { await FB.closeQuiz(Q.cfg.sid); toast("마감했어요."); } catch (e) { alert("마감하지 못했습니다: " + errText(e)); }
  }

  /* ---------- 기록 선택·구독 ---------- */
  function select(sid) {
    if (sid) Q.tab = "results";
    if (Q.sid === sid) { paint(); return; }
    [Q.unA, Q.unG].forEach(f => { try { f && f(); } catch (e) {} }); Q.unA = Q.unG = null;
    Q.sid = sid; Q.answers = null; Q.grades = null; Q.draft = {}; Q.open = new Set(); Q.ai = null; Q.err = "";
    paint(); if (!sid) return;
    FB.watchQuizAnswers(sid, (rows, err) => { if (Q.sid !== sid) return; Q.answers = rows || []; if (err) Q.err = errText(err); paint(); }).then(f => { if (Q.sid === sid && T.liveTok === tok) Q.unA = f; else f(); }).catch(() => {});
    FB.watchQuizGrades(sid, (rows, err) => { if (Q.sid !== sid) return; Q.grades = rows || []; if (err) Q.err = errText(err); paint(); }).then(f => { if (Q.sid === sid && T.liveTok === tok) Q.unG = f; else f(); }).catch(() => {});
  }

  /* ---------- 채점 ---------- */
  /* 학생들을 최대 3명씩 동시에 AI 로 채점한다. AI 선택 동의가 없는 학생은 건너뛰고 직접 채점하도록 안내한다. */
  async function gradeMany(uids) {
    const todo = uids.filter(aiOk), skipped = uids.length - todo.length;
    Q.ai = { done: 0, total: todo.length, fails: [], skipped, running: true }; paint();
    let i = 0;
    const worker = async () => { for (;;) { const k = i++; if (k >= todo.length) return; const uid = todo[k];
      try { await FB.gradeQuizAnswer(Q.sid, uid); delete Q.draft[uid]; } catch (e) { Q.ai.fails.push({ uid, msg: errText(e) }); }
      Q.ai.done++; paint(); } };
    await Promise.all([worker(), worker(), worker()]);
    Q.ai.running = false; paint();
  }
  /* 학생별 편집 상태: 저장된 채점(있으면)에서 시작한다. scores 는 0~3 또는 null(아직 안 고름). */
  function draftOf(uid, s) {
    if (Q.draft[uid]) return Q.draft[uid];
    const g = grade(uid), d = { scores: {}, feedback: {}, summary: (g && g.summary) || "" };
    s.questions.forEach(q => { const it = g && (g.items || []).find(x => x.id === q.id); d.scores[q.id] = it ? it.score : null; d.feedback[q.id] = it ? it.feedback : ""; });
    return (Q.draft[uid] = d);
  }
  async function save(uid, s) {
    const d = draftOf(uid, s);
    if (s.questions.some(q => d.scores[q.id] == null)) { alert("모든 문항의 점수(0~3)를 고르세요."); return false; }
    try { await FB.saveQuizGrade(Q.sid, uid, Object.fromEntries(s.questions.map(q => [q.id, { score: d.scores[q.id], feedback: d.feedback[q.id] }])), d.summary); delete Q.draft[uid]; toast("저장했어요."); return true; }
    catch (e) { alert("저장하지 못했습니다: " + errText(e)); return false; }
  }
  async function release(uids) {
    try { const r = await FB.releaseQuiz(Q.sid, uids); toast(`${r.released}명에게 피드백을 보냈어요.`); } catch (e) { alert("보내지 못했습니다: " + errText(e)); }
  }
  const status = (g) => {
    if (!g) return ["off", "미채점"];
    const t = Math.max(tsMs(g.gradedAt) || 0, tsMs(g.editedAt) || 0), r = tsMs(g.releasedAt) || 0;
    return r && r >= t ? ["ok", "학생에게 전송됨"] : g.source === "ai" ? ["part", "AI 초안"] : ["part", "채점함(미전송)"];
  };

  /* ---------- 화면 ---------- */
  function renderPresent() {
    const chs = (CONTENT.chapters || []).filter(c => bank(c.slug).length), active = isActive();
    const groups = ["create", "struct", "behave"].map(g => [g, chs.filter(c => c.group === g)]).filter(x => x[1].length);
    const bk = bank(Q.sel), ch = chs.find(c => c.slug === Q.sel);
    return [
      el("div", { class: "qzt-groups" }, groups.map(([g, list]) => el("div", { class: "qzt-grp" }, el("b", {}, GROUP_NAME[g]),
        el("div", { class: "qzt-pats" }, list.map(c => el("button", { type: "button", class: "btn small" + (Q.sel === c.slug ? " primary" : ""), onclick: () => { if (Q.sel === c.slug) { Q.sel = ""; paint(); return; } Q.sel = c.slug; Q.picked = new Set(bank(c.slug).map(q => q.id)); Q.min = nearest(bank(c.slug).reduce((a, q) => a + (q.minutes || 2), 0)); paint(); } }, c.title)))))),
      ch ? el("div", { class: "qzt-bank" },
        el("div", { class: "qzt-bhead" }, el("h4", {}, `${ch.title} — 서술형 ${bk.length}문항`), el("span", { style: "flex:1" }),
          el("button", { type: "button", class: "btn small", title: "문항 목록을 닫습니다", onclick: () => { Q.sel = ""; paint(); } }, ico("close"), "닫기")),
        el("p", { class: "lead", style: "font-size:13px" }, "제시할 문항을 고르세요. 채점 기준과 모범 답안은 학생에게 보이지 않습니다(AI 채점과 교사 확인용)."),
        bk.map((q, i) => el("div", { class: "qzt-q" },
          el("label", { class: "qzt-qhead" }, el("input", { type: "checkbox", ...(Q.picked.has(q.id) ? { checked: "" } : {}), onchange: e => { e.target.checked ? Q.picked.add(q.id) : Q.picked.delete(q.id); dirty = true; Q.min = nearest(bk.filter(x => Q.picked.has(x.id)).reduce((a, x) => a + (x.minutes || 2), 0)); paint(); } }),
            el("b", {}, `${i + 1}.`), el("span", { class: "nb" }, q.kind), el("small", { style: "color:var(--dim)" }, `권장 ${q.minutes}분`), el("span", { class: "qzt-qtext" }, q.q)),
          el("details", { class: "qzt-key" }, el("summary", {}, "채점 기준·모범 답안"), el("ol", {}, (q.key || []).map(k => el("li", {}, k))), el("p", {}, el("b", {}, "모범 답안 "), q.model)))),
        el("div", { class: "qzt-go" },
          el("label", {}, "제한 시간 ", el("select", { onchange: e => { Q.min = Number(e.target.value); dirty = true; } }, MIN_CHOICES.map(m => el("option", { value: m, ...(m === Q.min ? { selected: "" } : {}) }, `${m}분`)))),
          el("span", { class: "lead", style: "margin:0" }, `이 장을 지금 보는 학생 ${nf(viewers(ch.title))}명 · 고른 문항 ${Q.picked.size}개`),
          el("button", { type: "button", class: "btn primary", disabled: active || !Q.picked.size, title: active ? "진행 중인 퀴즈를 마감한 뒤 제시할 수 있어요." : "", onclick: present }, ico("campaign"), "제시하기"))) : el("p", { class: "lead" }, "패턴을 고르면 문항이 나옵니다.")];
  }
  function renderActive() {
    return isActive() ? el("div", { class: "qzt-active" }, el("b", {}, ico("timer", "fill"), `진행 중 · ${Q.cfg.title}`), el("span", { class: "qzt-clock" }, timeEl = el("b", {}, mmss(Q.cfg.endsAt - Date.now()))),
        el("span", {}, `제출 ${nf(Q.sid === Q.cfg.sid ? (Q.answers || []).length : 0)}명 · 이 장을 보는 학생 ${nf(viewers(Q.cfg.title))}명`),
        el("button", { type: "button", class: "btn small", onclick: () => select(Q.cfg.sid) }, "답안 보기"), el("button", { type: "button", class: "btn small", onclick: closeNow }, ico("stop"), "지금 마감")) : null;
  }
  function renderHistory() {
    const list = Q.sessions;
    return [el("h4", {}, "퀴즈 기록"),
      list === null ? el("p", { class: "lead" }, "불러오는 중…") : !list.length ? el("p", { class: "lead" }, "아직 제시한 퀴즈가 없어요.")
        : el("div", { class: "qzt-hist" }, list.map(s => el("button", { type: "button", class: "ask-item" + (Q.sid === s.id ? " on" : ""), onclick: () => select(s.id) },
          el("span", { class: "ask-item-top" }, el("b", {}, s.title), el("span", { class: "nb" + (s.state === "open" && tsMs(s.endsAt) > Date.now() ? " ok" : "") }, s.state === "open" && tsMs(s.endsAt) > Date.now() ? "진행 중" : "마감")),
          el("small", {}, `${stamp(new Date(tsMs(s.startedAt) || Date.now()))} · ${s.questions.length}문항 · ${Math.round(s.seconds / 60)}분`))))];
  }
  function renderStudent(a, s, key) {
    const g = grade(a.id), d = draftOf(a.id, s), [cls, lab] = status(g), open = Q.open.has(a.id), bk = bank(s.slug);
    const total = s.questions.every(q => d.scores[q.id] != null) ? s.questions.reduce((t, q) => t + d.scores[q.id], 0) : null;
    const head = el("button", { type: "button", class: "qzt-row", onclick: () => { open ? Q.open.delete(a.id) : Q.open.add(a.id); paint(); } },
      ico(open ? "expand_more" : "chevron_right"), el("b", {}, `${(a.student || {}).name || a.id}${(a.student || {}).email ? " · " + a.student.email.split("@")[0] : ""}`),
      el("span", { class: "pill " + cls }, lab), g ? el("span", { class: "nb" }, `${g.total}/${g.max}점`) : null, aiOk(a.id) ? null : el("span", { class: "nb off", title: "개인정보 동의에서 AI 도우미 이용(선택)에 동의하지 않아 AI 채점을 할 수 없어요. 직접 채점하세요." }, "AI 동의 없음"),
      a.late ? el("span", { class: "nb bad" }, "시간 지나 제출") : null, el("small", { style: "margin-left:auto;color:var(--dim)" }, ago(tsMs(a.submittedAt))));
    if (!open) return el("div", { class: "qzt-stu" }, head);
    return el("div", { class: "qzt-stu open" }, head, el("div", { class: "qzt-detail" },
      s.questions.map((q, i) => {
        const b = bk.find(x => x.id === q.id) || {}, it = g && (g.items || []).find(x => x.id === q.id), ans = ((a.answers || {})[q.id] || "").trim();
        return el("div", { class: "qzt-qa" }, el("div", { class: "qzt-qq" }, el("b", {}, `${i + 1}.`), " ", q.q),
          el("pre", { class: "qzt-ans" + (ans ? "" : " empty") }, ans || "(무응답)"),
          it && it.hits && (b.key || []).length ? el("ul", { class: "qzt-hits" }, (b.key || []).map((k, j) => el("li", { class: it.hits[j] ? "y" : "n" }, ico(it.hits[j] ? "check_circle" : "cancel", "fill"), k))) : (b.key || []).length ? el("details", { class: "qzt-key" }, el("summary", {}, "채점 기준"), el("ol", {}, b.key.map(k => el("li", {}, k)))) : null,
          el("div", { class: "qzt-score", role: "group", "aria-label": `${i + 1}번 점수` }, "점수 ", [0, 1, 2, 3].map(n => el("button", { type: "button", class: "seg-b", "aria-pressed": String(d.scores[q.id] === n), onclick: () => { d.scores[q.id] = n; dirty = false; paint(); } }, String(n)))),
          el("textarea", { class: "qzt-fb", rows: 2, placeholder: "학생에게 보낼 피드백", oninput: e => { d.feedback[q.id] = e.target.value; } }, d.feedback[q.id] || ""));
      }),
      el("textarea", { class: "qzt-fb", rows: 2, placeholder: "총평(학생에게 보임)", oninput: e => { d.summary = e.target.value; } }, d.summary || ""),
      el("div", { class: "qzt-btns" }, total != null ? el("b", {}, `합계 ${total}/${s.questions.length * 3}`) : null, el("span", { style: "flex:1" }),
        el("button", { type: "button", class: "btn small", disabled: !aiOk(a.id) || (Q.ai && Q.ai.running), title: aiOk(a.id) ? "이 학생의 답안을 AI 로 다시 채점합니다(직접 고친 내용은 덮어씁니다)." : "AI 선택 동의가 없는 학생입니다.", onclick: async () => { if (g && !confirm("이미 채점한 내용을 AI 채점으로 덮어쓸까요?")) return; await gradeMany([a.id]); } }, ico("auto_awesome"), "AI 채점"),
        el("button", { type: "button", class: "btn small", onclick: () => save(a.id, s) }, ico("save"), "저장"),
        el("button", { type: "button", class: "btn small primary", disabled: !g && total == null, onclick: async () => { if (await save(a.id, s)) await release([a.id]); } }, ico("send"), "저장하고 이 학생에게 보내기"))));
  }
  function renderDetail() {
    const s = session(); if (!s) return [];
    const ans = (Q.answers || []).slice().sort((a, b) => ((a.student || {}).name || "").localeCompare((b.student || {}).name || "", "ko")), unGraded = ans.filter(a => !grade(a.id));
    const stat = s.questions.map(q => { const sc = (Q.grades || []).map(g => (g.items || []).find(x => x.id === q.id)).filter(Boolean).map(x => x.score); return sc.length ? (sc.reduce((a, b) => a + b, 0) / sc.length) : null; });
    const sendable = (Q.grades || []).filter(g => status(g)[1] !== "학생에게 전송됨");
    return [el("div", { class: "qzt-dhead" }, el("h4", {}, `${s.title} 답안`), el("span", { class: "nb" }, `제출 ${ans.length}명 · 채점 ${(Q.grades || []).length}명`), el("span", { style: "flex:1" }),
        el("button", { type: "button", class: "btn small", onclick: async () => { if (!confirm("이 퀴즈의 답안·채점·학생에게 보낸 결과를 모두 지울까요? 되돌릴 수 없습니다.")) return; try { await FB.deleteQuizSession(s.id); select(""); toast("지웠습니다."); } catch (e) { alert("지우지 못했습니다: " + errText(e)); } } }, ico("delete"), "기록 삭제")),
      Q.err ? el("div", { class: "err-box" }, Q.err) : null,
      stat.some(x => x != null) ? el("div", { class: "qzt-stat" }, el("b", {}, "문항별 평균(0~3)"), s.questions.map((q, i) => el("span", { class: "nb" }, `${i + 1}번 ${stat[i] == null ? "—" : stat[i].toFixed(1)}`)), el("small", { style: "color:var(--dim)" }, "낮은 문항이 학생들이 어려워한 개념입니다.")) : null,
      el("div", { class: "qzt-tools" },
        el("button", { type: "button", class: "btn primary", disabled: !unGraded.length || !!(Q.ai && Q.ai.running), onclick: () => gradeMany(unGraded.map(a => a.id)) }, ico("auto_awesome"), `AI 채점 (미채점 ${unGraded.length}명)`),
        el("button", { type: "button", class: "btn", disabled: !sendable.length, onclick: async () => { if (!confirm(`채점한 ${sendable.length}명에게 점수와 피드백을 보낼까요? 학생 화면에 팝업으로 나타납니다.`)) return; await release(sendable.map(g => g.id)); } }, ico("send"), `채점 결과 학생에게 보내기 (${sendable.length}명)`),
        Q.ai ? el("span", { class: "lead", style: "margin:0" }, Q.ai.running ? `AI 채점 중… ${Q.ai.done}/${Q.ai.total}` : `AI 채점 ${Q.ai.done - Q.ai.fails.length}/${Q.ai.total}명 완료` + (Q.ai.skipped ? ` · AI 동의 없는 ${Q.ai.skipped}명은 직접 채점` : "") + (Q.ai.fails.length ? ` · 실패 ${Q.ai.fails.length}명(${Q.ai.fails[0].msg})` : "")) : null),
      Q.answers === null ? el("p", { class: "lead" }, "불러오는 중…") : !ans.length ? el("p", { class: "lead" }, "아직 제출한 학생이 없어요.") : el("div", { class: "qzt-list" }, ans.map(a => renderStudent(a, s)))];
  }
  /* 탭: [문제 출제·제시] (패턴·문항 고르기, 제시) / [결과] (제시한 퀴즈 기록, 답안, 채점, 피드백 보내기) */
  function renderTabs() {
    const n = (Q.sessions || []).length, tabs = [["present", "문제 출제·제시"], ["results", `결과${n ? ` (${n})` : ""}`]];
    return el("div", { class: "seg qzt-tabs", role: "tablist", "aria-label": "돌발퀴즈 화면" }, tabs.map(([k, l]) => el("button", { type: "button", role: "tab", class: "seg-b", "aria-selected": String(Q.tab === k), "aria-pressed": String(Q.tab === k), onclick: () => { Q.tab = k; paint(); } }, l)));
  }
  function render() {
    fill(root, el("h3", {}, "돌발퀴즈"),
      el("p", { class: "lead" }, "패턴을 고르고 [제시하기]를 누르면 그 패턴 장(요약 판·긴 버전)을 보고 있는 학생 화면에 팝업으로 서술형 문제가 나타나고, 학생은 제한 시간 안에 답합니다(시간이 끝나면 쓴 글이 자동 제출). 마감 뒤 이 화면에서 답안을 보고 AI 로 채점한 다음 피드백을 학생에게 보냅니다. AI 채점에는 학생의 답안(이름·이메일 제외)이 Google Gemini 로 전달되므로 개인정보 동의의 ‘AI 도우미 이용(선택)’에 동의한 학생만 AI 채점이 되고, 그렇지 않은 학생은 직접 채점합니다."),
      renderActive(), renderTabs(),
      ...(Q.tab === "present" ? renderPresent() : [el("div", { class: "qzt-cols" }, el("div", {}, ...renderHistory()), el("div", {}, ...renderDetail()))]));
  }

  /* c = {prog: () => 진도 행들, consents: () => 동의 행들}. root 는 이 메뉴의 패널. */
  function mount(panel, t, c) {
    root = panel; tok = t; ctx = c; Q.sel = ""; Q.cfg = undefined; Q.sessions = null;
    paint();
    liveSub(FB.watchQuiz(cfg => { Q.cfg = cfg || null; paint(); }), tok);
    liveSub(FB.watchQuizSessions((rows, err) => { Q.sessions = rows || []; if (err) Q.err = errText(err); paint(); }), tok);
    const iv = setInterval(() => { if (timeEl && timeEl.isConnected) { timeEl.textContent = isActive() ? mmss(Q.cfg.endsAt - Date.now()) : "0:00"; if (!isActive()) paint(); } }, 500);
    T.live.push(() => { clearInterval(iv); [Q.unA, Q.unG].forEach(f => { try { f && f(); } catch (e) {} }); Q.unA = Q.unG = null; });
  }
  return { mount, repaint: paint };
})();
