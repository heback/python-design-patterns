"use strict";
/* 학생 로그인(학교 Google 계정). 학습지와 교재 사본이 같은 주소라 한 번 로그인하면 두 화면이 함께 쓴다.
   진도 전달은 로그인한 학교 계정이 있어야 한다. 서버 규칙(firestore.rules)이 도메인과 uid 를 다시 확인한다.
   필요한 전역: FB(fb.js). */
const StudentAuth = (() => {
  let user = null; const subs = [];
  const mine = u => (u && !u.isAnonymous && (u.email || "").toLowerCase().endsWith("@" + FB.domain)) ? u : null;
  const notify = () => subs.forEach(f => { try { f(user); } catch (e) {} });
  async function init() {
    try { user = mine(await FB.currentUser()); } catch (e) { user = null; }
    notify();
    FB.onAuth(u => { user = mine(u); notify(); }).catch(() => {});
  }
  /* 로그인 창을 띄운다. 학교 계정이 아니면 바로 로그아웃하고 이유를 돌려준다. 성공하면 null, 실패하면 안내 문장. */
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
  const key = base => base + "-" + (user ? user.uid : "anon");
  return { init, login, logout: () => FB.signOut(), get: () => user, key, onChange: f => subs.push(f) };
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
