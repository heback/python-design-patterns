<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>디자인 패턴 탐구 학습 · 교사용 가이드</title>
<style>/*@STYLE@*/</style>
<style>/*@PYRUN_CSS@*/</style>
</head>
<body>
<div id="gate" class="gate" hidden>
  <h1>🧑‍🏫 탐구 학습 교사용</h1>
  <p class="lead">학교 Google 계정으로 로그인한 교사만 사용할 수 있어요.</p>
  <button class="btn primary" id="btn-google" style="font-size:16px;padding:10px 18px">학교 Google 계정으로 로그인</button>
  <p class="err" id="gate-msg" role="alert"></p>
</div>
<div id="app">
<header class="topbar">
  <h1>🧑‍🏫 탐구 학습 교사용 가이드 · 코멘트</h1>
  <span class="grow"></span>
  <span class="lead" id="who" hidden></span>
  <button class="btn" id="btn-sync" hidden title="Firebase에 제출된 학생 응답·코멘트 가져오기">☁ 제출 불러오기</button>
  <button class="btn primary" id="btn-load">📂 학생 JSON 불러오기 (여러 개 선택 가능)</button>
  <button class="btn ghost" id="btn-print">🖨</button>
  <button class="btn ghost danger" id="btn-clear">불러온 데이터 지우기</button>
  <button class="btn ghost" id="btn-logout" hidden>로그아웃</button>
  <button class="btn ghost theme-toggle" title="밝게/어둡게">◐</button>
  <input type="file" id="file-in" accept=".json,application/json" multiple hidden>
</header>
<nav class="tabs" id="views" role="tablist"></nav>
<main id="main"></main>
</div>
<script>/*@PYHL@*/</script>
<script>/*@PYRUN@*/</script>
<script>/*@FB@*/</script>
<script>/*@CONTENT@*/</script>
<script>/*@CORE@*/</script>
<script>/*@APP@*/</script>
</body>
</html>
