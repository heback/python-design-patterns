"use strict";
/* 학생 '선생님께 질문'(학습지·호스팅 교재 공용). AI 도우미 아이콘 바로 위에 아이콘이 있고, 누르면 AI 도우미와 같은 모양의 대화창이 열린다.
   입력 방식은 AI 도우미와 같다(글·사진 첨부·붙여넣기·끌어다 놓기, Enter 로 보내기) — Assistant.composer 를 그대로 쓴다.
   AI 도우미와 달리 답은 AI 가 아니라 선생님이 쓴다. 질문 개수에는 제한이 없고, 선생님이 답하면 이 창에 실시간으로 나타나며 아이콘에 새 답변 수 배지가 뜬다.
   서버에는 질문·사진·지금 보던 화면의 제목·고른 글이 선생님이 볼 수 있도록 저장된다. 선생님이 AI 추천 답변을 쓰면(AI 선택 동의를 한 학생만) 질문이 AI(Google Gemini)로 전달될 수 있다.
   필요한 전역: el, ico, FB(fb.js), StudentAuth(student-auth.js), Assistant(assistant.js, init 에서 이 모듈을 함께 시작한다). 호스트의 getContext() => {kind, chapter, title, selection} 를 AI 도우미와 같이 쓴다. */
const AskTeacher = (() => {
  const MAX_BYTES = 500_000, SIDES = [1280, 1024, 800];       // 사진은 문서에 저장되므로(문서 1MiB 한도) AI 도우미보다 작게 줄인다
  let getContext = () => ({}), fab = null, badge = null, panel = null, log = null, cp = null, ctxChip = null, loginBox = null;
  let started = false, busy = false, uid = null, thread = null, msgs = [], unThread = null, unMsgs = null, marking = false, msgErr = "", pending = null;

  const fmt = t => { const d = t && t.toMillis ? new Date(t.toMillis()) : null; if (!d) return ""; const p = n => String(n).padStart(2, "0"); return `${d.getMonth() + 1}/${d.getDate()} ${p(d.getHours())}:${p(d.getMinutes())}`; };
  const unread = () => (thread && Number(thread.studentUnread)) || 0;

  /* ---------- 대화 그리기 ---------- */
  function bubble(m) {
    if (m.from === "teacher") return el("div", { class: "ai-msg teacher" }, el("div", { class: "ask-who" }, ico("school", "fill"), "선생님", el("span", {}, fmt(m.at))), el("div", { class: "ai-txt" }, m.text));
    const b = el("div", { class: "ai-msg me" });
    if (m.image && m.image.data) b.append(el("img", { src: `data:${m.image.mime};base64,${m.image.data}`, alt: "보낸 사진" }));
    else if (m.hasImage) b.append(el("div", { class: "ask-noimg" }, "(사진)"));
    if (m.text) b.append(el("div", { class: "ai-txt" }, m.text));
    b.append(el("div", { class: "ask-time" }, fmt(m.at)));
    return b;
  }
  function paint() {
    const kids = [el("div", { class: "ai-msg bot" }, el("div", { class: "ai-txt" }, "선생님께 궁금한 것을 보내세요. 글로 묻거나 사진(오류 화면, 필기)을 보낼 수 있어요.\n선생님이 확인하면 이 창에 답이 나타나고, 아이콘에 새 답변 표시가 떠요. 바로 답하지 못할 수 있으니 기다리는 동안 AI 도우미에게 먼저 물어봐도 좋아요.\n질문 개수에는 제한이 없어요."))];
    if (msgErr) kids.push(el("div", { class: "ai-msg err" }, msgErr));
    msgs.forEach(m => kids.push(bubble(m)));
    if (pending) kids.push(pending);
    log.replaceChildren(...kids); log.scrollTop = log.scrollHeight;
  }
  function paintBadge() {
    const n = unread();
    badge.hidden = !n; badge.textContent = n > 9 ? "9+" : String(n);
    fab.setAttribute("aria-label", n ? `선생님께 질문 열기 (새 답변 ${n}건)` : "선생님께 질문 열기");
    fab.title = n ? `선생님께 질문 — 새 답변 ${n}건` : "선생님께 질문";
  }
  function refreshCtx() {
    const c = getContext() || {};
    ctxChip.replaceChildren(ico("visibility"), `선생님이 보게 되는 화면: ${c.title || "현재 화면"}${c.selection ? " · 선택한 글 포함" : ""}`);
  }

  /* ---------- 서버와 연결: 로그인(·동의)한 학생의 대화를 실시간으로 읽는다 ---------- */
  function stop() { [unThread, unMsgs].forEach(f => { try { f && f(); } catch (e) {} }); unThread = unMsgs = null; }
  function syncUser() {
    const u = StudentAuth.get(), next = u ? u.uid : null;
    loginBox.hidden = !!u;
    if (next === uid) return;
    stop(); uid = next; thread = null; msgs = []; msgErr = ""; pending = null; marking = false;
    paintBadge(); paint();
    if (!uid) return;
    const me = uid;
    FB.watchMyThread(me, t => { if (uid !== me) return; thread = t || null; paintBadge(); markReadIfOpen(); }).then(f => { if (uid === me && !unThread) unThread = f; else f(); }).catch(() => {});
    if (!panel.hidden) watchMsgs();
  }
  function watchMsgs() {
    if (unMsgs || !uid) return; const me = uid;
    FB.watchAskMsgs(me, (rows, err) => { if (uid !== me) return; msgs = rows || []; msgErr = err ? "질문 기록을 불러오지 못했어요. 잠시 뒤 다시 열어 보세요." : ""; paint(); markReadIfOpen(); })
      .then(f => { if (uid === me && !unMsgs) unMsgs = f; else f(); }).catch(() => {});
  }
  /* 창을 열어 둔 동안 새 답변이 오면 곧바로 읽음 처리한다(배지가 계속 남지 않게) */
  function markReadIfOpen() {
    if (panel.hidden || marking || !unread()) return;
    marking = true; FB.markAskRead().catch(() => {}).then(() => { marking = false; });
  }

  /* ---------- 보내기 ---------- */
  function addErr(text) { msgErr = text; paint(); }
  async function send() {
    if (busy) return;
    const text = cp.input.value.trim(), im = cp.image; if (!text && !im) return;
    if (!StudentAuth.get()) { addErr("먼저 아래 버튼으로 학교 Google 계정에 로그인해 주세요."); return; }
    const c = getContext() || {};
    msgErr = ""; busy = true; cp.setBusy(true);
    pending = el("div", { class: "ai-msg me wait" }, im ? el("img", { src: im.url, alt: "보내는 사진" }) : null, el("div", { class: "ai-txt" }, (text || "(사진)") + "\n보내는 중…")); paint();
    try {
      await FB.askTeacher({ text, image: im ? { mime: im.mime, data: im.data } : null, context: { kind: c.kind, chapter: c.chapter, title: c.title, selection: c.selection } });
      cp.input.value = ""; cp.grow(); cp.setImage(null); pending = null;           // 성공했을 때만 입력란을 비운다(실패하면 쓴 글을 지키려고 그대로 둔다)
      paint();
    } catch (e) {
      pending = null;
      const m = String(e.message || ""), code = String(e.code || "");
      msgErr = /resource-exhausted/.test(code) ? "질문이 너무 빨라요. 잠시 뒤에 다시 보내 주세요."
        : /failed-precondition/.test(code) && /동의/.test(m) ? m.replace(/^.*?: /, "")
        : /invalid-argument/.test(code) ? m.replace(/^.*?: /, "")
        : /permission|unauth/.test(code) ? "학교 Google 계정으로 로그인해야 해요." : "보내지 못했어요. 쓴 글은 그대로 두었으니 잠시 뒤에 다시 보내 주세요.";
      paint();
    }
    busy = false; cp.setBusy(false); cp.input.focus();
  }

  /* ---------- 화면 ---------- */
  function build() {
    fab = el("button", { type: "button", class: "ai-fab ask-fab", "aria-label": "선생님께 질문 열기", title: "선생님께 질문", onclick: toggle }, ico("contact_support", "fill"));
    badge = el("span", { class: "fab-badge", hidden: true, "aria-hidden": "true" }); fab.append(badge);
    log = el("div", { class: "ai-log", role: "log", "aria-live": "polite" });
    cp = Assistant.composer({ placeholder: "선생님께 궁금한 것을 적어 주세요.\n(Enter: 보내기 · Shift+Enter: 줄바꿈)", onSend: send, onError: addErr, maxBytes: MAX_BYTES, sides: SIDES });
    ctxChip = el("div", { class: "ai-ctx" });
    loginBox = el("div", { class: "ai-login", hidden: true }, "학교 Google 계정으로 로그인하면 질문할 수 있어요. ",
      el("button", { type: "button", class: "qbtn", onclick: async () => { const m = await StudentAuth.login(); if (m) addErr(m); } }, ico("login"), "로그인"));
    panel = el("section", { class: "ai-panel ask-panel", role: "dialog", "aria-label": "선생님께 질문", hidden: true },
      el("header", {}, el("b", {}, ico("contact_support", "fill"), "선생님께 질문"),
        el("span", { class: "ai-hbtn" }, el("button", { type: "button", class: "ai-ico", "aria-label": "닫기", title: "닫기", onclick: toggle }, ico("close")))),
      el("p", { class: "ai-note" }, "질문과 사진, 지금 보는 화면의 제목·고른 글은 선생님이 볼 수 있게 저장돼요(이름·이메일과 함께). ‘AI 도우미 이용(선택)’에 동의했다면, 선생님이 답을 쓸 때 AI(Google Gemini)의 추천 답변을 참고하면서 질문 내용이 AI로 전달될 수 있어요. 전화번호 같은 개인정보는 쓰지 마세요."),
      log, loginBox, ctxChip, cp.preview, cp.row, cp.hint);
    cp.wire(panel);
    document.body.append(panel); Assistant.dock().prepend(fab);                  // AI 도우미 아이콘 바로 위
    document.addEventListener("dp-panel-open", e => { if (e.detail !== "ask" && !panel.hidden) toggle(); });
    document.addEventListener("keydown", e => { if (e.key === "Escape" && !panel.hidden) toggle(); });
    paint(); paintBadge();
  }
  function toggle() {
    const open = panel.hidden; panel.hidden = !open; fab.setAttribute("aria-expanded", String(open));
    if (open) { Assistant.announceOpen("ask"); refreshCtx(); watchMsgs(); markReadIfOpen(); cp.input.focus(); log.scrollTop = log.scrollHeight; }
    else if (document.activeElement && panel.contains(document.activeElement)) fab.focus();
  }

  /* o = {getContext}. 로그인한 학생에게는 항상 보인다(AI 도우미와 달리 교사가 켜고 끄지 않는다). */
  function init(o) {
    if (started || typeof FB === "undefined" || typeof Assistant === "undefined") return; started = true;
    getContext = o.getContext; build();
    setInterval(() => { if (!panel.hidden) refreshCtx(); }, 1500);                // 화면을 옮기거나 글을 고르면 안내가 따라간다
    StudentAuth.onChange(syncUser); syncUser();
  }
  return { init };
})();
