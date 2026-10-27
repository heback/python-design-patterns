"use strict";
/* Firebase 어댑터(학생·교사 공용). 빌드에서 firebase-config.js가 있을 때만 포함된다.
   SDK는 고정 버전 CDN에서 필요할 때 불러온다. 모든 규칙 검사는 서버(firestore.rules, functions)가 한다. */
const FB = (() => {
  const VER = "11.10.0", BASE = `https://www.gstatic.com/firebasejs/${VER}/`;
  const REGION = window.FIREBASE_REGION || "asia-northeast3", DOMAIN = window.TEACHER_DOMAIN || "ts.hs.kr";
  const EMU = /[?&]emulator\b/.test(location.search);
  let M = null;
  const sid = st => [st.klass, st.number, st.name].map(safeName).filter(Boolean).join("_");
  const wkOf = id => { const m = /^w(\d+)-/.exec(id); return m ? Number(m[1]) : 0; };

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

  /* ---------- 제출 설정 ---------- */
  async function watchSettings(cb) {
    const m = await load();
    return m.fs.onSnapshot(m.fs.doc(m.db, "config", "submission"), s => cb(s.exists() ? s.data() : null), () => cb(undefined));
  }
  async function loadSettings() {
    const m = await load(), s = await m.fs.getDoc(m.fs.doc(m.db, "config", "submission")), c = await m.fs.getDoc(m.fs.doc(m.db, "config", "submissionSecret"));
    return { settings: s.exists() ? s.data() : { open: false, weeks: {} }, code: c.exists() ? c.data().code || "" : "" };
  }
  async function saveSettings(st, code) {
    const m = await load(), { doc, setDoc, Timestamp } = m.fs, o = { open: !!st.open, weeks: st.weeks || {}, hasCode: !!code, updatedBy: m.au.currentUser.email, updatedAt: Timestamp.now() };
    if (st.opensAt) o.opensAt = Timestamp.fromDate(new Date(st.opensAt));
    if (st.closesAt) o.closesAt = Timestamp.fromDate(new Date(st.closesAt));
    await setDoc(doc(m.db, "config", "submissionSecret"), { code: code || "" });
    await setDoc(doc(m.db, "config", "submission"), o);
  }

  /* ---------- 학생 ---------- */
  async function submitWeek(S, n, code) {
    const user = await anon(), m = await load(), { doc, setDoc, serverTimestamp } = m.fs, id = sid(S.student);
    const answers = {}; Object.keys(S.answers).forEach(k => { if (wkOf(k) === n) answers[k] = S.answers[k]; });
    const head = { student: { klass: S.student.klass || "", number: S.student.number || "", name: S.student.name }, uid: user.uid, updatedAt: serverTimestamp() };
    const body = { json: JSON.stringify(answers), updatedAt: serverTimestamp() };
    if (code) { head.code = code; body.code = code; }
    await setDoc(doc(m.db, "submissions", id), head);
    await setDoc(doc(m.db, "submissions", id, "weeks", String(n)), body);
    return Object.keys(answers).length;
  }
  async function fetchPublished(student) {
    await anon(); const m = await load(), { collection, getDocs } = m.fs, out = {};
    (await getDocs(collection(m.db, "submissions", sid(student), "published"))).forEach(d => { out[d.id] = d.data(); });
    return out;
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
  const generate = (id, week) => call("generateFeedback", { submissionId: id, week });

  async function listSubmissions() {
    const m = await load(), { collection, getDocs } = m.fs, out = [];
    const subs = await getDocs(collection(m.db, "submissions"));
    for (const s of subs.docs) {
      const st = s.data().student || {}, answers = {}, feedback = {};
      let saved = null;
      const [wk, pub, dr] = await Promise.all(["weeks", "published", "drafts"].map(c => getDocs(collection(m.db, "submissions", s.id, c))));
      wk.forEach(d => { try { Object.assign(answers, JSON.parse(d.data().json)); } catch (e) {} const t = d.data().updatedAt; if (t && t.toDate && (!saved || t.toDate() > saved)) saved = t.toDate(); });
      dr.forEach(d => { feedback[d.id] = d.data(); });                       // 초안(ai:true)
      pub.forEach(d => { feedback[d.id] = Object.assign({}, d.data(), { ai: false, published: true }); });   // 공개본이 우선
      out.push({ app: "dp-inquiry", schema: 1, student: { klass: st.klass || "", number: st.number || "", name: st.name || "" }, saved: saved ? saved.toISOString() : null, answers, feedback });
    }
    return out;
  }
  async function publish(student, feedback) {
    const m = await load(), { doc, setDoc } = m.fs, id = sid(student); let n = 0;
    for (const [k, f] of Object.entries(feedback)) {
      if (!f || f.ai || !(f.comment || f.mark)) continue;     // 검수하지 않은 AI 초안은 공개하지 않는다
      await setDoc(doc(m.db, "submissions", id, "published", k), { mark: f.mark || null, comment: f.comment || "", at: f.at || new Date().toISOString() }); n++;
    }
    return n;
  }
  async function removeSubmission(student) {
    const m = await load(), { collection, getDocs, deleteDoc, doc } = m.fs, id = sid(student);
    for (const c of ["weeks", "drafts", "published"]) await Promise.all((await getDocs(collection(m.db, "submissions", id, c))).docs.map(d => deleteDoc(d.ref)));
    await deleteDoc(doc(m.db, "submissions", id));
  }

  return { sid, domain: DOMAIN, fbErr, watchSettings, loadSettings, saveSettings, submitWeek, fetchPublished,
           signIn, onAuth, signOut, teacherContent, generate, listSubmissions, publish, removeSubmission };
})();
