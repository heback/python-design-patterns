"use strict";
/* 교재 사본(Firebase 호스팅) 전용: 교재 코드 편집기에서 학생이 단 주석·고친 코드를 서버(codeNotes)에도 저장한다.
   편집·자동 저장·복원은 textbook-code.js 가 하고(이 브라우저의 localStorage), 이 파일은 저장·불러오기·삭제 방법만 DPCode.attach 로 건네준다.
   StudentAuth.get() 은 학교 계정 로그인 + 현재 문구 동의가 모두 끝났을 때만 계정을 돌려주므로 그 전에는 서버로 아무것도 보내지 않는다.
   로그인·동의가 끝나면 DPCode.pull 이 서버 저장본과 이 브라우저의 것을 맞춘다(나중에 고친 쪽이 이김). 필요한 전역: DPCode(textbook-code.js), FB(fb.js), StudentAuth(student-auth.js). */
(function () {
  if (typeof DPCode === "undefined" || typeof FB === "undefined" || typeof StudentAuth === "undefined") return;
  DPCode.attach({
    active: () => !!StudentAuth.get(),
    load: () => FB.loadMyCode(),
    save: (bid, rec) => FB.saveCodeBlock(bid, rec),
    remove: bid => FB.deleteCodeBlock(bid),
  });
  StudentAuth.onChange(() => DPCode.pull());
})();
