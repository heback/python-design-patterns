"""연습문제 2 해설: 매개변수 8개짜리 Request 생성자를 유창한 빌더로, GET 본문은 build()에서 거부.

상황: BI 팀의 데이터 수집 스크립트는 외부 광고 플랫폼 API를 부를 때
`Request(method, url, headers=None, params=None, body=None, timeout=None, retries=None, auth=None)`를
썼다(문제 본문 코드). 호출부마다 None이 늘어섰고, 누군가 GET 요청에 본문을 실어 보내
일부 프록시가 본문을 버리는 바람에 필터가 적용되지 않은 전체 데이터가 내려온 사고가 있었다.

해설의 설계 결정:
- Request는 frozen dataclass(완성품), RequestBuilder는 가변(조립 중 상태).
- header()·param()은 '하나씩 누적'하는 단계로 만든다 — dict를 통째로 받는 것보다 조건부 조립에 유리.
- GET+본문 금지, 재시도에는 타임아웃 필수 같은 교차 제약은 build()에서 한 번에 검사한다.
"""
from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping, Self


@dataclass(frozen=True)
class Request:
    """[Product] 완성된 HTTP 요청 정의. 매핑 필드는 읽기 전용 뷰로 감싸 불변을 끝까지 지킨다."""

    method: str
    url: str
    headers: Mapping[str, str]
    params: Mapping[str, str]
    body: bytes | None
    timeout: float
    retries: int


class RequestBuilder:
    """[Builder] Request를 단계적으로 조립한다."""

    def __init__(self, method: str, url: str) -> None:
        """필수 두 가지만 생성자로. 나머지는 이름 붙은 단계와 합리적 기본값."""
        self._method, self._url = method.upper(), url
        # 메서드를 대문자로 정규화해 두어야 build()의 "GET" 비교가 "get" 입력에도 동작한다.
        # 아래 필드들은 조립 중 상태다. None은 '아직 지정하지 않음'을 뜻하며 build()에서 기본값으로 바뀐다.
        self._headers: dict[str, str] = {}
        self._params: dict[str, str] = {}
        self._body: bytes | None = None
        self._timeout: float | None = None
        self._retries = 0

    def header(self, name: str, value: str) -> Self:
        """헤더 하나를 더한다."""
        self._headers[name] = value
        return self

    def bearer(self, token: str) -> Self:
        """auth 인자 대신 의도가 드러나는 편의 단계. 빌더는 '도메인 어휘'를 더하기 좋은 자리다."""
        return self.header("Authorization", f"Bearer {token}")

    def param(self, name: str, value: str) -> Self:
        """쿼리 문자열 매개변수 하나를 더한다."""
        self._params[name] = value
        return self

    def body(self, data: bytes) -> Self:
        """본문을 정한다. GET 여부는 여기서 검사하지 않는다(build()의 몫)."""
        self._body = data
        return self

    def timeout(self, seconds: float) -> Self:
        """타임아웃."""
        self._timeout = seconds
        return self

    def retries(self, n: int) -> Self:
        """재시도 횟수."""
        self._retries = n
        return self

    def build(self) -> Request:
        """교차 검증 후 불변 Request를 만든다."""
        if self._method in ("GET", "HEAD") and self._body is not None:
            raise ValueError(f"{self._method} 요청에는 본문을 둘 수 없다 — 필터는 param()으로")
        if self._retries and self._timeout is None:
            # 타임아웃 없는 재시도는 '영원히 기다리기 × n'이 된다.
            raise ValueError("재시도를 쓰려면 timeout()을 지정해야 한다")
        # dict(...)로 복사한 뒤 읽기 전용 뷰로 감싼다. 복사하지 않으면 빌더를 재사용해 헤더를 더할 때
        # 이미 만든 Request의 헤더까지 바뀐다 — 뷰는 원본의 변경을 그대로 비춰 주기 때문이다.
        # timeout 기본값 30초는 '지정 안 함'이 '무한 대기'가 되지 않게 하려는 안전장치다.
        return Request(self._method, self._url, MappingProxyType(dict(self._headers)),
                       MappingProxyType(dict(self._params)), self._body,
                       self._timeout if self._timeout is not None else 30.0, self._retries)


if __name__ == "__main__":
    print("[1] 광고 성과 조회 — 필터는 쿼리 매개변수로")
    # 소문자 "get"도 받아 준다 — 정규화는 빌더의 일이다. 단계 순서는 자유롭다.
    req = (RequestBuilder("get", "https://ads.example.com/v2/reports")
           .bearer("tok-123").param("from", "2026-09-01").param("to", "2026-09-30")
           .timeout(10).retries(3).build())
    print(f"  {req.method} {req.url} params={dict(req.params)} retries={req.retries}")

    print("\n[2] 사고를 낸 조합: GET + 본문")
    try:
        # body() 단계 자체는 통과한다. 거부는 교차 검증 시점인 build()에서 일어난다.
        RequestBuilder("GET", "https://ads.example.com/v2/reports").body(b'{"from": "2026-09-01"}').build()
    except ValueError as e:
        print(f"  ValueError: {e}")

    print("\n[3] 타임아웃 없는 재시도")
    try:
        RequestBuilder("POST", "https://ads.example.com/v2/jobs").body(b"{}").retries(5).build()
    except ValueError as e:
        print(f"  ValueError: {e}")

    print("\n[4] 완성된 Request의 헤더는 바꿀 수 없다")
    try:
        # frozen=True만으로는 dict 내부 수정을 못 막는다. MappingProxyType이 그 구멍을 막는다.
        req.headers["Authorization"] = "탈취"  # type: ignore[index]
    except TypeError as e:
        print(f"  TypeError: {e}")
