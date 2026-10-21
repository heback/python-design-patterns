# 용어 정의 작업 계획 — 3판 (13-15만 재생성; 00~12,99는 완료)

## 13-state.html — 19개

- `illegal-transition` **불법 전이** [concept] 별칭=['불법 전이']
  - 첫 등장: 13-state.html · 코드 src/13_state/01_naive.py · …이다. 상태 수 × 메서드 수만큼 분기가 생기고, 그중 하나만 빠뜨려도 불법 전이가 조용히 허용된다. """ def __init__(self, …
  - 용어집 정의(short): 현재 상태에서 허용되지 않은 동작이 요청되어 일어나서는 안 되는 상태 변화.
  - 책 안의 기존 설명: ['13 · 현재 상태에서 허용되지 않는 동작을 요청했을 때']
  - 감사 메모: ['13장 01_naive.py docstring이 IllegalTransition docstring보다 먼저 쓴다.']

- `guard-condition` **가드 조건** [concept] 별칭=['가드 조건', '가드(guard)', '전이 가드']
  - 첫 등장: 13-state.html · 코드 src/13_state/02_state.py · …: int) -> None: """예약자 본인만 잠금 해제할 수 있다. 가드(guard) 조건도 상태 안에 있다.""" if user != se…
  - 용어집 정의(short): 전이가 일어나기 위해 추가로 만족해야 하는 조건(예: 예약자 본인만 잠금 해제).
  - 책 안의 기존 설명: ['13 · 가드 조건(예약자 본인만 잠금 해제 가능)']
  - 감사 메모: ['예시로만 정의된다.']

- `entry-action` **진입 동작** [concept] 별칭=['entry action', '진입 동작']
  - 첫 등장: 13-state.html · 코드 src/13_state/04_pythonic_fsm.py · …ame}-> {new.name}") self.status = new # 진입 동작은 대입 '뒤'에: _enter가 현재 상태를 근거로 판단할 수…
  - 용어집 정의(short): 어떤 상태로 들어갈 때마다 실행되는 동작(예: 그 상태에 필요 없는 데이터 정리).
  - 책 안의 기존 설명: ['13 · 진입 동작(entry action). 상태별 데이터의 수명을']

- `state-machine` **상태 기계** [concept] 별칭=['상태 기계', '유한 상태 기계']
  - 첫 등장: 13-state.html · 코드 src/13_state/03_state_vs_strategy.py · …은 주행 시간(분) 하나뿐인 좁은 인터페이스다. 전략은 Context의 상태 기계를 전혀 모른다. 어떤 정책이 다른 정책으로 '넘어가는' 일도 …
  - 용어집 정의(short): 유한한 상태 집합과, (현재 상태, 사건) → 다음 상태로 정해진 전이 규칙으로 동작을 기술하는 모델.
  - 감사 메모: ["13장 03 docstring에서 처음, 04 docstring에서 '유한 상태 기계'로 쓰인다."]

- `stateless` **무상태** [gloss] 별칭=['무상태']
  - 첫 등장: 13-state.html · 코드 src/13_state/02_state.py · …, 상태 객체가 '어느 킥보드의 상태인지'에 묶이지 않게 하기 위해서다(무상태 상태 객체는 여러 킥보드가 공유할 수도 있다 — 05 참고). 추…
  - 용어집 정의(short): 인스턴스마다 다른 필드(상태)를 갖지 않는 성질. 무상태 객체는 여러 곳이 하나를 공유해도 안전하다.
  - 책 안의 기존 설명: ['13 · 필드를 갖지 않는 상태']
  - 감사 메모: ["13장 02 docstring('무상태 상태 객체는 … 공유할 수도')이 05의 정의보다 먼저."]

- `typing-noreturn` **NoReturn** [concept] 별칭=['NoReturn']
  - 첫 등장: 13-state.html · 원고 · …el(): str {abstract} # _reject(action): NoReturn _state (위임) Available reserve, …
  - 용어집 정의(short): 함수가 정상적으로 반환하지 않음(항상 예외를 던짐)을 표시하는 반환 타입 힌트.

- `enum-enum` **Enum** [concept] 별칭=['Enum', 'auto()']
  - 첫 등장: 13-state.html · 원고 · … 상관없는 스케줄러 훅인데, 그 안에도 상태 분기가 들어왔다. 문자열을 Enum 으로 바꾸면 오타 문제 하나는 사라진다. 하지만 위의 네 가지는…
  - 용어집 정의(short): 이름 붙은 상수들의 닫힌 집합을 만드는 클래스. 오타는 AttributeError로 즉시 드러나며 auto()로 값을 자동 부여한다.
  - 감사 메모: ['앞 장에서 쓰였을 가능성.']

- `match-statement` **match 문** [concept] 별칭=['case _', 'match 문']
  - 첫 등장: 13-state.html · 원고 · …본은 거부"를 키가 없음 으로 표현하는 방식. 둘째, 같은 전이 함수를 match 문으로 쓴 next_status_match() 와의 비교. 셋…
  - 용어집 정의(short): 값의 구조를 패턴과 대조해 분기하는 문(파이썬 3.10+). | 로 여러 패턴, if로 가드, _ 로 나머지를 표현한다.

- `wildcard-pattern` **와일드카드 패턴** [concept] 별칭=['와일드카드', '와일드카드 패턴']
  - 첫 등장: 13-state.html · 코드 src/13_state/04_pythonic_fsm.py · …ANCE, E.REPAIRED): return S.AVAILABLE # 와일드카드 = 표의 '키 없음'. 이 줄을 빼먹으면 None이 반환되어 …
  - 용어집 정의(short): match 문에서 어떤 값과도 맞는 case _ 패턴.
  - 책 안의 기존 설명: ["13 · 와일드카드 = 표의 '키 없음'"]

- `collections-deque` **deque** [concept] 별칭=['deque']
  - 첫 등장: 13-state.html · 코드 src/13_state/04_pythonic_fsm.py · …ort annotations from collections import deque from enum import Enum, auto RESERV…
  - 용어집 정의(short): 양쪽 끝에서 빠르게 넣고 뺄 수 있는 큐 자료구조.

- `slots` **__slots__** [concept] 별칭=['__slots__']
  - 첫 등장: 13-state.html · 원고 · … 문구 그대로 "클래스가 바뀐 것처럼" 만드는 방법이다. A 부분에서는 __slots__ = () 가 공유 상태 객체를 어떻게 보호하는지 보라.…
  - 용어집 정의(short): 인스턴스가 가질 속성 이름을 고정해 __dict__를 없애는 클래스 속성. 메모리를 아끼고 새 속성 추가를 막는다.
  - 책 안의 기존 설명: ['13 · 인스턴스 속성 추가를 막는다']

- `no-show` **노쇼** [gloss] 별칭=['노쇼']
  - 첫 등장: 13-state.html · 원고 · … 문구, 허용되는 동작이 다르다. 예약은 10분이 지나면 저절로 풀리고 노쇼 수수료가 붙는다. 사용자가 아무것도 하지 않아도 시간이 흐르기만 하…
  - 용어집 정의(short): 예약해 두고 나타나지 않는 것.
  - 책 안의 기존 설명: ['13 · 예약 후 나타나지 않으면 부과']
  - 감사 메모: ['13장 1절 원고가 상수 주석보다 먼저.']

- `global-positioning-system` **GPS** [gloss] 별칭=['GPS']
  - 첫 등장: 13-state.html · 원고 · … 부족 으로 지도에서 내려야 한다. 운영팀은 정비 중 상태를, 관제팀은 GPS 신호가 끊긴 기기를 위한 분실 신고 상태를 요구했다. 상태가 늘자…
  - 용어집 정의(short): 위성 신호로 위치를 측정하는 시스템.

- `qr-code` **QR** [gloss] 별칭=['QR']
  - 첫 등장: 13-state.html · 원고 · … 사고가 났다. 정비 기사가 브레이크를 분해해 둔 킥보드를 한 사용자가 QR로 열었고, 주행이 시작됐다 . 원인은 출시 첫 주에 쓴 unlock…
  - 용어집 정의(short): 스마트폰으로 읽는 2차원 바코드.

- `time-to-live` **TTL** [gloss] 별칭=['RESERVATION_TTL', 'TTL']
  - 첫 등장: 13-state.html · 코드 src/13_state/01_naive.py · … """ from __future__ import annotations RESERVATION_TTL = 600 # 예약 유지 시간(초) — 10…
  - 용어집 정의(short): 데이터·예약 등이 유효한 유지 시간. 지나면 만료된다.
  - 책 안의 기존 설명: ['13 · 예약 유지 시간(초) — 10분']
  - 감사 메모: ['약어 풀이 없음(상수 주석이 의미만 설명).']

