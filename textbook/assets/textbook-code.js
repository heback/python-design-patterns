"use strict";
/* 교재 쪽 연결: 코드 블록(figure.code)은 [▶ 실행]만, 연습문제의 시작 코드는 실행·편집이 가능한 편집기로 만든다.
   고친 코드는 저장하지 않는다(새로고침하면 처음 코드로 돌아간다). */
(function () {
  const $$ = (s, r) => Array.from((r || document).querySelectorAll(s));

  /* 1) 예제 코드 블록: 고칠 필요가 없으므로 코드는 그대로 두고 [▶ 실행]만 둔다. 결과는 코드 아래에 나타난다.
        일부 행만 보이는 블록(data-full)은 파일 전체를 실행한다. */
  $$("figure.code").forEach(fig => {
    const cap = fig.querySelector("figcaption"), code = fig.dataset.full || fig.querySelector("code").textContent;
    const rn = PyRun.makeRunner(() => code);
    rn.bRun.title = fig.dataset.full ? "이 장면은 파일의 일부입니다. 파일 전체를 실행합니다." : "이 코드를 실행합니다.";
    const cp = cap.querySelector(".copy");
    cap.insertBefore(rn.bRun, cp); cap.insertBefore(rn.bStop, cp); cap.insertBefore(rn.status, cp);
    fig.append(rn.outBox);
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
      const ed = PyRun.mountEditor({ code, example: solCode, exampleTitle: "예시 코드 — " + title.replace(/^\S+\s*/, "").trim(), label: "연습문제 코드" });
      pre.replaceWith(ed.el);
      ed.el.classList.add("pr-exercise");
    });
  });
})();
