VERDICT: PASS

## 기계 검증
```

=== 장 09 ===
  OK   원고 09-proxy.html
  OK   메타 주석(title) 있음
  OK   필수 섹션 모두 있음
  OK   섹션 순서 올바름
  OK   #context 에 코드 없음 (맥락만)
  OK   상황 설명이 첫 코드보다 앞
  OK   모든 본문 코드 앞에 lead-in 문단
  OK   코드 참조 5개 확인
  OK   #structure 에 SVG 다이어그램 있음
  OK   SVG 색 하드코딩 없음
  OK   연습문제 3개
  OK   모든 연습문제에 해설
  OK   코드 디렉터리 있음
  OK   09_proxy/01_naive.py: 모듈 docstring 있음
  OK   09_proxy/01_naive.py: 모든 클래스/함수에 docstring
  OK   09_proxy/01_naive.py: 주석 비율 37%
  OK   09_proxy/01_naive.py: __main__ 데모 있음
  OK   09_proxy/01_naive.py: 실행 성공
  OK   09_proxy/01_naive.py: 데모 출력 있음
  OK   09_proxy/01_naive.py: 원고에서 참조됨
  OK   09_proxy/02_proxy.py: 모듈 docstring 있음
  OK   09_proxy/02_proxy.py: 모든 클래스/함수에 docstring
  OK   09_proxy/02_proxy.py: 주석 비율 41%
  OK   09_proxy/02_proxy.py: __main__ 데모 있음
  OK   09_proxy/02_proxy.py: 실행 성공
  OK   09_proxy/02_proxy.py: 데모 출력 있음
  OK   09_proxy/02_proxy.py: 원고에서 참조됨
  OK   09_proxy/03_pythonic.py: 모듈 docstring 있음
  OK   09_proxy/03_pythonic.py: 모든 클래스/함수에 docstring
  OK   09_proxy/03_pythonic.py: 주석 비율 37%
  OK   09_proxy/03_pythonic.py: __main__ 데모 있음
  OK   09_proxy/03_pythonic.py: 실행 성공
  OK   09_proxy/03_pythonic.py: 데모 출력 있음
  OK   09_proxy/03_pythonic.py: 원고에서 참조됨
  OK   09_proxy/solutions/ex2_protection.py: 모듈 docstring 있음
  OK   09_proxy/solutions/ex2_protection.py: 모든 클래스/함수에 docstring
  OK   09_proxy/solutions/ex2_protection.py: 주석 비율 33%
  OK   09_proxy/solutions/ex2_protection.py: __main__ 데모 있음
  OK   09_proxy/solutions/ex2_protection.py: 실행 성공
  OK   09_proxy/solutions/ex2_protection.py: 데모 출력 있음
  OK   09_proxy/solutions/ex2_protection.py: 원고에서 참조됨
  OK   09_proxy/solutions/ex3_lazy_choice.py: 모듈 docstring 있음
  OK   09_proxy/solutions/ex3_lazy_choice.py: 모든 클래스/함수에 docstring
  OK   09_proxy/solutions/ex3_lazy_choice.py: 주석 비율 34%
  OK   09_proxy/solutions/ex3_lazy_choice.py: __main__ 데모 있음
  OK   09_proxy/solutions/ex3_lazy_choice.py: 실행 성공
  OK   09_proxy/solutions/ex3_lazy_choice.py: 데모 출력 있음
  OK   09_proxy/solutions/ex3_lazy_choice.py: 원고에서 참조됨
  --> PASS (ok 48, warn 0, fail 0)

총 1장, 실패 0장 
```

## 의미 검증 (재검증 2회차)

수정된 파일(03_pythonic.py, solutions/ex2_protection.py, solutions/ex3_lazy_choice.py, 원고)을 처음부터 다시 읽고 data-run 5개를 모두 다시 실행했다. 02_proxy.py는 바뀌지 않았으므로 data-lines 18-71, 72-131, 132-188, 189-222는 그대로 유효하다.

### 이전 지적 해소 여부
- [해소][필수] ex2 모듈 docstring(3-6줄)은 이제 문제 코드와 일치한다. update/delete에 검사를 복사했고, read는 "검사 없음"으로 허용을 표현했으며, export에서 복사가 빠졌다. "허용인지 누락인지 구분되지 않았다"는 해설의 핵심 관찰과도 맞는다.
- [해소] 기본 거부의 한계: 원고 해설(247줄)이 "기본 거부가 막는 것은 표 갱신 누락뿐이고, `_check()` 호출 누락은 별도로 막아야 한다"고 명시한다. 해설 코드는 두 가지 장치를 추가했다. `check_policy_complete()`는 Subject의 추상 메서드 ⊆ POLICY를 검사하고, 데모 [3]은 권한 없는 사용자로 모든 메서드를 호출한다. 실행 결과 셋 다 "거부됨"이다.
- [해소] 03_pythonic.py 데모 [1]에 `dem == dem._target()` → False가 추가되었다(110-111줄). 주석 "__eq__는 위임되지 않고 기본 동작(정체성 비교)이 쓰인다"는 정확하다. 이제 docstring 7줄의 "== 에서 샌다"를 데모가 보여 준다.
- [해소] ex3는 생성과 사용을 분리했다. [A]·[B] 모두 "생성 직후 로딩: []"를 먼저 출력하고, band(3) 뒤에 로딩 기록을 출력한다. 지연의 핵심이 출력으로 드러난다.
- [해소] LazyProxy는 `_UNSET = object()` 센티널을 쓴다(49, 54, 58줄). 주석으로 None을 쓰면 안 되는 이유도 밝혔다.

### 새 문제 검사
- 03 [1]~[4], ex2 [1]~[3], ex3 [A]~[C]의 출력이 원고 설명과 일치한다. [3]의 lru_cache 결과(hits=2, misses=4, 마지막 B 재다운로드)도 원고 서술과 같다.
- 새로 생긴 틀린 주석이나 원고-코드 불일치는 없다.
- [권장] src/09_proxy/solutions/ex2_protection.py:63 — "새 메서드를 추가할 때 표에 없으면 _check가 거부하므로 빠뜨림이 유출로 이어지지 않는다"에서 "빠뜨림"은 '표 갱신 누락'만 뜻한다. 그러나 바로 아래 check_policy_complete docstring(100-102줄)은 `_check` 호출 누락은 막지 못한다고 말하므로, 같은 파일 안에서 범위가 모호하게 읽힌다. → "표 갱신을 빠뜨려도 유출이 아니라 거부로 끝난다(단, _check 호출 자체의 누락은 아래 check_policy_complete와 데모 [3]으로 막는다)"로 한정할 것.
- [권장] src/09_proxy/solutions/ex2_protection.py:105 — 정책 완전성 검사를 `assert`로 한다. `python -O`로 실행하면 검사가 사라진다. 교재 데모로는 문제없지만, "실무에서는 이 순회를 테스트로 둔다"는 원고 문맥에 맞춰 주석 한 줄("운영 코드에서는 assert 대신 예외나 테스트로")을 달면 좋다.

필수 지적 없음.
