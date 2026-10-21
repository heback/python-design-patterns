"""파이썬다운 변형: 콜러블 구독자, 약한 참조 자동 해제, 이벤트 이름 디스패치, property 통지.

상황: 02_observer.py는 동작하지만 하린의 팀 동료들은 불만이 있다. "로그 한 줄 남기려고
PriceObserver를 상속한 클래스를 만들어야 하나요?", "화면 닫을 때 close()를 깜박하면
여전히 누수잖아요." 하린은 파이썬의 언어 기능으로 이 두 불만을 해결한다.

  - 구독자 = 아무 콜러블. 함수·람다·바운드 메서드 모두 OK (Observer ABC 제거)
  - 바운드 메서드는 weakref.WeakMethod로 보관 → 객체가 사라지면 구독도 자동 소멸
  - 이벤트 이름('price:005930', 'halt:005930') → 콜백 목록 defaultdict 디스패치
  - on()이 '구독 해제 함수'를 돌려준다 → 해제할 대상을 기억할 필요가 없다
  - Quote.price를 property로 만들어, 값 대입 자체가 통지를 일으키게 한다
"""
from __future__ import annotations

import gc
import inspect
import weakref
from collections import defaultdict
from typing import Any, Callable

Callback = Callable[..., None]
# 보관용 참조의 공통 모양: 호출하면 콜백(살아 있으면) 또는 None(죽었으면)을 돌려준다.
# weakref.WeakMethod 객체가 바로 이 모양이라, 강한 참조도 같은 모양으로 맞춰 둔다.
Ref = Callable[[], "Callback | None"]


class EventHub:
    """[Subject] 이벤트 이름별 구독/통지 허브. 관찰자 인터페이스 없이 콜러블만 받는다.

    02의 PriceFeed와 달리 '시세'라는 도메인을 모른다. 통지 메커니즘을 도메인에서
    떼어 낸 재사용 부품이고, Quote(아래)가 이것을 '가진다'(합성).
    """

    def __init__(self, on_error: Callable[[str, BaseException], None] | None = None) -> None:
        """이벤트 → 참조 목록. 예외 처리 정책을 바깥에서 주입받는다(로그? 재전파? 무시?)."""
        self._handlers: defaultdict[str, list[Ref]] = defaultdict(list)
        self._on_error = on_error or (lambda ev, e: print(f"    !! [{ev}] 구독자 실패 격리: {e}"))

    @staticmethod
    def _make_ref(cb: Callback) -> Ref:
        """콜백을 보관할 참조를 만든다. 여기가 이 파일에서 가장 미묘한 결정이다.

        바운드 메서드(chart.redraw)는 약하게: 화면 객체가 사라지면 구독도 사라지게.
          weakref.ref(chart.redraw)가 아니라 WeakMethod인 이유 — 바운드 메서드 객체는
          속성 접근 때마다 새로 만들어지는 임시 객체라 ref()로 잡으면 즉시 죽는다.
        일반 함수·람다는 강하게: 이들은 대개 구독 지점에서만 만들어지는 임시 객체라,
          약하게 잡으면 구독하자마자 수거되어 '조용히 아무 일도 안 하는' 버그가 된다.
        """
        if inspect.ismethod(cb):
            return weakref.WeakMethod(cb)
        return lambda: cb

    def on(self, event: str, cb: Callback) -> Callable[[], None]:
        """구독하고, 그 구독을 해제하는 함수를 돌려준다.

        해제 함수를 돌려주는 이유: 호출자가 '무엇을 어디에 구독했는지'를 기억할 필요
        없이 off()만 보관하면 된다. 람다로 구독한 경우엔 같은 람다를 다시 만들 수
        없으므로 이 방식이 사실상 유일한 해제 수단이다.
        """
        ref = self._make_ref(cb)
        self._handlers[event].append(ref)

        def off() -> None:
            """이 구독 하나만 제거한다. 두 번 불러도 안전(멱등)."""
            if ref in self._handlers[event]:
                self._handlers[event].remove(ref)

        return off

    def emit(self, event: str, **payload: Any) -> None:
        """통지. 복사본 순회 + 예외 격리 + 죽은 참조 정리를 한 번에 한다."""
        for ref in list(self._handlers[event]):        # 복사본: 통지 중 on/off에 안전
            cb = ref()
            if cb is None:
                continue                               # 주인이 수거된 바운드 메서드
            try:
                cb(**payload)
            except Exception as exc:  # noqa: BLE001 — 격리가 목적이므로 넓게
                self._on_error(event, exc)
        # 죽은 참조를 원본 목록에서 걷어 낸다. 순회가 끝난 뒤라 안전하다.
        self._handlers[event] = [r for r in self._handlers[event] if r() is not None]

    def count(self, event: str) -> int:
        """살아 있는 구독자 수(데모·테스트용)."""
        return sum(1 for r in self._handlers[event] if r() is not None)


