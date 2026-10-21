VERDICT: PASS

## 기계 검증
```

=== 장 03 ===
  OK   원고 03-builder.html
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
  OK   03_builder/01_naive.py: 모듈 docstring 있음
  OK   03_builder/01_naive.py: 모든 클래스/함수에 docstring
  OK   03_builder/01_naive.py: 주석 비율 33%
  OK   03_builder/01_naive.py: __main__ 데모 있음
  OK   03_builder/01_naive.py: 실행 성공
  OK   03_builder/01_naive.py: 데모 출력 있음
  OK   03_builder/01_naive.py: 원고에서 참조됨
  OK   03_builder/02_builder.py: 모듈 docstring 있음
  OK   03_builder/02_builder.py: 모든 클래스/함수에 docstring
  OK   03_builder/02_builder.py: 주석 비율 32%
  OK   03_builder/02_builder.py: __main__ 데모 있음
  OK   03_builder/02_builder.py: 실행 성공
  OK   03_builder/02_builder.py: 데모 출력 있음
  OK   03_builder/02_builder.py: 원고에서 참조됨
  OK   03_builder/03_director.py: 모듈 docstring 있음
  OK   03_builder/03_director.py: 모든 클래스/함수에 docstring
  OK   03_builder/03_director.py: 주석 비율 37%
  OK   03_builder/03_director.py: __main__ 데모 있음
  OK   03_builder/03_director.py: 실행 성공
  OK   03_builder/03_director.py: 데모 출력 있음
  OK   03_builder/03_director.py: 원고에서 참조됨
  OK   03_builder/04_pythonic.py: 모듈 docstring 있음
  OK   03_builder/04_pythonic.py: 모든 클래스/함수에 docstring
  OK   03_builder/04_pythonic.py: 주석 비율 35%
  OK   03_builder/04_pythonic.py: __main__ 데모 있음
  OK   03_builder/04_pythonic.py: 실행 성공
  OK   03_builder/04_pythonic.py: 데모 출력 있음
  OK   03_builder/04_pythonic.py: 원고에서 참조됨
  OK   03_builder/solutions/ex2_request_builder.py: 모듈 docstring 있음
  OK   03_builder/solutions/ex2_request_builder.py: 모든 클래스/함수에 docstring
  OK   03_builder/solutions/ex2_request_builder.py: 주석 비율 31%
  OK   03_builder/solutions/ex2_request_builder.py: __main__ 데모 있음
  OK   03_builder/solutions/ex2_request_builder.py: 실행 성공
  OK   03_builder/solutions/ex2_request_builder.py: 데모 출력 있음
  OK   03_builder/solutions/ex2_request_builder.py: 원고에서 참조됨
  --> PASS (ok 48, warn 0, fail 0)

총 1장, 실패 0장 
```

## 의미 검증 (재검증 2회차)

수정된 파일(01_naive.py, 02_builder.py, 04_pythonic.py, 원고)을 처음부터 다시 읽고, data-run 5개를 모두 다시 실행해 원고와 비교했다. 이 장은 data-lines를 쓰지 않는다.

### 이전 지적 해소 여부
- [해소] 연습문제 2 해설 근거: "메서드를 바꾸는 조립 순서" 논거를 삭제했다. 지금은 `.retries(3).timeout(10)` 예로 build() 검사의 필요성을 설명하고, GET 본문은 "body()에서 해도 동작은 같지만 교차 제약을 한 곳에 모은다"고 정확히 서술한다(원고 241줄).
- [해소] 01_naive [4]·[5]에 start를 넣었다. 출력은 `WHERE order_date >= '2026-01-01' AND region = '서울' OR '1'='1'`로 문법상 유효한 주입이다. 95-96줄 주석과 원고 29줄의 "OR 우선순위 때문에 기간 조건까지 무력화된다"는 설명이 출력과 일치한다.
- [해소] GROUP BY 없는 HAVING 서술: 원고 21줄, 01_naive.py 11·55-56줄, 02_builder.py 4·166-168줄이 모두 "SQL 문법은 허용, 비집계 열이 섞이면 DB 거부, 팀의 대시보드 규칙으로 막는다"로 일관된다. 에러 메시지도 "(대시보드 규칙)"으로 바꿨고, 04_pythonic.py:44와 02의 [4] 출력이 같다.
- [해소] 02_builder.py:50과 원고 137줄은 이제 "컬렉션 필드는 전부 tuple/튜플"이라고 쓴다.
- [해소] 04_pythonic.py:3은 "70줄 남짓한 클래스"라고 쓰고, 이는 실제(100-176줄)와 맞는다.
- [해소] 02_builder.py:151-153에 int·bool 타입 검사를 추가했다. 96줄 주석 "limit()가 양의 int만 통과시키므로"가 이제 사실이다.

### 새 문제 검사
- 01_naive 출력 [1]~[5], 02 [1]~[6], 03 [1]~[3], 04 [1]~[5], ex2의 출력이 모두 원고 설명과 일치한다.
- 새로 생긴 틀린 주석이나 원고-코드 불일치는 없다.

필수 지적 없음.
