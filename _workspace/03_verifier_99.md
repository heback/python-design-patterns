VERDICT: PASS

# 장 99 종합 재검증 보고서 (2차)

## 기계 검증

```
=== 장 99 ===
  OK   원고 99-summary.html
  OK   메타 주석(title) 있음
  OK   필수 섹션 모두 있음
  OK   모든 본문 코드 앞에 lead-in 문단
  OK   코드 참조 4개 확인
  OK   99_summary/01_lookalikes.py: 모듈 docstring 있음 / 모든 클래스·함수 docstring / 주석 비율 38% / __main__ 데모 / 실행 성공 / 데모 출력 / 원고에서 참조됨
  OK   99_summary/02_naive_wms.py: (동일 항목 모두 OK, 주석 비율 32%)
  OK   99_summary/03_wms.py: (동일 항목 모두 OK, 주석 비율 38%)
  OK   99_summary/solutions/ex2_parking.py: (동일 항목 모두 OK, 주석 비율 38%)
  --> PASS (ok 33, warn 0, fail 0)
총 1장, 실패 0장
```

- 링크: 원고의 `href`를 모두 `chapters/`의 파일과 `<section id>`에 대조함. 새로 생긴 `14-template-method.html#structure`, `#implementation`을 포함해 **누락 0건.**
- `src/` 아래 `__pycache__` 없음(모든 실행에 `PYTHONDONTWRITEBYTECODE=1`을 썼고, 실험은 scratchpad에서 한 뒤 삭제함).
- 그림 99-1 SVG: `fill=`/`stroke=`/`style=`/hex/rgb 하드코딩 **없음**. 사용한 클래스(`uml-class`, `uml-name`, `uml-note`, `uml-assoc`, `uml-dep`, `uml-label`, `uml-member`, `uml-abstract`, `uml-impl`, `highlight`)는 모두 `textbook/assets/style.css`에 정의되어 있음.

## 이전 지적 해소 확인

### 필수 (4건 모두 해소)

| # | 이전 지적 | 판정 | 확인 내용 |
|---|---|---|---|
| 1 | 5절 흡수 표 3건 모순 | **해소** | 커맨드는 "함수로 일부 대체"로 옮겨졌고 셀에 12장의 "절반만"이 인용됨. 빌더와 추상 팩토리는 "대체 수단이 대부분을 맡음"으로 옮겨짐. 추상 팩토리 셀에는 2장의 "두세 개 + composition root면 충분"과 번들의 한계가 그대로 들어감. "클래스 구조가 핵심"에는 상태와 컴포지트만 남음. rowspan 합계 1+2+6+4+2=15로 맞음. 아래 전수 대조 참고 |
| 2 | 239행의 5장 귀속 오류 | **해소** | 5장은 번역 우회 누수, SDK 이름 오타, 타입 검사기로 쓰고, 6·9장은 특수 메서드와 `isinstance`로 분리함. 05/06/09 #pythonic 본문과 일치 |
| 3 | 2.5 템플릿 메서드 행 근거 | **해소** | 근거를 "14장 3절(골격이 패턴의 전제), 6절(상속 결합의 비용)"으로 바꿈. 14장 3절의 GoF 의도 인용("알고리즘의 골격을 정의")과 일치. 158행도 "'쓰지 말아야 할 때' 기준과 7절 체크리스트를 … 적용"으로 약해짐 |
| 4 | TaskQueue isinstance / 3.1 주장 | **해소(안 a 채택)** | 아래 03_wms.py 항목 참고 |

### 권장 (9건 모두 해소)

