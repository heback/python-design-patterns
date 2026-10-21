VERDICT: PASS

## 기계 검증 (재검증)
```

=== 장 10 ===
  OK   원고 10-strategy.html
  OK   메타 주석(title) 있음
  OK   필수 섹션 모두 있음
  OK   섹션 순서 올바름
  OK   #context 에 코드 없음 (맥락만)
  OK   상황 설명이 첫 코드보다 앞
  OK   모든 본문 코드 앞에 lead-in 문단
  OK   코드 참조 6개 확인
  OK   #structure 에 SVG 다이어그램 있음
  OK   SVG 색 하드코딩 없음
  OK   연습문제 4개
  OK   모든 연습문제에 해설
  OK   코드 디렉터리 있음
  OK   10_strategy/01_naive.py: 모듈 docstring 있음
  OK   10_strategy/01_naive.py: 모든 클래스/함수에 docstring
  OK   10_strategy/01_naive.py: 주석 비율 34%
  OK   10_strategy/01_naive.py: __main__ 데모 있음
  OK   10_strategy/01_naive.py: 실행 성공
  OK   10_strategy/01_naive.py: 데모 출력 있음
  OK   10_strategy/01_naive.py: 원고에서 참조됨
  OK   10_strategy/02_strategy.py: 모듈 docstring 있음
  OK   10_strategy/02_strategy.py: 모든 클래스/함수에 docstring
  OK   10_strategy/02_strategy.py: 주석 비율 44%
  OK   10_strategy/02_strategy.py: __main__ 데모 있음
  OK   10_strategy/02_strategy.py: 실행 성공
  OK   10_strategy/02_strategy.py: 데모 출력 있음
  OK   10_strategy/02_strategy.py: 원고에서 참조됨
  OK   10_strategy/03_pythonic.py: 모듈 docstring 있음
  OK   10_strategy/03_pythonic.py: 모든 클래스/함수에 docstring
  OK   10_strategy/03_pythonic.py: 주석 비율 41%
  OK   10_strategy/03_pythonic.py: __main__ 데모 있음
  OK   10_strategy/03_pythonic.py: 실행 성공
  OK   10_strategy/03_pythonic.py: 데모 출력 있음
  OK   10_strategy/03_pythonic.py: 원고에서 참조됨
  OK   10_strategy/solutions/ex2_resize_registry.py: 모듈 docstring 있음
  OK   10_strategy/solutions/ex2_resize_registry.py: 모든 클래스/함수에 docstring
  OK   10_strategy/solutions/ex2_resize_registry.py: 주석 비율 34%
  OK   10_strategy/solutions/ex2_resize_registry.py: __main__ 데모 있음
  OK   10_strategy/solutions/ex2_resize_registry.py: 실행 성공
  OK   10_strategy/solutions/ex2_resize_registry.py: 데모 출력 있음
  OK   10_strategy/solutions/ex2_resize_registry.py: 원고에서 참조됨
  OK   10_strategy/solutions/ex3_sort_key.py: 모듈 docstring 있음
  OK   10_strategy/solutions/ex3_sort_key.py: 모든 클래스/함수에 docstring
  OK   10_strategy/solutions/ex3_sort_key.py: 주석 비율 40%
  OK   10_strategy/solutions/ex3_sort_key.py: __main__ 데모 있음
  OK   10_strategy/solutions/ex3_sort_key.py: 실행 성공
  OK   10_strategy/solutions/ex3_sort_key.py: 데모 출력 있음
  OK   10_strategy/solutions/ex3_sort_key.py: 원고에서 참조됨
  OK   10_strategy/solutions/ex4_surcharge_slot.py: 모듈 docstring 있음
  OK   10_strategy/solutions/ex4_surcharge_slot.py: 모든 클래스/함수에 docstring
  OK   10_strategy/solutions/ex4_surcharge_slot.py: 주석 비율 43%
  OK   10_strategy/solutions/ex4_surcharge_slot.py: __main__ 데모 있음
  OK   10_strategy/solutions/ex4_surcharge_slot.py: 실행 성공
  OK   10_strategy/solutions/ex4_surcharge_slot.py: 데모 출력 있음
  OK   10_strategy/solutions/ex4_surcharge_slot.py: 원고에서 참조됨
  --> PASS (ok 55, warn 0, fail 0)

총 1장, 실패 0장 
```

## 재검증: 이전 지적 해소 여부
- [필수→해소] src/10_strategy/solutions/ex2_resize_registry.py:63-64 — 틀린 docstring("함수 객체를 직접 받는 길") 삭제, "등록된 보간 함수(nearest, linear, box)는 모듈 함수로 남아 있어 직접 호출·단위 테스트할 수 있다"로 교체됨. 사실과 일치(nearest/linear/box는 모듈 함수). 실행 출력 변동 없음.
- [권장→해소] src/10_strategy/02_strategy.py:125 — 주석이 "심야 기준을 A안과 통일했다(구간제 실험의 대상은 요금표지 심야 기준이 아니므로)"로 바뀌어 코드와 일치.
- [권장→해소] chapters/10-strategy.html:115 — "추상 메서드는 calculate(q) 하나뿐이다(describe()는 로그용 기본 구현)"로 수정, 그림 10-1(60행) FeePolicy 박스에 `+ describe(): str` 추가됨.
- [권장→해소] src/10_strategy/01_naive.py:71-72 — "금액 차이(500 vs 1000)는 의도된 정책" / "심야 기준 차이는 의도인가 실수인가"로 구분됨.

## 데모 출력·data-lines 재대조
- 02_strategy.py 실행 출력 [1]~[6]이 이전 보고서 및 원고 설명과 동일.
- data-lines 경계(23-154, 157-200, 203-238)가 수정 후에도 구획 주석/블록 끝과 정확히 맞음(줄 수 변동 없음).

## 의미 검증
신규 지적 없음.