- `submission-for-approval` **상신** [gloss] 별칭=['상신', '전자결재']
  - 첫 등장: 13-state.html · 원고 · … 리팩터링 문제 2. 전자결재 문서 아래 Document 를 상태 패턴으로 바꿔라. 리팩터링 …
  - 용어집 정의(short): 전자결재에서 작성한 문서를 결재권자에게 올리는 것.

- `scheduler` **스케줄러** [gloss] 별칭=['스케줄러']
  - 첫 등장: 13-state.html · 원고 · …이가 정기 작업 안에 섞여 든다. tick() 은 원래 상태와 상관없는 스케줄러 훅인데, 그 안에도 상태 분기가 들어왔다. 문자열을 Enum 으…
  - 용어집 정의(short): 정해진 시각·주기에 작업을 실행해 주는 장치.

- `breadth-first-search` **BFS** [gloss] 별칭=['BFS']
  - 첫 등장: 13-state.html · 코드 src/13_state/04_pythonic_fsm.py · …터이기 때문에 가능한 정적 검증: 시작 상태에서 도달 가능한 상태 집합(BFS).""" # 표를 그래프의 간선 목록으로 읽는다. 상태 클래스 방…
  - 용어집 정의(short): 가까운 노드부터 차례로 방문하는 그래프 너비 우선 탐색.

- `metrics-collection` **지표 수집** [gloss] 별칭=['지표 수집']
  - 첫 등장: 13-state.html · 코드 src/13_state/02_state.py · …다. 모든 전이가 이 한 지점을 지나가므로 로그·통지(옵저버, 11장)·지표 수집을 붙이기 좋다. """ self.history.append(f…
  - 용어집 정의(short): 시스템 동작 수치(횟수·지연 등)를 모아 모니터링하는 것.

## 14-template-method.html — 28개

- `online-judge` **온라인 저지** [gloss] 별칭=['온라인 저지']
  - 첫 등장: 14-template-method.html · 코드 src/14_template_method/01_naive.py · … 메서드 · 순진한 설계] 언어별 채점기 세 개를 복사-붙여넣기로 만든 온라인 저지. 상황: 코딩 교육 플랫폼 '코드랩'의 개발자 도윤은 파이썬…
  - 용어집 정의(short): 제출된 프로그램을 테스트 입력으로 자동 실행해 정답 여부·시간 초과 등을 판정하는 채점 시스템.

