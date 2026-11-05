"use strict";
/* 학생 로그인(학교 Google 계정)과 개인정보 수집·이용 동의. 학습지와 교재 사본이 같은 주소라 한 번 로그인·동의하면 두 화면이 함께 쓴다.
   진도 전달·AI 도우미는 '로그인 + 현재 문구에 동의'가 있어야 한다: StudentAuth.get() 은 동의까지 마친 계정만 돌려주므로
   monitor.js·textbook-monitor.js·assistant.js 는 고칠 것 없이 동의 전에는 아무것도 보내지 않는다. 서버(firestore.rules·functions)가 다시 확인한다.
   필요한 전역: FB(fb.js), core.js(el, ico, $). */

/* ---------- 개인정보 수집·이용 동의 ----------
   동의 기록은 consents/{uid}(버전·선택 항목·서버 시각). 문구를 바꾸면 VERSION 을 올린다 → 학생은 새 문구로 다시 동의한다.
   VERSION 은 firestore.rules 의 consentVersion(), firebase/functions/config.js 의 CONSENT_VERSION 과 같아야 한다(functions 테스트가 확인). */
const Consent = (() => {
  const VERSION = "2026-11-05";
  let ov = null;
  const close = () => { if (ov) { ov.remove(); ov = null; document.body.classList.remove("cs-lock"); } };
  const sec = (title, ...body) => el("section", { class: "cs-sec" }, el("h4", {}, title), ...body);
  const li = (...k) => el("li", {}, ...k);

  /* 동의 창. manage=false: 처음 동의(건너뛸 수 없다, 동의하지 않으면 로그아웃), manage=true: 동의한 뒤의 관리(선택 항목 변경·철회) */
  function open(manage) {
    if (ov) { if (!!ov._manage === !!manage) return; close(); }
    const acct = StudentAuth.account(), cur = StudentAuth.consentDoc(), msg = el("div", { class: "cs-msg", role: "alert" });
    const req = el("input", { type: "checkbox", id: "cs-req" }), ai = el("input", { type: "checkbox", id: "cs-ai" });
    req.checked = !!manage; req.disabled = !!manage; ai.checked = !!(manage && cur && cur.ai);
    const go = el("button", { type: "button", class: "qbtn primary cs-go" }, ico("task_alt"), manage ? "저장" : "동의하고 시작하기");
    const sync = () => { go.disabled = !req.checked; };
    req.addEventListener("change", sync); sync();
    const busy = (b, on) => { b.disabled = on; };
    go.addEventListener("click", async () => {
      msg.textContent = ""; busy(go, true);
      try { await FB.saveConsent(VERSION, ai.checked); if (manage) close(); }          // 처음 동의는 저장되면 구독이 알려 주어 StudentAuth 가 창을 닫는다
      catch (e) { msg.textContent = "저장하지 못했어요: " + FB.fbErr(e); busy(go, false); }
    });
    const side = manage
      ? [el("button", { type: "button", class: "qbtn small", onclick: close }, "닫기"),
         el("button", { type: "button", class: "qbtn small cs-bad", onclick: async () => {
           if (!confirm("동의를 철회하면 진도 전달과 AI 도우미 이용이 멈추고 로그아웃돼요. 이미 모인 기록의 삭제는 선생님께 요청해야 해요. 철회할까요?")) return;
           try { await FB.withdrawConsent(); close(); await StudentAuth.logout(); } catch (e) { msg.textContent = "철회하지 못했어요: " + FB.fbErr(e); }
         } }, "동의 철회하고 로그아웃")]
      : [el("button", { type: "button", class: "qbtn small", onclick: async () => { close(); await StudentAuth.logout(); } }, "동의하지 않아요(로그아웃)")];
    const box = el("div", { class: "cs-box", role: "dialog", "aria-modal": "true", "aria-labelledby": "cs-title" },
      el("h3", { id: "cs-title" }, ico("verified_user", "fill"), "개인정보 수집·이용 동의"),
      el("p", { class: "cs-lead" }, manage ? "동의한 내용이에요. 선택 항목을 바꾸거나 동의를 철회할 수 있어요." : "진도를 선생님께 전달하고 AI 도우미를 쓰려면 아래 내용에 동의해야 해요. 끝까지 읽고 선택해 주세요.",
        acct ? el("span", { class: "cs-acct" }, " 로그인한 계정: " + acct.email) : null),
      el("div", { class: "cs-scroll", tabindex: "0" },
        sec("1. 수집·이용 목적", el("p", {}, "수업 중 학습 진도 확인과 학습 지원·피드백, (선택) AI 도우미가 질문에 답하기 위해서예요.")),
        sec("2. 수집·제공하는 개인정보 — 필수",
          el("ul", {},
            li(el("b", {}, "학번, 성명, 이메일"), " — 학교 Google 계정에 등록된 정보"),
            li(el("b", {}, "학습 이력 정보"), " — 교재에서 읽은 장·절, 학습지에서 마친 문항과 지금 있던 곳, 장·절별 체류 시간, 활동 시간(입력·스크롤이 있던 시간), 마지막 활동 시각, 이 화면을 보고 있는지(다른 탭·창으로 옮겼는지)와 벗어난 횟수·시간")),
          el("p", {}, "위 정보는 ", el("b", {}, "수업 담당 교사에게 제공"), "되어 교사 화면에 표시돼요. 그 밖의 사람이나 기관에는 제공하지 않아요."),
          el("p", { class: "cs-dim" }, "수집하지 않는 것: 학습지에 쓴 글의 내용, 키 입력, 화면 내용, 보고 있는 주소.")),
        sec("3. AI 도우미 이용 — 선택",
          el("ul", {},
            li("질문, 사진을 보냈는지(사진 파일은 저장하지 않아요), AI의 답, 질문할 때 보던 화면의 글. 주고받은 내용은 ", el("b", {}, "담당 교사가 볼 수 있게 기록"), "돼요."),
            li("질문·사진·화면의 글은 답을 만들기 위해 ", el("b", {}, "Google(Gemini API, Google LLC, 미국)에 전달"), "돼요(국외 이전). 이름·학번·연락처 같은 개인정보는 질문에 쓰지 마세요.")),
          el("p", { class: "cs-dim" }, "선택 항목에 동의하지 않아도 필수 항목만으로 진도 전달은 쓸 수 있어요.")),
        sec("4. 보유·이용 기간", el("p", {}, "이 과목의 수업이 끝나면 담당 교사가 지체 없이 삭제해요.")),
        sec("5. 동의하지 않을 권리와 철회",
          el("ul", {},
            li("동의하지 않을 수 있어요. 그러면 진도 전달과 AI 도우미를 쓸 수 없어요(교재 읽기와 코드 실행은 그대로 할 수 있어요)."),
            li("동의한 뒤에도 화면 위쪽 안내 줄의 ", el("b", {}, "[개인정보 동의]"), "에서 언제든 선택 항목을 바꾸거나 철회할 수 있어요. 철회하면 새로 모으는 것이 멈추고, 이미 모인 기록의 삭제는 담당 교사에게 요청해요."))),
        el("p", { class: "cs-dim" }, `문구 버전 ${VERSION}`)),
      el("label", { class: "cs-ck", for: "cs-req" }, req, el("span", {}, el("b", { class: "cs-tag" }, "필수"), " 위 개인정보(학번, 성명, 이메일, 학습 이력 정보)를 수집·이용하고 수업 담당 교사에게 제공하는 데 동의해요.")),
      el("label", { class: "cs-ck", for: "cs-ai" }, ai, el("span", {}, el("b", { class: "cs-tag opt" }, "선택"), " AI 도우미를 쓸 때 질문·답이 기록되고 질문·사진·화면의 글이 Google(Gemini)에 전달되는 데 동의해요.")),
      msg,
      el("div", { class: "cs-btns" }, go, el("span", { class: "grow" }), ...side));
    ov = el("div", { class: "cs-overlay" }, box); ov._manage = !!manage;
    if (manage) ov.addEventListener("keydown", e => { if (e.key === "Escape") close(); });
    document.body.append(ov); document.body.classList.add("cs-lock");
    (manage ? ai : req).focus();
  }
  return { VERSION, open, close, isOpen: () => !!ov, isManage: () => !!(ov && ov._manage) };
})();

