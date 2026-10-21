<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>디자인 패턴 탐구 학습지</title>
<style>/*@STYLE@*/</style>
</head>
<body>
<header class="topbar">
  <h1>🔍 디자인 패턴 탐구 학습지</h1>
  <input class="id" id="f-class" placeholder="학급" aria-label="학급">
  <input class="id sm" id="f-num" placeholder="번호" aria-label="번호">
  <input class="id" id="f-name" placeholder="이름" aria-label="이름">
  <span class="grow"></span>
  <span class="savestate" id="savestate"></span>
  <button class="btn primary" id="btn-save" title="내 답을 JSON 파일로 내려받기">💾 저장</button>
  <button class="btn" id="btn-load" title="저장해 둔 JSON 파일(또는 선생님 코멘트가 담긴 파일) 불러오기">📂 불러오기</button>
  <button class="btn ghost" id="btn-print">🖨</button>
  <button class="btn ghost danger" id="btn-reset">초기화</button>
  <button class="btn ghost theme-toggle" title="밝게/어둡게">◐</button>
  <input type="file" id="file-in" accept=".json,application/json" hidden>
</header>
<nav class="tabs" id="tabs" role="tablist"></nav>
<main>
  <noscript>이 학습지는 JavaScript가 필요합니다.</noscript>
  <section id="week"></section>
</main>
<script>/*@CONTENT@*/</script>
<script>/*@CORE@*/</script>
<script>/*@APP@*/</script>
</body>
</html>