class Quote:
    """[Concrete Subject] 종목 시세. price에 값을 대입하면 그 자체가 통지가 된다.

    property setter에서 통지하는 이유: 호출자가 'price를 바꾼 뒤 notify()를 부르는 것'을
    잊을 수 없게 된다. 상태 변경과 통지가 원자적으로 묶인다. 같은 값이면 통지하지
    않는다 — 거래소는 같은 가격을 반복해서 보내기도 하는데, 차트가 매번 다시 그려질
    이유가 없다.
    """

    def __init__(self, hub: EventHub, symbol: str) -> None:
        """허브를 주입받는다. 여러 Quote가 하나의 허브를 공유할 수 있다."""
        self.hub, self.symbol = hub, symbol
        self._price: int | None = None

    @property
    def price(self) -> int | None:
        """현재가(아직 수신 전이면 None)."""
        return self._price

    @price.setter
    def price(self, value: int) -> None:
        """값 변경 → 상태 먼저 갱신 → 통지. 변화가 없으면 아무것도 하지 않는다."""
        old, self._price = self._price, value
        if old != value:
            self.hub.emit(f"price:{self.symbol}", symbol=self.symbol, price=value, old=old)

    def halt(self, reason: str) -> None:
        """거래 정지. 가격과 별개의 이벤트라 이름만 다르게 통지한다."""
        self.hub.emit(f"halt:{self.symbol}", symbol=self.symbol, reason=reason)


class ChartWidget:
    """[Concrete Observer] 차트 화면. Observer를 상속하지 않는다 — 메서드 시그니처만 맞추면 된다."""

    def __init__(self, name: str) -> None:
        """화면 이름(로그용)."""
        self.name = name

    def redraw(self, symbol: str, price: int, old: int | None) -> None:
        """가격 이벤트 핸들러. payload의 키 이름이 곧 매개변수 이름이다."""
        arrow = "▲" if old is not None and price > old else "▼" if old is not None else "·"
        print(f"    [{self.name}] {symbol} {price:,}원 {arrow}")


if __name__ == "__main__":
    hub = EventHub()
    samsung = Quote(hub, "005930")

    print("[1] 함수·람다·바운드 메서드가 같은 자리에 구독된다")
    chart = ChartWidget("메인 차트")
    hub.on("price:005930", chart.redraw)
    hub.on("price:005930", lambda symbol, price, **_: print(f"    [로그] {symbol} {price:,}"))
    off_alert = hub.on("price:005930",
                       lambda price, **_: print("    [알림] 72,000원 돌파!") if price >= 72000 else None)
    samsung.price = 71500
    samsung.price = 71500   # 같은 값 — 통지 없음
    print(f"    (같은 값 재대입은 통지하지 않음, 구독자 {hub.count('price:005930')}명)")

    print("[2] 사용자가 알림을 끈다 — on()이 돌려준 해제 함수만 부르면 된다")
    off_alert()
    samsung.price = 72100

    print("[3] 차트 화면 객체가 사라진다 — close()를 부르지 않았는데도 구독이 자동 소멸")
    del chart
    gc.collect()            # CPython은 참조 카운트로 즉시 수거하지만, 다른 구현을 위해 명시
    samsung.price = 72300
    print(f"    (남은 구독자 {hub.count('price:005930')}명: 로그뿐)")

    print("[4] 함정: 람다를 약한 참조로 잡았다면? — 구독하자마자 죽는다")
    r = weakref.ref(lambda **_: None)
    print(f"    weakref.ref(lambda ...)() is None → {r() is None}")
    print("    그래서 _make_ref는 바운드 메서드만 약하게, 함수는 강하게 보관한다")

    print("[5] 다른 이벤트 이름은 다른 구독자 목록 — 거래 정지 핸들러가 실패해도 격리")

    def broken_halt_handler(**_: Any) -> None:
        """일부러 실패하는 핸들러. 뒤 핸들러가 계속 불리는지 확인용."""
        raise RuntimeError("UI 스레드 아님")

    hub.on("halt:005930", broken_halt_handler)
    hub.on("halt:005930", lambda symbol, reason: print(f"    [배너] {symbol} 거래정지: {reason}"))
    samsung.halt("변동성 완화장치 발동")