- `hollywood-principle` **할리우드 원칙** [concept] 별칭=['할리우드 원칙']
  - 첫 등장: 14-template-method.html · 코드 src/14_template_method/02_template_method.py · … """[Abstract Class] 채점 알고리즘의 골격을 소유한다. 할리우드 원칙("우리에게 전화하지 마라, 우리가 전화하겠다"): 하위 클…
  - 용어집 정의(short): "우리에게 전화하지 마라, 우리가 전화하겠다" — 하위 코드는 상위 코드를 부르지 않고, 상위 코드(골격·프레임워크)가 언제 하위 코드를 부를지 정한다는 설계 원칙.
  - 책 안의 기존 설명: ['14 · 하위 클래스는 judge()를 부르지도, 단계를 부르는']
  - 감사 메모: ['14장 02 코드 docstring에서 정의, 04 docstring에서 재사용.']

- `inversion-of-control` **제어의 역전** [concept] 별칭=['제어가 역전', '제어의 역전']
  - 첫 등장: 14-template-method.html · 원고 · …validate(), compile() judge()가 단계를 호출한다(제어의 역전). 하위 클래스는 judge()를 부르지 않는다. outpu…
  - 용어집 정의(short): 흐름의 제어권이 사용자 코드가 아니라 골격·프레임워크 쪽에 있어서, 사용자 코드는 불리기만 하는 구조.
  - 책 안의 기존 설명: ['14 · 하위 클래스는 단계만 채우고, 언제 불릴지는']
  - 감사 메모: ["14장 그림 14-1 메모 '(제어의 역전)'이 docstring보다 먼저 읽힌다."]

- `axis-of-change` **변경 축** [concept] 별칭=['변경 축', '변이 축', '변이의 축']
  - 첫 등장: 14-template-method.html · 코드 src/14_template_method/02_template_method.py · …oatTolerantJavaJudge… 언어 수만큼 클래스가 곱해진다. 변이의 축이 둘이 되는 순간 템플릿 메서드는 버거워진다. 03_strat…
  - 용어집 정의(short): 서로 다른 이유·주체·시점으로 독립적으로 바뀌는 요구의 방향. 축마다 분리하는 것이 설계의 기준이 된다.

- `fragile-base-class` **취약한 기반 클래스** [concept] 별칭=['fragile base class', '취약한 기반 클래스']
  - 첫 등장: 14-template-method.html · 원고 · …해야 한다 결합 하위 클래스가 상위 클래스의 내부 호출 순서에 의존한다(취약한 기반 클래스) 단계는 골격을 모른다 핵심 정리 템플릿 메서드와 전…
  - 용어집 정의(short): 상위 클래스의 내부 호출 순서를 조금만 바꿔도 그것에 암묵적으로 의존하던 하위 클래스가 깨지는 문제.
  - 책 안의 기존 설명: ['14 · 상위 클래스가 골격을 조금만 바꿔도 하위 클래스가']
  - 감사 메모: ['14장 4절 비교표에 먼저 이름만 나오고, 정의는 6절.']

- `yo-yo-problem` **요요 문제** [concept] 별칭=['요요 문제']
  - 첫 등장: 14-template-method.html · 원고 · …은 단계가 어떤 맥락에서 불리는지 알기 위해 상위 클래스를 오가야 한다(요요 문제). 이 패턴을 쓰지 말아야 할 때 변이의 축이 둘 이상일 때.…
  - 용어집 정의(short): 상속 계층이 깊을 때 동작을 이해하려고 하위·상위 클래스를 계속 오가야 하는 문제.
  - 책 안의 기존 설명: ['14 · 상위 클래스를 오가야 한다(요요 문제)']

- `don-t-repeat-yourself` **DRY** [concept] 별칭=['DRY']
  - 첫 등장: 14-template-method.html · 원고 · … 관련 패턴 얻는 것과 잃는 것 얻는 것 : 공통 절차가 한 곳에 있다(DRY). 순서와 필수 단계를 강제할 수 있다. 공통 요구사항이 변경 한…
  - 용어집 정의(short): 같은 지식을 두 곳 이상에 쓰지 말라는 원칙(Don't Repeat Yourself).
  - 감사 메모: ['약어 풀이 없음.']

- `final` **typing.final** [gloss] 별칭=['@final', 'typing.final']
  - 첫 등장: 14-template-method.html · 코드 src/14_template_method/02_template_method.py · …--------------------------------------- @final def judge(self, sub: Submission, …
  - 용어집 정의(short): 메서드·클래스를 재정의·상속하지 말라고 타입 검사기에 알리는 데코레이터. 런타임에는 아무것도 막지 않는다.
  - 책 안의 기존 설명: ["14 · 하위 클래스가 '순서'를 재정의하지 말라는 선언"]

- `tempfile` **tempfile** [gloss] 별칭=['mkdtemp', 'tempfile']
  - 첫 등장: 14-template-method.html · 코드 src/14_template_method/01_naive.py · …import annotations import shutil import tempfile import time from dataclasses im…
  - 용어집 정의(short): 임시 파일·디렉터리를 안전하게 만드는 표준 라이브러리.

- `pathlib-path` **pathlib** [gloss] 별칭=['pathlib']
  - 첫 등장: 14-template-method.html · 코드 src/14_template_method/01_naive.py · … from dataclasses import dataclass from pathlib import Path from typing import C…
  - 용어집 정의(short): 파일 경로를 객체로 다루는 표준 라이브러리(/ 연산자로 경로 결합).

- `time-perf-counter` **time.perf_counter** [gloss] 별칭=['perf_counter', 'time.perf_counter']
  - 첫 등장: 14-template-method.html · 코드 src/14_template_method/01_naive.py · …pected) in enumerate(tests, 1): start = time.perf_counter() out = sub.solve(inp)…
  - 용어집 정의(short): 짧은 구간의 경과 시간을 재는 고해상도 시계 함수.

- `tracemalloc` **tracemalloc** [gloss] 별칭=['tracemalloc']
  - 첫 등장: 14-template-method.html · 원고 · … 검사 → 메모리 검사 → 출력 비교"를 고정하고, 측정은 기본 구현( tracemalloc )이 있는 measure() 훅으로 연다. Pyth…
  - 용어집 정의(short): 파이썬 메모리 할당을 추적해 최대 사용량 등을 재는 표준 라이브러리.

- `sandbox` **샌드박스** [gloss] 별칭=['sandbox', '샌드박스']
  - 첫 등장: 14-template-method.html · 원고 · …발자 도윤은 파이썬 제출물 채점기를 만들었다. 절차는 단순했다. 소스를 샌드박스에 저장하고, 실행하고, 테스트 케이스마다 출력을 기대값과 비교한…
  - 용어집 정의(short): 신뢰할 수 없는 코드를 다른 시스템과 격리해 실행하는 환경.
  - 책 안의 기존 설명: ['14 · 제출물마다 격리된 디렉터리']
  - 감사 메모: ['14장 1절 원고에서 먼저 설명 없이 쓰인다.']

- `accepted` **AC** [gloss] 별칭=['AC']
  - 첫 등장: 14-template-method.html · 코드 src/14_template_method/01_naive.py · …t | None = None) -> str: """채점 후 판정 문자열(AC/WA/TLE/RE)을 돌려준다.""" # 준비 단계: 제출물마다 격…
  - 용어집 정의(short): 온라인 저지 판정: 모든 테스트를 통과한 정답.

- `wrong-answer` **WA** [gloss] 별칭=['WA']
  - 첫 등장: 14-template-method.html · 코드 src/14_template_method/01_naive.py · … None = None) -> str: """채점 후 판정 문자열(AC/WA/TLE/RE)을 돌려준다.""" # 준비 단계: 제출물마다 격리된 …
  - 용어집 정의(short): 온라인 저지 판정: 출력이 기대값과 다른 오답.

- `time-limit-exceeded` **TLE** [gloss] 별칭=['TLE']
  - 첫 등장: 14-template-method.html · 코드 src/14_template_method/01_naive.py · …ne = None) -> str: """채점 후 판정 문자열(AC/WA/TLE/RE)을 돌려준다.""" # 준비 단계: 제출물마다 격리된 디렉터…
  - 용어집 정의(short): 온라인 저지 판정: 시간 제한 초과.
  - 감사 메모: ["'느린 오답은 TLE'처럼 쓰임새만 드러난다."]

- `runtime-error` **RE** [gloss] 별칭=['RE', '런타임 에러']
  - 첫 등장: 14-template-method.html · 코드 src/14_template_method/01_naive.py · … None) -> str: """채점 후 판정 문자열(AC/WA/TLE/RE)을 돌려준다.""" # 준비 단계: 제출물마다 격리된 디렉터리. 이…
  - 용어집 정의(short): 온라인 저지 판정: 실행 중 예외로 비정상 종료.
  - 책 안의 기존 설명: ['14 · 제출물이 던진 예외 = 런타임 에러']

- `compile-error` **CE** [gloss] 별칭=['CE']
  - 첫 등장: 14-template-method.html · 코드 src/14_template_method/01_naive.py · …urce: # 컴파일 흉내: main이 없으면 링크 실패 return "CE" for i, (inp, expected) in enumerate(…
  - 용어집 정의(short): 온라인 저지 판정: 컴파일(또는 사전 검증) 실패.

- `memory-limit-exceeded` **MLE** [gloss] 별칭=['MLE']
  - 첫 등장: 14-template-method.html · 원고 · …0만 개를 쌓는 풀이가 채점 서버를 죽였다." 모든 언어에 메모리 제한(MLE 판정)을 추가하라. 판정 규칙(한도를 넘으면 MLE, 비교보다 먼…
  - 용어집 정의(short): 온라인 저지 판정: 메모리 제한 초과.
  - 책 안의 기존 설명: ['14 · 모든 언어에 메모리 제한(MLE 판정)']

- `special-judge` **특수 저지** [gloss] 별칭=['특수 저지']
  - 첫 등장: 14-template-method.html · 원고 · …antJavaJudge 가 더 필요하다. 여기에 "답의 순서를 무시하는 특수 저지"까지 더하면 클래스 수는 언어 수 × 비교 방식 수가 된다. …
  - 용어집 정의(short): 답이 여러 개일 수 있는 문제에서 정확 일치 대신 별도 규칙으로 출력을 판정하는 채점 방식.
  - 책 안의 기존 설명: ['14 · 답이 여러 개인 문제']

- `checker` **체커** [gloss] 별칭=['Checker', '체커']
  - 첫 등장: 14-template-method.html · 원고 · …여럿을 묶은 Toolchain 값 객체가 맡고, 비교 축은 함수 하나( Checker )가 맡는다. Judge.judge() 의 본문이 02와 …
  - 용어집 정의(short): 실제 출력과 기대 출력을 받아 일치 여부를 판정하는 함수.
  - 책 안의 기존 설명: ['14 · (실제 출력, 기대 출력) → 일치 여부']

- `toolchain` **툴체인** [gloss] 별칭=['Toolchain', '툴체인']
  - 첫 등장: 14-template-method.html · 원고 · …. 10장의 전략 패턴을 그대로 적용했다. 언어 축은 단계 여럿을 묶은 Toolchain 값 객체가 맡고, 비교 축은 함수 하나( Checker…
  - 용어집 정의(short): 한 언어의 소스를 검증·컴파일·실행하는 도구 묶음.
  - 책 안의 기존 설명: ['14 · 언어별 단계 묶음']

- `extensible-markup-language` **XML** [gloss] 별칭=['XML']
  - 첫 등장: 14-template-method.html · 원고 · …트 생성기 세 개 코드랩 운영팀은 주간 채점 통계를 CSV, JSON, XML로 내려받는다. 아래 코드를 템플릿 메서드로 바꿔라. 원래 코드에 …
  - 용어집 정의(short): 태그로 구조를 표현하는 텍스트 데이터 형식.

- `linking` **링크** [gloss] 별칭=['링크', '링크 실패']
  - 첫 등장: 14-template-method.html · 코드 src/14_template_method/01_naive.py · … not in sub.source: # 컴파일 흉내: main이 없으면 링크 실패 return "CE" for i, (inp, expected)…
  - 용어집 정의(short): 컴파일된 조각들과 라이브러리를 이어 실행 파일을 만드는 단계.

- `interpreter` **인터프리터** [gloss] 별칭=['인터프리터']
  - 첫 등장: 14-template-method.html · 코드 src/14_template_method/02_template_method.py · …r) -> str: """프로그램 실행. 실제로는 subprocess로 인터프리터/바이너리를 부르는 자리다.""" # --------------…
  - 용어집 정의(short): 소스를 미리 실행 파일로 만들지 않고 읽어 가며 실행하는 프로그램.

- `cgroup-setrlimit` **cgroup·setrlimit** [gloss] 별칭=['cgroup', 'cgroup·setrlimit', 'setrlimit']
  - 첫 등장: 14-template-method.html · 코드 src/14_template_method/solutions/ex4_memory_limit.py · …제출물(solve 함수)의 파이썬 할당 최대치를 잰다. 실제 채점기라면 cgroup이나 setrlimit로 프로세스 메모리를 제한하겠지만, 골격…
  - 용어집 정의(short): 운영체제가 프로세스의 메모리·CPU 사용량을 제한하는 수단.

- `java-virtual-machine` **JVM** [gloss] 별칭=['JVM']
  - 첫 등장: 14-template-method.html · 코드 src/14_template_method/solutions/ex4_memory_limit.py · … """[새 훅] 실행 + 최대 메모리. 기본은 tracemalloc. JVM처럼 측정 방식이 다른 언어는 재정의한다. 훅으로 연 이유: 'ML…
  - 용어집 정의(short): 자바 바이트코드를 실행하는 가상 머신.

