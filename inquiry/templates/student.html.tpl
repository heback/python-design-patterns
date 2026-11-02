<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>디자인 패턴 학습 관리</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+KR:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;700&family=Noto+Serif+KR:wght@600;700&display=swap">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@24,400,0..1,0&display=block">
<style>/*@STYLE@*/</style>
<style>/*@PYRUN_CSS@*/</style>
</head>
<body>
<header class="topbar">
  <h1><span class="ms" aria-hidden="true">menu_book</span>디자인 패턴 학습 관리</h1>
  <input class="id" id="f-num" placeholder="학번" aria-label="학번" inputmode="numeric">
  <input class="id" id="f-name" placeholder="성명" aria-label="성명">
  <span class="grow"></span>
  <span class="savestate" id="savestate"></span>
  <a class="btn ghost" href="https://heback.github.io/python-design-patterns/" target="_blank" rel="noopener" title="교재(GitHub Pages)를 새 창으로 열기"><span class="ms" aria-hidden="true">auto_stories</span>교재</a>
  <button class="btn ghost" id="btn-print" title="인쇄" aria-label="인쇄"><span class="ms" aria-hidden="true">print</span></button>
  <button class="btn ghost danger" id="btn-reset"><span class="ms" aria-hidden="true">restart_alt</span>초기화</button>
  <button class="btn ghost theme-toggle" title="밝게/어둡게" aria-label="밝게/어둡게"><span class="ms" aria-hidden="true">contrast</span></button>
</header>
<nav class="tabs" id="tabs" role="tablist"></nav>
<div class="monbar" id="monbar" hidden></div>
<main>
  <noscript>이 학습지는 JavaScript가 필요합니다.</noscript>
  <section id="week"></section>
</main>
<script>window.PYRUN_ICONS = true;</script>
<script>/*@PYHL@*/</script>
<script>/*@PYRUN@*/</script>
<script>/*@FB@*/</script>
<script>/*@CONTENT@*/</script>
<script>/*@CORE@*/</script>
<script>/*@MONITOR@*/</script>
<script>/*@APP@*/</script>
</body>
</html>
