"""07 컴포지트 — 연습문제 2 해설: 조직도 인건비 합산을 컴포지트로.

상황: 다온기계 인사팀의 스크립트는 부서(Department)와 직원(Employee)을 isinstance로
나누고, '본부 → 팀 → 직원' 2단계를 가정한 중첩 루프로 인건비를 더했다. 조직 개편으로
'본부 → 실 → 팀 → 직원'이 되자 실 소속 인원이 합계에서 빠졌다(예외조차 나지 않았다).
이 파일은 OrgUnit 공통 타입으로 바꿔 깊이와 무관하게 합산한다.
"""
from __future__ import annotations

from abc import ABC, abstractmethod


class OrgUnit(ABC):
    """[Component] 조직의 한 단위. 인건비와 인원수를 물을 수 있다."""

    def __init__(self, name: str) -> None:
        """이름."""
        self.name = name

    @abstractmethod
    def payroll(self) -> int:
        """연간 인건비(만 원)."""

    @abstractmethod
    def headcount(self) -> int:
        """인원수."""


class Employee(OrgUnit):
    """[Leaf] 직원."""

    def __init__(self, name: str, salary: int) -> None:
        """연봉(만 원)."""
        super().__init__(name)
        self.salary = salary

    def payroll(self) -> int:
        """자기 연봉."""
        return self.salary

    def headcount(self) -> int:
        """1명."""
        return 1


class Department(OrgUnit):
    """[Composite] 부서. 하위에 직원과 부서가 섞여 있어도 된다(팀장이 본부 직속인 경우 등)."""

    def __init__(self, name: str, *members: OrgUnit) -> None:
        """구성원을 생성자에서 받는다. 조직도는 한 번 만들고 읽기만 하는 경우가 많아서다."""
        super().__init__(name)
        self.members = list(members)

    def payroll(self) -> int:
        """하위 단위의 합. 깊이 가정이 없다."""
        return sum(m.payroll() for m in self.members)

    def headcount(self) -> int:
        """하위 단위 인원의 합."""
        return sum(m.headcount() for m in self.members)


if __name__ == "__main__":
    # 개편 후 4단계: 본부 → 실 → 팀 → 직원. 본부장은 본부 직속(직원과 부서가 형제).
    hq = Department(
        "생산본부",
        Employee("본부장", 12_000),
        Department("생산관리실",
                   Department("자재팀", Employee("소연", 5_200), Employee("태민", 4_800)),
                   Department("공정팀", Employee("하린", 5_000))),
        Department("품질팀", Employee("도겸", 5_500)),
    )
    print(f"[1] {hq.name}: {hq.headcount()}명, 인건비 {hq.payroll():,}만 원")
    for unit in hq.members:
        print(f"    └ {unit.name}: {unit.headcount()}명, {unit.payroll():,}만 원")
