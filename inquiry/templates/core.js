"use strict";
/* 학생용·교사용이 공유하는 엔진: 문항 렌더링, 응답 판정, 파일 입출력.
   응답 값의 모양(JSON에 그대로 저장된다)
   text: string | choice: {sel, why} | multi: {sel:[], why} | table: string[][] | sort: {카드번호: 칸번호}
   triples: string[][3] | list: string[] | scales: (number|null)[] | code: string */

const APP = "dp-inquiry", SCHEMA = 1;
const $ = (s, r) => (r || document).querySelector(s);
const $$ = (s, r) => Array.from((r || document).querySelectorAll(s));

function el(tag, props, ...kids) {
  const e = document.createElement(tag);
  for (const [k, v] of Object.entries(props || {})) {
    if (v == null || v === false) continue;
    if (k === "class") e.className = v;
    else if (k === "html") e.innerHTML = v;
    else if (k.startsWith("on")) e.addEventListener(k.slice(2), v);
    else e.setAttribute(k, v === true ? "" : v);
  }
  for (const c of kids.flat()) if (c != null && c !== false) e.append(c.nodeType ? c : document.createTextNode(c));
  return e;
}

function autosize(t) { if (t.classList.contains("code")) return; t.style.height = "auto"; t.style.height = (t.scrollHeight + 2) + "px"; }
function toast(msg) {
  let t = $(".toast"); if (!t) { t = el("div", { class: "toast" }); document.body.append(t); }
  t.textContent = msg; t.classList.add("on"); clearTimeout(t._h); t._h = setTimeout(() => t.classList.remove("on"), 2400);
}
function lsGet(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }
function lsSet(k, v) { try { localStorage.setItem(k, v); return true; } catch (e) { return false; } }
function download(name, text, mime) {
  const a = el("a", { href: URL.createObjectURL(new Blob([text], { type: mime || "application/json" })), download: name });
  document.body.append(a); a.click(); a.remove(); setTimeout(() => URL.revokeObjectURL(a.href), 2000);
}
function safeName(s) { return String(s || "").trim().replace(/[\\/:*?"<>|\s]+/g, "_"); }
function stamp(d) { d = d || new Date(); const p = n => String(n).padStart(2, "0"); return `${d.getMonth() + 1}/${d.getDate()} ${p(d.getHours())}:${p(d.getMinutes())}`; }

/* ---------- 응답 여부·자동 판정 ---------- */
const nonEmpty = s => typeof s === "string" && s.trim() !== "";
function isAnswered(it, v) {
  if (v == null) return false;
  switch (it.type) {
    case "text": return nonEmpty(v);
    case "code": return nonEmpty(v) && v.trim() !== (it.starter || "").trim();
    case "choice": return v.sel != null;
    case "multi": return Array.isArray(v.sel) && v.sel.length > 0;
    case "table": return Array.isArray(v) && v.some(r => Array.isArray(r) && r.some(nonEmpty));
    case "sort": return Object.values(v).some(x => x !== "" && x != null);
    case "triples": return Array.isArray(v) && v.filter(r => r.every(nonEmpty)).length > 0;
    case "list": return Array.isArray(v) && v.some(nonEmpty);
    case "scales": return Array.isArray(v) && v.some(x => x != null);
  }
  return false;
}
const ANSWERABLE = it => it.type !== "info";
function weekProgress(week, answers) {
  let total = 0, done = 0;
  for (const st of week.stages) for (const it of st.items) if (ANSWERABLE(it)) { total++; if (isAnswered(it, answers[it.id])) done++; }
  return { total, done };
}
/* 선택형만 자동 판정. 반환: null | {state:"ok"|"part"|"bad", text} */
function autoCheck(it, v) {
  const a = it.answer;
  if (!a || !isAnswered(it, v)) return null;
  if (it.type === "choice") return v.sel === a.sel ? { state: "ok", text: "정답" } : { state: "bad", text: "오답" };
  if (it.type === "multi") {
    const A = new Set(a.sel), S = new Set(v.sel), hit = [...S].filter(x => A.has(x)).length, wrong = S.size - hit;
    if (hit === A.size && wrong === 0) return { state: "ok", text: "정답" };
    return { state: hit ? "part" : "bad", text: `${hit}/${A.size} 맞음${wrong ? `, 잘못 고른 ${wrong}` : ""}` };
  }
  if (it.type === "sort") {
    const keys = Object.keys(a), hit = keys.filter(k => String(v[k]) === String(a[k])).length;
    return { state: hit === keys.length ? "ok" : hit ? "part" : "bad", text: `${hit}/${keys.length} 일치` };
  }
  return null;
}

/* ---------- 입력 위젯 ---------- */
function taInput(val, onChange, o) {
  o = o || {};
  const t = el("textarea", { rows: o.rows || 3, placeholder: o.placeholder || "", class: o.code ? "code" : "", spellcheck: o.code ? "false" : null });
  t.value = val || "";
  t.addEventListener("input", () => { autosize(t); onChange(t.value); });
  if (o.code) t.addEventListener("keydown", e => {
    if (e.key === "Tab") { e.preventDefault(); const s = t.selectionStart; t.setRangeText("    ", s, t.selectionEnd, "end"); onChange(t.value); }
  });
  requestAnimationFrame(() => autosize(t));
  setTimeout(() => autosize(t), 60);
  return t;
}

/* 안내문 속 예제 코드(<pre><code>)를 실행·편집 가능한 칸으로 바꾼다. 고친 내용은 저장하지 않는다. */
function enhanceCode(root) {
  $$("pre", root).forEach(pre => {
    const c = pre.querySelector("code"); if (!c) return;
    const code = c.textContent;
    pre.replaceWith(PyRun.mountEditor({ code, minRows: 3, label: "예제 코드 — 실행하거나 고쳐 볼 수 있어요" }).el);
  });
  return root;
}

function renderInput(it, val, set) {
  switch (it.type) {
    case "info": return enhanceCode(el("div", { html: it.html || "" }));
    case "text": return taInput(val, set, { rows: it.rows || 3, placeholder: it.hint });
    case "code": {
      const ed = PyRun.mountEditor({
        code: val == null ? (it.starter || "") : val, starter: it.starter || "", minRows: 8, label: "코드 작성",
        example: it.answer, exampleTitle: "예시 코드 (정답 예시)", onChange: set,
      });
      return ed.el;
    }
    case "choice": case "multi": {
      const multi = it.type === "multi", cur = val || { sel: multi ? [] : null, why: "" };
      const box = el("div", { class: "opts" });
      it.options.forEach((o, i) => {
        const inp = el("input", { type: multi ? "checkbox" : "radio", name: it.id });
        inp.checked = multi ? cur.sel.includes(i) : cur.sel === i;
        const lab = el("label", { class: "opt" + (inp.checked ? " sel" : "") }, inp, el("span", { html: o }));
        inp.addEventListener("change", () => {
          if (multi) cur.sel = $$("input", box).map((x, j) => x.checked ? j : -1).filter(j => j >= 0);
          else cur.sel = i;
          $$(".opt", box).forEach((l, j) => l.classList.toggle("sel", multi ? cur.sel.includes(j) : cur.sel === j));
          set({ sel: cur.sel, why: cur.why });
        });
        box.append(lab);
      });
      const out = el("div", {}, box);
      if (it.why !== false) {
        const w = taInput(cur.why, v => { cur.why = v; set({ sel: cur.sel, why: v }); }, { rows: 2, placeholder: it.whyHint || "그렇게 고른 이유를 적어 보세요." });
        out.append(el("div", { class: "why" }, el("label", {}, "이유·근거"), w));
      }
      return out;
    }
    case "table": {
      const cur = (val || []).map(r => r.slice());
      const R = it.rows.length, C = it.cols.length;
      for (let r = 0; r < R; r++) { cur[r] = cur[r] || []; for (let c = 0; c < C; c++) cur[r][c] = cur[r][c] || ""; }
      const thead = el("thead", {}, el("tr", {}, el("th", {}, it.corner || ""), it.cols.map(c => el("th", {}, c))));
      const tbody = el("tbody", {}, it.rows.map((rl, r) => el("tr", {}, el("th", { html: rl }),
        it.cols.map((_, c) => el("td", {}, taInput(cur[r][c], v => { cur[r][c] = v; set(cur.map(x => x.slice())); }, { rows: 2 }))))));
      return el("div", { class: "tbl-wrap" }, el("table", { class: "grid" }, thead, tbody));
    }
    case "sort": {
      const cur = Object.assign({}, val || {});
      return el("div", {}, it.cards.map((c, i) => {
        const s = el("select", {}, el("option", { value: "" }, "— 고르기 —"), it.buckets.map((b, j) => el("option", { value: j }, b)));
        s.value = cur[i] == null ? "" : String(cur[i]);
        s.addEventListener("change", () => { if (s.value === "") delete cur[i]; else cur[i] = Number(s.value); set(Object.assign({}, cur)); });
        return el("div", { class: "sortrow" }, el("div", { html: c }), s);
      }));
    }
    case "triples": {
      let rows = (val && val.length ? val : Array.from({ length: it.min || 3 }, () => ["", "", ""])).map(r => r.slice());
      const wrap = el("div"), dl = el("datalist", { id: "dl-" + it.id }, (it.relations || []).map(r => el("option", { value: r })));
      const emit = () => set(rows.map(r => r.slice()));
      const draw = () => {
        wrap.replaceChildren(dl, ...rows.map((r, i) => {
          const mk = (k, ph, list) => { const x = el("input", { type: "text", placeholder: ph, list: list ? "dl-" + it.id : null }); x.value = r[k]; x.addEventListener("input", () => { r[k] = x.value; emit(); }); return x; };
          return el("div", { class: "triple" }, mk(0, "개념 A"), mk(1, "관계(→)", true), mk(2, "개념 B"),
            el("button", { class: "xbtn", type: "button", title: "삭제", onclick: () => { rows.splice(i, 1); if (!rows.length) rows.push(["", "", ""]); emit(); draw(); } }, "×"));
        }), el("button", { class: "btn small addbtn", type: "button", onclick: () => { rows.push(["", "", ""]); draw(); } }, "+ 관계 추가"));
      };
      draw(); return wrap;
    }
    case "list": {
      let rows = (val && val.length ? val : Array(it.n || 3).fill("")).slice();
      const wrap = el("div"), emit = () => set(rows.slice());
      const draw = () => {
        wrap.replaceChildren(...rows.map((r, i) => {
          const x = el("input", { type: "text", placeholder: it.hint || "" }); x.value = r;
          x.addEventListener("input", () => { rows[i] = x.value; emit(); });
          return el("div", { class: "listrow" }, el("span", { class: "n" }, i + 1 + "."), x,
            el("button", { class: "xbtn", type: "button", title: "삭제", onclick: () => { rows.splice(i, 1); if (!rows.length) rows.push(""); emit(); draw(); } }, "×"));
        }), el("button", { class: "btn small addbtn", type: "button", onclick: () => { rows.push(""); draw(); const ins = $$("input", wrap); ins[ins.length - 1].focus(); } }, "+ 칸 추가"));
      };
      draw(); return wrap;
    }
    case "scales": {
      const cur = (val || []).slice(); while (cur.length < it.items.length) cur.push(null);
      const lo = (it.labels || ["전혀 아니다", "매우 그렇다"]);
      return el("div", {}, it.items.map((s, i) => el("div", { class: "scale-row" }, el("div", { html: s }),
        el("div", {}, el("div", { class: "scale-pts" }, [1, 2, 3, 4, 5].map(n => {
          const inp = el("input", { type: "radio", name: it.id + "-" + i, value: n }); inp.checked = cur[i] === n;
          inp.addEventListener("change", () => { cur[i] = n; set(cur.slice()); });
          return el("label", {}, inp, el("span", {}, n));
        })), el("div", { class: "scale-ends" }, el("span", {}, lo[0]), el("span", {}, lo[1]))))));
    }
  }
  return el("div", {}, "(지원하지 않는 문항 유형)");
}

/* ---------- 읽기 전용 표시 (교사용 화면·예시 정답) ---------- */
function renderValue(it, v, key) {
  const empty = () => el("div", { class: "val empty" }, "(미응답)");
  if (v == null || (it.type !== "scales" && !isAnswered(it, v) && it.type !== "code")) return empty();
  switch (it.type) {
    case "text": return el("div", { class: "val" }, v);
    case "code": return nonEmpty(v) ? PyRun.mountEditor({ code: v, resettable: false, label: "학생 코드(실행해 볼 수 있음)" }).el : empty();
    case "choice": case "multi": {
      const sel = it.type === "multi" ? v.sel : [v.sel], keys = key ? (it.type === "multi" ? key.sel : [key.sel]) : [];
      const box = el("div", {}, it.options.map((o, i) => el("div", { class: "ro-opt" + (sel.includes(i) ? " on" : "") + (key && keys.includes(i) && key === it.answer && v === it.answer ? " key" : "") }, el("span", { html: (sel.includes(i) ? "● " : "○ ") + o }))));
      if (v.why && nonEmpty(v.why)) box.append(el("div", { class: "val" }, el("b", {}, "이유: "), v.why));
      return box;
    }
    case "table": return el("div", { class: "tbl-wrap" }, el("table", { class: "ro" },
      el("thead", {}, el("tr", {}, el("th", {}, it.corner || ""), it.cols.map(c => el("th", {}, c)))),
      el("tbody", {}, it.rows.map((rl, r) => el("tr", {}, el("th", { html: rl }), it.cols.map((_, c) => el("td", {}, (v[r] && v[r][c]) || "")))))));
    case "sort": return el("table", { class: "ro" }, el("tbody", {}, it.cards.map((c, i) => el("tr", {}, el("td", { html: c }), el("td", {}, v[i] == null ? "—" : it.buckets[v[i]])))));
    case "triples": return el("div", {}, v.filter(r => r.some(nonEmpty)).map(r => el("div", { class: "val" }, `${r[0] || "?"}  —[${r[1] || "?"}]→  ${r[2] || "?"}`)));
    case "list": return el("ol", { class: "val" }, v.filter(nonEmpty).map(x => el("li", {}, x)));
    case "scales": return el("div", {}, it.items.map((s, i) => el("div", { class: "val" }, el("span", { html: s }), `  →  ${v[i] == null ? "—" : v[i] + "/5"}`)));
  }
  return empty();
}
function renderSample(it) {
  const a = it.answer;
  if (a == null) return null;
  if (it.type === "choice" || it.type === "multi") {
    const sel = it.type === "multi" ? a.sel : [a.sel];
    const box = el("div", {}, it.options.map((o, i) => el("div", { class: "ro-opt" + (sel.includes(i) ? " on key" : "") }, el("span", { html: (sel.includes(i) ? "● " : "○ ") + o }))));
    if (a.why) box.append(el("div", { class: "val" }, el("b", {}, "근거: "), a.why));
    return box;
  }
  return renderValue(Object.assign({}, it, { type: it.type }), a);
}

/* ---------- 파일 ---------- */
function newState() { return { app: APP, schema: SCHEMA, student: { name: "", number: "", klass: "" }, answers: {}, feedback: {}, saved: null }; }
function validState(d) { return d && d.app === APP && d.answers && typeof d.answers === "object"; }
function readJsonFile(file) {
  return new Promise((res, rej) => {
    const r = new FileReader();
    r.onload = () => { try { res(JSON.parse(r.result)); } catch (e) { rej(new Error(file.name + ": JSON 형식이 올바르지 않습니다.")); } };
    r.onerror = () => rej(new Error(file.name + ": 읽을 수 없습니다."));
    r.readAsText(file);
  });
}
function bindDrop(onFiles) {
  const dz = el("div", { class: "dropzone" }, "JSON 파일을 여기에 놓으세요"); document.body.append(dz);
  let n = 0;
  addEventListener("dragenter", e => { if (e.dataTransfer && [...e.dataTransfer.types].includes("Files")) { n++; dz.classList.add("on"); } });
  addEventListener("dragleave", () => { if (--n <= 0) { n = 0; dz.classList.remove("on"); } });
  addEventListener("dragover", e => e.preventDefault());
  addEventListener("drop", e => { e.preventDefault(); n = 0; dz.classList.remove("on"); if (e.dataTransfer.files.length) onFiles([...e.dataTransfer.files]); });
}
function initTheme() {
  const t = lsGet("dp-theme"); if (t) document.documentElement.dataset.theme = t;
  const b = $(".theme-toggle"); if (!b) return;
  b.addEventListener("click", () => {
    const r = document.documentElement, dark = r.dataset.theme ? r.dataset.theme === "dark" : matchMedia("(prefers-color-scheme: dark)").matches;
    r.dataset.theme = dark ? "light" : "dark"; lsSet("dp-theme", r.dataset.theme);
  });
}
const MARKS = { 3: ["◎", "우수"], 2: ["○", "적절"], 1: ["△", "보완 필요"] };
const STAGE_NO = { engage: 1, find: 2, sort: 3, general: 4, transfer: 5, reflect: 6 };