- `heap` **힙** [gloss] 별칭=['힙']
  - 첫 등장: 14-template-method.html · 코드 src/14_template_method/solutions/ex4_memory_limit.py · …vaJudge(Judge): """[Concrete Class] JVM 힙 기준 측정을 흉내 내 measure 훅을 재정의한다.""" def c…
  - 용어집 정의(short): 실행 중 동적으로 할당되는 객체가 놓이는 메모리 영역.

## 15-iterator.html — 14개

- `lazy-evaluation` **지연 평가** [concept] 별칭=['지연 평가', '지연성']
  - 첫 등장: 15-iterator.html · 코드 src/15_iterator/03_pythonic.py · …를 섞어서. 섞는 시점이 '첫 next()' 이후라는 점이 제너레이터의 지연성이다.""" yield start, pl[start] rest = …
  - 용어집 정의(short): 값이 실제로 요구될 때까지 계산(또는 요청)을 미루는 평가 방식. 제너레이터는 소비자가 next()를 부를 때만 다음 값까지 진행한다.
  - 책 안의 기존 설명: ['15 · 제너레이터는 소비자가 값을 요구할 때만 진행']
  - 감사 메모: ["15장 03_pythonic.py docstring('섞는 시점이 첫 next() 이후라는 점이 제너레이터의 지연성이다')이 5.2절 제목보다 먼저 나온다."]

- `mixin` **믹스인** [concept] 별칭=['믹스인']
  - 첫 등장: 15-iterator.html · 코드 src/15_iterator/03_pythonic.py · …s__`, `__reversed__`, `index`, `count`를 믹스인으로 얻는다. """ from __future__ import an…
  - 용어집 정의(short): 단독으로 쓰기보다 상속해서 메서드 묶음을 얻기 위해 만든 클래스(예: collections.abc.Sequence가 __iter__·__contains__ 등을 제공).
  - 책 안의 기존 설명: ['15 · 두 메서드만 쓰고 나머지 순회 관련 연산을 물려받는다']

