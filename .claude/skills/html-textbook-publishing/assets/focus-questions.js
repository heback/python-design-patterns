"use strict";
/* 절 제목 옆의 [?] 아이콘: 누르면 "이 절을 읽으며 생각할 질문"이 팝업으로 뜬다.
   닫기: ESC, 팝업 밖(어두운 바탕) 클릭, ✕ 버튼. 질문은 빌드가 버튼의 data-questions(JSON 배열)에 넣어 둔다. */
(function () {
  const btns = Array.from(document.querySelectorAll("button.focus-q"));
  if (!btns.length) return;
  let overlay = null, opener = null, prevOverflow = "";

  function close() {
    if (!overlay) return;
    overlay.remove(); overlay = null;
    document.body.style.overflow = prevOverflow;
    document.removeEventListener("keydown", onKey, true);
    if (opener && document.contains(opener)) opener.focus();
    opener = null;
  }

  function onKey(e) {
    if (!overlay) return;
    if (e.key === "Escape") { e.preventDefault(); e.stopPropagation(); close(); }
    else if (e.key === "Tab") { e.preventDefault(); overlay.querySelector(".fq-close").focus(); }   /* 포커스가 팝업 밖으로 나가지 않게 한다 */
  }

  function open(btn) {
    if (overlay) close();
    let qs = [];
    try { qs = JSON.parse(btn.dataset.questions || "[]"); } catch (e) { /* 질문이 깨졌으면 빈 목록 */ }
    if (!qs.length) return;
    const h2 = btn.closest("h2");
    const section = h2 ? Array.from(h2.childNodes).filter(n => n !== btn).map(n => n.textContent).join("").trim() : "";
    const el = (tag, cls, text) => { const n = document.createElement(tag); if (cls) n.className = cls; if (text != null) n.textContent = text; return n; };

    const close_ = el("button", "fq-close", "✕"); close_.type = "button"; close_.setAttribute("aria-label", "닫기");
    close_.addEventListener("click", close);
    const title = el("h3", "fq-title", "읽으면서 생각해 볼 질문"); title.id = "fq-title";
    const head = el("div", "fq-head"); head.append(title, close_);
    const list = el("ol", "fq-list"); qs.forEach(q => list.append(el("li", null, q)));
    const panel = el("div", "fq-panel");
    panel.setAttribute("role", "dialog"); panel.setAttribute("aria-modal", "true"); panel.setAttribute("aria-labelledby", "fq-title");
    panel.append(head, el("p", "fq-sec", section), list,
      el("p", "fq-note", "답을 미리 알 필요는 없어요. 글과 코드를 읽으면서 하나씩 찾아보세요."));
    overlay = el("div", "fq-overlay"); overlay.append(panel);
    overlay.addEventListener("mousedown", e => { if (e.target === overlay) close(); });   /* 팝업 밖 클릭 */
    opener = btn; prevOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    document.body.append(overlay);
    document.addEventListener("keydown", onKey, true);
    close_.focus();
  }

  btns.forEach(b => b.addEventListener("click", () => open(b)));
})();
