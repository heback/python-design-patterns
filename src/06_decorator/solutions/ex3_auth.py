"""06 데코레이터 — 연습문제 3 해설: 웹 핸들러에 '인증 확인'을 붙이는 세 가지 방법.

상황: 농장 관리 웹 콘솔에 인증을 붙여야 한다. 대부분의 화면은 로그인이 필요하지만
/health 같은 몇몇 엔드포인트는 공개다. 후보는 (A) 함수 @decorator, (B) 미들웨어 리스트,
(C) GoF 데코레이터 객체. 이 파일은 셋을 같은 요청으로 실행해 보인다.
세 방법 모두 '같은 호출 모양을 유지한 채 책임을 덧붙인다'는 데코레이터 의도를 구현한다.
차이는 '어디서, 언제 적용 범위를 정하는가'다.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from functools import reduce, wraps
from typing import Callable


@dataclass
class Request:
    """간단한 요청 객체."""

    path: str
    user: str | None = None
    headers: dict[str, str] = field(default_factory=dict)


Handler = Callable[[Request], str]
"""[Component] 핸들러의 모양: 요청 → 응답 문자열."""


# --- (A) 함수 @decorator: 핸들러 '정의 지점'에서 선언 -----------------------

def login_required(handler: Handler) -> Handler:
    """[Concrete Decorator] 로그인하지 않았으면 401.

    장점: 핸들러 코드 바로 위에서 '이 화면은 인증 필요'가 보인다(선언적, 지역적).
    단점: 빠뜨리기 쉽다. 새 핸들러에 @를 깜빡하면 기본값이 '공개'가 된다.
    """
    @wraps(handler)
    def wrapper(req: Request) -> str:
        """인증 확인 후 위임."""
        if req.user is None:
            return "401 Unauthorized"
        return handler(req)
    return wrapper


@login_required
def dashboard(req: Request) -> str:
    """대시보드(인증 필요)."""
    return f"200 {req.user}의 대시보드"


def health(req: Request) -> str:
    """헬스 체크(공개)."""
    return "200 ok"


# --- (B) 미들웨어 리스트: '앱 전체'에 순서대로 적용 --------------------------

Middleware = Callable[[Handler], Handler]
PUBLIC_PATHS = {"/health"}


def auth_middleware(next_handler: Handler) -> Handler:
    """[Concrete Decorator] 모든 요청에 적용. 예외 경로는 화이트리스트.

    장점: 기본값이 '보호됨'이다. 새 엔드포인트를 만들어도 빠뜨릴 수 없다.
    단점: 핸들러 코드만 봐서는 인증 여부가 보이지 않는다.
    """
    def handle(req: Request) -> str:
        """공개 경로가 아니면 인증 확인."""
        if req.path not in PUBLIC_PATHS and req.user is None:
            return "401 Unauthorized"
        return next_handler(req)
    return handle


def timing_middleware(next_handler: Handler) -> Handler:
    """[Concrete Decorator] 응답에 처리 표시를 붙인다(순서 확인용)."""
    def handle(req: Request) -> str:
        """위임 후 꼬리표."""
        return next_handler(req) + " (timed)"
    return handle


def build_app(router: Handler, middlewares: list[Middleware]) -> Handler:
    """리스트의 첫 미들웨어가 가장 바깥이 되도록 조립한다. 사실상 데코레이터 체인이다."""
    return reduce(lambda inner, mw: mw(inner), reversed(middlewares), router)


def router(req: Request) -> str:
    """경로에 따라 핸들러 선택(인증을 모르는 원래 핸들러들)."""
    routes: dict[str, Handler] = {"/health": health, "/dashboard": lambda r: f"200 {r.user}의 대시보드"}
    return routes.get(req.path, lambda r: "404")(req)


# --- (C) GoF 데코레이터 객체: 핸들러가 '여러 메서드를 가진 객체'일 때 ---------

class Resource:
    """[Component] REST 리소스. get/post 두 메서드 — 함수 하나로는 감쌀 수 없는 모양."""

    def get(self, req: Request) -> str:
        """조회."""
        raise NotImplementedError

    def post(self, req: Request) -> str:
        """변경."""
        raise NotImplementedError


class ValveResource(Resource):
    """[Concrete Component] 관수 밸브 제어."""

    def get(self, req: Request) -> str:
        """밸브 상태."""
        return "200 valve=closed"

    def post(self, req: Request) -> str:
        """밸브 열기."""
        return "200 valve opened"


class WriteProtected(Resource):
    """[Concrete Decorator] 조회는 공개, 변경만 인증. 메서드별로 다른 책임을 덧붙인다.

    인터페이스가 메서드 여러 개이고 메서드마다 정책이 다르면 객체 데코레이터가 자연스럽다.
    """

    def __init__(self, inner: Resource) -> None:
        """감쌀 리소스."""
        self._inner = inner

    def get(self, req: Request) -> str:
        """그대로 위임."""
        return self._inner.get(req)

    def post(self, req: Request) -> str:
        """인증 후 위임."""
        return "401 Unauthorized" if req.user is None else self._inner.post(req)


if __name__ == "__main__":
    anon, alice = Request("/dashboard"), Request("/dashboard", user="alice")
    print("[A] 함수 @decorator")
    print(f"    익명 → {dashboard(anon)} / alice → {dashboard(alice)} / health → {health(Request('/health'))}")

    print("[B] 미들웨어 리스트 [timing, auth]")
    app = build_app(router, [timing_middleware, auth_middleware])
    for r in (anon, alice, Request("/health")):
        print(f"    {r.path} user={r.user} → {app(r)}")

    print("[C] GoF 데코레이터 객체(메서드별 정책)")
    valve = WriteProtected(ValveResource())
    print(f"    익명 GET → {valve.get(anon)} / 익명 POST → {valve.post(anon)} / alice POST → {valve.post(alice)}")