- `generator-expression` **제너레이터 표현식** [concept] 별칭=['제너레이터 식', '제너레이터 표현식']
  - 첫 등장: 15-iterator.html · 원고 · … 곳으로 옮긴다. 그러면 업무 로직은 "필터 + 앞에서 n개"가 되어, 제너레이터 식과 islice 로 표현된다. 조기 종료를 손으로 처리할 필…
  - 용어집 정의(short): (x for x in ...) 꼴로 쓰는, 리스트를 만들지 않고 값을 하나씩 내는 표현식.
  - 감사 메모: ["10장 이후 코드(next((f for … ), default), sum(… for …))에서 이름 없이 쓰이고 15장에서 '제너레이터 식'으로 불린다."]

- `exhaustion` **고갈** [concept] 별칭=['고갈']
  - 첫 등장: 15-iterator.html · 원고 · …eld from 으로 바뀐 한 단어뿐이다. 후반 데모 [5]와 [6]은 고갈 버그와 in 연산자의 함정을 재현한다. …
  - 용어집 정의(short): 이터레이터(제너레이터 객체)를 끝까지 소비해 더 이상 값이 나오지 않는 상태. 두 번째 순회는 예외 없이 빈 결과가 된다.
  - 책 안의 기존 설명: ["15 · 제너레이터 객체를 변수에 담아 두 번 쓰는' 고갈"]