const StudentAuth = (() => {
  /* acct: 로그인한 학교 계정, consent: 내 동의 문서(undefined = 아직 모름·읽기 실패, null = 없음). get() 은 acct 와 현재 버전의 동의가 모두 있어야 계정을 돌려준다. */
  let acct = null, consent = undefined, unwatch = null, lastSig = ""; const subs = [];
  const mine = u => (u && !u.isAnonymous && (u.email || "").toLowerCase().endsWith("@" + FB.domain)) ? u : null;
  const consentOk = c => !!(c && c.version === Consent.VERSION);
  const effective = () => (acct && consentOk(consent)) ? acct : null;
  /* 상태가 바뀌었으면(계정·동의 여부·선택 항목) 구독자에게 알리고, 동의 창을 맞춘다. */
  function sync() {
    const sig = [acct && acct.uid, consentOk(consent), !!(consent && consent.ai)].join("|");
    if (acct && consent === null || (acct && consent && !consentOk(consent))) Consent.open(false);      // 동의한 적 없음·철회·문구 버전이 바뀜 → 동의 창
    else if (Consent.isOpen() && (!acct || (!Consent.isManage() && consentOk(consent)))) Consent.close();   // 로그아웃했거나 처음 동의를 마침
    if (sig === lastSig) return; lastSig = sig;
    subs.forEach(f => { try { f(effective()); } catch (e) {} });
  }
  function setAcct(u) {
    const next = mine(u), changed = (next && next.uid) !== (acct && acct.uid);
    acct = next;
    if (changed) {
      consent = undefined; if (unwatch) { unwatch(); unwatch = null; }
      if (acct) { const uid = acct.uid;
        FB.watchMyConsent(uid, c => { if (acct && acct.uid === uid) { consent = c; sync(); } })
          .then(f => { if (acct && acct.uid === uid && !unwatch) unwatch = f; else f(); }).catch(() => {}); }
    }
    sync();
  }
  async function init() {
    try { setAcct(await FB.currentUser()); } catch (e) { setAcct(null); }
    FB.onAuth(u => setAcct(u)).catch(() => {});
  }
  /* 로그인 창을 띄운다. 학교 계정이 아니면 바로 로그아웃하고 이유를 돌려준다. 성공하면 null, 실패하면 안내 문장. 동의가 없으면 로그인 직후 동의 창이 뜬다. */
  async function login() {
    try {
      const r = await FB.signIn();
      if (!mine(r.user)) { await FB.signOut(); return `학교 계정(@${FB.domain})으로 로그인해 주세요.`; }
      return null;
    } catch (e) {
      if (/popup-closed|cancelled|popup_closed/.test(e.code || "")) return null;
      return /popup-blocked/.test(e.code || "") ? "로그인 창이 막혔어요. 브라우저의 팝업 허용을 켜 주세요." : "로그인하지 못했어요: " + FB.fbErr(e);
    }
  }
  /* 계정(uid)별 저장소 키(읽은 절·활동 시간). 로그인 전에는 "-anon" */
  const key = base => base + "-" + (acct ? acct.uid : "anon");
  return { init, login, logout: () => FB.signOut(), get: effective, key, onChange: f => subs.push(f),
           account: () => acct,                                         // 로그인한 계정(동의 전이어도)
           consentDoc: () => consent || null,
           aiOk: () => !!(effective() && consent && consent.ai === true),   // AI 도우미(선택 항목)에 동의했는가
           manageConsent: () => { if (effective()) Consent.open(true); } };
})();

