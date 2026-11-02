"use strict";
/* 학생용 앱. CONTENT(문항)는 빌드 때 주입된다. 정답·교사 메모는 학생용 빌드에 들어 있지 않다. */
const LS_KEY = "dp-inquiry-student";
let S = newState(), curWeek = 0, saveTimer = null;
let lsFailed = false;   // 브라우저 저장소가 막혔는가(boot 보다 먼저 선언)

(function boot() {
  const raw = lsGet(LS_KEY);
  if (raw) { try { const d = JSON.parse(raw); if (validState(d)) S = d; } catch (e) {} }
  curWeek = Number(lsGet(LS_KEY + "-week")) || 0;
  const hm = /^#w(\d)$/.exec(location.hash); if (hm) curWeek = Number(hm[1]) - 1;   // 첫 화면의 주차 카드에서 바로 들어오기
  if (!(curWeek >= 0 && curWeek < CONTENT.weeks.length)) curWeek = 0;
  initTheme();
  bindTop();
  render();
  initFb();
})();

function hasAnswers() { return Object.keys(S.answers).length > 0; }

function bindTop() {
  const f = $("#f-name"), n = $("#f-num");
  [[f, "name"], [n, "number"]].forEach(([inp, key]) => inp.addEventListener("input", () => { S.student[key] = inp.value; touch(); if (typeof Mon !== "undefined") Mon.refresh(); }));
  $("#btn-print").addEventListener("click", () => print());
  $("#btn-reset").addEventListener("click", () => {
    if (!confirm("이 브라우저에 있는 작성 내용을 모두 지우고 처음부터 시작합니다. 지운 내용은 복구할 수 없습니다. 계속할까요?")) return;
    S = newState(); persist(); render(); toast("초기화했습니다");
  });
}

function touch() {
  updateSaveState();
  clearTimeout(saveTimer); saveTimer = setTimeout(persist, 400);
}
function persist() {
  S.saved = new Date().toISOString();
  const ok = lsSet(LS_KEY, JSON.stringify(S));
  updateSaveState(ok);
}
function updateSaveState(lsOk) {
  if (lsOk === false) lsFailed = true; else if (lsOk === true) lsFailed = false;
  const e = $("#savestate");
  if (lsFailed) { e.className = "savestate dirty"; e.replaceChildren(ico("warning"), "자동 저장이 막혀 있어요. 창을 닫으면 작성한 내용이 사라져요"); e.title = "브라우저가 저장소 사용을 막고 있습니다(사생활 보호 모드 등)."; }
  else if (!hasAnswers()) { e.className = "savestate"; e.textContent = "아직 작성한 내용이 없어요"; e.title = ""; }
  else { e.className = "savestate clean"; e.replaceChildren(ico("check_circle", "fill"), "이 브라우저에 자동 저장됨 " + stamp(S.saved ? new Date(S.saved) : new Date())); e.title = "같은 기기·브라우저에서만 이어 쓸 수 있어요. 쓴 글은 선생님께 전달되지 않고 이 브라우저에만 남아요."; }
}

/* ---------- 진도 전달·돌발 퀴즈(Firebase) ---------- */
function initFb() {
  if (typeof FB === "undefined") return;
  if (typeof Mon !== "undefined") Mon.init();
}

/* ---------- 화면 ---------- */
function render() {
  $("#f-name").value = S.student.name; $("#f-num").value = S.student.number;
  renderTabs(); renderWeek(); updateSaveState();
  if (typeof Mon !== "undefined") { Mon.rebase(); Mon.refresh(); }
}

function renderTabs() {
  const box = $("#tabs"); box.replaceChildren();
  CONTENT.weeks.forEach((w, i) => {
    const p = weekProgress(w, S.answers), pct = p.total ? Math.round(100 * p.done / p.total) : 0;
    const t = el("button", { class: "tab", role: "tab", "aria-selected": String(i === curWeek), "data-w": i, onclick: () => { curWeek = i; lsSet(LS_KEY + "-week", i); renderTabs(); renderWeek(); scrollTo(0, 0); } },
      el("b", {}, `${w.n}주차 · ${w.concept}`), el("small", {}, w.title), el("div", { class: "bar" }, el("i", { style: `width:${pct}%` })), el("small", { class: "pg" }, `${p.done}/${p.total} 완료`));
    box.append(t);
  });
}
function refreshProgress() {
  CONTENT.weeks.forEach((w, i) => {
    const p = weekProgress(w, S.answers), t = $(`.tab[data-w="${i}"]`); if (!t) return;
    $(".bar > i", t).style.width = (p.total ? Math.round(100 * p.done / p.total) : 0) + "%"; $(".pg", t).textContent = `${p.done}/${p.total} 완료`;
  });
}