- `collections-abc` **collections.abc** [concept] 별칭=['Sequence', 'collections.abc']
  - 첫 등장: 15-iterator.html · 원고 · …미리보기는 chain + islice 로 조립된다. Playlist 가 Sequence 를 상속하면서 __iter__ 를 직접 쓰지 않게 된 점…
  - 용어집 정의(short): Iterator·Sequence 같은 컨테이너 추상 기반 클래스를 모은 표준 모듈. 필수 메서드만 구현하면 나머지를 믹스인으로 제공한다.

- `frame` **실행 프레임** [concept] 별칭=['gi_frame', '실행 프레임']
  - 첫 등장: 15-iterator.html · 원고 · …고 반복자를 직렬화하거나 복제해야 할 때도 그렇다. 제너레이터의 상태는 실행 프레임 안에 갇혀 있어서 공개 인터페이스로는 바깥에서 읽을 수 없다…
  - 용어집 정의(short): 함수 실행 중의 지역 변수와 현재 위치를 담은 객체. 제너레이터의 상태가 여기에 갇혀 있다.

- `pagination` **페이지네이션** [gloss] 별칭=['커서 토큰', '페이지 토큰', '페이지네이션']
  - 첫 등장: 15-iterator.html · 원고 · … 유저의 '좋아요 표시한 곡'은 2만 곡이 넘고, 서버는 이를 50곡씩 페이지 토큰과 함께 준다. 리스트만 다룰 줄 아는 재생기에 맞추려고 지안…
  - 용어집 정의(short): 큰 목록을 페이지 단위로 나눠 주고, 다음 페이지를 토큰으로 요청하게 하는 API 방식.
  - 책 안의 기존 설명: ['15 · 서버는 이를 50곡씩 페이지 토큰과 함께 준다']

