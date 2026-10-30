---
name: pattern-chapter-writing
description: 파이썬 디자인패턴 교재의 장(章) 원고와 예제 코드를 쓰는 방법 — 장 구조, 맥락 선행 규칙, 주석 작성 규칙, 고급 학습자용 톤, SVG 다이어그램, 연습문제·해설 형식, 장 목록/슬러그. 교재의 어떤 장이든 집필·수정·보완하거나, 예제 코드나 연습문제를 쓰거나 고칠 때 반드시 이 스킬을 사용할 것.
---

# 패턴 장 집필 가이드

이 교재의 독자는 **객체지향 원리를 이미 깊이 이해한 학생**이다. 클래스·상속·다형성·SOLID를 설명하지 않는다. 그 대신 "그 원리들이 반복되는 설계 문제에서 어떤 형태로 굳어졌는가"를 보여준다. 학생이 장을 덮을 때 남아야 하는 것은 UML 모양이 아니라 **"이런 냄새가 나면 이 패턴을 떠올린다"는 판단력**이다.

## 장 목록 (기본 범위)

| nn | slug | 패턴 | 분류 |
|----|------|------|------|
| 00 | intro | 서론: OOP 원리에서 패턴으로 | — |
| 01 | factory-method | 팩토리 메서드 | 생성 |
| 02 | abstract-factory | 추상 팩토리 | 생성 |
| 03 | builder | 빌더 | 생성 |
| 04 | singleton | 싱글턴 | 생성 |
| 05 | adapter | 어댑터 | 구조 |
| 06 | decorator | 데코레이터 | 구조 |
| 07 | composite | 컴포지트 | 구조 |
| 08 | facade | 퍼사드 | 구조 |
| 09 | proxy | 프록시 | 구조 |
| 10 | strategy | 전략 | 행위 |
| 11 | observer | 옵저버 | 행위 |
| 12 | command | 커맨드 | 행위 |
| 13 | state | 상태 | 행위 |
| 14 | template-method | 템플릿 메서드 | 행위 |
| 15 | iterator | 반복자 | 행위 |
| 99 | summary | 종합: 패턴 비교와 조합 | — |

경로 규칙: 원고 `chapters/{nn}-{slug}.html`, 코드 디렉터리 `src/{nn}_{slug_with_underscores}/` (예: `src/01_factory_method/`).

## 파일 구성

```
src/03_builder/
├── 01_naive.py          # 순진한 설계 — 문제를 "보여주는" 코드
├── 02_builder.py        # 패턴 적용 — 교과서적 구조
├── 03_pythonic.py       # 파이썬다운 변형
└── solutions/
    ├── ex1_*.py         # 연습문제 해설 코드 (코드 문제만)
    └── ...
```
번호 접두사로 원고 등장 순서를 맞춘다. 각 파일은 `python3 파일.py`로 단독 실행되고 표준 라이브러리만 쓴다. 파일끼리 import하지 않는다(학생이 파일 하나만 열어도 전체가 보이게).

## 원고 구조 (패턴 장, 01~15)

원고는 `<html>`/`<head>` 없는 **본문 조각**이다. 맨 위에 메타 주석을 둔다. 섹션 `id`는 빌드·검증 스크립트가 사용하므로 바꾸지 않는다.

```html
<!--meta
title: 빌더 (Builder)
subtitle: 복잡한 객체를 단계적으로, 읽히게 조립하기
part: 생성 패턴
-->
<section id="goals">      <h2>학습 목표</h2>              ...3개 </section>
<section id="context">    <h2>1. 상황</h2>                ...코드 없음 </section>
<section id="naive">      <h2>2. 순진한 설계와 그 한계</h2> ...설명 → 코드 → 문제점 분석 </section>
<section id="structure">  <h2>3. 패턴의 구조</h2>          ...SVG 다이어그램 + 참여자 역할 </section>
<section id="implementation"><h2>4. 패턴 적용</h2>        ...설명 → 코드 → 실행 결과 → 해설 </section>
<section id="pythonic">   <h2>5. 파이썬다운 변형</h2>      ...언어 기능이 패턴을 어떻게 바꾸/없애는가 </section>
<section id="tradeoffs">  <h2>6. 트레이드오프와 관련 패턴</h2> ...언제 쓰지 말아야 하는가 포함 </section>
<section id="exercises">  <h2>7. 연습문제</h2>            ...문제 + 접힌 해설 </section>
```

