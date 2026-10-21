"""옵저버 패턴 적용: 시세 수신기는 '구독자 목록'만 알고, 누가 무엇을 하는지는 모른다.

상황: 01_naive.py의 PriceFeed는 차트·알림·포트폴리오·로거를 직접 만들고 호출했다.
하린은 방향을 뒤집는다. 수신기가 기능들을 찾아가 부르는 대신, 기능들이 수신기에
'이 종목 가격이 바뀌면 알려 달라'고 등록한다.

  - PriceFeed                       [Subject]           구독 관리 + 통지
  - PriceObserver(ABC)              [Observer]          통지를 받는 공통 인터페이스
  - ChartView, TargetPriceAlert 등   [Concrete Observer] 각자 통지에 반응
  - Tick                            (통지 메시지)        푸시 모델로 넘기는 값 객체

교과서 구조에 더해, 실전에서 반드시 부딪히는 네 가지 쟁점을 코드로 다룬다.
  ① 종목별 구독  ② 통지 도중 구독 해제(복사본 순회)  ③ 관찰자 예외 격리
  ④ 화면이 닫힐 때의 명시적 구독 해제 (자동 해제는 03_pythonic.py의 weakref에서)
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

ALL = "*"   # 모든 종목을 구독할 때 쓰는 키. 로거처럼 종목을 가리지 않는 관찰자용.


@dataclass(frozen=True)
class Tick:
    """통지 메시지: 어떤 종목이 얼마가 되었는가.

    푸시(push) 모델: 주체가 관찰자에게 '바뀐 내용'을 담아 보낸다. 관찰자는 주체를
    다시 조회할 필요가 없다. frozen=True로 둔 이유 — 같은 Tick 객체가 여러 관찰자에게
    차례로 전달되므로, 앞 관찰자가 값을 고치면 뒤 관찰자가 오염된 값을 받게 된다.
    """

    symbol: str
    price: int


class PriceObserver(ABC):
    """[Observer] 시세 통지를 받는 쪽의 계약.

    PriceFeed는 이 추상 타입만 안다(DIP). 차트 모듈이든 알림 모듈이든 PriceFeed는
    import하지 않는다 — 의존 방향이 '기능 → 수신기'로 뒤집혔다.
    """

    @abstractmethod
    def on_price(self, tick: Tick) -> None:
        """가격 변경 통지. 빨리 반환해야 한다 — 다음 관찰자가 이 호출을 기다린다."""


class PriceFeed:
    """[Subject] 시세 수신기. 구독자 목록을 관리하고 새 가격을 통지한다."""

    def __init__(self) -> None:
        """종목 → 관찰자 목록. 리스트를 쓴 이유: 등록 순서대로 통지하는 것이 디버깅에 낫다.

        단, 관찰자는 통지 '순서'에 의존하면 안 된다(계약에 없는 순서에 기대는 순간
        관찰자끼리 숨은 결합이 생긴다). 순서가 중요하다면 그건 관찰자가 아니라 파이프라인이다.
        """
        self._subscribers: dict[str, list[PriceObserver]] = {}
        self._last: dict[str, int] = {}

    def subscribe(self, symbol: str, observer: PriceObserver) -> None:
        """구독. 같은 키 안에서의 중복 등록을 막는다(종목 키와 ALL을 함께 구독하면 두 번 통지된다)."""
        subs = self._subscribers.setdefault(symbol, [])
        if observer not in subs:
            subs.append(observer)

    def unsubscribe(self, symbol: str, observer: PriceObserver) -> None:
        """구독 해제. 이미 해제된 관찰자에 대해 다시 불러도 조용히 넘어간다(멱등).

        화면 닫기와 자동 정리가 겹쳐 두 번 해제되는 일이 실전에서 흔하므로, 여기서
        예외를 던지면 사용자는 '닫기 버튼이 가끔 크래시'를 겪게 된다.
        """
        subs = self._subscribers.get(symbol, [])
        if observer in subs:
            subs.remove(observer)

    def last_price(self, symbol: str) -> int | None:
        """풀(pull) 모델용 조회. 관찰자가 통지받은 종목 '외의' 정보가 필요할 때 쓴다."""
        return self._last.get(symbol)

    def push_price(self, symbol: str, price: int) -> None:
        """거래소에서 새 가격 도착. 상태를 먼저 갱신하고 나서 통지한다.

        순서가 중요하다: 통지를 먼저 하면 관찰자가 last_price()로 조회했을 때 아직
        옛 가격을 보게 된다(주체 상태가 일관된 뒤에 통지하라).
        """
        self._last[symbol] = price
        self._notify(Tick(symbol, price))

    def _notify(self, tick: Tick) -> None:
        """관찰자들에게 통지한다. 이 메서드 안에 실전 쟁점 두 가지가 들어 있다."""
        # ② 복사본 순회: list(...)로 '지금 이 순간의' 목록을 떠서 돈다. 원본 리스트를
        #    직접 돌면, 관찰자가 on_price 안에서 자기 자신을 unsubscribe할 때 리스트가
        #    한 칸 당겨져 '바로 다음 관찰자'가 건너뛰어진다(연습문제 1에서 재현).
        targets = list(self._subscribers.get(tick.symbol, [])) + list(self._subscribers.get(ALL, []))
        for observer in targets:
            # ③ 예외 격리: 관찰자 하나의 실패가 나머지 관찰자를 막지 않게 한다.
            #    주체는 관찰자가 무엇을 하는지 모르므로, 그 실패를 '처리'할 수도 없다.
            #    할 수 있는 일은 기록하고 다음으로 넘어가는 것뿐이다.
            try:
                observer.on_price(tick)
            except Exception as exc:  # noqa: BLE001 — 의도적으로 넓게 잡는다(격리가 목적)
                print(f"    !! {type(observer).__name__} 실패 격리: {exc}")


# ---------------------------------------------------------------------------
# [Concrete Observer] 들 — PriceFeed를 수정하지 않고 얼마든지 추가된다(OCP)
# ---------------------------------------------------------------------------
class ChartView(PriceObserver):
    """[Concrete Observer] 종목 차트 화면. 열릴 때 구독하고 닫힐 때 해제한다.

    ④ 구독과 해제를 '화면의 생명주기' 메서드에 짝지어 둔다. 해제를 잊으면 PriceFeed의
    리스트가 이 객체를 계속 붙잡아, 닫힌 화면이 메모리에 남고 계속 다시 그려진다.
    """

    def __init__(self, feed: PriceFeed, symbol: str) -> None:
        """어느 수신기에 구독할지 주입받는다. 수신기를 직접 만들지 않는다."""
        self.feed, self.symbol = feed, symbol

    def open(self) -> None:
        """화면 열기 = 구독 시작."""
        self.feed.subscribe(self.symbol, self)
        print(f"    (차트 {self.symbol} 열림)")

    def close(self) -> None:
        """화면 닫기 = 구독 해제. 이 한 줄이 naive 코드의 누수를 막는다."""
        self.feed.unsubscribe(self.symbol, self)
        print(f"    (차트 {self.symbol} 닫힘)")

    def on_price(self, tick: Tick) -> None:
        """다시 그리기."""
        print(f"    [차트:{tick.symbol}] {tick.price:,}원으로 다시 그림")


class TargetPriceAlert(PriceObserver):
    """[Concrete Observer] 목표가 도달 시 한 번 알리고 스스로 구독을 해제하는 일회성 관찰자.

    '통지 도중 자기 자신을 해제'하는 대표 사례다. PriceFeed가 복사본을 순회하기
    때문에 안전하다. 푸시 전송이 실패하면 해제하지 않고 남아 다음 시세에 재시도한다.
    """

    def __init__(self, feed: PriceFeed, symbol: str, target: int) -> None:
        """감시 조건. server_up은 푸시 서버 장애를 흉내 내는 스위치다."""
        self.feed, self.symbol, self.target = feed, symbol, target
        self.server_up = True

    def on_price(self, tick: Tick) -> None:
        """목표가 이상이면 푸시 후 해제."""
        if tick.price < self.target:
            return
        if not self.server_up:
            raise ConnectionError("푸시 서버 응답 없음")   # 격리되어 다른 관찰자는 계속 돈다
        print(f"    [알림] {tick.symbol} 목표가 {self.target:,}원 도달! (푸시 전송, 구독 해제)")
        self.feed.unsubscribe(tick.symbol, self)


class PortfolioValuator(PriceObserver):
    """[Concrete Observer] 보유 종목 평가액. 푸시 + 풀을 함께 쓴다.

    통지(Tick)는 '한 종목'의 가격만 알려 준다. 평가액에는 모든 보유 종목의 가격이
    필요하므로 나머지는 feed.last_price()로 끌어온다(pull). 모든 Tick에 전 종목 가격을
    싣는 것(극단적 push)은 대부분의 관찰자에게 쓸모없는 데이터를 보내는 셈이다.
    """

    def __init__(self, feed: PriceFeed, holdings: dict[str, int]) -> None:
        """보유 종목마다 구독한다. 보유하지 않은 종목의 시세에는 깨어나지 않는다."""
        self.feed, self.holdings = feed, holdings
        for symbol in holdings:
            feed.subscribe(symbol, self)

    def on_price(self, tick: Tick) -> None:
        """평가액 재계산. 아직 시세가 없는 종목은 0원으로 본다."""
        total = sum(q * (self.feed.last_price(s) or 0) for s, q in self.holdings.items())
        print(f"    [포트폴리오] 평가액 {total:,}원")


class TradeLogger(PriceObserver):
    """[Concrete Observer] 전 종목 로그. ALL 키로 한 번만 구독한다."""

    def on_price(self, tick: Tick) -> None:
        """한 줄 기록."""
        print(f"    [로그] {tick.symbol} {tick.price:,}")


if __name__ == "__main__":
    feed = PriceFeed()
    chart = ChartView(feed, "005930")
    alert = TargetPriceAlert(feed, "005930", 72000)

    print("[0] 조립: 기능들이 수신기에 '등록'한다 (수신기는 이들을 import하지 않는다)")
    chart.open()
    feed.subscribe("005930", alert)
    PortfolioValuator(feed, {"005930": 10, "000660": 3})
    feed.subscribe(ALL, TradeLogger())

    print("[1] SK하이닉스(000660) 시세 — 차트·알림은 깨어나지 않는다(종목별 구독)")
    feed.push_price("000660", 180000)

    print("[2] 삼성전자(005930) 71,500원 — 이 종목 구독자 + 전 종목 구독자")
    feed.push_price("005930", 71500)

    print("[3] 사용자가 차트를 닫은 뒤 71,800원 — 차트는 더 이상 깨어나지 않는다")
    chart.close()
    feed.push_price("005930", 71800)

    print("[4] 72,000원 도달, 그런데 푸시 서버 장애 — 실패는 격리되고 나머지는 계속")
    alert.server_up = False
    feed.push_price("005930", 72000)

    print("[5] 서버 복구 후 72,100원 — 알림이 통지 도중 스스로 해제, 다음 관찰자는 건너뛰지 않음")
    alert.server_up = True
    feed.push_price("005930", 72100)

    print("[6] 72,300원 — 일회성 알림은 더 이상 오지 않는다")
    feed.push_price("005930", 72300)
