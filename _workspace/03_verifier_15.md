VERDICT: PASS

(재검증, 2026-10-08. 이전 보고서의 필수 1건과 권장 6건을 항목별로 확인했다. 수정된 파일 4개(chapters/15-iterator.html, 02_iterator.py, 03_pythonic.py, solutions/ex4_smart_shuffle.py)는 처음부터 다시 읽었다.)

## 기계 검증
```
=== 장 15 ===
  OK   원고 15-iterator.html
  OK   메타 주석(title) 있음
  OK   필수 섹션 모두 있음
  OK   섹션 순서 올바름
  OK   #context 에 코드 없음 (맥락만)
  OK   상황 설명이 첫 코드보다 앞
  OK   모든 본문 코드 앞에 lead-in 문단
  OK   코드 참조 7개 확인
  OK   #structure 에 SVG 다이어그램 있음
  OK   SVG 색 하드코딩 없음
  OK   연습문제 4개
  OK   모든 연습문제에 해설
  OK   코드 디렉터리 있음
  OK   (01_naive / 02_iterator / 03_pythonic / 04_lazy_pagination /
        solutions/ex1_iter_returns_self / ex2_page_token_generator / ex4_smart_shuffle 각각:
        docstring · 주석 비율(30/34/38/39/37/32/37%) · __main__ · 실행 성공 · 출력 · 원고 참조 모두 OK)
  --> PASS (ok 62, warn 0, fail 0)

총 1장, 실패 0장
```

## 이전 지적 해소 확인

### [필수] ex4 해설 코드가 03의 MODES 계약을 따르지 않음 → 해소
- **계약 준수**: `smart_shuffle(pl, start=0, seed=None) -> Iterator[tuple[int, Track]]`(49-66행)는 첫 값으로 `(start, pl[start])`를 내고(52행), 이후 `(i, pl[i])` 쌍을 낸다. 03의 `sequential`/`shuffled`와 같은 모양이다.
- **실제 03에 꽂아 보기**(scratchpad/p03_default.py): 03_pythonic.py 사본에 ① `Track.artist` 추가, ② `MODES["smart_shuffle"] = partial(smart_shuffle, seed=5)` 한 줄만 넣었다. `Player`와 `Playlist`는 손대지 않았다. 그 상태에서 `set_mode("smart_shuffle")`는 지금 곡(잔나비)을 유지하고 `['아이유','새소년','아이유','잔나비','아이유']`(연속 0회)를 냈다. 이어서 `set_mode("repeat_all")`도 smart_shuffle이 넘긴 위치(아이유-4)에서 이어 갔다. 03의 `set_mode`는 `"shuffle"`이 아닌 이름에 `MODES[mode]`를 쓰므로(96행), partial로 seed를 묶으면 특수 처리를 추가할 필요가 없다. 원고 232행의 "③ … MODES 값에 partial(smart_shuffle, seed=...)을 넣는다", "재생 로직과 Playlist는 고치지 않는다"는 사실이다.
- **알고리즘 주장**(docstring 23-24행, "시작 곡이 정해진 조건에서 가능한 최소 연속 횟수"): 직접 전수 탐색과 대조했다(scratchpad/t15opt.py). 1-8곡, 아티스트 1-3명, 무작위 3,000건에서 불일치 0건이었다. 데모 출력(seed 100개 중 평범한 셔플 87, 스마트 셔플 0)은 원고 설명과 일치한다.

### [권장] 탐욕 선택이 피할 수 있는 연속을 만듦 → 해소
과반 아티스트 우선 규칙(57-60행)이 추가되었고, 위 전수 탐색으로 최적임을 확인했다.

### [권장] 03 up_next가 모드와 무관하게 순서대로 미리 봄 → 해소
03 docstring 113-114행과 원고 [3] 항목에 "'순서대로' 모드 기준, tee/peek 필요"라는 한계가 명시되었다.

