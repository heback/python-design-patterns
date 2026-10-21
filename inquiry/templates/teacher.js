"use strict";
/* 교사용 앱: ① 수업 가이드(예시 정답·메모) ② 학생 JSON 불러오기 → 비교·코멘트 → 코멘트 포함 JSON 내보내기 */
const LS_T = "dp-inquiry-teacher";
const T = { students: {}, view: "guide", week: 0, student: null, mode: "by-student", item: null, showKey: true };
const PHRASES = [
  "근거를 코드의 구체적인 줄·이름을 들어 설명해 보세요.",
  "핵심 개념어(변경 축, 결합, 위임, 책임)를 써서 다시 정리해 보세요.",
  "정의를 옮겨 적기보다 내가 만난 상황에 비추어 설명해 보세요.",
  "다른 패턴과 비교해 보면 차이가 더 분명해져요.",
  "코드를 직접 실행해 출력으로 확인해 보세요.",
  "반례까지 생각한 점이 돋보여요. 아주 좋아요!",
  "일반화 문장에 '~할수록 ~하지만 ~'처럼 얻는 것과 치르는 것을 함께 담아 보세요."
];
const itemsOf = w => w.stages.flatMap(s => s.items).filter(ANSWERABLE);

(function boot() {
  const raw = lsGet(LS_T);
  if (raw) { try { const d = JSON.parse(raw); if (d && d.students) T.students = d.students; } catch (e) {} }
  T.student = Object.keys(T.students)[0] || null;
  initTheme();
  $("#btn-load").addEventListener("click", () => $("#file-in").click());
  $("#file-in").addEventListener("change", e => { importFiles([...e.target.files]); e.target.value = ""; });
  $("#btn-print").addEventListener("click", () => print());
  $("#btn-clear").addEventListener("click", () => { if (confirm("불러온 모든 학생 데이터와 작성 중인 코멘트를 이 브라우저에서 지웁니다. 코멘트 파일을 내보냈는지 확인하셨나요?")) { T.students = {}; T.student = null; persistT(); render(); } });
  bindDrop(importFiles);
  render();
})();

function persistT() { lsSet(LS_T, JSON.stringify({ students: T.students })); }
const keyOf = d => [d.student.klass, d.student.number, d.student.name].map(x => (x || "").trim()).join("|");
const labelOf = d => [d.student.klass, d.student.number && d.student.number + "번", d.student.name].filter(x => x && String(x).trim()).join(" ") || "(이름 없음)";

async function importFiles(files) {
  let ok = 0, msgs = [];
  for (const f of files) {
    try {
      const d = await readJsonFile(f);
      if (!validState(d)) throw new Error(f.name + ": 탐구학습 JSON이 아닙니다.");
      d.student = Object.assign({ name: "", number: "", klass: "" }, d.student); d.feedback = d.feedback || {};
      const k = keyOf(d), old = T.students[k];
      if (old) d.feedback = Object.assign({}, d.feedback, old.feedback);   // 이미 쓴 코멘트는 보존
      T.students[k] = d; T.student = T.student || k; ok++;
    } catch (e) { msgs.push(e.message); }
  }
  if (ok) { T.view = "review"; if (!T.students[T.student]) T.student = Object.keys(T.students)[0]; persistT(); toast(`${ok}개 파일을 불러왔습니다`); }
  if (msgs.length) alert(msgs.join("\n"));
  render();
}

function render() {
  const nav = $("#views"); nav.replaceChildren(
    ...[["guide", "📘 수업 가이드·예시 정답"], ["review", `🧑‍🎓 학생 응답·코멘트 (${Object.keys(T.students).length})`]].map(([k, l]) =>
      el("button", { class: "tab", role: "tab", "aria-selected": String(T.view === k), onclick: () => { T.view = k; render(); scrollTo(0, 0); } }, el("b", {}, l))));
  const main = $("#main"); main.replaceChildren();
  (T.view === "guide" ? renderGuide : renderReview)(main);
}

