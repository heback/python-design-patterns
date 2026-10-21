VERDICT: PASS

## 기계 검증
```

=== 장 08 ===
  OK   원고 08-facade.html
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
  OK   08_facade/01_naive.py: 모듈 docstring 있음
  OK   08_facade/01_naive.py: 모든 클래스/함수에 docstring
  OK   08_facade/01_naive.py: 주석 비율 38%
  OK   08_facade/01_naive.py: __main__ 데모 있음
  OK   08_facade/01_naive.py: 실행 성공
  OK   08_facade/01_naive.py: 데모 출력 있음
  OK   08_facade/01_naive.py: 원고에서 참조됨
  OK   08_facade/02_facade.py: 모듈 docstring 있음
  OK   08_facade/02_facade.py: 모든 클래스/함수에 docstring
  OK   08_facade/02_facade.py: 주석 비율 38%
  OK   08_facade/02_facade.py: __main__ 데모 있음
  OK   08_facade/02_facade.py: 실행 성공
  OK   08_facade/02_facade.py: 데모 출력 있음
  OK   08_facade/02_facade.py: 원고에서 참조됨
  OK   08_facade/03_pythonic.py: 모듈 docstring 있음
  OK   08_facade/03_pythonic.py: 모든 클래스/함수에 docstring
  OK   08_facade/03_pythonic.py: 주석 비율 40%
  OK   08_facade/03_pythonic.py: __main__ 데모 있음
  OK   08_facade/03_pythonic.py: 실행 성공
  OK   08_facade/03_pythonic.py: 데모 출력 있음
  OK   08_facade/03_pythonic.py: 원고에서 참조됨
  OK   08_facade/solutions/ex2_video_upload.py: 모듈 docstring 있음
  OK   08_facade/solutions/ex2_video_upload.py: 모든 클래스/함수에 docstring
  OK   08_facade/solutions/ex2_video_upload.py: 주석 비율 32%
  OK   08_facade/solutions/ex2_video_upload.py: __main__ 데모 있음
  OK   08_facade/solutions/ex2_video_upload.py: 실행 성공
  OK   08_facade/solutions/ex2_video_upload.py: 데모 출력 있음
  OK   08_facade/solutions/ex2_video_upload.py: 원고에서 참조됨
  OK   08_facade/solutions/ex3_split_facade.py: 모듈 docstring 있음
  OK   08_facade/solutions/ex3_split_facade.py: 모든 클래스/함수에 docstring
  OK   08_facade/solutions/ex3_split_facade.py: 주석 비율 48%
  OK   08_facade/solutions/ex3_split_facade.py: __main__ 데모 있음
  OK   08_facade/solutions/ex3_split_facade.py: 실행 성공
  OK   08_facade/solutions/ex3_split_facade.py: 데모 출력 있음
  OK   08_facade/solutions/ex3_split_facade.py: 원고에서 참조됨
  --> PASS (ok 48, warn 0, fail 0)

총 1장, 실패 0장 
```

## 의미 검증 (재검증 2회차)

수정된 파일(01_naive.py, solutions/ex2_video_upload.py, solutions/ex3_split_facade.py, 원고)을 처음부터 다시 읽고 data-run 5개를 모두 다시 실행했다. 02_facade.py는 바뀌지 않았으므로 data-lines 83-138, 139-192는 그대로 유효하다.

### 이전 지적 해소 여부
- [해소][필수] 01_naive.py:111 docstring이 이제 "다섯 의존이 또 생긴다(APIS 게이트웨이는 복제 과정에서 빠졌다)"이다. 112-113줄의 실제 생성 수(5)와 원고 표(MobileApp 5)와 일치한다.
- [해소] ex2에 `cli_bulk_upload(facade, paths)`(100-108줄)를 추가했다. 데모 [3]에서 같은 퍼사드를 부르고, promo.avi 실패 시 보상 삭제가 일어나며, 실패 목록이 출력된다. 원고 해설(225줄)의 "CLI는 같은 퍼사드를 부르되 결과를 실패 목록으로 표현한다(실행 [3])"와 일치한다.
- [해소] ex3:73의 출력 문구가 "force_seat(수동 지정)가 있는가?"로 바뀌어 실제 검사 `hasattr(passenger, 'force_seat')`와 맞는다.
- [해소] ex3 모듈 docstring(5-6줄)이 "(가)만 코드로 보이고 (나)는 원고 서술 참조"로 바뀌었다.
- [해소] ex3:34-37이 "승객 퍼사드를 '통해서는' 호출할 길이 없다. 다만 퍼사드는 접근을 막지 않으며 진짜 차단은 보호 프록시나 권한 검사 몫(9장)"으로 완화되었다. 원고 해설 (가) 항목도 같은 정밀도로 고쳤다.
- [해소] 원고 5절(129줄)이 세션 퍼사드와 함수 퍼사드의 "조합"이라서 클라이언트가 reader/printer를 다시 넘긴다고 명시한다. 성립 범위를 "열기·닫기를 모른다"까지로 한정하고, `functools.partial`로 완전히 숨기는 변형도 언급한다. 03_pythonic.py:82의 "클라이언트는 open/close를 아예 몰라도 된다"와도 정합한다.

### 새 문제 검사
- 01 [1]~[3], ex2 [1]~[3], ex3 [1]~[3]의 출력이 원고 설명과 일치한다.
- 새로 생긴 틀린 주석이나 원고-코드 불일치는 없다.

필수 지적 없음.
