"""순진한 설계: 시세 수신기가 모든 하위 기능을 직접 호출한다.

상황: 개인 투자자용 증권 앱 '틱톡증권'의 앱 개발자 하린은 시세 수신기(PriceFeed)가
새 가격을 받으면 push_price() 안에서 차트를 직접 다시 그리게 만들었다. 이후 목표가 알림,
포트폴리오 평가액 재계산, 거래 로그가 붙으면서 push_price()는 '시세를 받은 뒤 해야 할
모든 일'의 목록이 되었다.

이 파일에서 확인할 고통:
  1) PriceFeed가 차트·알림·포트폴리오·로거를 모두 알고 직접 만든다(강한 결합, OCP 위반).
  2) 알림 하나가 예외를 던지면 그 뒤의 포트폴리오 갱신과 로그가 실행되지 않는다.
  3) 사용자가 차트 화면을 닫아도 PriceFeed가 참조를 쥐고 있어 계속 갱신된다(누수).
  4) 종목별로 알림을 켜고 끄려면 PriceFeed 안에 사용자 설정 분기가 또 들어온다(데모 없음, 원고 참조).
"""
from __future__ import annotations


class ChartView:
    """종목 차트 화면. 화면이 닫혀도 객체는 PriceFeed가 붙잡고 있다."""

    def __init__(self, symbol: str) -> None:
        """표시할 종목과 '닫힘' 여부를 가진다."""
        self.symbol = symbol
        self.closed = False
        self.redraws_after_close = 0   # 닫힌 뒤 헛되이 다시 그린 횟수 — 누수의 증거

    def redraw(self, price: int) -> None:
        """차트를 다시 그린다. 닫힌 뒤에도 호출되면 낭비(그리고 실제 앱에서는 크래시)다."""
        if self.closed:
            self.redraws_after_close += 1
        state = "닫힌 화면!" if self.closed else "표시 중"
        print(f"    [차트:{self.symbol}] {price:,}원으로 다시 그림 ({state})")


class TargetPriceAlert:
    """목표가 도달 푸시 알림."""

    def __init__(self, symbol: str, target: int) -> None:
        """감시할 종목과 목표가."""
        self.symbol, self.target = symbol, target

    def check(self, price: int) -> None:
        """목표가 이상이면 푸시. 푸시 서버 장애를 흉내 내려고 특정 조건에서 예외를 던진다."""
        if price >= self.target:
            # 실제로는 네트워크 타임아웃 같은 예외다. 알림 모듈의 문제일 뿐인데…
            raise ConnectionError("푸시 서버 응답 없음")


class Portfolio:
    """보유 종목 평가액."""

    def __init__(self, holdings: dict[str, int]) -> None:
        """종목별 보유 수량."""
        self.holdings = holdings
        self.prices: dict[str, int] = {}

    def revalue(self, symbol: str, price: int) -> None:
        """한 종목 가격이 바뀌면 전체 평가액을 다시 계산한다."""
        self.prices[symbol] = price
        total = sum(q * self.prices.get(s, 0) for s, q in self.holdings.items())
        print(f"    [포트폴리오] 평가액 {total:,}원")


class TradeLogger:
    """시세 로그. 감사·분석용."""

    def log(self, symbol: str, price: int) -> None:
        """한 줄 기록."""
        print(f"    [로그] {symbol} {price:,}")


class PriceFeed:
    """시세 수신기. 거래소 소켓에서 가격을 받는다(여기서는 push_price로 흉내)."""

    def __init__(self) -> None:
        """⚠ 문제: 수신기가 하위 기능을 '직접 생성'한다. 기능이 늘 때마다 이 생성자가 바뀐다."""
        self.chart = ChartView("005930")
        self.alert = TargetPriceAlert("005930", 72000)
        self.portfolio = Portfolio({"005930": 10, "000660": 3})
        self.logger = TradeLogger()

    def push_price(self, symbol: str, price: int) -> None:
        """새 가격 도착. ⚠ 문제: 아래 목록이 '시세를 받은 뒤 할 일' 전부를 하드코딩한다."""
        # ⚠ 문제: 종목 필터가 각 호출마다 흩어져 있다. 구독 개념이 없어서다.
        if symbol == self.chart.symbol:
            self.chart.redraw(price)            # ⚠ 문제: 화면이 닫혔는지 수신기는 모른다.
        if symbol == self.alert.symbol:
            self.alert.check(price)             # ⚠ 문제: 여기서 예외가 나면 아래 줄은 실행되지 않는다.
        self.portfolio.revalue(symbol, price)
        self.logger.log(symbol, price)


if __name__ == "__main__":
    feed = PriceFeed()

    print("[1] 평소: 71,500원 수신 → 네 기능이 순서대로 실행")
    feed.push_price("005930", 71500)

    print("[2] 사용자가 차트 화면을 닫음 — 그러나 수신기는 여전히 참조를 쥐고 있다")
    feed.chart.closed = True
    feed.push_price("005930", 71800)

    print("[3] 72,000원 도달 → 알림이 예외를 던짐")
    try:
        feed.push_price("005930", 72000)
    except ConnectionError as e:
        print(f"    !! {e} — 그 뒤의 포트폴리오 갱신과 로그가 통째로 빠졌다")

    print(f"[4] 닫힌 차트가 다시 그려진 횟수: {feed.chart.redraws_after_close}")
