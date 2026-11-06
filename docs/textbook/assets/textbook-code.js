"use strict";
/* 교재 쪽 연결: 본문의 모든 예제 코드(figure.code)와 연습문제의 시작 코드를 코드 편집기로 보여 준다.
   - 학생은 코드에 주석(# 메모)을 달거나 고쳐 볼 수 있고([# 주석] 버튼, Ctrl/⌘+/), 고친 내용은 입력하는 대로 자동 저장된다(이 브라우저의 localStorage).
     다음에 열면 저장한 코드가 그대로 나오고, [처음 코드]로 되돌리면 저장도 지워진다. 장의 코드가 나중에 바뀌면(원본이 달라지면) 옛 저장본은 쓰지 않는다.
     호스팅된 교재 사본에서는 로그인·동의한 학생의 편집이 서버(codeNotes)에도 저장되어 다른 기기에서도 이어지고 교사가 볼 수 있다. GitHub Pages 사본은 이 브라우저에만 저장된다.
   - 편집기의 [📌 오른쪽 고정]을 누르면 그 편집기가 화면 오른쪽 고정 창으로 올라가 본문을 읽으면서 코드를 함께 볼 수 있다. 하나만 고정되고, 다른 편집기를 고정하면 앞의 것은 제자리로 돌아간다.
   - 연습문제 해설 안의 코드(details.solution)는 고칠 필요가 없으므로 이전처럼 읽기 전용 + [▶ 실행]이다. */
