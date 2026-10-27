"use strict";
/* 학생용 앱. CONTENT(문항)는 빌드 때 주입된다. 정답·교사 메모는 학생용 빌드에 들어 있지 않다. */
const LS_KEY = "dp-inquiry-student";
let S = newState(), dirty = false, curWeek = 0, saveTimer = null;

(function boot() {
  const raw = lsGet(LS_KEY);
  if (raw) { try { const d = JSON.parse(raw); if (validState(d)) S = d; } catch (e) {} }
  curWeek = Number(lsGet(LS_KEY + "-week")) || 0;
  const hm = /^#w(\d)$/.exec(location.hash); if (hm) curWeek = Number(hm[1]) - 1;   // 첫 화면의 주차 카드에서 바로 들어오기
  if (!(curWeek >= 0 && curWeek < CONTENT.weeks.length)) curWeek = 0;
  initTheme();
  bindTop();
  render();
  bindDrop(files => importFile(files[0]));
  initFb();
  addEventListener("beforeunload", e => { if (dirty && hasAnswers()) { e.preventDefault(); e.returnValue = ""; } });
})();

function hasAnswers() { return Object.keys(S.answers).length > 0; }

function bindTop() {
  const f = $("#f-name"), n = $("#f-num");
  [[f, "name"], [n, "number"]].forEach(([inp, key]) => inp.addEventListener("input", () => { S.student[key] = inp.value; touch(); }));
  $("#btn-save").addEventListener("click", saveFile);
  $("#btn-load").addEventListener("click", () => $("#file-in").click());
  $("#file-in").addEventListener("change", e => { if (e.target.files[0]) importFile(e.target.files[0]); e.target.value = ""; });
  $("#btn-print").addEventListener("click", () => print());
  $("#btn-reset").addEventListener("click", () => {
    if (!confirm("작성한 모든 내용을 지우고 처음부터 시작합니다. 저장하지 않은 내용은 복구할 수 없습니다. 계속할까요?")) return;
    S = newState(); dirty = false; persist(); render(); toast("초기화했습니다");
  });
}

function touch() {
  dirty = true; updateSaveState();
  clearTimeout(saveTimer); saveTimer = setTimeout(persist, 400);
}
function persist() {
  S.saved = new Date().toISOString();
  const ok = lsSet(LS_KEY, JSON.stringify(S));
  updateSaveState(ok);
}
function updateSaveState(lsOk) {
  const e = $("#savestate");
  if (dirty) { e.className = "savestate dirty"; e.textContent = "● 아직 파일로 저장하지 않았어요"; }
  else if (!hasAnswers()) { e.className = "savestate"; e.textContent = "아직 작성한 내용이 없어요"; }
  else { e.className = "savestate clean"; e.textContent = "✔ 파일 저장됨 " + stamp(); }
  if (lsOk === false) e.title = "브라우저 자동 저장이 막혀 있습니다. 반드시 JSON 파일로 저장하세요.";
}

function saveFile() {
  if (!S.student.number.trim()) { toast("먼저 학번을 입력해 주세요"); $("#f-num").focus(); return; }
  if (!S.student.name.trim()) { toast("먼저 성명을 입력해 주세요"); $("#f-name").focus(); return; }
  S.saved = new Date().toISOString();
  const name = [S.student.number, S.student.name].map(safeName).filter(Boolean).join("_") + "_탐구학습.json";
  download(name, JSON.stringify(S, null, 2));
  dirty = false; persist(); updateSaveState(); toast("저장했습니다: " + name);
}

async function importFile(file) {
  try {
    const d = await readJsonFile(file);
    if (!validState(d)) throw new Error("이 앱에서 저장한 탐구학습 JSON이 아닙니다.");
    if (hasAnswers() && dirty && !confirm("지금 작성 중인 내용(저장 전)이 불러온 파일의 내용으로 바뀝니다. 계속할까요?")) return;
    S = Object.assign(newState(), d, { student: Object.assign({ name: "", number: "", klass: "" }, d.student) });
    S.feedback = S.feedback || {};
    dirty = false; persist(); render();
    toast("불러왔습니다" + (Object.keys(S.feedback).length ? " · 선생님 코멘트가 포함되어 있어요" : ""));
  } catch (e) { alert(e.message); }
}

