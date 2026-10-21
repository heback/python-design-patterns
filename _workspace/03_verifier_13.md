VERDICT: PASS

## 기계 검증 (재검증 시 재실행, 결과 동일)
```

=== 장 13 ===
  OK   원고 13-state.html
  OK   메타 주석(title) 있음
  OK   필수 섹션 모두 있음
  OK   섹션 순서 올바름
  OK   #context 에 코드 없음 (맥락만)
  OK   상황 설명이 첫 코드보다 앞
  OK   모든 본문 코드 앞에 lead-in 문단
  OK   코드 참조 8개 확인
  OK   #structure 에 SVG 다이어그램 있음
  OK   SVG 색 하드코딩 없음
  OK   연습문제 4개
  OK   모든 연습문제에 해설
  OK   코드 디렉터리 있음
  OK   13_state/01_naive.py: 모듈 docstring 있음
  OK   13_state/01_naive.py: 모든 클래스/함수에 docstring
  OK   13_state/01_naive.py: 주석 비율 35%
  OK   13_state/01_naive.py: __main__ 데모 있음
  OK   13_state/01_naive.py: 실행 성공
  OK   13_state/01_naive.py: 데모 출력 있음
  OK   13_state/01_naive.py: 원고에서 참조됨
  OK   13_state/02_state.py: 모듈 docstring 있음
  OK   13_state/02_state.py: 모든 클래스/함수에 docstring
  OK   13_state/02_state.py: 주석 비율 42%
  OK   13_state/02_state.py: __main__ 데모 있음
  OK   13_state/02_state.py: 실행 성공
  OK   13_state/02_state.py: 데모 출력 있음
  OK   13_state/02_state.py: 원고에서 참조됨
  OK   13_state/03_state_vs_strategy.py: 모듈 docstring 있음
  OK   13_state/03_state_vs_strategy.py: 모든 클래스/함수에 docstring
  OK   13_state/03_state_vs_strategy.py: 주석 비율 44%
  OK   13_state/03_state_vs_strategy.py: __main__ 데모 있음
  OK   13_state/03_state_vs_strategy.py: 실행 성공
  OK   13_state/03_state_vs_strategy.py: 데모 출력 있음
  OK   13_state/03_state_vs_strategy.py: 원고에서 참조됨
  OK   13_state/04_pythonic_fsm.py: 모듈 docstring 있음
  OK   13_state/04_pythonic_fsm.py: 모든 클래스/함수에 docstring
  OK   13_state/04_pythonic_fsm.py: 주석 비율 31%
  OK   13_state/04_pythonic_fsm.py: __main__ 데모 있음
  OK   13_state/04_pythonic_fsm.py: 실행 성공
  OK   13_state/04_pythonic_fsm.py: 데모 출력 있음
  OK   13_state/04_pythonic_fsm.py: 원고에서 참조됨
  OK   13_state/05_pythonic_variants.py: 모듈 docstring 있음
  OK   13_state/05_pythonic_variants.py: 모든 클래스/함수에 docstring
  OK   13_state/05_pythonic_variants.py: 주석 비율 42%
  OK   13_state/05_pythonic_variants.py: __main__ 데모 있음
  OK   13_state/05_pythonic_variants.py: 실행 성공
  OK   13_state/05_pythonic_variants.py: 데모 출력 있음
  OK   13_state/05_pythonic_variants.py: 원고에서 참조됨
  OK   13_state/solutions/ex1_transition_owner.py: 모듈 docstring 있음
  OK   13_state/solutions/ex1_transition_owner.py: 모든 클래스/함수에 docstring
  OK   13_state/solutions/ex1_transition_owner.py: 주석 비율 34%
  OK   13_state/solutions/ex1_transition_owner.py: __main__ 데모 있음
  OK   13_state/solutions/ex1_transition_owner.py: 실행 성공
  OK   13_state/solutions/ex1_transition_owner.py: 데모 출력 있음
  OK   13_state/solutions/ex1_transition_owner.py: 원고에서 참조됨
  OK   13_state/solutions/ex2_approval_state.py: 모듈 docstring 있음
  OK   13_state/solutions/ex2_approval_state.py: 모든 클래스/함수에 docstring
  OK   13_state/solutions/ex2_approval_state.py: 주석 비율 30%
  OK   13_state/solutions/ex2_approval_state.py: __main__ 데모 있음
  OK   13_state/solutions/ex2_approval_state.py: 실행 성공
  OK   13_state/solutions/ex2_approval_state.py: 데모 출력 있음
  OK   13_state/solutions/ex2_approval_state.py: 원고에서 참조됨
  OK   13_state/solutions/ex3_enum_table.py: 모듈 docstring 있음
  OK   13_state/solutions/ex3_enum_table.py: 모든 클래스/함수에 docstring
  OK   13_state/solutions/ex3_enum_table.py: 주석 비율 31%
  OK   13_state/solutions/ex3_enum_table.py: __main__ 데모 있음
  OK   13_state/solutions/ex3_enum_table.py: 실행 성공
  OK   13_state/solutions/ex3_enum_table.py: 데모 출력 있음
  OK   13_state/solutions/ex3_enum_table.py: 원고에서 참조됨
  --> PASS (ok 69, warn 0, fail 0)

총 1장, 실패 0장 
```

