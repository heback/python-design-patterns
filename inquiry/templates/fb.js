"use strict";
/* Firebase 어댑터(학생·교사 공용). 빌드에서 firebase-config.js가 있을 때만 포함된다.
   SDK는 고정 버전 CDN에서 필요할 때 불러온다. 모든 규칙 검사는 서버(firestore.rules, functions)가 한다. */
const FB = (() => {
  const VER = "11.10.0", BASE = `https://www.gstatic.com/firebasejs/${VER}/`;
  const REGION = window.FIREBASE_REGION || "asia-northeast3", DOMAIN = window.TEACHER_DOMAIN || "ts.hs.kr";
  const EMU = /[?&]emulator\b/.test(location.search);
  let M = null;
  /* 학생 식별은 로그인 계정으로만 한다: 진도 문서 ID = uid, 이름 = 계정 이름(없으면 이메일 앞부분), 이메일 = 계정 이메일 */
  const who = u => ({ name: ((u.displayName || "").trim() || (u.email || "").split("@")[0]), email: (u.email || "").toLowerCase() });

  async function load() {
    if (M) return M;
    const [app, auth, fs, fn] = await Promise.all(["app", "auth", "firestore", "functions"].map(n => import(`${BASE}firebase-${n}.js`)));
    const a = app.initializeApp(window.FIREBASE_CONFIG), au = auth.getAuth(a), db = fs.getFirestore(a), fx = fn.getFunctions(a, REGION);
    if (EMU) { auth.connectAuthEmulator(au, "http://localhost:9099", { disableWarnings: true }); fs.connectFirestoreEmulator(db, "localhost", 8080); fn.connectFunctionsEmulator(fx, "localhost", 5001); }
    return (M = { app, auth, fs, fn, au, db, fx });
  }

  /* ---------- 공통 ---------- */
  /* 지금 로그인한 학교 Google 계정(없으면 null). 학생·교사 모두 같은 로그인을 쓴다. */
  async function currentUser() {
    const m = await load(); await m.au.authStateReady();
    const u = m.au.currentUser; return u && !u.isAnonymous ? u : null;
  }
  async function schoolUser() {
    const u = await currentUser();
    if (!u) { const e = new Error("학교 Google 계정으로 로그인해야 합니다."); e.code = "auth/login-required"; throw e; }
    return u;
  }
  const call = async (name, data) => { const m = await load(); return (await m.fn.httpsCallable(m.fx, name)(data)).data; };
  const fbErr = e => (e && (e.message || e.code)) || String(e);

  /* ---------- 학생 AI 도우미 ---------- */
  const watchAssistant = cb => watchDoc("config", "assistant", cb);
  const askAssistant = p => call("askAssistant", p);

  /* ---------- 진도 수집(학생) ---------- */
  /* 문서 하나를 실시간으로 구독한다. 문서가 없으면 null, 읽기에 실패하면 undefined 를 콜백에 준다. */
  async function watchDoc(col, id, cb) {
    const m = await load();
    return m.fs.onSnapshot(m.fs.doc(m.db, col, id), s => cb(s.exists() ? s.data() : null), () => cb(undefined));
  }
  const watchMonitor = cb => watchDoc("config", "monitor", cb);
  /* 진도 한 번 전송. p = {weeks?, chapters?, where?, focus?, activeMs, lastActiveAt(ms)}. 응답 본문은 보내지 않는다.
     학습지는 weeks 를, 교재 페이지는 chapters 를 보낸다. merge 로 쓰므로 서로의 필드를 덮어쓰지 않는다. */
  async function reportProgress(p) {
    const user = await schoolUser(), m = await load(), { doc, setDoc, serverTimestamp, Timestamp } = m.fs;
    const d = { student: who(user),
      uid: user.uid, activeMs: Math.round(p.activeMs), lastActiveAt: Timestamp.fromMillis(p.lastActiveAt), updatedAt: serverTimestamp() };
    if (p.weeks) d.weeks = p.weeks;
    if (p.chapters) d.chapters = p.chapters;
    if (p.where) d.where = String(p.where).slice(0, 80);
    if (p.focus) Object.assign(d, { view: p.focus.view, viewAt: Timestamp.fromMillis(p.focus.viewAt), leaves: p.focus.leaves, awayMs: p.focus.awayMs });   // 화면을 보고 있는지(student-auth.js FocusTrack)
    await setDoc(doc(m.db, "progress", user.uid), d, { merge: true });
  }

  /* ---------- 진도 제어(교사) ---------- */
  async function watchProgress(cb) {
    const m = await load();
    return m.fs.onSnapshot(m.fs.collection(m.db, "progress"), snap => cb(snap.docs.map(d => Object.assign({ id: d.id }, d.data()))), e => cb(null, e));
  }
  async function saveMonitor(on) {
    const m = await load();
    await m.fs.setDoc(m.fs.doc(m.db, "config", "monitor"), { on: !!on, updatedBy: m.au.currentUser.email, updatedAt: m.fs.Timestamp.now() });
  }
  async function saveAssistant(on) {
    const m = await load();
    await m.fs.setDoc(m.fs.doc(m.db, "config", "assistant"), { on: !!on, updatedBy: m.au.currentUser.email, updatedAt: m.fs.Timestamp.now() });
  }
  async function clearProgress() {
    const m = await load(), { collection, getDocs, deleteDoc } = m.fs;
    const snap = await getDocs(collection(m.db, "progress"));
    await Promise.all(snap.docs.map(d => deleteDoc(d.ref)));
    return snap.size;
  }

  /* ---------- 교사 ---------- */
  async function signIn() {
    const m = await load(), p = new m.auth.GoogleAuthProvider();
    p.setCustomParameters({ hd: DOMAIN, prompt: "select_account" });
    return m.auth.signInWithPopup(m.au, p);
  }
  async function onAuth(cb) { const m = await load(); return m.auth.onAuthStateChanged(m.au, cb); }
  async function signOut() { const m = await load(); return m.auth.signOut(m.au); }
  const teacherContent = () => call("getTeacherContent", {});

  return { who, domain: DOMAIN, fbErr, currentUser,
           watchMonitor, reportProgress, watchAssistant, askAssistant, saveAssistant,
           watchProgress, saveMonitor, clearProgress,
           signIn, onAuth, signOut, teacherContent };
})();