1. 02 데모: R2 초기 배터리가 50이 됨. 출력은 `A1-1-01 피킹, 배터리 25%` → `충전 시작 (주문 처리 도중!)` → `B1-1-01 피킹, 배터리 0%` → `충전 시작` 순서다. "충전 시작 후 0%까지 피킹 계속"이 **실제로 출력됨.** 57행 lead-in 서술과 일치함.
2. BatteryGuard docstring: "설계 근거이며 데모 출력이 보여 주지 않는다"를 밝혔고, 발행 시점이 바뀌는 시나리오로 바꿔 씀. 해소됨. 다만 부수 문장 하나에 새 오류가 있다(아래 권장 1).
3. "갱신 폭포"를 "재진입"으로 바꿈. 해소.
4. "여섯 축에 일곱 패턴"을 03 docstring과 핵심 정리에 반영했고, 배터리 축은 조합으로, 퍼사드는 별도 요구로 분리함. 해소.
5. 퍼사드 행과 `WarehouseOps` docstring에 공유 흐름(order/run_all)과 한 줄 위임(cancel/stock)을 구분함. 해소.
6. 그림 99-1: `«create»`(→ 명령 상자)와 `submit(urgent)`(→ TaskQueue)를 나눔. PickOrder/ChargeRobot은 두 개의 `uml-name` 줄로 그리고 figcaption에서 설명함. 해소.
7. 데코레이터·프록시 행 근거를 "7절 체크리스트 1번"으로 바꿈. 해소.
8. 22행: 13장 3절의 두 화살표를 구분했고, 반환값 변형이라 전자가 없다고 밝힘. 해소.
9. `Group` docstring의 7장 기준 인용을 바로잡음. 해소.

## 재검토: 03_wms.py

- **isinstance**: `TaskQueue`에 없음. 파일에 남은 `isinstance`는 245행(docstring 문장)과 398행(`BatteryGuard`가 이벤트 dict의 `pct` 값 타입을 좁히는 용도) 둘뿐이고, 명령 타입 판별에 쓰이지 않음.
- **프로토콜 일관성**: `Command` Protocol은 `key`, `cancellable`, `label`, `execute(ctx)`를 정의함. `PickOrder`는 `key`=order_id(property), `cancellable` 필드 기본값 True, `label` property, `execute`를 갖춤. `ChargeRobot`은 `key`=`charge-{robot}`(property), `cancellable` 필드 기본값 False, `label`(사유 포함) property, `execute`를 갖춤. **두 명령 모두 네 멤버를 빠짐없이 구현함.** `TaskQueue`는 `cancel`에서 `c.key`/`c.cancellable`만, `labels`에서 `c.label`만, `run_next`에서 `execute`만 씀. Invoker docstring("구체 타입을 모른다 — key/cancellable/label만 본다")이 이제 사실임.
- **데모 [4] 출력**: `charge-R1 취소 시도: False / 대기열: ['충전 R1(운영자 요청: 점검 전 충전)']` → `[대시보드] R1 충전 완료 100%` → `실행: ['충전 R1(운영자 요청: 점검 전 충전)']`. 원고 155행의 "TaskQueue.cancel()은 구체 타입을 묻지 않고 key와 cancellable만 본다 / 충전 명령은 스스로 취소 불가 / 실행 이력에 사유가 남는다"와 **일치함.** 다만 "안전 조치"라는 이유와 데모의 사유가 어긋난다(아래 권장 2).
- **데모 [3]**: `실행 순서: ['주문 O-001(MUG×2)', '충전 R2(배터리 20% < 30%)', '주문 O-003(CUP×1)']`. 155행의 "주문 → 충전 → 주문"과 일치하고, 사유가 이력에 남는 것도 확인됨.
- **3.1 주장의 코드 대조**
  - 재진입 차단: 설계 근거로 명시함. `run_next`가 pop한 뒤 execute하고 urgent는 index 0에 넣으므로 "명령 사이에서만 충전"이 코드로 참임.
  - 같은 경로: 대기열(`submit`), 우선순위(`urgent`), 실행 이력(`run_all`의 label 목록)이 모두 참임. `reason` 필드가 label에 들어가므로 "왜 충전했는가가 이력에 남는다"도 참임. "호출자는 그 속성만 보고 판단한다"도 참임(358행).
  - 정책 분리: `PickOrder.execute`는 `robot.battery`를 발행만 하고, 임계값은 `BatteryGuard.threshold`만 앎. 참.
  - 순환 없음: `ChargeRobot`은 `robot.charged`만 발행하고 BatteryGuard는 `robot.battery`만 구독함. 참.

## 재검토: 5절 흡수 표 15행 전수 대조 (각 장 #pythonic/#tradeoffs 본문 추출 후 대조)

