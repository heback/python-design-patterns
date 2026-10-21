VERDICT: PASS

## 기계 검증
```

=== 장 05 ===
  OK   원고 05-adapter.html
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
  OK   05_adapter/01_naive.py: 모듈 docstring 있음
  OK   05_adapter/01_naive.py: 모든 클래스/함수에 docstring
  OK   05_adapter/01_naive.py: 주석 비율 31%
  OK   05_adapter/01_naive.py: __main__ 데모 있음
  OK   05_adapter/01_naive.py: 실행 성공
  OK   05_adapter/01_naive.py: 데모 출력 있음
  OK   05_adapter/01_naive.py: 원고에서 참조됨
  OK   05_adapter/02_adapter.py: 모듈 docstring 있음
  OK   05_adapter/02_adapter.py: 모든 클래스/함수에 docstring
  OK   05_adapter/02_adapter.py: 주석 비율 38%
  OK   05_adapter/02_adapter.py: __main__ 데모 있음
  OK   05_adapter/02_adapter.py: 실행 성공
  OK   05_adapter/02_adapter.py: 데모 출력 있음
  OK   05_adapter/02_adapter.py: 원고에서 참조됨
  OK   05_adapter/03_pythonic.py: 모듈 docstring 있음
  OK   05_adapter/03_pythonic.py: 모든 클래스/함수에 docstring
  OK   05_adapter/03_pythonic.py: 주석 비율 43%
  OK   05_adapter/03_pythonic.py: __main__ 데모 있음
  OK   05_adapter/03_pythonic.py: 실행 성공
  OK   05_adapter/03_pythonic.py: 데모 출력 있음
  OK   05_adapter/03_pythonic.py: 원고에서 참조됨
  OK   05_adapter/solutions/ex1_class_adapter.py: 모듈 docstring 있음
  OK   05_adapter/solutions/ex1_class_adapter.py: 모든 클래스/함수에 docstring
  OK   05_adapter/solutions/ex1_class_adapter.py: 주석 비율 42%
  OK   05_adapter/solutions/ex1_class_adapter.py: __main__ 데모 있음
  OK   05_adapter/solutions/ex1_class_adapter.py: 실행 성공
  OK   05_adapter/solutions/ex1_class_adapter.py: 데모 출력 있음
  OK   05_adapter/solutions/ex1_class_adapter.py: 원고에서 참조됨
  OK   05_adapter/solutions/ex2_thermometer.py: 모듈 docstring 있음
  OK   05_adapter/solutions/ex2_thermometer.py: 모든 클래스/함수에 docstring
  OK   05_adapter/solutions/ex2_thermometer.py: 주석 비율 50%
  OK   05_adapter/solutions/ex2_thermometer.py: __main__ 데모 있음
  OK   05_adapter/solutions/ex2_thermometer.py: 실행 성공
  OK   05_adapter/solutions/ex2_thermometer.py: 데모 출력 있음
  OK   05_adapter/solutions/ex2_thermometer.py: 원고에서 참조됨
  OK   05_adapter/solutions/ex3_rename_only.py: 모듈 docstring 있음
  OK   05_adapter/solutions/ex3_rename_only.py: 모든 클래스/함수에 docstring
  OK   05_adapter/solutions/ex3_rename_only.py: 주석 비율 48%
  OK   05_adapter/solutions/ex3_rename_only.py: __main__ 데모 있음
  OK   05_adapter/solutions/ex3_rename_only.py: 실행 성공
  OK   05_adapter/solutions/ex3_rename_only.py: 데모 출력 있음
  OK   05_adapter/solutions/ex3_rename_only.py: 원고에서 참조됨
  --> PASS (ok 55, warn 0, fail 0)

총 1장, 실패 0장 
```

## 의미 검증
data-run 대상 6개 실행 결과는 원고 설명과 일치한다. naive [3]에서는 15000 minor unit이 환불되고, 02 [1]에서는 1500000이 나가며, [2]의 세 거절은 PaymentDeclined로 수렴하고 A만 __cause__=PgAError다. ex1의 MRO 문자열도 원고와 같다. `data-lines` 94-133, 134-238, 239-283은 각각 Target, 어댑터, 클라이언트 구획을 정확히 잘라 낸다. 객체 어댑터가 Target을 구현하고 Adaptee를 합성하는 구조, 클래스 어댑터 비판, `__getattr__` 위임의 함정은 모두 정확하다.

- [권장] chapters/05-adapter.html #implementation 첫 lead-in, src/05_adapter/02_adapter.py:9 — 원고와 모듈 docstring은 "SDK 흉내 코드는 01과 같다"고 하지만, 같은 파일 22줄과 PgCClient(81-91줄)는 C SDK를 threading.Timer 기반의 다른 스레드 콜백으로 바꿨다. 두 곳 모두 "01과 같되 C는 실제처럼 다른 스레드에서 콜백한다"로 고칠 것.
- [권장] src/05_adapter/01_naive.py:79-91 및 124-130 — 원고 #context는 "C의 결과는 다른 스레드에서 온다"고 하는데, naive SDK는 콜백을 동기로 즉시 부른다. naive의 `box` 트릭은 동기 콜백이라서 동작하는 것이다. naive의 PgCClient docstring에 "단순화를 위해 콜백을 즉시 호출한다(실제로는 다른 스레드)"를 밝히거나, 그 트릭이 실제 비동기에서 깨진다는 ⚠ 주석을 추가할 것.
- [권장] src/05_adapter/02_adapter.py:220-222 — `fut.result(timeout=...)`의 TimeoutError가 번역되지 않고 그대로 새어 나간다. 이 장의 주제인 "예외 체계 번역"과 어긋난다. `except TimeoutError as e: raise PaymentDeclined("[C] 응답 시간 초과") from e`(또는 별도 도메인 예외)를 추가할 것.
- [권장] src/05_adapter/03_pythonic.py:151 — docstring은 "SDK가 던지는 아무 예외를"이라고 하지만 실제로는 ConnectionError와 TimeoutError만 잡는다. "통신 계열 예외(ConnectionError, TimeoutError)를"로 고칠 것.
- [권장] src/05_adapter/solutions/ex2_thermometer.py:67-81 — 문제 코드의 두 클라이언트 중 `max_celsius`가 해설에서 빠졌다. `def max_celsius(sensors): return max(s.get_celsius() for s in sensors)`를 추가해, 복제되던 분기가 두 곳 모두에서 사라졌음을 보일 것.
