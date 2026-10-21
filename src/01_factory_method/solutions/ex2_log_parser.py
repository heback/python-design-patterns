"""연습문제 2 해설: if/elif로 파서를 고르는 로그 수집기를 팩토리 메서드로, 이어서 레지스트리로.

상황: 연구실 서버 관리자가 웹 서버 접근 로그를 모으는 LogCollector를 만들었다. collect()
안에서 `if fmt == "nginx": ... elif fmt == "apache": ...`로 파서를 골랐다(문제 본문 코드).
본문 01~02와 같은 냄새 — 흐름과 생성의 결합 — 를 같은 방법으로 푼다.

해설의 두 단계:
- 1단계(GoF 팩토리 메서드): LogCollector가 collect() 흐름을 소유하고 create_parser()를 훅으로
  남긴다. NginxCollector/ApacheCollector가 오버라이드한다.
- 2단계(__init_subclass__ 레지스트리): 하위 클래스가 '정의되는 순간' 형식 이름으로 등록되어
  설정 문자열로 수집기를 고를 수 있게 한다. Creator 하위 클래스 자체를 등록한다는 점이
  본문 04_registry.py(Product를 등록)와 다르다 — 어느 쪽을 등록해도 된다.
"""
from __future__ import annotations

import re
from abc import ABC, abstractmethod
from typing import Any, ClassVar


class LogParser(ABC):
    """[Product] 로그 한 줄을 (IP, 상태 코드)로 바꾼다."""

    @abstractmethod
    def parse(self, line: str) -> tuple[str, int]:
        """한 줄을 해석한다."""


class NginxParser(LogParser):
    """[Concrete Product] nginx combined 형식: IP가 맨 앞, 상태 코드는 요청 문자열 뒤."""

    PATTERN = re.compile(r'^(\S+) .*?" (\d{3}) ')

    def parse(self, line: str) -> tuple[str, int]:
        """정규식으로 IP와 상태 코드를 뽑는다."""
        m = self.PATTERN.match(line)
        if m is None:
            # assert가 아니라 예외: assert는 python -O에서 사라지므로 입력 검증에 쓰면 안 된다.
            raise ValueError(f"nginx 형식이 아님: {line}")
        return m.group(1), int(m.group(2))


class ApacheParser(LogParser):
    """[Concrete Product] 연구실 아파치 서버의 사용자 정의 형식: '상태|IP|경로'."""

    def parse(self, line: str) -> tuple[str, int]:
        """세로 막대(|)로 나눈다. 필드 순서가 nginx와 다르다는 점이 파서를 나눌 이유다."""
        status, ip, _path = line.split("|")
        return ip, int(status)


class LogCollector(ABC):
    """[Creator] 수집 흐름(파싱 → 오류 집계)을 소유한다. 형식별 지식은 없다."""

    # 2단계: 형식 이름 → Concrete Creator 클래스.
    registry: ClassVar[dict[str, type[LogCollector]]] = {}

    def __init_subclass__(cls, *, fmt: str | None = None, **kwargs: Any) -> None:
        """하위 클래스 정의 시 fmt 키로 자기 자신을 등록한다(2단계)."""
        super().__init_subclass__(**kwargs)
        if fmt is None:
            return
        if fmt in LogCollector.registry:
            # 본문 04_registry.py와 같은 이유: 조용히 덮어쓰면 두 수집기가 서로를 가리는 버그가 늦게 드러난다.
            raise ValueError(f"형식 {fmt!r}가 이미 {LogCollector.registry[fmt].__name__}로 등록됨")
        LogCollector.registry[fmt] = cls

    @classmethod
    def for_format(cls, fmt: str) -> LogCollector:
        """설정 문자열로 수집기를 만든다. 원래 코드의 if/elif가 여기서 표 조회 한 번이 된다."""
        return LogCollector.registry[fmt]()

    @abstractmethod
    def create_parser(self) -> LogParser:
        """[Factory Method] 이 수집기가 쓸 파서를 만든다(1단계의 핵심)."""

    def collect(self, lines: list[str]) -> dict[str, int]:
        """IP별 5xx 오류 수를 센다. 파서를 '언제' 만들지는 여기서 결정한다."""
        parser = self.create_parser()
        errors: dict[str, int] = {}
        for line in lines:
            ip, status = parser.parse(line)
            if status >= 500:
                errors[ip] = errors.get(ip, 0) + 1
        return errors


class NginxCollector(LogCollector, fmt="nginx"):
    """[Concrete Creator] nginx 로그 수집기."""

    def create_parser(self) -> LogParser:
        """nginx 파서를 고른다."""
        return NginxParser()


class ApacheCollector(LogCollector, fmt="apache"):
    """[Concrete Creator] 아파치 로그 수집기."""

    def create_parser(self) -> LogParser:
        """아파치 파서를 고른다."""
        return ApacheParser()


if __name__ == "__main__":
    nginx_lines = [
        '10.0.0.7 - - [08/Oct/2026:10:00:01] "GET /spectra HTTP/1.1" 200 512',
        '10.0.0.9 - - [08/Oct/2026:10:00:02] "POST /upload HTTP/1.1" 502 0',
        '10.0.0.9 - - [08/Oct/2026:10:00:03] "POST /upload HTTP/1.1" 503 0',
    ]
    apache_lines = ["500|10.0.1.2|/xrd", "200|10.0.1.3|/ms", "500|10.0.1.2|/xrd"]

    print("[1] 1단계 — Concrete Creator를 직접 고른다 (GoF 팩토리 메서드)")
    print("  nginx :", NginxCollector().collect(nginx_lines))
    print("  apache:", ApacheCollector().collect(apache_lines))

    print("\n[2] 2단계 — 설정 문자열로 고른다 (정의만 하면 등록되는 레지스트리)")
    print("  등록된 형식:", sorted(LogCollector.registry))
    print("  for_format('apache'):", LogCollector.for_format("apache").collect(apache_lines))

    print("\n[3] 새 형식 추가: 프레임워크(LogCollector) 수정 없이 클래스 정의만으로")

    class CaddyParser(LogParser):
        """[Concrete Product] Caddy 서버의 공백 구분 형식: '상태 IP 경로'."""

        def parse(self, line: str) -> tuple[str, int]:
            """공백으로 나눈다."""
            status, ip, _path = line.split()
            return ip, int(status)

    class CaddyCollector(LogCollector, fmt="caddy"):
        """[Concrete Creator] 정의되는 순간 'caddy'로 등록된다."""

        def create_parser(self) -> LogParser:
            """Caddy 파서를 고른다."""
            return CaddyParser()

    print("  등록된 형식:", sorted(LogCollector.registry))
    print("  for_format('caddy'):", LogCollector.for_format("caddy").collect(["503 10.0.2.5 /ms", "200 10.0.2.6 /uv"]))