서론(00)과 종합(99)은 `goals`만 필수이고 나머지 섹션은 자유 구성이다(`<section id="...">`로 나누되 id는 영문).

### 맥락 선행 규칙 (가장 중요)
학생은 동기 없이 코드를 받으면 문법만 읽는다. 그래서:
1. `#context` 섹션에는 코드가 **없다**. 구체적인 인물·팀·제품·요구사항이 등장하는 이야기로 쓴다. "요구사항 → 첫 구현은 잘 돌아감 → 변경 요구가 들어옴 → 무엇이 아파지는가"의 흐름.
2. **모든** 코드 블록 바로 앞에는 `<p class="lead-in">` 문단을 둔다. 이 코드가 지금 상황의 어느 부분을 다루는지, 읽을 때 무엇에 주목해야 하는지 말한다.
3. 코드 블록 뒤에는 그 코드가 드러낸 것(문제점 혹은 해결)을 해설한다. 코드만 던지고 다음 절로 넘어가지 않는다.

### 코드 삽입 — 붙여넣지 말고 참조한다
```html
<p class="lead-in">이제 주문서 객체를 생성자 하나로 만드는 첫 구현을 보자. 매개변수 목록이 어떻게 자라는지에 주목하라.</p>
<pre data-src="03_builder/01_naive.py"></pre>
<pre data-src="03_builder/02_builder.py" data-lines="12-58"></pre>   <!-- 일부만 -->
```
빌드 시 `data-src`는 파일 내용(HTML 이스케이프 + 문법 강조)으로 치환된다. 실행 결과는 원고에 싣지 않는다. 독자가 코드 블록의 [▶ 실행]으로 직접 확인하므로, 본문이 출력을 설명할 때는 "실행하면 …"처럼 쓰고 데모의 `print` 라벨(`[1]`, `[2]`)로 가리킨다. 출력을 손으로 옮겨 적지 않는다(코드 수정 시 어긋난다). `data-lines`로 일부만 보일 때는 앞뒤 맥락이 끊기지 않게 lead-in에서 "전체 파일은 …"이라고 안내한다.

## 코드 주석 규칙

모든 코드에 자세한 주석을 단다. 그러나 "자세하다"는 **줄마다 동작을 반복한다는 뜻이 아니다.** 이 독자에게 `# 리스트에 추가한다`는 소음이다. 주석이 답해야 하는 질문:
- **왜 이 구조인가?** "상속 대신 합성을 쓰는 이유: 런타임에 교체해야 하므로"
- **패턴의 어느 역할인가?** `# [Concrete Strategy]`, `# [Context]` 같은 역할 태그를 클래스 docstring 첫 줄에 단다.
- **어떤 원칙이 여기서 실현되는가?** "OCP: 새 할인 정책은 이 파일을 수정하지 않고 클래스 추가로 끝난다"
- **순진한 코드라면 무엇이 문제인가?** 01_naive.py에서는 문제 지점에 `# ⚠ 문제:` 주석으로 표시한다.
- **파이썬 특유의 선택의 이유**: `ABC` vs `Protocol`, `__slots__`, `dataclass(frozen=True)`, `@property` 등.

