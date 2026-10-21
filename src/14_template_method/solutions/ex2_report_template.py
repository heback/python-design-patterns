"""[14장 연습문제 2 해설] CSV/JSON/XML 리포트 생성기 세 개를 템플릿 메서드로 리팩터링한다.

상황: 코드랩 운영팀은 주간 채점 통계를 세 형식으로 내려받는다. 원래 코드는 형식마다
'데이터 조회 → 머리말 → 본문 → 꼬리말 → 저장'을 각자 구현했고, JSON 생성기만 조회 단계에서
삭제된 문제를 거르지 않아 숫자가 달랐다. 공통 단계(조회, 저장)는 골격으로 올리고,
형식마다 다른 세 단계(머리말·행·꼬리말)만 하위 클래스에 남긴다.

설계 판단: 머리말과 꼬리말은 CSV처럼 없는 형식이 있으므로 '훅'(기본값 빈 문자열),
행 서식은 모든 형식에 반드시 필요하므로 '추상 단계'로 둔다. 행 사이 구분자(JSON의 쉼표)도
형식마다 다르므로 클래스 속성으로 노출한다 — 메서드 훅보다 가벼운 '데이터 훅'이다.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import final

# 데모용 데이터. deleted=True인 문제는 어느 형식에서든 빠져야 한다.
ROWS = [
    {"problem": "A+B", "submissions": 120, "ac_rate": 0.92, "deleted": False},
    {"problem": "피보나치", "submissions": 80, "ac_rate": 0.55, "deleted": False},
    {"problem": "테스트용", "submissions": 3, "ac_rate": 0.0, "deleted": True},
]


class ReportGenerator(ABC):
    """[Abstract Class] 리포트 생성 골격."""

    separator: str = "\n"     # 데이터 훅: 행 사이 구분자

    @final
    def generate(self) -> str:
        """[Template Method] 조회 → 머리말 → 본문 → 꼬리말 → 저장. 순서와 필터는 여기서만 정한다."""
        rows = self.fetch()
        body = self.separator.join(self.format_row(r) for r in rows)
        parts = [p for p in (self.header(), body, self.footer()) if p]
        return self.save("\n".join(parts))

    @final
    def fetch(self) -> list[dict]:
        """공통 단계: 삭제된 문제 필터가 한 곳에만 있다(원래 JSON 버그의 원인 제거)."""
        return [r for r in ROWS if not r["deleted"]]

    def header(self) -> str:
        """훅: 머리말. 기본은 없음."""
        return ""

    @abstractmethod
    def format_row(self, row: dict) -> str:
        """추상 단계: 행 하나의 서식."""

    def footer(self) -> str:
        """훅: 꼬리말. 기본은 없음."""
        return ""

    @final
    def save(self, text: str) -> str:
        """공통 단계: 실제로는 파일/S3에 쓴다. 데모에서는 바이트 수를 덧붙여 돌려준다."""
        return f"{text}\n  ({type(self).__name__}: {len(text.encode())} bytes 저장)"


class CsvReport(ReportGenerator):
    """[Concrete Class] CSV는 열 이름 줄이 머리말이고 꼬리말이 없다."""

    def header(self) -> str:
        """열 이름."""
        return "problem,submissions,ac_rate"

    def format_row(self, row: dict) -> str:
        """쉼표 구분."""
        return f"{row['problem']},{row['submissions']},{row['ac_rate']}"


class JsonReport(ReportGenerator):
    """[Concrete Class] 배열 괄호가 머리말·꼬리말, 쉼표가 구분자."""

    separator = ",\n"

    def header(self) -> str:
        """배열 시작."""
        return "["

    def format_row(self, row: dict) -> str:
        """json.dumps를 쓰지 않은 이유: 행 단위 단계 분할을 보여 주려는 데모이기 때문. 실무에선 dumps."""
        return f'  {{"problem": "{row["problem"]}", "submissions": {row["submissions"]}}}'

    def footer(self) -> str:
        """배열 끝."""
        return "]"


class XmlReport(ReportGenerator):
    """[Concrete Class] 루트 태그가 머리말·꼬리말."""

    def header(self) -> str:
        """루트 시작."""
        return "<report>"

    def format_row(self, row: dict) -> str:
        """속성 형태의 행."""
        return f'  <row problem="{row["problem"]}" ac_rate="{row["ac_rate"]}"/>'

    def footer(self) -> str:
        """루트 끝."""
        return "</report>"


if __name__ == "__main__":
    for gen in (CsvReport(), JsonReport(), XmlReport()):
        print(gen.generate())
    print("세 형식 모두 '테스트용' 문제가 빠졌다 — 필터가 골격 한 곳에 있기 때문")
