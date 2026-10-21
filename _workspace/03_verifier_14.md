VERDICT: PASS

(재검증, 2026-10-08. 이전 보고서의 필수 1건과 권장 5건을 항목별로 확인했다. 수정된 파일 4개(chapters/14-template-method.html, 02_template_method.py, 03_strategy_version.py, solutions/ex4_memory_limit.py)는 처음부터 다시 읽었다.)

## 기계 검증
```
=== 장 14 ===
  OK   원고 14-template-method.html
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
  OK   (01_naive / 02_template_method / 03_strategy_version / 04_pythonic /
        solutions/ex2_report_template / solutions/ex4_memory_limit 각각:
        docstring · 주석 비율(30/38/33/38/36/40%) · __main__ · 실행 성공 · 출력 · 원고 참조 모두 OK)
  --> PASS (ok 55, warn 0, fail 0)

총 1장, 실패 0장
```
검증 뒤 src/에 __pycache__나 .mypy_cache는 남지 않았다(python3 -B 사용, mypy 캐시는 scratchpad로 보냄).

## 이전 지적 해소 확인

### [필수] 비교 축 '필수 단계 누락 / 시그니처 오류' 서술 → 해소
- (1) `compile=print` 데모: 03 [3](c)로 옮겨졌고 문구가 "타입 검사기도 런타임도 잡지 못한다(테스트의 몫)"로 바뀌었다. 실제 출력은 `(c) compile=print → AC`이다. 사실과 맞다.
- (2) 누락 검출 서술: 03 [3](a)의 실제 출력은 `run 누락 → 생성 시점 TypeError: Toolchain.__init__() missing 1 required positional argument: 'run'`이다. 02 [7]은 `run 누락 → 인스턴스화 시점 TypeError: Can't instantiate abstract class GoJudge ...`와 `시그니처가 틀린 run → RE (TypeError)`를 낸다. 원고 92·99행과 표 104·105행이 이 출력과 일치한다.
  - 표 '필수 단계 누락 검출' 행: 02는 "인스턴스화 시점(abstractmethod, 이름만 검사)"(02 [7] 첫 줄), 03은 "생성 시점(dataclass 필수 필드)"(03 [3](a))로 적혀 있다. 일치한다. None 허용 훅에서 빠뜨림이 조용히 기본값이 된다는 단서도 코드(Toolchain 58-59행, Judge 123-126행)와 맞다.
  - 표 '시그니처·의미 오류 검출' 행: "양쪽 모두 런타임에는 못 잡는다(학생의 RE로 오판)"는 02 [7] 둘째 줄(`RE (TypeError)`), 03 [3](b)(`RE (TypeError)`)와 일치한다. "의미가 틀린 콜러블은 테스트만 잡는다"는 03 [3](c)(`AC`)와 일치한다.
- (3) 03 docstring 8행: "파일명·실행 + 선택적 검증·컴파일"로 바뀌었다. `Toolchain.run`이 필수 필드로 추가되었고(57행) 골격 129행이 `tc.run(sub, inp)`를 부른다. 이제 주석과 코드가 일치한다.
- **"(b)는 mypy가 잡는다"는 사실이다.** 근거는 두 가지다.
  - 논리: `Toolchain.compile`의 선언 타입은 `Callable[[str], None] | None`이다. mypy는 람다를 기대 타입 문맥으로 검사하고, 인자 0개 람다는 위치 인자 1개를 받는 콜러블의 하위 타입이 아니다(호출 측이 넘기는 인자를 받을 수 없다). 반면 `print`는 `(*values: object, sep=..., end=..., file=..., flush=...) -> None`이므로 `str` 하나를 받는 호출을 허용한다. 따라서 `Callable[[str], None]`과 호환되고, 오류가 나지 않는다.
  - 실측: scratchpad에 mypy를 설치해 `# type: ignore`를 지운 사본을 검사했다. 176행에서 `Argument "compile" to "Toolchain" has incompatible type "Callable[[], None]"; expected "Callable[[str], None] | None" [arg-type]`가 나왔다. 182행(`compile=print`)에는 오류가 없었다. 02의 `SloppyJudge.run(self)`도 `Signature of "run" incompatible with supertype [override]`로 잡혀서, 02 docstring 266행의 "mypy는 override 오류로 잡지만"이 사실임을 확인했다. 171행 run 누락은 `[call-arg]`로 잡힌다.

