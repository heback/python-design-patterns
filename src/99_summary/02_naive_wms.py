"""순진한 프로토타입: 로봇 창고 관리 시스템(WMS)의 모든 것이 한 클래스에.

상황: 한빛로지스의 개발자 도윤은 석 달 전 창고 자동화 프로토타입을 만들었다. 주문이 들어오면
재고가 있는 칸을 찾아 피킹 로봇을 보내는 단순한 구조였다. 그 뒤 요구가 쌓였다.
- 로봇 제조사가 둘이 되었다(Acme: 좌표 mm 단위 / RoboKo: 칸 이름 문자열). SDK 모양이 다르다.
- 경로 알고리즘을 구역에 따라 바꾸고 싶다(가까운 칸 먼저 / 구역 순서대로 쓸기).
- 주문을 대기열에 넣고, 실행 전이면 취소할 수 있어야 한다.
- 배터리가 낮아지면 충전하러 보내고, 관제 대시보드에 실시간으로 보여야 한다.
- 재고를 구역 → 랙 → 선반 → 칸 단위로 집계해야 한다.
도윤은 매번 WMS 클래스에 분기를 추가했다. 이 파일은 그 결과다.
"""
from __future__ import annotations

# 재고: 구역 → 랙 → 선반 → [(칸 코드, SKU, 수량, x, y)] — 깊이가 코드에 박혀 있다
INVENTORY = {
    "A": {"A1": {"A1-1": [("A1-1-01", "MUG", 5, 1, 1), ("A1-1-02", "CUP", 3, 2, 1)]}},
    "B": {"B1": {"B1-1": [("B1-1-01", "MUG", 4, 8, 6)], "B1-2": [("B1-2-01", "PLATE", 9, 9, 6)]}},
}


class WMS:
    """창고 관리 시스템. 로봇·경로·주문·배터리·대시보드·재고를 한 클래스가 다 안다."""

    def __init__(self, route_mode: str) -> None:
        """로봇 두 대(제조사가 다름)와 경로 모드."""
        self.robots = [{"id": "R1", "vendor": "acme", "bat": 40, "pos": (0, 0), "status": "idle"},
                       {"id": "R2", "vendor": "roboko", "bat": 50, "pos": (0, 0), "status": "idle"}]
        self.route_mode = route_mode

    def count(self, sku: str) -> int:
        """⚠ 문제: 4중 반복문 — 계층이 하나 늘면(예: 선반 아래 '칸막이') 모든 집계 코드를 고친다."""
        total = 0
        for racks in INVENTORY.values():
            for shelves in racks.values():
                for bins in shelves.values():
                    for _code, s, qty, _x, _y in bins:
                        if s == sku:
                            total += qty
        return total

    def order(self, sku: str, qty: int) -> None:
        """⚠ 문제: 주문 즉시 실행된다. 대기열도 취소도 없다 — 요청이 객체가 아니기 때문이다."""
        bins = [(c, q, x, y) for racks in INVENTORY.values() for shelves in racks.values()
                for bs in shelves.values() for c, s, q, x, y in bs if s == sku and q > 0]
        # ⚠ 문제: 경로 알고리즘이 if 분기로 박혀 있다. 세 번째 알고리즘은 이 메서드를 또 고친다.
        if self.route_mode == "nearest":
            bins.sort(key=lambda b: b[2] + b[3])
        elif self.route_mode == "sweep":
            bins.sort(key=lambda b: b[0])
        robot = max(self.robots, key=lambda r: r["bat"])
        for code, _q, x, y in bins[:qty]:  # 단순화: 칸 하나에서 1개씩 집는다
            # ⚠ 문제: 제조사 SDK 차이가 업무 로직 한가운데 있다. 세 번째 제조사가 오면 여기를 고친다.
            if robot["vendor"] == "acme":
                print(f"    [acme] goto({x * 1000}mm, {y * 1000}mm) grab({code})")
            elif robot["vendor"] == "roboko":
                print(f"    [roboko] move('{code}') pick({code[-2:]})")
            robot["bat"] -= 25  # 한 번 이동·피킹에 25%p (시뮬레이션)
            robot["status"] = "moving"
            # ⚠ 문제: 대시보드 갱신이 직접 호출이다. 모바일 알림이 추가되면 여기에 또 한 줄.
            print(f"    [대시보드] {robot['id']} {code} 피킹, 배터리 {robot['bat']}%")
            # ⚠ 문제: 배터리 처리도 여기서. 충전을 '바로' 시작해 진행 중인 주문과 뒤엉킨다.
            if robot["bat"] < 30:
                robot["status"] = "charging"
                print(f"    [대시보드] {robot['id']} 충전 시작 (주문 처리 도중!)")
        robot["status"] = "idle" if robot["status"] != "charging" else "charging"


if __name__ == "__main__":
    wms = WMS(route_mode="nearest")
    print("[1] MUG 재고:", wms.count("MUG"))
    print("[2] MUG 2개 주문 — 즉시 실행")
    wms.order("MUG", 2)
    print("[3] 방금 주문을 취소하고 싶다면? → 방법이 없다(이미 실행됨)")
    print("[4] 이 클래스를 고쳐야 하는 이유: 제조사 추가, 경로 알고리즘, 주문 정책,")
    print("    배터리 규칙, 알림 채널, 재고 계층 — 변경 축 여섯 개가 한 클래스에 묶여 있다")
