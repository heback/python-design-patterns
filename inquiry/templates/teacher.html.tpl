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
<div id="gate" class="gate" hidden>
  <h1><span class="ms" aria-hidden="true">school</span>디자인 패턴 학습 관리</h1>
  <p class="lead">학교 Google 계정으로 로그인한 교사만 사용할 수 있어요.</p>
  <button class="btn primary" id="btn-google" style="font-size:16px;padding:10px 18px">학교 Google 계정으로 로그인</button>
  <p class="err" id="gate-msg" role="alert"></p>
</div>
<div id="app">
<header class="topbar">
  <h1><span class="ms" aria-hidden="true">school</span>디자인 패턴 학습 관리</h1>
  <span class="grow"></span>
  <span class="lead" id="who" hidden></span>
  <a class="btn ghost" href="https://heback.github.io/python-design-patterns/" target="_blank" rel="noopener" title="교재(GitHub Pages)를 새 창으로 열기"><span class="ms" aria-hidden="true">auto_stories</span>교재</a>
  <button class="btn ghost" id="btn-logout" hidden><span class="ms" aria-hidden="true">logout</span>로그아웃</button>
  <button class="btn ghost theme-toggle" title="밝게/어둡게" aria-label="밝게/어둡게"><span class="ms" aria-hidden="true">contrast</span></button>
</header>
<main id="main" class="wide"></main>
</div>
<script>window.PYRUN_ICONS = true;</script>
<script>/*@PYHL@*/</script>
<script>/*@PYRUN@*/</script>
<script>/*@FB@*/</script>
<script>/*@CONTENT@*/</script>
<script>/*@CORE@*/</script>
<script>/*@APP@*/</script>
</body>
</html>
