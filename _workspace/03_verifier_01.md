VERDICT: PASS

## 기계 검증
```

=== 장 01 ===
  OK   원고 01-factory-method.html
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
  OK   01_factory_method/01_naive.py: 모듈 docstring 있음
  OK   01_factory_method/01_naive.py: 모든 클래스/함수에 docstring
  OK   01_factory_method/01_naive.py: 주석 비율 39%
  OK   01_factory_method/01_naive.py: __main__ 데모 있음
  OK   01_factory_method/01_naive.py: 실행 성공
  OK   01_factory_method/01_naive.py: 데모 출력 있음
  OK   01_factory_method/01_naive.py: 원고에서 참조됨
  OK   01_factory_method/02_factory_method.py: 모듈 docstring 있음
  OK   01_factory_method/02_factory_method.py: 모든 클래스/함수에 docstring
  OK   01_factory_method/02_factory_method.py: 주석 비율 45%
  OK   01_factory_method/02_factory_method.py: __main__ 데모 있음
  OK   01_factory_method/02_factory_method.py: 실행 성공
  OK   01_factory_method/02_factory_method.py: 데모 출력 있음
  OK   01_factory_method/02_factory_method.py: 원고에서 참조됨
  OK   01_factory_method/03_pythonic.py: 모듈 docstring 있음
  OK   01_factory_method/03_pythonic.py: 모든 클래스/함수에 docstring
  OK   01_factory_method/03_pythonic.py: 주석 비율 40%
  OK   01_factory_method/03_pythonic.py: __main__ 데모 있음
  OK   01_factory_method/03_pythonic.py: 실행 성공
  OK   01_factory_method/03_pythonic.py: 데모 출력 있음
  OK   01_factory_method/03_pythonic.py: 원고에서 참조됨
  OK   01_factory_method/04_registry.py: 모듈 docstring 있음
  OK   01_factory_method/04_registry.py: 모든 클래스/함수에 docstring
  OK   01_factory_method/04_registry.py: 주석 비율 33%
  OK   01_factory_method/04_registry.py: __main__ 데모 있음
  OK   01_factory_method/04_registry.py: 실행 성공
  OK   01_factory_method/04_registry.py: 데모 출력 있음
  OK   01_factory_method/04_registry.py: 원고에서 참조됨
  OK   01_factory_method/solutions/ex1_alt_constructors.py: 모듈 docstring 있음
  OK   01_factory_method/solutions/ex1_alt_constructors.py: 모든 클래스/함수에 docstring
  OK   01_factory_method/solutions/ex1_alt_constructors.py: 주석 비율 43%
  OK   01_factory_method/solutions/ex1_alt_constructors.py: __main__ 데모 있음
  OK   01_factory_method/solutions/ex1_alt_constructors.py: 실행 성공
  OK   01_factory_method/solutions/ex1_alt_constructors.py: 데모 출력 있음
  OK   01_factory_method/solutions/ex1_alt_constructors.py: 원고에서 참조됨
  OK   01_factory_method/solutions/ex2_log_parser.py: 모듈 docstring 있음
  OK   01_factory_method/solutions/ex2_log_parser.py: 모든 클래스/함수에 docstring
  OK   01_factory_method/solutions/ex2_log_parser.py: 주석 비율 33%
  OK   01_factory_method/solutions/ex2_log_parser.py: __main__ 데모 있음
  OK   01_factory_method/solutions/ex2_log_parser.py: 실행 성공
  OK   01_factory_method/solutions/ex2_log_parser.py: 데모 출력 있음
  OK   01_factory_method/solutions/ex2_log_parser.py: 원고에서 참조됨
  --> PASS (ok 55, warn 0, fail 0)

총 1장, 실패 0장 
```

## 의미 검증
data-run 대상 6개 실행 결과는 원고의 출력 설명([1]~[5])과 모두 일치한다. 02_factory_method.py는 GoF 팩토리 메서드에 맞게 구현되어 있다. 생성 결정을 하위 클래스에 위임하고, run()에는 구체 리더 이름이 없으며, 원고가 주장한 대로 port가 SerialJsonJob으로 옮겨졌다. 03과 04의 "GoF와의 거리" 비판도 정확하다.

- [권장] chapters/01-factory-method.html #ex2 해설 3번째 문단 — "파서 인스턴스를 `__init__`에서 만들어 두는 것은 … 테스트에서 하위 클래스로 바꿔 끼우기 어려워진다"는 근거가 맞지 않는다. `__init__`에서 `self.create_parser()`를 불러도 오버라이드는 그대로 동작한다. 생성자에서 팩토리 메서드를 부를 때의 진짜 함정을 근거로 쓸 것: (1) 하위 클래스가 `super().__init__()`보다 늦게 설정하는 상태(예: SerialJsonJob.port)가 아직 없다. (2) 생성 시점이 '실행 시'에서 '객체 생성 시'로 당겨진다(03 [3]에서 다룬 논점).
- [권장] chapters/01-factory-method.html #context 3번째 문단 — "분기 순서를 잘못 바꿔 질량분석 데이터가 CSV 파서로 들어가는 사고"는 01_naive.py의 `==` 비교 분기로는 일어날 수 없다. "분기 조건을 잘못 고쳐…"로 바꾸거나, 순서가 의미를 갖는 분기(startswith 등)를 쓰는 사고로 바꿀 것.
- [권장] src/01_factory_method/solutions/ex2_log_parser.py:58-62 — `__init_subclass__`가 중복 fmt를 아무 말 없이 덮어쓴다. 본문 04_registry.py:52-54는 "조용히 덮어쓰면 버그"라며 거부했으므로 해설도 같은 검사(`if fmt in LogCollector.registry: raise ValueError`)를 넣을 것. 문제는 "새 형식은 클래스 정의만으로 추가"를 요구하는데 데모는 이를 보여 주지 않는다. `__main__`에서 세 번째 형식(예: `class CaddyCollector(LogCollector, fmt="caddy")`)을 정의하고 for_format으로 고르는 데모를 추가할 것.
- [권장] src/01_factory_method/04_registry.py:85 — `not ln[0].isalpha()`로 CSV 헤더를 건너뛰는 이유를 설명하는 주석이 없다. "헤더 줄(wavelength_nm,...) 제외" 같은 주석을 추가할 것.
- [권장] src/01_factory_method/01_naive.py:64 — docstring은 "16바이트씩 끊어"라고 하지만 코드는 8바이트 float64를 모두 풀어 둘씩 묶는다. 02의 표현("8바이트 float64를 두 개씩 묶어")에 맞출 것.
- [권장] src/01_factory_method/04_registry.py:56 — `cls.device = device`가 쓰는 속성이 Reader에 선언되어 있지 않다. `device: ClassVar[str]`을 선언해 타입 검사기와 독자에게 알릴 것.