형식 요건 (검증 스크립트가 확인):
- 모듈 docstring 필수. 첫 단락에 **상황 요약**(이 파일이 교재의 어떤 상황을 다루는지)을 쓴다 — 코드 파일만 열어도 맥락이 보이게.
- 모든 클래스·함수·메서드에 docstring.
- 주석+docstring 줄 비율 ≥ 30% (빈 줄 제외). 짧은 메서드라도 "왜"가 있으면 쓴다.
- `if __name__ == "__main__":` 데모는 단계마다 `print`로 무슨 일이 일어나는지 보여준다. 독자가 [▶ 실행]으로 보는 출력이 본문의 근거이므로 출력 자체가 읽히게 쓴다(예: `print("[1] 기본 옵션으로 주문 생성")`).
- 타입 힌트를 쓴다(학생 수준에 맞음). `from __future__ import annotations` 허용.

주석 예시:
```python
class DiscountPolicy(ABC):
    """[Strategy] 할인 계산 규칙의 공통 인터페이스.

    Checkout(Context)은 이 추상 타입에만 의존한다. 그래서 할인 규칙이
    늘어나도 Checkout은 수정되지 않는다(OCP). Protocol 대신 ABC를 쓴 이유는
    구현을 빠뜨린 정책 클래스를 '인스턴스화 시점'에 바로 잡아내기 위해서다.
    """

    @abstractmethod
    def apply(self, subtotal: int) -> int:
        """할인 후 금액을 돌려준다. 원 단위 정수로 다뤄 부동소수 오차를 피한다."""
```

## 톤과 깊이
- 존댓말 평서문이 아닌 **교재체(~다)**. 독자를 "여러분"으로 부르지 않는다.
- OOP 기초 용어는 설명 없이 쓴다. 대신 GoF 원전의 의도(intent)를 인용 수준으로 정확히 제시하고, 파이썬에서는 그 의도가 어떻게 달라지는지 비판적으로 다룬다(예: "파이썬에서 Strategy의 상당수는 그냥 함수다. 그렇다면 클래스는 언제 여전히 필요한가?").
- `#tradeoffs`에는 반드시 "이 패턴을 쓰지 말아야 할 때"를 포함한다. 과잉 적용은 이 수준 학생의 대표적 실수다.
- 용어는 한글 + 첫 등장 시 영문 병기: 구체 전략(Concrete Strategy).

## 용어 정의 규칙
학생이 모르는 용어를 뜻 없이 만나면, 그 문단의 논증 전체를 놓친다. 그래서 **책 전체에서 처음 등장하는 자리**에서 정의한다(장 단위가 아니라 00 → 01…15 → 99 읽기 순서 기준).

- **정의하지 않는 기준선**: OOP 기초(클래스·객체·상속·다형성·캡슐화·추상 클래스·인터페이스·합성·위임·결합도·응집도·SOLID 각 원칙·오버라이드)와 파이썬 기본 문법(함수·클래스 정의·리스트/딕셔너리·예외·import·타입 힌트 표기).
- **정의할 것**: 그 밖의 모든 용어 — 패턴·설계 용어(훅, 합성 루트, 간접층, 푸시/풀 모델, 재진입 …), 파이썬 중급 이상 기능(덕 타이핑, `Protocol`, 클로저, 제너레이터, 던더 메서드, 데코레이터 문법, `__init_subclass__`, 메타클래스, 디스크립터, `singledispatch` …), 도메인 전문어(BOM, PG사, AC/WA/TLE …), 약어.
- **정의 방식**: 처음 등장하는 단어를 `<dfn data-term="id">훅</dfn>`으로 감싸고, 같은 문장이나 바로 다음 문장에서 한두 문장으로 뜻을 밝힌다 — "무엇인가 + 지금 문맥에서 왜 중요한가". 뒤 장에서 깊이 다루면 "(14장에서 자세히)"로 잇는다. 괄호 속 영문 병기만으로는 정의가 아니다.
- 첫 등장이 **코드 주석**이면 그 코드 블록 앞 `lead-in`에서 정의한다(lead-in이 코드보다 먼저 읽힌다).
- 같은 단어가 장마다 다른 폭으로 쓰이면(예: 일반적인 '훅' vs GoF 템플릿 메서드의 '훅 연산') 첫 정의에서 일반 의미를 주고, 좁은 의미를 쓰는 장에서 차이를 명시한다.
- 이미 정의된 용어는 다시 정의하지 않는다. 필요하면 `<a href="glossary.html#gl-id">`로 용어집에 잇는다.
- **등록**: `chapters/terms.json`에 `{"id", "term", "en", "aliases", "short"}` 항목을 둔다. `aliases`에는 본문·코드에 쓰이는 모든 표기(한글, 영문, 식별자)를 넣는다 — 검사기는 이 표기들의 첫 등장을 찾는다. `short`는 용어집에 실리는 한 문장 정의다. 너무 흔한 단어(예: '상태')는 별칭으로 넣지 말고 구체적 표기('상태 객체')를 쓴다.
- 학습 목표(`#goals`)와 `data-preview` 속성을 단 블록은 예고라 첫 등장으로 치지 않는다. 그래도 그 안의 약어에는 괄호 풀이를 붙인다.

