"use strict";
/* 교재 쪽 연결: 코드 블록(figure.code)과 연습문제의 시작 코드를 실행·편집 가능하게 만들고,
   학생이 고친 코드를 브라우저에 자동 저장하며 JSON 파일로 저장/불러오기를 지원한다.
   JSON 모양: {app:"dp-textbook", schema:1, saved, edits:{"03-builder.html|키": "코드"}} */
(function () {
  const APP = "dp-textbook", LS = "dp-textbook-edits";
  const PAGE = (location.pathname.split("/").pop() || "index.html");
  const $$ = (s, r) => Array.from((r || document).querySelectorAll(s));
  const ls = {
    get(k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
    set(k, v) { try { localStorage.setItem(k, v); } catch (e) {} },
  };
  let edits = {};
  try { const d = JSON.parse(ls.get(LS) || "{}"); if (d && typeof d === "object") edits = d; } catch (e) {}
  const persist = () => ls.set(LS, JSON.stringify(edits));
  const toast = msg => {
    let t = document.querySelector(".tb-toast");
    if (!t) { t = document.createElement("div"); t.className = "tb-toast"; document.body.append(t); }
    t.textContent = msg; t.classList.add("on"); clearTimeout(t._h); t._h = setTimeout(() => t.classList.remove("on"), 2400);
  };

  /* 블록마다 안정적인 키: 캡션(파일명) 또는 연습문제 번호 + 같은 이름의 등장 순서 */
  const seen = {};
  const keyOf = base => { seen[base] = (seen[base] || 0) + 1; return PAGE + "|" + base + (seen[base] > 1 ? "#" + seen[base] : ""); };

  function mount(host, o) {
    const key = o.key, saved = edits[key];
    const ed = PyRun.mountEditor({
      code: saved != null ? saved : o.code, starter: o.code, example: o.example, exampleTitle: o.exampleTitle, label: o.label,
      onChange: v => { if (v === o.code) delete edits[key]; else edits[key] = v; persist(); },
    });
    host.replaceWith(ed.el);
    return ed;
  }

  /* 1) 예제 코드 블록: 평소엔 색칠된 코드, [▶ 실행/편집]을 누르면 편집기로 바뀐다. */
  $$("figure.code").forEach(fig => {
    const cap = fig.querySelector("figcaption"), code = fig.dataset.full || fig.querySelector("code").textContent;
    const key = keyOf(cap.firstChild.textContent.trim());
    const full = !!fig.dataset.full;
    const btn = document.createElement("button");
    btn.className = "copy edit"; btn.type = "button"; btn.textContent = full ? "▶ 전체 실행·편집" : "▶ 실행·편집";
    btn.title = full ? "이 장면은 파일의 일부입니다. 파일 전체를 편집기로 엽니다." : "코드를 고쳐 보고 실행합니다.";
    const open = () => {
      const wrap = document.createElement("div");
      fig.querySelector("pre").replaceWith(wrap);
      btn.remove(); fig.classList.add("editing");
      const ed = mount(wrap, { key, code, label: cap.firstChild.textContent.trim() });
      const cp = fig.querySelector(".copy"); if (cp) cp.remove();
      fig.querySelector("figcaption").append(Object.assign(document.createElement("span"), { className: "tb-live", textContent: full ? "전체 파일 · 편집 중" : "편집 중" }));
      return ed;
    };
    btn.addEventListener("click", open);
    cap.insertBefore(btn, cap.querySelector(".copy"));
    if (edits[key] != null) open();       // 이전에 고친 코드가 있으면 바로 편집기로
  });

  /* 2) 연습문제의 시작 코드: 처음부터 편집기. 해설의 코드가 '예시 코드' 팝업이 된다. */
  $$(".exercise").forEach(ex => {
    const sol = ex.querySelector("details.solution");
    const solFig = sol && sol.querySelector("figure.code");
    const solCode = solFig ? (solFig.dataset.full || solFig.querySelector("code").textContent)
      : (sol && sol.querySelector("pre code") ? sol.querySelector("pre code").textContent : null);
    const title = (ex.querySelector("h3") || {}).textContent || "연습문제";
    $$("pre", ex).filter(p => !p.closest("details") && !p.closest("figure") && p.querySelector("code.language-python")).forEach(pre => {
      const code = pre.textContent.replace(/\n$/, "");
      const ed = mount(pre, { key: keyOf((ex.id || "ex") + "-시작코드"), code, example: solCode, exampleTitle: "예시 코드 — " + title.replace(/^\S+\s*/, "").trim(), label: "연습문제 코드" });
      ed.el.classList.add("pr-exercise");
    });
  });

  /* 3) 내 코드 JSON 저장/불러오기 (상단 바의 버튼) */
  const bSave = document.getElementById("tb-save"), bLoad = document.getElementById("tb-load"), fIn = document.getElementById("tb-file");
  if (bSave) bSave.addEventListener("click", () => {
    if (!Object.keys(edits).length) { toast("아직 고친 코드가 없어요. 코드 블록의 ▶ 실행·편집을 눌러 고쳐 보세요."); return; }
    const d = { app: APP, schema: 1, saved: new Date().toISOString(), edits };
    const p = n => String(n).padStart(2, "0"), t = new Date();
    const name = `디자인패턴교재_내코드_${t.getFullYear()}${p(t.getMonth() + 1)}${p(t.getDate())}.json`;
    const a = Object.assign(document.createElement("a"), { href: URL.createObjectURL(new Blob([JSON.stringify(d, null, 2)], { type: "application/json" })), download: name });
    document.body.append(a); a.click(); a.remove(); setTimeout(() => URL.revokeObjectURL(a.href), 2000);
    toast("저장했습니다: " + name);
  });
  if (bLoad && fIn) {
    bLoad.addEventListener("click", () => fIn.click());
    fIn.addEventListener("change", () => {
      const f = fIn.files[0]; fIn.value = ""; if (!f) return;
      const r = new FileReader();
      r.onload = () => {
        try {
          const d = JSON.parse(r.result);
          if (!d || d.app !== APP || typeof d.edits !== "object") throw 0;
          const n = Object.keys(d.edits).length;
          if (Object.keys(edits).length && !confirm("지금 브라우저에 있는 내 코드가 불러온 파일의 내용으로 바뀝니다. 계속할까요?")) return;
          edits = d.edits; persist(); toast(`불러왔습니다 (${n}곳) — 화면을 새로 고칩니다`);
          setTimeout(() => location.reload(), 600);
        } catch (e) { alert("이 교재에서 저장한 코드 JSON 파일이 아닙니다."); }
      };
      r.readAsText(f);
    });
  }
})();