/* ---------- 제출(Firebase) ---------- */
let SET;   // 제출 설정: undefined=확인 중/불러오기 실패, null=설정 없음(닫힘), 객체=교사 설정
function initFb() {
  if (typeof FB === "undefined") return;
  ["#btn-submit", "#btn-getfb"].forEach(q => { $(q).hidden = false; });
  $("#btn-submit").addEventListener("click", submitCurrent);
  $("#btn-getfb").addEventListener("click", getFeedback);
  FB.watchSettings(s => { SET = s; updateSubmitUi(); }).catch(() => { SET = undefined; updateSubmitUi(); });
}
function weekStatus(n) {
  if (SET === undefined) return { ok: false, msg: "제출 설정을 확인하는 중이에요(인터넷 연결 확인). 파일 저장은 언제든 할 수 있어요." };
  if (!SET || !SET.open || !(SET.weeks || {})[n]) return { ok: false, msg: `${n}주차는 지금 제출할 수 없어요. 선생님이 열어 주면 제출할 수 있어요. (JSON 저장은 가능)` };
  const now = Date.now(), t = x => x && x.toMillis ? x.toMillis() : null;
  if (t(SET.opensAt) && now < t(SET.opensAt)) return { ok: false, msg: `${n}주차 제출은 ${stamp(new Date(t(SET.opensAt)))}부터예요.` };
  if (t(SET.closesAt) && now >= t(SET.closesAt)) return { ok: false, msg: `${n}주차 제출이 ${stamp(new Date(t(SET.closesAt)))}에 마감됐어요.` };
  return { ok: true, msg: `${n}주차 제출이 열려 있어요` + (t(SET.closesAt) ? ` · 마감 ${stamp(new Date(t(SET.closesAt)))}` : "") + ". 마감 전에는 다시 제출해 덮어쓸 수 있어요." };
}
function updateSubmitUi() {
  if (typeof FB === "undefined") return;
  const n = CONTENT.weeks[curWeek].n, st = weekStatus(n);
  $("#btn-submit").disabled = !st.ok; $("#btn-submit").title = st.msg;
  $("#f-code").hidden = !(SET && SET.hasCode);
  const note = $("#submit-note"); if (note) { note.textContent = st.msg; note.style.opacity = st.ok ? "1" : ".8"; }
}
const fbMsg = e => /permission|denied/i.test(e.code + e.message) ? "제출할 수 없어요. 열린 주차인지, 제출 코드가 맞는지, 같은 학번·성명으로 다른 기기에서 이미 제출하지 않았는지 확인하세요." : "오류: " + FB.fbErr(e);
async function submitCurrent() {
  if (!S.student.number.trim()) { toast("먼저 학번을 입력해 주세요"); $("#f-num").focus(); return; }
  if (!S.student.name.trim()) { toast("먼저 성명을 입력해 주세요"); $("#f-name").focus(); return; }
  const n = CONTENT.weeks[curWeek].n, st = weekStatus(n);
  if (!st.ok) { toast(st.msg); return; }
  if (SET.hasCode && !$("#f-code").value.trim()) { toast("선생님이 알려 준 제출 코드를 입력해 주세요"); $("#f-code").focus(); return; }
  if (!confirm(`${n}주차 응답을 선생님께 제출할까요? 마감 전에는 다시 제출할 수 있어요.`)) return;
  try { const c = await FB.submitWeek(S, n, $("#f-code").value.trim()); toast(`${n}주차 제출 완료 (응답 ${c}개)`); }
  catch (e) { alert(fbMsg(e)); }
}
async function getFeedback() {
  if (!S.student.number.trim()) { toast("먼저 학번을 입력해 주세요"); $("#f-num").focus(); return; }
  if (!S.student.name.trim()) { toast("먼저 성명을 입력해 주세요"); $("#f-name").focus(); return; }
  try {
    const fb = await FB.fetchPublished(S.student);
    if (!Object.keys(fb).length) { toast("아직 공개된 코멘트가 없어요"); return; }
    S.feedback = Object.assign({}, S.feedback, fb); persist(); render(); toast("선생님 코멘트를 가져왔어요");
  } catch (e) { alert(/permission|denied/i.test(e.code + e.message) ? "이 브라우저에서 제출한 기록이 없어요. 제출한 같은 기기·브라우저에서 눌러 주세요(다른 기기는 선생님이 보낸 코멘트 파일을 [불러오기])." : "오류: " + FB.fbErr(e)); }
}

