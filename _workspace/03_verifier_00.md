VERDICT: PASS

(재검증, 2026-10-08. 대상: chapters/00-intro.html, src/00_intro/01_naive.py, 03_pythonic.py (02·ex2는 변경 없음, 실행만 재확인). Python 3.13.7, PYTHONDONTWRITEBYTECODE=1로 실행해 src/에 __pycache__ 없음 확인.)

## 기계 검증
```
=== 장 00 ===
  OK   원고 00-intro.html / 메타 주석(title) / 필수 섹션 / lead-in / 코드 참조 4개
  OK   00_intro/01_naive.py: docstring 모두 / 주석 비율 39% / __main__ / 실행 성공 / 출력 / 원고 참조
  OK   00_intro/02_refactored.py: (같은 항목 모두 OK, 주석 비율 32%)
  OK   00_intro/03_pythonic.py: (같은 항목 모두 OK, 주석 비율 37%)
  OK   00_intro/solutions/ex2_lost_item_two_ways.py: (같은 항목 모두 OK, 주석 비율 36%)
  --> PASS (ok 33, warn 0, fail 0)
총 1장, 실패 0장
```

## data-run 출력 ↔ 원고
- 01 [1] 표, [2] 변경 이유 6가지 → 원고 34행과 일치.
- 02 [1] 01과 동일 / [2] 3500→3000 / [3] 감면→상한 1750, 상한→감면 1500 → 원고 43행과 일치.
- 03 [1] 1250/1750/2500, 규칙 종류 ['function','ExamWaiver'] / ['function','function'] / ['ExamWaiver'] / [2] EXAM repr·describe, `cap(3000) → <function cap.<locals>.apply>` / [3] 100원 → 원고 77-78행과 일치. 01 주석의 "3,000원 상한"은 02 [3]에서 순서 효과(1750 vs 1500)가 실제로 나타나므로 정확하다.

## 이전 지적 해소 여부
1. [필수] Norvig 인용 범위 (66행) — **범위는 해소.** Lisp·Dylan 한정, "16개의 일부 용법", 23개 중 16개, 파이썬에 그대로 옮길 수 없다는 단서(멀티메서드·매크로), 일반 요지만 성립한다는 표현이 모두 원 주장 범위 안이다. 언급된 기능(일급 함수·타입, 멀티메서드, 매크로)도 Norvig 슬라이드의 분류(first-class types/functions, macros, method combination, multimethods, modules)와 맞다. **그러나 같은 문장에 새 사실 오류가 있다(아래 [필수] N1).**
2. [권장] C++/Smalltalk "그 언어들에 없는 기능" (66행) — **미해소.** 문장이 그대로다.
3. [권장] Forces (54행) — **해소.** 표 항목이 "동기(Motivation)와 적용 가능성(Applicability)"로 바뀌었고, 59행에서 forces가 GoF 항목이 아니라 Alexander에서 비롯된 개념이라고 구분했다. 59행의 GoF 항목 12개(의도, 별칭, 동기, 적용 가능성, 구조, 참여자, 협력, 결과, 구현, 예제 코드, 알려진 사용, 관련 패턴)는 GoF 1.3절의 Intent~Related Patterns와 순서까지 일치한다. (참고: GoF 1.3절은 맨 앞에 "Pattern Name and Classification"도 두지만, 이것은 본문 항목이라기보다 머리글이므로 생략해도 오류는 아니다.)
4. [권장] 클로저 과장 — **대부분 해소.** 원고 78행("__closure__로 억지로 꺼낼 수는 있다 … 명확한 공개 인터페이스로 드러내지 못한다"), 03:122-123은 고쳐졌다. **03_pythonic.py:65의 docstring은 여전히 "클로저는 이런 것을 외부에 드러내지 못한다"이다.** 아래 R2를 보라.
5. [권장] 03 Loan docstring (21행) — **해소.** "01·02에서 branch를 뺐다 …"로 사실과 맞다.
6. [권장] 01 상한 금액 (48-49행) — **해소.** "최대 3,000원 상한"으로 원고 19행, 02와 일치한다.
7. [권장] 전략↔상태 (154행) — **해소.** 13장의 컨텍스트 전이표 변형을 명시했다.
8. [권장] 반복자+컴포지트 (156행) — **해소.** 행 제목을 "+"로 바꾸고 "대안이 아니라 협력 관계"로 적었다. 145행도 "비교하거나 함께 쓰므로"로 맞췄다.
9. [권장] 12장 도메인 (138행) — **해소.** "웹 다이어그램 도구"가 12장 #context와 맞다.
10. [권장] 99장 전방 참조 (105행) — **해소.** chapters/99-summary.html이 있다. "로봇 물류 창고" ↔ 99장 2절 "사례 연구: 로봇 창고", "판단을 표 하나로 정리" ↔ 99장 5절 "파이썬이 흡수한 패턴들"의 흡수 정도 표(15개 패턴)가 실제로 대응한다. 링크 `99-summary.html`도 유효하다.