(function () {
  const $$ = (s, r) => Array.from((r || document).querySelectorAll(s));
  const mk = (tag, cls, ...kids) => { const e = document.createElement(tag); if (cls) e.className = cls; kids.flat().forEach(k => { if (k != null) e.append(k.nodeType ? k : document.createTextNode(k)); }); return e; };

  /* ---------- 자동 저장(localStorage) ---------- */
  const PAGE = (location.pathname.split("/").pop() || "index").replace(/\.html$/, "");
  const hash = t => { let h = 5381; for (let i = 0; i < t.length; i++) h = ((h << 5) + h + t.charCodeAt(i)) | 0; return (h >>> 0).toString(36); };
  const store = {
    get(key, h) { try { const j = JSON.parse(localStorage.getItem(key)); return j && j.h === h && typeof j.v === "string" ? j : null; } catch (e) { return null; } },
    set(key, h, v) { try { localStorage.setItem(key, JSON.stringify({ h, v, t: Date.now() })); return true; } catch (e) { return false; } },
    del(key) { try { localStorage.removeItem(key); } catch (e) {} },
  };
  const hhmm = () => { const d = new Date(), p = n => String(n).padStart(2, "0"); return p(d.getHours()) + ":" + p(d.getMinutes()); };
  const flushers = [];
  addEventListener("pagehide", () => flushers.forEach(f => f()));
  document.addEventListener("visibilitychange", () => { if (document.hidden) flushers.forEach(f => f()); });

  /* ---------- 서버 저장(호스팅된 교재 사본에서만) ----------
     학교 계정으로 로그인하고 동의한 학생의 편집 내용은 서버에도 저장된다(inquiry/templates/code-sync.js 가 DPCode.attach 로 저장 방법을 넘겨준다).
     GitHub Pages 사본에는 그 스크립트가 없으므로 이 브라우저(localStorage)에만 저장된다. sync = {active(), load(), save(bid, rec), remove(bid)}. */
  const DPCode = window.DPCode = { entries: [], sync: null };
  const addedLines = (code, original) => {
    const cnt = new Map(); original.split("\n").forEach(l => { const k = l.trim(); cnt.set(k, (cnt.get(k) || 0) + 1); });
    const out = []; code.split("\n").forEach(l => { const k = l.trim(); if (!k) return; const c = cnt.get(k) || 0; if (c > 0) cnt.set(k, c - 1); else out.push(l); });
    return out;
  };
  const stamp = () => "자동 저장됨 " + hhmm();

  /* 편집기 하나를 저장소와 잇는다. kind = "code"|"exercise", idx = 쪽 안의 번호, original = 원본 코드. 저장된 것이 있으면 initial 로 돌려준다. */
  function saved(kind, idx, original) {
    const key = (kind === "code" ? "dp-code:" : "dp-ex:") + PAGE + ":" + idx, h = hash(original), j = store.get(key, h);
    return { key, h, t: j ? j.t || 0 : 0, initial: j && j.v !== original ? j.v : original, restored: !!(j && j.v !== original) };
  }
  function autosave(ed, sv, original, bar, meta) {
    const note = mk("span", "pr-saved"); bar.append(note);
    const en = { bid: PAGE + "__" + (meta.kind === "code" ? "c" : "e") + meta.idx, ed, sv, original, note, kind: meta.kind, idx: meta.idx, title: meta.title, chain: Promise.resolve() };
    DPCode.entries.push(en);
    const rec = v => { const add = addedLines(v, original); return { page: PAGE, kind: en.kind, idx: en.idx, title: en.title, h: sv.h, code: v, added: add.join("\n").slice(0, 6000), addedN: add.length }; };
    const idleNote = () => { note.textContent = DPCode.sync ? (DPCode.sync.active() ? "고치면 자동 저장돼요 (서버에도)" : "로그인하면 서버에도 저장돼요") : "고치면 자동 저장돼요"; };
    /* 서버로 보낸다(같은 편집기의 저장은 차례대로). 원본 그대로면 서버 기록을 지운다. */
    en.push = () => {
      const sy = DPCode.sync; if (!sy || !sy.active()) return Promise.resolve();
      const v = ed.getValue();
      en.chain = en.chain.then(() => v === original ? sy.remove(en.bid) : (v.length > 30000 ? Promise.reject(new Error("too long")) : sy.save(en.bid, rec(v))))
        .then(() => { if (ed.getValue() === v) note.textContent = (v === original ? "처음 코드 그대로" : stamp()) + " · 서버에도 저장됨"; })
        .catch(() => { note.textContent = (v === original ? "처음 코드 그대로" : stamp()) + " · 서버에는 저장하지 못했어요(다시 고치면 재시도)"; });
      return en.chain;
    };
    let timer = null, dirty = false;
    const write = () => {
      clearTimeout(timer); timer = null; if (!dirty) return; dirty = false;
      const v = ed.getValue();
      if (v === original) { store.del(sv.key); sv.t = 0; note.textContent = "처음 코드 그대로"; }
      else { sv.t = Date.now(); note.textContent = store.set(sv.key, sv.h, v) ? stamp() : "저장하지 못했어요(브라우저 저장소가 막혀 있어요)"; }
      en.push();
    };
    flushers.push(write);
    if (sv.restored) note.textContent = "이전에 고친 코드를 불러왔어요"; else idleNote();
    en.idle = idleNote;
    return () => { dirty = true; note.textContent = "저장 중…"; clearTimeout(timer); timer = setTimeout(write, 500); };
  }

  /* 로그인·동의가 끝나면(또는 사본이 열릴 때) 서버의 내 코드와 이 브라우저의 것을 맞춘다: 더 나중에 고친 쪽이 이긴다. 서버에 없는 로컬 편집은 올린다. */
  let pulling = false, again = false;
  DPCode.pull = async function () {
    const sy = DPCode.sync; if (!sy) return; if (pulling) { again = true; return; } pulling = true;
    try {
      const map = sy.active() ? await sy.load() : null;
      DPCode.entries.forEach(en => en.idle());
      if (!map) return;
      DPCode.entries.forEach(en => {
        const srv = map[en.bid], v = en.ed.getValue(), edited = v !== en.original;
        const srvOk = srv && srv.h === en.sv.h && typeof srv.code === "string", srvT = srvOk && srv.updatedAt && srv.updatedAt.toMillis ? srv.updatedAt.toMillis() : 0;
        if (srvOk && srv.code !== v && (!edited || srvT > en.sv.t)) {
          en.ed.setValue(srv.code); en.sv.t = srvT; store.set(en.sv.key, en.sv.h, srv.code); en.note.textContent = "서버에 저장된 코드를 불러왔어요";
        } else if (edited && !(srvOk && srv.code === v)) en.push();
        else if (srvOk && srv.code === v) en.note.textContent = "서버에도 저장돼 있어요";
      });
    } catch (e) { DPCode.entries.forEach(en => { en.note.textContent = "서버 저장본을 불러오지 못했어요(이 브라우저의 저장본을 씁니다)"; }); }
    finally { pulling = false; if (again) { again = false; DPCode.pull(); } }
  };
  DPCode.attach = function (sync) { DPCode.sync = sync; DPCode.pull(); };

  /* ---------- 오른쪽 고정 창 ---------- */
  const Pin = (() => {
    let panel = null, body = null, titleEl = null, cur = null;
    const WKEY = "dp-pin-w";
    const clampW = w => Math.max(320, Math.min(w, Math.min(900, innerWidth - 320)));
    const setW = w => document.documentElement.style.setProperty("--pin-w", clampW(w) + "px");
    function build() {
      if (panel) return;
      const bBack = mk("button", "pr-btn primary", "↩ 제자리로");
      bBack.type = "button"; bBack.addEventListener("click", () => unpin());
      titleEl = mk("b", "pin-title");
      const grip = mk("div", "pin-grip"); grip.setAttribute("aria-hidden", "true"); grip.title = "끌어서 너비 바꾸기";
      body = mk("div", "pin-body");
      panel = mk("aside", "code-pin", grip, mk("div", "pin-head", titleEl, mk("span", "pr-grow"), bBack), body);
      panel.hidden = true; panel.setAttribute("aria-label", "고정한 코드 편집기"); panel.setAttribute("role", "complementary");
      document.body.append(panel);
      let w0 = 0; try { w0 = Number(localStorage.getItem(WKEY)) || 0; } catch (e) {}
      setW(w0 || Math.max(380, Math.min(640, innerWidth * 0.4)));
      grip.addEventListener("pointerdown", e => {
        e.preventDefault(); grip.setPointerCapture(e.pointerId); document.body.classList.add("pin-drag");
        const move = ev => { setW(innerWidth - ev.clientX); };
        const up = () => { grip.removeEventListener("pointermove", move); grip.removeEventListener("pointerup", up); grip.removeEventListener("pointercancel", up); document.body.classList.remove("pin-drag");
          try { localStorage.setItem(WKEY, String(parseInt(getComputedStyle(document.documentElement).getPropertyValue("--pin-w")) || 0)); } catch (er) {} if (cur) cur.ed.refit(); };
        grip.addEventListener("pointermove", move); grip.addEventListener("pointerup", up); grip.addEventListener("pointercancel", up);
      });
      addEventListener("resize", () => { if (cur) { place(); cur.ed.refit(); } });
    }
    const place = () => { const tb = document.querySelector(".topbar"); document.documentElement.style.setProperty("--pin-top", (tb ? tb.getBoundingClientRect().bottom : 0) + "px"); };
    function unpin() {
      if (!cur) return;
      const c = cur; cur = null;
      c.holder.replaceWith(c.ed.el); c.ed.textarea.dataset.maxh = c.maxh; c.btn.textContent = "📌 오른쪽 고정"; c.btn.title = "이 편집기를 화면 오른쪽에 고정해 본문을 읽으면서 함께 봅니다";
      panel.hidden = true; document.body.classList.remove("code-pinned");
      requestAnimationFrame(() => c.ed.refit());
    }
    function pin(ed, title, btn) {
      build(); if (cur) unpin();
      const maxh = ed.textarea.dataset.maxh || "";
      const holder = mk("div", "pin-holder", "이 코드는 화면 오른쪽 창에 고정되어 있어요. ");
      const back = mk("button", "pr-btn", "↩ 제자리로"); back.type = "button"; back.addEventListener("click", () => unpin()); holder.append(back);
      ed.el.replaceWith(holder); body.replaceChildren(ed.el);
      ed.textarea.dataset.maxh = "4000"; titleEl.textContent = title || "코드";
      cur = { ed, holder, maxh, btn }; btn.textContent = "↩ 제자리로"; btn.title = "고정을 풀어 본문의 원래 자리로 되돌립니다";
      place(); panel.hidden = false; document.body.classList.add("code-pinned");
      requestAnimationFrame(() => { ed.refit(); ed.textarea.focus({ preventScroll: true }); });
    }
    const isPinned = ed => !!(cur && cur.ed === ed);
    return { pin, unpin, isPinned };
  })();

  /* 편집기 막대에 [📌 오른쪽 고정] 버튼을 단다. */
  function addPin(ed, title) {
    const bar = ed.el.querySelector(".pr-bar"), btn = mk("button", "pr-btn", "📌 오른쪽 고정");
    btn.type = "button"; btn.title = "이 편집기를 화면 오른쪽에 고정해 본문을 읽으면서 함께 봅니다";
    btn.addEventListener("click", () => { if (Pin.isPinned(ed)) Pin.unpin(); else Pin.pin(ed, title, btn); });
    bar.insertBefore(btn, bar.querySelector(".pr-status"));
    return bar;
  }

  /* ---------- 1) 본문 예제 코드: 편집기 ---------- */
  let figNo = 0;
  $$("figure.code").forEach(fig => {
    const codeEl = fig.querySelector("code.language-python"), cap = fig.querySelector("figcaption");
    if (fig.closest("details.solution")) {
      /* 해설 안의 코드: 읽기 전용 + [▶ 실행] (행 번호 칸만 붙인다) */
      const pre = fig.querySelector("pre"), n = codeEl.textContent.split("\n").length;
      const gNum = mk("code", "", Array.from({ length: n }, (_, i) => i + 1).join("\n"));
      const gutter = mk("div", "pr-gutter", mk("pre", "pr-gutter-pre", gNum)); gutter.setAttribute("aria-hidden", "true");
      gutter.style.width = "calc(" + Math.max(2, String(n).length) + "ch + 24px)";
      const wrap = mk("div", "pr-edit pr-static"); pre.replaceWith(wrap); wrap.append(gutter, pre);
      const code = fig.dataset.full || codeEl.textContent, rn = PyRun.makeRunner(() => code), cp = cap.querySelector(".copy");
      rn.bRun.title = fig.dataset.full ? "이 장면은 파일의 일부입니다. 파일 전체를 실행합니다." : "이 코드를 실행합니다.";
      cap.insertBefore(rn.bRun, cp); cap.insertBefore(rn.bStop, cp); cap.insertBefore(rn.status, cp); fig.append(rn.outBox);
      return;
    }
    const idx = figNo++, original = codeEl.textContent, title = cap.firstChild ? cap.firstChild.textContent : "코드";
    const sv = saved("code", idx, original);
    /* 일부 줄만 보이는 코드(data-from~data-to행)는 고친 내용을 파일 전체의 같은 자리에 끼워 넣어 실행한다. */
    const a = Number(fig.dataset.from), b = Number(fig.dataset.to), full = fig.dataset.full;
    const runCode = full && a && b ? v => { const ls = full.split("\n"); return ls.slice(0, a - 1).concat(v.split("\n"), ls.slice(b)).join("\n"); } : full ? () => full : null;
    let onChange = () => {};
    const ed = PyRun.mountEditor({ code: sv.initial, starter: original, label: title + " 코드 편집기", runCode, onChange: v => onChange(v) });
    ed.textarea.dataset.maxh = "2400";                      // 본문 코드는 안쪽 스크롤 없이 다 보이게 한다
    fig.querySelector("pre").replaceWith(ed.el);
    const cp = cap.querySelector(".copy"); if (cp) cp.remove();      // 편집기에 [복사]가 있다
    const bar = addPin(ed, title);
    onChange = autosave(ed, sv, original, bar, { kind: "code", idx, title });
    requestAnimationFrame(() => ed.refit());
  });

  /* ---------- 2) 연습문제의 시작 코드: 편집기. 해설의 코드가 '예시 코드' 팝업이 된다. ---------- */
  $$(".exercise").forEach((ex, exNo) => {
    const sol = ex.querySelector("details.solution");
    const solFig = sol && sol.querySelector("figure.code");
    const solCode = solFig ? (solFig.dataset.full || solFig.querySelector("code.language-python").textContent)
      : (sol && sol.querySelector("pre code") ? sol.querySelector("pre code").textContent : null);
    const title = (ex.querySelector("h3") || {}).textContent || "연습문제";
    $$("pre", ex).filter(p => !p.closest("details") && !p.closest("figure") && p.querySelector("code.language-python")).forEach((pre, k) => {
      const code = pre.textContent.replace(/\n$/, "");
      const exIdx = exNo * 10 + k, sv = saved("exercise", exIdx, code), exTitle = title.replace(/^\S+\s*/, "").trim() || "연습문제";
      let onChange = () => {};
      const ed = PyRun.mountEditor({ code: sv.initial, starter: code, example: solCode, exampleTitle: "예시 코드 — " + title.replace(/^\S+\s*/, "").trim(), label: "연습문제 코드", onChange: v => onChange(v) });
      pre.replaceWith(ed.el);
      ed.el.classList.add("pr-exercise");
      const bar = addPin(ed, exTitle);
      onChange = autosave(ed, sv, code, bar, { kind: "exercise", idx: exIdx, title: exTitle });
    });
  });
})();

/* 요약 판 ↔ 원문 전환 버튼: 누르면 지금 읽던 절(두 판이 같은 절 id를 쓴다)의 위치로 바로 이동한다. 같은 id가 없으면 맨 위로 간다. */
(function () {
  const tabs = document.querySelectorAll(".ver-switch");
  if (!tabs.length) return;
  tabs.forEach(a => a.addEventListener("click", e => {
    if (e.metaKey || e.ctrlKey || e.shiftKey || e.button) return;
    let cur = null;
    document.querySelectorAll("main.content section[id]").forEach(s => { if (s.getBoundingClientRect().top <= 140) cur = s; });
    if (cur) { e.preventDefault(); location.href = a.getAttribute("href") + "#" + cur.id; }
  }));
})();
