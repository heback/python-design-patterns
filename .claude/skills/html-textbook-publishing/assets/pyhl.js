"use strict";
/* 파이썬 문법 강조 공용 모듈 (교재 textbook/ 과 탐구 학습지 inquiry/ 가 함께 쓴다). 외부 라이브러리·네트워크 없이 동작한다.
   토큰 클래스 이름은 Prism 과 같다(.token.keyword 등). 색은 pyrun.css 의 --tok-* 변수만 쓰므로 다크 모드가 자동으로 맞는다.
   공개 API: PyHL.html(code) → 색칠한 HTML 문자열 · PyHL.apply(root) → root 안의 code.language-python 을 색칠한다 */
const PyHL = (function () {
  const KEYWORDS = new Set(("and as assert async await break class continue def del elif else except finally for from global if import " +
    "in is lambda nonlocal not or pass raise return try while with yield match case").split(" "));
  const CONSTS = new Set(["True", "False", "None"]);
  const BUILTINS = new Set(("abs all any bool bytes callable chr dict dir divmod enumerate filter float format frozenset getattr hasattr hash " +
    "id input int isinstance issubclass iter len list map max min next object open ord pow print property range repr reversed round set setattr " +
    "slice sorted staticmethod classmethod str sum super tuple type vars zip self cls NotImplemented Ellipsis " +
    "Exception ValueError TypeError KeyError IndexError AttributeError RuntimeError NotImplementedError StopIteration ZeroDivisionError").split(" "));

  /* 한 번에 한 토큰씩 앞에서부터 읽는다. 순서가 중요하다: 긴 문자열·주석을 먼저 잡아야 그 안의 키워드가 색칠되지 않는다. */
  const RE = new RegExp([
    "(#[^\\n]*)",                                                                           // 1 주석
    "((?:[rRbBuUfF]{1,2})?(?:\"\"\"[\\s\\S]*?(?:\"\"\"|$)|'''[\\s\\S]*?(?:'''|$)))",       // 2 삼중 따옴표(독스트링)
    "((?:[rRbBuUfF]{1,2})?(?:\"(?:\\\\.|[^\"\\\\\\n])*\"?|'(?:\\\\.|[^'\\\\\\n])*'?))",     // 3 문자열
    "(^[ \\t]*@[A-Za-z_][\\w.]*)",                                                          // 4 데코레이터
    "(\\b(?:0[xX][0-9a-fA-F_]+|0[bB][01_]+|0[oO][0-7_]+|\\d[\\d_]*\\.?[\\d_]*(?:[eE][+-]?\\d+)?j?)\\b|\\.\\d[\\d_]*)", // 5 숫자
    "([A-Za-z_][A-Za-z_0-9]*)",                                                             // 6 식별자
    "([+\\-*/%=<>!&|^~:]+)",                                                                // 7 연산자
    "([()\\[\\]{},.;])",                                                                    // 8 구두점
  ].join("|"), "gm");

  const esc = s => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  const span = (cls, s) => '<span class="token ' + cls + '">' + esc(s) + "</span>";

  /* f-문자열의 {표현식} 은 문자열 색에서 빼 준다. */
  function fstring(s) {
    if (!/^[rRbBuU]*[fF]/.test(s)) return span("string", s);
    return s.split(/(\{\{|\}\}|\{[^{}\n]*\})/).map((p, i) => i % 2 && p.length > 2 && p[1] !== "{" ?
      '<span class="token string-interpolation">' + esc(p) + "</span>" : span("string", p)).join("");
  }

  function html(code) {
    let out = "", last = 0, prev = "", m;           // prev: 직전 의미 있는 토큰(def/class 뒤 이름 판별용)
    RE.lastIndex = 0;
    while ((m = RE.exec(code))) {
      if (m.index > last) out += esc(code.slice(last, m.index));
      const t = m[0]; last = RE.lastIndex;
      if (m[1] != null) out += span("comment", t);
      else if (m[2] != null) out += /^[rRbBuU]*[fF]/.test(t) ? fstring(t).replace(/class="token string"/g, 'class="token triple-quoted-string string"') : span("triple-quoted-string string", t);
      else if (m[3] != null) out += fstring(t);
      else if (m[4] != null) out += esc(t.slice(0, t.indexOf("@"))) + span("decorator", t.slice(t.indexOf("@")));
      else if (m[5] != null) out += span("number", t);
      else if (m[6] != null) {
        const next = code.slice(last).match(/^[ \t]*(\()?/)[1];
        if (prev === "def") out += span("function", t);
        else if (prev === "class") out += span("class-name", t);
        else if (KEYWORDS.has(t)) out += span("keyword", t);
        else if (CONSTS.has(t)) out += span("boolean", t);
        else if (BUILTINS.has(t)) out += span("builtin", t);
        else if (next && prev !== ".") out += span("function", t);        // 일반 호출 f(...)
        else if (next) out += span("function", t);                        // 메서드 호출 obj.f(...)
        else if (/^[A-Z][A-Za-z0-9]*$/.test(t) && /[a-z]/.test(t)) out += span("class-name", t);   // CamelCase 는 클래스로 본다
        else out += esc(t);
        prev = t;
        continue;
      }
      else if (m[7] != null) out += span("operator", t);
      else out += span("punctuation", t);
      prev = "";
    }
    return out + esc(code.slice(last));
  }

  function apply(root) {
    (root || document).querySelectorAll("code.language-python:not([data-hl])").forEach(c => {
      c.innerHTML = html(c.textContent); c.dataset.hl = "1";
    });
  }

  return { html, apply };
})();
