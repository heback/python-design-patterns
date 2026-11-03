"""11 옵저버 — 패턴 코드: 수신기는 구독자 목록에 알리기만 한다.

상황: 하린은 PriceFeed가 차트·알림·로그를 모르게 바꿨다. 반응하는 쪽이 스스로
구독하고 스스로 해제한다. PriceFeed는 PriceObserver 목록에 Tick을 보내기만 하고,
한 구독자의 예외는 잡아서 기록한 뒤 다음 구독자로 넘어간다.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass(frozen=True)
class Tick:
    """통지 메시지. 무엇이 바뀌었는지 담아 보낸다. frozen이라 구독자가 고칠 수 없다."""
    symbol: str
    price: int

class PriceObserver(ABC):
    """[Observer] 통지를 받는 약속. 수신기는 이 타입만 안다."""
    @abstractmethod
    def on_price(self, tick: Tick) -> None:
        """새 시세를 받는다."""

class PriceFeed:
    """[Subject] 구독자 목록을 관리하고 가격이 바뀌면 알린다."""
    def __init__(self) -> None:
        """차트·알림 같은 구체 클래스를 하나도 import하지 않는다."""
        self._observers: list[PriceObserver] = []

    def subscribe(self, obs: PriceObserver) -> None:
        """구독. 무엇이 반응할지는 바깥이 정한다."""
        self._observers.append(obs)

    def unsubscribe(self, obs: PriceObserver) -> None:
        """해제. 이미 빠졌어도 조용히 넘어가 두 번 불러도 안전하다."""
        if obs in self._observers:
            self._observers.remove(obs)

    def push_price(self, symbol: str, price: int) -> None:
        """새 가격을 Tick에 담아 보낸다. 구독자가 수신기에 되물을 필요가 없다."""
        self._notify(Tick(symbol, price))

    def _notify(self, tick: Tick) -> None:
        """두 가지 안전장치가 이 패턴을 실전 코드로 만든다."""
        # 복사본 순회: 도중에 누가 해제해도 이번 통지에서 건너뛰어지는 구독자가 없다.
        for obs in list(self._observers):
            try:
                obs.on_price(tick)
            # 예외 격리: 한 구독자의 실패가 다른 구독자를 막지 않는다
            except Exception as e:  # noqa: BLE001 — 넓은 except는 일부러다
                print(f"    !! {type(obs).__name__} 실패: {e} (기록하고 계속)")

class ChartView(PriceObserver):
    """[Concrete Observer] 열려 있는 동안만 구독한다. 수명은 화면이 스스로 관리한다."""
    def __init__(self, feed: PriceFeed) -> None:
        """화면을 열면 스스로 구독한다."""
        self.feed = feed
        feed.subscribe(self)

    def close(self) -> None:
        """화면을 닫으면 해제. 수신기는 화면이 닫혔는지 몰라도 된다."""
        self.feed.unsubscribe(self)

    def on_price(self, tick: Tick) -> None:
        """다시 그린다."""
        print(f"    차트 {tick.symbol} {tick.price:,}원")

class TargetPriceAlert(PriceObserver):
    """[Concrete Observer] 목표가에 닿으면 한 번 울리고 통지 도중 스스로 해제한다."""
    def __init__(self, feed: PriceFeed, target: int) -> None:
        """server_down은 알림 서버 장애를 흉내 내는 스위치다."""
        self.feed, self.target, self.server_down = feed, target, False

    def on_price(self, tick: Tick) -> None:
        """목표가 확인."""
        if tick.price < self.target:
            return
        if self.server_down:
            raise ConnectionError("알림 서버 응답 없음")
        print(f"    알림 {tick.price:,}원 도달 (구독 해제)")
        self.feed.unsubscribe(self)   # 통지 도중 해제해도 안전하다: _notify가 복사본을 돈다

class TradeLogger(PriceObserver):
    """[Concrete Observer] 모든 시세를 기록한다."""
    def on_price(self, tick: Tick) -> None:
        """기록."""
        print(f"    로그 {tick.symbol} {tick.price:,}원")

if __name__ == "__main__":
    feed = PriceFeed()
    chart, alert = ChartView(feed), TargetPriceAlert(feed, 72000)
    feed.subscribe(alert)
    feed.subscribe(TradeLogger())
    print("[1] 알림 서버 장애 — 알림만 실패하고 로그는 남는다")
    alert.server_down = True
    feed.push_price("삼성전자", 72000)
    print("[2] 차트를 닫았다 — 더는 다시 그리지 않는다")
    chart.close()
    feed.push_price("삼성전자", 71500)
    print("[3] 서버 복구 — 알림이 통지 도중 스스로 해제해도 바로 뒤의 로그는 받는다")
    alert.server_down = False
    feed.push_price("삼성전자", 72500)
