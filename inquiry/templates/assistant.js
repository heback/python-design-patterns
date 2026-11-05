"use strict";
/* 학생 AI 도우미(학습지·호스팅 교재 공용). 오른쪽 아래 아이콘을 누르면 대화창이 열린다.
   질문은 글 또는 사진, 답은 글. 학생이 지금 보고 있는 화면(교재의 절·학습지의 문항)과 드래그해 고른 글을 함께 보낸다.
   교사가 켜 둔 동안(config/assistant.on)에만 아이콘이 보이고, 학교 Google 계정으로 로그인해야 쓸 수 있다.
   질문과 답은 서버에 기록되어 선생님이 볼 수 있고, 학생은 기록을 지울 수 없다. 화면의 대화창은 [새 대화]로 비울 수 있지만 서버 기록은 그대로다.
   질문은 학생별·장별로 횟수가 정해져 있다(기본 40번, 선생님이 학생별로 가감). 호스트가 getContext 의 chapter(교재 장 slug 또는 week1~5)를 주면 그 장의 남은 횟수를 보여 준다.
   필요한 전역: el, ico, $, FB(fb.js), StudentAuth(student-auth.js). 호스트가 getContext() => {kind, title, text, selection} 를 준다. */
const Assistant = (() => {
  const MAX_SIDE = 1280, QUALITY = 0.82, MAX_BYTES = 1_300_000;
  let enabled = false, getContext = () => ({}), fab = null, panel = null, log = null, input = null, send = null, attach = null, preview = null, ctxChip = null, leftEl = null;
  let image = null, busy = false, history = [], started = false, quotaFor = null;

  /* ---------- 사진: 크기를 줄여 JPEG 으로(전송량·비용 절약) ---------- */
  async function shrink(file) {
    if (!/^image\/(jpeg|png|webp)$/.test(file.type)) throw new Error("JPG·PNG·WebP 사진만 보낼 수 있어요.");
    const bmp = await createImageBitmap(file), k = Math.min(1, MAX_SIDE / Math.max(bmp.width, bmp.height));
    const c = document.createElement("canvas"); c.width = Math.round(bmp.width * k); c.height = Math.round(bmp.height * k);
    const g = c.getContext("2d"); g.fillStyle = "#fff"; g.fillRect(0, 0, c.width, c.height); g.drawImage(bmp, 0, 0, c.width, c.height);
    let q = QUALITY, url = c.toDataURL("image/jpeg", q);
    while (url.length * 3 / 4 > MAX_BYTES && q > 0.4) { q -= 0.15; url = c.toDataURL("image/jpeg", q); }
    if (url.length * 3 / 4 > MAX_BYTES) throw new Error("사진이 너무 커요. 더 작은 사진을 보내 주세요.");
    return { mime: "image/jpeg", data: url.split(",")[1], url };
  }
  function setImage(im) {
    image = im; preview.replaceChildren();
    if (im) preview.append(el("img", { src: im.url, alt: "첨부한 사진" }), el("button", { type: "button", class: "ai-x", "aria-label": "사진 빼기", onclick: () => setImage(null) }, ico("close")));
    preview.hidden = !im;
  }
  async function pick(file) {
    if (!file) return;
    try { setImage(await shrink(file)); input.focus(); } catch (e) { addMsg("err", e.message || "사진을 불러오지 못했어요."); }
  }
  /* 붙여넣기·끌어다 놓기로 들어온 데이터에서 이미지 파일을 찾는다(스크린샷은 files 가 아니라 items 로만 오는 브라우저가 있다) */
  function imageFrom(dt) {
    if (!dt) return null;
    const f = [...(dt.files || [])].find(x => /^image\//.test(x.type)); if (f) return f;
    const it = [...(dt.items || [])].find(x => x.kind === "file" && /^image\//.test(x.type)); return it ? it.getAsFile() : null;
  }
  /* [붙여넣기] 버튼: 클립보드에 있는 이미지를 읽는다(브라우저가 허용할 때). 막히면 Ctrl/⌘+V 로 붙여넣는 방법을 알려 준다. */
  async function pasteFromClipboard() {
    try {
      const items = await navigator.clipboard.read();
      for (const it of items) { const t = it.types.find(x => /^image\//.test(x)); if (t) { await pick(new File([await it.getType(t)], "clipboard", { type: t })); return; } }
      addMsg("err", "클립보드에 이미지가 없어요. 이미지를 먼저 복사해 주세요(화면 캡처: Windows Win+Shift+S, Mac Cmd+Shift+Ctrl+4).");
    } catch (e) { addMsg("err", "브라우저가 클립보드 읽기를 막았어요. 이미지를 복사한 뒤 입력란을 누르고 Ctrl+V(Mac은 Cmd+V)로 붙여넣어 보세요."); }
  }

  /* ---------- 대화 ---------- */
  function addMsg(who, text, img) {
    const m = el("div", { class: "ai-msg " + who });
    if (img) m.append(el("img", { src: img, alt: "보낸 사진" }));
    if (text) m.append(el("div", { class: "ai-txt" }, text));           // textContent 로만 넣는다(HTML 해석 없음)
    log.append(m); log.scrollTop = log.scrollHeight; return m;
  }
  function welcome() {
    log.replaceChildren(); history = [];
    addMsg("bot", "안녕하세요! 지금 보고 있는 화면에 대해 궁금한 것을 물어보세요. 글로 묻거나 사진(오류 화면, 필기)을 보낼 수 있어요.\n탐구 학습지 문항은 정답을 바로 알려 주지 않고, 생각할 단서를 드려요.\n질문 횟수는 장(주차)마다 따로 세요. 아래에서 이 장에 남은 횟수를 볼 수 있어요.");
  }
  function refreshCtx() {
    const c = getContext() || {};
    ctxChip.replaceChildren(ico("visibility"), `AI가 보는 화면: ${c.title || "현재 화면"}${c.selection ? " · 선택한 글 포함" : ""}`);
    loadQuota(false);
  }
  /* 이 장에서 남은 질문 수. 장이 바뀌었을 때만 서버에 묻는다(화면을 옮기며 계속 묻지 않는다). */
  const showLeft = q => { leftEl.textContent = `${q.chapterTitle || "이 화면"} · 남은 질문 ${q.left}번 (이 장 ${q.limit}번까지)`; };
  async function loadQuota(force) {
    const ch = (getContext() || {}).chapter || "";
    if (!StudentAuth.get() || (!force && ch === quotaFor)) return;
    quotaFor = ch;
    try { showLeft(await FB.assistantQuota(ch)); } catch (e) { leftEl.textContent = ""; }
  }
  function setBusy(b) { busy = b; send.disabled = b; input.disabled = b; }
  async function ask() {
    if (busy) return;
    const q = input.value.trim(); if (!q && !image) return;
    if (!StudentAuth.get()) { addMsg("err", "먼저 아래 버튼으로 학교 Google 계정에 로그인해 주세요."); return; }
    if (!StudentAuth.aiOk()) { addMsg("err", "AI 도우미는 개인정보 동의의 ‘AI 도우미 이용(선택)’ 항목에 동의해야 쓸 수 있어요."); StudentAuth.manageConsent(); return; }
    const ctx = getContext() || {}, im = image;
    addMsg("me", q || "(사진)", im && im.url); input.value = ""; autosize(input); setImage(null);
    const wait = addMsg("bot wait", "생각하는 중…"); setBusy(true);
    try {
      const r = await FB.askAssistant({ question: q, image: im ? { mime: im.mime, data: im.data } : null, context: ctx, history });
      wait.remove(); addMsg(r.refused ? "bot refused" : "bot", r.reply);
      if (!r.refused) { history.push({ role: "user", text: q || "(사진)" }, { role: "model", text: r.reply }); history = history.slice(-6); }      // 범위 밖 질문은 대화 기록에 남기지 않는다
      quotaFor = ctx.chapter || ""; showLeft(r);
    } catch (e) {
      wait.remove();
      const m = String(e.message || "");
      if (/resource-exhausted/.test(e.code) && /번을 모두|쓸 수 없어요/.test(m)) quotaFor = null;        // 한도에 걸렸다: 다음에 화면을 볼 때 남은 횟수를 다시 읽는다
      addMsg("err", /resource-exhausted|너무 빨라|번까지|unavailable/.test(e.code + m) ? m.replace(/^.*?: /, "") : /failed-precondition/.test(e.code) && /동의/.test(m) ? m.replace(/^.*?: /, "") : /failed-precondition/.test(e.code) ? "지금은 AI 도우미를 쓸 수 없어요. 선생님이 켜 주면 쓸 수 있어요."
        : /permission|unauth/.test(e.code) ? "학교 Google 계정으로 로그인해야 해요." : "답을 받지 못했어요. 잠시 뒤에 다시 시도해 주세요.");
    }
    setBusy(false); input.focus();
  }
  function autosize(t) { t.style.height = "auto"; t.style.height = Math.max(96, Math.min(180, t.scrollHeight)) + "px"; }      // 늘 여러 줄(최소 4줄)이 보이고, 길어지면 6~7줄까지 자란다

  /* ---------- 화면 ---------- */
  function build() {
    fab = el("button", { type: "button", class: "ai-fab", "aria-label": "AI 도우미 열기", title: "AI 도우미", hidden: true, onclick: toggle }, ico("smart_toy", "fill"));
    log = el("div", { class: "ai-log", role: "log", "aria-live": "polite" });
    input = el("textarea", { class: "ai-in", rows: 4, placeholder: "궁금한 것을 물어보세요.\n(Enter: 보내기 · Shift+Enter: 줄바꿈)", "aria-label": "질문 입력",
      oninput: () => autosize(input), onkeydown: e => { if (e.key === "Enter" && !e.shiftKey && !e.isComposing) { e.preventDefault(); ask(); } } });
    const file = el("input", { type: "file", accept: "image/jpeg,image/png,image/webp", hidden: true, onchange: e => { pick(e.target.files[0]); e.target.value = ""; } });
    attach = el("button", { type: "button", class: "ai-ico", "aria-label": "사진 파일 첨부", title: "사진 파일 첨부", onclick: () => file.click() }, ico("add_photo_alternate"));
    const pasteBtn = el("button", { type: "button", class: "ai-ico", "aria-label": "클립보드의 이미지 붙여넣기", title: "클립보드의 이미지 붙여넣기", onclick: pasteFromClipboard }, ico("content_paste"));
    send = el("button", { type: "button", class: "ai-send", "aria-label": "보내기", title: "보내기", onclick: ask }, ico("send"));
    preview = el("div", { class: "ai-prev", hidden: true });
    ctxChip = el("div", { class: "ai-ctx" }); leftEl = el("span", { class: "ai-left" });
    const login = el("div", { class: "ai-login", hidden: true }, "학교 Google 계정으로 로그인하면 쓸 수 있어요. ",
      el("button", { type: "button", class: "qbtn", onclick: async () => { const m = await StudentAuth.login(); if (m) addMsg("err", m); } }, ico("login"), "로그인"));
    /* 로그인했지만 AI 도우미(선택 항목)에 동의하지 않은 학생에게는 동의 설정을 안내한다 */
    const needAi = el("div", { class: "ai-login", hidden: true }, "AI 도우미를 쓰려면 개인정보 동의의 ‘AI 도우미 이용(선택)’ 항목에 동의해야 해요. ",
      el("button", { type: "button", class: "qbtn", onclick: () => StudentAuth.manageConsent() }, ico("verified_user"), "동의 설정"));
    const syncLogin = () => { login.hidden = !!StudentAuth.get(); needAi.hidden = !(StudentAuth.get() && !StudentAuth.aiOk()); };
    StudentAuth.onChange(() => { syncLogin(); quotaFor = null; if (panel && !panel.hidden) loadQuota(true); }); syncLogin();
    panel = el("section", { class: "ai-panel", role: "dialog", "aria-label": "AI 도우미", hidden: true },
      el("header", {}, el("b", {}, ico("smart_toy", "fill"), "AI 도우미"),
        el("span", { class: "ai-hbtn" },
          el("button", { type: "button", class: "ai-ico", "aria-label": "새 대화 시작", title: "새 대화 시작 (화면만 비워요. 지난 질문과 답은 선생님이 볼 수 있도록 기록되어 남아요)", onclick: welcome }, ico("add_comment")),
          el("button", { type: "button", class: "ai-ico", "aria-label": "닫기", title: "닫기", onclick: toggle }, ico("close")))),
      el("p", { class: "ai-note" }, "질문과 사진, 지금 보는 화면의 글이 AI(Google Gemini)로 전달돼요. 주고받은 질문과 AI의 답은 선생님이 볼 수 있도록 기록돼요(사진 파일은 저장하지 않아요. 개인정보 동의의 선택 항목에 동의한 경우에만 쓸 수 있어요). 이름·학번·연락처 같은 개인정보는 쓰지 마세요. AI의 답은 틀릴 수 있으니 교재와 함께 확인하세요."),
      log, login, needAi, ctxChip, preview,
      el("div", { class: "ai-row" }, el("span", { class: "ai-tools" }, attach, pasteBtn), input, send, file),
      el("p", { class: "ai-hint" }, ico("image"), "사진: 이미지를 복사한 뒤 이 창에서 Ctrl+V(Mac은 Cmd+V), [붙여넣기] 버튼, 또는 끌어다 놓기로 올려요."), leftEl);
    // 창 어디에서든 이미지를 붙여넣거나(Ctrl/Cmd+V) 끌어다 놓을 수 있다
    panel.addEventListener("paste", e => { const f = imageFrom(e.clipboardData); if (f) { e.preventDefault(); pick(f); } });
    panel.addEventListener("dragover", e => { if ([...(e.dataTransfer ? e.dataTransfer.types : [])].includes("Files")) { e.preventDefault(); panel.classList.add("drop"); } });
    panel.addEventListener("dragleave", e => { if (e.target === panel) panel.classList.remove("drop"); });
    panel.addEventListener("drop", e => { const f = imageFrom(e.dataTransfer); panel.classList.remove("drop"); if (f) { e.preventDefault(); pick(f); } });
    document.body.append(fab, panel);
    document.addEventListener("keydown", e => { if (e.key === "Escape" && !panel.hidden) toggle(); });
    welcome();
  }
  function toggle() {
    const open = panel.hidden; panel.hidden = !open; fab.setAttribute("aria-expanded", String(open));
    if (open) { refreshCtx(); input.focus(); log.scrollTop = log.scrollHeight; } else fab.focus();
  }
  function show() { if (fab) { fab.hidden = !enabled; if (!enabled && !panel.hidden) toggle(); } }

  /* 호스트가 화면 맥락을 만들 때 쓰는 도구 */
  /* 노드의 글을 읽기 좋은 글로: 줄 번호·실행 결과·버튼·그림은 빼고, 화면 밖에 복제해 줄바꿈이 살아 있는 innerText 로 읽는다(visibility:hidden 이면 innerText 가 비므로 화면 밖으로만 치운다). */
  function readable(node, max) {
    const c = node.cloneNode(true);
    c.querySelectorAll(".pr-gutter, .pr-out, .pr-bar, .pr-hl, .copy, button, svg, script, style, textarea, input, select, .ms").forEach(n => n.remove());
    const box = el("div", { style: "position:absolute;left:-99999px;top:0;width:700px;pointer-events:none" }); box.append(c); document.body.append(box);
    const t = (box.innerText || "").replace(/\n{3,}/g, "\n\n").trim(); box.remove(); return t.slice(0, max);
  }
  /* 학생이 드래그해 고른 글(대화창 안에서 고른 것은 뺀다) */
  function selectedText() {
    const s = window.getSelection(); if (!s || s.isCollapsed) return "";
    const n = s.anchorNode && (s.anchorNode.nodeType === 1 ? s.anchorNode : s.anchorNode.parentElement);
    if (n && n.closest && n.closest(".ai-panel")) return "";
    return String(s).trim().slice(0, 1500);
  }
  /* 화면 가운데에 가장 가까운(가운데를 지나면 0) 요소 */
  function nearestMid(nodes) {
    const mid = innerHeight / 2; let best = null, bd = Infinity;
    nodes.forEach(x => { const r = x.getBoundingClientRect(); const d = r.top <= mid && r.bottom >= mid ? 0 : Math.min(Math.abs(r.top - mid), Math.abs(r.bottom - mid)); if (d < bd) { bd = d; best = x; } });
    return best;
  }

  /* o = {getContext}. 교사가 켠 동안만 아이콘을 보인다. */
  function init(o) {
    if (started || typeof FB === "undefined") return; started = true;
    getContext = o.getContext; build();
    setInterval(() => { if (!panel.hidden) refreshCtx(); }, 1500);                // 화면을 옮기거나 글을 고르면 안내가 따라간다
    FB.watchAssistant(s => { enabled = !!(s && s.on); show(); }).catch(() => {});
  }
  return { init, readable, selectedText, nearestMid };
})();
