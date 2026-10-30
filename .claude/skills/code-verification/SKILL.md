---
name: code-verification
description: 디자인패턴 교재의 장 원고와 예제 코드를 검증하는 체크리스트와 자동 검증 스크립트(verify_chapter.py). 장 검증, 코드 실행 확인, 주석 기준 점검, 패턴 구현 정확성 리뷰, 교재 QA/점검/감사 요청 시 반드시 사용할 것. 집필자의 완료 전 자체 점검에도 사용.
---

# 교재 코드·원고 검증

검증은 두 층이다. 스크립트가 잡는 것은 "형식"이고, 학생에게 해로운 오류는 대개 "의미"에서 나온다. 둘 다 한다.

## 1. 기계 검증 (스크립트)

```bash
python3 .claude/skills/code-verification/scripts/verify_chapter.py 03      # 한 장
python3 .claude/skills/code-verification/scripts/verify_chapter.py all     # 전체
```

확인 항목: .py 실행 성공(20초 제한) · 모듈/클래스/함수 docstring · 주석 비율 ≥30% · 원고 메타 블록 · 필수 섹션과 순서 · `#context`에 코드 없음 & 첫 코드보다 앞 · 모든 본문 코드 앞 `lead-in` · `data-src`/`data-lines` 참조 무결성 · SVG 다이어그램 존재 · 연습문제 ≥3 & 해설 존재. WARN은 실패가 아니지만 보고서에 남긴다.

용어 순서(책 전체):
```bash
python3 .claude/skills/code-verification/scripts/check_terms.py          # 등록 용어가 첫 등장 자리에서 <dfn>으로 정의되었는가
python3 .claude/skills/code-verification/scripts/check_terms.py --first  # 용어별 첫 등장 위치
python3 .claude/skills/code-verification/scripts/check_terms.py --scan 훅 hook   # 미등록 문자열의 첫 등장
```
스크립트는 등록된 용어만 본다. **등록되지 않은 새 용어를 찾는 것은 사람(검증자)의 몫**이다 — 아래 체크리스트의 용어 항목.

## 2. 의미 검증 체크리스트

장마다 원고와 .py를 **나란히** 열고 확인한다. 한쪽만 읽으면 불일치를 못 찾는다.

**패턴 정확성**
- [ ] 패턴 적용 코드가 GoF 의도(intent)를 실제로 구현하는가? 이름만 패턴인 코드가 가장 흔한 결함이다.
  - Strategy/State: Context에 타입 분기(if/elif/match)가 남아 있지 않은가. State는 상태 전이가 상태 객체 쪽에 있는가(Strategy와의 차이).
  - Decorator: 감싼 객체와 **같은 인터페이스**인가, 중첩 가능한가. Proxy와 구분되는 설명이 있는가.
  - Factory Method: 생성 결정을 **서브클래스**에 위임하는가(단순 팩토리 함수와 구분). Abstract Factory: 제품 **군**의 일관성이 드러나는가.
  - Observer: 구독 해제, 통지 중 구독 변경 같은 실제 쟁점이 다뤄지는가.
  - Composite: Leaf와 Composite가 클라이언트 입장에서 동일하게 다뤄지는가.
  - Singleton: 파이썬에서의 대안(모듈, 의존성 주입)과 테스트 곤란성이 비판적으로 다뤄지는가.
- [ ] 순진한 코드(01_naive.py)의 `# ⚠ 문제:` 주석이 가리키는 문제가 데모 출력이나 코드 구조로 **실제로** 드러나는가.

**원고 ↔ 코드 정합성**
- [ ] 원고가 언급한 클래스·메서드·변수 이름이 코드에 그대로 존재하는가.
- [ ] 원고의 출력 설명("출력 [2]…")이 `src/` 파일을 실제로 실행한 출력과 일치하는가(스크립트로 실행해 비교).
- [ ] `data-lines` 범위가 원고가 설명하는 부분을 정확히 잘라내는가(코드 수정 후 범위가 밀리는 일이 잦다).
- [ ] SVG 다이어그램의 클래스 이름·관계(상속/합성/의존)가 코드와 일치하는가.

**주석 품질**
- [ ] 주석이 사실과 맞는가. 틀린 주석은 가장 심각한 결함으로 분류한다(학생은 주석을 믿는다).
- [ ] "왜"를 설명하는가, 아니면 코드를 한국어로 반복하는가. 반복형 주석이 대부분이면 `권장` 지적.
- [ ] 클래스 docstring에 패턴 역할 태그(`[Context]`, `[Concrete Product]` 등)가 있는가.

**용어**
- [ ] 이 장에서 기준선(pattern-chapter-writing "용어 정의 규칙") 밖의 용어가 정의 없이 쓰이지 않는가. 이전 장에서 이미 정의된 용어인지는 `chapters/terms.json`과 `check_terms.py --scan`으로 확인한다.
- [ ] `<dfn>` 옆의 정의 문장이 실제로 뜻을 밝히는가(영문 병기만 있는 것은 정의가 아니다). 정의가 사실과 맞는가.

**교육적 품질**
- [ ] 맥락 서사가 구체적인가(인물/제품/변경 요구). 추상적 "어떤 시스템에서…"는 `권장` 지적.
- [ ] `#tradeoffs`에 "쓰지 말아야 할 때"가 있는가.
- [ ] 연습문제 해설이 문제 요구를 실제로 충족하는가, 오답 분석이 있는가.
- [ ] 다른 장과 시나리오 도메인이 겹치지 않는가.

## 3. 보고서 형식

`_workspace/03_verifier_{nn}.md`:
```
VERDICT: PASS | FAIL

## 기계 검증
(스크립트 출력 그대로)

## 의미 검증
- [필수] src/10_strategy/02_strategy.py:42 — Checkout.total()에 `if policy == "vip"` 분기가 남아 있음 → 분기를 제거하고 policy.apply() 위임으로.
- [권장] chapters/10-strategy.html #context — 도메인이 추상적. 구체 인물·요구 변경 추가.
```
`필수`: 학생이 틀린 것을 배우게 되는 결함, 스크립트 FAIL. `권장`: 품질 개선. 필수가 하나라도 있으면 FAIL.
