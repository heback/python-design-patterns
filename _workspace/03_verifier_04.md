VERDICT: PASS

## 기계 검증
```

=== 장 04 ===
  OK   원고 04-singleton.html
  OK   메타 주석(title) 있음
  OK   필수 섹션 모두 있음
  OK   섹션 순서 올바름
  OK   #context 에 코드 없음 (맥락만)
  OK   상황 설명이 첫 코드보다 앞
  OK   모든 본문 코드 앞에 lead-in 문단
  OK   코드 참조 6개 확인
  OK   #structure 에 SVG 다이어그램 있음
  OK   SVG 색 하드코딩 없음
  OK   연습문제 3개
  OK   모든 연습문제에 해설
  OK   코드 디렉터리 있음
  OK   04_singleton/01_naive.py: 모듈 docstring 있음
  OK   04_singleton/01_naive.py: 모든 클래스/함수에 docstring
  OK   04_singleton/01_naive.py: 주석 비율 38%
  OK   04_singleton/01_naive.py: __main__ 데모 있음
  OK   04_singleton/01_naive.py: 실행 성공
  OK   04_singleton/01_naive.py: 데모 출력 있음
  OK   04_singleton/01_naive.py: 원고에서 참조됨
  OK   04_singleton/02_singleton.py: 모듈 docstring 있음
  OK   04_singleton/02_singleton.py: 모든 클래스/함수에 docstring
  OK   04_singleton/02_singleton.py: 주석 비율 39%
  OK   04_singleton/02_singleton.py: __main__ 데모 있음
  OK   04_singleton/02_singleton.py: 실행 성공
  OK   04_singleton/02_singleton.py: 데모 출력 있음
  OK   04_singleton/02_singleton.py: 원고에서 참조됨
  OK   04_singleton/03_variants.py: 모듈 docstring 있음
  OK   04_singleton/03_variants.py: 모든 클래스/함수에 docstring
  OK   04_singleton/03_variants.py: 주석 비율 47%
  OK   04_singleton/03_variants.py: __main__ 데모 있음
  OK   04_singleton/03_variants.py: 실행 성공
  OK   04_singleton/03_variants.py: 데모 출력 있음
  OK   04_singleton/03_variants.py: 원고에서 참조됨
  OK   04_singleton/04_injection.py: 모듈 docstring 있음
  OK   04_singleton/04_injection.py: 모든 클래스/함수에 docstring
  OK   04_singleton/04_injection.py: 주석 비율 32%
  OK   04_singleton/04_injection.py: __main__ 데모 있음
  OK   04_singleton/04_injection.py: 실행 성공
  OK   04_singleton/04_injection.py: 데모 출력 있음
  OK   04_singleton/04_injection.py: 원고에서 참조됨
  OK   04_singleton/solutions/ex1_init_reset_bug.py: 모듈 docstring 있음
  OK   04_singleton/solutions/ex1_init_reset_bug.py: 모든 클래스/함수에 docstring
  OK   04_singleton/solutions/ex1_init_reset_bug.py: 주석 비율 38%
  OK   04_singleton/solutions/ex1_init_reset_bug.py: __main__ 데모 있음
  OK   04_singleton/solutions/ex1_init_reset_bug.py: 실행 성공
  OK   04_singleton/solutions/ex1_init_reset_bug.py: 데모 출력 있음
  OK   04_singleton/solutions/ex1_init_reset_bug.py: 원고에서 참조됨
  OK   04_singleton/solutions/ex2_config_injection.py: 모듈 docstring 있음
  OK   04_singleton/solutions/ex2_config_injection.py: 모든 클래스/함수에 docstring
  OK   04_singleton/solutions/ex2_config_injection.py: 주석 비율 40%
  OK   04_singleton/solutions/ex2_config_injection.py: __main__ 데모 있음
  OK   04_singleton/solutions/ex2_config_injection.py: 실행 성공
  OK   04_singleton/solutions/ex2_config_injection.py: 데모 출력 있음
  OK   04_singleton/solutions/ex2_config_injection.py: 원고에서 참조됨
  --> PASS (ok 55, warn 0, fail 0)

총 1장, 실패 0장 
```

## 의미 검증 (재검증 2회차)

수정된 파일(02_singleton.py, 03_variants.py, 원고)을 처음부터 다시 읽고 data-run 6개를 모두 다시 실행했다. 이 장은 data-lines를 쓰지 않는다. 03_variants.py를 20회 실행했고 출력 md5는 1종이었다(결정적).

### 이전 지적 해소 여부
- [해소][필수] Borg `__init__` 함정: 원고 표 Borg 행이 "있음(공유 dict에 `setdefault`로 회피)"으로 바뀌었다. 03_variants.py:124-125에 `self.entries = []`가 공유 기록을 지운다는 주석을 달았다. 데모 [3]에서 세 번째 `BorgLogger()`를 만든 뒤에도 `b3.entries → ['lab.lee 열람']`이 출력된다. 원고 118줄의 설명("데모의 세 번째 인스턴스가 기록을 그대로 보는 것으로 확인된다")이 실제 출력과 일치한다.
- [해소] count_instances는 객체 자체를 `seen`에 담고 `len({id(o) for o in seen})`로 센다(60-62, 74줄). 주석의 이유 설명도 정확하다.
- [해소] 161-162줄 주석이 "대개 8개 모두 따로 만들지만 보장은 아니므로 2개 이상인지만 본다"로 보강되었다.
- [해소] 병렬 실행 서술을 "스레드 기반 병렬"로 한정했다(원고 21·100줄, 02_singleton.py:98-99·160). 원고 100줄에 pytest-xdist의 경우(같은 워커 내 순서 의존)도 덧붙였다.
- [해소] 02_singleton.py:47-49 주석이 잠금의 두 용도와 비재진입 Lock의 교착 위험을 명시한다.

### 새 문제 검사
- 02 [1]~[3], 03 [1]~[4]의 출력이 원고 설명과 일치한다. 새로 추가된 Borg 데모 줄도 원고 서술과 맞는다.
- 새로 생긴 틀린 주석이나 원고-코드 불일치는 없다.

필수 지적 없음.