- `crossfade` **크로스페이드** [gloss] 별칭=['크로스페이드']
  - 첫 등장: 15-iterator.html · 원고 · …. 7. 연습문제 개념 문제 1. self를 반환하는 컬렉션 멜로디의 '크로스페이드 추천' 기능은 앨범의 모든 곡 쌍을 중첩 for 로 만든다.…
  - 용어집 정의(short): 앞 곡이 작아지며 다음 곡이 커지도록 겹쳐 전환하는 재생 효과.

- `cursor` **커서** [gloss] 별칭=['커서']
  - 첫 등장: 15-iterator.html · 원고 · … 곡" 미리보기를 추가했는데, 미리보기가 다음 곡을 계산하려고 재생기의 커서를 실제로 움직였다. 사용자가 미리보기를 열 때마다 곡이 건너뛰어졌다…
  - 용어집 정의(short): 순회 중 '어디까지 왔는가'를 가리키는 위치 상태.
  - 책 안의 기존 설명: ['15 · 순회 상태(커서)를 컬렉션에서 떼어 내']
  - 감사 메모: ['15장 1절에서 먼저 설명 없이 쓰인다.']

- `big-o-notation` **빅오 표기** [gloss] 별칭=['O(n)', '빅오 표기']
  - 첫 등장: 15-iterator.html · 코드 src/15_iterator/02_iterator.py · … None = None) -> None: """순서를 미리 섞어 둔다. O(n)이지만 플레이리스트는 메모리에 있는 컬렉션이다.""" super(…
  - 용어집 정의(short): 입력 크기에 따라 비용이 늘어나는 정도를 나타내는 표기.

- `peek` **peek** [gloss] 별칭=['peek']
  - 첫 등장: 15-iterator.html · 원고 · …m_api() 가 첫 곡 전에 무엇을 하는지, UpNextPreview.peek() 가 왜 next_track() 을 부를 수밖에 없는지도 살펴…
  - 용어집 정의(short): 다음 값을 소비하지 않고 미리 보기만 하는 연산.

- `random-access` **무작위 접근** [gloss] 별칭=['무작위 접근']
  - 첫 등장: 15-iterator.html · 원고 · …리 버그 가능성 Sequence 믹스인 인덱스 접근이 자연스러운 컬렉션 무작위 접근이 불가능한 원천(페이지 API)에는 맞지 않는다 이 패턴을(…
  - 용어집 정의(short): 임의 위치의 원소에 바로 접근하는 것(인덱스 접근).

- `materialization` **구체화** [concept] 별칭=['구체화']
  - 첫 등장: 15-iterator.html · 원고 · … 번 순회해도 되는가"를 문서화하거나, 필요하면 list() 로 한 번 구체화하라. 6. 트레이드오프와 관련 패턴 설계 선택지 방법 쓸 때 대가…
  - 용어집 정의(short): 지연된 이터러블을 list() 등으로 끝까지 펼쳐 메모리에 실제 컬렉션으로 만드는 것.

- `exhaustive-search` **전수 탐색** [gloss] 별칭=['전수 탐색']
  - 첫 등장: 15-iterator.html · 코드 src/15_iterator/solutions/ex4_smart_shuffle.py · … 조건에서 가능한 최소 연속 횟수를 낸다(2~7곡 무작위 1,500회를 전수 탐색 결과와 대조해 확인). 단 시작 곡이 이미 과반 아티스트라면 …
  - 용어집 정의(short): 가능한 모든 경우를 빠짐없이 확인하는 방법.
