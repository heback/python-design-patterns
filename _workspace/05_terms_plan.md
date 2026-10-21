# 용어 정의 작업 계획 — 2판 (용어 455개, 00장은 완료)

첫 등장 장별. level=concept → 1~2문장, level=gloss → 짧은 괄호 풀이. 등록부: chapters/terms.json

## 00-intro.html — 51개 [완료]

- `hook` **훅** [concept] 별칭=['hook', '훅']
  - 첫 등장: 00-intro.html · 원고 · …는 대개 그냥 함수다. 전략, 커맨드, 팩토리 메서드의 생성 ⟦hook⟧훅 이 함수 하나로 줄어드는 경우가 많다. 훅(hook)이란 흐름을 소유…
  - 용어집 정의(short): 흐름을 소유한 쪽(상위 클래스·프레임워크·언어 런타임)이 정해 둔 시점에 호출해 주도록 비워 둔 확장 지점으로, 하위 클래스가 오버라이드하는 메서드, 주입받는 함수, `__init_subclass__`처럼 언어가 특정 순간에 불러 주는 특수 메서드가 모두 여기에 든다. GoF 템플릿 메서드의 좁은 의미의 '훅 연산'은 그중 기본 구현(흔히 no-op)이 있어 하위 클래스가 필요할 때만 재정의하는 단계로, 반드시 구현해야 하는 추상 단계와 구별된다.
  - 책 안의 기존 설명: ['14 · 기본 동작이 있고 필요한 하위 클래스만 재정의한다']
  - 감사 메모: ["범위 안 첫 사용은 12장 03_pythonic.py docstring('from_payload()/retarget() 훅만 재정의')과 13장 원고('스케줄러 훅')로, 일반 의미(정해진 자리에서 불리는 확장 지점)이며 설명이 없다. 책 전체로는 00·01·04장(생성 훅, 리셋 훅, __init_subclass__는 훅)에서 이미 정의 없이 쓰인다. 14장 #structure 표는 GoF의 좁은 의미(기본 구현이 있는 선택적 재정의 연산)를 '추상 단계(primitive operation, 기본값 없음·반드시 구현)'와 대비해 정의하지만, 이것이 일반 의미의 한 종류라는 관계는 명시하지 않는다. 14장은 같은 장 안에서 '데이터 훅'(클래스 속성 separator), unittest setUp/tearDown, None 허용 필드(03의 Toolchain.validate/compile)도 훅이라 부르므로 좁은 의미를 넓혀 쓴다."]