## 구조 다이어그램 (SVG)
`#structure`에 인라인 SVG 클래스 다이어그램을 넣는다. 색을 하드코딩하지 않고 아래 클래스만 쓴다(다크 모드 대응은 style.css가 한다).

```html
<figure class="diagram">
  <svg viewBox="0 0 640 260" role="img" aria-label="빌더 패턴 구조">
    <g class="uml-class" transform="translate(20,20)">
      <rect width="180" height="70"/>
      <text class="uml-name" x="90" y="22">Director</text>
      <line x1="0" y1="32" x2="180" y2="32"/>
      <text class="uml-member" x="10" y="52">+ construct()</text>
    </g>
    <path class="uml-assoc" d="M200 55 H300"/>          <!-- 연관 -->
    <path class="uml-inherit" d="..."/>                  <!-- 상속/구현 (빈 삼각형 마커) -->
    <path class="uml-dep" d="..."/>                      <!-- 의존 (점선) -->
    <text class="uml-note" x=".." y="..">메모</text>
  </svg>
  <figcaption>그림 3-1. 빌더 패턴의 참여자</figcaption>
</figure>
```
- 추상 클래스명은 `class="uml-name uml-abstract"`(이탤릭).
- 마커는 style.css가 아닌 SVG 내부 `<defs>`가 필요하므로, 빌드 스크립트가 `<svg>` 안에 공통 마커(`#arrow`, `#triangle`, `#diamond`)를 자동 주입한다. 경로에 `marker-end="url(#triangle)"` 식으로 참조만 한다.
- 다이어그램은 실제 코드의 클래스 이름과 일치시킨다(일반명 Context/Strategy 아님). 일반 역할명은 `uml-note`로 곁들인다.

## 연습문제 형식
장마다 3~4문제, 유형을 섞는다.
1. **개념/판단** — "다음 상황 중 이 패턴이 과잉인 것은? 이유는?"
2. **리팩터링** — 짧은 코드(원고 안 `<pre><code class="language-python">`에 직접 써도 됨, 10~25줄)를 패턴으로 바꾸기
3. **확장** — 본문 코드에 새 요구사항 추가
4. (선택) **비교** — 관련 패턴과의 차이를 코드로 보이기

```html
<div class="exercise" id="ex1">
  <h3><span class="ex-tag">판단</span> 문제 1. ...</h3>
  <p>...</p>
  <details class="solution">
    <summary>해설 보기</summary>
    <p>...</p>
    <pre data-src="03_builder/solutions/ex1_xxx.py"></pre>
  </details>
</div>
```
해설은 정답만 주지 않고 **왜 그 답이며, 흔한 오답은 왜 틀렸는지**를 쓴다. 원고 안에 직접 쓴 짧은 문제 코드도 주석 규칙을 따른다.

## 완료 전 점검
`python3 .claude/skills/code-verification/scripts/verify_chapter.py {nn}` 와 `python3 .claude/skills/code-verification/scripts/check_terms.py`(책 전체 용어 순서)가 통과해야 한다.