## 의미 검증 지적 (현재)
- [필수] N1 chapters/00-intro.html:66 — 발표 제목이 틀렸다. Norvig의 1996년 Object World 발표 제목은 **"Design Patterns in Dynamic Programming"**이다(norvig.com/design-patterns/). "Design Patterns in Dynamic Languages"가 아니다. 학생이 이 제목으로 원문을 찾으면 찾을 수 없고, 교재가 잘못된 서지 정보를 가르치게 된다. → `"Design Patterns in Dynamic Programming"`으로 고친다. 같은 문장의 "보였다"는 슬라이드 발표의 주장이므로 "주장했다"가 더 정확하다(권장).
- [권장] R1 chapters/00-intro.html:66 — (이전 지적 2가 미해소) "패턴의 상당수는 그 언어들(C++와 Smalltalk)에 없는 기능을 메우기 위한 것"이라고 한다. 그런데 Smalltalk는 일급 블록과 일급 클래스를 갖춘 동적 언어이고, Norvig의 비교 대상도 C++다. → "패턴의 상당수는 주로 C++ 같은 정적 언어에 없는 기능을 메우기 위한 것이었다"로 바꾼다.
- [권장] R2 src/00_intro/03_pythonic.py:65 — "클로저는 이런 것을 외부에 드러내지 못한다"는 원고 78행, 같은 파일 122행과 표현 수위가 어긋난다. → "클로저는 이런 것을 공개 인터페이스(repr·비교·직렬화)로 드러내지 못한다"로 바꾼다.
- [권장] R3 chapters/00-intro.html:66 — 수정 과정에서 같은 말이 두 번 들어갔다. "…이 교재가 장마다 확인하는 것이 바로 그 범위다. 이 교재는 장마다 '파이썬다운 변형' 절에서 …를 판단하게 한다." → 앞 문장의 "이 교재가 장마다 확인하는 것이 바로 그 범위다"를 지우고 "…성립한다. 그래서 이 교재는 장마다 …"로 잇는다.

## 새로 읽은 부분에서 확인한 것 (문제 없음)
- 60행의 "상태 객체 스스로 결정하는가"는 154행 보충과 함께 읽으면 일관된다.
- 82행의 표 "설정을 드러내야 할 때(10)"는 99장 표의 전략 행("로그·비교·직렬화가 필요하면 frozen dataclass + __call__")과 일치한다.
- 01_naive.py:51 주석("하늘 지점은 시험 기간 면제를 하지 않는다")은 원고 19행, 출력(하늘 university=500)과 일치한다.

## 오케스트레이터 후속 조치 (2026-10-08)
- [필수] Norvig 발표 제목을 "Design Patterns in Dynamic Programming"(1996, Object World)으로 정정, "보였다"→"주장했다". 남은 [필수] 없음 → PASS.
