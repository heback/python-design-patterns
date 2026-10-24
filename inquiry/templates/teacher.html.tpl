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
<header class="topbar">
  <h1>🧑‍🏫 탐구 학습 교사용 가이드 · 코멘트</h1>
  <span class="grow"></span>
  <button class="btn primary" id="btn-load">📂 학생 JSON 불러오기 (여러 개 선택 가능)</button>
  <button class="btn ghost" id="btn-print">🖨</button>
  <button class="btn ghost danger" id="btn-clear">불러온 데이터 지우기</button>
  <button class="btn ghost theme-toggle" title="밝게/어둡게">◐</button>
  <input type="file" id="file-in" accept=".json,application/json" multiple hidden>
</header>
<nav class="tabs" id="views" role="tablist"></nav>
<main id="main"></main>
<script>/*@PYHL@*/</script>
<script>/*@PYRUN@*/</script>
<script>/*@CONTENT@*/</script>
<script>/*@CORE@*/</script>
<script>/*@APP@*/</script>
</body>
</html>