/* ===================== 수업 가이드 ===================== */
function weekTabs(cur, onPick, extra) {
  return el("div", { class: "tabs", style: "padding:0 0 12px" }, ...(extra || []), CONTENT.weeks.map((w, i) =>
    el("button", { class: "tab", "aria-selected": String(cur === i), onclick: () => onPick(i) }, el("b", {}, `${w.n}주차 · ${w.concept}`), el("small", {}, w.title))));
}
function renderGuide(main) {
  const g = T.guide == null ? -1 : T.guide;
  main.append(weekTabs(g, i => { T.guide = i; render(); scrollTo(0, 0); }, [
    el("button", { class: "tab", "aria-selected": String(g === -1), onclick: () => { T.guide = -1; render(); } }, el("b", {}, "운영 안내"), el("small", {}, "5주 개관·평가·JSON"))]));
  if (g === -1) return guideCourse(main);
  const w = CONTENT.weeks[g], t = w.teacher;
  main.append(el("section", { class: "hero" },
    el("div", { class: "kicker" }, `교사 가이드 · ${w.n}주차`),
    el("h2", {}, w.title), el("p", {}, el("span", { class: "concept" }, "핵심 개념: " + w.concept), el("span", { class: "lead" }, w.subtitle)),
    el("p", { html: t.summary }),
    el("div", { class: "sample", style: "margin-top:10px" }, el("b", {}, "도달 목표 일반화 (학생이 4단계에서 자기 말로 쓰게 될 문장)"), el("div", {}, w.target)),
    el("div", { class: "grid2" },
      card("학습 목표", w.goals), card("탐구 질문 (발문 예)", [].concat(
        w.questions.factual.map(q => "[사실적] " + q), w.questions.conceptual.map(q => "[개념적] " + q), w.questions.debatable.map(q => "[논쟁적] " + q))),
      card("시간 배분 (주 2차시 기준)", w.stages.map(s => `${s.title}(${s.en}) — ${s.minutes}분`)),
      card("준비물", t.prep), card("진행 팁", t.tips), card("예상 오개념", t.misconceptions), card("평가 포인트", t.assessment), card("교실 토론 발문", t.discussion))));
  w.stages.forEach((st, si) => {
    const sec = el("section", { class: "stage", "data-s": STAGE_NO[st.key] }, el("header", {}, el("span", { class: "badge" }, `${si + 1}. ${st.title}`), el("span", { class: "min" }, `${st.en} · ${st.minutes}분`)));
    if (st.tnote) sec.append(el("div", { class: "tnote" }, el("b", {}, "이 단계 운영 메모"), el("div", { html: st.tnote })));
    let no = 0;
    st.items.forEach(it => {
      if (it.type === "info") { sec.append(el("div", { class: "item info" }, el("div", { html: it.html }))); return; }
      no++;
      const c = el("div", { class: "item", id: it.id }, el("p", { class: "q" }, el("span", { class: "no" }, "Q" + no), el("span", { html: it.q })));
      if (it.hint) c.append(el("p", { class: "hint", html: it.hint }));
      if (["choice", "multi", "table", "sort"].includes(it.type)) c.append(el("details", { class: "fold" }, el("summary", {}, "문항 보기"), renderInput(it, null, () => {})));
      const s = renderSample(it);
      c.append(el("div", { class: "sample" }, el("b", {}, it.type === "scales" ? "" : "예시 정답"), s || el("div", { class: "lead" }, "정답이 없는 문항입니다 — 학생 응답 자체가 평가·상담 자료입니다.")));
      if (it.note) c.append(el("div", { class: "tnote" }, el("b", {}, "채점·지도 포인트"), el("div", { html: it.note })));
      sec.append(c);
    });
    main.append(sec);
  });
}
function card(title, arr) {
  return el("div", { class: "card" }, el("h4", {}, title), el("ul", {}, (arr || []).map(x => el("li", { html: x }))));
}
function guideCourse(main) {
  const C = COURSE;
  main.append(el("section", { class: "hero" }, el("div", { class: "kicker" }, "교사 가이드"), el("h2", {}, C.title), el("p", { html: C.intro }),
    el("div", { class: "grid2" }, card("수업 설계 원리 (개념기반탐구)", C.principles), card("수업 흐름 6단계", C.stages), card("준비와 환경", C.setup))));
  main.append(el("section", { class: "hero" }, el("h3", { style: "margin-top:0" }, "5주 개관"),
    el("div", { class: "tbl-wrap" }, el("table", { class: "ro" }, el("thead", {}, el("tr", {}, ["주", "핵심 개념", "다루는 패턴", "일반화(목표)", "산출물"].map(h => el("th", {}, h)))),
      el("tbody", {}, CONTENT.weeks.map(w => el("tr", {}, el("td", {}, w.n + "주"), el("td", {}, w.concept), el("td", {}, w.patterns.map(p => p.name).join(", ")), el("td", {}, w.target), el("td", {}, w.product))))))));
  main.append(el("section", { class: "hero" }, el("h3", { style: "margin-top:0" }, "JSON 주고받기 흐름"),
    el("ol", {}, C.workflow.map(x => el("li", { html: x }))),
    el("details", { class: "fold" }, el("summary", {}, "JSON 파일 구조 보기"), el("pre", {}, el("code", {}, C.jsonSample)))));
  main.append(el("section", { class: "hero" }, el("h3", { style: "margin-top:0" }, "평가 루브릭 (◎ 3 · ○ 2 · △ 1)"),
    el("div", { class: "tbl-wrap" }, el("table", { class: "ro" }, el("thead", {}, el("tr", {}, ["관점", "◎ 우수", "○ 적절", "△ 보완 필요"].map(h => el("th", {}, h)))),
      el("tbody", {}, C.rubric.map(r => el("tr", {}, r.map((c, i) => el(i ? "td" : "th", {}, c)))))))));
}