- `extension-point` **확장 지점** [concept] 별칭=['확장 지점']
  - 첫 등장: 00-intro.html · 원고 · …않는다. 우리가 정의하고 우리가 구현하는 ⟦extension-point⟧확장 지점 (기존 코드를 고치지 않고 새 동작을 끼워 넣도록 설계가 일부…
  - 용어집 정의(short): 기존 코드를 고치지 않고 새 동작을 끼워 넣을 수 있도록 설계가 일부러 열어 둔 자리(추상 메서드, 주입 인자, 등록부 등).

- `indirection-layer` **간접층** [concept] 별칭=['간접 층', '간접층']
  - 첫 등장: 00-intro.html · 원고 · …는 것은, 그 1년 동안 모든 독자가 ⟦indirection-layer⟧간접층 (호출하는 쪽과 실제 일을 하는 쪽 사이에 끼워 넣은 중간 단계.…
  - 용어집 정의(short): 호출하는 쪽과 실제 일을 하는 쪽 사이에 끼워 넣은 중간 단계(퍼사드, 프록시, 인터페이스 등). 변경을 흡수하지만 읽는 사람이 거쳐야 할 단계도 늘린다.
  - 감사 메모: ["01장에서 먼저 쓰였음(정의 여부 확인 필요). 08·09장에서 정의 없이 '간접 층'으로 쓰인다."]

- `composition-root` **합성 루트** [concept] 별칭=['Composition Root', 'Composition root', 'composition root', 'composition_root', '조립 지점', '합성 루트']
  - 첫 등장: 00-intro.html · 원고 · …알 수도 바꿀 수도 없다. 파이썬에서는 ⟦composition-root⟧composition root (프로그램 시작 지점에서 구체 클래스를 고…
  - 용어집 정의(short): 프로그램 시작 지점에서 구체 클래스를 고르고 객체 그래프 전체를 한 번에 조립해 주입하는 단 한 곳; 구체 타입과 설정을 아는 코드를 여기로 모은다.
  - 책 안의 기존 설명: ['02 · 프로그램 시작 지점(composition root) 한 곳', '08 · 서브시스템을 한 번 만들어 퍼사드와']
  - 감사 메모: ["08장 02_facade.py 주석 '조립 지점: …'이 사실상 정의. 영문 'composition root'는 99장에서 쓰이며 04장에서 먼저 나왔을 가능성."]

- `dependency-injection` **의존성 주입** [concept] 별칭=['생성자 주입', '생성자로 주입', '의존성 주입', '주입으로 해결', '주입하거나']
  - 첫 등장: 00-intro.html · 원고 · …하는 단 한 곳)에서 하나 읽어 ⟦dependency-injection⟧주입하거나 (필요한 객체를 스스로 만들거나 전역에서 꺼내지 않고 생성자·…
  - 용어집 정의(short): 객체가 필요한 협력 객체를 스스로 만들거나 전역에서 꺼내지 않고 생성자·인자로 바깥에서 받게 하는 기법; 의존성이 시그니처에 드러나 테스트에서 교체할 수 있다.
  - 감사 메모: ['08장은 이유(테스트용 가짜, 인스턴스 공유)만 설명. 04장 등 앞 장에서 정의되었을 가능성.']

- `combinatorial-explosion` **조합 폭발** [concept] 별칭=['조합 폭발', '조합의 수만큼 클래스가 생긴다']
  - 첫 등장: 00-intro.html · 원고 · …마다 하위 클래스를 만들면 ⟦combinatorial-explosion⟧조합의 수만큼 클래스가 생긴다 . 독립적인 선택지가 늘 때마다 클래스 수…
  - 용어집 정의(short): 독립적인 선택지들의 조합마다 클래스를 만들 때 클래스 수가 곱(예: 기능 n개면 2^n)으로 늘어나는 현상.
  - 책 안의 기존 설명: ['00 · 규칙 조합마다 클래스가 필요해 조합 폭발이 일어난다']

- `contract` **계약** [concept] 별칭=['계약', '계약 하나면', '계약에 ABC', '계약을 명시', '명목적 계약', '빌더의 계약', '인터페이스 계약']
  - 첫 등장: 00-intro.html · 원고 · …"대출과 현재 금액을 받아 조정된 금액을 돌려준다"는 ⟦contract⟧계약 하나면 감면·면제·상한이 모두 들어간다. 계약이란 인터페이스가 호출…
  - 용어집 정의(short): 인터페이스가 호출자에게 약속하는 입력·출력·실패 방식·불변 조건의 총체; 구현은 시그니처뿐 아니라 이 약속을 지켜야 대체 가능하다.

- `forces` **힘** [concept] 별칭=['forces', '힘', '힘(forces)']
  - 첫 등장: 00-intro.html · 원고 · … 쓰이는 넷을 고른 것이다. "서로 당기는 요구들", 즉 ⟦forces⟧힘(forces) (예: 유연성과 단순성처럼 한 설계 상황에서 서로 반대…
  - 용어집 정의(short): 한 설계 상황에서 서로 당기는 요구·제약들(예: 유연성 대 단순성); Christopher Alexander의 건축 패턴에서 비롯해 패턴 문헌에 널리 쓰인 개념이다.
  - 책 안의 기존 설명: ['00 · "서로 당기는 요구들", 즉 힘(forces)']

- `creational-structural-behavioral-patterns` **생성·구조·행위 패턴** [concept] 별칭=['구조 패턴', '생성 패턴', '생성·구조·행위 패턴', '행위 패턴']
  - 첫 등장: 00-intro.html · 원고 · …eational-structural-behavioral-patterns⟧생성 패턴 은 객체를 누가, 언제, 무엇으로 만드는지를 클라이언트로부터 …
  - 용어집 정의(short): GoF가 목적에 따라 나눈 패턴 분류: 객체 생성을 떼어 내는 생성 패턴, 클래스·객체를 엮어 큰 구조를 만드는 구조 패턴, 책임과 알고리즘을 나누고 소통 방식을 정하는 행위 패턴.
  - 책 안의 기존 설명: ['00 · 생성 패턴 은 객체를 누가, 언제, 무엇으로 만드는지']

- `code-smell` **코드 냄새** [concept] 별칭=['냄새', '코드 냄새']
  - 첫 등장: 00-intro.html · 원고 · …규칙이 지점별로 조합되고 순서가 의미를 가진다"는 ⟦code-smell⟧냄새 (코드 냄새: 당장 버그는 아니지만 설계 문제가 숨어 있음을 알리는…
  - 용어집 정의(short): 당장 버그는 아니지만 설계 문제가 숨어 있음을 시사하는 코드의 징후(분기 복제, 전역 바꿔치기, 테스트용 뒷문 등).
  - 감사 메모: ["04장에서 '같은 냄새가 난다'로 먼저 쓰였음. 99장 6절 제목."]

- `refactoring` **리팩터링** [concept] 별칭=['리팩터링']
  - 첫 등장: 00-intro.html · 원고 · …은 그대로 두고 내부 구조만 고치는 이런 작업을 ⟦refactoring⟧리팩터링 이라 하며, 동작 보존이 첫 조건이다. 코드에 처음 나오는 도구…
  - 용어집 정의(short): 외부에서 관찰되는 동작은 그대로 두고 코드의 내부 구조만 개선하는 일; 동작 보존이 첫 조건이다.
  - 책 안의 기존 설명: ['00 · 리팩터링은 동작을 보존해야 하므로']

- `test-double` **테스트 대역** [concept] 별칭=['가짜 객체', '가짜 리더', '가짜 클래스', '가짜 판독기', '가짜를 넣', '테스트 대역', '테스트 더블']
  - 첫 등장: 00-intro.html · 원고 · …대개 우리가 고칠 수 없는 라이브러리), 함수, ⟦test-double⟧테스트 대역 (테스트에서 실제 협력 객체 대신 끼워 넣는 가짜 객체)처럼…
  - 용어집 정의(short): 테스트에서 실제 협력 객체 대신 끼워 넣는 가짜·스텁 등 대체 객체; 실제 장비·네트워크 없이 대상 로직만 검증하게 해 준다.

- `context` **컨텍스트(전략·상태의 Context)** [concept] 별칭=['Context', '[Context]', '컨텍스트(전략·상태의 Context)', '컨텍스트의 전이표']
  - 첫 등장: 00-intro.html · 원고 · …클래스 다이어그램과 역할 표, 코드 docstring의 ⟦context⟧[Context] 같은 역할 태그. 역할 태그는 그 클래스가 패턴 안에서…
  - 용어집 정의(short): 전략·상태 패턴에서 교체 가능한 전략(또는 상태) 객체를 보유하고 일을 위임하는 쪽 객체의 역할명(10·13장에서 정의).

- `state-transition` **상태 전이** [concept] 별칭=['상태 전이', '시간 기반 전이', '전이 결정', '전이 규칙', '전이표']
  - 첫 등장: 00-intro.html · 원고 · … 행동이 내부 상태에 따라 바뀌고, 그 ⟦state-transition⟧상태 전이 규칙 이 복잡할 때" 전이를 상태 객체로 옮기는 것이다. 상태…
  - 용어집 정의(short): 객체가 사건에 따라 한 상태에서 다른 상태로 옮겨 가는 것; 전이표는 (현재 상태, 사건) → 다음 상태를 표로 적은 것이다.
  - 감사 메모: ["13장 1절('시간이 흐르기만 하면 일어나는 전이다')부터 '전이'가 설명 없이 쓰인다."]

- `dictionary-dispatch` **딕셔너리 디스패치** [concept] 별칭=['딕셔너리 디스패치']
  - 첫 등장: 00-intro.html · 원고 · … 키 → 함수 딕셔너리를 조회하는 ⟦dictionary-dispatch⟧딕셔너리 디스패치 로 충분한 경우가 많다. 변하는 것이 무엇인지 먼저 물…
  - 용어집 정의(short): if/elif 분기 대신 키 → 함수(또는 클래스) 딕셔너리를 조회해 실행할 것을 고르는 기법.

- `chain-of-responsibility` **책임 연쇄 패턴** [concept] 별칭=['책임 연쇄', '책임 연쇄 패턴']
  - 첫 등장: 00-intro.html · 원고 · … 쌓는 데코레이터(6장)나 ⟦chain-of-responsibility⟧책임 연쇄 (요청을 처리할 수 있는 객체들을 사슬로 잇고, 각자 처리하거…
  - 용어집 정의(short): 요청을 처리할 수 있는 객체들을 사슬로 잇고, 각 객체가 처리하거나 다음으로 넘기게 하는 GoF 행위 패턴(이 책의 범위 밖).

- `hidden-dependency` **숨은 의존성** [concept] 별칭=['숨은 의존성', '의존성을 숨긴다']
  - 첫 등장: 00-intro.html · 원고 · …싱글턴은 그것을 막고, 전역 접근으로 ⟦hidden-dependency⟧의존성을 숨긴다 . 숨은 의존성이란 생성자나 인자에 드러나지 않고 메서드…
  - 용어집 정의(short): 생성자·인자 등 시그니처에 드러나지 않고 메서드 본문 안에서 전역 객체를 직접 꺼내 쓰는 의존; 호출자가 알 수도 바꿀 수도 없다.
  - 책 안의 기존 설명: ['04 · 시그니처만 봐서는 이 메서드가 전역 감사 로그에 쓴다는 것을 알 수 없다']

- `unified-modeling-language` **UML** [concept] 별칭=['UML']
  - 첫 등장: 00-intro.html · 원고 · …을 때 남아야 할 것은 ⟦unified-modeling-language⟧UML (클래스와 그 관계를 그림으로 나타내는 표준 표기법. 각 장 3절…
  - 용어집 정의(short): 클래스·객체·상호작용을 그림으로 나타내는 표준 모델링 표기법; 이 책의 구조 다이어그램은 UML 클래스 다이어그램이다.

- `gang-of-four` **GoF** [concept] 별칭=['GoF']
  - 첫 등장: 00-intro.html · 원고 · …. 2. 세 원칙의 재해석: 원칙에서 패턴으로 ⟦gang-of-four⟧GoF 는 Gamma·Helm·Johnson·Vlissides 네 저자(…
  - 용어집 정의(short): 1994년 『Design Patterns』를 쓴 Gamma·Helm·Johnson·Vlissides 네 저자, 또는 그 책; 이 책이 다루는 23개 고전 패턴의 출처다.

- `duck-typing` **덕 타이핑** [concept] 별칭=['덕 타이핑']
  - 첫 등장: 00-intro.html · 원고 · …게 한다. 그 판단에 쓰는 도구는 다섯 가지다. ⟦duck-typing⟧덕 타이핑 . 파이썬에서는 객체의 선언된 타입이 아니라 실제로 가진 메서…
  - 용어집 정의(short): 객체의 선언된 타입이 아니라 실제로 가진 메서드·속성으로 협력 가능 여부가 정해지는 파이썬의 동적 타이핑 방식.
  - 책 안의 기존 설명: ['00 · 파이썬은 객체의 타입이 아니라 가진 메서드로 협력한다']
  - 감사 메모: ['앞 장에서 정의되었을 가능성.']

- `abstract-base-class` **abc.ABC와 @abstractmethod** [concept] 별칭=['@abstractmethod', 'ABC', 'ABC·abstractmethod', 'abc.ABC', 'abc.ABC와 @abstractmethod', 'abstractmethod']
  - 첫 등장: 00-intro.html · 원고 · …에 처음 나오는 도구가 셋 있다. ⟦abstract-base-class⟧abc.ABC 를 상속하고 메서드에 @abstractmethod 를 붙이…
  - 용어집 정의(short): 파이썬에서 추상 클래스를 만드는 도구. @abstractmethod가 남은 클래스는 인스턴스화할 때 TypeError가 난다(시그니처는 검사하지 않음).
  - 책 안의 기존 설명: ['00 · 구현을 빠뜨린 규칙 클래스를 인스턴스화 시점에 잡아 주기']

- `typing-protocol` **Protocol** [concept] 별칭=['Protocol', 'typing.Protocol']
  - 첫 등장: 00-intro.html · 원고 · …ocstring이 비교 대상으로 언급하는 ⟦typing-protocol⟧typing.Protocol 은 상속 없이 메서드 모양만 맞으면 그 타입…
  - 용어집 정의(short): 메서드 모양만 선언해 두면 상속 없이도 그 모양을 갖춘 클래스를 호환 타입으로 인정하는(구조적 타이핑) 인터페이스 선언 방식. 검사는 타입 검사기가 한다.
  - 책 안의 기존 설명: ["00 · 상속 없이 '모양'만 맞으면 된다"]
  - 감사 메모: ["00장에서 이미 쓰였음. 10·12·99장에서 'Protocol 대신 ABC를 쓴 이유'로 비교된다."]

- `nominal-typing` **명목적 타이핑** [concept] 별칭=['명목적 타이핑']
  - 첫 등장: 00-intro.html · 원고 · … 시점(인스턴스화)에 잡고 싶다면 ABC (⟦nominal-typing⟧명목적 타이핑 : 명시적으로 상속해야 그 타입으로 인정한다). 외부 ⟦s…
  - 용어집 정의(short): 타입 호환을 이름(명시적 상속·선언)으로 판단하는 방식; ABC를 상속해야 그 타입으로 인정된다.
  - 책 안의 기존 설명: ['00 · 구현체가 이 클래스를 상속하거나 import할 필요가 없다']

- `structural-typing` **구조적 타이핑** [concept] 별칭=['구조적 인터페이스', '구조적 타이핑', '구조적 타입']
  - 첫 등장: 00-intro.html · 원고 · …는 것이 구현체라면 Protocol (⟦structural-typing⟧구조적 타이핑 : 상속 관계가 아니라 메서드 모양이 맞는지로 타입을 인정…
  - 용어집 정의(short): 상속 관계가 아니라 메서드·호출 모양이 맞는지로 타입 호환을 판정하는 방식(파이썬의 Protocol, Callable 타입 별칭).
  - 책 안의 기존 설명: ['10 · 전략 여부는 상속 관계가 아니라 호출 모양']

- `static-type-checker` **정적 타입 검사기** [concept] 별칭=['mypy', 'pyright', '정적 검사기', '정적 검증', '정적 분석', '정적 분석기', '정적 타입 검사', '정적 타입 검사기', '타입 검사기']
  - 첫 등장: 00-intro.html · 원고 · …맞는지로 타입을 인정한다. 검사는 ⟦static-type-checker⟧mypy 같은 정적 검사기, 곧 코드를 실행하지 않고 타입 힌트를 읽어 …
  - 용어집 정의(short): 실행하지 않고 타입 힌트를 읽어 타입 불일치를 찾아 주는 도구(mypy, pyright).

- `first-class-function` **일급 함수** [concept] 별칭=['일급 값', '일급 객체', '일급 함수']
  - 첫 등장: 00-intro.html · 원고 · …이 Lisp와 Dylan의 기능(⟦first-class-function⟧일급 함수 와 타입, ⟦multimethod⟧멀티메서드 , ⟦macro⟧…
  - 용어집 정의(short): 변수에 담고, 인자로 넘기고, 반환값으로 돌려줄 수 있는 값. 파이썬에서 함수는 일급 객체다.
  - 감사 메모: ["00장에서 '일급 함수'로 먼저 쓰였음."]

- `closure` **클로저** [concept] 별칭=['__closure__', '클로저']
  - 첫 등장: 00-intro.html · 원고 · …힌트를 읽어 불일치를 찾는 도구가 한다). 일급 함수와 ⟦closure⟧클로저 . 클로저는 바깥 함수의 지역 변수를 붙잡아 기억하는 안쪽 함수로…
  - 용어집 정의(short): 바깥 함수의 지역 변수를 붙잡아(캡처) 기억하는 안쪽 함수. 바깥 함수가 끝난 뒤에도 그 값을 쓸 수 있다.
  - 책 안의 기존 설명: ['00 · limit을 캡처한 함수를 돌려준다(함수를 만드는 함수)', '10 · 클로저가 생성자 역할, 캡처 변수가 필드 역할']
  - 감사 메모: ['00장에서 먼저 쓰였음.']

- `dunder-special-method` **던더 메서드** [concept] 별칭=['dunder', '던더', '던더 메서드', '특수 메서드']
  - 첫 등장: 00-intro.html · 원고 · …당수는 모듈 하나로 충분하다. ⟦dunder-special-method⟧던더 (dunder) 프로토콜. 던더는 double underscore의…
  - 용어집 정의(short): `__init__`, `__call__`, `__iter__`처럼 이름 앞뒤에 밑줄 두 개가 붙은 특수 메서드; 언어가 정해 둔 프로토콜(호출, 반복, with 등)에 참여하는 방법이며, 파이썬은 이를 인스턴스가 아니라 타입에서 찾는다.
  - 책 안의 기존 설명: ['00 · 특수 메서드는 언어가 미리 정해 둔 인터페이스다']

- `call` **__call__** [gloss] 별칭=['__call__', '콜러블', '호출 가능한']
  - 첫 등장: 00-intro.html · 원고 · …Iteration 을 던진다. for 문이 이것을 부른다), ⟦call⟧__call__ (객체를 함수처럼 () 로 부를 수 있게 한다), ⟦ge…
  - 용어집 정의(short): () 로 호출할 수 있는 모든 객체(함수, 람다, partial, __call__을 정의한 인스턴스).
  - 책 안의 기존 설명: ['00 · __call__ 이 객체를 함수와 같은 모양으로 만들어 준다']

- `getattr` **__getattr__** [gloss] 별칭=['__getattr__']
  - 첫 등장: 00-intro.html · 원고 · …__ (객체를 함수처럼 () 로 부를 수 있게 한다), ⟦getattr⟧__getattr__ (일반 속성 조회가 실패했을 때만 불린다), ⟦co…
  - 용어집 정의(short): 일반 속성 조회가 실패했을 때만 호출되는 특수 메서드(모든 조회를 가로채는 `__getattribute__`와 다름); 위임 래퍼를 짧게 만드는 데 쓰인다.
  - 책 안의 기존 설명: ['05 · 일반 속성 조회가 실패했을 때만 호출되므로', "09 · '일반 조회가 실패했을 때만' 불리므로"]
  - 감사 메모: ['앞 장(5·6장)에서 정의되었을 가능성.']

- `init-subclass` **__init_subclass__** [concept] 별칭=['__init_subclass__']
  - 첫 등장: 00-intro.html · 원고 · …순간 파이썬이 상위 클래스 쪽에서 불러 주는 ⟦init-subclass⟧__init_subclass__ (1장에서 쓴다) 같은 메서드가 모두 훅…
  - 용어집 정의(short): 어떤 클래스의 하위 클래스가 '정의될 때' 파이썬이 상위 클래스 쪽에서 호출해 주는 훅(3.6+); 메타클래스 없이 하위 클래스 등록·검사를 할 수 있다.
  - 책 안의 기존 설명: ["01 · 하위 클래스가 '정의될 때' 파이썬이 호출한다", '12 · 하위 클래스를 정의하는 순간 등록부에 올린다']
  - 감사 메모: ['01장에서 먼저 소개됨.']

- `dataclasses-dataclass` **dataclass** [concept] 별칭=['@dataclass', 'dataclass', '데이터클래스']
  - 첫 등장: 00-intro.html · 원고 · …후 모든 예제 파일에 있다). ⟦dataclasses-dataclass⟧@dataclass 는 필드 선언만으로 생성자, __repr__ , __…
  - 용어집 정의(short): 필드 선언만으로 `__init__`·`__repr__`·`__eq__` 등을 자동 생성해 주는 클래스 데코레이터.
  - 책 안의 기존 설명: ['00 · dataclass가 __repr__과 __eq__를 공짜로 준다']
  - 감사 메모: ['앞 장에서 정의되었을 가능성.']

- `frozen-true` **frozen dataclass** [concept] 별칭=['frozen', 'frozen dataclass', 'frozen=True']
  - 첫 등장: 00-intro.html · 원고 · …자동으로 만들어 주는 표준 라이브러리 도구이고, ⟦frozen-true⟧frozen=True 를 주면 생성 후 필드에 대입할 수 없는 객체가 된…
  - 용어집 정의(short): `@dataclass(frozen=True)`로 만든, 생성 후 필드에 대입할 수 없는 불변 데이터클래스; 같은 값이면 해시가 같아 딕셔너리 키로 쓸 수 있다.
  - 책 안의 기존 설명: ['01 · 불변으로 두어 정규화가 원시 데이터를 덮어쓰지 못하게', '10 · 정책이 입력을 고쳐서 다음 계산에 영향을 주는 일을']

- `dataclasses-field` **field(default_factory=…)** [gloss] 별칭=['default_factory', 'field(default_factory=…)']
  - 첫 등장: 00-intro.html · 원고 · …식으로, 4절에서 다룬다. ⟦dataclasses-field⟧field(default_factory=list) 는 인스턴스마다 새 빈 리스트를 …
  - 용어집 정의(short): 데이터클래스 필드의 세부 옵션을 지정하는 함수; `default_factory=list`는 인스턴스마다 새 빈 리스트를 기본값으로 만든다(가변 기본값 공유 방지).

- `postponed-evaluation-of-annotations` **from __future__ import annotations** [gloss] 별칭=['from __future__ import annotations']
  - 첫 등장: 00-intro.html · 원고 · …리의 ⟦postponed-evaluation-of-annotations⟧from __future__ import annotations 는 타입 …
  - 용어집 정의(short): 타입 힌트를 정의 시점에 평가하지 않고 문자열로 미뤄 두게 하는 선언. 아직 정의되지 않은 클래스 이름을 힌트에 쓸 수 있다.
  - 감사 메모: ['모든 예제 파일 첫머리에 있다. 앞 장에서 이미 등장.']

- `callable` **호출 가능 객체** [concept] 별칭=['Callable', 'callable', '호출 가능 객체', '호출 가능한']
  - 첫 등장: 00-intro.html · 원고 · …엇을 말하는지 주목하라. docstring이 말하는 "⟦callable⟧호출 가능한 것"(callable)은 () 로 부를 수 있는 모든 것, …
  - 용어집 정의(short): `()`로 호출할 수 있는 모든 것(함수, 클래스, 람다, `__call__`을 가진 객체); 타입 힌트 `Callable[[인자...], 반환]`으로 그 모양을 적는다.

- `namespace` **이름공간** [concept] 별칭=['이름공간']
  - 첫 등장: 00-intro.html · 원고 · …⟧캐시 되는(다시 실행하지 않도록 결과가 저장되는) ⟦namespace⟧이름공간 , 곧 이름과 객체의 대응을 담는 공간이다. 싱글턴과 퍼사드의 …
  - 용어집 정의(short): 이름과 객체의 대응을 담는 공간(모듈, 클래스, 함수 지역 등); 같은 이름도 이름공간이 다르면 충돌하지 않는다.

- `generator` **제너레이터** [concept] 별칭=['yield', '제너레이터']
  - 첫 등장: 00-intro.html · 원고 · …)가 대표적이다. 반복자 패턴은 언어 자체가 되었고(⟦generator⟧제너레이터 : yield 가 든 함수를 부르면 나오는 반복자로, 값을 하…
  - 용어집 정의(short): yield가 있는 함수(제너레이터 함수)를 부르면 나오는 반복자 객체. 값을 하나 내고 실행을 멈췄다가 다음 next()에서 이어 간다.
  - 책 안의 기존 설명: ['15 · yield 가 있는 함수를 호출하면 반복자 객체가 나온다']
  - 감사 메모: ["08장 @contextmanager 예제의 yield, 14장 '@contextmanager 제너레이터'가 15장 정의보다 먼저."]

- `context-manager` **컨텍스트 매니저** [concept] 별칭=['__enter__', 'contextmanager', 'with 블록', '컨텍스트 관리자', '컨텍스트 매니저']
  - 첫 등장: 00-intro.html · 원고 · …반 속성 조회가 실패했을 때만 불린다), ⟦context-manager⟧__enter__ / __exit__ (컨텍스트 매니저: with 블록에…
  - 용어집 정의(short): with 문에 쓰여 블록 진입 시 준비, 빠져나올 때(예외 포함) 정리를 보장하는 객체. @contextmanager는 yield 하나 있는 제너레이터 함수로 이를 만든다.
  - 감사 메모: ["08장에서 @contextmanager로 범위 안 처음 쓰이고, 14장은 '컨텍스트 관리자'로 표기한다. 앞 장(6장 등)에서 정의되었을 가능성."]

- `serialization` **직렬화** [concept] 별칭=['직렬화']
  - 첫 등장: 00-intro.html · 원고 · …ble[[인자...], 반환] 으로 적는다. ⟦serialization⟧직렬화 는 객체를 저장하거나 전송할 수 있는 문자열·바이트 형식으로 바꾸…
  - 용어집 정의(short): 객체를 저장·전송할 수 있는 바이트·문자열 형식으로 바꾸는 것(반대는 역직렬화); 동시성 맥락에서는 '여러 실행을 한 줄로 차례대로 세운다'는 다른 뜻으로도 쓰인다.
  - 감사 메모: ['09장에서 처음, 12장에서 본격적으로 쓰인다.']

- `plugin` **플러그인** [gloss] 별칭=['플러그인']
  - 첫 등장: 00-intro.html · 원고 · …만 남는다. 일리가 있는 조건 : 그 경계가 다른 팀이나 ⟦plugin⟧플러그인 (본체 코드를 고치지 않고 정해진 확장 지점에 꽂아 기능을 더하…
  - 용어집 정의(short): 본체 코드를 고치지 않고 정해진 확장 지점에 꽂아 기능을 더하는 독립 모듈.

- `software-development-kit` **SDK** [gloss] 별칭=['SDK']
  - 첫 등장: 00-intro.html · 원고 · …입으로 인정한다). 외부 ⟦software-development-kit⟧SDK (외부 서비스·장비를 쓰도록 제공되는, 대개 우리가 고칠 수 없는…
  - 용어집 정의(short): 특정 서비스·장비를 프로그램에서 쓰도록 제공되는 라이브러리·도구 묶음(이 책에서는 대개 수정할 수 없는 외부 코드).

- `internet-of-things` **IoT** [gloss] 별칭=['IoT']
  - 첫 등장: 00-intro.html · 원고 · …d⟧EMR (전자의무기록), 결제, ⟦internet-of-things⟧IoT (센서·장비가 네트워크로 데이터를 주고받는 사물인터넷)…). 패턴…
  - 용어집 정의(short): 센서·장비가 네트워크에 연결되어 데이터를 주고받는 사물인터넷.

- `electronic-medical-record` **EMR** [gloss] 별칭=['EMR', '전자의무기록']
  - 첫 등장: 00-intro.html · 원고 · …클라우드 인프라, 병원 ⟦electronic-medical-record⟧EMR (전자의무기록), 결제, ⟦internet-of-things⟧Io…
  - 용어집 정의(short): 전자의무기록 — 환자의 진료·처방·검사 기록을 전산으로 관리하는 병원 정보 시스템.

- `multimethod` **멀티메서드** [concept] 별칭=['멀티메서드']
  - 첫 등장: 00-intro.html · 원고 · …class-function⟧일급 함수 와 타입, ⟦multimethod⟧멀티메서드 , ⟦macro⟧매크로 등)으로 단순해지거나 보이지 않게 된다…
  - 용어집 정의(short): 호출할 구현을 첫 인자 하나가 아니라 여러 인자의 실행 시점 타입 조합으로 고르는 함수(다중 디스패치); 파이썬에는 언어 기능으로 없다.

- `macro` **매크로(Lisp)** [concept] 별칭=['매크로 등', '매크로(Lisp)', '매크로에']
  - 첫 등장: 00-intro.html · 원고 · …일급 함수 와 타입, ⟦multimethod⟧멀티메서드 , ⟦macro⟧매크로 등)으로 단순해지거나 보이지 않게 된다고 주장했다. 일급 함수는 …
  - 용어집 정의(short): Lisp 계열 언어에서 코드를 입력받아 코드를 만들어 내 컴파일 전에 펼치는 문법 확장 장치; 파이썬에는 없다.

- `pattern-description-template` **GoF 패턴 기술 항목** [concept] 별칭=['Applicability', 'Consequences', 'GoF 패턴 기술 항목', 'Motivation', 'consequence']
  - 첫 등장: 00-intro.html · 원고 · … 장 3절 첫 문단. GoF 원문의 의도를 인용 수준으로 옮긴다. 동기(Motivation)와 적용 가능성(Applicability) 어떤 상황…
  - 용어집 정의(short): GoF가 모든 패턴을 기술하는 공통 틀(의도, 동기, 적용 가능성, 구조, 참여자, 협력, 결과 등); 특히 결과(Consequences)는 패턴을 쓸 때 얻고 치르는 것이다.
  - 책 안의 기존 설명: ['00 · GoF는 모든 패턴을 같은 틀로 기술한다']

- `program-to-an-interface` **인터페이스에 프로그래밍** [concept] 별칭=['구현에 프로그래밍', '인터페이스에 프로그래밍']
  - 첫 등장: 00-intro.html · 원고 · … 명시한다. "구현이 아닌 ⟦program-to-an-interface⟧인터페이스에 프로그래밍 하라", "클래스 상속보다 객체 합성을 선호하라"…
  - 용어집 정의(short): 구체 클래스가 아니라 추상 타입(인터페이스)에 의존하도록 코드를 쓰라는 GoF 원칙.
  - 감사 메모: ['00장 서론의 세 원칙 중 하나로 이미 정의되었을 가능성.']

- `iterator-protocol` **이터레이터 프로토콜** [concept] 별칭=['StopIteration', '__next__', '반복자 프로토콜', '이터레이터 프로토콜']
  - 첫 등장: 00-intro.html · 원고 · …타입에서 찾는다. __iter__ / ⟦iterator-protocol⟧__next__ (반복자 프로토콜: 순회할 반복자를 내주고 다음 값을 꺼…
  - 용어집 정의(short): __iter__/__next__ 메서드와 StopIteration 예외로 이루어진 파이썬의 순회 규약. for·list()·next()가 이 규약을 호출한다.
  - 책 안의 기존 설명: ['15 · first()/next()/is_done()/current_item() 네 메서드가']

- `cache` **캐시** [gloss] 별칭=['캐시']
  - 첫 등장: 00-intro.html · 원고 · …절 ). 모듈. 모듈은 첫 import 때 한 번 실행되고 ⟦cache⟧캐시 되는(다시 실행하지 않도록 결과가 저장되는) ⟦namespace⟧이…
  - 용어집 정의(short): 다시 계산·요청하지 않도록 결과를 가까운 곳에 저장해 두는 것.
  - 감사 메모: ['앞 장에서 이미 쓰였을 가능성.']

- `dispatch` **디스패치** [concept] 별칭=['디스패치']
  - 첫 등장: 00-intro.html · 원고 · …히려 전략이나, 키에 따라 실행할 구현을 골라 부르는 ⟦dispatch⟧디스패치 의 영역이다. 특히 if/elif 대신 키 → 함수 딕셔너리를 …
  - 용어집 정의(short): 이름·타입 같은 키에 따라 실행할 구현을 골라 호출하는 것.

## 01-factory-method.html — 47개

- `registry` **레지스트리** [concept] 별칭=['_registry', 'registry', '등록부', '레지스트리']
  - 첫 등장: 01-factory-method.html · 원고 · … 한다. 확장의 주도권 문제로 되돌아온 것이다. 정의하는 순간 등록되는 레지스트리 설정 문자열로 장비를 고르고 싶으면서도 "추가만으로 확장"을 …
  - 용어집 정의(short): 이름(키)과 클래스·함수를 짝지어 두는 표; 호출자는 분기 대신 표를 조회하고, 새 항목은 표에 등록만 하면 추가된다.
  - 책 안의 기존 설명: ["01 · '문자열 키 → 클래스' 등록부가 결정한다"]
  - 감사 메모: ["01장에서 '레지스트리'로 먼저 쓰였음."]

- `alternative-constructor` **대체 생성자** [concept] 별칭=['@classmethod', 'alternative constructor', 'classmethod', '대체 생성자']
  - 첫 등장: 01-factory-method.html · 원고 · …클래스 계층 없이 같은 분담을 얻을 수 있지 않을까? 생성 함수 주입과 대체 생성자 아래 코드는 create_reader() 오버라이드를 생성자…
  - 용어집 정의(short): `@classmethod` 등으로 만든, 같은 타입을 다른 입력 형식(설정 dict, 타임스탬프 등)에서 만드는 이름 붙은 생성 진입점; GoF 팩토리 메서드와 달리 무엇을 만들지는 호출자가 고른 클래스가 정한다.
  - 책 안의 기존 설명: ['01 · 생성자 오버로딩이 없는 파이썬에서 이름 붙은 생성자']
  - 감사 메모: ["01장에서 '대체 생성자'가 먼저 다뤄짐."]

- `simple-factory` **단순 팩토리** [concept] 별칭=['Simple Factory', '단순 팩토리']
  - 첫 등장: 01-factory-method.html · 원고 · …(device) 라는 별도 함수로 빼내는 것은 좋은 첫걸음이다. 이것을 단순 팩토리(Simple Factory) 라 부른다. 생성 지식이 한곳에…
  - 용어집 정의(short): 생성 분기(if/elif 또는 표 조회)를 한 함수에 모아 둔 것; 생성 지식은 모이지만 새 제품을 더하려면 그 함수를 고쳐야 하므로 GoF 패턴으로 치지 않는다.
  - 책 안의 기존 설명: ['01 · 분기를 make_reader(device) 라는 별도 함수로 빼내는']

- `parallel-class-hierarchies` **평행 클래스 계층** [concept] 별칭=['parallel class hierarchies', '평행 계층', '평행 클래스 계층']
  - 첫 등장: 01-factory-method.html · 원고 · …duct 계층이 같은 축(장비 종류)을 따라 나란히 늘어나는 이 모양을 평행 클래스 계층(parallel class hierarchies) 이라…
  - 용어집 정의(short): 두 상속 계층(예: Creator와 Product)이 같은 축을 따라 한 쌍씩 나란히 늘어나는 구조; 팩토리 메서드의 대표적 결과이자 비용이다.
  - 책 안의 기존 설명: ['01 · Creator 계층과 Product 계층이 같은 축(장비 종류)을 따라 나란히']

- `seam` **이음새** [concept] 별칭=['seam', '이음새']
  - 첫 등장: 01-factory-method.html · 원고 · …생성 인자가 모든 작업의 생성자로 새어 나오며, (3) 테스트가 끼어들 이음새(seam)가 없다. 흐름은 모든 장비에 공통이고 변하지 않는다. …
  - 용어집 정의(short): 코드를 고치지 않고도 테스트나 확장이 다른 구현을 끼워 넣을 수 있는 지점.
  - 책 안의 기존 설명: ['01 · 테스트가 끼어들 이음새(seam)가 없다']

- `you-aren-t-gonna-need-it` **YAGNI** [concept] 별칭=['YAGNI']
  - 첫 등장: 01-factory-method.html · 원고 · … 몇 분이면 충분하다. 바꾸는 비용이 낮은 결정을 미리 내려 두는 것은 YAGNI 위반이고, 그동안 모든 독자가 불필요한 간접층을 읽는 비용을 …
  - 용어집 정의(short): '그건 필요 없을 것이다' — 실제로 필요해지기 전에는 기능이나 추상화를 미리 만들지 말라는 원칙.

- `uml-stereotype` **UML 스테레오타입** [concept] 별칭=['UML 스테레오타입', '«Abstract Class»', '«Aggregate»', '«Client»', '«Concrete Iterator»', '«Concrete State»', '«Context»', '«Iterator»', '«State»', '«create»', '«frozen dataclass»', '«functions»', '«function»', '«uses»']
  - 첫 등장: 01-factory-method.html · 원고 · …der + read_samples() [Concrete Product] «create» «create» 그림 1-1. 측정 프레임워크의 팩토리 …
  - 용어집 정의(short): UML 요소에 « » 꺾쇠로 붙이는 꼬리표. 그 요소의 종류나 관계의 의미(예: «create» = 생성 관계)를 표시한다.
  - 감사 메모: ['09·10·11·13·15장 그림에 쓰인다. 앞 장 그림에서 먼저 나왔을 가능성(«create»).']

- `metaclass` **메타클래스** [concept] 별칭=['ABCMeta', 'metaclass', '메타클래스']
  - 첫 등장: 01-factory-method.html · 코드 src/01_factory_method/04_registry.py · …상속하면 (예: 공통 기능을 모은 중간 추상 클래스) 등록하지 않는다. 메타클래스로도 같은 일을 할 수 있지만, __init_subclass__…
  - 용어집 정의(short): 클래스를 만들어 내는 클래스(기본은 `type`); 클래스 생성·호출 방식을 바꿀 수 있지만 상속 계층 전체에 전파되고 다른 메타클래스와 충돌할 수 있다.

- `functools-partial` **functools.partial** [concept] 별칭=['functools.partial', 'partial']
  - 첫 등장: 01-factory-method.html · 코드 src/01_factory_method/03_pythonic.py · …factory: Callable[[], Reader] 주입 — 클래스, functools.partial, 람다 모두 팩토리가 된다. 2. Rea…
  - 용어집 정의(short): 함수의 일부 인자를 미리 채워 둔 새 호출 가능 객체를 만든다. repr에 채운 인자가 보인다.
  - 책 안의 기존 설명: ['01 · partial로 장비별 인자(port 등)를 미리 묶어', '10 · 키워드 인자를 미리 채운 함수']
  - 감사 메모: ['08장 원고(functools.partial(check_in, …))가 먼저 쓴다.']

- `classmethod` **@classmethod** [concept] 별칭=['@classmethod', 'classmethod']
  - 첫 등장: 01-factory-method.html · 코드 src/01_factory_method/03_pythonic.py · …로 — 장비 리더가 프레임워크 클래스를 상속할 필요조차 없어진다. 3. @classmethod from_config() — 흔히 '팩토리 메서드…
  - 용어집 정의(short): 인스턴스 대신 클래스(cls)를 첫 인자로 받는 메서드를 만드는 데코레이터; 하위 클래스에서 부르면 cls가 그 하위 클래스가 된다.
  - 감사 메모: ["01장에서 '대체 생성자'가 먼저 다뤄짐."]

- `typing-classvar` **ClassVar** [concept] 별칭=['ClassVar']
  - 첫 등장: 01-factory-method.html · 코드 src/01_factory_method/03_pythonic.py · …rtial from typing import Any, Callable, ClassVar, Protocol @dataclass(frozen=Tru…
  - 용어집 정의(short): 그 속성이 인스턴스가 아니라 클래스 전체에 속함을 타입 검사기에 알리는 타입 힌트(데이터클래스 필드에서도 제외된다).
  - 책 안의 기존 설명: ['01 · ClassVar로 표시해 인스턴스 속성이 아님을', "99 · 취소 가능성은 명령 '종류'의 성질이다"]
  - 감사 메모: ['12·14장에서 설명 없이 먼저 쓰인다.']

- `keyword-only-argument` **키워드 전용 인자** [concept] 별칭=['키워드 인자로', '키워드 전용', '키워드 전용 인자']
  - 첫 등장: 01-factory-method.html · 코드 src/01_factory_method/04_registry.py · …의될 때' 파이썬이 호출한다(인스턴스 생성 때가 아님). device를 키워드 전용 인자로 받는 이유: class XrdReader(Reader…
  - 용어집 정의(short): 매개변수 목록의 * 뒤에 두어 반드시 이름=값으로만 넘길 수 있게 한 인자.

- `cooperative-multiple-inheritance` **협력적 다중 상속** [concept] 별칭=['협력적 다중 상속']
  - 첫 등장: 01-factory-method.html · 코드 src/01_factory_method/04_registry.py · …" super().__init_subclass__(**kwargs) # 협력적 다중 상속을 위해 반드시 위로 넘긴다 if device is No…
  - 용어집 정의(short): 다중 상속 계층의 각 클래스가 `super()`로 다음 클래스에 호출을 넘겨 MRO 순서대로 모두 실행되게 하는 관례.

- `exception-chaining` **예외 연쇄(raise … from)** [concept] 별칭=['__cause__', '__context__', 'from None', 'from e', 'raise ... from', '예외 연결 끊기', '예외 연쇄(raise … from)']
  - 첫 등장: 01-factory-method.html · 코드 src/01_factory_method/04_registry.py · …"등록되지 않은 장비 {device!r} (등록됨: {known})") from None return reader_cls(**options) @…
  - 용어집 정의(short): `raise New(...) from e`로 새 예외의 `__cause__`에 원인 예외를 남기는 문법; `from`을 빼면 원래 예외는 `__context__`에 담겨 '처리 도중 다른 예외'로 보고되고, `from None`은 원인 표시를 숨긴다.
  - 책 안의 기존 설명: ['05 · from 을 빼면 파이썬은 원래 예외를 __context__ 에 담고']

- `assert-python-o` **assert 문과 -O** [concept] 별칭=['assert', 'assert 문과 -O', 'python -O']
  - 첫 등장: 01-factory-method.html · 코드 src/01_factory_method/02_factory_method.py · …ader() result = FakeJob("S-test").run() assert [s.intensity for s in result] == …
  - 용어집 정의(short): 개발 중 불변 조건을 확인하는 문장; `python -O`로 실행하면 제거되므로 입력 검증에 쓰면 안 된다.
  - 책 안의 기존 설명: ['01 · assert는 python -O에서 사라지므로']

- `globals` **globals()** [gloss] 별칭=['globals()']
  - 첫 등장: 01-factory-method.html · 코드 src/01_factory_method/01_naive.py · …e(2, 4.0)] original = CsvSpectrumReader globals()["CsvSpectrumReader"] = FakeRea…
  - 용어집 정의(short): 현재 모듈의 전역 이름공간 딕셔너리를 돌려주는 내장 함수; 여기에 대입하면 모듈 전역 이름을 바꿔치기할 수 있다.

- `monkeypatch` **몽키패치** [concept] 별칭=['monkeypatch', '몽키패치', '바꿔치기']
  - 첫 등장: 01-factory-method.html · 원고 · …un() 이 실제 리더를 이름으로 직접 만드는 탓에, 모듈 전역 이름을 바꿔치기(monkeypatch)하는 것 외에는 가짜 리더를 끼울 방법을 …
  - 용어집 정의(short): 실행 중에 모듈·클래스의 이름이 가리키는 대상을 다른 것으로 바꿔치기하는 기법; 테스트에서 의존 대상을 갈아 끼우는 데 쓰이지만 전역 상태를 오염시킨다.
  - 책 안의 기존 설명: ['01 · 모듈 전역 이름을 바꿔치기(monkeypatch)하는 것']

- `entry-points` **엔트리 포인트(패키징)** [concept] 별칭=['entry points', '엔트리 포인트(패키징)']
  - 첫 등장: 01-factory-method.html · 코드 src/01_factory_method/04_registry.py · … 장비'로 실패한다.") print(" 그래서 플러그인 시스템은 진입점(entry points)이나 명시적 import 목록을 함께 둔다.") …
  - 용어집 정의(short): 설치된 패키지가 '이 이름으로 이 객체를 제공한다'고 메타데이터에 선언해, 다른 프로그램이 import하지 않고도 플러그인을 찾게 하는 파이썬 패키징 메커니즘.

- `io-stringio` **io.StringIO** [gloss] 별칭=['StringIO', 'contextlib.redirect_stdout', 'io.StringIO', 'redirect_stdout']
  - 첫 등장: 01-factory-method.html · 코드 src/01_factory_method/01_naive.py · …mple 목록으로 바꾼다.""" rows = csv.DictReader(io.StringIO(self.RAW)) return [Sample(fl…
  - 용어집 정의(short): with 블록 안의 print 출력을 다른 파일 객체(예: io.StringIO 메모리 버퍼)로 돌리는 컨텍스트 매니저.

- `struct` **struct 모듈** [gloss] 별칭=['struct 모듈', 'struct.pack', 'struct.unpack']
  - 첫 등장: 01-factory-method.html · 코드 src/01_factory_method/01_naive.py · … float64 쌍: m/z, counts)을 읽는다.""" RAW = struct.pack("<6d", 18.0, 1200.0, 44.0, 5…
  - 용어집 정의(short): 파이썬 값과 C 구조체 형식의 바이트열을 형식 문자열(예: `<6d`)에 따라 서로 변환하는 표준 모듈.

- `regular-expression` **정규식** [gloss] 별칭=['re.compile', 're.match', '정규식']
  - 첫 등장: 01-factory-method.html · 원고 · …싱 결정이 엉켜 있다 if self.fmt == "nginx": m = re.match(r'^(\S+) .*?" (\d{3}) ', line) …
  - 용어집 정의(short): 문자열 패턴을 기술하는 작은 언어; 파이썬은 `re` 모듈로 다룬다.

- `side-effect` **부수 효과** [concept] 별칭=['부수 효과']
  - 첫 등장: 01-factory-method.html · 원고 · …면 이 통제가 호출자에게 넘어갔을 것이다(장비 연결처럼 생성이 비싸거나 부수 효과가 있을 때 결정적인 차이다). 이것은 구조적으로 전략 패턴(1…
  - 용어집 정의(short): 함수가 값을 돌려주는 것 외에 바깥 상태를 바꾸는 일(파일·네트워크 I/O, 장비 연결, 전역 등록 등).

- `unit-test` **단위 테스트** [gloss] 별칭=['단위 테스트']
  - 첫 등장: 01-factory-method.html · 원고 · …어져 야간 측정 전체가 멈추는 사고도 났다. 게다가 정규화 로직에 대한 단위 테스트를 쓰려던 학부 연구생은 run() 이 실제 리더를 이름으로 …
  - 용어집 정의(short): 함수·클래스 같은 작은 단위를 외부 의존 없이 따로 검증하는 테스트.
  - 감사 메모: ['4장에서 먼저 쓰였음.']

- `immutable-object` **불변 객체** [concept] 별칭=['불변', '불변 객체']
  - 첫 등장: 01-factory-method.html · 코드 src/01_factory_method/02_factory_method.py · …s(frozen=True) class Sample: """측정점 하나. 불변으로 두어 정규화가 원시 데이터를 덮어쓰지 못하게 한다.""" x: …
  - 용어집 정의(short): 생성된 뒤 상태를 바꿀 수 없는 객체; 공유해도 안전하고 해시 키로 쓸 수 있다.
  - 책 안의 기존 설명: ['03 · frozen 객체는 생성 후 바뀌지 않으므로']

- `declarative` **선언적** [gloss] 별칭=['선언적']
  - 첫 등장: 01-factory-method.html · 코드 src/01_factory_method/04_registry.py · … device="xrd")처럼 클래스 정의 줄에 등록 정보가 함께 보여 선언적이다. device 없이 상속하면 (예: 공통 기능을 모은 중간 추…
  - 용어집 정의(short): '어떻게'의 절차 대신 '무엇'을 원하는지를 기술하는 방식.

- `parser` **파서** [gloss] 별칭=['파서', '파싱']
  - 첫 등장: 01-factory-method.html · 원고 · …없다. DIP 관점에서 보면 상위 정책(측정 흐름)이 하위 세부(CSV 파싱 클래스)에 직접 의존하고 있다. 흔한 첫 시도와 그 한계 분기를 m…
  - 용어집 정의(short): 텍스트·바이트 입력을 해석해 구조화된 데이터로 바꾸는 코드(그 작업이 파싱).

- `little-endian` **리틀엔디언** [gloss] 별칭=['리틀엔디언']
  - 첫 등장: 01-factory-method.html · 코드 src/01_factory_method/01_naive.py · …ssSpecBinaryReader: """질량분석기 고유 바이너리 포맷(리틀엔디언 float64 쌍: m/z, counts)을 읽는다.""" R…
  - 용어집 정의(short): 여러 바이트 수를 낮은 자리 바이트부터 메모리에 저장하는 순서.

- `comma-separated-values` **CSV** [gloss] 별칭=['CSV']
  - 첫 등장: 01-factory-method.html · 원고 · … 첫 과제는 단순했다. 연구실의 UV-Vis 분광광도계는 측정이 끝나면 CSV 파일을 내보내는데, 그것을 읽어 세기를 정규화하고 연구실 데이터 …
  - 용어집 정의(short): 쉼표로 필드를 구분하고 한 줄에 한 레코드를 적는 텍스트 표 형식.

- `javascript-object-notation` **JSON** [gloss] 별칭=['JSON']
  - 첫 등장: 01-factory-method.html · 원고 · …유의 바이너리 포맷을 쓴다. 같은 시기에 새로 산 장비는 시리얼 포트로 JSON 프레임을 흘려보낸다. 서윤은 가장 빠른 길을 택했다. run()…
  - 용어집 정의(short): 키-값 객체와 배열을 텍스트로 표현하는 데이터 교환 형식.

- `pull-request` **PR** [gloss] 별칭=['PR']
  - 첫 등장: 01-factory-method.html · 원고 · … 붙이고 싶어 했지만, 그러려면 공용 프레임워크의 run() 을 고치는 PR을 보내야 했다. 다른 연구실의 장비 분기와 같은 메서드를 건드리니 …
  - 용어집 정의(short): 풀 리퀘스트 — 공유 저장소에 변경을 합쳐 달라고 리뷰와 함께 요청하는 단위.

- `integrated-development-environment` **IDE** [gloss] 별칭=['IDE']
  - 첫 등장: 01-factory-method.html · 원고 · …또 프레임워크 사용자가 " XrdJob "이라는 이름 붙은 개념을 문서·IDE에서 발견할 수 있다는 점도 가치다. [4]의 from_config…
  - 용어집 정의(short): 편집·실행·디버깅·자동 완성을 한데 묶은 통합 개발 환경.

- `http-status-code` **HTTP 상태 코드** [gloss] 별칭=['401 Unauthorized', '409 Conflict', '5xx', 'HTTP 상태 코드', '상태 코드']
  - 첫 등장: 01-factory-method.html · 원고 · …class LogCollector: """웹 서버 접근 로그에서 IP별 5xx 오류 수를 센다.""" def __init__(self, fmt:…
  - 용어집 정의(short): HTTP 응답의 결과를 나타내는 세 자리 숫자(2xx 성공, 4xx 클라이언트 오류, 5xx 서버 오류, 401은 인증 필요).

- `http-method` **HTTP 메서드** [gloss] 별칭=['GET', 'HEAD', 'HTTP 메서드', 'POST']
  - 첫 등장: 01-factory-method.html · 코드 src/01_factory_method/solutions/ex2_log_parser.py · …[ '10.0.0.7 - - [08/Oct/2026:10:00:01] "GET /spectra HTTP/1.1" 200 512', '10.0.0…
  - 용어집 정의(short): HTTP 요청의 동작 종류(GET 조회, POST 생성·변경, HEAD 헤더만 조회 등).

- `uv-vis-spectrophotometer` **UV-Vis 분광광도계** [gloss] 별칭=['UV-Vis', 'UV-Vis 분광광도계', '분광광도계']
  - 첫 등장: 01-factory-method.html · 원고 · …박사과정생 서윤은 실험 자동화를 맡았다. 첫 과제는 단순했다. 연구실의 UV-Vis 분광광도계는 측정이 끝나면 CSV 파일을 내보내는데, 그것을…
  - 용어집 정의(short): 자외선·가시광선을 시료에 비춰 파장별 흡광도를 측정하는 분석 장비.

- `mass-spectrometer` **질량분석기** [gloss] 별칭=['m/z', '질량분석', '질량분석기']
  - 첫 등장: 01-factory-method.html · 원고 · …이니 이것으로 충분했다. 석 달 뒤 공동 연구를 하는 생화학 연구실에서 질량분석기를 들여왔다. 이 장비는 CSV가 아니라 제조사 고유의 바이너리…
  - 용어집 정의(short): 시료를 이온화해 질량 대 전하비(m/z)별 세기를 측정하는 분석 장비.

- `x-ray-diffractometer` **X선 회절계(XRD)** [gloss] 별칭=['XRD', 'X선 회절계', 'X선 회절계(XRD)']
  - 첫 등장: 01-factory-method.html · 원고 · …소로 옮겨 다섯 개 연구실이 함께 쓰기로 한 것이다. 재료공학 연구실은 X선 회절계(XRD)를 붙이고 싶어 했지만, 그러려면 공용 프레임워크의 …
  - 용어집 정의(short): X선을 시료에 쏘아 회절 각도(2θ)별 세기로 결정 구조를 분석하는 장비.

- `normalization` **정규화(측정 데이터)** [gloss] 별칭=['정규화', '정규화(측정 데이터)']
  - 첫 등장: 01-factory-method.html · 원고 · …광광도계는 측정이 끝나면 CSV 파일을 내보내는데, 그것을 읽어 세기를 정규화하고 연구실 데이터 아카이브에 저장하는 작업을 매번 손으로 하고 있…
  - 용어집 정의(short): 단위가 다른 측정값을 비교하려고 일정 기준(여기서는 최대 세기 = 1.0)에 맞춰 크기를 조정하는 것.
  - 책 안의 기존 설명: ['01 · 최대 세기를 1.0으로 맞춘다']

- `serial-port` **시리얼 포트** [gloss] 별칭=['시리얼', '시리얼 포트']
  - 첫 등장: 01-factory-method.html · 원고 · …니라 제조사 고유의 바이너리 포맷을 쓴다. 같은 시기에 새로 산 장비는 시리얼 포트로 JSON 프레임을 흘려보낸다. 서윤은 가장 빠른 길을 택했…
  - 용어집 정의(short): 데이터를 한 비트씩 순서대로 주고받는 장비 연결 단자(COM3, /dev/ttyUSB0 등).

- `nginx` **nginx** [gloss] 별칭=['nginx']
  - 첫 등장: 01-factory-method.html · 원고 · …t_subclass__ 레지스트리로 리팩터링하라. 두 번째 단계에서는 "nginx" , "apache" 같은 설정 문자열로 수집기를 고를 수 있…
  - 용어집 정의(short): 널리 쓰이는 웹 서버·리버스 프록시; 요청마다 접근 로그를 남긴다.

- `double-precision-float` **float64** [gloss] 별칭=['float64']
  - 첫 등장: 01-factory-method.html · 코드 src/01_factory_method/01_naive.py · …BinaryReader: """질량분석기 고유 바이너리 포맷(리틀엔디언 float64 쌍: m/z, counts)을 읽는다.""" RAW = s…
  - 용어집 정의(short): 8바이트(64비트) 배정밀도 부동소수점 수 형식.

- `receiver-class` **수신 클래스** [concept] 별칭=['수신 클래스']
  - 첫 등장: 01-factory-method.html · 원고 · …체 생성자 다. 판별 근거는 두 가지다. 첫째, 만들 클래스는 호출자가 수신 클래스를 고르는 순간 정해진다. datetime.fromtimest…
  - 용어집 정의(short): `Cls.method()`처럼 클래스 메서드를 호출할 때 점 앞에 온 클래스; `@classmethod`의 cls로 전달된다.

- `port-ports-and-adapters` **포트** [concept] 별칭=['소유하는 포트', '포트']
  - 첫 등장: 01-factory-method.html · 원고 · …조사 고유의 바이너리 포맷을 쓴다. 같은 시기에 새로 산 장비는 시리얼 포트로 JSON 프레임을 흘려보낸다. 서윤은 가장 빠른 길을 택했다. r…
  - 용어집 정의(short): 헥사고날(포트와 어댑터) 아키텍처에서 도메인이 소유하고 바깥 구현이 맞춰야 하는 인터페이스.
  - 감사 메모: ["99장 표('Target은 도메인이 소유하는 포트')에만 등장. 별칭 '포트'는 '리포트'·'시리얼 포트'에 오검출되어 구체 표기만 넣었다."]

- `typing-any` **Any** [concept] 별칭=['Any']
  - 첫 등장: 01-factory-method.html · 코드 src/01_factory_method/03_pythonic.py · …tools import partial from typing import Any, Callable, ClassVar, Protocol @datac…
  - 용어집 정의(short): 어떤 타입이든 허용한다는 타입 힌트. 타입 검사를 사실상 끈다.

- `framework` **프레임워크** [gloss] 별칭=['프레임워크']
  - 첫 등장: 01-factory-method.html · 원고 · …학 연구실은 X선 회절계(XRD)를 붙이고 싶어 했지만, 그러려면 공용 프레임워크의 run() 을 고치는 PR을 보내야 했다. 다른 연구실의 장…
  - 용어집 정의(short): 전체 흐름을 쥐고 사용자 코드를 정해진 자리에서 불러 주는 재사용 골격 코드.
  - 감사 메모: ['01장에서 먼저 쓰였음.']

- `hypertext-transfer-protocol` **HTTP** [gloss] 별칭=['HTTP']
  - 첫 등장: 01-factory-method.html · 코드 src/01_factory_method/solutions/ex2_log_parser.py · … - [08/Oct/2026:10:00:01] "GET /spectra HTTP/1.1" 200 512', '10.0.0.9 - - [08/Oc…
  - 용어집 정의(short): 웹에서 요청·응답을 주고받는 프로토콜.

- `pipe` **파이프** [gloss] 별칭=['subprocess.PIPE', '파이프', '파이프 연결']
  - 첫 등장: 01-factory-method.html · 코드 src/01_factory_method/solutions/ex2_log_parser.py · …self, line: str) -> tuple[str, int]: """파이프로 나눈다. 필드 순서가 nginx와 다르다는 점이 파서를 나눌 이…
  - 용어집 정의(short): 한 프로세스의 출력을 다른 프로세스의 입력으로 잇는 운영체제 통로.

- `runtime` **런타임** [gloss] 별칭=['런타임']
  - 첫 등장: 01-factory-method.html · 코드 src/01_factory_method/03_pythonic.py · …t()와 read_samples()만 있으면 된다. 대가는 누락 검사가 런타임 인스턴스화가 아니라 정적 타입 검사기(mypy 등)로 옮겨 간다는…
  - 용어집 정의(short): 프로그램이 실제로 실행되는 시점(또는 실행 환경). 정적 검사 시점과 대비된다.

## 02-abstract-factory.html — 32개

- `publish-subscribe` **발행-구독(토픽·구독)** [concept] 별칭=['구독에서', '구독자', '발행-구독(토픽·구독)', '토픽']
  - 첫 등장: 02-abstract-factory.html · 코드 src/02_abstract_factory/01_naive.py · …ssage: dict[str, str]) -> None: """메시지를 토픽에 발행한다.""" _QUEUE.append(message) def …
  - 용어집 정의(short): 발행자는 메시지를 토픽에 발행하고, 그 토픽을 구독한 수신자(구독자)들이 받아 가는 메시징 모델; 발행자는 누가 받는지 모른다.

- `wrapper` **래퍼** [concept] 별칭=['래퍼']
  - 첫 등장: 02-abstract-factory.html · 원고 · … 순진한 설계와 그 한계 GCP 전환을 반쯤 끝낸 시점의 코드다. 벤더 래퍼는 실제 SDK 대신 메모리로 흉내 냈다. UploadService.…
  - 용어집 정의(short): 다른 객체나 함수를 감싸 호출을 받아 전달하면서 인터페이스를 바꾸거나(어댑터) 책임을 덧붙이는(데코레이터) 객체·함수.

- `kw-only-true` **kw_only** [gloss] 별칭=['__post_init__', 'dataclass kw_only·__post_init__', 'kw_only']
  - 첫 등장: 02-abstract-factory.html · 원고 · …읽는 composition_root() 가 하나뿐이라는 점과, 무엇보다 __post_init__ 이 왜 필요한지에 주목하라. 데모 [2]와 [3…
  - 용어집 정의(short): `@dataclass(kw_only=True)`(3.10+)로 생성자를 키워드 전용으로 만들어 위치 인자 호출을 막는 옵션.
  - 책 안의 기존 설명: ['03 · 위치 인자로 부를 수 없게 막아야']
  - 감사 메모: ['3장에서 정의되었을 가능성.']

- `post-init` **__post_init__** [concept] 별칭=['__post_init__']
  - 첫 등장: 02-abstract-factory.html · 원고 · …읽는 composition_root() 가 하나뿐이라는 점과, 무엇보다 __post_init__ 이 왜 필요한지에 주목하라. 데모 [2]와 [3…
  - 용어집 정의(short): 데이터클래스가 자동 생성한 `__init__`이 필드를 채운 직후 호출하는 훅; 교차 검증이나 파생 값 계산을 넣는다.
  - 감사 메모: ['3장에서 정의되었을 가능성.']

- `dataclasses-replace` **dataclasses.replace** [gloss] 별칭=['dataclasses.replace', 'replace()']
  - 첫 등장: 02-abstract-factory.html · 코드 src/02_abstract_factory/03_pythonic.py · …" __post_init__이 막음: {e}") print("\n[3] dataclasses.replace로 '하나만 바꾼' 키트도 같은 검증을…
  - 용어집 정의(short): 기존 데이터클래스 인스턴스에서 일부 필드만 바꾼 새 인스턴스를 만드는 함수; 내부적으로 `__init__`을 다시 불러 `__post_init__` 검증도 다시 돈다.
  - 책 안의 기존 설명: ['03 · 기존 쿼리에서 하나만 바꾼 쿼리', '12 · init=False 필드를 기본값으로 둔 새 객체를 만든다']
  - 감사 메모: ["99장 표에서 'replace 파생'으로도 쓰인다."]

- `integration-test` **통합 테스트** [gloss] 별칭=['통합 테스트']
  - 첫 등장: 02-abstract-factory.html · 원고 · …짜 저장소와 실제 큐를 섞어 쓰는 것은 오히려 원하는 유연성일 수 있다(통합 테스트 일부만 실제로). 옮겨 갈 조건 : (1) 두 번째 운영 제…
  - 용어집 정의(short): 여러 구성 요소나 실제 외부 시스템을 함께 연결해 검증하는 테스트.

- `environment-variable` **환경 변수** [gloss] 별칭=['os.environ', '환경 변수']
  - 첫 등장: 02-abstract-factory.html · 코드 src/02_abstract_factory/01_naive.py · …om __future__ import annotations # 실제로는 os.environ["CLOUD"]에서 읽는다. 예제에서는 전역 설정으로…
  - 용어집 정의(short): 프로세스 밖에서 주입되는 이름=값 설정(파이썬에서는 `os.environ`); 배포 환경 선택 등에 쓴다.

- `worker` **워커** [gloss] 별칭=['워커']
  - 첫 등장: 02-abstract-factory.html · 원고 · …썸네일을 만들어 달라"는 메시지를 넣는다. 별도 프로세스로 도는 썸네일 워커는 큐에서 메시지를 꺼내 원본을 S3에서 내려받는다. 둘 다 API …
  - 용어집 정의(short): 큐의 작업이나 요청을 받아 처리하는 별도 프로세스·스레드.
  - 감사 메모: ['4장에서 먼저 쓰였음.']

- `message-queue` **메시지 큐** [concept] 별칭=['SQS 큐', '메시지 큐', '인메모리 큐']
  - 첫 등장: 02-abstract-factory.html · 원고 · …스를 만들었다. 업로드 API는 사용자가 올린 파일을 S3에 저장하고, SQS 큐에 "썸네일을 만들어 달라"는 메시지를 넣는다. 별도 프로세스로…
  - 용어집 정의(short): 생산자가 넣은 메시지를 소비자가 나중에 꺼내 처리하게 하는 비동기 전달 통로.

- `health-check` **헬스 체크** [gloss] 별칭=['헬스 체크']
  - 첫 등장: 02-abstract-factory.html · 원고 · …여 나갔는데, 썸네일 워커의 저장소 한 줄을 빠뜨렸다. 배포는 성공했고 헬스 체크도 통과했다. 첫 사용자가 파일을 올리자 업로드는 gs:// U…
  - 용어집 정의(short): 서비스가 살아 있는지 확인하려고 주기적으로 호출하는 점검 요청·엔드포인트.

- `credentials` **자격 증명** [gloss] 별칭=['자격 증명']
  - 첫 등장: 02-abstract-factory.html · 원고 · …객체들이다. 저장소가 낸 URL을 다른 프로세스의 저장소가 읽고, 같은 자격 증명 체계 안에서 동작해야 한다. 이 "섞이면 안 된다"는 제약이 …
  - 용어집 정의(short): 시스템에 접근할 권한을 증명하는 정보(키, 토큰, 계정 등).

- `connection-pool` **연결 풀** [gloss] 별칭=['연결 풀', '커넥션 풀']
  - 첫 등장: 02-abstract-factory.html · 원고 · …스 계층은 언제 여전히 필요한가? (1) 구체 팩토리가 리전·자격 증명·연결 풀 같은 공유 상태를 소유 해야 할 때(02의 CloudAccoun…
  - 용어집 정의(short): 비싼 DB·네트워크 연결을 미리 만들어 두고 재사용하는 연결 묶음.

- `retry-policy` **재시도 정책** [gloss] 별칭=['재시도 정책']
  - 첫 등장: 02-abstract-factory.html · 원고 · …로 일관성을 강제 하고 싶을 때, (3) 제품 생성에 제품군 공통 로직(재시도 정책, 계측 래핑)이 붙을 때다. 반대로 제품군이 두세 개이고 c…
  - 용어집 정의(short): 실패한 요청을 언제, 몇 번, 어떤 간격으로 다시 시도할지 정한 규칙.

- `instrumentation` **계측** [gloss] 별칭=['계측']
  - 첫 등장: 02-abstract-factory.html · 원고 · …제 하고 싶을 때, (3) 제품 생성에 제품군 공통 로직(재시도 정책, 계측 래핑)이 붙을 때다. 반대로 제품군이 두세 개이고 compositi…
  - 용어집 정의(short): 실행 시간·호출 수 같은 지표를 수집하도록 코드에 측정 장치를 붙이는 일.

- `command-line-interface` **CLI** [gloss] 별칭=['CLI']
  - 첫 등장: 02-abstract-factory.html · 원고 · …후가 아니라 시작 시점에 드러나기 때문이다. 리팩터링 문제 2. 테마별 CLI 위젯 사내 배포 도구의 CLI는 터미널 테마에 따라 버튼과 대화상…
  - 용어집 정의(short): 명령행(터미널)에서 텍스트 명령으로 쓰는 프로그램 인터페이스.

- `url-scheme` **URL 스킴** [gloss] 별칭=['S3', 'URL 스킴', 'URL 형식', 'gs://', 's3://', 'url_scheme', '객체 저장소']
  - 첫 등장: 02-abstract-factory.html · 원고 · … 위에 업로드 서비스를 만들었다. 업로드 API는 사용자가 올린 파일을 S3에 저장하고, SQS 큐에 "썸네일을 만들어 달라"는 메시지를 넣는다…
  - 용어집 정의(short): URL 맨 앞의 `s3://`, `gs://`, `file://` 같은 부분으로, 어느 시스템·프로토콜이 그 주소를 해석하는지 나타낸다.

- `amazon-web-services-google-cloud-platform` **AWS와 GCP** [gloss] 별칭=['AWS', 'AWS와 GCP', 'GCP']
  - 첫 등장: 02-abstract-factory.html · 원고 · … 1. 상황 파일 공유 스타트업 '구름다리'의 플랫폼 엔지니어 도현은 AWS 위에 업로드 서비스를 만들었다. 업로드 API는 사용자가 올린 파…
  - 용어집 정의(short): 대표적 퍼블릭 클라우드 두 곳.

- `object-storage` **객체 저장소(S3·GCS)** [gloss] 별칭=['Cloud Storage', 'GCS', 'S3', '객체 저장소(S3·GCS)']
  - 첫 등장: 02-abstract-factory.html · 원고 · … 위에 업로드 서비스를 만들었다. 업로드 API는 사용자가 올린 파일을 S3에 저장하고, SQS 큐에 "썸네일을 만들어 달라"는 메시지를 넣는다…
  - 용어집 정의(short): 파일을 키로 식별되는 객체로 버킷에 저장하는 클라우드 저장 서비스(AWS S3, GCP Cloud Storage).

- `sqs-pub-sub` **SQS와 Pub/Sub** [gloss] 별칭=['Pub/Sub', 'SQS', 'SQS와 Pub/Sub', '발행/구독', '주제(topic)']
  - 첫 등장: 02-abstract-factory.html · 원고 · …스를 만들었다. 업로드 API는 사용자가 올린 파일을 S3에 저장하고, SQS 큐에 "썸네일을 만들어 달라"는 메시지를 넣는다. 별도 프로세스로…
  - 용어집 정의(short): 발행자가 주제(이벤트 이름)로 메시지를 내보내고, 그 주제를 구독한 쪽들이 받는 통신 방식. 발행자는 구독자를 모른다.

- `secrets-manager` **시크릿 저장소** [gloss] 별칭=['Secret Manager', 'Secrets Manager', '시크릿', '시크릿 저장소']
  - 첫 등장: 02-abstract-factory.html · 원고 · … 큐에서 메시지를 꺼내 원본을 S3에서 내려받는다. 둘 다 API 키를 Secrets Manager에서 꺼낸다. 코드 곳곳에서 S3Storage…
  - 용어집 정의(short): API 키·비밀번호 같은 비밀 값을 안전하게 보관하고 꺼내 주는 서비스.

- `region` **리전** [gloss] 별칭=['리전']
  - 첫 등장: 02-abstract-factory.html · 원고 · …calFactory 한 제품군의 제품만 만든다. 제품군이 공유하는 설정(리전, 프로젝트, 계정)을 소유한다. 추상 제품(Abstract Prod…
  - 용어집 정의(short): 클라우드 데이터센터가 위치한 지리적 구역; 자원은 리전에 묶인다.

- `bucket` **버킷** [gloss] 별칭=['버킷']
  - 첫 등장: 02-abstract-factory.html · 코드 src/02_abstract_factory/02_abstract_factory.py · … class CloudAccount: """시뮬레이션용 클라우드 계정: 버킷과 큐를 메모리에 둔다.""" name: str url_scheme:…
  - 용어집 정의(short): 객체 저장소에서 객체들을 담는 최상위 컨테이너.

- `dotenv` **.env 파일** [gloss] 별칭=['.env', '.env 파일']
  - 첫 등장: 02-abstract-factory.html · 원고 · … 없이 백엔드를 돌리고 싶어 한다. 파일 시스템 저장소, 인메모리 큐, .env 파일의 시크릿으로 된 세 번째 조합이 필요하다. 이제 생성 지점…
  - 용어집 정의(short): 개발 환경에서 환경 변수·시크릿을 `이름=값` 줄로 적어 두는 파일.

- `content-delivery-network` **CDN** [gloss] 별칭=['CDN']
  - 첫 등장: 02-abstract-factory.html · 원고 · …기존 클래스는 건드리지 않는다. 반면 제품 종류를 하나 더하는 것(예: CDN)은 행 을 추가하는 일인데, CloudFactory 에 메서드를 …
  - 용어집 정의(short): 콘텐츠를 사용자 가까운 서버에 캐시해 빠르게 전달하는 분산 네트워크.

- `on-premises` **온프레미스** [gloss] 별칭=['온프레미스']
  - 첫 등장: 02-abstract-factory.html · 원고 · …제로). 옮겨 갈 조건 : (1) 두 번째 운영 제품군(다른 클라우드, 온프레미스)이 생길 때, (2) 제품들이 같은 세션·자격 증명·리전을 공…
  - 용어집 정의(short): 클라우드가 아니라 조직이 직접 보유·운영하는 서버 환경.

- `boto3` **boto3** [gloss] 별칭=['boto3']
  - 첫 등장: 02-abstract-factory.html · 코드 src/02_abstract_factory/02_abstract_factory.py · …------------- # 각 클라우드의 '계정 컨텍스트'. 실제로는 boto3.Session이나 GCP 자격 증명에 해당한다. # 제품군이 …
  - 용어집 정의(short): AWS 서비스를 파이썬에서 쓰기 위한 공식 SDK.

- `shared-context` **공유 컨텍스트(제품군)** [concept] 별칭=['계정 컨텍스트', '공유 컨텍스트', '공유 컨텍스트(제품군)']
  - 첫 등장: 02-abstract-factory.html · 원고 · …위의 CloudAccount : 제품군이 일관되어야 하는 실제 이유인 "공유 컨텍스트"다. (2) CloudFactory 와 세 구체 팩토리: …
  - 용어집 정의(short): 한 제품군의 제품들이 함께 써야 하는 자격 증명·리전·프로젝트 같은 공통 설정·상태; 구체 팩토리가 소유해 모든 제품에 나눠 준다.
  - 책 안의 기존 설명: ['02 · 같은 자격 증명·리전·프로젝트를 공유해야']

- `uniform-resource-locator` **URL** [gloss] 별칭=['URL']
  - 첫 등장: 02-abstract-factory.html · 원고 · … 헬스 체크도 통과했다. 첫 사용자가 파일을 올리자 업로드는 gs:// URL을 큐에 넣었고, 워커는 S3 SDK로 그 URL을 읽으려다 실패했…
  - 용어집 정의(short): 웹 자원의 주소.

- `application-programming-interface` **API** [gloss] 별칭=['API']
  - 첫 등장: 02-abstract-factory.html · 원고 · … 플랫폼 엔지니어 도현은 AWS 위에 업로드 서비스를 만들었다. 업로드 API는 사용자가 올린 파일을 S3에 저장하고, SQS 큐에 "썸네일을 …
  - 용어집 정의(short): 프로그램이 다른 프로그램·서비스의 기능을 호출하기 위해 약속한 인터페이스.
  - 감사 메모: ['앞 장에서 이미 쓰였을 가능성.']

- `session` **세션** [gloss] 별칭=['세션']
  - 첫 등장: 02-abstract-factory.html · 원고 · … 제품군(다른 클라우드, 온프레미스)이 생길 때, (2) 제품들이 같은 세션·자격 증명·리전을 공유해 "같이 만들어져야" 할 때, (3) 제품 …
  - 용어집 정의(short): 한 사용자·연결이 시작해 끝날 때까지의 상호작용 단위와 그 상태.

- `backend` **백엔드** [gloss] 별칭=['백엔드']
  - 첫 등장: 02-abstract-factory.html · 원고 · … 알려졌다. 설상가상으로 프런트엔드 개발자들은 노트북에서 클라우드 없이 백엔드를 돌리고 싶어 한다. 파일 시스템 저장소, 인메모리 큐, .env…
  - 용어집 정의(short): 사용자 화면 뒤에서 데이터와 업무 처리를 맡는 서버 쪽 코드.

- `queue` **큐** [gloss] 별칭=['작업 큐', '큐', '큐에 넣', '큐에서', '큐잉']
  - 첫 등장: 02-abstract-factory.html · 원고 · …들었다. 업로드 API는 사용자가 올린 파일을 S3에 저장하고, SQS 큐에 "썸네일을 만들어 달라"는 메시지를 넣는다. 별도 프로세스로 도는 …
  - 용어집 정의(short): 먼저 넣은 것을 먼저 꺼내는 대기열 자료구조.
  - 감사 메모: ["'큐'는 '큐브'와 겹쳐 구체 표기만 별칭으로 넣었다."]

## 03-builder.html — 27개

- `fluent-interface` **유창한 인터페이스** [concept] 별칭=['유창한 빌더', '유창한 인터페이스', '유창한(fluent)']
  - 첫 등장: 03-builder.html · 원고 · …고 하면 대부분 Builder().a(1).b(2).build() 같은 유창한 인터페이스를 떠올린다. 이것은 Joshua Bloch가 Effec…
  - 용어집 정의(short): 메서드가 자신(self)을 돌려주어 `b.select(...).where(...).build()`처럼 호출을 한 문장으로 이어 쓰게 만든 API 스타일; 빌더에서 선택 사항이 많은 객체를 읽히게 조립하는 데 흔히 쓴다.
  - 책 안의 기존 설명: ['03 · Builder().a(1).b(2).build() 같은 유창한 인터페이스']

- `method-chaining` **메서드 체이닝** [concept] 별칭=['메서드 체이닝', '체이닝']
  - 첫 등장: 03-builder.html · 코드 src/03_builder/02_builder.py · …der] Query를 단계적으로 조립한다. 각 단계는 self를 돌려줘 체이닝된다. 반환 타입이 Self(3.11+)인 이유: 하위 클래스(예:…
  - 용어집 정의(short): 메서드가 객체 자신을 돌려주게 하여 여러 호출을 점(.)으로 이어 붙이는 기법.
  - 책 안의 기존 설명: ['03 · 각 단계는 self를 돌려줘 체이닝된다']

- `cross-field-validation` **교차 검증** [concept] 별칭=['교차 검증', '교차 제약']
  - 첫 등장: 03-builder.html · 원고 · … 확인하라. 가변 상태( _where 등의 리스트)는 어디에만 있는가? 교차 검증은 각 단계가 아니라 왜 build() 에 모여 있는가(docs…
  - 용어집 정의(short): 필드 하나가 아니라 여러 필드의 조합에 걸린 제약(예: HAVING이 있으면 GROUP BY도 있어야 함)을 검사하는 것.
  - 책 안의 기존 설명: ['03 · 검증이 단일 필드가 아니라 조립 결과 전체에 걸쳐']

- `telescoping-constructor` **점층적 생성자** [concept] 별칭=['telescoping constructor', '점층적 생성자']
  - 첫 등장: 03-builder.html · 코드 src/03_builder/01_naive.py · …t: int | None = None) -> None: """⚠ 문제: 점층적 생성자(telescoping constructor). 선택 인자가…
  - 용어집 정의(short): 선택 인자가 늘 때마다 생성자 매개변수를 하나씩 덧붙여, 호출부가 위치로만 구분되는 긴 인자 목록(None 행렬)을 쓰게 되는 안티패턴.
  - 책 안의 기존 설명: ["03 · 선택 인자가 하나 늘 때마다 모든 호출부가 '위치'를 다시 맞춰야"]

- `value-object` **값 객체** [concept] 별칭=['값 객체']
  - 첫 등장: 03-builder.html · 코드 src/03_builder/04_pythonic.py · …ue) class Query: """[Product이자 스스로 검증하는 값 객체] 빌더 없이 키워드 인자로 만든다. kw_only=True(3.…
  - 용어집 정의(short): 정체성 없이 담긴 값으로만 의미가 정해지는, 대개 불변인 작은 객체(예: FeeInput, Tick).

- `compare-false` **field(compare=False)** [concept] 별칭=['compare=False', 'field(compare=False)']
  - 첫 등장: 03-builder.html · 코드 src/03_builder/04_pythonic.py · …t: int | None = None # 비교·해시에서 제외되는 메모. field(compare=False)는 '정의의 일부가 아닌' 정보를 표…
  - 용어집 정의(short): 데이터클래스 필드를 동등성 비교와 해시에서 빼는 옵션; 정의의 일부가 아닌 메모 같은 정보에 쓴다.
  - 책 안의 기존 설명: ['03 · "정의의 일부가 아닌 정보"를 동등성과 해시에서 빼는']

- `typing-self` **typing.Self** [concept] 별칭=['Self', 'typing.Self']
  - 첫 등장: 03-builder.html · 원고 · …lder] 가변 QueryBuilder + select(*exprs): Self + where(expr, op, value): Self + gr…
  - 용어집 정의(short): '이 메서드가 호출된 객체의 실제 클래스'를 뜻하는 반환 타입 힌트(3.11+); 하위 클래스에서 체이닝해도 타입이 유지된다.
  - 책 안의 기존 설명: ['03 · 타입 검사기가 하위 클래스 메서드를 계속 인식하게']

- `frozenset` **frozenset** [concept] 별칭=['frozenset']
  - 첫 등장: 03-builder.html · 코드 src/03_builder/02_builder.py · …MAX)\(([a-z_][a-z0-9_]*|\*)\)$") _OPS = frozenset({"=", "<>", "<", "<=", ">", ">…
  - 용어집 정의(short): 생성 후 바꿀 수 없는 집합 타입(해시 가능).

- `types-mappingproxytype` **MappingProxyType** [concept] 별칭=['MappingProxyType']
  - 첫 등장: 03-builder.html · 원고 · …horization"] = ... 처럼 내부 를 바꿀 수 있다. 해설은 MappingProxyType 으로 읽기 전용 뷰를 씌우고, 빌더의 di…
  - 용어집 정의(short): 딕셔너리를 감싸 읽기 전용으로 보여 주는 뷰; 원본이 바뀌면 그대로 비춰 보이므로 복사본을 감싸야 불변이 된다.
  - 책 안의 기존 설명: ['03 · MappingProxyType 으로 읽기 전용 뷰를 씌우고']

- `type-ignore-comment` **# type: ignore** [concept] 별칭=['# type: ignore', 'type: ignore']
  - 첫 등장: 03-builder.html · 코드 src/03_builder/02_builder.py · … ({', '.join(['%s'] * len(c.value))})") # type: ignore[arg-type] params.extend(c…
  - 용어집 정의(short): 그 줄에 대해 정적 타입 검사기의 경고를 끄는 주석 지시문(대괄호 안에 무시할 오류 코드를 적을 수 있다).

- `pandas` **pandas** [gloss] 별칭=['pandas', '데이터프레임']
  - 첫 등장: 03-builder.html · 코드 src/03_builder/03_director.py · …ERE-GROUP-LIMIT")을 한 곳에 두었기 때문에 새 표현(예: 데이터프레임 코드 생성기)을 추가해도 절차를 다시 쓰지 않는다. 절차가 …
  - 용어집 정의(short): 표 형태 데이터(데이터프레임)를 다루는 파이썬 데이터 분석 라이브러리.

- `hashable` **해시 가능** [concept] 별칭=['해시', '해시 가능', '해시 불가']
  - 첫 등장: 03-builder.html · 코드 src/03_builder/02_builder.py · … 만든 Query는 변하지 않는다. 대시보드 캐시의 키로도 쓸 수 있다(해시 가능). """ table: str select: tuple[str…
  - 용어집 정의(short): 수명 동안 해시값이 변하지 않아 dict 키·set 원소가 될 수 있는 성질. frozen dataclass는 해시 가능하다.

- `structured-query-language` **SQL** [gloss] 별칭=['SQL']
  - 첫 등장: 03-builder.html · 원고 · …점검에서는 대시보드 검색창에 따옴표를 넣으면 쿼리 조건이 바뀐다는 지적(SQL 주입)을 받았다. 마지막으로 분석 팀장이 "차트마다 이 숫자가 무…
  - 용어집 정의(short): 관계형 데이터베이스에 질의하고 데이터를 다루는 표준 언어.

- `group-by-having` **GROUP BY와 HAVING** [gloss] 별칭=['GROUP BY', 'GROUP BY와 HAVING', 'HAVING']
  - 첫 등장: 03-builder.html · 원고 · …) FROM orders WHERE order_date >= '...' GROUP BY month 를 만들면 충분했다. 이것을 SalesQuer…
  - 용어집 정의(short): GROUP BY는 행을 열 값별 그룹으로 묶어 집계(SUM 등)하는 기준이고, HAVING은 집계가 끝난 그룹에 거는 조건이다(WHERE는 집계 전 행에 거는 조건).
  - 책 안의 기존 설명: ['03 · 집계 기준과 집계 후 필터']

- `non-aggregated-column` **비집계 열** [gloss] 별칭=['비집계 열']
  - 첫 등장: 03-builder.html · 원고 · …UP BY 없는 HAVING 을 허용하지만(전체를 한 그룹으로 본다), 비집계 열이 섞이면 DB가 거부하고, 이 팀의 대시보드에서 HAVING …
  - 용어집 정의(short): SELECT에서 SUM·COUNT 같은 집계식으로 감싸지 않은 열; GROUP BY가 있으면 그 열은 GROUP BY에도 있어야 한다.
  - 책 안의 기존 설명: ['03 · 집계식이 아닌 SELECT 열은 모두 GROUP BY에 있어야 한다']

- `sql-injection` **SQL 주입** [concept] 별칭=['SQL 주입', 'SQL injection']
  - 첫 등장: 03-builder.html · 원고 · …점검에서는 대시보드 검색창에 따옴표를 넣으면 쿼리 조건이 바뀐다는 지적(SQL 주입)을 받았다. 마지막으로 분석 팀장이 "차트마다 이 숫자가 무…
  - 용어집 정의(short): 입력 값이 SQL 텍스트에 그대로 섞여 들어가 쿼리의 의미 자체가 바뀌는 보안 취약점.
  - 책 안의 기존 설명: ['03 · 따옴표를 넣으면 쿼리 조건이 바뀐다는 지적(SQL 주입)']

- `parameter-binding` **매개변수 바인딩** [concept] 별칭=['매개변수 바인딩', '매개변수로 바인딩', '자리표시자']
  - 첫 등장: 03-builder.html · 코드 src/03_builder/02_builder.py · … 때문이다. - 값은 SQL 문자열에 넣지 않고 params로 분리한다(매개변수 바인딩). 역할 대응: [Builder] QueryBuilder…
  - 용어집 정의(short): SQL 텍스트에는 `%s` 같은 자리표시자만 두고 값은 별도로 넘겨 DB 드라이버가 안전하게 결합하게 하는 방식; 식별자는 바인딩할 수 없다.
  - 책 안의 기존 설명: ['03 · 값은 %s 자리표시자와 params 로 분리해 DB 드라이버가 바인딩하게']

- `allowlist` **화이트리스트** [gloss] 별칭=['화이트리스트']
  - 첫 등장: 03-builder.html · 코드 src/03_builder/02_builder.py · …Self # 식별자(테이블·열 이름)는 매개변수로 바인딩할 수 없으므로 화이트리스트 정규식으로 막는다. _IDENT = re.compile(r"…
  - 용어집 정의(short): 허용할 값·패턴을 명시해 그 밖의 것은 모두 거부하는 검사 방식.

- `database-driver` **DB 드라이버** [gloss] 별칭=['DB 드라이버']
  - 첫 등장: 03-builder.html · 코드 src/03_builder/02_builder.py · …rams={params}") try: # 식별자는 바인딩할 수 없으므로(DB 드라이버는 값만 바인딩한다) 단계 호출 즉시 거부한다. QueryB…
  - 용어집 정의(short): 애플리케이션과 특정 데이터베이스 사이의 통신을 맡는 라이브러리(`cursor.execute(sql, params)` 등을 제공).

- `postgresql` **PostgreSQL** [gloss] 별칭=['PostgreSQL']
  - 첫 등장: 03-builder.html · 원고 · …는다. [3]의 쿼리는 category 가 GROUP BY 에 없으므로 PostgreSQL이 거부한다. 문제는 그 거부가 운영 DB에 보낸 뒤에…
  - 용어집 정의(short): 널리 쓰이는 오픈 소스 관계형 데이터베이스.

- `query-string` **쿼리 문자열** [gloss] 별칭=['쿼리 문자열']
  - 첫 등장: 03-builder.html · 코드 src/03_builder/solutions/ex2_request_builder.py · …elf, name: str, value: str) -> Self: """쿼리 문자열 매개변수 하나를 더한다.""" self._params[nam…
  - 용어집 정의(short): URL의 `?` 뒤에 `이름=값&…`으로 붙는 요청 매개변수.

- `bearer-token` **Bearer 토큰** [gloss] 별칭=['Bearer', 'Bearer 토큰', 'bearer']
  - 첫 등장: 03-builder.html · 원고 · …생성자로 받고 나머지는 이름 붙은 단계로 만든다. auth 문자열 대신 bearer(token) 이라는 도메인 어휘를 더할 수 있다는 것도 빌더…
  - 용어집 정의(short): 가진 사람(bearer)에게 권한을 주는 접근 토큰으로, HTTP `Authorization: Bearer <토큰>` 헤더로 보낸다.

- `http-proxy` **HTTP 프록시** [gloss] 별칭=['HTTP 프록시', '일부 프록시']
  - 첫 등장: 03-builder.html · 원고 · … "tok-123") # 문제 2: 실제로 났던 사고 — GET 본문은 일부 프록시가 버린다. # 필터가 적용되지 않은 전체 데이터가 내려왔다.…
  - 용어집 정의(short): 클라이언트와 서버 사이에서 HTTP 요청을 중계하는 네트워크 서버(9장의 프록시 패턴과는 다른 뜻).

- `business-intelligence` **BI** [gloss] 별칭=['BI']
  - 첫 등장: 03-builder.html · 원고 · … 1. 상황 이커머스 회사 '장바구니랩'의 데이터 분석가 하은은 사내 BI 대시보드의 첫 차트인 "기간별 매출"을 맡았다. 처음에는 f-str…
  - 용어집 정의(short): 비즈니스 인텔리전스 — 사내 데이터를 집계·시각화해 의사 결정을 돕는 분석 체계(대시보드 등).

- `customer-relationship-management` **CRM** [gloss] 별칭=['CRM']
  - 첫 등장: 03-builder.html · 원고 · …무 개로 늘었다. 영업팀은 지역 필터를, 상품기획팀은 카테고리 필터를, CRM팀은 회원 등급 필터를 원했다. 어떤 차트는 카테고리별로 묶어 매출…
  - 용어집 정의(short): 고객 관계 관리 — 고객 정보·등급·이력을 관리하는 업무(또는 그 팀·시스템).

- `rich-text-format` **RTF** [gloss] 별칭=['RTF']
  - 첫 등장: 03-builder.html · 원고 · … 절차에서 서로 다른 표현 결과를 만들 수 있게 한다." 원전의 예제는 RTF 문서를 읽는 하나의 파서(Director)가 ASCII 변환기, …
  - 용어집 정의(short): 서식 정보를 담는 문서 교환용 텍스트 형식.

- `public-api` **공개 API** [concept] 별칭=['공개 API', '공개 표면']
  - 첫 등장: 03-builder.html · 원고 · …은 좋은 선택이다. 주입 방어와 교차 검증을 그대로 재사용할 수 있다. 공개 API는 함수, 구현 도구는 빌더다. 결론이 바뀌는 조건 : 사용자…
  - 용어집 정의(short): 모듈·패키지·클래스가 바깥 사용자에게 쓰라고 약속한 이름들의 집합. 그 밖의 것은 내부 구현으로 취급한다.

## 04-singleton.html — 42개

- `virtual-proxy` **가상 프록시** [concept] 별칭=['가상 프록시']
  - 첫 등장: 04-singleton.html · 원고 · …) : "처음 쓸 때 만든다"는 지연 초기화가 싱글턴을 쓰는 이유라면, 가상 프록시가 전역 접근 없이 같은 효과를 낸다. 옵저버(11장) : "…
  - 용어집 정의(short): 비싼 실제 객체를 정말 필요할 때까지 만들지 않고, 첫 사용 시점에 만들어 위임하는 프록시.
  - 책 안의 기존 설명: ['09 · 생성 시점 : 비싼 객체를 정말 필요할 때까지']

- `event-bus` **이벤트 버스** [concept] 별칭=['이벤트 버스']
  - 첫 등장: 04-singleton.html · 원고 · …프록시가 전역 접근 없이 같은 효과를 낸다. 옵저버(11장) : "전역 이벤트 버스"는 싱글턴이 되는 가장 흔한 경로다. 구독자가 테스트 사이에…
  - 용어집 정의(short): 발행자와 구독자 사이에서 이벤트를 중계하는 공용 통로; 전역 하나로 두면 구독자가 테스트 사이에 남는 문제가 생긴다.

- `object-graph` **객체 그래프** [concept] 별칭=['객체 그래프']
  - 첫 등장: 04-singleton.html · 코드 src/04_singleton/04_injection.py · …[Composition Root] 프로그램 시작 시 단 한 번 호출되어 객체 그래프를 조립한다. 유일성 보장은 여기 있다: AuditLogger…
  - 용어집 정의(short): 프로그램 안의 객체들이 서로를 참조하며 이루는 연결 구조.

- `test-isolation` **테스트 격리** [concept] 별칭=['격리 붕괴', '테스트 격리']
  - 첫 등장: 04-singleton.html · 원고 · …다. 싱글턴은 1차 고통(인스턴스 중복)을 해결한다. 그러나 2차 고통(테스트 격리 붕괴, 숨은 의존성, 초기화 경쟁)은 싱글턴 자신이 만든다.…
  - 용어집 정의(short): 각 테스트가 다른 테스트의 실행 여부·순서와 무관하게 같은 결과를 내도록 상태를 공유하지 않는 성질.
  - 책 안의 기존 설명: ['04 · 테스트 결과가 실행 순서에 의존하는 것은 단위 테스트가 가져서는 안 되는 성질']

- `lazy-initialization` **지연 초기화** [concept] 별칭=['지연 로딩', '지연 생성', '지연 초기화']
  - 첫 등장: 04-singleton.html · 코드 src/04_singleton/03_variants.py · …f get_audit_logger() -> PlainLogger: """지연 생성 접근 함수. 첫 호출 때 만들고 이후 같은 객체를 돌려준다. …
  - 용어집 정의(short): 비싼 객체나 데이터를 미리 만들지 않고, 실제로 처음 필요해지는 순간에 만들거나 불러오는 기법.
  - 책 안의 기존 설명: ['04 · "처음 쓸 때 만든다"는 지연 초기화', '09 · 비싼 객체를 정말 필요할 때까지 만들지 않는다']
  - 감사 메모: ["인용은 가상 프록시 표 행이다. 09장 01_naive.py docstring('지연 로딩·권한·캐시 검사')이 먼저 나온다. 04장(싱글턴)에서 '지연 초기화'가 먼저 쓰였을 수 있음."]

- `borg-monostate` **Borg(Monostate)** [concept] 별칭=['Borg', 'Borg(Monostate)', 'Monostate']
  - 첫 등장: 04-singleton.html · 원고 · …w__ 가 정말 깨지는지 스레드로 실험하고, (2) 메타클래스, (3) Borg, (4) 모듈 수준 객체, (5) functools.cache …
  - 용어집 정의(short): 인스턴스는 여럿 만들되 모든 인스턴스가 같은 속성 저장소(`__dict__`)를 공유해 상태만 하나로 만드는 파이썬 관용구.
  - 책 안의 기존 설명: ['04 · 인스턴스는 여럿, 상태는 하나']

- `double-checked-locking` **이중 검사 잠금** [concept] 별칭=['double-checked locking', '이중 검사 잠금']
  - 첫 등장: 04-singleton.html · 원고 · …태윤이 적용한 싱글턴이다. 앞부분은 유일성 구현이다. __new__ 의 이중 검사 잠금과 __init__ 의 _initialized 가드가 각각…
  - 용어집 정의(short): 잠금 없이 먼저 검사하고, 필요할 때만 잠금을 잡은 뒤 다시 한 번 검사해 지연 생성 객체가 둘 생기는 경쟁을 막는 기법.
  - 책 안의 기존 설명: ['04 · 바깥 검사: 이미 만들어졌다면 잠금 비용 없이']

- `cross-cutting-concern` **횡단 관심사** [concept] 별칭=['횡단 관심사']
  - 첫 등장: 04-singleton.html · 원고 · …은 이미 이름별로 하나인 레지스트리이고, 로깅은 거의 모든 코드가 쓰는 횡단 관심사라 주입하면 모든 시그니처가 오염된다. 테스트도 로그 내용을 …
  - 용어집 정의(short): 로깅·인증·계측처럼 여러 모듈에 걸쳐 공통으로 필요해 한 모듈에 담기 어려운 관심사.

- `new` **__new__** [concept] 별칭=['__new__']
  - 첫 등장: 04-singleton.html · 원고 · …ger - _instance: AuditLogger {static} + __new__(cls): AuditLogger + record(actor…
  - 용어집 정의(short): 인스턴스를 할당해 돌려주는 특수 메서드; `Cls()`는 먼저 `__new__`로 객체를 얻고 그것이 Cls의 인스턴스이면 `__init__`으로 초기화한다.
  - 책 안의 기존 설명: ["04 · 먼저 __new__로 객체를 '할당'하고 그다음 __init__으로 '초기화'한다"]

- `type-call` **type.__call__** [concept] 별칭=['type.__call__']
  - 첫 등장: 04-singleton.html · 원고 · … 파이썬 특유의 것이다. 첫째, 파이썬에서 AuditLogger() 는 type.__call__ 이 __new__ 로 객체를 얻은 뒤 그것이 해…
  - 용어집 정의(short): 클래스 호출 `Cls()`를 실제로 처리하는 메서드; `__new__`를 부르고 결과가 그 클래스의 인스턴스면 `__init__`을 부른다.
  - 책 안의 기존 설명: ['04 · type.__call__ 이 __new__ 로 객체를 얻은 뒤']

- `dict` **__dict__** [gloss] 별칭=['__dict__', '인스턴스 __dict__']
  - 첫 등장: 04-singleton.html · 코드 src/04_singleton/03_variants.py · …class BorgLogger: """[Borg] 모든 인스턴스가 같은 __dict__를 공유한다. Alex Martelli가 제안한 관용구. …
  - 용어집 정의(short): 인스턴스의 속성 이름과 값을 담은 딕셔너리. vars(obj)로 볼 수 있다.
  - 책 안의 기존 설명: ['04 · 인스턴스의 속성 저장소를 클래스 수준의 dict 하나로']

- `module-cache` **모듈 캐시(sys.modules)** [concept] 별칭=['import 캐시', 'sys.modules', '모듈 캐시(sys.modules)']
  - 첫 등장: 04-singleton.html · 코드 src/04_singleton/03_variants.py · …축: - 유일성을 '무엇이' 보장하는가 (클래스 자신 / 메타클래스 / import 캐시 / 함수 캐시) - 하위 클래스·테스트에서 교체할 수 …
  - 용어집 정의(short): 파이썬은 모듈을 첫 import 때 한 번만 실행하고 `sys.modules`에 캐시해, 이후 import는 같은 모듈 객체를 돌려준다.
  - 책 안의 기존 설명: ['00 · 모듈은 첫 import 때 한 번 실행되고 캐시되는']

- `functools-cache` **functools.cache** [gloss] 별칭=['@cache', 'cache_clear', 'functools.cache']
  - 첫 등장: 04-singleton.html · 원고 · … (2) 메타클래스, (3) Borg, (4) 모듈 수준 객체, (5) functools.cache 접근 함수를 나란히 놓는다. 각 방식에서 "…
  - 용어집 정의(short): 인자별로 첫 호출 결과를 저장해 두고 이후 같은 인자 호출에는 저장된 값을 돌려주는 데코레이터; `cache_clear()`로 비운다.
  - 책 안의 기존 설명: ['04 · 첫 호출 때 만들고 이후 같은 객체를 돌려준다']

- `global-interpreter-lock` **GIL** [concept] 별칭=['GIL']
  - 첫 등장: 04-singleton.html · 코드 src/04_singleton/02_singleton.py · …른 스레드가 먼저 만들었을 수 있으므로 다시 확인한다. CPython의 GIL이 있어도 '검사 후 대입' 사이에 스레드 전환이 일어날 수 있어 …
  - 용어집 정의(short): CPython에서 한 번에 한 스레드만 바이트코드를 실행하게 하는 전역 잠금; 바이트코드 하나의 원자성만 줄 뿐 '검사 후 대입' 같은 여러 동작 사이는 보호하지 않는다.
  - 책 안의 기존 설명: ['04 · GIL은 바이트코드 하나의 원자성을 줄 뿐']

- `cpython` **CPython** [gloss] 별칭=['CPython', 'CPython·PyPy', 'PyPy']
  - 첫 등장: 04-singleton.html · 코드 src/04_singleton/02_singleton.py · …기다리는 동안 다른 스레드가 먼저 만들었을 수 있으므로 다시 확인한다. CPython의 GIL이 있어도 '검사 후 대입' 사이에 스레드 전환이 …
  - 용어집 정의(short): 파이썬 언어의 구현체들. CPython은 C로 만든 표준 구현, PyPy는 JIT 컴파일러를 쓰는 대안 구현으로 메모리 회수 시점 등이 다르다.

- `bytecode` **바이트코드** [concept] 별칭=['__code__', 'co_names', '바이트코드']
  - 첫 등장: 04-singleton.html · 원고 · … "파이썬에는 GIL이 있으니 괜찮다"는 흔한 믿음은 틀렸다. GIL은 바이트코드 하나의 원자성을 줄 뿐, 검사와 대입이라는 두 동작 사이를 보…
  - 용어집 정의(short): 파이썬 소스를 컴파일한 중간 명령어. 함수의 __code__.co_names에는 그 함수가 참조하는 전역 이름이 담긴다.

- `lock` **threading.Lock** [concept] 별칭=['threading.Lock', '내부 잠금', '잠금', '잠금 없이']
  - 첫 등장: 04-singleton.html · 원고 · …한 싱글턴이다. 앞부분은 유일성 구현이다. __new__ 의 이중 검사 잠금과 __init__ 의 _initialized 가드가 각각 어떤 함정…
  - 용어집 정의(short): 한 번에 한 스레드만 임계 구역에 들어가게 하는 동기화 도구; `with lock:`으로 잡고 놓는다.

- `threading-barrier` **threading.Barrier** [gloss] 별칭=['Barrier', 'threading.Barrier']
  - 첫 등장: 04-singleton.html · 코드 src/04_singleton/03_variants.py · …때 서로 다른 인스턴스가 몇 개 나오는지 센다.""" barrier = threading.Barrier(n) # 모든 스레드를 출발선에 세웠다가…
  - 용어집 정의(short): 지정한 수의 스레드가 모두 도착할 때까지 기다렸다가 한꺼번에 통과시키는 동기화 도구.
  - 책 안의 기존 설명: ['04 · 모든 스레드를 출발선에 세웠다가 한꺼번에 출발시킨다']

- `late-binding` **늦은 바인딩** [concept] 별칭=['늦은 바인딩']
  - 첫 등장: 04-singleton.html · 코드 src/04_singleton/04_injection.py · …본 인자는 반복문 변수를 람다가 '현재 값'으로 붙잡게 하려는 관용구다(늦은 바인딩 방지). results: list[bool] = [] thr…
  - 용어집 정의(short): 클로저가 변수의 값을 정의 시점이 아니라 호출 시점에 찾는 성질; 반복문 안 람다가 마지막 값만 보는 함정의 원인이며 `f=f` 기본 인자로 피한다.

- `pytest` **pytest** [gloss] 별칭=['caplog', 'pytest', 'pytest 픽스처', '픽스처']
  - 첫 등장: 04-singleton.html · 코드 src/04_singleton/02_singleton.py · …한 테스트가 리셋하는 순간 같은 프로세스의 다른 테스트 로그가 사라진다(pytest-xdist처럼 프로세스로 나누는 러너에서는 워커마다 싱글턴이…
  - 용어집 정의(short): 파이썬의 대표적 테스트 프레임워크; 픽스처로 준비·정리를 주입하고(예: 로그 캡처용 `caplog`), pytest-xdist 플러그인으로 테스트를 여러 워커 프로세스에 나눠 병렬 실행한다.

- `fixture` **픽스처** [gloss] 별칭=['트랜잭션 롤백', '픽스처']
  - 첫 등장: 04-singleton.html · 원고 · …적으로 틀리지는 않는다. 그리고 테스트는 반드시 다른 풀(테스트 DB, 트랜잭션 롤백 픽스처)을 써야 한다. 숨은 전역 풀은 테스트가 운영 DB…
  - 용어집 정의(short): 테스트 실행 전 준비하고 끝난 뒤 정리하는 테스트 환경 구성 요소(테스트 DB, 트랜잭션 롤백 등).

- `logging-getlogger` **logging 모듈과 로거 레지스트리** [concept] 별칭=['getLogger', 'logging 모듈과 로거 레지스트리', 'logging.basicConfig', 'logging.getLogger']
  - 첫 등장: 04-singleton.html · 원고 · … 값으로서의 싱글턴이다( is 비교가 의미를 가지려면 하나여야 한다). logging.getLogger(name) 은 이름별 레지스트리로, 같은…
  - 용어집 정의(short): 표준 로깅 모듈; `logging.getLogger(name)`은 이름별로 로거를 하나만 두는 레지스트리이고, 핸들러·포맷 구성은 진입점에서 한 번 한다.
  - 책 안의 기존 설명: ['04 · logging.getLogger(name) 은 이름별 레지스트리로']

- `gunicorn` **gunicorn** [gloss] 별칭=['gunicorn']
  - 첫 등장: 04-singleton.html · 원고 · …app() 의 docstring이 지적하듯 싱글턴은 프로세스당 하나다. gunicorn이 워커를 네 개 띄우면 싱글턴 기록기도 넷이고, 체인은 …
  - 용어집 정의(short): 파이썬 웹 앱을 여러 워커 프로세스로 띄워 서비스하는 WSGI 서버.

- `thread` **스레드** [concept] 별칭=['멀티스레드', '스레드']
  - 첫 등장: 04-singleton.html · 원고 · …영 코드에 _reset_for_tests() 를 넣어 달라고 요청했고, 스레드 기반 병렬 실행을 켜자 한 테스트의 리셋이 같은 프로세스에서 돌던…
  - 용어집 정의(short): 한 프로세스 안에서 동시에 실행되는 실행 흐름. 스레드 풀은 미리 만든 스레드들에 작업을 나눠 준다.
  - 감사 메모: ['4장에서 먼저 쓰였음.']

- `race-condition` **경쟁 조건** [concept] 별칭=['경쟁', '경쟁 조건']
  - 첫 등장: 04-singleton.html · 원고 · … 해결한다. 그러나 2차 고통(테스트 격리 붕괴, 숨은 의존성, 초기화 경쟁)은 싱글턴 자신이 만든다. 그리고 그 원인은 싱글턴이 서로 다른 두…
  - 용어집 정의(short): 여러 실행 흐름이 공유 상태에 접근하는 순서·타이밍에 따라 결과가 달라지는 결함(예: 검사와 대입 사이에 다른 스레드가 끼어듦).
  - 책 안의 기존 설명: ['04 · 검사와 대입 사이에 다른 스레드가 끼어들 수 있다']

- `atomicity` **원자성** [concept] 별칭=['원자성', '원자적']
  - 첫 등장: 04-singleton.html · 원고 · …L이 있으니 괜찮다"는 흔한 믿음은 틀렸다. GIL은 바이트코드 하나의 원자성을 줄 뿐, 검사와 대입이라는 두 동작 사이를 보호하지 않는다. […
  - 용어집 정의(short): 여러 단계가 전부 적용되거나 전부 적용되지 않거나 둘 중 하나여서 중간 상태가 남지 않는 성질.

- `reentrancy` **재진입** [concept] 별칭=['재진입']
  - 첫 등장: 04-singleton.html · 코드 src/04_singleton/02_singleton.py · …2) record()의 기록 순서 직렬화. threading.Lock은 재진입이 안 되므로, record() 안에서 # 잠금을 쥔 채 Audit…
  - 용어집 정의(short): 이미 그 잠금(또는 함수)을 쥐고 있는 같은 스레드가 다시 들어갈 수 있는 성질; `threading.Lock`은 재진입할 수 없고 `RLock`은 가능하다.
  - 책 안의 기존 설명: ['99 · 이것을 재진입이라 부른다']
  - 감사 메모: ["99장 03_wms.py BatteryGuard docstring('1) 재진입: 관찰자는 통지가…')이 원고 3.1절 정의보다 먼저 읽힌다. docstring은 결과만 말하고 뜻은 설명하지 않는다. 책 전체 첫 등장은 04장 코드 주석('threading.Lock은 재진입이 안 되므로')으로, 재진입 가능 잠금이라는 다른 폭의 의미다."]

- `deadlock` **교착 상태** [concept] 별칭=['교착', '교착 상태']
  - 첫 등장: 04-singleton.html · 코드 src/04_singleton/02_singleton.py · …에서 # 잠금을 쥔 채 AuditLogger()를 부르는 코드가 생기면 교착한다 — 분리하려면 인스턴스 잠금을 따로 둔다. _lock = thr…
  - 용어집 정의(short): 실행 흐름들이 서로(또는 자신이) 쥔 자원을 기다리며 영원히 멈춘 상태.

- `hash-function` **해시 함수** [gloss] 별칭=['SHA-256', 'hashlib', 'sha256', '해시 함수', '해시를 포함', '해싱']
  - 첫 등장: 04-singleton.html · 원고 · …작되지 않았음을 증명할 수 있어야 한다. 태윤은 각 기록에 직전 기록의 해시를 포함시키는 해시 체인 으로 한 파일에 순서대로 쓰는 AuditLo…
  - 용어집 정의(short): 임의 길이 데이터를 고정 길이 값으로 바꾸는 함수; 입력이 조금만 바뀌어도 결과가 크게 달라져 변조 탐지에 쓴다(SHA-256 등).

- `hash-chain` **해시 체인** [gloss] 별칭=['hash chain', '해시 체인']
  - 첫 등장: 04-singleton.html · 원고 · …명할 수 있어야 한다. 태윤은 각 기록에 직전 기록의 해시를 포함시키는 해시 체인 으로 한 파일에 순서대로 쓰는 AuditLogger 를 만들었…
  - 용어집 정의(short): 각 기록에 직전 기록의 해시를 넣어 이어 쓰는 구조; 한 줄만 고쳐도 뒤의 모든 해시가 어긋나 위·변조가 드러난다.
  - 책 안의 기존 설명: ['04 · 각 기록에 직전 기록의 해시를 포함시키는 해시 체인']

- `integrity` **무결성** [gloss] 별칭=['무결성']
  - 첫 등장: 04-singleton.html · 원고 · …는 자기 코드에서 AuditLogger() 를 만들었다. 분기 감사에서 무결성 검증 도구를 돌리자 수백 건이 "변조 의심"으로 나왔다. 실제 변…
  - 용어집 정의(short): 데이터가 허가 없이 바뀌거나 손상되지 않았음; 무결성 검증은 그 사실을 확인하는 절차다.

- `object-identity` **객체 정체성** [concept] 별칭=['identity', '객체 정체성', '정체성']
  - 첫 등장: 04-singleton.html · 코드 src/04_singleton/03_variants.py · … 캐시 / 함수 캐시) - 하위 클래스·테스트에서 교체할 수 있는가 - 정체성(identity)이 하나인가, 상태(state)만 공유하는가 (B…
  - 용어집 정의(short): 값이 같은지(==)와 별개로 두 참조가 '같은 객체'인지(is)를 가르는 성질.

- `lint` **린트** [gloss] 별칭=['린트']
  - 첫 등장: 04-singleton.html · 원고 · …부르는 곳은 build_app 하나"라는 규칙이고, grep 한 번이나 린트 규칙, 코드 리뷰로 지킨다. 싱글턴은 이것을 런타임에 강제한다. 그…
  - 용어집 정의(short): 코드를 실행하지 않고 규칙 위반·의심스러운 패턴을 찾아 주는 정적 점검(도구는 린터).

- `database-sequence` **DB 시퀀스** [gloss] 별칭=['DB 시퀀스']
  - 첫 등장: 04-singleton.html · 코드 src/04_singleton/04_injection.py · …띄우면 기록기도 4개다. 프로세스를 넘는 유일성은 단일 기록 프로세스나 DB 시퀀스 같은 외부 장치가 맡아야 한다. """ audit = Aud…
  - 용어집 정의(short): 데이터베이스가 원자적으로 증가하는 번호를 발급하는 객체; 여러 프로세스에 걸친 유일성을 보장할 수 있다.

- `append-only` **append-only** [gloss] 별칭=['append-only']
  - 첫 등장: 04-singleton.html · 코드 src/04_singleton/01_naive.py · … 16 # 체인의 첫 기록이 가리키는 가상의 '직전 해시' # 실제로는 append-only 파일(/var/log/emr/audit.log). …
  - 용어집 정의(short): 끝에 덧붙이기만 허용하고 기존 내용은 고칠 수 없게 한 저장 방식.

- `handler` **핸들러** [gloss] 별칭=['이벤트 핸들러', '핸들러']
  - 첫 등장: 04-singleton.html · 원고 · …r(name) 은 이름별 레지스트리로, 같은 이름에 다른 로거가 생기면 핸들러 설정이 갈라지므로 하나여야 한다. 공통점은 상태가 없거나 , 상태…
  - 용어집 정의(short): 이벤트나 요청이 들어왔을 때 그것을 처리하도록 등록된 함수.

- `audit-log` **감사 로그** [gloss] 별칭=['감사 로그']
  - 첫 등장: 04-singleton.html · 원고 · … 한결종합병원 의료정보팀의 개발자 태윤은 전자의무기록(EMR) 시스템의 감사 로그를 맡았다. 의료법과 개인정보 보호 규정에 따라 "누가, 언제,…
  - 용어집 정의(short): 누가 언제 어떤 데이터를 열람·수정했는지를 사후 검증할 수 있도록 빠짐없이 남기는 기록.
  - 책 안의 기존 설명: ['04 · "누가, 언제, 어떤 환자의 기록을 열람하거나 수정했는가"']

- `quality-assurance` **QA** [gloss] 별칭=['QA']
  - 첫 등장: 04-singleton.html · 원고 · … 체인은 다시 하나가 되었다. 문제는 해결된 것처럼 보였다. 두 달 뒤 QA 팀이 모듈별 단위 테스트를 도입하면서 새 문제가 터졌다. "처방 한…
  - 용어집 정의(short): 품질 보증 — 테스트 등으로 소프트웨어 품질을 검증하는 업무(또는 그 팀).

- `notimplemented-ellipsis` **NotImplemented와 Ellipsis** [concept] 별칭=['Ellipsis', 'NotImplemented ,', 'NotImplemented와 Ellipsis']
  - 첫 등장: 04-singleton.html · 원고 · …스트에서 대체할 필요가 거의 없을 때다. 표준 라이브러리의 None , NotImplemented , Ellipsis 는 값으로서의 싱글턴이다(…
  - 용어집 정의(short): 파이썬에 단 하나씩만 존재하는 내장 상수 객체(None과 같은 '값으로서의 싱글턴'); NotImplemented는 이항 연산 메서드가 '이 조합은 처리 못 함'을 알릴 때, Ellipsis(`...`)는 생략 표시에 쓴다.

- `test-runner` **테스트 러너** [concept] 별칭=['러너', '테스트 러너']
  - 첫 등장: 04-singleton.html · 코드 src/04_singleton/02_singleton.py · …른 테스트 로그가 사라진다(pytest-xdist처럼 프로세스로 나누는 러너에서는 워커마다 싱글턴이 따로 있다). """ cls._instanc…
  - 용어집 정의(short): 테스트를 찾아 실행하고 결과를 모으는 도구(unittest의 TextTestRunner 등).

- `transaction` **트랜잭션** [concept] 별칭=['트랜잭션']
  - 첫 등장: 04-singleton.html · 원고 · …적으로 틀리지는 않는다. 그리고 테스트는 반드시 다른 풀(테스트 DB, 트랜잭션 롤백 픽스처)을 써야 한다. 숨은 전역 풀은 테스트가 운영 DB…
  - 용어집 정의(short): 원자적으로 처리되어야 하는 작업 단위(전부 커밋 또는 전부 롤백).

- `rollback` **롤백** [gloss] 별칭=['롤백']
  - 첫 등장: 04-singleton.html · 원고 · …리지는 않는다. 그리고 테스트는 반드시 다른 풀(테스트 DB, 트랜잭션 롤백 픽스처)을 써야 한다. 숨은 전역 풀은 테스트가 운영 DB에 연결되…
  - 용어집 정의(short): 진행한 변경을 취소해 이전 상태로 되돌리는 것.

## 05-adapter.html — 29개

- `bridge` **브리지 패턴** [concept] 별칭=['브리지 패턴', '브리지(범위 밖)', '브리지는']
  - 첫 등장: 05-adapter.html · 원고 · … 통제한다. ⟦bridge⟧브리지 (범위 밖) 추상과 구현을 분리한다. 브리지 패턴은 추상 계층과 구현 계층을 따로 두어 각자 독립적으로 확장하…
  - 용어집 정의(short): 추상과 구현을 별도 계층으로 나누어 둘을 독립적으로 확장하게 하는 GoF 구조 패턴(이 책의 범위 밖); 설계 초기에 계획적으로 쓴다는 점에서 사후에 맞추는 어댑터와 다르다.
  - 책 안의 기존 설명: ['05 · 브리지는 설계 초기에 두 계층을 분리하려고 쓰고']

- `hexagonal-architecture-ports-and-adapters` **헥사고날 아키텍처(포트와 어댑터)** [concept] 별칭=['포트와 어댑터', '헥사고날 아키텍처', '헥사고날 아키텍처(포트와 어댑터)']
  - 첫 등장: 05-adapter.html · 원고 · …xagonal-architecture-ports-and-adapters⟧헥사고날 아키텍처(포트와 어댑터) 는 도메인이 바깥 세계와 만나는 인터페…
  - 용어집 정의(short): 도메인이 바깥 세계와 만나는 인터페이스(포트)를 도메인 쪽이 정의하고, 외부 기술마다 그 포트에 꽂히는 어댑터를 두는 아키텍처.
  - 책 안의 기존 설명: ["05 · PaymentGateway 는 도메인이 바깥 세계에 내미는 '포트'이고"]

- `object-adapter-class-adapter` **객체 어댑터와 클래스 어댑터** [concept] 별칭=['class adapter', 'object adapter', '객체 어댑터', '객체 어댑터와 클래스 어댑터', '클래스 어댑터']
  - 첫 등장: 05-adapter.html · 원고 · …제 연동에 적용한 ⟦object-adapter-class-adapter⟧객체 어댑터 (Adaptee를 필드로 갖고 위임하는 어댑터. 상속으로 만…
  - 용어집 정의(short): 어댑터의 두 변형: Adaptee를 필드로 보유(합성)하는 객체 어댑터와, Target과 Adaptee를 모두 상속하는 클래스 어댑터.
  - 책 안의 기존 설명: ['05 · Adaptee를 필드로 갖는 객체 어댑터(object adapter)']

- `interface-pollution` **인터페이스 오염** [concept] 별칭=['인터페이스 오염']
  - 첫 등장: 05-adapter.html · 원고 · …lution-order⟧MRO 와 ⟦interface-pollution⟧인터페이스 오염 관점에서 설명하라. MRO(메서드 결정 순서)는 메서드를…
  - 용어집 정의(short): 의도하지 않은 메서드(예: 상속한 SDK 메서드)가 공개 인터페이스에 섞여 들어 경계가 흐려지는 것.
  - 책 안의 기존 설명: ['05 · 클래스 어댑터는 SDK의 모든 공개 메서드를 상속하므로']

- `exception-translation` **예외 변환** [concept] 별칭=['예외 변환', '예외 체계의 번역']
  - 첫 등장: 05-adapter.html · 원고 · …례한다는 점에 주목하라. 용어 ⟦exception-translation⟧예외 변환 : 외부 라이브러리의 예외를 경계에서 잡아 우리 도메인의 예외…
  - 용어집 정의(short): 외부 라이브러리의 예외를 경계에서 잡아 우리 도메인의 예외로 바꿔 던지는 것; 호출자가 남의 예외 어휘를 몰라도 되게 한다.
  - 책 안의 기존 설명: ['05 · 남의 예외를 우리 예외로']

- `speculative-generality` **투기적 일반화** [concept] 별칭=['투기적 일반화']
  - 첫 등장: 05-adapter.html · 원고 · … 와 PgAAdapter 는 ⟦speculative-generality⟧투기적 일반화 (아직 오지 않은 요구를 짐작해 미리 만들어 둔 추상화. …
  - 용어집 정의(short): 아직 없는 미래 요구를 예상해 미리 추상화·확장 지점을 만들어 두는 코드 냄새.

- `boilerplate` **보일러플레이트** [gloss] 별칭=['보일러플레이트']
  - 첫 등장: 05-adapter.html · 원고 · …서드가 두 개뿐이라 (가)와 (나)가 아껴 주는 ⟦boilerplate⟧보일러플레이트 (본질적 로직 없이 형식 때문에 반복해 쓰는 상투적 코드)…
  - 용어집 정의(short): 본질적 로직 없이 형식 때문에 반복해서 써야 하는 상투적 코드(단순 위임 메서드 등).

- `staticmethod` **@staticmethod** [concept] 별칭=['@staticmethod', 'staticmethod']
  - 첫 등장: 05-adapter.html · 원고 · …출자가 남의 예외 이름을 몰라도 되게 한다. ⟦staticmethod⟧ @staticmethod : 메서드 정의 위에 붙이면 그 메서드가 sel…
  - 용어집 정의(short): self나 cls를 받지 않는, 클래스 이름공간에 둔 보통 함수를 만드는 데코레이터.

- `method-resolution-order` **MRO** [concept] 별칭=['MRO', '__mro__']
  - 첫 등장: 05-adapter.html · 원고 · …터를 기본으로 하는 이유를 ⟦method-resolution-order⟧MRO 와 ⟦interface-pollution⟧인터페이스 오염 관점에서…
  - 용어집 정의(short): 메서드·속성을 찾을 때 클래스들을 훑는 순서(메서드 결정 순서); 파이썬은 C3 선형화로 계산한다.
  - 책 안의 기존 설명: ['05 · 두 부모가 한 줄로 선형화된다']

- `c3-linearization` **C3 선형화** [concept] 별칭=['C3 선형화']
  - 첫 등장: 05-adapter.html · 원고 · … 불리는지 모호해지는 것이다. 파이썬은 ⟦c3-linearization⟧C3 선형화 (다중 상속 계층을 부모 순서를 지키는 한 줄의 MRO로 펴…
  - 용어집 정의(short): 다중 상속 계층을 부모 순서를 지키는 하나의 일렬 순서(MRO)로 펴는 알고리즘.

- `diamond-problem` **다이아몬드 문제** [gloss] 별칭=['다이아몬드 문제', '다이아몬드를']
  - 첫 등장: 05-adapter.html · 원고 · …도 취약하다. 흔한 오답: "다중 상속은 ⟦diamond-problem⟧다이아몬드 문제 가 있어서 위험하다." 다이아몬드 문제란 두 부모가 같은…
  - 용어집 정의(short): 두 부모가 같은 조상을 공유할 때 조상 메서드가 어느 경로로, 몇 번 호출되는지 모호해지는 다중 상속 문제.

- `dynamic-dispatch` **동적 디스패치** [concept] 별칭=['동적 디스패치', '디스패치되어']
  - 첫 등장: 05-adapter.html · 원고 · …는 self.refund(...) 까지 ⟦dynamic-dispatch⟧동적 디스패치 (호출할 메서드 구현을 실행 시점에 객체의 실제 타입으로 …
  - 용어집 정의(short): 호출할 메서드 구현을 실행 시점에 객체의 실제 타입으로 고르는 메커니즘; `self.m()`도 하위 클래스의 재정의로 간다.

- `bound-method` **바운드 메서드** [concept] 별칭=['바운드 메서드', '바인딩된']
  - 첫 등장: 05-adapter.html · 원고 · …두 갖는다. 함수 하나만 필요한 클라이언트라면 ⟦bound-method⟧바운드 메서드 client.make_payment 자체가 어댑터 다. 바…
  - 용어집 정의(short): 인스턴스에 묶인 메서드 객체(chart.redraw). 호출할 때 self가 자동으로 채워지며, 속성 접근 때마다 새로 만들어진다.
  - 책 안의 기존 설명: ['11 · 속성 접근 때마다 새로 만들어지는 임시 객체']

- `typing-runtime-checkable` **runtime_checkable** [concept] 별칭=['runtime_checkable']
  - 첫 등장: 05-adapter.html · 원고 · … (Target에 붙은 ⟦typing-runtime-checkable⟧ runtime_checkable 을 Protocol 정의 위에 붙이면 i…
  - 용어집 정의(short): Protocol에 붙여 `isinstance` 검사를 가능하게 하는 데코레이터; 메서드 이름의 존재만 보고 시그니처는 보지 않는다.
  - 책 안의 기존 설명: ["05 · isinstance()는 메서드 '이름' 존재만 보고"]

- `decimal-decimal` **Decimal** [concept] 별칭=['Decimal']
  - 첫 등장: 05-adapter.html · 원고 · … PaymentRequest(amount=⟦decimal-decimal⟧Decimal , currency="KRW") 객체로 감싸야 하고( De…
  - 용어집 정의(short): 이진 부동소수점 오차 없이 10진수를 정확히 표현하는 수 타입; 금액 계산에 쓴다.

- `future` **concurrent.futures.Future** [gloss] 별칭=['Future', 'concurrent.futures', 'concurrent.futures.Future']
  - 첫 등장: 05-adapter.html · 원고 · …eck 처럼 인스턴스 상태를 쓰지 않는 도우미에 쓴다. ⟦future⟧ concurrent.futures.Future : 아직 끝나지 않은 작업…
  - 용어집 정의(short): 아직 끝나지 않은 작업의 결과를 담을 자리; 다른 스레드가 `set_result()`로 채우면 `result(timeout=…)`로 기다려 꺼낸다.

- `asyncio` **asyncio** [gloss] 별칭=['async def', 'asyncio', 'loop.create_future']
  - 첫 등장: 05-adapter.html · 원고 · …es.Future 를 썼다. 만약 우리 서비스 전체가 ⟦asyncio⟧ asyncio (한 스레드 안에서 async def 로 정의한 함수들이 …
  - 용어집 정의(short): 이벤트 루프 위에서 `async`/`await` 코루틴으로 비동기 I/O를 처리하는 표준 라이브러리.

- `blocking` **블로킹** [concept] 별칭=['블로킹']
  - 첫 등장: 05-adapter.html · 원고 · …꾸기보다 훨씬 큰 결정이다. 호출자가 결과를 기다리며 ⟦blocking⟧블로킹 되기(결과가 준비될 때까지 호출한 쪽의 실행이 멈춰 서기) 때문이…
  - 용어집 정의(short): 호출이 결과가 준비될 때까지 호출한 쪽의 실행을 멈춰 두는 것.
  - 책 안의 기존 설명: ['05 · 호출자가 결과를 기다리며 블로킹되기 때문이다']

- `asynchronous-callback` **비동기와 콜백** [concept] 별칭=['비동기', '비동기와 콜백', '콜백']
  - 첫 등장: 05-adapter.html · 원고 · …이다. 결과는 반환값이 아니라 ⟦asynchronous-callback⟧콜백 으로 온다. 콜백은 호출할 때 함께 넘겨 둔 함수로, SDK가 작업…
  - 용어집 정의(short): 결과를 반환값으로 즉시 주지 않고, 작업이 끝나면 미리 넘겨받은 함수(콜백)를 불러 알리는 방식; 콜백은 다른 스레드에서 나중에 올 수 있다.

- `function-object` **함수 객체** [concept] 별칭=['함수 객체']
  - 첫 등장: 05-adapter.html · 원고 · …994년의 C++/Smalltalk에서 '⟦function-object⟧함수 객체 '(함수처럼 호출할 수 있는 값. 함수를 값으로 넘기기 어려운…
  - 용어집 정의(short): 함수처럼 호출할 수 있는 값; 함수가 일급이 아닌 언어에서는 호출 연산을 가진 객체로 흉내 낸다.

- `continuous-integration` **CI** [gloss] 별칭=['CI']
  - 첫 등장: 05-adapter.html · 원고 · …라. 팀이 정적 타입 검사를 ⟦continuous-integration⟧CI (지속적 통합: 변경을 올릴 때마다 빌드·테스트·정적 검사를 자동으…
  - 용어집 정의(short): 변경을 자주 통합하며 빌드·테스트·정적 검사를 자동으로 돌리는 지속적 통합 체계.

- `payment-gateway-provider` **PG사** [gloss] 별칭=['PG 연동', 'PG가', 'PG별', 'PG사']
  - 첫 등장: 05-adapter.html · 원고 · … 결제를 붙였다. 계약한 ⟦payment-gateway-provider⟧PG사 (전자결제대행사: 가맹점 대신 카드사 등과 결제 승인·취소·정산을…
  - 용어집 정의(short): 전자결제대행사 — 가맹점 대신 카드사 등과 결제 승인·취소·정산을 처리해 주는 회사.

- `minor-unit` **최소 화폐 단위** [gloss] 별칭=['minor unit', '최소 화폐 단위']
  - 첫 등장: 05-adapter.html · 원고 · …고객을 위한 간편결제 C가 들어왔다. C는 금액을 ⟦minor-unit⟧최소 화폐 단위(minor unit) 로 받는다. 통화를 소수 둘째 자리…
  - 용어집 정의(short): 통화의 소수 둘째 자리 등 가장 작은 단위로 금액을 정수 표현한 것(예: 15,000원 → 1500000).
  - 책 안의 기존 설명: ["05 · '소수 둘째 자리 단위(minor unit)'로 받는다"]

- `settlement-batch` **정산 배치** [gloss] 별칭=['배치 작업', '야간 배치', '정산 배치']
  - 첫 등장: 05-adapter.html · 원고 · …주문 서비스, 관리자 환불 화면, 야간 ⟦settlement-batch⟧정산 배치 (하루치 거래를 밤에 한꺼번에 집계해 PG사 기록과 맞춰 보는…
  - 용어집 정의(short): 일정 주기(예: 야간)로 쌓인 거래를 한꺼번에 집계·대사하는 일괄 작업.

- `authorization-capture` **승인과 매입** [gloss] 별칭=['승인+매입', '승인과 매입']
  - 첫 등장: 05-adapter.html · 원고 · …확보하는 단계)만, 다른 쪽은 ⟦authorization-capture⟧승인+매입 (매입은 승인된 금액을 실제로 청구하는 단계)을 한 번에 한다…
  - 용어집 정의(short): 카드 결제에서 한도를 확보하는 승인과, 승인된 금액을 실제로 청구하는 매입 단계.

- `single-source-of-truth` **단일 출처** [concept] 별칭=['단일 출처']
  - 첫 등장: 05-adapter.html · 원고 · … 것 얻는 것: 번역 규칙의 ⟦single-source-of-truth⟧단일 출처 (같은 지식이 시스템 안에 한 곳에만 정의되어 사본이 어긋날 …
  - 용어집 정의(short): 같은 지식(규칙·데이터)이 시스템 안에 오직 한 곳에만 정의되어 있는 상태. 복제본이 어긋날 여지가 없다.
  - 감사 메모: ["08·99장 표에서 '흐름 규칙의 단일 출처'로만 쓰인다."]

- `iterable` **이터러블** [concept] 별칭=['Iterable', 'iterable', '이터러블']
  - 첫 등장: 05-adapter.html · 원고 · …다. 해설 코드의 클라이언트 함수는 매개변수 타입을 ⟦iterable⟧ Iterable 로 적었다. 이터러블은 for 문으로 처음부터 순회할 수…
  - 용어집 정의(short): __iter__()를 호출할 때마다 새 이터레이터를 돌려주는 객체. for 문으로 몇 번이든 처음부터 돌 수 있다.
  - 책 안의 기존 설명: ['15 · __iter__() 가 새 반복자를 돌려준다']

- `itertools` **itertools** [gloss] 별칭=['cycle', 'islice', 'itertools', 'tee']
  - 첫 등장: 05-adapter.html · 원고 · …방식)를 먼저 훑고(SDK 흉내 코드의 거래번호는 ⟦itertools⟧ itertools 의 count() 로 매긴다. itertools 는 연…
  - 용어집 정의(short): 반복자를 조립하는 표준 라이브러리 모듈(cycle 무한 반복, islice 앞 n개 자르기, chain 이어 붙이기, repeat, tee 복제 등).
  - 책 안의 기존 설명: ['15 · 반복자를 조립하는 부품 상자']

- `user-experience` **UX** [gloss] 별칭=['UX']
  - 첫 등장: 05-adapter.html · 원고 · …잔액 부족이면 다른 카드를 권하라" 같은 ⟦user-experience⟧UX (사용자 경험)를 만들기 어려워진다. 필요한 구분은 Target의 …
  - 용어집 정의(short): 사용자가 제품을 쓰며 겪는 경험 전체.

## 06-decorator.html — 32개

- `transparent-wrapper` **투명 래퍼** [concept] 별칭=["'투명' 래퍼", '투명 래퍼', '투명 위임']
  - 첫 등장: 06-decorator.html · 원고 · …겉으로는 원본과 같아 보이게 만든 ⟦transparent-wrapper⟧투명 래퍼 를 만들면 어떻게 되는지 본다. …
  - 용어집 정의(short): 가로챌 메서드만 정의하고 나머지 속성 접근은 `__getattr__`로 감싼 객체에 넘겨, 겉으로는 원본과 같아 보이게 만든 래퍼.
  - 책 안의 기존 설명: ['06 · 가로챌 메서드만 정의하고 나머지는 __getattr__ 로 넘기는']

- `recursive-composition` **재귀적 합성** [concept] 별칭=['재귀 합성', '재귀적 중첩', '재귀적 합성']
  - 첫 등장: 06-decorator.html · 원고 · …진다(합성). 이 이중 관계가 ⟦recursive-composition⟧재귀적 중첩 (같은 타입의 래퍼가 래퍼를 다시 감싸, 구조가 자기와 같은…
  - 용어집 정의(short): 어떤 타입의 객체가 같은 타입의 객체를 품어 몇 겹이든 중첩될 수 있는 구조(데코레이터 체인, 컴포지트 트리).
  - 책 안의 기존 설명: ['06 · 다른 래퍼가 나를 다시 감쌀 수 있다(재귀적 합성)']

- `middleware` **미들웨어** [concept] 별칭=['미들웨어']
  - 첫 등장: 06-decorator.html · 원고 · …@login_required , (B) 앱 전체에 ⟦middleware⟧미들웨어 리스트(미들웨어는 모든 요청이 핸들러에 닿기 전후로 거치도록 줄…
  - 용어집 정의(short): 웹 앱 등에서 모든 요청이 핸들러에 닿기 전후로 거치게 줄지어 놓은 처리 단계; 사실상 앱 전체에 적용되는 데코레이터 체인이다.
  - 책 안의 기존 설명: ['06 · 미들웨어 리스트는 사실상 reduce 로 조립한 데코레이터 체인이다']

- `secure-by-default` **기본 보안** [concept] 별칭=['secure by default', '기본 보안']
  - 첫 등장: 06-decorator.html · 원고 · …로와 그 처리기)가 자동으로 보호되고(⟦secure-by-default⟧secure by default : 명시적으로 예외를 두지 않는 한 기본…
  - 용어집 정의(short): 명시적으로 예외를 두지 않는 한 기본값이 '보호됨'이 되게 하는 설계 원칙.
  - 책 안의 기존 설명: ['06 · 새 엔드포인트가 자동으로 보호되고(secure by default)']

- `decorator-syntax` **@ 데코레이터 문법** [concept] 별칭=['@ 데코레이터 문법', '@ 문법', '@decorator', '데코레이터 문법']
  - 첫 등장: 06-decorator.html · 원고 · …혼동되는 문제가 숨어 있다. 파이썬의 ⟦decorator-syntax⟧ @decorator 와 GoF의 데코레이터 패턴은 같은 것인가? ( @ …
  - 용어집 정의(short): 정의 바로 위에 `@deco`를 쓰면 정의 직후 `f = deco(f)`로 이름을 다시 묶는 문법 설탕; 결과가 무엇이어야 하는지는 강제하지 않으므로 GoF 데코레이터 패턴과는 범주가 다르다.
  - 책 안의 기존 설명: ['06 · 정의 직후 그 함수/클래스를 어떤 호출 가능 객체에 넘기고']

- `syntactic-sugar` **문법 설탕** [concept] 별칭=['문법 설탕', '설탕']
  - 첫 등장: 06-decorator.html · 원고 · … 감싸진 '팩토리'가 되는지 보라. 용어 ⟦syntactic-sugar⟧문법 설탕 : 새 기능을 더하지 않고 기존 표현을 짧고 읽기 좋게 쓰게 …
  - 용어집 정의(short): 새 기능을 더하지 않고 기존 표현을 더 짧고 읽기 좋게 쓰게 해 주는 문법.

- `functools-wraps` **functools.wraps** [gloss] 별칭=['__wrapped__', 'functools.wraps', 'wraps']
  - 첫 등장: 06-decorator.html · 원고 · … 짧고 읽기 좋게 쓰게 해 주는 문법. ⟦functools-wraps⟧ functools.wraps : 래퍼 함수가 원래 함수의 __name__…
  - 용어집 정의(short): 래퍼 함수가 원래 함수의 `__name__`·`__doc__` 등을 물려받고 `__wrapped__`로 원본에 닿게 해 주는 데코레이터.
  - 책 안의 기존 설명: ['06 · 래퍼 함수가 원래 함수의 __name__, __doc__을 물려받고']
  - 감사 메모: ['6장에서 먼저 다뤄졌을 가능성.']

- `functools-reduce` **functools.reduce** [gloss] 별칭=['functools.reduce', 'reduce']
  - 첫 등장: 06-decorator.html · 원고 · …__ 로 원본에 닿게 해 주는 도구. ⟦functools-reduce⟧ functools.reduce : 두 값을 받는 함수를 목록에 왼쪽부터 …
  - 용어집 정의(short): 이항 함수를 시퀀스에 왼쪽부터 차례로 적용해 하나의 값으로 접는 함수; 래퍼 목록을 한 체인으로 조립하는 데 쓸 수 있다.

- `property` **@property** [concept] 별칭=['@price.setter', '@property', 'property', 'property setter', '프로퍼티']
  - 첫 등장: 06-decorator.html · 원고 · … 왼쪽부터 차례로 적용해 하나의 값으로 접는 함수. ⟦property⟧ @property : 메서드를 속성처럼 읽게(필요하면 대입하게) 만드는 …
  - 용어집 정의(short): 메서드를 속성처럼 읽고(getter) 대입하게(setter) 만드는 데코레이터. 대입 시점에 검사·통지 같은 코드를 끼울 수 있다.

- `descriptor` **디스크립터** [concept] 별칭=['디스크립터']
  - 첫 등장: 06-decorator.html · 원고 · …대로 돌려줄 뿐이다. @property 는 함수를 ⟦descriptor⟧디스크립터 객체( __get__ / __set__ 을 구현해 클래스 속성…
  - 용어집 정의(short): `__get__`/`__set__`을 구현해 클래스 속성 접근 방식을 가로채는 객체; property·메서드 바인딩의 기반이다.

- `introspection` **내성** [concept] 별칭=['introspection', '내성', '내성(introspection)']
  - 첫 등장: 06-decorator.html · 원고 · …__ 로 원본에 닿을 수 있게 해, 디버깅과 ⟦introspection⟧내성(introspection) , 즉 실행 중에 객체의 이름·타입·문서…
  - 용어집 정의(short): 실행 중에 객체의 타입·속성·이름·문서 등을 조사하는 것.

- `flask` **Flask** [gloss] 별칭=['Flask']
  - 첫 등장: 06-decorator.html · 원고 · … @dataclass 는 클래스에 메서드를 생성해 넣으며, ⟦flask⟧Flask (파이썬 경량 웹 프레임워크)의 @app.route 는 URL…
  - 용어집 정의(short): 파이썬 경량 웹 프레임워크; `@app.route`로 URL과 핸들러 함수를 등록한다.

- `python-enhancement-proposal` **PEP** [concept] 별칭=['PEP']
  - 첫 등장: 06-decorator.html · 원고 · … @ 문법을 도입한 ⟦python-enhancement-proposal⟧PEP 318(PEP는 파이썬 언어·표준 라이브러리 변경을 제안하고 기록…
  - 용어집 정의(short): 파이썬 언어·표준 라이브러리 변경을 제안하고 기록하는 공식 문서(예: PEP 318은 데코레이터 문법을 도입했다).

- `rate-limiting` **호출 제한** [gloss] 별칭=['with_rate_limit', '호출 제한']
  - 첫 등장: 06-decorator.html · 원고 · …부를 bool 로 반환)은 유지한다. 코드의 ⟦rate-limiting⟧호출 제한 은 일정 시간 안의 호출 횟수를 제한해 과도한 요청을 막는 기…
  - 용어집 정의(short): 일정 시간 안의 호출 횟수를 제한해 과도한 요청을 막는 것.
  - 책 안의 기존 설명: ['06 · 1초에 한 번만']

- `endpoint` **엔드포인트** [gloss] 별칭=['엔드포인트']
  - 첫 등장: 06-decorator.html · 원고 · …대부분 보호' 요구에는 (B) 미들웨어 가 맞다. 새 ⟦endpoint⟧엔드포인트 (요청을 받는 개별 URL 경로와 그 처리기)가 자동으로 보호…
  - 용어집 정의(short): 웹 API에서 요청을 받는 개별 경로(URL)와 그 처리기.

- `rest-resource` **REST 리소스** [gloss] 별칭=['REST', 'REST 리소스']
  - 첫 등장: 06-decorator.html · 원고 · …해야 한다. 해설 코드의 Resource 는 ⟦rest-resource⟧REST 리소스 를 흉내 낸다. REST 방식 웹 API에서 URL로 식…
  - 용어집 정의(short): REST 방식 웹 API에서 URL로 식별되고 GET·POST 같은 HTTP 메서드로 조작되는 대상.

- `mqtt-broker` **MQTT와 브로커** [gloss] 별칭=['MQTT', 'MQTT와 브로커', '브로커']
  - 첫 등장: 06-decorator.html · 원고 · …eway⟧게이트웨이 가 측정값을 모아 클라우드의 ⟦mqtt-broker⟧MQTT 브로커 로 올린다. 게이트웨이는 현장 센서들의 값을 모아 클라우…
  - 용어집 정의(short): IoT에서 많이 쓰는 경량 발행-구독 메시징 프로토콜; 브로커는 발행된 메시지를 구독자에게 중계하는 서버다.

- `payload` **페이로드** [gloss] 별칭=['payload', '페이로드']
  - 첫 등장: 06-decorator.html · 원고 · …든 첫 버전은 단순했다. MqttChannel.send(⟦payload⟧payload ) 가 JSON 한 줄을 받아 브로커에 publish한다(…
  - 용어집 정의(short): 메시지·패킷에서 헤더 등을 뺀 실제 전달 데이터.

- `stream-cipher` **스트림 암호** [gloss] 별칭=['XOR', '스트림 암호', '키스트림']
  - 첫 등장: 06-decorator.html · 원고 · …이썬 객체를 JSON 문자열로 바꾸는 함수. ⟦stream-cipher⟧스트림 암호 : 키로부터 만든 무작위처럼 보이는 바이트열(키스트림)을 평…
  - 용어집 정의(short): 키로부터 만든 의사난수 바이트열(키스트림)을 평문과 XOR해 암호화하는 방식; 출력이 무작위처럼 보여 압축되지 않는다.

- `aes-gcm` **AES-GCM** [gloss] 별칭=['AES-GCM', 'nonce']
  - 첫 등장: 06-decorator.html · 원고 · … toy_encrypt 는 교육용이며, 실제 제품에서는 ⟦aes-gcm⟧AES-GCM (AES 암호를 GCM 모드로 써서 암호화와 변조 검증을 …
  - 용어집 정의(short): AES 블록 암호를 GCM 모드로 써서 암호화와 변조 검증을 함께 제공하는 표준 방식(nonce와 인증 태그가 붙는다).

- `zlib` **zlib** [gloss] 별칭=['zlib']
  - 첫 등장: 06-decorator.html · 원고 · …스가 너무 많이 안다. 용어 아래 코드가 쓰는 도구들이다. ⟦zlib⟧ zlib : DEFLATE 알고리즘으로 데이터를 압축·해제하는 파이썬 표…
  - 용어집 정의(short): DEFLATE 알고리즘으로 데이터를 압축·해제하는 라이브러리(파이썬 표준 모듈).

- `checksum` **체크섬** [gloss] 별칭=['체크섬']
  - 첫 등장: 06-decorator.html · 원고 · …화 뒤에 압축하면 줄일 것이 없고, 압축 포맷의 헤더·⟦checksum⟧체크섬 (데이터 손상을 확인하려고 붙이는 짧은 검증 값)만큼 오히려 커진…
  - 용어집 정의(short): 데이터 손상을 확인하려고 붙이는 짧은 검증 값.

- `lifecycle` **생명주기** [gloss] 별칭=['생명주기', '수명 관리']
  - 첫 등장: 06-decorator.html · 원고 · … 프록시는 접근을 통제 하며 흔히 실제 객체의 생성·⟦lifecycle⟧생명주기 (객체가 만들어져 쓰이다가 해제되기까지의 전 과정)까지 관리한다…
  - 용어집 정의(short): 객체가 생성되어 쓰이다가 해제·소멸되기까지의 전 과정. 누가 그 시점을 결정하는가가 설계 쟁점이 된다.

- `telemetry` **텔레메트리** [gloss] 별칭=['텔레메트리']
  - 첫 등장: 06-decorator.html · 원고 · …격 장치가 측정값을 자동으로 수집해 보내는 데이터를 ⟦telemetry⟧텔레메트리 라 한다. 임베디드 개발자 준호가 만든 첫 버전은 단순했다. …
  - 용어집 정의(short): 원격 장비가 측정값·상태를 자동으로 수집해 중앙으로 보내는 데이터(또는 그 전송).

- `gateway` **게이트웨이(IoT)** [gloss] 별칭=['IoT 게이트웨이', '게이트웨이(IoT)', '게이트웨이가', '게이트웨이는']
  - 첫 등장: 06-decorator.html · 원고 · …을 모아 클라우드의 ⟦mqtt-broker⟧MQTT 브로커 로 올린다. 게이트웨이는 현장 센서들의 값을 모아 클라우드로 중계하는 장치이고, MQ…
  - 용어집 정의(short): 현장 센서들의 측정값을 모아 클라우드로 중계하는 장치.

- `batching` **배치(묶어 보내기)** [gloss] 별칭=['(배치)', 'BatchingChannel', '묶는 배치', '배치 래퍼', '배치(묶어 보내기)']
  - 첫 등장: 06-decorator.html · 코드 src/06_decorator/01_naive.py · … 요금 때문에 압축, 보안 감사 때문에 암호화, 배터리 때문에 10건씩 묶는 배치, 장애 진단용 전송 로그. 농장마다 필요한 조합이 다르다. 준…
  - 용어집 정의(short): 여러 건을 모아 한 번에 처리·전송하는 것; 호출 횟수를 줄이는 대신 버퍼를 비우는(flush) 책임이 생긴다.
  - 책 안의 기존 설명: ['06 · "10건씩 모아서 보내기(배치)"']

- `buffer-flush` **버퍼와 flush** [gloss] 별칭=['flush', '버퍼와 flush']
  - 첫 등장: 06-decorator.html · 원고 · …버퍼, 버퍼에 남은 것을 모두 내보내는 연산을 ⟦buffer-flush⟧flush 라 한다), 현장 장애를 추적하던 운영팀은 "몇 바이트를 언제…
  - 용어집 정의(short): 버퍼는 데이터를 바로 내보내지 않고 모아 두는 임시 저장 공간이고, flush는 버퍼에 남은 것을 모두 내보내는 연산이다.
  - 책 안의 기존 설명: ['06 · 버퍼에 남은 것을 모두 내보낸다']

- `redundancy` **중복성** [gloss] 별칭=['중복성']
  - 첫 등장: 06-decorator.html · 원고 · …고 확인하라. 해설 보기 압축은 데이터 안의 반복(⟦redundancy⟧중복성 ) , 즉 되풀이되는 부분을 찾아 짧은 참조로 바꾸는 일이다. 센…
  - 용어집 정의(short): 데이터 안의 반복되는 부분; 압축은 이를 짧은 참조로 바꾸는 일이라 중복성이 없는 암호문은 압축되지 않는다.
  - 책 안의 기존 설명: ['06 · 압축은 데이터 안의 반복(중복성) 을 찾아']

- `monotonic-clock` **time.monotonic** [gloss] 별칭=['time.monotonic']
  - 첫 등장: 06-decorator.html · 원고 · … 제한해 과도한 요청을 막는 기능이고, ⟦monotonic-clock⟧ time.monotonic() 은 시스템 시각 조정에 영향받지 않고 늘어…
  - 용어집 정의(short): 시스템 시각 조정에 영향받지 않고 단조 증가하는 시계 값(초)을 돌려주는 함수; 경과 시간 측정에 쓴다.

- `transparency` **투명성** [concept] 별칭=['투명성', '투명하']
  - 첫 등장: 06-decorator.html · 원고 · …성처럼 읽게(필요하면 대입하게) 만드는 표기. ⟦transparency⟧투명성 : 감싼 객체가 원래 객체와 똑같이 보여서, 쓰는 쪽이 차이를 알…
  - 용어집 정의(short): 대리 객체가 실제 객체와 완전히 똑같이 보여서, 클라이언트가 그 차이를 알 수도 알 필요도 없는 성질.

- `json-dumps` **json.dumps** [gloss] 별칭=['json.dumps']
  - 첫 등장: 06-decorator.html · 원고 · …으로 데이터를 압축·해제하는 파이썬 표준 모듈. ⟦json-dumps⟧ json.dumps : 파이썬 객체를 JSON 문자열로 바꾸는 함수. ⟦…
  - 용어집 정의(short): 파이썬 객체를 JSON 문자열로 직렬화하는 함수.

- `compiler` **컴파일러** [gloss] 별칭=['컴파일', '컴파일러']
  - 첫 등장: 06-decorator.html · 원고 · …력 [1]처럼 기능 넷이면 열여섯이다. 게다가 상속은 ⟦compiler⟧컴파일 시점에 고정되므로(컴파일은 소스를 실행 가능한 형태로 번역하는 단…
  - 용어집 정의(short): 소스 코드를 실행 가능한 형태(기계어·바이트코드)로 번역하는 프로그램.

## 07-composite.html — 22개

- `visitor` **방문자 패턴** [concept] 별칭=['방문자 패턴', '방문자(Visitor)', '방문자(범위 밖)']
  - 첫 등장: 07-composite.html · 원고 · … most_common() 으로 많은 순서대로 꺼낸다. ⟦visitor⟧방문자 패턴 : 객체 구조의 클래스를 고치지 않고 새 연산을 추가하려고,…
  - 용어집 정의(short): 객체 구조의 클래스를 고치지 않고 새 연산을 추가하기 위해, 연산을 별도 방문자 객체에 모으고 이중 디스패치로 호출하는 GoF 행위 패턴(이 책의 범위 밖).
  - 책 안의 기존 설명: ['07 · 컴포지트 위에 연산을 추가하는 GoF의 해법']

- `macro-command` **매크로 커맨드** [concept] 별칭=['매크로 커맨드']
  - 첫 등장: 07-composite.html · 원고 · …코드가 빌더의 좋은 후보다. 커맨드(12장) ⟦macro-command⟧매크로 커맨드 (여러 커맨드를 묶어 하나처럼 실행·취소하는 복합 커맨드)…
  - 용어집 정의(short): 여러 커맨드를 묶어 하나의 커맨드처럼 실행·취소하는 복합 커맨드(12장에서 다룸).

- `transparency-safety` **투명성과 안전성(컴포지트 설계 선택)** [concept] 별칭=['안전성 설계', '안전성(safety)', '투명성 설계', '투명성(transparency)', '투명성과 안전성(컴포지트 설계 선택)']
  - 첫 등장: 07-composite.html · 원고 · … 원전은 두 길을 모두 제시한다. ⟦transparency-safety⟧투명성(transparency) : add/remove 를 Compone…
  - 용어집 정의(short): 컴포지트에서 자식 관리 메서드(add/remove)를 Component에 둘지(투명성: 클라이언트가 전혀 구별하지 않음, 대신 Leaf가 계약을 어길 소지) Composite에만 둘지(안전성: 타입 검사로 실수를 막음, 대신 조립 코드가 Composite 타입을 앎)의 선택.
  - 책 안의 기존 설명: ['07 · add/remove 를 Component에 둔다']

- `yield-from` **yield from** [concept] 별칭=['yield from']
  - 첫 등장: 07-composite.html · 원고 · …mbly 가 모두 구현하는 다형적 walk() (⟦yield-from⟧ yield from 재귀 제너레이터. yield from 은 하위 제너레…
  - 용어집 정의(short): 하위 이터러블의 값을 하나씩 그대로 흘려보내는(순회를 위임하는) 제너레이터 문법.
  - 책 안의 기존 설명: ['07 · yield from은 하위 제너레이터의 값을 그대로 흘려보낸다', '15 · 하위 반복자에 순회를 위임한다']

- `iterator` **이터레이터** [concept] 별칭=['Iterator', 'iterator', '이터레이터']
  - 첫 등장: 07-composite.html · 원고 · …) 에 재귀가 한 줄도 없다는 점을 확인하라. 용어 ⟦iterator⟧ Iterator (이터레이터): next() 를 부를 때마다 다음 값을 …
  - 용어집 정의(short): __next__()로 다음 값을 주고 끝나면 StopIteration을 던지는, '한 번 쓰면 닳는 커서' 객체. __iter__()는 자기 자신을 돌려준다.
  - 책 안의 기존 설명: ['15 · __next__() 로 다음 값을 주고, 끝나면 StopIteration']
  - 감사 메모: ["08장 03_pythonic.py의 typing.Iterator 타입 힌트가 먼저. 15장의 한국어 대표어는 '반복자'(패턴명과 겹침)."]

- `container-protocol` **컨테이너 프로토콜** [concept] 별칭=['__contains__', '컨테이너 프로토콜']
  - 첫 등장: 07-composite.html · 원고 · …_iter__ · __len__ ·⟦container-protocol⟧ __contains__ 가 조립품을 파이썬 컨테이너처럼 만들며(이 특수 …
  - 용어집 정의(short): `__iter__`, `__len__`, `__contains__` 등을 구현해 객체가 `for`, `len()`, `in`과 어울리게 하는 특수 메서드 묶음.
  - 책 안의 기존 설명: ['07 · __iter__ , __len__ , __contains__ 를 구현하면 조립품이 for']

- `functools-singledispatch` **functools.singledispatch** [concept] 별칭=['functools.singledispatch', 'singledispatch']
  - 첫 등장: 07-composite.html · 원고 · …과 어울린다), (3) ⟦functools-singledispatch⟧ singledispatch 가 새 연산을 클래스 밖의 함수로 추가한다(첫…
  - 용어집 정의(short): 첫 인자의 타입에 따라 등록된 구현을 골라 호출하는 제네릭 함수 데코레이터; 타입별 분기를 한 디스패치 표에 모은다.
  - 책 안의 기존 설명: ["07 · 타입별 분기'를 디스패치 표 한 곳으로 모은 것이다"]

- `counter` **collections.Counter** [gloss] 별칭=['Counter', 'collections.Counter', 'most_common']
  - 첫 등장: 07-composite.html · 원고 · …r[...] 는 이런 값의 흐름을 돌려준다는 뜻이다. ⟦counter⟧ collections.Counter : 키별 개수를 세는 딕셔너리. +=…
  - 용어집 정의(short): 키별 개수를 세는 딕셔너리 하위 클래스; `+=`로 누적하고 `most_common()`으로 많은 순서대로 꺼낸다.

- `recursion-limit` **재귀 한도** [concept] 별칭=['RecursionError', '재귀 한도']
  - 첫 등장: 07-composite.html · 원고 · …의존 경로. 리드타임 계산이 이것이다. ⟦recursion-limit⟧ RecursionError : 파이썬이 허용하는 최대 재귀 깊이(재귀 한…
  - 용어집 정의(short): 파이썬이 허용하는 최대 재귀 호출 깊이(기본 약 1,000); 넘으면 RecursionError가 난다.

- `circular-reference` **순환 참조** [gloss] 별칭=['순환 참조']
  - 첫 등장: 07-composite.html · 원고 · … 프레임에도 들어간다. 다른 하나는 ⟦circular-reference⟧순환 참조 , 즉 A가 B를 참조하고 B가 다시 A를 참조하는 고리다. …
  - 용어집 정의(short): A가 B를 참조하고 B가 다시 A를 참조하는 고리; 트리 순회에서는 무한 재귀를 낳는다.
  - 책 안의 기존 설명: ['07 · "A의 하위에 B, B의 하위에 A"']

- `directed-acyclic-graph` **DAG** [gloss] 별칭=['DAG']
  - 첫 등장: 07-composite.html · 원고 · …00)를 넘으면 나는 예외. ⟦directed-acyclic-graph⟧DAG : 방향성 비순환 그래프. 간선에 방향이 있고 고리가 없는 그래프…
  - 용어집 정의(short): 방향성 비순환 그래프 — 간선에 방향이 있고 고리가 없는 그래프; 공유 노드를 허용하는 트리의 일반화다.
  - 책 안의 기존 설명: ['07 · 같은 Part 객체가 여러 조립품에 들어가도 된다(트리가 아니라 DAG가 된다)']

- `depth-first-search` **깊이 우선 탐색** [gloss] 별칭=['깊이 우선', '깊이 우선 순회', '깊이 우선 탐색', '너비 우선']
  - 첫 등장: 07-composite.html · 원고 · …려준다. render() 는 트리를 ⟦depth-first-search⟧깊이 우선 으로 출력한다. 한 가지를 끝까지 내려간 뒤 되돌아오며 순회하…
  - 용어집 정의(short): 트리·그래프를 한 가지를 끝까지 내려간 뒤 되돌아오며 순회하는 방식(반대는 형제를 먼저 훑는 너비 우선).

- `critical-path` **임계 경로** [gloss] 별칭=['임계 경로', '최장 경로']
  - 첫 등장: 07-composite.html · 원고 · …라. add() 의 순환 검사도 보라. 용어 ⟦critical-path⟧최장 경로 (임계 경로): 병렬로 진행되는 작업 중 전체 완료 시간을 결…
  - 용어집 정의(short): 병렬로 진행되는 작업 중 전체 완료 시간을 결정하는 가장 긴 의존 경로.
  - 책 안의 기존 설명: ["07 · 리드타임 39일은 '실린더 블록 30일 → 엔진 조립 5일"]

- `cache-invalidation` **캐시 무효화** [concept] 별칭=['무효화', '캐시 무효화']
  - 첫 등장: 07-composite.html · 원고 · …시하되, 부품 단가가 바뀌면 캐시를 ⟦cache-invalidation⟧무효화 하는(낡은 항목을 지우거나 갱신하는) 책임이 생긴다는 점을 기억하…
  - 용어집 정의(short): 원본이 바뀌었을 때 캐시의 낡은 항목을 지우거나 갱신하는 일.

- `no-op` **no-op** [gloss] 별칭=['no-op']
  - 첫 등장: 07-composite.html · 원고 · …. 흔한 오답: "단품의 add() 를 아무것도 하지 않게(⟦no-op⟧no-op , 아무 일도 하지 않는 연산) 만들면 LSP 문제가 없다."…
  - 용어집 정의(short): 아무 일도 하지 않는 연산.
  - 책 안의 기존 설명: ['07 · 아무것도 하지 않게(no-op)']

- `bill-of-materials` **BOM** [gloss] 별칭=['BOM', '부품표']
  - 첫 등장: 07-composite.html · 원고 · …하면 끝이었다. 그런데 설계팀의 실제 ⟦bill-of-materials⟧부품표(BOM, Bill of Materials) 는 평평하지 않았다. …
  - 용어집 정의(short): 부품표 — 완제품을 이루는 조립품·단품과 수량을 계층으로 적은 목록.
  - 책 안의 기존 설명: ['07 · 경운기는 엔진과 프레임으로, 엔진은 실린더 블록']
  - 감사 메모: ['3·7장에서 정의되었을 가능성.']

- `lead-time` **리드타임** [gloss] 별칭=['리드타임']
  - 첫 등장: 07-composite.html · 원고 · …오는 부품 기준으로 완제품이 언제 나올 수 있는가"(⟦lead-time⟧리드타임 : 발주·착수부터 완료까지 걸리는 기간)를, 품질팀은 "단종 예…
  - 용어집 정의(short): 발주·착수부터 완료(입고·완성)까지 걸리는 기간; 조립품은 가장 늦은 하위 부품 + 자기 조립 기간이다.
  - 책 안의 기존 설명: ['07 · 가장 늦게 들어오는 부품 기준으로 완제품이 언제 나올 수 있는가']

- `bom-explosion` **소요량 전개** [gloss] 별칭=['BOM explosion', '소요량 전개']
  - 첫 등장: 07-composite.html · 원고 · … "경운기 10대에 볼트가 몇 개 필요한가"(⟦bom-explosion⟧소요량 전개 : BOM을 펼쳐 완제품 n개에 필요한 단품별 총수량을 계산…
  - 용어집 정의(short): BOM을 펼쳐 완제품 n개에 필요한 단품별 총수량을 계산하는 것.
  - 책 안의 기존 설명: ['07 · 경운기 10대에 볼트가 몇 개 필요한가']

- `labor-cost` **공임** [gloss] 별칭=['공임']
  - 첫 등장: 07-composite.html · 원고 · …은 다시 링과 핀으로 이루어진다. 조립품마다 조립 ⟦labor-cost⟧공임 (조립 작업에 드는 인건비성 비용)이 붙는다. 소연은 단품 클래스와…
  - 용어집 정의(short): 조립 등 작업에 드는 인건비성 비용.

- `enterprise-resource-planning` **ERP** [gloss] 별칭=['ERP']
  - 첫 등장: 07-composite.html · 원고 · … 조립하는 코드는 ⟦enterprise-resource-planning⟧ERP (생산·구매·재고·회계 정보를 통합 관리하는 전사 시스템) 데이터…
  - 용어집 정의(short): 생산·구매·재고·회계 등 기업 자원 정보를 통합 관리하는 전사 시스템.

- `edge` **간선** [gloss] 별칭=['간선']
  - 첫 등장: 07-composite.html · 원고 · … 목표는 클라이언트의 무지(無知)다. 아래 그림의 '(수량은 ⟦edge⟧간선 에)'라는 표기에서 간선은 두 노드(부모와 자식)를 잇는 연결을 말…
  - 용어집 정의(short): 그래프에서 두 노드를 잇는 연결; 컴포지트 BOM에서는 (자식, 수량) 쌍이 간선 역할을 한다.

- `domain-exception` **도메인 예외** [concept] 별칭=['도메인 예외']
  - 첫 등장: 07-composite.html · 원고 · …fHasNoChildrenError 는 ⟦domain-exception⟧도메인 예외 다. 파이썬 내장 예외나 특정 클라이언트의 표현(HTTP 상…
  - 용어집 정의(short): HTTP 상태 코드 같은 특정 클라이언트의 표현이 아니라 업무 의미(예: 업로드 실패)로 이름 붙인 예외 타입.

## 08-facade.html — 21개

- `subsystem` **서브시스템** [concept] 별칭=['서브시스템']
  - 첫 등장: 08-facade.html · 원고 · …루면서 각자 독립적으로 관리되는 하위 구성 요소들을 ⟦subsystem⟧서브시스템 이라 부르자. 서브시스템은 각자 단순하다. 문제는 아래쪽의 두…
  - 용어집 정의(short): 하나의 기능 영역을 함께 이루는 여러 클래스·서비스의 묶음. 퍼사드는 서브시스템 앞에 단순한 진입점을 둔다.
  - 책 안의 기존 설명: ['08 · 대상은 객체 하나가 아니라 서브시스템(여러 객체)']
  - 감사 메모: ["GoF 퍼사드의 참여자 'Subsystem classes'이기도 하다. 08장 2절·01_naive.py에서 #structure보다 먼저 설명 없이 쓰인다."]

- `law-of-demeter` **디미터 법칙** [concept] 별칭=['디미터 법칙']
  - 첫 등장: 08-facade.html · 원고 · …존 수를 세는 것이 이 장의 측정 지표다. ⟦law-of-demeter⟧디미터 법칙 위반. 디미터 법칙(최소 지식 원칙)은 객체가 직접 협력하는…
  - 용어집 정의(short): 객체는 직접 협력하는 객체에게만 말을 걸어야 하며, 받은 결과의 내부 구조를 따라 들어가 판단하지 말라는 원칙(최소 지식 원칙).
  - 감사 메모: ['08장은 위반 사례(UI가 booking.passport_verified를 들여다봄)만 들고 법칙 자체는 정의하지 않는다.']

- `god-object` **신 객체** [concept] 별칭=['God object', '신 객체']
  - 첫 등장: 08-facade.html · 원고 · …면 표시·통신·조율 같은 기술적 코드와 구별된다. ⟦god-object⟧신 객체(God object) 는 너무 많은 책임과 지식을 떠안아 시스템…
  - 용어집 정의(short): 너무 많은 책임과 지식을 떠안아 시스템의 대부분이 의존하게 된 거대한 클래스.
  - 감사 메모: ["08장 02_facade.py docstring에 영문 병기만 있고, 원고 '함정' 상자는 징후만 나열한다."]

- `pass-through-method` **통과용 메서드** [concept] 별칭=['pass-through', '통과용 메서드', '통과용(pass-through) 메서드']
  - 첫 등장: 08-facade.html · 원고 · …이 기능을 추가할 때마다 퍼사드에 ⟦pass-through-method⟧통과용(pass-through) 메서드 , 즉 받은 호출을 가공 없이 서…
  - 용어집 정의(short): 받은 호출을 아무 가공 없이 다른 객체의 같은 메서드로 넘기기만 하는 메서드.
  - 책 안의 기존 설명: ['08 · seats.get_seat_map() 을 그대로 부르기만']
  - 감사 메모: ["08장 '함정' ④에서 영문 병기로 먼저 나오고, 정의는 6절 '쓰지 말아야 할 때'에 있다."]

- `business-logic` **업무 로직** [concept] 별칭=['비즈니스 흐름', '업무 로직']
  - 첫 등장: 08-facade.html · 원고 · …g이 경계하는 두 개념도 미리 밝혀 둔다. ⟦business-logic⟧업무 로직 은 요금 계산·좌석 배정처럼 도메인 규칙 자체를 구현한 코드로…
  - 용어집 정의(short): 도메인의 규칙 자체(요금 계산, 좌석 배정 등)를 구현한 코드. 화면 표시·통신·조율 같은 기술적 코드와 구별된다.

- `compensating-action` **보상 처리** [concept] 별칭=['보상 규칙', '보상 처리']
  - 첫 등장: 08-facade.html · 원고 · …앞 단계의 효과를 되돌리는 처리를 ⟦compensating-action⟧보상 처리 라 한다. def upload_handler(request):…
  - 용어집 정의(short): 여러 단계 중 뒤 단계가 실패했을 때, 이미 끝난 앞 단계의 효과를 되돌리는 별도의 처리(예: 저장한 원본 삭제).
  - 책 안의 기존 설명: ['08 · 실패 시 원본 삭제라는 보상 규칙']
  - 감사 메모: ["08장 연습문제 2 문제 코드 주석('보상 처리: CLI에서 빠뜨리기 쉽다')이 먼저."]

- `protection-proxy` **보호 프록시** [concept] 별칭=['보호 프록시']
  - 첫 등장: 08-facade.html · 원고 · …제로 막아야 한다면 그것은 9장 프록시(⟦protection-proxy⟧보호 프록시 : 호출자의 권한에 따라 실제 객체로의 접근을 허용하거나 거…
  - 용어집 정의(short): 호출자의 권한에 따라 실제 객체로의 접근을 허용하거나 거부하는 프록시.
  - 책 안의 기존 설명: ['09 · 접근 권한 : 호출자에 따라 허용·거부']
  - 감사 메모: ["08장(퍼사드)에서 '(9장)' 예고와 함께 세 번 먼저 쓰인다."]

- `all` **__all__** [gloss] 별칭=['__all__']
  - 첫 등장: 08-facade.html · 원고 · …다. 아래 파일은 (1) 모듈 수준 함수 하나로 된 퍼사드와 ⟦all⟧ __all__ ( from 모듈 import * 로 내보낼 이름 목록. …
  - 용어집 정의(short): from 모듈 import * 로 노출할 이름 목록. 패키지의 공개 API를 선언하는 관례로도 쓰인다.
  - 책 안의 기존 설명: ["08 · 'from 이모듈 import *'로 노출할 이름"]

- `package-init-py` **__init__.py** [gloss] 별칭=['__init__.py']
  - 첫 등장: 08-facade.html · 원고 · …역순으로 닫힌다는 점을 확인하라. 용어 ⟦package-init-py⟧ __init__.py : 디렉터리를 파이썬 패키지로 만드는 파일. 패키지…
  - 용어집 정의(short): 디렉터리를 파이썬 패키지로 만드는 파일. import 패키지 시 실행되며 공개 이름을 모아 내보낼 수 있다.

- `leading-underscore-convention` **밑줄 접두사 관례** [concept] 별칭=['밑줄 접두사', '밑줄 접두사 관례', '이름 앞 밑줄']
  - 첫 등장: 08-facade.html · 원고 · …보낼 수 있다. ⟦leading-underscore-convention⟧이름 앞 밑줄 ( _name ): '내부용, 공개 API 아님'을 뜻하는…
  - 용어집 정의(short): 이름 앞 밑줄(_name)은 '내부용, 공개 API 아님'을 뜻하는 관례. 접근을 실제로 막지는 않는다.
  - 책 안의 기존 설명: ["08 · 파이썬 관례상 '모듈 내부용'"]

- `subprocess` **subprocess** [gloss] 별칭=['Popen', 'subprocess']
  - 첫 등장: 08-facade.html · 원고 · …사드, (3) 표준 라이브러리의 대표적 퍼사드인 ⟦subprocess⟧ subprocess .run 을 보여 준다( subprocess 는 자식…
  - 용어집 정의(short): 자식 프로세스를 실행하고 입출력·종료 코드를 다루는 표준 라이브러리. run()은 Popen·파이프·대기를 감싼 퍼사드다.

- `shutil` **shutil** [gloss] 별칭=['shutil', 'shutil.copytree', 'shutil.rmtree']
  - 첫 등장: 08-facade.html · 원고 · … 하는 사람은 직접 쓴다(데모 [3]의 두 번째 줄). ⟦shutil⟧ shutil .copytree() ( shutil 은 디렉터리 복사·삭제…
  - 용어집 정의(short): 파일·디렉터리 복사(copytree)와 삭제(rmtree) 같은 고수준 파일 작업 표준 라이브러리.

- `urllib-request-urlopen` **urllib.request.urlopen** [gloss] 별칭=['urllib.request.urlopen', 'urlopen']
  - 첫 등장: 08-facade.html · 원고 · …stat 호출을 묶는다), ⟦urllib-request-urlopen⟧ urllib.request.urlopen() (URL을 열어 응답을 돌려…
  - 용어집 정의(short): URL을 열어 응답을 돌려주는 표준 라이브러리 함수.

- `advance-passenger-information-system` **APIS** [gloss] 별칭=['APIS', '사전 승객정보']
  - 첫 등장: 08-facade.html · 원고 · …에 ⟦advance-passenger-information-system⟧사전 승객정보(APIS) 전송 의무가 생겼다. 발권 전에 승객 정보를 미…
  - 용어집 정의(short): 항공사가 발권 전에 승객 정보를 도착국 당국에 보내는 사전 승객정보 제도. 미전송 시 항공사가 벌금을 문다.
  - 책 안의 기존 설명: ['08 · 발권 전에 승객 정보를 미국 당국에 보내지 않으면']

- `passenger-name-record` **PNR** [gloss] 별칭=['PNR', 'pnr']
  - 첫 등장: 08-facade.html · 원고 · … 그 차이의 결과다. 코드의 ⟦passenger-name-record⟧ pnr 은 항공 예약 기록 번호(PNR, 예약 번호)이고, ⟦machin…
  - 용어집 정의(short): 항공 예약 기록 번호(예약 번호).
  - 책 안의 기존 설명: ['08 · 예약 번호와 성으로 예약을 찾는다']
  - 감사 메모: ['약어 풀이 없음. 코드 매개변수명으로만 등장.']

- `machine-readable-zone` **MRZ** [gloss] 별칭=['MRZ', 'mrz']
  - 첫 등장: 08-facade.html · 원고 · …(PNR, 예약 번호)이고, ⟦machine-readable-zone⟧ mrz 는 여권 하단의 기계 판독 영역(MRZ)에 정해진 형식으로 인쇄된…
  - 용어집 정의(short): 여권 하단의 기계 판독 영역. 이름·여권번호 등이 정해진 형식으로 인쇄되어 있다.
  - 책 안의 기존 설명: ['08 · MRZ(기계 판독 영역)의 성이 예약과']

- `transcoding` **트랜스코딩** [gloss] 별칭=['Transcoder', '트랜스코더', '트랜스코딩']
  - 첫 등장: 08-facade.html · 원고 · …CLI에서도 필요해졌다. 퍼사드로 리팩터링하라. ⟦transcoding⟧트랜스코딩 (동영상을 다른 해상도·형식으로 다시 인코딩하는 작업)이 실패…
  - 용어집 정의(short): 동영상을 다른 해상도·코덱 형식으로 다시 인코딩하는 작업.

- `codec` **코덱** [gloss] 별칭=['코덱']
  - 첫 등장: 08-facade.html · 원고 · … 핸들러의 몫이다. 해설 코드의 트랜스코더는 지원하지 않는 ⟦codec⟧코덱 (영상·음성을 압축하고 푸는 방식)이면 실패한다고 흉내 낸다. 흔한…
  - 용어집 정의(short): 영상·음성을 압축(인코딩)하고 푸는(디코딩) 방식.

- `overbooking` **오버부킹** [gloss] 별칭=['오버부킹']
  - 첫 등장: 08-facade.html · 원고 · …변경, 수하물 추가), 직원용(수동 좌석 지정, ⟦overbooking⟧오버부킹 처리, 탑승 마감. 오버부킹은 좌석 수보다 예약을 더 받는 항공…
  - 용어집 정의(short): 좌석 수보다 예약을 더 받는 항공사 관행. 초과 승객 처리 절차가 따른다.

- `redirect` **리다이렉트** [gloss] 별칭=['리다이렉트']
  - 첫 등장: 08-facade.html · 원고 · …) (URL을 열어 응답을 돌려주는 함수. 연결·요청·⟦redirect⟧리다이렉트 처리를 묶는다. 리다이렉트는 서버가 다른 URL로 다시 요청하…
  - 용어집 정의(short): HTTP 서버가 다른 URL로 다시 요청하라고 안내하는 응답.

- `streaming` **스트리밍** [gloss] 별칭=['스트리밍']
  - 첫 등장: 08-facade.html · 원고 · …님'을 뜻하는 관례. 접근을 실제로 막지는 않는다. ⟦streaming⟧스트리밍 : 결과를 한꺼번에 모으지 않고 생기는 대로 조금씩 받아 처리하…
  - 용어집 정의(short): 데이터를 전부 받은 뒤가 아니라 도착하는 대로 조금씩 처리하는 방식.

## 09-proxy.html — 31개

- `caching-proxy` **캐싱 프록시** [concept] 별칭=['캐싱 프록시']
  - 첫 등장: 09-proxy.html · 원고 · …용·거부 ProtectedImageProxy ⟦caching-proxy⟧캐싱 프록시 (caching, GoF의 ⟦smart-reference⟧s…
  - 용어집 정의(short): 실제 객체 호출 결과를 기억해 두었다가 같은 요청에 재사용함으로써 반복 비용을 줄이는 프록시.
  - 책 안의 기존 설명: ['09 · 반복 비용 : 결과를 재사용']

- `remote-proxy` **원격 프록시** [concept] 별칭=['원격 프록시']
  - 첫 등장: 09-proxy.html · 원고 · …를 재사용 CachingArchiveProxy ⟦remote-proxy⟧원격 프록시 (remote) 위치 : 다른 프로세스·머신의 객체를 로컬처…
  - 용어집 정의(short): 다른 프로세스·머신에 있는 객체를 로컬 객체처럼 호출할 수 있게 대신 서 있는 프록시.
  - 책 안의 기존 설명: ['09 · 다른 프로세스·머신의 객체를 로컬처럼']

- `smart-reference` **스마트 참조** [concept] 별칭=['smart reference', '스마트 참조']
  - 첫 등장: 09-proxy.html · 원고 · …⟧캐싱 프록시 (caching, GoF의 ⟦smart-reference⟧smart reference 계열. 스마트 참조는 실제 객체에 접근할 때…
  - 용어집 정의(short): 실제 객체에 접근할 때 참조 횟수 세기·잠금·캐시 같은 부가 동작을 함께 수행하는 프록시(GoF의 분류).
  - 감사 메모: ['09장 표에 영문으로만 등장.']

- `default-deny` **기본 거부** [concept] 별칭=['기본 거부', '기본은 거부']
  - 첫 등장: 09-proxy.html · 원고 · …CY ) 하나 로 선언하고, 표에 없는 동작은 ⟦default-deny⟧기본 거부 (명시적으로 허용되지 않은 것은 모두 거부)하는 것이다. 원래…
  - 용어집 정의(short): 명시적으로 허용되지 않은 것은 모두 거부하는 정책. 새 동작을 추가하면서 규칙을 빠뜨려도 '허용'이 아니라 '거부'로 실패한다.
  - 책 안의 기존 설명: ['09 · 표에 없는 동작은 기본 거부 하는 것']
  - 감사 메모: ["13장에서 상태 패턴의 '기본은 거부' 정책으로 다시 쓴다."]

- `invariant` **불변식** [concept] 별칭=['불변식']
  - 첫 등장: 09-proxy.html · 원고 · …프록시로 설계했다면 "모든 경로가 캐시를 거친다"는 ⟦invariant⟧불변식 (어떤 연산 전후에도 항상 참으로 유지되어야 하는 조건)을 보장해…
  - 용어집 정의(short): 객체나 시스템이 어떤 연산 전후에도 항상 참으로 유지해야 하는 조건(예: 모든 경로가 캐시를 거친다).

- `security-boundary` **보안 경계** [concept] 별칭=['보안 경계']
  - 첫 등장: 09-proxy.html · 원고 · …름에 드러내는 명시적 API가 낫다. ⟦security-boundary⟧보안 경계 가 프로세스 안에 있을 때. 보안 경계란 신뢰할 수 없는 코드…
  - 용어집 정의(short): 신뢰할 수 없는 코드가 넘을 수 없도록 강제되는 경계(프로세스·서비스 경계 등). 같은 프로세스 안의 파이썬 객체 경계는 이에 해당하지 않는다.

- `weak-reference` **약한 참조** [concept] 별칭=['weakref', '약한 참조']
  - 첫 등장: 09-proxy.html · 원고 · …키로 결과를 기억하는 LRU 캐시), (4) 표준 라이브러리의 프록시인 weakref.proxy 를 차례로 본다. weakref 는 ⟦weak-…
  - 용어집 정의(short): 대상 객체를 살려 두지 않는 참조. 다른 참조가 모두 사라지면 대상은 회수되고, 약한 참조는 죽은 참조가 된다.
  - 책 안의 기존 설명: ["09 · 실제 객체의 생명주기를 '소유하지 않는' 참조"]

- `reference-counting` **참조 카운트** [concept] 별칭=['참조 카운트']
  - 첫 등장: 09-proxy.html · 원고 · … 이 '아직 안 만듦'을 나타낸다. ⟦reference-counting⟧참조 카운트 : 객체를 가리키는 참조 수를 세어 0이 되는 즉시 회수하는…
  - 용어집 정의(short): 객체를 가리키는 참조 수를 세어 0이 되는 즉시 회수하는 CPython의 메모리 관리 방식.

- `garbage-collection` **가비지 컬렉션** [concept] 별칭=['GC', 'gc.collect', '가비지 컬렉션']
  - 첫 등장: 09-proxy.html · 원고 · …CPython의 메모리 관리 방식. ⟦garbage-collection⟧가비지 컬렉션 (GC): 더 이상 쓰이지 않는 객체의 메모리를 자동으로 …
  - 용어집 정의(short): 더 이상 쓰이지 않는 객체의 메모리를 자동으로 회수하는 기능. gc.collect()는 순환 참조까지 찾아 회수하도록 강제한다.

- `functools-cached-property` **cached_property** [gloss] 별칭=['cached_property']
  - 첫 등장: 09-proxy.html · 원고 · … 내부에서 지연시키는 ⟦functools-cached-property⟧ cached_property (첫 접근 때 한 번 계산한 값을 인스턴스에…
  - 용어집 정의(short): 첫 접근 때 한 번 계산한 값을 인스턴스 __dict__에 저장해, 이후에는 일반 속성처럼 읽히게 하는 데코레이터.
  - 책 안의 기존 설명: ['09 · 첫 접근 때 한 번 계산되어 인스턴스 __dict__에']

- `functools-lru-cache` **lru_cache** [gloss] 별칭=['cache_info', 'lru_cache']
  - 첫 등장: 09-proxy.html · 원고 · …3) 캐싱 프록시의 함수 버전인 ⟦functools-lru-cache⟧ lru_cache (함수 인자를 키로 결과를 기억하는 LRU 캐시), (…
  - 용어집 정의(short): 함수 인자를 키로 결과를 기억하고, 용량을 넘으면 가장 오래 안 쓴 항목부터 버리는 캐시 데코레이터.
  - 책 안의 기존 설명: ['09 · 함수 결과 캐시 — 캐싱 프록시의 가장 가벼운 형태']

- `class` **__class__** [gloss] 별칭=['__class__']
  - 첫 등장: 09-proxy.html · 원고 · …나하나 정의해야 하고, isinstance 까지 속이려면 ⟦class⟧ __class__ (객체가 속한 클래스를 가리키는 속성)를 프로퍼티로 재…
  - 용어집 정의(short): 객체가 속한 클래스를 가리키는 속성. 대입하면 객체의 클래스 자체가 바뀐다.
  - 감사 메모: ['13장 5.2절에서 교체 트릭으로 다룬다.']

- `unittest-mock` **unittest.mock** [gloss] 별칭=['unittest.mock']
  - 첫 등장: 09-proxy.html · 원고 · …)를 프로퍼티로 재정의하는 기교가 필요하다(⟦unittest-mock⟧ unittest.mock 이 그렇게 한다. 이는 표준 테스트 프레임워크 …
  - 용어집 정의(short): 테스트용 가짜 객체(Mock)를 만드는 표준 라이브러리. 어떤 속성 접근에도 응답하는 범용 대역을 제공한다.

- `collections-ordereddict` **OrderedDict** [concept] 별칭=['OrderedDict', 'move_to_end', 'popitem']
  - 첫 등장: 09-proxy.html · 원고 · …를 통해 받는지 모른다. ⟦collections-ordereddict⟧ OrderedDict (삽입 순서를 다루는 move_to_end , po…
  - 용어집 정의(short): 삽입 순서를 다루는 연산(move_to_end, popitem(last=False))을 제공하는 딕셔너리. LRU 캐시를 몇 줄로 구현할 수 있다.

- `sentinel` **센티널** [concept] 별칭=['_UNSET', '센티널']
  - 첫 등장: 09-proxy.html · 원고 · … len() 의 결과가 어떻게 다른지 비교하라. 용어 ⟦sentinel⟧센티널 : None 같은 정상 값과 구별되도록 object() 로 만든 …
  - 용어집 정의(short): None 같은 정상 값과 구별되도록 만든 '표시용' 고유 객체(object()). '아직 없음'을 None과 헷갈리지 않게 표현한다.
  - 책 안의 기존 설명: ["09 · '아직 안 만듦' 표시. None을 쓰면 factory가"]
  - 감사 메모: ["용어 '센티널' 자체는 쓰이지 않는다. 15장 연습문제 4의 iter(p.skip, None)도 센티널 형태의 iter()를 설명 없이 쓴다."]

- `abstractmethods` **__abstractmethods__** [gloss] 별칭=['__abstractmethods__']
  - 첫 등장: 09-proxy.html · 원고 · …가 추상 메서드 이름을 모아 두는 집합 ⟦abstractmethods⟧ __abstractmethods__ 를 쓴다), 데모 [3]이 권한 없는…
  - 용어집 정의(short): ABC 클래스가 아직 구현되지 않은 추상 메서드 이름을 담아 두는 집합.

- `xmlrpc-client-serverproxy` **xmlrpc.client.ServerProxy** [gloss] 별칭=['ServerProxy', 'xmlrpc', 'xmlrpc.client.ServerProxy']
  - 첫 등장: 09-proxy.html · 원고 · …체를 로컬처럼 파이썬 ⟦xmlrpc-client-serverproxy⟧ xmlrpc.client.ServerProxy (원격 XML-RPC 서버…
  - 용어집 정의(short): 원격 XML-RPC 서버의 메서드를 로컬 메서드처럼 부르게 해 주는 표준 라이브러리의 원격 프록시.

- `unittest` **unittest** [gloss] 별칭=['TestCase', 'setUp', 'tearDown', 'unittest']
  - 첫 등장: 09-proxy.html · 원고 · …)를 프로퍼티로 재정의하는 기교가 필요하다(⟦unittest-mock⟧ unittest.mock 이 그렇게 한다. 이는 표준 테스트 프레임워크 …
  - 용어집 정의(short): 표준 테스트 프레임워크. TestCase의 run()이 setUp → 테스트 메서드 → tearDown 순서를 정해 부른다.

- `geographic-information-system` **GIS** [gloss] 별칭=['GIS']
  - 첫 등장: 09-proxy.html · 원고 · …토 관측 기관의 ⟦geographic-information-system⟧GIS (지리 정보를 저장·분석·표시하는 시스템) 개발자 수아는 위성 영…
  - 용어집 정의(short): 지리 정보를 저장·분석·표시하는 시스템.

- `raster` **래스터** [gloss] 별칭=['raster', '래스터']
  - 첫 등장: 09-proxy.html · 원고 · …한, 캐시)가 이 화면에만 있다는 점에 주목하라. 코드의 ⟦raster⟧raster (래스터)는 영상을 격자(픽셀) 값의 배열로 표현한 데이터이…
  - 용어집 정의(short): 영상을 격자(픽셀) 값의 배열로 표현한 데이터.

- `tile` **원본 타일** [gloss] 별칭=['원본 타일', '타일']
  - 첫 등장: 09-proxy.html · 원고 · …이브 뷰어를 맡았다. 위성이 찍은 장면 하나는 수백 MB짜리 ⟦tile⟧원본 타일 (큰 위성 영상을 사각형 조각 단위로 나눈 원본 데이터)이고,…
  - 용어집 정의(short): 큰 위성 영상을 나눈 사각형 조각 단위의 원본 데이터.

- `digital-elevation-model` **DEM** [gloss] 별칭=['DEM', '수치표고모델']
  - 첫 등장: 09-proxy.html · 원고 · …요한 대형 객체가 더 있다(⟦digital-elevation-model⟧수치표고모델 (DEM: 지표면의 고도를 격자 값으로 나타낸 데이터), ⟦…
  - 용어집 정의(short): 지표면의 고도를 격자 값으로 나타낸 수치표고모델.
  - 감사 메모: ['한국어 명칭만 병기.']

- `land-cover` **토지피복** [gloss] 별칭=['토지피복']
  - 첫 등장: 09-proxy.html · 원고 · …: 지표면의 고도를 격자 값으로 나타낸 데이터), ⟦land-cover⟧토지피복 (지표가 농경지·산림·수계 등 무엇으로 덮여 있는지) 분류 래스…
  - 용어집 정의(short): 지표가 농경지·산림·수계 등 무엇으로 덮여 있는지 분류한 정보.

- `hyperspectral-image` **초분광 영상** [gloss] 별칭=['HyperspectralCube', '초분광', '초분광 영상']
  - 첫 등장: 09-proxy.html · 원고 · … 가지 길 뷰어 팀이 수 GB짜리 ⟦hyperspectral-image⟧초분광 영상 큐브(수백 개의 좁은 파장 대역으로 찍어 화소마다 스펙트럼을…
  - 용어집 정의(short): 수백 개의 좁은 파장 대역(밴드)으로 찍어 화소마다 스펙트럼을 가진 영상(데이터 큐브).

- `security-clearance` **인가 등급** [gloss] 별칭=['clearance', '인가 등급']
  - 첫 등장: 09-proxy.html · 원고 · …에는 군사 보안 구역이 찍혀 있어, ⟦security-clearance⟧인가 등급 (사용자가 열람할 수 있는 기밀 수준)이 있는 사용자만 원본을…
  - 용어집 정의(short): 사용자가 볼 수 있는 기밀 수준. 영상의 민감도보다 낮으면 접근이 거부된다.
  - 책 안의 기존 설명: ['09 · clearance가 높을수록 민감 영상을 볼 수 있다']

- `extensible-markup-language` **XML** [gloss] 별칭=['XML']
  - 첫 등장: 09-proxy.html · 원고 · …verproxy⟧ xmlrpc.client.ServerProxy (원격 XML-RPC 서버의 메서드를 로컬 메서드처럼 부르게 해 주는 표준 라이…
  - 용어집 정의(short): 태그로 구조를 표현하는 텍스트 데이터 형식.

- `cache-hit` **캐시 적중** [gloss] 별칭=['캐시 적중']
  - 첫 등장: 09-proxy.html · 원고 · …격자(픽셀) 값의 배열로 표현한 데이터이고, 주석의 ⟦cache-hit⟧캐시 적중 은 요청한 값이 이미 캐시에 있어 다시 받지 않고 돌려준 경우…
  - 용어집 정의(short): 요청한 값이 캐시에 있어 실제 계산·요청 없이 돌려준 경우.

- `least-recently-used` **LRU** [gloss] 별칭=['LRU']
  - 첫 등장: 09-proxy.html · 원고 · …lse) 를 제공하는 딕셔너리)로 ⟦least-recently-used⟧LRU (용량이 차면 가장 오래 쓰이지 않은 항목부터 버리는 캐시 교체 …
  - 용어집 정의(short): 용량이 차면 가장 오래 쓰이지 않은 항목부터 버리는 캐시 교체 정책.
  - 책 안의 기존 설명: ['09 · 아니면 받아서 넣고 가장 오래된 것을 내보낸다']
  - 감사 메모: ['약어 풀이 없음. 메서드 docstring이 동작을 설명한다.']

- `remote-procedure-call` **원격 호출** [gloss] 별칭=['원격 호출']
  - 첫 등장: 09-proxy.html · 원고 · …으로 직렬화한다. 편리하지만, ⟦remote-procedure-call⟧원격 호출 (다른 프로세스·머신의 함수를 네트워크를 거쳐 호출하는 것)을…
  - 용어집 정의(short): 다른 프로세스·머신의 함수를 네트워크를 거쳐 호출하는 것(RPC).

- `partial-failure` **부분 실패** [gloss] 별칭=['부분 실패']
  - 첫 등장: 09-proxy.html · 원고 · …하는 것 자체가 위험이기도 하다. 지연, ⟦partial-failure⟧부분 실패 (일부 구성 요소나 요청만 실패하는 상황), 네트워크 예외가 …
  - 용어집 정의(short): 분산 시스템에서 일부 구성 요소나 요청만 실패하는 상황.

- `memory-leak` **메모리 누수** [gloss] 별칭=['누수', '메모리 누수']
  - 첫 등장: 09-proxy.html · 원고 · …. 캐시나 옵저버 목록(11장)이 객체를 붙잡아 ⟦memory-leak⟧메모리 누수 (쓰지 않는 객체가 참조에 붙잡혀 회수되지 않고 메모리를 계…
  - 용어집 정의(short): 더 이상 쓰지 않는 객체가 참조에 붙잡혀 회수되지 않고 메모리를 계속 차지하는 것.

## 10-strategy.html — 20개

- `entity` **엔티티** [concept] 별칭=['엔티티']
  - 첫 등장: 10-strategy.html · 원고 · … 어떻게 계산되는지'가 한 덩어리라 복제가 생긴다. 셋째, 정책이 주문 엔티티 깊숙이 박혀 있어 따로 떼어 시험할 수 없다. 넷째, 정책 변경이…
  - 용어집 정의(short): 값이 바뀌어도 같은 대상으로 추적되는 정체성(ID)을 가진 도메인 객체(예: 주문).

- `contract-2` **입력 계약** [concept] 별칭=['입력 계약']
  - 첫 등장: 10-strategy.html · 원고 · … 모든 정책에 공통인 규칙(구독 무료, 가게 할인)만 직접 처리한다. (입력 계약) FeeInput 전략이 알아야 하는 사실만 담은 좁은 입력.…
  - 용어집 정의(short): 메서드가 무엇을 받고 무엇을 보장하는지에 대한 약속. 10장은 시그니처뿐 아니라 '넘기는 인자의 폭'까지 계약이라 한다.
  - 책 안의 기존 설명: ['10 · calculate() 의 시그니처만이 아니라 인자의 폭']
  - 감사 메모: ["본문에는 '계약'이라는 일반어가 장마다 넓게 쓰여 별칭은 구체 표기만 넣었다."]

- `over-engineering` **과잉 설계** [concept] 별칭=['과잉 설계', '패턴 과잉']
  - 첫 등장: 10-strategy.html · 원고 · …는 곳에 SortStrategy 계층을 만드는 것은 파이썬에서 대표적인 과잉 설계다. 관련 패턴 관계 상태 (13장) 구조가 같다. 전략은 바깥…
  - 용어집 정의(short): 현재 문제에 필요한 것보다 많은 추상화·구조를 미리 넣는 것.

- `class-explosion` **클래스 폭발** [concept] 별칭=['클래스 폭발', '클래스가 폭발']
  - 첫 등장: 10-strategy.html · 원고 · …를 만드는 것인데, 이는 정확히 전략 패턴이 피하려 한 "상속으로 인한 클래스 폭발"을 되살린다. …
  - 용어집 정의(short): 변이의 축 여러 개를 상속으로 조합할 때 클래스 수가 축들의 곱만큼 늘어나는 현상.

- `pure-function` **순수 함수** [concept] 별칭=['순수 계산', '순수 함수']
  - 첫 등장: 10-strategy.html · 원고 · …스를 만들 필요가 없다. 전략의 성격 권하는 형태 이유 매개변수 없음, 순수 계산 모듈 수준 함수 클래스로 감싸면 소음만 는다. standard…
  - 용어집 정의(short): 같은 입력에 항상 같은 출력을 내고, 바깥 상태를 바꾸는 부수 효과가 없는 함수.

- `type-alias` **타입 별칭** [concept] 별칭=['타입 별칭']
  - 첫 등장: 10-strategy.html · 원고 · …한 dataclass )을 나란히 두었다. 모두 같은 FeePolicy 타입 별칭을 만족한다는 점에 주목하라. …
  - 용어집 정의(short): 복잡한 타입 힌트에 이름을 붙인 것(FeePolicy = Callable[[FeeInput], int]).

- `nonlocal` **nonlocal** [concept] 별칭=['nonlocal']
  - 첫 등장: 10-strategy.html · 원고 · …출 사이에 상태를 쌓음(캐시, 통계) 일반 클래스 가변 상태는 클로저의 nonlocal 보다 필드가 정직하다. 마지막으로 표준 라이브러리 자체를…
  - 용어집 정의(short): 안쪽 함수에서 바깥 함수의 지역 변수에 다시 대입할 수 있게 하는 선언.

- `dataclasses-asdict` **dataclasses.asdict** [gloss] 별칭=['asdict', 'dataclasses.asdict']
  - 첫 등장: 10-strategy.html · 코드 src/10_strategy/03_pythonic.py · … frozen이므로 해시 가능 → 캐시 키나 집합 원소가 된다, (3) dataclasses.asdict()로 설정을 다시 JSON으로 직렬화할…
  - 용어집 정의(short): dataclass 인스턴스를 필드 이름→값 dict로 바꾸는 함수.

- `concurrent-futures-threadpoolexecutor` **ThreadPoolExecutor** [concept] 별칭=['ThreadPoolExecutor']
  - 첫 등장: 10-strategy.html · 원고 · ….dumps(default=...) , re.sub(repl=함수) , ThreadPoolExecutor.map 에 넘기는 함수가 모두 "알고리…
  - 용어집 정의(short): 작업 함수를 스레드 풀에 나눠 실행하는 표준 라이브러리 클래스.

- `operator-attrgetter` **operator.attrgetter** [gloss] 별칭=['attrgetter', 'operator.attrgetter']
  - 첫 등장: 10-strategy.html · 원고 · …자리다. 우리가 할 일은 key 함수 두 개에 이름을 붙이는 것뿐이고, operator.attrgetter 가 그것마저 한 줄로 만들어 준다. …
  - 용어집 정의(short): 객체에서 지정한 속성을 꺼내는 함수를 만들어 주는 도구(정렬 key 등에 사용).

- `typing-namedtuple` **NamedTuple** [concept] 별칭=['NamedTuple']
  - 첫 등장: 10-strategy.html · 코드 src/10_strategy/solutions/ex3_sort_key.py · …or import attrgetter from typing import NamedTuple class StoreSales(NamedTuple):…
  - 용어집 정의(short): 필드 이름으로 접근할 수 있는 불변 튜플을 만드는 클래스.

- `customer-service` **CS 팀** [gloss] 별칭=['CS 팀']
  - 첫 등장: 10-strategy.html · 원고 · …대용 분기를 추가하면서 서울 쪽 할증 코드를 복사해 붙였고, 몇 주 뒤 CS 팀에서 "새벽 5시대 주문인데 서울은 심야 할증이 붙고 부산은 안 …
  - 용어집 정의(short): 고객 문의를 처리하는 고객 서비스 팀.
  - 감사 메모: ['약어 풀이 없음.']

- `a-b-test` **A/B 테스트** [gloss] 별칭=['A/B 실험', 'A/B 테스트', '실험군']
  - 첫 등장: 10-strategy.html · 코드 src/10_strategy/01_naive.py · … 구독 회원 무료 배달, 가게 부담 프로모션이 붙었고, 운영팀이 지역별 A/B 테스트를 요구하자 '실험군 B용 요금표'가 같은 메서드 안에 복제…
  - 용어집 정의(short): 사용자(또는 지역)를 무작위로 나눠 두 안을 동시에 적용하고 결과를 비교하는 실험.

- `tiered-pricing` **구간제 요금** [gloss] 별칭=['구간제', '구간제 요금']
  - 첫 등장: 10-strategy.html · 원고 · …다. 결정타는 운영팀의 요청이었다. "부산 해운대에서는 거리 비례 대신 구간제 요금표 를 실험해 보고 싶어요. 결과가 좋으면 다른 지역에도 넓히…
  - 용어집 정의(short): 거리 구간마다 정해진 요금을 매기는 방식.
  - 책 안의 기존 설명: ['10 · tiers는 (최대 km, 요금) 목록']

- `interpolation` **보간** [gloss] 별칭=['보간']
  - 첫 등장: 10-strategy.html · 원고 · … 정책 군을 나눠야 한다는 신호다. 리팩터링 문제 2. 이미지 리사이즈 보간 방식 사진 편집 서비스의 리사이즈 함수다(이해를 쉽게 하려고 이미지…
  - 용어집 정의(short): 알려진 값들 사이의 값을 추정해 채우는 계산(이미지 리사이즈에 쓰임).

- `nearest-neighbor-interpolation` **최근접 이웃 보간** [gloss] 별칭=['최근접 이웃', '최근접 이웃 보간']
  - 첫 등장: 10-strategy.html · 코드 src/10_strategy/solutions/ex2_resize_registry.py · …t) -> list[int]: """[Concrete Strategy] 최근접 이웃. 가장 빠르고, 계단 현상이 생긴다.""" # 목표 좌표 i…
  - 용어집 정의(short): 목표 위치에 가장 가까운 원본 픽셀 값을 그대로 쓰는 보간.
  - 책 안의 기존 설명: ['10 · 가장 가까운 픽셀을 고른다']

- `linear-interpolation` **선형 보간** [gloss] 별칭=['선형 보간']
  - 첫 등장: 10-strategy.html · 코드 src/10_strategy/solutions/ex2_resize_registry.py · …t) -> list[int]: """[Concrete Strategy] 선형 보간. 이웃 두 픽셀을 거리 비율로 섞는다.""" out = [] …
  - 용어집 정의(short): 이웃 두 값을 거리 비율로 섞는 보간.
  - 책 안의 기존 설명: ['10 · 이웃 두 픽셀을 거리 비율로 섞는다']

- `aliasing` **앨리어싱** [gloss] 별칭=['앨리어싱']
  - 첫 등장: 10-strategy.html · 코드 src/10_strategy/solutions/ex2_resize_registry.py · …t]: """[Concrete Strategy] 구간 평균. 축소할 때 앨리어싱이 적다.""" step = len(row) / size retu…
  - 용어집 정의(short): 표본을 너무 듬성하게 뽑아 원래 없던 무늬·톱니가 생기는 왜곡.

- `jaggies` **계단 현상** [gloss] 별칭=['계단 현상']
  - 첫 등장: 10-strategy.html · 코드 src/10_strategy/solutions/ex2_resize_registry.py · … """[Concrete Strategy] 최근접 이웃. 가장 빠르고, 계단 현상이 생긴다.""" # 목표 좌표 i를 원본 좌표로 되돌려 가장 …
  - 용어집 정의(short): 확대·축소한 이미지의 경계가 계단처럼 각지는 현상.

- `grayscale` **회색조** [gloss] 별칭=['회색조']
  - 첫 등장: 10-strategy.html · 원고 · … 방식 사진 편집 서비스의 리사이즈 함수다(이해를 쉽게 하려고 이미지를 회색조 픽셀 한 줄로 줄였다). 새 보간 방식이 추가될 때마다 이 함수를…
  - 용어집 정의(short): 색 없이 밝기 하나로만 픽셀을 나타내는 이미지 형식.

## 11-observer.html — 23개

- `push-model-pull-model` **푸시 모델·풀 모델** [concept] 별칭=['푸시 모델', '푸시 모델·풀 모델', '푸시(push)', '풀(pull)']
  - 첫 등장: 11-observer.html · 원고 · … 관리한다. (통지 메시지) Tick 무엇이 바뀌었는지 담는 불변 값. 푸시 모델의 운반체. 푸시와 풀. 주체가 바뀐 내용을 메시지에 담아 보내…
  - 용어집 정의(short): 옵저버 통지 방식. 푸시는 주체가 바뀐 내용을 메시지에 담아 보내고, 풀은 '바뀌었다'는 신호만 보낸 뒤 관찰자가 주체를 조회해 가져간다.
  - 책 안의 기존 설명: ['11 · 주체가 바뀐 내용을 메시지에 담아 보내면 푸시']
  - 감사 메모: ['15장 관련 패턴에서 반복자=풀, 옵저버=푸시로 다시 쓴다.']

- `iterate-over-a-copy` **복사본 순회** [concept] 별칭=['복사본 순회', '복사본을 순회']
  - 첫 등장: 11-observer.html · 원고 · ….py 이며 두 부분으로 나눠 본다. _notify() 의 두 주석 — 복사본 순회와 예외 격리 — 이 이 패턴을 장난감에서 실전 코드로 바꾸는…
  - 용어집 정의(short): 통지를 시작할 때의 구독자 목록을 복사해 그 복사본을 도는 것. 통지 도중 구독·해제가 일어나도 건너뛰기가 생기지 않는다.
  - 책 안의 기존 설명: ["11 · 지금 이 순간의' 목록을 떠서 돈다"]

- `exception-isolation` **예외 격리** [concept] 별칭=['실패 격리', '예외 격리']
  - 첫 등장: 11-observer.html · 원고 · … 부분으로 나눠 본다. _notify() 의 두 주석 — 복사본 순회와 예외 격리 — 이 이 패턴을 장난감에서 실전 코드로 바꾸는 부분이다. p…
  - 용어집 정의(short): 한 관찰자(구독자)가 던진 예외를 잡아 기록하고 다음으로 넘어가, 실패가 다른 관찰자에게 번지지 않게 하는 것.
  - 책 안의 기존 설명: ['11 · 관찰자 하나의 실패가 나머지 관찰자를 막지 않게']

- `idempotent` **멱등** [concept] 별칭=['멱등']
  - 첫 등장: 11-observer.html · 코드 src/11_observer/02_observer.py · …""구독 해제. 이미 해제된 관찰자에 대해 다시 불러도 조용히 넘어간다(멱등). 화면 닫기와 자동 정리가 겹쳐 두 번 해제되는 일이 실전에서 흔…
  - 용어집 정의(short): 같은 연산을 여러 번 수행해도 한 번 수행한 것과 결과가 같은 성질.
  - 책 안의 기존 설명: ['11 · 다시 불러도 조용히 넘어간다(멱등)']

- `pipeline` **파이프라인** [concept] 별칭=['파이프라인']
  - 첫 등장: 11-observer.html · 코드 src/11_observer/02_observer.py · …찰자끼리 숨은 결합이 생긴다). 순서가 중요하다면 그건 관찰자가 아니라 파이프라인이다. """ self._subscribers: dict[str…
  - 용어집 정의(short): 앞 단계의 결과가 다음 단계의 입력이 되도록 순서가 고정된 처리 흐름. 앞 단계가 실패하면 뒤가 멈춰야 한다.

- `update-cascade` **갱신 폭포** [concept] 별칭=['갱신 폭포']
  - 첫 등장: 11-observer.html · 원고 · …쇄되면(관찰자가 다른 주체의 상태를 바꾸고, 그 주체가 또 통지하고…) 갱신 폭포와 무한 루프가 생길 수 있다. 그리고 구독 해제 누락은 이 패…
  - 용어집 정의(short): 통지를 받은 관찰자가 다른 주체를 바꾸고, 그 주체가 또 통지하는 식으로 갱신이 연쇄적으로 번지는 현상.
  - 책 안의 기존 설명: ['11 · 관찰자가 다른 주체의 상태를 바꾸고, 그 주체가']

- `domain-event` **도메인 이벤트** [concept] 별칭=['도메인 이벤트']
  - 첫 등장: 11-observer.html · 코드 src/11_observer/solutions/ex2_signup_events.py · …zen=True) class UserSignedUp: """통지 메시지(도메인 이벤트). 과거형 이름: '일어난 사실'을 알릴 뿐, 무엇을 하라…
  - 용어집 정의(short): 도메인에서 이미 일어난 사실(예: UserSignedUp)을 과거형 이름으로 알리는 메시지. 무엇을 하라고 지시하지 않는다.
  - 책 안의 기존 설명: ["11 · 과거형 이름: '일어난 사실'을 알릴 뿐"]

- `transactional-outbox` **아웃박스 패턴** [concept] 별칭=['아웃박스 테이블', '아웃박스 패턴']
  - 첫 등장: 11-observer.html · 원고 · … 메일이 이미 나가면 안 되므로, 실제 시스템은 커밋 후 에 발행하거나 아웃박스 테이블을 쓴다. 판단 문제 3. 관찰자가 하나뿐일 때 CSV 업…
  - 용어집 정의(short): 보낼 메시지를 업무 데이터와 같은 트랜잭션으로 DB 테이블에 먼저 기록하고, 커밋 후 별도로 발행해 '롤백됐는데 메시지는 나간' 사고를 막는 기법.

- `weakref-weakmethod` **WeakMethod** [concept] 별칭=['WeakMethod']
  - 첫 등장: 11-observer.html · 코드 src/11_observer/03_pythonic.py · …(살아 있으면) 또는 None(죽었으면)을 돌려준다. # weakref.WeakMethod 객체가 바로 이 모양이라, 강한 참조도 같은 모양으로…
  - 용어집 정의(short): 바운드 메서드를 약하게 참조하는 weakref 도구. 메서드 객체가 아니라 그 주인 객체의 생존에 맞춰 살아 있다.
  - 책 안의 기존 설명: ['11 · 바운드 메서드 객체는 속성 접근 때마다 새로 만들어지는']

- `collections-defaultdict` **defaultdict** [concept] 별칭=['defaultdict']
  - 첫 등장: 11-observer.html · 코드 src/11_observer/03_pythonic.py · …주입받는다(로그? 재전파? 무시?).""" self._handlers: defaultdict[str, list[Ref]] = defaultdic…
  - 용어집 정의(short): 없는 키를 조회하면 지정한 함수(list 등)로 기본값을 만들어 넣어 주는 딕셔너리.

- `inspect-ismethod` **inspect.ismethod** [gloss] 별칭=['inspect', 'inspect.ismethod']
  - 첫 등장: 11-observer.html · 코드 src/11_observer/03_pythonic.py · …마자 수거되어 '조용히 아무 일도 안 하는' 버그가 된다. """ if inspect.ismethod(cb): return weakref.Wea…
  - 용어집 정의(short): 객체가 바운드 메서드인지 확인하는 표준 라이브러리 함수.

- `noqa` **noqa** [gloss] 별칭=['noqa']
  - 첫 등장: 11-observer.html · 코드 src/11_observer/02_observer.py · …_price(tick) except Exception as exc: # noqa: BLE001 — 의도적으로 넓게 잡는다(격리가 목적) prin…
  - 용어집 정의(short): 린터(flake8 등)에게 그 줄의 특정 경고(예: BLE001 너무 넓은 except)를 무시하라고 알리는 주석.

- `push-notification` **푸시 알림** [gloss] 별칭=['푸시 서버', '푸시 알림']
  - 첫 등장: 11-observer.html · 원고 · …제가 없었다. 두 달째, 기획팀의 요구가 몰려왔다. "목표가에 도달하면 푸시 알림을 보내 주세요." "보유 종목 평가액이 실시간으로 바뀌어야 해…
  - 용어집 정의(short): 앱이 실행 중이 아니어도 서버가 사용자 기기로 보내는 알림.

- `trade-execution` **체결** [gloss] 별칭=['체결']
  - 첫 등장: 11-observer.html · 원고 · …30' 처럼 이벤트 이름에 주제를 넣으면, 하나의 허브로 가격·거래정지·체결 등 여러 종류의 통지를 다룰 수 있다. 이것을 프로세스 밖으로 꺼내…
  - 용어집 정의(short): 매수·매도 주문이 서로 맞아 거래가 성립하는 것.

- `synchronous-notification` **동기 통지** [concept] 별칭=['동기 통지']
  - 첫 등장: 11-observer.html · 원고 · …Hub 가 예외 처리 함수를 생성자로 주입받는 이유다. 또한 이 구현은 동기 통지다. 느린 관찰자 하나가 모든 통지를 지연시키므로, 실시간 시세…
  - 용어집 정의(short): 통지자가 각 수신자의 처리가 끝날 때까지 기다리는 통지 방식.

- `simple-mail-transfer-protocol` **SMTP** [gloss] 별칭=['SMTP']
  - 첫 등장: 11-observer.html · 코드 src/11_observer/solutions/ex2_signup_events.py · …@down.example"): raise ConnectionError("SMTP 타임아웃") print(f" 환영 메일 → {e.email}")…
  - 용어집 정의(short): 이메일 전송 프로토콜.

- `schema` **스키마** [gloss] 별칭=['스키마']
  - 첫 등장: 11-observer.html · 원고 · …리지 않지만, 새 구독자가 필요로 하는 사실 이 메시지에 없으면 이벤트 스키마는 넓혀야 한다 — 3절에서 본 푸시 모델 메시지 설계의 비용이다.…
  - 용어집 정의(short): 데이터·메시지가 가져야 할 필드와 타입의 구조 정의.

- `backward-compatibility` **하위 호환** [gloss] 별칭=['하위 호환']
  - 첫 등장: 11-observer.html · 코드 src/11_observer/solutions/ex2_signup_events.py · … 기본값 None을 둔 덕분에 기존 구독자와 발행 코드는 깨지지 않는다(하위 호환). referrer_id: int | None = None L…
  - 용어집 정의(short): 새 버전이 기존 사용 코드를 깨지 않고 그대로 동작하게 하는 성질.

- `persistence` **영속성** [gloss] 별칭=['영속성']
  - 첫 등장: 11-observer.html · 원고 · …제(topic) 기반 발행/구독이 된다. 구조는 같고, 전달 보장·순서·영속성이 추가될 뿐이다. 이제 허브를 쓰는 주체 Quote 와, 아무것도…
  - 용어집 정의(short): 프로세스가 끝나도 데이터가 저장되어 남는 성질.

- `delivery-guarantee` **전달 보장** [concept] 별칭=['전달 보장']
  - 첫 등장: 11-observer.html · 원고 · …시지 브로커의 주제(topic) 기반 발행/구독이 된다. 구조는 같고, 전달 보장·순서·영속성이 추가될 뿐이다. 이제 허브를 쓰는 주체 Quot…
  - 용어집 정의(short): 메시지가 최소 한 번·최대 한 번·정확히 한 번 전달되는지에 대한 시스템의 약속.

- `message-broker` **메시지 브로커** [gloss] 별칭=['Kafka', 'Redis', '메시지 브로커']
  - 첫 등장: 11-observer.html · 원고 · …를 다룰 수 있다. 이것을 프로세스 밖으로 꺼내 네트워크 너머로 보내면 Redis Pub/Sub, Kafka 같은 메시지 브로커의 주제(topi…
  - 용어집 정의(short): 발행자와 소비자 사이에서 메시지를 받아 보관·전달하는 별도 서버(Kafka, Redis 등).

- `nondeterministic` **비결정적** [concept] 별칭=['비결정적']
  - 첫 등장: 11-observer.html · 원고 · …관 해제 누락에 대한 안전망 람다·클로저에 쓰면 즉시 소멸, 수거 시점 비결정적 6. 트레이드오프와 관련 패턴 얻는 것. 주체와 관찰자의 독립적…
  - 용어집 정의(short): 같은 입력이라도 실행할 때마다 시점·결과가 달라질 수 있는 성질.

- `socket` **소켓** [gloss] 별칭=['소켓']
  - 첫 등장: 11-observer.html · 원고 · …권'의 앱 개발자 하린은 첫 버전에서 화면 하나만 만들면 됐다. 거래소 소켓에서 삼성전자 시세가 들어오면 차트를 다시 그린다. 그래서 시세 수신…
  - 용어집 정의(short): 네트워크 연결의 양 끝점. 이를 통해 데이터를 주고받는다.

## 12-command.html — 11개

- `snapshot` **스냅샷** [concept] 별칭=['스냅샷']
  - 첫 등장: 12-command.html · 코드 src/12_command/02_command.py · …te Command] 상대 이동. undo 방식: 바뀌는 필드(좌표)의 스냅샷. 주의: 이름만 보면 역연산(−dx)이 자연스럽지만, Canvas…
  - 용어집 정의(short): 어떤 시점의 상태(또는 그 일부)를 복사해 저장해 둔 것. 커맨드의 undo에서 실행 직전 값을 기억해 두었다가 그대로 되돌리는 데 쓴다.
  - 책 안의 기존 설명: ['12 · execute() 때 이전 좌표를 기억한다(스냅샷)']
  - 감사 메모: ["12장 4절 표('스냅샷(snapshot)')가 역연산과 대비해 장단점을 정리한다. 15장 6절은 '스냅샷(이 장의 tuple 복사)'으로 다른 맥락에 쓴다."]

- `inverse-operation` **역연산** [concept] 별칭=['역연산']
  - 첫 등장: 12-command.html · 코드 src/12_command/01_naive.py · … rest s = self.shapes[shape_id] # ⚠ 문제: 역연산이 '0에서 자르기'를 모른다. 잘린 이동은 정확히 되돌려지지 않는…
  - 용어집 정의(short): 어떤 연산의 효과를 정확히 거꾸로 되돌리는 연산(예: +1 ↔ −1). 연산이 정보를 잃으면(자르기·삭제·반올림) 존재하지 않는다.
  - 책 안의 기존 설명: ['12 · 역연산(inverse) 온도 +1 ↔ −1']
  - 감사 메모: ["12장 01_naive.py 주석('역연산이 0에서 자르기를 모른다')이 4절 표보다 먼저 나온다."]

- `field-init-false` **init=False 필드** [concept] 별칭=['init=False', 'init=False 필드']
  - 첫 등장: 12-command.html · 원고 · …짜로 해 준다. 요청 매개변수( init=True )와 undo 정보( init=False )를 필드 수준에서 나눈 방법에 주목하라. …
  - 용어집 정의(short): 생성자 인자로 받지 않는 dataclass 필드. 12장에서는 execute() 때 채워지는 undo 정보를 담는다.
  - 책 안의 기존 설명: ['12 · execute() 때 채워지는 undo 정보']

- `assignment-expression-walrus` **대입 표현식** [concept] 별칭=[':=', '대입 표현식']
  - 첫 등장: 12-command.html · 코드 src/12_command/solutions/ex2_remote_undo.py · … 누름. 빈 슬롯은 조용히 무시(실제 리모컨처럼).""" if make := self.slots.get(button): cmd = make() …
  - 용어집 정의(short): 식 안에서 값을 이름에 대입하면서 그 값을 쓰는 := 연산자.

- `argparse` **argparse** [gloss] 별칭=['argparse']
  - 첫 등장: 12-command.html · 코드 src/12_command/solutions/ex3_cli_dispatch.py · …) -> None: """배포. 인자 파싱은 각 함수의 몫 — 실제로는 argparse 하위 파서를 쓴다.""" print(f" {args[0]…
  - 용어집 정의(short): 명령행 인자와 하위 명령(subparser)을 해석하는 표준 라이브러리.

- `undo-redo` **undo/redo** [concept] 별칭=['redo', 'undo', 'undo/redo', '실행 취소']
  - 첫 등장: 12-command.html · 원고 · …바꿨다. 단순하고 빨랐다. 베타 사용자들의 첫 피드백은 거의 같았다. "실행 취소가 없어요." 그리고 "화살표 키로 도형을 옮기고 싶어요", "…
  - 용어집 정의(short): 직전 작업을 되돌리기(undo)와 되돌린 작업을 다시 하기(redo).

- `macro-2` **매크로** [gloss] 별칭=['매크로 녹화', '"매크로"로 녹화']
  - 첫 등장: 12-command.html · 원고 · …리고 다음 분기 로드맵에는 더 큰 요구가 있었다. 사용자가 반복 작업을 "매크로"로 녹화해 다른 도형에 재생하는 기능, 그리고 실시간 협업 — …
  - 용어집 정의(short): 여러 편집 동작을 하나로 기록해 두었다가 한 번에 재생하는 기능.
  - 책 안의 기존 설명: ['12 · 반복 작업을 "매크로"로 녹화해 다른 도형에']

- `z-order` **z-순서** [gloss] 별칭=['z-순서']
  - 첫 등장: 12-command.html · 코드 src/12_command/02_command.py · …None) -> None: """도형 추가. index를 주면 그 위치(z-순서)에 끼워 넣는다 — 삭제 취소용.""" items = list(…
  - 용어집 정의(short): 화면에서 겹친 도형의 앞뒤(그리기) 순서.
  - 책 안의 기존 설명: ['12 · 순서(그리기 순서)도 의미가 있다']

- `operational-transformation-crdt` **OT·CRDT** [gloss] 별칭=['CRDT', 'OT', 'OT·CRDT']
  - 첫 등장: 12-command.html · 원고 · …점에 거부되는 모습이다. 실제 협업 도구는 여기에 동시 편집 충돌 해결(OT, CRDT)이 더해지지만, 그 출발점은 언제나 "편집 동작이 직렬화…
  - 용어집 정의(short): 여러 사용자의 동시 편집 충돌을 자동으로 맞추는 알고리즘 계열.
  - 감사 메모: ['약어 풀이 없음.']

- `undo-tree` **undo 트리** [gloss] 별칭=['undo tree', 'undo 트리']
  - 첫 등장: 12-command.html · 원고 · …린다. 분기를 보존하려면 이력은 스택이 아니라 트리가 된다(Emacs의 undo tree). 5. 파이썬다운 변형 10장에서 "파이썬에서 전략의…
  - 용어집 정의(short): 되돌린 뒤 새로 편집한 분기까지 보존하도록 이력을 트리로 저장하는 방식(Emacs).

- `deferred-execution` **지연 실행** [concept] 별칭=['지연 실행']
  - 첫 등장: 12-command.html · 원고 · … 버튼·단축키·메뉴·스크립트에서), 다단계 undo/redo, 매크로, 지연 실행과 큐잉, 로그 기반 재생·감사·협업. 새 동작은 새 명령 클래…
  - 용어집 정의(short): 요청을 만들어 두고 실제 실행은 나중으로 미루는 것.

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

## 14-template-method.html — 27개

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

## 99-summary.html — 7개

- `event-sourcing` **이벤트 소싱** [concept] 별칭=['이벤트 소싱']
  - 첫 등장: 99-summary.html · 원고 · …행자는 그대로다. GUI 프레임워크(버튼 클릭 이벤트 → 편집 명령), 이벤트 소싱(도메인 이벤트 → 후속 명령), 메시지 브로커의 소비자(메시…
  - 용어집 정의(short): 현재 상태 대신 상태를 바꾼 이벤트들의 기록을 저장하고, 그 기록을 재생해 상태를 얻는 설계 방식.

- `ceiling-division` **올림 나눗셈** [concept] 별칭=['올림 나눗셈']
  - 첫 등장: 99-summary.html · 코드 src/99_summary/solutions/ex2_parking.py · …둔다.""" fee = -(-minutes // 30) * 1000 # 올림 나눗셈: 31분은 2구간 return fee // 2 if car …
  - 용어집 정의(short): -(-a // b)처럼 써서 나눗셈 결과를 올림하는 정수 관용구.
  - 책 안의 기존 설명: ['99 · 올림 나눗셈: 31분은 2구간']

- `picking` **피킹** [gloss] 별칭=['피킹']
  - 첫 등장: 99-summary.html · 원고 · … 로봇 창고 2.1 상황 중견 물류 기업 한빛로지스는 경기도 물류센터에 피킹 로봇을 도입했다. 개발자 도윤이 석 달 전 만든 프로토타입은 단순했…
  - 용어집 정의(short): 물류 창고에서 주문 상품을 보관 위치에서 꺼내 모으는 작업.

- `warehouse-management-system` **WMS** [gloss] 별칭=['WMS']
  - 첫 등장: 99-summary.html · 원고 · …은 선반 아래에 칸막이 단계가 하나 더 있다. 도윤은 이 요구를 하나씩 WMS 클래스에 분기로 넣었다. 그러다 사고가 났다. 배터리가 떨어진 로…
  - 용어집 정의(short): 창고의 재고·입출고·작업을 관리하는 창고 관리 시스템.
  - 책 안의 기존 설명: ['99 · 로봇 창고 관리 시스템(WMS)']
  - 감사 메모: ["99장 2.1절 원고('WMS 클래스')가 코드 docstring보다 먼저."]

- `stock-keeping-unit` **SKU** [gloss] 별칭=['SKU', 'sku']
  - 첫 등장: 99-summary.html · 코드 src/99_summary/02_naive_wms.py · …annotations # 재고: 구역 → 랙 → 선반 → [(칸 코드, SKU, 수량, x, y)] — 깊이가 코드에 박혀 있다 INVENTOR…
  - 용어집 정의(short): 재고 관리 단위(상품 식별 코드).

- `rack` **랙** [gloss] 별칭=['랙']
  - 첫 등장: 99-summary.html · 원고 · …고, 다음 분기에는 모바일 알림도 붙인다고 한다. 재무팀은 재고를 구역·랙·선반·칸 단위로 집계해 달라고 했는데, 신축 동은 선반 아래에 칸막이…
  - 용어집 정의(short): 창고에서 상품을 쌓는 선반 구조물.

- `manhattan-distance` **맨해튼 거리** [gloss] 별칭=['맨해튼 거리']
  - 첫 등장: 99-summary.html · 코드 src/99_summary/03_wms.py · …list[Bin]: """[Concrete Strategy] 출발점에서 맨해튼 거리가 가까운 칸부터.""" return sorted(bins, …
  - 용어집 정의(short): 두 점의 x 차이와 y 차이의 절댓값 합.
