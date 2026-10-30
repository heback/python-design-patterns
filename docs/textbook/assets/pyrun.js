"use strict";
/* 브라우저 안에서 파이썬을 실행·편집하는 공용 모듈 (교재 textbook/ 과 탐구 학습지 inquiry/ 가 함께 쓴다).
   - Pyodide(WebAssembly 파이썬)를 Web Worker 에서 돌린다. 무한 루프도 '중지'로 끊을 수 있다.
   - 처음 실행할 때 한 번만 내려받고(약 10MB) 이후에는 브라우저 캐시를 쓴다.
   공개 API: PyRun.run(code, onChunk) · PyRun.stop() · PyRun.makeRunner(getCode) · PyRun.mountEditor(opts) · PyRun.showExample(opts) */
const PyRun = (function () {
  const PYODIDE_BASE = "https://cdn.jsdelivr.net/pyodide/v0.26.4/full/";

  /* Pyodide 는 스레드를 만들 수 없다. 교재 예제의 threading 은 '순차 실행'으로 흉내 낸다(경쟁 상태는 재현되지 않음). */
  const SHIM = [
    "import threading as _t",
    "def _start(self):",
    "    self.run()",
    "_t.Thread.start = _start",
    "_t.Thread.join = lambda self, timeout=None: None",
    "_t.Barrier.wait = lambda self, timeout=None: 0",
  ].join("\n");

  function workerMain() {
    let py = null;
    self.onmessage = async function (e) {
      const m = e.data;
      try {
        if (m.type === "init") {
          importScripts(m.base + "pyodide.js");
          py = await loadPyodide({ indexURL: m.base });
          await py.runPythonAsync(m.shim);
          postMessage({ type: "ready" });
        } else if (m.type === "run") {
          py.setStdout({ batched: s => postMessage({ type: "out", id: m.id, text: s + "\n" }) });
          py.setStderr({ batched: s => postMessage({ type: "out", id: m.id, text: s + "\n", err: true }) });
          const g = py.globals.get("dict")();
          g.set("__name__", "__main__");
          try {
            await py.runPythonAsync(m.code, { globals: g });
            postMessage({ type: "done", id: m.id, ok: true });
          } catch (err) {
            let msg = String((err && err.message) || err);
            const i = msg.indexOf('File "<exec>"');
            if (i >= 0) msg = "Traceback (most recent call last):\n  " + msg.slice(i);
            if (/SystemExit/.test(msg)) postMessage({ type: "done", id: m.id, ok: true });
            else postMessage({ type: "done", id: m.id, ok: false, err: msg.trimEnd() });
          } finally { g.destroy(); }
        }
      } catch (err) {
        postMessage({ type: "fatal", message: String((err && err.message) || err) });
      }
    };
  }

  let worker = null, ready = null, cur = null, seq = 0, chain = Promise.resolve();

  function boot(onStatus) {
    if (ready) return ready;
    ready = new Promise((resolve, reject) => {
      const url = URL.createObjectURL(new Blob(["(" + workerMain.toString() + ")()"], { type: "text/javascript" }));
      worker = new Worker(url);
      worker.onmessage = e => {
        const m = e.data;
        if (m.type === "ready") resolve();
        else if (m.type === "fatal") { reject(new Error(m.message)); if (cur) finish({ ok: false, err: m.message }); }
        else if (cur && m.id === cur.id) {
          if (m.type === "out") cur.onChunk && cur.onChunk(m.text, !!m.err);
          else if (m.type === "done") finish({ ok: m.ok, err: m.err });
        }
      };
      worker.onerror = ev => { reject(new Error("파이썬 실행기를 시작하지 못했습니다. 인터넷 연결을 확인하세요.")); };
      worker.postMessage({ type: "init", base: PYODIDE_BASE, shim: SHIM });
    });
    ready.catch(() => { reset(); });
    return ready;
  }
  function reset() { if (worker) worker.terminate(); worker = null; ready = null; }
  function finish(res) { const c = cur; cur = null; if (c) c.resolve(res); }

  /* 코드를 실행한다. 한 번에 하나씩 차례로 실행한다. 반환: Promise<{ok, err?, stopped?}> */
  function run(code, onChunk, onStatus) {
    const job = chain.then(async () => {
      try {
        if (!ready) onStatus && onStatus("loading");
        await boot();
      } catch (e) { return { ok: false, err: e.message }; }
      onStatus && onStatus("running");
      return new Promise(resolve => {
        cur = { id: ++seq, resolve, onChunk };
        worker.postMessage({ type: "run", id: cur.id, code });
      });
    });
    chain = job.catch(() => {});
    return job;
  }
  /* 실행 중인 코드를 끊는다(실행기를 새로 만든다). 다음 실행 때 캐시에서 빠르게 다시 뜬다. */
  function stop() { if (cur) { const c = cur; reset(); cur = null; c.resolve({ ok: false, stopped: true }); } }

  /* ---------- UI ---------- */
  function h(tag, props, ...kids) {
    const e = document.createElement(tag);
    for (const [k, v] of Object.entries(props || {})) {
      if (v == null || v === false) continue;
      if (k === "class") e.className = v;
      else if (k.startsWith("on")) e.addEventListener(k.slice(2), v);
      else e.setAttribute(k, v === true ? "" : v);
    }
    for (const c of kids.flat()) if (c != null && c !== false) e.append(c.nodeType ? c : document.createTextNode(c));
    return e;
  }
  function copyText(text) {
    if (navigator.clipboard && window.isSecureContext) return navigator.clipboard.writeText(text);
    return new Promise((res, rej) => {
      const t = h("textarea", { style: "position:fixed;opacity:0" }); t.value = text; document.body.append(t); t.select();
      try { document.execCommand("copy") ? res() : rej(); } catch (e) { rej(e); } t.remove();
    });
  }
  function flash(btn, text) { const old = btn.dataset.label || btn.textContent; btn.dataset.label = old; btn.textContent = text; clearTimeout(btn._t); btn._t = setTimeout(() => { btn.textContent = old; }, 1300); }
  function fit(t) { t.style.height = "auto"; t.style.height = Math.min(t.scrollHeight + 2, 560) + "px"; }

  const NOTES = [
    [/\bthreading\b/, "ℹ️ 브라우저에서는 스레드를 만들 수 없어, 스레드를 차례대로 실행하는 방식으로 대신합니다. (경쟁 상태는 재현되지 않습니다)"],
    [/\bsubprocess\b/, "ℹ️ 브라우저에서는 다른 프로그램(subprocess)을 실행할 수 없어 오류가 날 수 있습니다."],
  ];

  /* 실행 버튼·중지 버튼·상태 표시·출력 칸 한 벌. 편집기(mountEditor)와 읽기 전용 코드 블록(교재의 예제 코드)이 함께 쓴다.
     getCode() 가 돌려주는 코드를 실행하고, 결과는 outBox 에 쌓는다. outBox 는 호출한 쪽이 원하는 자리에 붙인다. */
  function makeRunner(getCode) {
    const status = h("span", { class: "pr-status" });
    const bRun = h("button", { class: "pr-btn run", type: "button", title: "실행 (Ctrl/⌘ + Enter)" }, "▶ 실행");
    const bStop = h("button", { class: "pr-btn stop", type: "button", hidden: true }, "■ 중지");
    const outPre = h("pre", { class: "pr-pre" });
    const outBox = h("div", { class: "pr-out", hidden: true }, h("div", { class: "pr-outhead" }, h("span", {}, "출력"),
      h("button", { class: "pr-btn small", type: "button", onclick: () => { outBox.hidden = true; outPre.textContent = ""; } }, "지우기")), outPre);
    let busy = false;
    function setBusy(b) { busy = b; bRun.disabled = b; bStop.hidden = !b; }
    function go() {
      if (busy) return;
      const code = getCode(); outPre.textContent = ""; outBox.hidden = false;
      const note = NOTES.filter(([re]) => re.test(code)).map(n => n[1]);
      if (note.length) outPre.append(h("span", { class: "pr-note" }, note.join("\n") + "\n"));
      setBusy(true);
      const t0 = performance.now();
      PyRun.run(code, (text, isErr) => { outPre.append(isErr ? h("span", { class: "pr-err" }, text) : document.createTextNode(text)); },
        st => { status.textContent = st === "loading" ? "파이썬을 불러오는 중… (처음 한 번, 몇 초 걸려요)" : "실행 중…"; })
        .then(res => {
          setBusy(false);
          if (res.stopped) { outPre.append(h("span", { class: "pr-err" }, "■ 사용자가 중지했습니다.\n")); status.textContent = ""; return; }
          if (!res.ok) outPre.append(h("span", { class: "pr-err" }, res.err + "\n"));
          else if (!outPre.textContent.replace(/^ℹ️.*\n/, "").trim()) outPre.append(h("span", { class: "pr-dim" }, "(출력 없음 — print() 로 결과를 찍어 보세요)\n"));
          status.textContent = (res.ok ? "✔ 끝남 " : "✖ 오류 ") + Math.round(performance.now() - t0) + "ms";
        });
    }
    bRun.addEventListener("click", go);
    bStop.addEventListener("click", () => PyRun.stop());
    return { bRun, bStop, status, outBox, go };
  }

  /* 편집 가능한 코드 칸 + 실행 + 출력 (+ 예시 코드 버튼).
     opts: {code, starter, example, exampleTitle, onChange, minRows, label, resettable} */
  function mountEditor(opts) {
    const starter = opts.starter == null ? opts.code || "" : opts.starter;
    const ta = h("textarea", { class: "pr-ta", spellcheck: "false", autocapitalize: "off", autocomplete: "off", "aria-label": opts.label || "파이썬 코드 편집기", rows: opts.minRows || 6 });
    ta.value = opts.code == null ? starter : opts.code;
    const { bRun, bStop, status, outBox, go } = makeRunner(() => ta.value);
    const bReset = h("button", { class: "pr-btn", type: "button", title: "처음 코드로 되돌리기" }, "↺ 처음 코드");
    const bCopy = h("button", { class: "pr-btn", type: "button", title: "내 코드 복사" }, "복사");
    const bEx = opts.example ? h("button", { class: "pr-btn ex", type: "button", title: "정답 예시 코드를 팝업으로 보기" }, "💡 예시 코드") : null;
    /* 문법 강조: 글자를 투명하게 만든 textarea 뒤에 같은 글꼴의 색칠된 <pre> 를 깔고 스크롤을 맞춘다. */
    const hlCode = h("code", {}), hl = h("pre", { class: "pr-hl", "aria-hidden": "true" }, hlCode);
    const stack = h("div", { class: "pr-stack" }, hl, ta);
    /* 행 번호: 편집기 왼쪽 칸. 줄마다 점선 구분선은 CSS(.pr-hl code / .pr-gutter code 의 ::before)가 그린다. */
    const gNum = h("code", {}), gutter = h("div", { class: "pr-gutter", "aria-hidden": "true" }, h("pre", { class: "pr-gutter-pre" }, gNum));
    let nLines = 0;
    const paint = () => {
      hlCode.innerHTML = (typeof PyHL !== "undefined" ? PyHL.html(ta.value) : ta.value.replace(/&/g, "&amp;").replace(/</g, "&lt;")) + "\n";
      const n = ta.value.split("\n").length;
      if (n !== nLines) {
        nLines = n; gNum.textContent = Array.from({ length: n }, (_, i) => i + 1).join("\n");
        gutter.style.width = "calc(" + Math.max(2, String(n).length) + "ch + 24px)";
      }
      syncScroll();
    };
    const syncScroll = () => { hl.scrollTop = ta.scrollTop; hl.scrollLeft = ta.scrollLeft; gutter.firstChild.scrollTop = ta.scrollTop; };
    ta.addEventListener("scroll", syncScroll);
    const root = h("div", { class: "pr" }, h("div", { class: "pr-bar" }, bRun, bStop, opts.resettable === false ? null : bReset, bCopy, bEx, status), h("div", { class: "pr-edit" }, gutter, stack), outBox);

    ta.addEventListener("input", () => { fit(ta); paint(); opts.onChange && opts.onChange(ta.value); });
    /* [a, b) 를 text 로 바꾼다. execCommand 를 쓰면 브라우저의 실행 취소(Ctrl+Z)가 유지된다. 막혀 있으면 setRangeText 로 대신한다. */
    function replaceRange(a, b, text) {
      ta.focus(); ta.setSelectionRange(a, b);
      if (!document.execCommand("insertText", false, text)) { ta.setRangeText(text, a, b, "end"); ta.dispatchEvent(new Event("input")); }
    }
    /* 선택에 걸친 모든 줄을 들여쓰기(Tab)/내어쓰기(Shift+Tab). 선택 영역은 유지한다. */
    function shiftLines(outdent) {
      const v = ta.value, s = ta.selectionStart, en = ta.selectionEnd, a = v.lastIndexOf("\n", s - 1) + 1;
      const last = en > s && v[en - 1] === "\n" ? en - 1 : en;       // 선택이 다음 줄 맨 앞에서 끝나면 그 줄은 제외
      let b = v.indexOf("\n", last); if (b < 0) b = v.length;
      let first = 0, total = 0;
      const out = v.slice(a, b).split("\n").map((ln, i) => {
        let d = 0;
        if (outdent) { const m = /^( {1,4}|\t)/.exec(ln); if (m) { d = -m[0].length; ln = ln.slice(m[0].length); } }
        else if (ln) { ln = "    " + ln; d = 4; }                      // 빈 줄은 건드리지 않는다
        if (i === 0) first = d; total += d; return ln;
      });
      replaceRange(a, b, out.join("\n"));
      const ns = Math.max(a, s + first); ta.setSelectionRange(ns, Math.max(ns, en + total));
    }
    let tabFree = false;                       // Esc 를 누르면 다음 Tab 은 들여쓰기 대신 포커스를 옮긴다(키보드 사용자 탈출구)
    ta.addEventListener("blur", () => { tabFree = false; });
    ta.addEventListener("keydown", e => {
      if (e.key === "Escape") { tabFree = true; return; }
      if (e.key === "Tab" && !e.ctrlKey && !e.metaKey && !e.altKey) {
        if (tabFree) { tabFree = false; return; }
        e.preventDefault();
        const s = ta.selectionStart, en = ta.selectionEnd, multi = ta.value.slice(s, en).includes("\n");
        if (e.shiftKey || multi) shiftLines(e.shiftKey);
        else replaceRange(s, en, "    ");
      } else if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) { e.preventDefault(); go(); }
      else if (e.key === "Enter" && !e.shiftKey && !e.altKey) {   // 자동 들여쓰기
        const s = ta.selectionStart, line = ta.value.slice(ta.value.lastIndexOf("\n", s - 1) + 1, s);
        let ind = (/^ */.exec(line) || [""])[0]; if (/:\s*$/.test(line)) ind += "    ";
        if (ind) { e.preventDefault(); replaceRange(s, ta.selectionEnd, "\n" + ind); }
      }
    });

    bReset.addEventListener("click", () => {
      if (ta.value !== starter && ta.value.trim() && !confirm("내가 고친 코드가 처음 코드로 바뀝니다. 계속할까요?")) return;
      ta.value = starter; fit(ta); paint(); opts.onChange && opts.onChange(ta.value);
    });
    bCopy.addEventListener("click", () => copyText(ta.value).then(() => flash(bCopy, "복사됨"), () => flash(bCopy, "복사 실패")));
    if (bEx) bEx.addEventListener("click", () => showExample({ title: opts.exampleTitle, code: opts.example, opener: bEx }));
    paint(); requestAnimationFrame(() => fit(ta)); setTimeout(() => fit(ta), 80);
    return {
      el: root, textarea: ta, getValue: () => ta.value,
      setValue(v) { ta.value = v; fit(ta); paint(); }, refit: () => fit(ta),
    };
  }

  /* 정답 예시 코드 팝업. 코드는 드래그해서 복사하거나 '복사' 버튼으로 복사한다. 닫기 버튼·Esc·바깥 클릭으로 닫힌다. */
  let modal = null;
  function showExample(o) {
    closeExample();
    const prev = o.opener || document.activeElement;
    const pre = h("pre", { class: "pr-modal-code", tabindex: "0" }, h("code", { class: "language-python" }, o.code));
    if (typeof PyHL !== "undefined") PyHL.apply(pre);
    const bCopy = h("button", { class: "pr-btn", type: "button" }, "📋 복사");
    const bClose = h("button", { class: "pr-btn primary", type: "button" }, "닫기");
    const title = h("h3", { id: "pr-modal-title" }, o.title || "예시 코드");
    const panel = h("div", { class: "pr-modal-panel", role: "dialog", "aria-modal": "true", "aria-labelledby": "pr-modal-title" },
      h("div", { class: "pr-modal-head" }, title, h("span", { class: "pr-grow" }), bCopy, bClose),
      h("p", { class: "pr-modal-note" }, "하나의 예시일 뿐, 이것만 정답은 아닙니다. 먼저 직접 풀어 본 뒤 비교해 보세요."), pre);
    const back = h("div", { class: "pr-modal" }, panel);
    const close = () => closeExample(prev);
    back.addEventListener("mousedown", e => { if (e.target === back) close(); });
    bClose.addEventListener("click", close);
    bCopy.addEventListener("click", () => copyText(o.code).then(() => flash(bCopy, "✔ 복사됨"), () => flash(bCopy, "복사 실패 — 직접 선택해 복사하세요")));
    const onKey = e => {
      if (e.key === "Escape") { e.preventDefault(); close(); }
      else if (e.key === "Tab") {             // 팝업 안에서만 포커스 이동
        const f = [bCopy, bClose, pre]; const i = f.indexOf(document.activeElement);
        e.preventDefault(); f[(i + (e.shiftKey ? f.length - 1 : 1)) % f.length].focus();
      }
    };
    document.addEventListener("keydown", onKey, true);
    document.body.append(back); document.body.classList.add("pr-lock");
    modal = { back, onKey };
    bClose.focus();
  }
  function closeExample(restore) {
    if (!modal) return;
    document.removeEventListener("keydown", modal.onKey, true);
    modal.back.remove(); modal = null; document.body.classList.remove("pr-lock");
    if (restore && restore.focus) try { restore.focus(); } catch (e) {}
  }

  return { run, stop, makeRunner, mountEditor, showExample, closeExample, copyText };
})();