/* ===================== 학생 응답·코멘트 ===================== */
function renderReview(main) {
  const keys = Object.keys(T.students);
  if (!keys.length) {
    main.append(el("section", { class: "hero" }, el("h2", {}, "학생 JSON을 불러오세요"),
      el("p", {}, "학생들이 제출한 ‘…_탐구학습.json’ 파일을 위 [📂 학생 JSON 불러오기]로 여러 개 한꺼번에 선택하거나, 이 창에 끌어다 놓으세요."),
      el("p", { class: "lead" }, "불러온 데이터와 작성한 코멘트는 이 브라우저에 자동 보관됩니다. 코멘트가 끝나면 학생별로 ‘코멘트 포함 JSON’을 내보내 학생에게 돌려주세요."),
      el("button", { class: "btn primary", onclick: () => { loadDemo(); } }, "예시 학생 데이터로 체험해 보기")));
    return;
  }
  if (!T.students[T.student]) T.student = keys[0];
  const modes = el("div", { class: "tabs", style: "padding:0 0 12px" },
    [["by-student", "학생별 보기"], ["by-item", "문항별 모아보기"], ["matrix", "현황표"]].map(([k, l]) =>
      el("button", { class: "tab", "aria-selected": String(T.mode === k), onclick: () => { T.mode = k; render(); } }, el("b", {}, l))),
    el("label", { class: "tab", style: "flex:0 0 auto;display:flex;gap:6px;align-items:center" }, el("input", { type: "checkbox", ...(T.showKey ? { checked: "" } : {}), onchange: e => { T.showKey = e.target.checked; render(); } }), "예시 정답 함께 보기"));
  main.append(modes);
  if (T.mode === "matrix") return reviewMatrix(main);
  main.append(weekTabs(T.week, i => { T.week = i; T.item = null; render(); }));
  if (T.mode === "by-item") return reviewByItem(main);
  reviewByStudent(main);
}