/* ---------- 화면 ---------- */
function render() {
  $("#f-name").value = S.student.name; $("#f-num").value = S.student.number;
  renderTabs(); renderWeek(); updateSaveState();
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
  const hasFb = Object.values(S.feedback || {}).some(f => f && (f.comment || f.mark));
  if (typeof FB !== "undefined") main.append(el("div", { class: "banner", id: "submit-note" }));
  if (hasFb) main.append(el("div", { class: "banner" }, el("b", {}, "선생님 코멘트가 도착했어요. "), "각 문항 아래 보라색 상자와 주차 마지막의 총평을 읽어 보고, 고쳐 쓴 뒤 다시 저장해서 제출하세요."));
  const fbWeek = (S.feedback || {})["week-" + w.n];
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
        el("p", { class: "lead", style: "margin:6px 0 0;font-size:14px" }, "💡 일반화(결론)는 정답을 외우는 것이 아니라 4단계에서 내 말로 직접 써 보는 것입니다.")))));
  w.stages.forEach((st, si) => {
    const sec = el("section", { class: "stage", "data-s": STAGE_NO[st.key], id: `st-${w.n}-${si}` },
      el("header", {}, el("span", { class: "badge" }, `${si + 1}. ${st.title}`), el("span", { class: "min" }, `${st.en} · 약 ${st.minutes}분`)));
    if (st.intro) sec.append(el("p", { class: "intro", html: st.intro }));
    let no = 0;
    st.items.forEach(it => sec.append(renderItem(it, ANSWERABLE(it) ? ++no : 0)));
    main.append(sec);
  });
  if (fbWeek && fbWeek.comment) main.append(el("div", { class: "fb" }, el("b", {}, `${w.n}주차 총평`), el("div", { class: "val" }, fbWeek.comment)));
  const ov = (S.feedback || {})._overall;
  if (curWeek === CONTENT.weeks.length - 1 && ov && ov.comment) main.append(el("div", { class: "fb" }, el("b", {}, "선생님 종합 코멘트"), el("div", { class: "val" }, ov.comment)));
  main.append(el("div", { class: "no-print", style: "margin-top:24px;display:flex;gap:8px;flex-wrap:wrap" },
    el("button", { class: "btn primary", onclick: saveFile }, "💾 JSON으로 저장"),
    typeof FB !== "undefined" && el("button", { class: "btn primary", onclick: submitCurrent }, "📤 이번 주차 제출"),
    curWeek < CONTENT.weeks.length - 1 && el("button", { class: "btn", onclick: () => { curWeek++; lsSet(LS_KEY + "-week", curWeek); renderTabs(); renderWeek(); scrollTo(0, 0); } }, "다음 주차 →")));
  updateSubmitUi();
}

function renderItem(it, no) {
  if (it.type === "info") return el("div", { class: "item info" }, enhanceCode(el("div", { html: it.html })));
  const done = isAnswered(it, S.answers[it.id]);
  const card = el("div", { class: "item" + (done ? " done" : ""), id: it.id },
    el("div", { class: "filled-mark" }, done ? "✔ 작성함" : ""),
    el("p", { class: "q" }, el("span", { class: "no" }, "Q" + no), it.optional ? el("span", { class: "opt-tag" }, "선택") : null, el("span", { html: it.q })));
  if (it.recall) card.append(recallBox(it.recall));
  if (it.compare) card.append(compareBox(it.compare));
  if (it.hint && it.type !== "text" && it.type !== "list") card.append(el("p", { class: "hint", html: it.hint }));
  card.append(renderInput(it, S.answers[it.id], v => {
    S.answers[it.id] = v; touch();
    const d = isAnswered(it, v); card.classList.toggle("done", d); $(".filled-mark", card).textContent = d ? "✔ 작성함" : "";
    refreshProgress();
  }));
  const fb = (S.feedback || {})[it.id];
  if (fb && (fb.comment || fb.mark)) card.append(el("div", { class: "fb" }, el("b", {}, "선생님 코멘트 "), fb.mark && MARKS[fb.mark] ? el("span", { class: "mk" }, MARKS[fb.mark][0] + " " + MARKS[fb.mark][1]) : null, fb.comment ? el("div", { class: "val" }, fb.comment) : null));
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
