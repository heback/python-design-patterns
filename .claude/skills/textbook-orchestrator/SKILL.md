---
name: textbook-orchestrator
description: 파이썬 디자인패턴 교재 제작 하네스의 오케스트레이터. 교재 전체 제작, 커리큘럼 설계, 장 집필, 코드 검증, HTML 빌드를 에이전트(curriculum-architect, pattern-author, code-verifier, html-publisher)로 조율한다. "교재 만들어줘", "디자인패턴 교재", "패턴 장 추가", "OO 패턴 장만 다시 써줘", "교재 수정/보완/업데이트/다시 실행/재빌드", "연습문제 보강", "이전 결과 기반으로 개선", "교재 검증/점검" 등 이 교재와 관련된 생성·후속 작업 요청 시 반드시 이 스킬을 사용할 것. 교재와 무관한 단순 파이썬 질문에는 사용하지 않는다.
---

# 교재 제작 오케스트레이터

## 실행 모드: 하이브리드 (서브 에이전트 + 파일 기반 전달)
이 환경에는 TeamCreate/TaskCreate가 없다. 각 에이전트는 `Agent` 도구로 호출하고(`model: "opus"`, `subagent_type: "general-purpose"`), 프롬프트 첫 줄에 "`.claude/agents/{name}.md`를 읽고 그 역할로 행동하라"를 넣는다. 산출물은 약속된 경로의 파일로 주고받는다. 수정 요청은 같은 에이전트에 `SendMessage`로 이어 보내 맥락을 유지한다.

| 에이전트 | 스킬 | 출력 |
|---|---|---|
| curriculum-architect | pattern-chapter-writing(장 목록) | `_workspace/01_architect_curriculum.md` |
| pattern-author ×N | pattern-chapter-writing, code-verification | `src/{nn}_{slug}/`, `chapters/{nn}-{slug}.html` |
| code-verifier | code-verification | `_workspace/03_verifier_{nn}.md` |
| html-publisher | html-textbook-publishing | `textbook/` |

## Phase 0: 컨텍스트 확인
1. `_workspace/`, `chapters/`, `src/` 존재 여부를 본다.
2. 분기:
   - 없음 → **초기 실행** (Phase 1부터).
   - 있음 + 특정 장/부분 수정 요청 → **부분 재실행**: 해당 장의 pattern-author(피드백 + 기존 파일 경로 전달) → code-verifier → html-publisher 빌드만.
   - 있음 + 디자인 수정 → html-publisher만.
   - 있음 + 범위/대상 변경 같은 새 입력 → **새 실행**: `_workspace/`를 `_workspace_{YYYYMMDD_HHMMSS}/`로 옮기고 Phase 1. `chapters/`·`src/`는 덮어쓰기 전에 사용자에게 확인한다.
   - "검증/점검"만 요청 → `verify_chapter.py all` + code-verifier.

## Phase 1: 커리큘럼 설계 (서브 에이전트 1)
curriculum-architect 호출. 사용자 요구(대상 수준, 범위, 연습문제 여부)를 그대로 전달. 완료 후 설계서를 읽어 장 수와 도메인 중복 여부만 빠르게 확인한다.

## Phase 2: 패턴 장 집필 (서브 에이전트, 병렬)
- 패턴 장(01~15)을 **분류별 묶음으로 병렬** 호출한다: 생성(01–04), 구조(05–09), 행위(10–12), 행위(13–15). 에이전트 하나가 2~5장을 순서대로 맡는다 — 한 장당 한 에이전트는 오버헤드가 크고, 한 에이전트가 너무 많은 장을 맡으면 뒷장 품질이 떨어진다.
- 각 프롬프트에 포함: 맡은 장 번호/슬러그, 설계서 경로와 해당 장 헤딩, "완료 전 verify_chapter.py 통과" 요구, 반환 형식.
- `run_in_background: true`로 띄우되 **동시 실행은 2개까지** 둔다. 4개를 한꺼번에 띄우면 사용량 한도에 반복해서 걸려 전원이 중단된다(2026-10-08 초기 실행에서 3회 발생). 하나가 끝나면 다음 묶음/검증을 채워 넣는다.
- 한도·절전 등으로 에이전트가 중단되면 새로 띄우지 말고 같은 에이전트에 `SendMessage`로 "디스크 상태를 확인하고 이어서"라고 보낸다(맥락 유지, 완료분 재작업 방지).

