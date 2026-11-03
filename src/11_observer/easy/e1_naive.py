"""11 옵저버 — 순진한 코드: 시세 수신기가 반응하는 쪽을 모두 직접 부른다.

상황: 증권 앱의 하린은 새 가격이 들어오면 차트를 다시 그리게 했다. 그 뒤 목표가
알림과 거래 로그가 붙을 때마다 PriceFeed.push_price()에 호출이 한 줄씩 늘었다.
알림 서버가 멈춘 날, 알림의 예외가 그 아래 로그까지 막아 버렸다.
"""
from __future__ import annotations


class ChartView:
    """차트 화면. 사용자가 닫을 수 있다."""

    def __init__(self) -> None:
        """처음에는 열려 있다."""
        self.closed = False

    def redraw(self, price: int) -> None:
        """다시 그린다. 닫힌 뒤에 불리면 헛일이다."""
        state = "(닫힌 화면!)" if self.closed else ""
        print(f"    차트 {price:,}원 {state}")


class TargetPriceAlert:
    """목표가 알림. 알림 서버가 멈추면 예외를 던진다."""

    def __init__(self, target: int) -> None:
        """목표가를 기억한다."""
        self.target = target
        self.server_down = False

    def check(self, price: int) -> None:
        """목표가에 닿으면 알림을 보낸다."""
        if price >= self.target:
            if self.server_down:
                raise ConnectionError("알림 서버 응답 없음")
            print(f"    알림 {price:,}원 도달")


class TradeLogger:
    """모든 시세를 기록한다. 하나라도 빠지면 안 된다."""

    def log(self, price: int) -> None:
        """기록."""
        print(f"    로그 {price:,}원")


class PriceFeed:
    """시세 수신기. 원래 일은 '가격이 바뀌었다'를 아는 데까지다."""

    def __init__(self) -> None:
        """⚠ 문제: 반응하는 쪽을 수신기가 직접 만든다. 기능이 늘면 여기를 고친다."""
        self.chart = ChartView()
        self.alert = TargetPriceAlert(72000)
        self.logger = TradeLogger()

    def push_price(self, price: int) -> None:
        """새 가격을 받아 할 일을 차례로 부른다."""
        # ⚠ 문제: 화면이 닫혔는지 수신기는 모른다. 닫힌 차트도 계속 그린다.
        self.chart.redraw(price)
        # ⚠ 문제: 여기서 예외가 나면 아래 로그는 실행되지 않는다.
        self.alert.check(price)
        self.logger.log(price)


if __name__ == "__main__":
    feed = PriceFeed()
    print("[1] 평소")
    feed.push_price(71000)
    print("[2] 사용자가 차트를 닫았다 — 그래도 다시 그린다")
    feed.chart.closed = True
    feed.push_price(71500)
    print("[3] 알림 서버 장애 — 알림 예외가 로그까지 막는다")
    feed.alert.server_down = True
    try:
        feed.push_price(72000)
    except ConnectionError as e:
        print(f"    !! {e} — 이 가격의 로그가 없다")
