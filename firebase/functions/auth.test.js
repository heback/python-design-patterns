"use strict";
const test = require("node:test");
const assert = require("node:assert");

test("isSchoolAccount: 학교 도메인 Google 계정만(확인된 이메일, 익명·외부 도메인 거부)", () => {
  const { isSchoolAccount } = require("./index")._test;
  const tok = (email, provider = "google.com", verified = true) => ({ token: { email, email_verified: verified, firebase: { sign_in_provider: provider } } });
  assert.equal(isSchoolAccount(tok("a@ts.hs.kr")), true);
  assert.equal(isSchoolAccount(tok("A@TS.HS.KR")), true);
  assert.equal(isSchoolAccount(tok("a@gmail.com")), false);
  assert.equal(isSchoolAccount(tok("a@evil.ts.hs.kr.com")), false);
  assert.equal(isSchoolAccount(tok("a@ts.hs.kr", "anonymous")), false);
  assert.equal(isSchoolAccount(tok("a@ts.hs.kr", "google.com", false)), false);
  assert.equal(isSchoolAccount(null), false);
  assert.equal(isSchoolAccount({ token: { firebase: { sign_in_provider: "anonymous" } } }), false);
});
