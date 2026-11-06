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
  /* 이 화면의 장에서 남은 질문 수: {chapter, chapterTitle, limit, used, left} */
  const assistantQuota = chapter => call("getAssistantQuota", { chapter });

  /* ---------- 선생님께 질문(학생 ↔ 교사) ----------
     대화는 askThreads/{학생 uid}(요약·안 읽음 수)와 그 아래 msgs(한 건씩). 쓰기는 모두 함수가 하고 화면은 실시간으로 읽기만 한다(firestore.rules). */
  /* 질문 보내기. p = {text, image?:{mime,data}, context:{kind, chapter, title, selection}}. 개수 제한은 없다(서버가 1분에 10번까지만 받는다). */
  const askTeacher = p => call("askTeacher", p);
  /* 읽음 처리: 학생은 uid 없이(내 '새 답변' 배지), 교사는 학생 uid 를 주어(그 학생의 '새 질문' 배지) 부른다. */
  const markAskRead = uid => call("markAskRead", uid ? { uid } : {});
  const watchMyThread = (uid, cb) => watchDoc("askThreads", uid, cb);
  /* 한 학생 대화의 메시지를 오래된 순으로 실시간 구독(학생은 본인 것만, 교사는 누구 것이든). cb(rows) 또는 오류 시 cb(null, err). */
  async function watchAskMsgs(uid, cb) {
    const m = await load(), { collection, query, orderBy, onSnapshot } = m.fs;
    return onSnapshot(query(collection(m.db, "askThreads", uid, "msgs"), orderBy("at")), snap => cb(snap.docs.map(d => Object.assign({ id: d.id }, d.data()))), e => cb(null, e));
  }
  /* 교사: 모든 학생의 대화 목록(요약), 답변, AI 추천 답변, 대화 삭제, AI 추천 사용 집계 */
  const watchAskThreads = cb => live("askThreads", cb);
  const replyToStudent = (uid, text, viaAi) => call("replyToStudent", { uid, text, viaAi: !!viaAi });
  const suggestReply = uid => call("suggestReply", { uid });
  async function deleteAskThread(uid) {
    const m = await load(), { collection, getDocs, writeBatch, doc, limit, query } = m.fs;
    for (;;) {
      const snap = await getDocs(query(collection(m.db, "askThreads", uid, "msgs"), limit(200))); if (snap.empty) break;
      const b = writeBatch(m.db); snap.docs.forEach(d => b.delete(d.ref)); await b.commit();
    }
    await m.fs.deleteDoc(doc(m.db, "askThreads", uid));
  }
  async function watchAskStats(cb) { const m = await load(); return m.fs.onSnapshot(m.fs.doc(m.db, "stats", "askTeacher"), s => cb(s.exists() ? s.data() : null, null), e => cb(null, e)); }

  /* ---------- 교재 코드 편집기에서 학생이 단 주석·고친 코드(codeNotes) ----------
     학생: 내 블록 전부 읽기(loadMyCode), 블록 하나 저장(saveCodeBlock: 학생 요약 문서와 블록을 한 묶음으로 쓴다), 블록 삭제(처음 코드로 되돌렸을 때).
     교사: 학생 목록(watchCodeStudents)과 한 학생의 블록(loadStudentCode), 한 학생의 코드 기록 삭제(deleteStudentCode). 규칙이 서버에서 권한·모양·서버 시각을 강제한다. */
  async function loadMyCode() {
    const user = await schoolUser(), m = await load(), { collection, getDocs } = m.fs;
    const snap = await getDocs(collection(m.db, "codeNotes", user.uid, "blocks"));
    return Object.fromEntries(snap.docs.map(d => [d.id, d.data()]));
  }
  async function saveCodeBlock(bid, rec) {
    const user = await schoolUser(), m = await load(), { doc, writeBatch, serverTimestamp } = m.fs, w = who(user), b = writeBatch(m.db);
    b.set(doc(m.db, "codeNotes", user.uid), { uid: user.uid, student: { name: w.name.slice(0, 80), email: w.email }, updatedAt: serverTimestamp() });
    b.set(doc(m.db, "codeNotes", user.uid, "blocks", bid), { page: rec.page, kind: rec.kind, idx: rec.idx, title: String(rec.title || "").slice(0, 200), h: rec.h, code: rec.code, added: rec.added, addedN: rec.addedN, updatedAt: serverTimestamp() });
    await b.commit();
  }
  async function deleteCodeBlock(bid) {
    const user = await schoolUser(), m = await load();
    await m.fs.deleteDoc(m.fs.doc(m.db, "codeNotes", user.uid, "blocks", bid));
  }
  const watchCodeStudents = cb => live("codeNotes", cb);
  async function loadStudentCode(uid) {
    const m = await load(), snap = await m.fs.getDocs(m.fs.collection(m.db, "codeNotes", uid, "blocks"));
    return snap.docs.map(d => Object.assign({ id: d.id }, d.data()));
  }
  async function deleteStudentCode(uid) {
    const m = await load(), { collection, getDocs, writeBatch, doc, limit, query } = m.fs;
    for (;;) {
      const snap = await getDocs(query(collection(m.db, "codeNotes", uid, "blocks"), limit(200))); if (snap.empty) break;
      const b = writeBatch(m.db); snap.docs.forEach(d => b.delete(d.ref)); await b.commit();
    }
    await m.fs.deleteDoc(doc(m.db, "codeNotes", uid));
  }

  /* ---------- 개인정보 수집·이용 동의 ---------- */
  /* 내 동의 문서 구독: 문서가 없으면 null(동의한 적 없음·철회), 읽기에 실패하면 undefined(모름). 문서 모양은 firestore.rules 의 consentOk 가 강제한다. */
  const watchMyConsent = (uid, cb) => watchDoc("consents", uid, cb);
  /* 동의 저장. version = 동의한 문구의 버전, ai = 선택 항목(AI 도우미)에 동의했는지. 동의 일시는 서버 시각이다. */
  async function saveConsent(version, ai) {
    const user = await schoolUser(), m = await load(), { doc, setDoc, serverTimestamp } = m.fs, w = who(user);
    await setDoc(doc(m.db, "consents", user.uid), { uid: user.uid, student: { name: w.name.slice(0, 80), email: w.email }, version, ai: !!ai, agreedAt: serverTimestamp() });
  }
  /* 동의 초기화(교사만 — 규칙): 그 학생의 동의 문서를 지운다. 학생은 다음에 화면을 열 때(열어 둔 화면은 곧바로) 다시 동의해야 하고, 그 전까지 진도·AI 질문이 막힌다. 학생은 스스로 철회할 수 없다(선택 항목 ai 를 false → true 로 바꾸는 동의만 saveConsent 로 직접 할 수 있다). */
  async function resetConsent(uid) {
    const m = await load();
    await m.fs.deleteDoc(m.fs.doc(m.db, "consents", uid));
  }

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

  /* 내 진도 문서 한 번 읽기(없으면 null). 기기를 바꾸거나 기록이 지워져도 값이 줄지 않게, 보내기 전에 서버의 값과 비교해 큰 쪽을 쓴다. */
  async function readMyProgress() {
    const u = await schoolUser(), m = await load(), s = await m.fs.getDoc(m.fs.doc(m.db, "progress", u.uid));
    return s.exists() ? s.data() : null;
  }

  /* ---------- 진도 제어(교사) ---------- */
  async function watchProgress(cb) {
    const m = await load();
    return m.fs.onSnapshot(m.fs.collection(m.db, "progress"), snap => cb(snap.docs.map(d => Object.assign({ id: d.id }, d.data()))), e => cb(null, e));
  }
  /* 켜기/끄기는 서버 함수가 한다: 스위치와 변경 이력(monitorEvents)을 서버 시각으로 함께 쓰고, 클라이언트는 직접 쓰지 못한다. */
  const saveMonitor = on => call("setMonitor", { on: !!on });
  const watchMonitorEvents = cb => live("monitorEvents", cb, m => m.fs.query(m.fs.collection(m.db, "monitorEvents"), m.fs.orderBy("at", "desc"), m.fs.limit(30)));
  /* 켜기/끄기와 기본 한도(limit)는 같은 문서(config/assistant)에 있으므로 merge 로 써서 서로 지우지 않는다. */
  async function saveAssistant(on) {
    const m = await load();
    await m.fs.setDoc(m.fs.doc(m.db, "config", "assistant"), { on: !!on, updatedBy: m.au.currentUser.email, updatedAt: m.fs.Timestamp.now() }, { merge: true });
  }
  /* 장별 기본 질문 한도(학생 한 명이 장 하나에서). 서버가 0~1000 의 정수가 아니면 기본값(40)으로 본다. */
  async function saveAssistantLimit(n) {
    const m = await load();
    await m.fs.setDoc(m.fs.doc(m.db, "config", "assistant"), { limit: n, limitBy: m.au.currentUser.email, limitAt: m.fs.Timestamp.now() }, { merge: true });
  }
  /* 학생·장별 한도 가감: chapter 는 "all"(모든 장) 또는 장 키, value 는 기본 한도에 더할 값(0 이면 가감 없음). 함수가 교사를 확인하고 쓴다. */
  const setAssistantQuota = (uid, chapter, value) => call("setAssistantQuota", { uid, chapter, value });
  /* AI 도우미 기록·집계(교사). 함수가 쓰고 교사만 읽는다. */
  const live = (col, cb, q) => load().then(m => m.fs.onSnapshot(q ? q(m) : m.fs.collection(m.db, col), snap => cb(snap.docs.map(d => Object.assign({ id: d.id }, d.data()))), e => cb(null, e)));
  const watchConsents = cb => live("consents", cb);           // 학생들의 개인정보 동의 기록(교사)
  const watchChatUsage = cb => live("chatUsage", cb);
  const watchChatQuota = cb => live("chatQuota", cb);
  const watchChatLogs = (cb, n) => live("chatLogs", cb, m => m.fs.query(m.fs.collection(m.db, "chatLogs"), m.fs.orderBy("at", "desc"), m.fs.limit(n || 200)));
  async function watchStats(cb) { const m = await load(); return m.fs.onSnapshot(m.fs.doc(m.db, "stats", "assistant"), s => cb(s.exists() ? s.data() : null, null), e => cb(null, e)); }
  /* 대화 기록 한 쪽. o = {uid?, kind: all|refused|error|image, size, after?(앞 쪽의 마지막 문서)}. 서버 쿼리로 거르고 커서로 넘긴다.
     반환 {rows, last, more}: more 는 다음 쪽이 있는지(size+1 건을 읽어 알아낸다). 필터 조합마다 복합 색인이 필요하다(firestore.indexes.json). */
  function chatLogQuery(m, o) {
    const { collection, query, where } = m.fs, cs = [];
    if (o.uid) cs.push(where("uid", "==", o.uid));
    if (o.kind === "refused") cs.push(where("refused", "==", true));
    else if (o.kind === "error") cs.push(where("failed", "==", true));
    else if (o.kind === "image") cs.push(where("hasImage", "==", true));
    return { cs, col: collection(m.db, "chatLogs"), query };
  }
  async function chatLogsPage(o) {
    const m = await load(), { orderBy, limit, startAfter, getDocs } = m.fs, q = chatLogQuery(m, o), size = o.size || 20;
    const extra = [orderBy("at", "desc")]; if (o.after) extra.push(startAfter(o.after)); extra.push(limit(size + 1));
    const docs = (await getDocs(q.query(q.col, ...q.cs, ...extra))).docs, page = docs.slice(0, size);
    return { rows: page.map(d => Object.assign({ id: d.id }, d.data())), last: page.length ? page[page.length - 1] : null, more: docs.length > size };
  }
  /* 같은 조건의 전체 건수(서버 집계, 문서를 내려받지 않는다). 실패하면 null. */
  async function chatLogsCount(o) {
    try { const m = await load(), q = chatLogQuery(m, o); return (await m.fs.getCountFromServer(q.query(q.col, ...q.cs))).data().count; } catch (e) { return null; }
  }
  /* 모든 대화 기록 삭제(교사만 — 규칙). 많을 수 있으므로 400건씩 묶어서 지운다. */
  async function clearChatLogs() {
    const m = await load(), { collection, query, limit, getDocs, writeBatch } = m.fs; let n = 0;
    for (;;) {
      const snap = await getDocs(query(collection(m.db, "chatLogs"), limit(400))); if (snap.empty) break;
      const b = writeBatch(m.db); snap.docs.forEach(d => b.delete(d.ref)); await b.commit(); n += snap.size;
    }
    return n;
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
           watchMyConsent, saveConsent, resetConsent, watchConsents,
           watchMonitor, reportProgress, readMyProgress, watchAssistant, askAssistant, assistantQuota, saveAssistant, saveAssistantLimit, setAssistantQuota, watchChatUsage, watchChatQuota, watchChatLogs, chatLogsPage, chatLogsCount, watchStats, clearChatLogs,
           askTeacher, markAskRead, watchMyThread, watchAskMsgs, watchAskThreads, replyToStudent, suggestReply, deleteAskThread, watchAskStats,
           loadMyCode, saveCodeBlock, deleteCodeBlock, watchCodeStudents, loadStudentCode, deleteStudentCode,
           watchProgress, saveMonitor, watchMonitorEvents, clearProgress,
           signIn, onAuth, signOut, teacherContent };
})();