| 행 | 분류 | 장 결론 | 판정 |
|---|---|---|---|
| 반복자 | 언어의 일부 | 15장 5.1 "반복자 클래스가 사라진다". 클래스가 필요한 경우는 외부 조회 상태, seek/peek, 직렬화·복제 | 일치 |
| 전략 | 대부분 함수로 | 10장 "전략의 상당수는 그냥 함수". 표의 frozen dataclass, ABC/Protocol 행 | 일치 |
| 옵저버 | 대부분 함수로 | 11장 5절 콜러블 구독, WeakMethod는 "안전망". ABC는 여러 콜백을 묶을 때 | 일치 |
| 싱글턴 | 대체 수단이 대부분 | 4장 5.1·5.2 모듈 객체, composition root. 예외로 든 `None` 값 싱글턴과 `getLogger` 레지스트리는 04 본문에 있음 | 일치 |
| 퍼사드 | 대체 수단이 대부분 | 8장 5절 모듈/`__all__`/`__init__.py`/`@contextmanager`, "상태가 없는 퍼사드라면 함수가 가장 단순" | 일치 |
| 어댑터 | 대체 수단이 대부분 | 5장 5절 Protocol, partial·클로저. "메서드 둘 이상 + 상태 공유면 클래스", `__getattr__`의 구멍 | 일치 |
| 프록시 | 대체 수단이 대부분 | 9장 5절 cached_property(클래스를 고칠 수 있을 때), lru_cache, weakref.proxy. 범용 `__getattr__`은 특수 메서드와 isinstance에서 깨짐 | 일치 |
| 빌더 | 대체 수단이 대부분 | 3장 5절 "상당 부분이 언어 기능으로 흡수". 표 6행 중 4행이 "충분". 부족한 두 행(조건부·누적 조립 반복, 여러 표현)이 마지막 열과 같음 | 일치 |
| 추상 팩토리 | 대체 수단이 대부분 | 2장 5절 "두세 개 + composition root면 번들로 충분". 클래스가 필요한 경우는 공유 상태, 타입 일관성 강제. 번들이 섞일 수 있다는 [2]도 반영함 | 일치 |
| 커맨드 | 함수로 일부 | 12장 5절 "절반만 그렇다". 요구 표(함수 / 명령 객체 / dataclass+등록부) | 일치 |
| 데코레이터 | 함수로 일부 | 6장 5절 함수 래퍼도 의도 충족. 둘 이상의 연산·상태 공유(Batching)는 클래스. `@`는 다른 범주. 런타임 조립은 reduce | 일치 |
| 템플릿 메서드 | 함수로 일부 | 14장 5절 contextmanager가 "첫 번째 선택지", `__init_subclass__`. 6절 "변이 축 하나·골격 안정" | 일치 |
| 팩토리 메서드 | 함수로 일부 | 1장 5절 생성 함수 주입, 레지스트리. "다른 훅도 함께 바꿀 때 하위 클래스". from_config는 이름만 같음 | 일치 |
| 상태 | 클래스 핵심 | 13장 5.1 Enum+전이표는 "행동이 크게 다를수록 불리". 5.2 무상태 공유, `__class__` 교체는 "유지보수 불가" 취지 | 일치 |
| 컴포지트 | 클래스 핵심 | 7장 5절 walk/own_cost는 다형성으로 유지, 보고서형 연산은 singledispatch | 일치 |

**15/15 일치.** 표 아래 문단(5장은 경계 누수, 6·9장은 특수 메서드)과 singledispatch 문단도 07 본문과 일치함.

## 재검토: 그림 99-1 (클래스명·화살표)

- 상자 이름(`WarehouseOps`, `TaskQueue`, `PickOrder`/`ChargeRobot`, `EventHub`, `BatteryGuard`, `Group / Bin`+`walk(): Iterator[Bin]`, `nearest_first / zone_sweep`, `RobotDriver`, `AcmeAdapter`/`RoboKoAdapter`)가 모두 코드에 있음.
- 화살표는 모두 코드와 일치함.
  - WarehouseOps→TaskQueue: `self.queue.submit` 등
  - TaskQueue→명령: `_pending`, `execute`
  - EventHub→BatteryGuard 통지: `hub.on("robot.battery", BatteryGuard(queue))`
  - BatteryGuard «create»→명령, submit(urgent)→TaskQueue: 400행
  - 명령 emit→EventHub: 302·304·335행
  - 명령→전략 "경로": `ctx.route`
  - 명령→RobotDriver: `robot.driver.go_and_pick`/`recharge`
  - 어댑터 실현(삼각형)→RobotDriver(Protocol, abstract 표기)
  - WarehouseOps→Group/Bin "stock()": 456행
- `RobotDriver`의 `uml-abstract`와 실현 화살표 `uml-impl`이 Protocol 구현 관계와 맞음.