/* 이 화면을 보고 있는지(탭 가림·창 포커스). 브라우저가 알려 주는 두 신호만 쓴다:
     hidden = 다른 탭으로 옮겼거나 창을 최소화해 이 탭이 가려짐(visibilitychange),
     blur   = 이 탭은 보이지만 다른 창·프로그램을 눌러 포커스를 잃음(blur),
     on     = 보이고 포커스도 있음.
   무엇을 보고 있는지(주소·제목·내용)는 브라우저가 알려 주지 않으므로 수집하지 않는다.
   전달: 지금 상태(view)와 그 상태가 된 시각(viewAt), 이탈 횟수(leaves = on 에서 벗어난 횟수), 이탈한 시간 합계(awayMs).
   횟수·시간은 이 브라우저의 localStorage 에 계정(uid)별로 쌓는다. 학생 안내 줄의 문구는 이 목록과 같게 유지한다. */
const FocusTrack = (() => {
  const now = () => Date.now();
  const compute = () => document.visibilityState === "hidden" ? "hidden" : (document.hasFocus() ? "on" : "blur");
  const K = () => StudentAuth.key("dp-inquiry-student-focus");
  let state = compute(), since = now(), leaves = 0, awayMs = 0, awaySince = state === "on" ? 0 : now(); const subs = [];
  function load() {
    let d = {}; try { d = JSON.parse(lsGet(K()) || "{}"); } catch (e) {}
    leaves = Number(d.leaves) || 0; awayMs = Number(d.awayMs) || 0;
  }
  const save = () => lsSet(K(), JSON.stringify({ leaves, awayMs: Math.round(awayMs) }));
  function update() {
    const next = compute(); if (next === state) return;
    const t = now();
    if (state === "on") { leaves++; awaySince = t; }                                    // 이 화면에서 벗어남
    else if (next === "on") { awayMs += t - awaySince; awaySince = 0; }                // 돌아옴
    state = next; since = t; save(); subs.forEach(f => { try { f(state); } catch (e) {} });
  }
  ["visibilitychange", "blur", "focus"].forEach(ev => (ev === "visibilitychange" ? document : window).addEventListener(ev, update));
  StudentAuth.onChange(() => { load(); });
  /* 서버로 보낼 값(벗어나 있는 중이면 그 시간도 합계에 더한다) */
  const snapshot = () => ({ view: state, viewAt: since, leaves, awayMs: Math.round(awayMs + (state !== "on" && awaySince ? now() - awaySince : 0)) });
  return { snapshot, onChange: f => subs.push(f) };
})();
