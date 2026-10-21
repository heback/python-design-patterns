VERDICT: PASS

## 기계 검증
```

=== 장 07 ===
  OK   원고 07-composite.html
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
  OK   07_composite/01_naive.py: 모듈 docstring 있음
  OK   07_composite/01_naive.py: 모든 클래스/함수에 docstring
  OK   07_composite/01_naive.py: 주석 비율 31%
  OK   07_composite/01_naive.py: __main__ 데모 있음
  OK   07_composite/01_naive.py: 실행 성공
  OK   07_composite/01_naive.py: 데모 출력 있음
  OK   07_composite/01_naive.py: 원고에서 참조됨
  OK   07_composite/02_composite.py: 모듈 docstring 있음
  OK   07_composite/02_composite.py: 모든 클래스/함수에 docstring
  OK   07_composite/02_composite.py: 주석 비율 35%
  OK   07_composite/02_composite.py: __main__ 데모 있음
  OK   07_composite/02_composite.py: 실행 성공
  OK   07_composite/02_composite.py: 데모 출력 있음
  OK   07_composite/02_composite.py: 원고에서 참조됨
  OK   07_composite/03_pythonic.py: 모듈 docstring 있음
  OK   07_composite/03_pythonic.py: 모든 클래스/함수에 docstring
  OK   07_composite/03_pythonic.py: 주석 비율 39%
  OK   07_composite/03_pythonic.py: __main__ 데모 있음
  OK   07_composite/03_pythonic.py: 실행 성공
  OK   07_composite/03_pythonic.py: 데모 출력 있음
  OK   07_composite/03_pythonic.py: 원고에서 참조됨
  OK   07_composite/solutions/ex1_transparency.py: 모듈 docstring 있음
  OK   07_composite/solutions/ex1_transparency.py: 모든 클래스/함수에 docstring
  OK   07_composite/solutions/ex1_transparency.py: 주석 비율 47%
  OK   07_composite/solutions/ex1_transparency.py: __main__ 데모 있음
  OK   07_composite/solutions/ex1_transparency.py: 실행 성공
  OK   07_composite/solutions/ex1_transparency.py: 데모 출력 있음
  OK   07_composite/solutions/ex1_transparency.py: 원고에서 참조됨
  OK   07_composite/solutions/ex2_org_chart.py: 모듈 docstring 있음
  OK   07_composite/solutions/ex2_org_chart.py: 모든 클래스/함수에 docstring
  OK   07_composite/solutions/ex2_org_chart.py: 주석 비율 34%
  OK   07_composite/solutions/ex2_org_chart.py: __main__ 데모 있음
  OK   07_composite/solutions/ex2_org_chart.py: 실행 성공
  OK   07_composite/solutions/ex2_org_chart.py: 데모 출력 있음
  OK   07_composite/solutions/ex2_org_chart.py: 원고에서 참조됨
  OK   07_composite/solutions/ex3_fixed_depth.py: 모듈 docstring 있음
  OK   07_composite/solutions/ex3_fixed_depth.py: 모든 클래스/함수에 docstring
  OK   07_composite/solutions/ex3_fixed_depth.py: 주석 비율 37%
  OK   07_composite/solutions/ex3_fixed_depth.py: __main__ 데모 있음
  OK   07_composite/solutions/ex3_fixed_depth.py: 실행 성공
  OK   07_composite/solutions/ex3_fixed_depth.py: 데모 출력 있음
  OK   07_composite/solutions/ex3_fixed_depth.py: 원고에서 참조됨
  --> PASS (ok 55, warn 0, fail 0)

총 1장, 실패 0장 
```

## 의미 검증 (재검증 2회차)

수정된 파일(01_naive.py, 03_pythonic.py, solutions/ex1·ex2·ex3, 원고)을 처음부터 다시 읽고 data-run 6개를 모두 다시 실행했다. 02_composite.py는 바뀌지 않았다. data-lines 13-87, 88-149, 150-185의 경계가 여전히 BomItem, Assembly, report()의 시작 줄과 정확히 맞는다.

### 이전 지적 해소 여부
- [해소][필수] 03_pythonic.py의 isinstance 회귀: 03_pythonic.py는 공통 기반 `BomItem(ABC)`를 되살렸다. 추상 멤버는 `own_cost`와 `walk()` 두 개다. `Part.walk`는 `yield self, multiplier`이고, `Assembly.walk`는 분기 없이 `yield from child.walk(multiplier * qty)`다. `total_cost()`는 `sum(item.own_cost * qty ...)`이므로 클라이언트 원가 계산에 타입 분기가 없다. `explode()`의 isinstance는 "단품 필터"라고 docstring(112-114줄)과 원고 127줄에서 구분해 설명한다. singledispatch가 "분기를 디스패치 표에 모은 것"이며 타입 추가가 어려워지는 교환이라는 점도 코드(127-129줄)와 원고 131줄에 들어갔다. 이로써 연습문제 2 해설의 기준("분기를 다형성으로")과 모순되지 않는다.
- [해소] 01_naive.py [3]은 이제 `total_cost(engine_v2)`를 직접 부른다. 손주 위치에 링 세트(Assembly)가 와서 51줄에서 AttributeError가 난다. 원고 21줄의 "링 세트 → AttributeError" 서사와 원인이 일치한다.
- [해소] 03_pythonic.py:147·159와 원고 127줄이 "02와 BOM이 달라 금액이 다르다(300,400원 vs 482,000원)"를 명시한다.
- [해소] ex1은 `LeafHasNoChildrenError(TypeError)`를 쓰고, 그 이유를 docstring(14-15줄)과 원고 170줄에서 설명한다. `BomItem.cost()`의 NotImplementedError는 "하위 클래스 미구현"이라는 정상 용법이다.
- [해소] 회사명을 '다온기계'로 바꿨다. 장 07 원고와 코드 전체에서 일관되고, 다른 장에서는 쓰이지 않는다. '한결'은 장 07에 남아 있지 않다.

### 새 문제 검사(수치 검산)
- 03 [1]: 120,000 + 40,000 + 5,000×2 + 2,400×6 + 3,100×2 + 120×16 + 15,000 + 45,000×2 + 120×24 = 300,400원. 출력과 같다.
- 03 [2]: 볼트 (16+24)×10 = 400, 링 3×2×10 = 60, 핀 20, 강관 20. 출력과 같다.
- 03 [4]: 6,000 + 엔진 5,980 + 프레임 37,710 = 49,690g. 출력과 같다.
- 01 [2]: 72,520원, 638g. ex2: 32,500만 원, 5명. 모두 출력과 원고가 일치한다.
- 새로 생긴 틀린 주석이나 원고-코드 불일치는 없다.

필수 지적 없음.
