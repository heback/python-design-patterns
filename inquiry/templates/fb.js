"use strict";
/* Firebase 어댑터(학생·교사 공용). 빌드에서 firebase-config.js가 있을 때만 포함된다.
   SDK는 고정 버전 CDN에서 필요할 때 불러온다. 모든 규칙 검사는 서버(firestore.rules, functions)가 한다. */
const FB = (() => {
  const VER = "11.10.0", BASE = `https://www.gstatic.com/firebasejs/${VER}/`;
  const REGION = window.FIREBASE_REGION || "asia-northeast3", DOMAIN = window.TEACHER_DOMAIN || "ts.hs.kr";
  const EMU = /[?&]emulator\b/.test(location.search);
  let M = null;
  const sid = st => [st.klass, st.number, st.name].map(safeName).filter(Boolean).join("_");

  async function load() {
    if (M) return M;
    const [app, auth, fs, fn] = await Promise.all(["app", "auth", "firestore", "functions"].map(n => import(`${BASE}firebase-${n}.js`)));
    const a = app.initializeApp(window.FIREBASE_CONFIG), au = auth.getAuth(a), db = fs.getFirestore(a), fx = fn.getFunctions(a, REGION);
    if (EMU) { auth.connectAuthEmulator(au, "http://localhost:9099", { disableWarnings: true }); fs.connectFirestoreEmulator(db, "localhost", 8080); fn.connectFunctionsEmulator(fx, "localhost", 5001); }
    return (M = { app, auth, fs, fn, au, db, fx });
  }

  /* ---------- 공통 ---------- */
  async function anon() {
    const m = await load(); await m.au.authStateReady();
    if (!m.au.currentUser) await m.auth.signInAnonymously(m.au);
    return m.au.currentUser;
  }
  const call = async (name, data) => { const m = await load(); return (await m.fn.httpsCallable(m.fx, name)(data)).data; };
  const fbErr = e => (e && (e.message || e.code)) || String(e);

  /* ---------- 진도 수집·돌발 퀴즈(학생) ---------- */
  /* 문서 하나를 실시간으로 구독한다. 문서가 없으면 null, 읽기에 실패하면 undefined 를 콜백에 준다. */
  async function watchDoc(col, id, cb) {
    const m = await load();
    return m.fs.onSnapshot(m.fs.doc(m.db, col, id), s => cb(s.exists() ? s.data() : null), () => cb(undefined));
  }
  const watchMonitor = cb => watchDoc("config", "monitor", cb);
  const watchQuiz = cb => watchDoc("config", "quiz", cb);
  /* 진도 한 번 전송. p = {weeks, activeMs, lastActiveAt(ms)}. 응답 본문은 보내지 않는다. */
  async function reportProgress(student, p) {
    const user = await anon(), m = await load(), { doc, setDoc, serverTimestamp, Timestamp } = m.fs;
    await setDoc(doc(m.db, "progress", sid(student)), {
      student: { klass: student.klass || "", number: student.number || "", name: student.name },
      uid: user.uid, weeks: p.weeks, activeMs: Math.round(p.activeMs), lastActiveAt: Timestamp.fromMillis(p.lastActiveAt), updatedAt: serverTimestamp() });
  }
  const answerQuiz = (student, quizId, choice) => call("answerQuiz", { quizId, sid: sid(student), choice });

  /* ---------- 진도·퀴즈 제어(교사) ---------- */
  async function watchProgress(cb) {
    const m = await load();
    return m.fs.onSnapshot(m.fs.collection(m.db, "progress"), snap => cb(snap.docs.map(d => Object.assign({ id: d.id }, d.data()))), e => cb(null, e));
  }
  async function watchQuizAnswers(quizId, cb) {
    const m = await load();
    return m.fs.onSnapshot(m.fs.collection(m.db, "quizResponses", quizId, "answers"), snap => cb(snap.docs.map(d => Object.assign({ id: d.id }, d.data()))), e => cb(null, e));
  }
  async function saveMonitor(on) {
    const m = await load();
    await m.fs.setDoc(m.fs.doc(m.db, "config", "monitor"), { on: !!on, updatedBy: m.au.currentUser.email, updatedAt: m.fs.Timestamp.now() });
  }
  /* cfg = {liveId, liveAt?, auto:{주차:bool}}. 즉시 출제를 새로 열 때는 liveAt 을 생략해 지금 시각이 찍히게 하면, 같은 퀴즈를 다시 열어도 학생 화면에 다시 뜬다.
     자동 모드만 바꿀 때는 기존 liveAt 을 그대로 넘겨 이미 닫은 학생에게 다시 뜨지 않게 한다. */
  async function saveQuizCfg(cfg) {
    const m = await load();
    await m.fs.setDoc(m.fs.doc(m.db, "config", "quiz"), { liveId: cfg.liveId || "", liveAt: cfg.liveAt || m.fs.Timestamp.now(), auto: cfg.auto || {}, updatedBy: m.au.currentUser.email });
  }
  async function loadQuizCfg() {
    const m = await load(), s = await m.fs.getDoc(m.fs.doc(m.db, "config", "quiz"));
    return s.exists() ? s.data() : { liveId: "", auto: {} };
  }
  async function resetQuizAnswers(quizId) {
    const m = await load(), { collection, getDocs, deleteDoc } = m.fs;
    const snap = await getDocs(collection(m.db, "quizResponses", quizId, "answers"));
    await Promise.all(snap.docs.map(d => deleteDoc(d.ref)));
    return snap.size;
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

  return { sid, domain: DOMAIN, fbErr,
           watchMonitor, watchQuiz, reportProgress, answerQuiz,
           watchProgress, watchQuizAnswers, saveMonitor, saveQuizCfg, loadQuizCfg, resetQuizAnswers, clearProgress,
           signIn, onAuth, signOut, teacherContent };
})();
