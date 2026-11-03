"""11 옵저버 — 파이썬다운 변형: 구독자는 함수면 되고, 해제는 약한 참조가 돕는다.

상황: 패턴 코드에서는 로그 한 줄을 남기는 데도 PriceObserver를 상속한 클래스가
필요했고, close()를 잊으면 닫힌 화면이 계속 붙잡혀 있었다. 하린은 도메인을 모르는
작은 통지 허브 EventHub를 만들어 두 불만을 푼다.
"""
from __future__ import annotations

import weakref
from typing import Callable


class EventHub:
    """[Subject] 이벤트 이름별로 콜러블 구독자를 보관하고 알린다."""

    def __init__(self) -> None:
        """이벤트 이름 -> 참조 목록."""
        self._subs: dict[str, list[Callable[[], Callable | None]]] = {}

    def on(self, event: str, fn: Callable) -> Callable[[], None]:
        """구독하고, 해제 함수를 돌려준다. 해제 방법을 구독한 쪽이 쥐게 된다."""
        # 바운드 메서드는 약하게 잡는다: 화면 객체가 사라지면 구독도 같이 사라진다.
        # 함수·람다는 강하게 잡는다: 약하게 잡으면 구독 직후 바로 사라지기 때문이다.
        ref = weakref.WeakMethod(fn) if hasattr(fn, "__self__") else (lambda: fn)
        # 처음 보는 이벤트 이름이면 빈 목록을 만들어 둔다.
        refs = self._subs.setdefault(event, [])
        refs.append(ref)

        def off() -> None:
            """해제. 이미 빠졌으면 조용히 넘어가 두 번 불러도 안전하다."""
            if ref in refs:
                refs.remove(ref)
        return off

    def emit(self, event: str, *args: object) -> None:
        """복사본을 돌며 알린다. 죽은 참조는 정리하고, 한 구독자의 예외는 격리한다."""
        refs = self._subs.get(event, [])
        # 복사본 순회: 통지 도중 off()가 불려도 건너뛰어지는 구독자가 없다.
        for ref in list(refs):
            fn = ref()                 # 약한 참조면 살아 있는지 확인, 강한 참조면 fn 그대로
            if fn is None:             # 주인 객체가 이미 수거되었다
                refs.remove(ref)
                continue
            try:
                fn(*args)
            except Exception as e:     # 기록하고 다음 구독자로
                print(f"    !! 구독자 실패: {e}")


class ChartWidget:
    """[Concrete Observer] 아무것도 상속하지 않는다. 메서드 모양만 맞으면 된다."""

    def redraw(self, price: int) -> None:
        """다시 그린다."""
        print(f"    차트 {price:,}원")


if __name__ == "__main__":
    hub = EventHub()
    chart = ChartWidget()
    hub.on("price", chart.redraw)
    hub.on("price", lambda p: print(f"    로그 {p:,}원"))

    def alert(p: int) -> None:
        """목표가 알림. 상태가 없는 반응이라 클래스 없이 함수 하나로 충분하다."""
        if p >= 72000:
            print(f"    알림 {p:,}원")
    off_alert = hub.on("price", alert)
    print("[1] 메서드·람다가 같은 이벤트를 구독")
    hub.emit("price", 72000)
    print("[2] 돌려받은 해제 함수로 알림만 끈다")
    off_alert()
    hub.emit("price", 72500)
    print("[3] 해제를 잊고 차트를 버렸다 — 약한 참조라 구독도 사라진다")
    del chart
    hub.emit("price", 73000)