### [권장] 02 [2] '미리보기' 레이블 → 해소
190행이 "다른 화면의 독립 순회(앨범 앞 3곡)"로 바뀌었다. 원고 103행에 '다음 곡부터' 미리 보는 방법이 괄호로 보충되었다.

### [권장] RepeatOneIterator 빈 목록, set_mode의 StopIteration 누출 → 해소
92-95행에 가드가 생겼고, 170행은 `next(new_it, None)`을 쓴다. 단, 같은 문제가 ShuffleIterator에 남아 있다(아래 새 지적).

### [권장] '제너레이터 상태는 바깥에서 읽을 수 없다' 과장 → 해소
"공개 인터페이스로는 … 읽을 수 없다(gi_frame 같은 디버깅용 내부 속성은 예외)"로 완화되었다. 설계 선택지 표도 "공개 인터페이스로 읽을 수 없다"로 맞췄다.

### [권장] PEP 479 안내 → 해소
5.1절 첫 문단에 "`raise StopIteration` → RuntimeError, 제너레이터는 `return`으로 끝낸다"가 추가되었다.

## 데모 출력 대조 (Python 3.13.7)
- 02: [1] 두 번 순회 동일, [2] 독립 순회 뒤에도 재생 중 Intro, [3] 셔플 Blue → ['Outro','Run'], 전체 반복 Run → …, [4] Run×3 / Echo부터 ['Echo','Outro'] / StopIteration. 원고 103-104행과 일치한다.
- 03: [2]가 02와 같은 순서, [3] ['친구가 추천한 곡','Blue','Run'] / 재생 중 Intro, [4] A1 A2 D1 D2, [5] 두 번째 순회 []. 원고 [2]-[5] 항목과 일치한다.
- ex4: [1] shuffle 연속 2회, smart_shuffle 연속 0회(둘 다 지금 곡 잔나비 유지), [2] 87/100 vs 0/100. 원고와 일치한다.

## 의미 검증 지적 (새로 찾은 것)
- [권장] chapters/15-iterator.html:232, src/15_iterator/solutions/ex4_smart_shuffle.py:13 — "① 03의 Track에 artist 필드를 추가한다"를 ex4처럼 기본값 없는 필드(`artist: str`)로 하면, 03의 기존 생성 코드 `Track(t)`, `Track("Run")`, `Track("친구가 추천한 곡")`, `Track("A1")` 등이 모두 TypeError로 깨진다(scratchpad/p03_required.py에서 확인: `Track.__init__() missing 1 required positional argument: 'artist'`). "고칠 곳은 정확히 세 가지"가 문자 그대로는 성립하지 않는다. → ①을 "`artist: str = \"\"`처럼 기본값을 두어 추가한다(기존 생성 코드는 그대로)"로 고친다.
- [권장] chapters/15-iterator.html:232, ex4_smart_shuffle.py:10, 79-96 — "03의 Player와 MODES를 같은 모양으로 재현"이라고 했다. 그런데 해설 코드의 재현본은 `"shuffle"`도 partial로 MODES에 넣고, `set_mode`에서 shuffle 특수 처리를 없앴다("모드 종류를 모른다", 94행). 03의 `set_mode`는 shuffle을 아는 상태다. 결론(등록 한 줄로 동작)은 03 원본에서도 성립함을 확인했으므로 동작상 문제는 없다. 하지만 '같은 모양'은 아니다. → "03을 축약하되 shuffle 특수 처리는 partial 등록으로 대체했다"고 밝힌다.
- [권장] src/15_iterator/02_iterator.py:105-119 — RepeatOne에 넣은 빈 목록 가드가 ShuffleIterator에는 없다. 빈 플레이리스트에서 `_order = [0]`이 되어 첫 `next()`에서 `IndexError: tuple index out of range`가 난다(실험: `Player(Playlist([])).set_mode("shuffle")`; normal/repeat_all/repeat_one은 None으로 정상 처리). → 생성자에서 `self._order = [start] + rest if len(playlist) else []`로 바꾼다.