function fbOf(d, id) { return d.feedback[id] || (d.feedback[id] = {}); }
function fbBox(d, id, label) {
  const f = d.feedback[id] || {};
  const wrap = el("div", { class: "fb no-print-border" });
  const marks = el("div", { style: "display:flex;gap:6px;align-items:center;flex-wrap:wrap;margin-bottom:6px" }, el("b", {}, label || "교사 코멘트"));
  const ta = taInput(f.comment || "", v => { const x = fbOf(d, id); x.comment = v; x.at = new Date().toISOString(); persistT(); }, { rows: 2, placeholder: "학생에게 보낼 코멘트…" });
  [3, 2, 1].forEach(m => {
    const b = el("button", { class: "btn small" + ((f.mark === m) ? " primary" : ""), type: "button", onclick: () => {
      const x = fbOf(d, id); x.mark = x.mark === m ? null : m; x.at = new Date().toISOString(); persistT();
      $$("button[data-m]", marks).forEach(bb => bb.classList.toggle("primary", Number(bb.dataset.m) === x.mark));
    }, "data-m": m }, MARKS[m][0] + " " + MARKS[m][1]);
    marks.append(b);
  });
  const sel = el("select", { style: "width:auto;max-width:260px;font-size:13px;padding:2px 6px", onchange: e => { if (!e.target.value) return; ta.value = (ta.value ? ta.value + "\n" : "") + e.target.value; ta.dispatchEvent(new Event("input")); e.target.value = ""; } },
    el("option", { value: "" }, "＋ 자주 쓰는 코멘트"), PHRASES.map(p => el("option", { value: p }, p.length > 30 ? p.slice(0, 30) + "…" : p)));
  marks.append(sel);
  wrap.append(marks, ta); return wrap;
}
function answerBlock(it, d) {
  const v = d.answers[it.id], chk = autoCheck(it, v), box = el("div", {});
  const head = el("div", { style: "display:flex;gap:8px;align-items:center;margin-bottom:4px" }, el("b", { style: "font-size:13px;color:var(--accent)" }, "학생 응답"));
  if (chk) head.append(el("span", { class: "pill " + chk.state }, "자동 판정: " + chk.text));
  box.append(head, renderValue(it, v));
  return box;
}
function itemCard(it, no, d, withName) {
  const c = el("div", { class: "item", id: (withName ? "n-" : "") + it.id },
    el("p", { class: "q" }, el("span", { class: "no" }, "Q" + no), el("span", { html: it.q })));
  c.append(answerBlock(it, d));
  return c;
}
function reviewByStudent(main) {
  const d = T.students[T.student], w = CONTENT.weeks[T.week];
  const side = el("div", { style: "display:flex;gap:8px;flex-wrap:wrap;align-items:center;margin-bottom:12px" },
    el("b", {}, "학생: "), el("select", { style: "width:auto", onchange: e => { T.student = e.target.value; render(); } },
      Object.entries(T.students).map(([k, s]) => { const o = el("option", { value: k }, labelOf(s)); if (k === T.student) o.selected = true; return o; })),
    el("span", { class: "lead" }, "저장 시각 " + (d.saved ? stamp(new Date(d.saved)) : "—")),
    el("span", { class: "grow", style: "flex:1" }),
    el("button", { class: "btn primary", onclick: () => exportStudent(d) }, "💾 이 학생 코멘트 파일 내보내기"),
    el("button", { class: "btn", onclick: exportAll }, "전체 내보내기"),
    el("button", { class: "btn", onclick: exportCsv }, "요약 CSV"),
    el("button", { class: "btn ghost danger", onclick: () => { if (confirm(labelOf(d) + " 학생 데이터를 목록에서 제거할까요?")) { delete T.students[T.student]; T.student = null; persistT(); render(); } } }, "제거"));
  main.append(side);
  const p = weekProgress(w, d.answers);
  main.append(el("p", { class: "lead" }, `${w.n}주차 응답 ${p.done}/${p.total}`));
  let no = 0;
  w.stages.forEach((st, si) => {
    const its = st.items.filter(ANSWERABLE); if (!its.length) return;
    const sec = el("section", { class: "stage", "data-s": STAGE_NO[st.key] }, el("header", {}, el("span", { class: "badge" }, `${si + 1}. ${st.title}`)));
    st.items.forEach(it => {
      if (!ANSWERABLE(it)) return; no++;
      const c = itemCard(it, no, d);
      if (T.showKey && it.answer != null) c.append(el("div", { class: "sample" }, el("b", {}, "예시 정답"), renderSample(it)));
      if (it.note) c.append(el("details", { class: "fold" }, el("summary", {}, "채점·지도 포인트"), el("div", { class: "tnote", html: it.note })));
      c.append(fbBox(d, it.id));
      sec.append(c);
    });
    main.append(sec);
  });
  main.append(el("section", { class: "stage", "data-s": 6 }, fbBox(d, "week-" + w.n, `${w.n}주차 총평`),
    T.week === CONTENT.weeks.length - 1 ? el("div", { style: "margin-top:10px" }, fbBox(d, "_overall", "종합 코멘트(마지막 주차에 표시)")) : null));
}
function reviewByItem(main) {
  const w = CONTENT.weeks[T.week], its = itemsOf(w);
  if (!T.item || !its.find(i => i.id === T.item)) T.item = its[0].id;
  const it = its.find(i => i.id === T.item), no = its.indexOf(it) + 1;
  main.append(el("div", { style: "margin-bottom:12px;display:flex;gap:8px;align-items:center" }, el("b", {}, "문항: "),
    el("select", { onchange: e => { T.item = e.target.value; render(); } }, its.map((x, i) => { const o = el("option", { value: x.id }, `Q${i + 1}. ` + x.q.replace(/<[^>]+>/g, "").slice(0, 70)); if (x.id === T.item) o.selected = true; return o; }))));
  main.append(el("div", { class: "item" }, el("p", { class: "q" }, el("span", { class: "no" }, "Q" + no), el("span", { html: it.q })),
    T.showKey && it.answer != null ? el("div", { class: "sample" }, el("b", {}, "예시 정답"), renderSample(it)) : null,
    it.note ? el("div", { class: "tnote" }, el("b", {}, "채점·지도 포인트"), el("div", { html: it.note })) : null));
  Object.entries(T.students).forEach(([k, d]) => {
    const c = el("div", { class: "item", style: "margin-left:18px" }, el("p", { class: "q" }, labelOf(d)), answerBlock(it, d), fbBox(d, it.id));
    main.append(c);
  });
}
function reviewMatrix(main) {
  const head = ["학생", ...CONTENT.weeks.map(w => w.n + "주 응답"), "선택형 자동판정", "코멘트 수"];
  const rows = Object.entries(T.students).map(([k, d]) => {
    let ok = 0, tot = 0;
    CONTENT.weeks.forEach(w => itemsOf(w).forEach(it => { if (["choice", "multi", "sort"].includes(it.type) && it.answer) { const c = autoCheck(it, d.answers[it.id]); if (c) { tot++; if (c.state === "ok") ok++; } } }));
    const n = Object.values(d.feedback).filter(f => f && (f.comment || f.mark)).length;
    return el("tr", {}, el("th", { style: "cursor:pointer", onclick: () => { T.student = k; T.mode = "by-student"; render(); } }, labelOf(d)),
      CONTENT.weeks.map(w => { const p = weekProgress(w, d.answers), pct = p.total ? Math.round(100 * p.done / p.total) : 0;
        return el("td", { style: `background:linear-gradient(90deg,var(--ok-soft) ${pct}%,transparent ${pct}%)` }, `${p.done}/${p.total}`); }),
      el("td", {}, tot ? `${ok}/${tot} 정답` : "—"), el("td", {}, String(n)));
  });
  main.append(el("div", { class: "tbl-wrap" }, el("table", { class: "ro" }, el("thead", {}, el("tr", {}, head.map(h => el("th", {}, h)))), el("tbody", {}, rows))),
    el("p", { class: "lead" }, "학생 이름을 누르면 그 학생의 응답 화면으로 이동합니다."));
}

