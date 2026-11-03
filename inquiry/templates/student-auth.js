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
