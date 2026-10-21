VERDICT: PASS

## 기계 검증 (재검증 2026-10-08)
```

=== 장 12 ===
  OK   원고 12-command.html
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
  OK   12_command/01_naive.py: 모듈 docstring 있음
  OK   12_command/01_naive.py: 모든 클래스/함수에 docstring
  OK   12_command/01_naive.py: 주석 비율 32%
  OK   12_command/01_naive.py: __main__ 데모 있음
  OK   12_command/01_naive.py: 실행 성공
  OK   12_command/01_naive.py: 데모 출력 있음
  OK   12_command/01_naive.py: 원고에서 참조됨
  OK   12_command/02_command.py: 모듈 docstring 있음
  OK   12_command/02_command.py: 모든 클래스/함수에 docstring
  OK   12_command/02_command.py: 주석 비율 33%
  OK   12_command/02_command.py: __main__ 데모 있음
  OK   12_command/02_command.py: 실행 성공
  OK   12_command/02_command.py: 데모 출력 있음
  OK   12_command/02_command.py: 원고에서 참조됨
  OK   12_command/03_pythonic.py: 모듈 docstring 있음
  OK   12_command/03_pythonic.py: 모든 클래스/함수에 docstring
  OK   12_command/03_pythonic.py: 주석 비율 33%
  OK   12_command/03_pythonic.py: __main__ 데모 있음
  OK   12_command/03_pythonic.py: 실행 성공
  OK   12_command/03_pythonic.py: 데모 출력 있음
  OK   12_command/03_pythonic.py: 원고에서 참조됨
  OK   12_command/solutions/ex2_remote_undo.py: 모듈 docstring 있음
  OK   12_command/solutions/ex2_remote_undo.py: 모든 클래스/함수에 docstring
  OK   12_command/solutions/ex2_remote_undo.py: 주석 비율 35%
  OK   12_command/solutions/ex2_remote_undo.py: __main__ 데모 있음
  OK   12_command/solutions/ex2_remote_undo.py: 실행 성공
  OK   12_command/solutions/ex2_remote_undo.py: 데모 출력 있음
  OK   12_command/solutions/ex2_remote_undo.py: 원고에서 참조됨
  OK   12_command/solutions/ex3_cli_dispatch.py: 모듈 docstring 있음
  OK   12_command/solutions/ex3_cli_dispatch.py: 모든 클래스/함수에 docstring
  OK   12_command/solutions/ex3_cli_dispatch.py: 주석 비율 33%
  OK   12_command/solutions/ex3_cli_dispatch.py: __main__ 데모 있음
  OK   12_command/solutions/ex3_cli_dispatch.py: 실행 성공
  OK   12_command/solutions/ex3_cli_dispatch.py: 데모 출력 있음
  OK   12_command/solutions/ex3_cli_dispatch.py: 원고에서 참조됨
  --> PASS (ok 48, warn 0, fail 0)

총 1장, 실패 0장 
```

## 이전 지적 해소 여부
- [필수→해소] 02_command.py:14-15, 93-98 — "MoveShape는 역연산" 주석이 "세 명령 모두 스냅샷, 역연산이 왜 틀리는지는 MoveShape docstring"으로 고쳐졌고, 원고 129-130행과 일치.
- [필수→해소] chapters/12-command.html:185 — "(99장)" → "종합 장에서 다룬다". 이전 지적의 "99장은 존재하지 않음"은 내 오판이었다: 커리큘럼(_workspace/01_architect_curriculum.md:420-)에 99 종합 장이 계획되어 있고 `combinations` 절에 "옵저버+커맨드"가 명시됨. 현 문구는 타당.
- [필수→해소] 03_pythonic.py — 중첩 매크로: Macro.from_payload()가 하위 단계를 EditCommand.from_dict()로 재귀 복원(216행), Macro.retarget()이 하위 retarget()에 위임(220행). from_dict()에 type 분기 없음(126행) → 원고 151행 "역직렬화 진입점에 '매크로면 따로' 분기가 없다"가 사실. 데모 [2]-[5]에서 2단 중첩 매크로 retarget·JSON 왕복·재생·undo 정상.
- [권장→해소] 02_command.py:185-199 MacroCommand 롤백 추가, 데모 [6]으로 시연(출력: 실패 'ghost' is not in list, 결과 box(10,10,black) — 반쯤 적용 상태 없음). 원고 134행 서술과 출력 일치. 03 Macro.execute(192-202)도 같은 롤백.
- [권장→해소] 02_command.py:60-64 Canvas.set_color 추가, ChangeColor가 수신자 API만 사용(132·137행). 그림 12-1 Canvas 박스에 `+ set_color(id, color)` 추가됨. 03도 Canvas.set_color(43-47) 사용.
- [권장→해소] 03_pythonic.py:104-107 — kind 미선언 하위 클래스와 kind 중복 모두 정의 시점 TypeError. 데모 [6] 출력과 원고 155행 일치.