function renderWeek() {
  const w = CONTENT.weeks[curWeek], main = $("#week"); main.replaceChildren();
  main.append(el("section", { class: "hero" },
    el("div", { class: "kicker" }, `${w.n}주차 / ${CONTENT.weeks.length}주`),
    el("h2", {}, `${w.title}`),
    el("p", {}, el("span", { class: "concept" }, "핵심 개념: " + w.concept), el("span", { class: "lead" }, w.subtitle)),
    el("p", { html: w.overview }),
    el("div", { class: "pattern-links" }, el("b", {}, "함께 읽을 교재: "), w.patterns.map(p => el("a", { href: p.href, target: "_blank", rel: "noopener" }, p.name))),
    el("div", { class: "grid2" },
      el("div", { class: "card" }, el("h4", {}, "이번 주 탐구 질문"),
        el("ul", {}, [["f", "사실적", w.questions.factual], ["c", "개념적", w.questions.conceptual], ["d", "논쟁적", w.questions.debatable]]
          .flatMap(([k, lab, arr]) => arr.map(q => el("li", {}, el("span", { class: "qtag " + k }, lab), q))))),
      el("div", { class: "card" }, el("h4", {}, "이번 주 목표"), el("ul", {}, w.goals.map(g => el("li", { html: g }))),
        el("p", { class: "lead", style: "margin:8px 0 0;font-size:14px" }, ico("lightbulb"), " 일반화(결론)는 정답을 외우는 것이 아니라 4단계에서 내 말로 직접 써 보는 것입니다.")))));
  w.stages.forEach((st, si) => {
    const sec = el("section", { class: "stage", "data-s": STAGE_NO[st.key], id: `st-${w.n}-${si}` },
      el("header", {}, el("span", { class: "badge" }, `${si + 1}. ${st.title}`), el("span", { class: "min" }, `${st.en} · 약 ${st.minutes}분`)));
    if (st.intro) sec.append(el("p", { class: "intro", html: st.intro }));
    let no = 0;
    st.items.forEach(it => sec.append(renderItem(it, ANSWERABLE(it) ? ++no : 0)));
    main.append(sec);
  });
  main.append(el("div", { class: "no-print", style: "margin-top:24px;display:flex;gap:8px;flex-wrap:wrap" },
    curWeek < CONTENT.weeks.length - 1 && el("button", { class: "btn", onclick: () => { curWeek++; lsSet(LS_KEY + "-week", curWeek); renderTabs(); renderWeek(); scrollTo(0, 0); } }, "다음 주차 →")));
}

function renderItem(it, no) {
  if (it.type === "info") return el("div", { class: "item info" }, enhanceCode(el("div", { html: it.html })));
  const done = isAnswered(it, S.answers[it.id]);
  const card = el("div", { class: "item" + (done ? " done" : ""), id: it.id },
    el("div", { class: "filled-mark" }, done ? [ico("check_circle", "fill"), "작성함"] : ""),
    el("p", { class: "q" }, el("span", { class: "no" }, "Q" + no), it.optional ? el("span", { class: "opt-tag" }, "선택") : null, el("span", { html: it.q })));
  if (it.recall) card.append(recallBox(it.recall));
  if (it.compare) card.append(compareBox(it.compare));
  if (it.hint && it.type !== "text" && it.type !== "list") card.append(el("p", { class: "hint", html: it.hint }));
  card.append(renderInput(it, S.answers[it.id], v => {
    S.answers[it.id] = v; touch();
    const d = isAnswered(it, v); card.classList.toggle("done", d); $(".filled-mark", card).replaceChildren(...(d ? [ico("check_circle", "fill"), "작성함"] : []));
    refreshProgress();
    if (typeof Mon !== "undefined") Mon.note(it.id);
  }));
  return card;
}

/* 앞서 쓴 글을 다시 보여 주는 상자: 일반화를 엮어 쓰거나 처음·지금의 생각을 비교할 때 쓴다. */
function recallBox(list) {
  return el("div", { class: "recall" }, el("b", {}, "내가 앞서 쓴 글"),
    list.map(r => { const v = S.answers[r.id]; return el("div", { class: "val" }, el("span", { class: "rl" }, r.label + " "), nonEmpty(v) ? v : "(아직 쓰지 않았어요)"); }));
}
/* 이전에 한 척도 응답(예: 1주차 사전 진단)을 항목별로 보여 준다. */
function compareBox(id) {
  const v = S.answers[id], it = CONTENT.weeks.flatMap(w => w.stages.flatMap(st => st.items)).find(x => x.id === id);
  if (!it) return null;
  return el("div", { class: "recall" }, el("b", {}, "처음(1주차)에 내가 한 응답"),
    it.items.map((t, i) => el("div", { class: "val" }, el("span", { html: t }), `  →  ${v && v[i] != null ? v[i] + "/5" : "—"}`)));
}
