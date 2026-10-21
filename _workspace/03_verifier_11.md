VERDICT: PASS

## 기계 검증 (재검증)
```

=== 장 11 ===
  OK   원고 11-observer.html
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
  OK   11_observer/01_naive.py: 모듈 docstring 있음
  OK   11_observer/01_naive.py: 모든 클래스/함수에 docstring
  OK   11_observer/01_naive.py: 주석 비율 37%
  OK   11_observer/01_naive.py: __main__ 데모 있음
  OK   11_observer/01_naive.py: 실행 성공
  OK   11_observer/01_naive.py: 데모 출력 있음
  OK   11_observer/01_naive.py: 원고에서 참조됨
  OK   11_observer/02_observer.py: 모듈 docstring 있음
  OK   11_observer/02_observer.py: 모든 클래스/함수에 docstring
  OK   11_observer/02_observer.py: 주석 비율 45%
  OK   11_observer/02_observer.py: __main__ 데모 있음
  OK   11_observer/02_observer.py: 실행 성공
  OK   11_observer/02_observer.py: 데모 출력 있음
  OK   11_observer/02_observer.py: 원고에서 참조됨
  OK   11_observer/03_pythonic.py: 모듈 docstring 있음
  OK   11_observer/03_pythonic.py: 모든 클래스/함수에 docstring
  OK   11_observer/03_pythonic.py: 주석 비율 39%
  OK   11_observer/03_pythonic.py: __main__ 데모 있음
  OK   11_observer/03_pythonic.py: 실행 성공
  OK   11_observer/03_pythonic.py: 데모 출력 있음
  OK   11_observer/03_pythonic.py: 원고에서 참조됨
  OK   11_observer/solutions/ex1_unsubscribe_during_notify.py: 모듈 docstring 있음
  OK   11_observer/solutions/ex1_unsubscribe_during_notify.py: 모든 클래스/함수에 docstring
  OK   11_observer/solutions/ex1_unsubscribe_during_notify.py: 주석 비율 40%
  OK   11_observer/solutions/ex1_unsubscribe_during_notify.py: __main__ 데모 있음
  OK   11_observer/solutions/ex1_unsubscribe_during_notify.py: 실행 성공
  OK   11_observer/solutions/ex1_unsubscribe_during_notify.py: 데모 출력 있음
  OK   11_observer/solutions/ex1_unsubscribe_during_notify.py: 원고에서 참조됨
  OK   11_observer/solutions/ex2_signup_events.py: 모듈 docstring 있음
  OK   11_observer/solutions/ex2_signup_events.py: 모든 클래스/함수에 docstring
  OK   11_observer/solutions/ex2_signup_events.py: 주석 비율 34%
  OK   11_observer/solutions/ex2_signup_events.py: __main__ 데모 있음
  OK   11_observer/solutions/ex2_signup_events.py: 실행 성공
  OK   11_observer/solutions/ex2_signup_events.py: 데모 출력 있음
  OK   11_observer/solutions/ex2_signup_events.py: 원고에서 참조됨
  --> PASS (ok 48, warn 0, fail 0)

총 1장, 실패 0장 
```

## 재검증: 이전 지적 해소 여부
- [필수→해소] 연습문제 2 — src/11_observer/solutions/ex2_signup_events.py에 `UserSignedUp.referrer_id: int | None = None`(25행), `sign_up(email, referrer_id=None)`, `award_referral_points` 구독자(추천인 없으면 무시)가 추가되고, 데모 [3]에서 "추천인 1에게 1,000포인트" 출력 확인. 해설(chapters/11-observer.html:201)이 "흐름은 그대로지만 이벤트 스키마는 넓혀야 한다 — 푸시 모델 메시지 설계의 비용, 기본값 None으로 하위 호환"으로 정직하게 수정됨. 문제의 두 요구(추천인 포인트, 메일 장애 격리) 모두 충족.
- [권장→해소] src/11_observer/01_naive.py:4-5 — on_price() → push_price()로 수정.
- [권장→해소] src/11_observer/01_naive.py:12 — 고통 4에 "(데모 없음, 원고 참조)" 표기.
- [권장→해소] src/11_observer/02_observer.py:62 — "같은 키 안에서의 중복 등록을 막는다(종목 키와 ALL을 함께 구독하면 두 번 통지된다)"로 좁혀짐.

## 데모 출력·data-lines 재대조
- 02_observer.py [0]~[6] 출력이 원고 109행 설명과 동일. ex2 출력 [1]~[3] 해설과 일치.
- data-lines(21-103, 106-182 / 21-85, 88-129) 경계 정확.

## 의미 검증
신규 지적 없음.

## 재검증 (2026-10-08)
- 문구 변경("99장" → "종합 장", chapters/11-observer.html:158) 후 verify_chapter.py 11 재실행: PASS (ok 48, warn 0, fail 0). 회귀 없음. 종합 장은 커리큘럼(01_architect_curriculum.md 99장 `combinations`에 "옵저버+커맨드")에 계획되어 있어 참조로 타당.