## data-lines 범위 (6개, 모두 정확)
- 02 33-68: `class Canvas` ~ dump() 끝(set_color 포함) / 71-170: Command ~ DeleteShape.label 끝 / 173-267: MacroCommand ~ context_menu_delete 끝(__main__ 제외).
- 03 54-71: 시도 ① 구분 주석 ~ partial_command_demo 끝 / 74-220: 시도 ② 구분 주석·COMMAND_TYPES ~ Macro.retarget 끝 / 223-240: Session 전체.
- 원고 각 lead-in이 가리키는 이름(remove/set_color, execute 시점 기록, MacroCommand 롤백 docstring, from_payload/retarget, init=True/False)이 모두 해당 범위 안에 있음.

## undo/redo 정확성 — 무작위 재시험 (scratchpad, src/에 __pycache__ 미생성 확인)
- 03: 3,000회 × 30단계. 깊이 3까지 중첩 매크로(5,229개가 2단 이상), 50% 확률로 JSON 왕복, 20% 확률로 retarget, ~8% 확률로 없는 도형("ghost") 단계 삽입. 실행 52,828 / 실패 1,413 / undo 20,367 / redo 3,605 — undo 후 == 직전 상태, redo 후 == 직후 상태, 실패 후 == 실행 전 상태(중첩 내부 실패 포함 롤백) **불일치 0건**.
- 03 Session: 1,000회 × 15명령(중첩·retarget), outbox 재생 캔버스 일치 1000/1000, 전체 undo 후 초기 상태 복귀.
- 03 retarget: 3단 중첩의 모든 잎이 새 shape_id, 모두 새 인스턴스. 등록부: kind 누락·중복 정의 모두 TypeError, 실패한 정의가 COMMAND_TYPES를 오염시키지 않음(['macro','move','recolor']).
- 02: 2,000회 × 25단계(이동·색·삭제·롤백 매크로, ~10% ghost) 불일치 0건, 실패 명령 5,766건 모두 실행 전 상태 유지.

## 의미 검증 (03_pythonic.py 전체 재독)
새 [필수] 없음. 주석·docstring은 모두 사실과 일치(replace가 init=False 필드를 기본값으로 재생성, from_dict 알 수 없는 type → KeyError 등 확인).
- [권장] src/12_command/03_pythonic.py:251-255 — `nested`가 이미 실행·이력에 들어간 `highlight` 인스턴스를 그대로 품는다. 데모는 retarget으로 새 인스턴스를 만들어 안전하지만, 학생이 `eunwoo.run(nested)`처럼 retarget 없이 실행하면 같은 인스턴스가 두 번 실행돼 첫 실행의 _before가 덮어쓰인다(원고 151행이 경고한 함정). → 253행 주석에 "nested를 그대로 run하면 highlight가 두 번 실행된다 — 반드시 retarget(새 인스턴스)으로 재생"을 한 줄 추가. 비차단.
- 참고: src/04_singleton/__pycache__, src/14_template_method/__pycache__ 가 존재(17:40·17:50 생성, 본 검증과 무관). 장 12·11 디렉터리에는 없음.