## 데모 출력 대조 (재검증 시 다시 실행)
- 01_naive.py: [3] 정비 중 unlock → 주행 중, [4] 주행 중 분실 → 정산 기록 [] → 원고 28행 일치.
- 02_state.py: [3] 세 시나리오 모두 거부, [1]·[4] 전이 로그 → 원고 106행 일치.
- 03_state_vs_strategy.py: [1] 민지 2,500원(주행 중 정책 교체 소급 없음), 도현 3,250원(심야), 로그에 [상태 전이]/[전략 교체] 두 갈래; [4] 반례 1,750원, 배터리 부족 → 원고 116·128행 일치.
- 04_pythonic_fsm.py: [2] 도달 불가/출구 없음 없음, [3] 54/54 일치, [4] 가드 거부 + 정비 중 UNLOCK 거부 → 원고 141행 일치.
- 05_pythonic_variants.py: [A-1] 상태 객체 2개, [A-2] AttributeError, [B-2]~[B-4] 문제 재현 → 원고 149-150행 일치. (getsizeof 32바이트와 AttributeError 문구는 파이썬 버전마다 다를 수 있음)
- solutions ex1/ex2/ex3: 실행 성공, 해설과 일치(ex1 co_names 의존 목록, ex2 승인 후 수정 거부, ex3 사용 중 book 거부).
- data-lines 범위(1-94, 96-224, 226-296) 정확.
- 재검증 시 03·04 출력이 위와 같음을 다시 확인했다. 04 [4] 전이 로그에 RIDING -END_RIDE-> AVAILABLE -BATTERY_LOW-> LOW_BATTERY가 나타나, 원고 142행에 새로 넣은 "출력 [4]의 전이 로그" 서술과 일치한다.

## 재검증: 이전 지적 해소 여부

- [필수 → 해소] 비교표의 "공개 세터가 없다" 문구가 바뀌었다. chapters/13-state.html:123은 이제 "몰라야 한다. 클라이언트용 상태 세터를 두지 않는다(`change_state()`는 상태 객체 전용 협력 메서드이며, 파이썬에서는 관례로만 막힌다)"이다. src/13_state/03_state_vs_strategy.py:147 주석도 "상태: 클라이언트용 세터 없음 — change_state()는 상태 객체 전용"으로 바뀌었다. 반례 app_server_end_ride docstring(187-188행)에도 "이 함수가 change_state()를 부를 수 있다는 것 자체가 관례 기반 캡슐화의 한계다 — 파이썬은 '상태 객체만 호출'을 강제하지 못하고, 문서와 리뷰가 지킨다"가 추가되었다. 코드(공개 change_state, 반례의 외부 호출)와 이제 모순이 없다.
- [권장 → 해소] html:89가 "4절 후반("전략 패턴과 무엇이 다른가")과 5·6절에서"로 바뀌었다.
- [권장 → 해소] html:142에 "방전 반납은 잠깐 AVAILABLE을 거친다(출력 [4]의 전이 로그)… 지도에 '대여 가능'이 순간적으로 떴다 사라진다. 중간 상태가 바깥에 보이는 비용이다"가 추가되었다. 04_pythonic_fsm.py end_ride docstring(163-165행)에도 같은 대가가 적혔다.
- [권장 → 해소] html:141이 "불가능하다"에서 "어렵다… 연습문제 1 해설처럼 바이트코드를 분석해 간선을 근사할 수는 있지만 조건부 전이는 놓친다"로 완화되어, ex1 해설과 더 이상 어긋나지 않는다.
- [권장 → 해소] 04_pythonic_fsm.py의 "표의 세 줄(MAINTAIN)이 한 case로 압축됐다" 주석이 MAINTAIN case(104행) 바로 위(103행)로 옮겨졌다.
- [동시 수정 항목 → 해소] '메서드 여덟 개/아홉 개' 표현: 01_naive.py의 `Scooter` 메서드는 `__init__`을 빼면 reserve, unlock, end_ride, tick, update_battery, send_to_maintenance, finish_maintenance, report_lost(동작 8개)와 label(1개)이다. html:19 "동작 메서드 여덟 개(표시용 `label()` 제외)", html:30 "`label()`까지 메서드 아홉 개", 02_state.py:3 "label()을 뺀 동작 메서드 여덟 개"가 모두 코드와 일치한다. 02의 ScooterState에서 거부 기본 구현을 가진 메서드는 6개(reserve/unlock/end_ride/send_to_maintenance/finish_maintenance/report_lost)이므로, 02_state.py:44 "거부용 보일러플레이트 여섯 개"와 html:97 "대여섯 개"(상태마다 자기가 허용하는 것을 빼면 2-5개)도 사실에 어긋나지 않는다.

## 의미 검증 (갱신)
패턴 정확성은 이전 보고서와 같다. 02에 상태 분기가 없고, 전이는 구체 상태가 change_state()로 결정하며, "기본은 거부"가 naive의 else 사고를 구조적으로 막는다. 이제 03과 원고의 State와 Strategy 비교도 코드와 일관된다. 남은 필수 지적은 없다.

- [권장, 선택] src/13_state/01_naive.py:130 — "같은 상태 목록이 일곱 번째로 반복된다"는 세는 기준이 모호하다(상태를 전부 나열하는 곳은 reserve와 label뿐이고, 나머지는 일부 상태만 비교한다). 04_pythonic_fsm.py:25 "01의 일곱 번째 반복"도 이 표현을 이어받는다. "같은 상태 목록이 또 반복된다" 정도로 바꾸면 학생이 세어 보다 혼란스러워하지 않는다. 판정에는 영향이 없다.
