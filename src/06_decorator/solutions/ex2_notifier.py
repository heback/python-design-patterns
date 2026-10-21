"""06 데코레이터 — 연습문제 2 해설: 플래그 인자 Notifier를 데코레이터 체인으로.

상황: 농장 관리 앱의 알림 모듈 Notifier.send(msg, *, with_retry, with_log, with_rate_limit)는
플래그 세 개를 받아 한 메서드 안에서 재시도·로그·호출 제한을 처리했다. 호출부마다 플래그
조합이 달랐고, "로그는 재시도마다 찍어야 하나, 최종 결과만 찍어야 하나" 같은 질문에
코드가 답하지 못했다. 이 파일은 각 플래그를 같은 Notifier 인터페이스의 래퍼 하나로 바꾼다.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Callable


class Notifier(ABC):
    """[Component] 알림 전송. 성공 여부를 bool로 돌려준다(원래 코드의 계약을 유지)."""

    @abstractmethod
    def send(self, msg: str) -> bool:
        """메시지를 보낸다."""


class SmsNotifier(Notifier):
    """[Concrete Component] SMS API 호출. 데모를 위해 처음 fail_times번은 연결 오류를 낸다."""

    def __init__(self, fail_times: int = 0) -> None:
        """실패 횟수 주입 — 재시도 래퍼를 결정적으로 시험하기 위해서다."""
        self._fail_left = fail_times

    def send(self, msg: str) -> bool:
        """실패 횟수가 남았으면 ConnectionError."""
        if self._fail_left > 0:
            self._fail_left -= 1
            raise ConnectionError("SMS 게이트웨이 응답 없음")
        print(f"      (SMS) {msg}")
        return True


class NotifierDecorator(Notifier):
    """[Decorator] 공통 위임 기반."""

    def __init__(self, inner: Notifier) -> None:
        """감쌀 Notifier."""
        self._inner = inner

    def send(self, msg: str) -> bool:
        """기본 위임."""
        return self._inner.send(msg)


class RetryingNotifier(NotifierDecorator):
    """[Concrete Decorator] ConnectionError면 최대 attempts번 시도한다."""

    def __init__(self, inner: Notifier, attempts: int = 3) -> None:
        """시도 횟수는 래퍼마다 다르게 줄 수 있다(플래그 방식에서는 3이 하드코딩돼 있었다)."""
        super().__init__(inner)
        self._attempts = attempts

    def send(self, msg: str) -> bool:
        """모두 실패하면 False — 원래 코드의 계약과 같다."""
        for _ in range(self._attempts):
            try:
                return self._inner.send(msg)
            except ConnectionError:
                continue
        return False


class LoggingNotifier(NotifierDecorator):
    """[Concrete Decorator] 시도와 결과를 기록한다.

    체인에서의 위치가 곧 '무엇을 기록하는가'를 정한다.
    Retrying 바깥이면 최종 결과 1줄, 안쪽이면 시도마다 1줄. 원래 코드는 이 선택이 불가능했다.
    """

    def __init__(self, inner: Notifier, label: str = "log") -> None:
        """로그 접두어."""
        super().__init__(inner)
        self._label = label

    def send(self, msg: str) -> bool:
        """예외도 기록한 뒤 다시 던진다 — 관찰만 하고 흐름은 바꾸지 않는다."""
        try:
            ok = self._inner.send(msg)
        except ConnectionError as e:
            print(f"    [{self._label}] 실패: {e}")
            raise
        print(f"    [{self._label}] 결과: {ok}")
        return ok


class RateLimitingNotifier(NotifierDecorator):
    """[Concrete Decorator] interval초 안의 재호출은 보내지 않고 False.

    clock을 주입받는 이유: time.monotonic을 직접 부르면 테스트가 실제로 기다려야 한다.
    """

    def __init__(self, inner: Notifier, interval: float, clock: Callable[[], float]) -> None:
        """간격과 시계."""
        super().__init__(inner)
        self._interval, self._clock = interval, clock
        self._last: float | None = None

    def send(self, msg: str) -> bool:
        """간격 안이면 차단."""
        now = self._clock()
        if self._last is not None and now - self._last < self._interval:
            print(f"    [rate] 차단: {msg!r}")
            return False
        self._last = now
        return self._inner.send(msg)


if __name__ == "__main__":
    t = [0.0]  # 가짜 시계: 리스트에 담아 람다가 바뀐 값을 읽게 한다

    print("[1] 제한 → 로그(최종) → 재시도 → 로그(시도별) → SMS (처음 2번 실패)")
    n = RateLimitingNotifier(
        LoggingNotifier(RetryingNotifier(LoggingNotifier(SmsNotifier(fail_times=2), "try"), 3), "final"),
        interval=1.0, clock=lambda: t[0])
    n.send("3번 하우스 수분 15% 미만")
    t[0] = 0.5
    n.send("3번 하우스 수분 14% 미만")   # 0.5초 뒤 → 차단
    t[0] = 2.0
    n.send("3번 하우스 관수 완료")

    print("[2] 재시도만 필요한 호출부 — 같은 클래스, 다른 조합")
    print(f"    결과: {RetryingNotifier(SmsNotifier(fail_times=5), 3).send('테스트')}")
