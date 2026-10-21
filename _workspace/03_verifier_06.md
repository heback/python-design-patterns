VERDICT: PASS

## 기계 검증
```

=== 장 06 ===
  OK   원고 06-decorator.html
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
  OK   06_decorator/01_naive.py: 모듈 docstring 있음
  OK   06_decorator/01_naive.py: 모든 클래스/함수에 docstring
  OK   06_decorator/01_naive.py: 주석 비율 38%
  OK   06_decorator/01_naive.py: __main__ 데모 있음
  OK   06_decorator/01_naive.py: 실행 성공
  OK   06_decorator/01_naive.py: 데모 출력 있음
  OK   06_decorator/01_naive.py: 원고에서 참조됨
  OK   06_decorator/02_decorator.py: 모듈 docstring 있음
  OK   06_decorator/02_decorator.py: 모든 클래스/함수에 docstring
  OK   06_decorator/02_decorator.py: 주석 비율 38%
  OK   06_decorator/02_decorator.py: __main__ 데모 있음
  OK   06_decorator/02_decorator.py: 실행 성공
  OK   06_decorator/02_decorator.py: 데모 출력 있음
  OK   06_decorator/02_decorator.py: 원고에서 참조됨
  OK   06_decorator/03_pythonic.py: 모듈 docstring 있음
  OK   06_decorator/03_pythonic.py: 모든 클래스/함수에 docstring
  OK   06_decorator/03_pythonic.py: 주석 비율 38%
  OK   06_decorator/03_pythonic.py: __main__ 데모 있음
  OK   06_decorator/03_pythonic.py: 실행 성공
  OK   06_decorator/03_pythonic.py: 데모 출력 있음
  OK   06_decorator/03_pythonic.py: 원고에서 참조됨
  OK   06_decorator/solutions/ex1_order.py: 모듈 docstring 있음
  OK   06_decorator/solutions/ex1_order.py: 모든 클래스/함수에 docstring
  OK   06_decorator/solutions/ex1_order.py: 주석 비율 32%
  OK   06_decorator/solutions/ex1_order.py: __main__ 데모 있음
  OK   06_decorator/solutions/ex1_order.py: 실행 성공
  OK   06_decorator/solutions/ex1_order.py: 데모 출력 있음
  OK   06_decorator/solutions/ex1_order.py: 원고에서 참조됨
  OK   06_decorator/solutions/ex2_notifier.py: 모듈 docstring 있음
  OK   06_decorator/solutions/ex2_notifier.py: 모든 클래스/함수에 docstring
  OK   06_decorator/solutions/ex2_notifier.py: 주석 비율 31%
  OK   06_decorator/solutions/ex2_notifier.py: __main__ 데모 있음
  OK   06_decorator/solutions/ex2_notifier.py: 실행 성공
  OK   06_decorator/solutions/ex2_notifier.py: 데모 출력 있음
  OK   06_decorator/solutions/ex2_notifier.py: 원고에서 참조됨
  OK   06_decorator/solutions/ex3_auth.py: 모듈 docstring 있음
  OK   06_decorator/solutions/ex3_auth.py: 모든 클래스/함수에 docstring
  OK   06_decorator/solutions/ex3_auth.py: 주석 비율 36%
  OK   06_decorator/solutions/ex3_auth.py: __main__ 데모 있음
  OK   06_decorator/solutions/ex3_auth.py: 실행 성공
  OK   06_decorator/solutions/ex3_auth.py: 데모 출력 있음
  OK   06_decorator/solutions/ex3_auth.py: 원고에서 참조됨
  --> PASS (ok 55, warn 0, fail 0)

총 1장, 실패 0장 
```

## 의미 검증
data-run 대상 6개 실행 결과는 원고 설명과 일치한다. 02 [1]에서는 25건이 10+10+5로 나뉘고 로그가 629/104바이트를 찍는다. [3]은 104 대 640바이트(원본 629)이고, ex1은 103%, 03 [4]에서는 len/with/isinstance가 실패한다. `data-lines`(02: 27-81, 82-151, 152-192 / 03: 1-69, 70-105, 106-124, 125-214)도 원고가 설명하는 구획과 맞는다. ChannelDecorator는 같은 인터페이스를 유지하며(is-a + has-a) 중첩이 가능하다. Proxy, Adapter, Composite, Strategy와의 구분, GoF와 `@` 문법의 구분, PEP 318 인용, "쓰지 말아야 할 때"도 모두 정확하다.

- [권장] src/06_decorator/03_pythonic.py:21-23 — 이 파일의 toy_encrypt는 02/ex1과 달리 반복 키 XOR이다. 반복 키 XOR 출력은 주기적이라 어느 정도 압축된다. 그래서 학생이 03의 build_send로 순서 실험(["encrypt","compress"])을 하면 "암호문은 압축되지 않는다"는 본문 주장과 다른 결과를 볼 수 있다. 02와 같은 SHA-256 카운터 키스트림을 쓰거나, docstring에 "반복 키라 압축 불가 성질은 없다. 순서 실험에는 02를 쓸 것"을 명시할 것.
- [권장] src/06_decorator/solutions/ex1_order.py:87-91 — Batch.send가 버퍼가 찰 때마다 `self.flush()`를 불러 안쪽 flush까지 전파한다. 본문 02의 BatchingChannel은 `_emit()`으로 "내보내기"와 "flush 전파"를 분리했다. 지금 결과에는 영향이 없지만 본문과 어긋나므로 같은 `_emit()` 구조로 맞출 것.