## Phase 3: 검증 (서브 에이전트, 묶음이 끝나는 대로)
- 묶음 하나가 끝나면 즉시 그 묶음의 장들에 code-verifier를 호출한다(점진적 QA — 전부 끝나길 기다리지 않는다).
- 검증자에게는 **장 하나를 끝낼 때마다 보고서를 즉시 파일로 쓰라**고 지시한다. 여러 장을 모아 마지막에 쓰면 중단 시 검토 결과가 사라진다.
- 검증자의 [권장] 중 **사실 오류**(틀린 수치·근거·인용, 코드와 다른 서술)는 [필수]처럼 수정시킨다. 학생은 본문과 주석을 그대로 믿는다.
- VERDICT: FAIL이면 보고서 경로를 해당 pattern-author에게 `SendMessage`로 보내 **1회** 수정시키고, code-verifier로 재검증한다.
- 재검증도 FAIL이면 그 장은 "검증 미통과"로 기록하고 진행한다. 최종 보고에 남은 필수 지적을 그대로 적는다.

## Phase 4: 서론·종합 장 (서브 에이전트 1)
모든 패턴 장이 검증된 뒤 pattern-author 하나에게 00-intro와 99-summary를 맡긴다. 종합 장의 비교표·조합 사례는 **실제 작성된 장들**(chapters/)을 읽고 쓰게 한다 — 설계서만 보고 쓰면 본문과 어긋난다.

## Phase 4.5: 용어 정의 감사 (책 전체)
장 단위 검증은 "앞 장에서 정의 없이 쓴 용어"를 놓친다. 서론·종합까지 끝난 뒤(또는 용어 관련 수정 요청 시):
1. 검증자 2명이 장 범위를 나눠(예: 00–07, 08–15+99) 기준선 밖 용어를 수집한다 → `_workspace/05_terms_candidates_{범위}.md` (용어, 표기들, 분류, 제안 정의, 이미 정의된 곳).
2. 오케스트레이터가 후보를 병합해 `chapters/terms.json`에 등록하고 `check_terms.py`를 돌려 용어별 **첫 등장 장**을 얻는다.
3. 첫 등장 장 기준으로 묶어 해당 장 저자에게 `<dfn>` + 정의 문장 추가를 맡긴다(동시 2개). 저자는 이후 장의 중복 정의를 지우고 필요하면 용어집 링크로 바꾼다.
4. `check_terms.py` 위반 0 → 바뀐 장 `verify_chapter.py` → 빌드.

## Phase 5: 빌드 (서브 에이전트 1)
html-publisher 호출 → `build_textbook.py` 실행, PROBLEM 해결(원고 문제는 오케스트레이터에 반환), SVG 다크 모드 확인.

## Phase 6: 최종 확인과 보고
1. 직접 실행: `verify_chapter.py all`, `check_terms.py`, `build_textbook.py` — 모두 종료 코드 0인지.
2. 사용자에게 보고: 장 목록, 검증 결과(미통과 장과 사유), 열어볼 경로 `textbook/index.html`.
3. 피드백 요청: "개선할 부분이 있나요? (내용 깊이, 예제 도메인, 디자인, 연습문제 난이도 등)" — 받은 피드백은 해당 스킬/에이전트에 반영하고 CLAUDE.md 변경 이력에 남긴다.

## 에러 처리
| 상황 | 대응 |
|---|---|
| 에이전트가 산출물 없이 종료 | 1회 재호출. 재실패 시 해당 장 누락으로 보고 |
| 검증 FAIL | 1회 수정 → 재검증 → 미통과 기록 후 진행 |
| 빌드 PROBLEM(참조 누락 등) | 원인 장의 author에게 수정 요청 후 재빌드 |
| 설계서와 다른 내용 | 삭제하지 않고 author의 변경 사유(원고 끝 HTML 주석)를 확인해 수용 여부 판단 |

## 테스트 시나리오
- **정상 흐름**: "디자인패턴 교재 만들어줘" → Phase 0 초기 실행 → 설계서 17장 → 4개 묶음 병렬 집필 → 묶음별 검증 PASS → 서론/종합 → 빌드 PROBLEM 0 → `verify_chapter.py all` 종료 코드 0.
- **부분 재실행**: "옵저버 장 예제를 주식 시세 말고 다른 걸로 바꿔줘" → Phase 0 부분 재실행 → 11장 author에 피드백 전달(기존 파일 읽고 수정) → 11장만 검증 → 재빌드. 다른 장 파일은 변경되지 않아야 한다.
- **에러 흐름**: 10장 검증에서 "Context에 if 분기 잔존"(필수) → author 수정 → 재검증 PASS. 재검증도 FAIL이면 최종 보고에 "10장 검증 미통과: …" 명시.