/* ---------- 내보내기 ---------- */
function exportStudent(d) {
  const out = Object.assign({}, d, { teacherSaved: new Date().toISOString() });
  const name = [d.student.klass, d.student.number, d.student.name].map(safeName).filter(Boolean).join("_") + "_코멘트.json";
  download(name, JSON.stringify(out, null, 2)); toast("내보냈습니다: " + name);
}
function exportAll() {
  const list = Object.values(T.students);
  if (list.length > 1 && !confirm(`${list.length}개의 파일이 차례로 내려받아집니다. 브라우저가 ‘여러 파일 다운로드’ 허용을 물으면 허용해 주세요.`)) return;
  list.forEach((d, i) => setTimeout(() => exportStudent(d), i * 350));
}
function exportCsv() {
  const q = s => '"' + String(s).replace(/"/g, '""') + '"';
  const lines = [["학급", "번호", "이름", ...CONTENT.weeks.map(w => w.n + "주 응답률(%)"), "선택형 정답/전체", "주차별 총평"].map(q).join(",")];
  Object.values(T.students).forEach(d => {
    let ok = 0, tot = 0;
    CONTENT.weeks.forEach(w => itemsOf(w).forEach(it => { if (["choice", "multi", "sort"].includes(it.type) && it.answer) { const c = autoCheck(it, d.answers[it.id]); if (c) { tot++; if (c.state === "ok") ok++; } } }));
    lines.push([d.student.klass, d.student.number, d.student.name,
      ...CONTENT.weeks.map(w => { const p = weekProgress(w, d.answers); return p.total ? Math.round(100 * p.done / p.total) : 0; }),
      `${ok}/${tot}`, CONTENT.weeks.map(w => ((d.feedback["week-" + w.n] || {}).comment || "")).join(" / ")].map(q).join(","));
  });
  download("탐구학습_현황.csv", "﻿" + lines.join("\n"), "text/csv"); toast("CSV를 내보냈습니다");
}

/* ---------- 체험용 예시 학생 ---------- */
function loadDemo() {
  const d = newState(); d.student = { name: "예시학생", number: "1", klass: "체험반" };
  for (const w of CONTENT.weeks) for (const it of itemsOf(w)) {
    const a = it.answer; if (a == null) continue;
    if (it.type === "choice") d.answers[it.id] = { sel: (a.sel + 1) % it.options.length, why: "(체험용) 잘 모르겠지만 이게 더 자연스러워 보여서요." };
    else if (it.type === "multi") d.answers[it.id] = { sel: a.sel.slice(0, 1), why: "(체험용) 하나만 골랐어요." };
    else if (typeof a === "string") d.answers[it.id] = "(체험용) " + a.split(/(?<=[.다요])\s/)[0];
  }
  T.students[keyOf(d)] = d; T.student = keyOf(d); T.view = "review"; persistT(); render();
}