### [권장] ex4의 compile을 추상으로 둔 문제 → 해소
`Judge.compile`이 기본 no-op 훅(60-61행)으로 바뀌었다. `PythonJudge` 본문은 비어 있다. 해설 1(a)와 모순이 없다.

### [권장] ex4 골격에 시간 검사 없음 → 해소
36-43행이 "실행 → TLE → MLE → 비교" 순서다. docstring 31-32행이 순서의 이유를 설명한다. 실행 결과는 `PythonJudge 절약형: AC 낭비형: MLE (#1, 3991KB)` / `JavaJudge ... MLE (#1, 4191KB)`로 해설과 일치한다.

### [권장] 체커 예외가 RE로 오판되는 문제 → 해소
03의 `within`이 ValueError를 False(WA)로 번역한다(78-81행). 02의 `FloatTolerantCppJudge.outputs_match` docstring(203행)은 한계를 명시한다. 수정안의 두 선택지가 모두 반영되었다.

### [권장] `__init_subclass__` 시점 서술 → 해소
124행: "abstractmethod(인스턴스화 시점)보다 이른, 런타임에서 가장 이른 시점인 import 시 … typing.final보다는 늦지만". 정확하다.

### [권장] 02 [6]이 전역 judge-*를 세는 문제 → 해소
219행에서 before를 잡고 242-243행에서 증가분을 센다. 실행 결과는 0이다.

## 재독에서 새로 확인한 것
- data-lines 1-122(골격·추상 단계·훅)와 124-204(구체 채점기 + FloatTolerantCppJudge)는 수정 뒤에도 범위가 정확하다(122행 = outputs_match의 return, 124행 = 구체 채점기 구분 주석, 204행 = FloatTolerant의 return).
- 01·02·03·04·ex2·ex4의 data-run 출력은 원고 설명(28·91-92·99·117-125행, 해설)과 모두 일치한다.

## 의미 검증 지적
- [권장] src/14_template_method/03_strategy_version.py:176 — `# type: ignore[arg-type]`는 같은 줄의 두 번째 mypy 오류 `Cannot infer type of lambda [misc]`를 덮지 못한다. 원본 파일에 mypy를 돌리면 "Error code "misc" not covered by "type: ignore[arg-type]" comment"가 나온다. 원고는 "mypy가 잡는다"를 가르치므로, 학생이 직접 돌려 보면 의도와 다른 잡음이 보인다. → `# type: ignore[arg-type, misc]`로 바꾼다.
- [권장] src/14_template_method/03_strategy_version.py:163-164 — `problem_config = {"checker": "within", "tol": 1e-3}`는 mypy가 `dict[str, object]`로 추론한다. 그래서 164행에서 `Argument "tol" to "within" has incompatible type "object"; expected "float" [arg-type]`가 난다. 데모의 주제(타입 검사기가 무엇을 잡는가)와 무관한 오류다. → `tol: float = 1e-3`를 따로 두거나 `float(problem_config["tol"])`로 쓴다.
- [권장] src/14_template_method/03_strategy_version.py:168 — 표제가 "02(상속)와 같은 시나리오 세 가지"인데, 02 데모 [7]은 두 가지(누락, 시그니처)만 보인다. 의미 오류(c)는 02에 대응 데모가 없다. → "02 데모 [7]의 두 시나리오 + 의미 오류 하나"로 고치거나, '같은'을 뺀다.