## 의미 검증 지적

### 필수

없음.

### 권장

1. **[권장] chapters/99-summary.html:156 및 src/99_summary/03_wms.py:381–382 — "관찰자가 그 자리에서 직접 충전해도 대시보드 출력은 같다(실행 이력에서 충전 항목과 사유만 빠진다)"는 사실이 아님.** scratchpad에서 docstring이 말하는 대안대로 `BatteryGuard`가 `robot.driver.recharge()`를 직접 부르게 바꿔 실행했다. 실행 순서 목록에서 충전 항목이 빠진 것에 더해, `[대시보드] R2 충전 완료 100%` 줄도 사라졌다(`robot.charged`는 `ChargeRobot.execute`만 발행하므로). 나머지 줄(`R2 배터리 20%`, `O-003 완료`, `R2 배터리 85%`)은 같았다.
   → 수정안: "직접 충전해도 충전이 일어나는 시점(두 주문 사이)과 이후 배터리 값은 같다(달라지는 것은 실행 이력의 충전 항목과 `robot.charged` 통지뿐이다)"로 바꾼다. docstring 382행의 "직접 충전해도 출력은 같다"도 같은 취지로 고친다.

2. **[권장] src/99_summary/03_wms.py:311–317, 495–497 및 원고 155·183행 — 취소 불가의 근거와 데모가 어긋남.** `ChargeRobot` docstring과 원고는 `cancellable=False`의 근거를 "배터리 부족 충전은 안전 조치"라고 한다. 그런데 [4]가 취소 불가를 보여 주는 명령의 사유는 `"운영자 요청: 점검 전 충전"`으로, 안전 조치가 아니다. 또 `cancellable`은 dataclass **인스턴스 필드**라서 생성하는 쪽이 `ChargeRobot(..., cancellable=True)`로 바꿀 수 있다. 엄밀히는 "명령 자신이 밝힌다"가 아니라 "생성 시 정해진다"이다.
   → 수정안(택1)
     - (a) [4]의 명령을 안전 사유로 만든다(예: `ChargeRobot("R1", "배터리 25% < 30%")`).
     - (b) 기본값을 "충전은 모두 취소 불가"로 일반화하고 docstring 근거를 "로봇 가용성에 관한 조치라 주문 취소 경로로 빼지 않는다"로 바꾼다.
     - (c) 정책이 타입 수준이라면 `cancellable: ClassVar[bool] = False`로 바꾸고 docstring에 "인스턴스마다 바꾸지 않는다"를 밝힌다(Protocol의 읽기 전용 property와도 호환됨).

3. **[권장] src/99_summary/03_wms.py:443–445, 497 — 매개변수 이름이 실제 사용과 다름.** `WarehouseOps.cancel(self, order_id: str)`의 매개변수는 `order_id`인데, 데모 [4]는 `ops.cancel('charge-R1')`처럼 명령 key를 넘긴다.
   → 수정안: 매개변수를 `key: str`로 바꾸고 docstring을 "명령 key로 취소한다(주문은 주문 번호가 key)"로 고친다.

4. **[권장] 그림 99-1 (원고 109·111행) — 화살표 교차와 중복 표기.** `submit(urgent)` 경로(M300 204 H260 V130 H170)의 수직선 x=260과 `emit` 경로(M170 212 H230 V146 H300)의 수평선 y=146이 (260,146)에서 교차한다. 또 라벨 `«create» ChargeRobot (BatteryGuard)`의 "(BatteryGuard)"는 화살표의 출발점과 겹치는 정보다.
   → 수정안: emit 경로를 x=200 근처로 옮기거나 EventHub 왼쪽 아래(y=150)로 들어가게 해 교차를 없앤다. 라벨은 `«create» ChargeRobot`으로 줄인다.

5. **[권장] chapters/99-summary.html 끝의 HTML 주석 — "최종 코드는 6개 패턴(…)을 쓴다"가 본문(일곱 패턴)과 다름.** 렌더링되지 않는 저자 메모라 학생에게 영향은 없다. 그래도 후속 집필자가 오해하지 않도록 "6개 축, 7개 패턴(컴포지트+반복자는 한 축)"으로 맞춘다.

## 연습문제

이전 판정이 그대로 유효함(코드 변경 없음). `ex2_parking.py`는 다시 실행해 PASS를 확인함.
