"""99 종합 — 통합 코드: 로봇 창고 WMS. 변경 축마다 가장 가벼운 해법 하나.

상황: 도윤의 프로토타입 WMS 클래스에는 변경 축 여섯 개가 묶여 있었다. 팀은 "패턴을 몇 개
넣을까"가 아니라 "실제로 바뀌는 것이 몇 가지인가"부터 셌다.
- 제조사 SDK 차이       → 어댑터: AcmeAdapter, RoboKoAdapter (Target은 Protocol)
- 경로 알고리즘         → 전략: 그냥 함수 + 이름표 dict(ROUTES)
- 주문 대기·취소        → 커맨드: PickOrder, ChargeRobot + TaskQueue
- 알림 채널             → 옵저버: EventHub에 함수 구독
- 재고 계층 깊이        → 컴포지트 + 반복자: Group/Bin, walk() 제너레이터
- 배터리 대응           → 새 패턴 없음: 옵저버 + 커맨드 조합(BatteryGuard)
운영 콘솔용 정문 하나는 퍼사드(WarehouseOps). 상태·싱글턴·빌더 등은 넣지 않았다.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterator, Protocol


# ---------- 컴포지트 + 반복자: 재고 계층 ----------
@dataclass
class Bin:
    """[Leaf] 칸 하나."""
    code: str
    sku: str
    qty: int
    x: int
    y: int

    def walk(self) -> Iterator[Bin]:
        """자기 하나를 내보낸다. Group과 같은 질문에 답하므로 호출자가 둘을 구별하지 않는다."""
        yield self


@dataclass
class Group:
    """[Composite] 구역·랙·선반 — 역할이 같으므로 단계별 클래스 대신 하나로 충분하다."""
    name: str
    children: list[Group | Bin]

    def walk(self) -> Iterator[Bin]:
        """[반복자] 깊이가 몇 단이든 칸들의 평평한 흐름이 된다. 칸막이 단계 추가 = 데이터 한 겹."""
        for child in self.children:
            yield from child.walk()


# ---------- 어댑터: 제조사 SDK를 우리 말로 ----------
class AcmeSDK:
    """[Adaptee] mm 좌표, 배터리는 정수 %. 우리가 고칠 수 없다."""
    def __init__(self) -> None:
        """시뮬레이션 배터리."""
        self.pct = 40

    def goto(self, x_mm: int, y_mm: int) -> None:
        """이동할 때마다 배터리가 준다."""
        self.pct -= 15

    def dock(self) -> None:
        """도킹이 곧 충전."""
        self.pct = 100


class RoboKoSDK:
    """[Adaptee] 칸 이름으로 이동, 배터리는 0~1 실수."""
    def __init__(self) -> None:
        """시뮬레이션 배터리."""
        self.bat = 0.5

    def move(self, cell: str) -> None:
        """이동."""
        self.bat -= 0.15

    def charge(self) -> None:
        """충전."""
        self.bat = 1.0


class RobotDriver(Protocol):
    """[Target] 우리 쪽이 로봇에게 원하는 최소한."""
    def go(self, b: Bin) -> None:
        """칸으로 간다."""
    def battery(self) -> int:
        """배터리(%). 단위 차이는 어댑터가 흡수한다."""
    def recharge(self) -> None:
        """충전한다. SDK마다 이름이 다르다(dock / charge)."""


class AcmeAdapter:
    """[Adapter] 칸 좌표(m)를 mm로 번역한다."""
    def __init__(self, sdk: AcmeSDK) -> None:
        """SDK를 감싼다(합성)."""
        self.sdk = sdk

    def go(self, b: Bin) -> None:
        """m → mm."""
        self.sdk.goto(b.x * 1000, b.y * 1000)

    def battery(self) -> int:
        """이미 %다."""
        return self.sdk.pct

    def recharge(self) -> None:
        """도킹 = 충전."""
        self.sdk.dock()


class RoboKoAdapter:
    """[Adapter] 칸 코드를 이름으로, 0~1을 %로 번역한다."""
    def __init__(self, sdk: RoboKoSDK) -> None:
        """SDK를 감싼다."""
        self.sdk = sdk

    def go(self, b: Bin) -> None:
        """칸 이름으로 이동."""
        self.sdk.move(b.code)

    def battery(self) -> int:
        """0.35 → 35. 반올림으로 부동소수 오차를 숨긴다."""
        return round(self.sdk.bat * 100)

    def recharge(self) -> None:
        """충전."""
        self.sdk.charge()


@dataclass
class Robot:
    """로봇 = 이름 + 드라이버. 상태가 '대기/작업' 정도라 상태 패턴은 넣지 않았다."""
    name: str
    driver: RobotDriver


# ---------- 옵저버: 알림 허브 ----------
class EventHub:
    """[Subject] 이벤트 이름별 함수 구독. 알리는 쪽은 듣는 쪽을 모른다."""
    def __init__(self) -> None:
        """이벤트 이름 → 구독 함수 목록."""
        self.subs: dict[str, list[Callable[[dict], None]]] = {}

    def on(self, event: str, fn: Callable[[dict], None]) -> None:
        """구독. 새 알림 채널 = 이 한 줄."""
        self.subs.setdefault(event, []).append(fn)

    def emit(self, event: str, **data: object) -> None:
        """통지."""
        for fn in self.subs.get(event, []):
            fn(data)


# ---------- 커맨드: 요청을 값으로 ----------
@dataclass
class Site:
    """명령이 실행될 때 필요한 것들의 묶음."""
    inventory: Group
    robots: list[Robot]
    hub: EventHub
    route: Callable[[list[Bin]], list[Bin]]


@dataclass
class PickOrder:
    """[Concrete Command] 주문. 대기열에 있는 동안은 그냥 데이터라 취소할 수 있다."""
    key: str
    sku: str
    cancellable = True  # 클래스 속성: 취소 가능성은 명령 '종류'가 정한다

    def execute(self, site: Site) -> None:
        """배터리가 가장 많은 로봇이 경로대로 피킹한다. 배터리 판단은 하지 않고 '사실'만 알린다."""
        robot = max(site.robots, key=lambda r: r.driver.battery())
        for b in site.route([b for b in site.inventory.walk() if b.sku == self.sku])[:1]:
            robot.driver.go(b)
            b.qty -= 1
        site.hub.emit("robot.battery", robot=robot.name, pct=robot.driver.battery())


@dataclass
class ChargeRobot:
    """[Concrete Command] 충전. 주문과 같은 대기열을 타므로 명령 '사이'에서만 실행된다."""
    robot: str
    reason: str
    cancellable = False  # 안전 조치라 운영자가 취소할 수 없다

    @property
    def key(self) -> str:
        """취소·추적용 이름."""
        return f"charge-{self.robot}"

    def execute(self, site: Site) -> None:
        """해당 로봇을 충전한다. 사유가 실행 기록에 남는다."""
        robot = next(r for r in site.robots if r.name == self.robot)
        robot.driver.recharge()
        print(f"    충전 {self.robot} ({self.reason}) → {robot.driver.battery()}%")


class TaskQueue:
    """[Invoker] 명령을 쌓고 하나씩 실행한다. 명령의 구체 타입을 묻지 않는다."""
    def __init__(self) -> None:
        """대기 중인 명령."""
        self.pending: list[PickOrder | ChargeRobot] = []

    def submit(self, cmd: PickOrder | ChargeRobot, urgent: bool = False) -> None:
        """뒤에 붙이거나 맨 앞에 끼운다."""
        if urgent:  # 긴급(충전)은 다음 차례로 — 그래도 진행 중인 명령을 끊지는 않는다
            self.pending.insert(0, cmd)
        else:
            self.pending.append(cmd)

    def cancel(self, key: str) -> bool:
        """실행 전 명령을 뺀다. 취소 가능 여부는 명령 스스로 밝힌다."""
        before = len(self.pending)
        self.pending = [c for c in self.pending if not (c.key == key and c.cancellable)]
        return len(self.pending) < before

    def run_next(self, site: Site) -> str | None:
        """맨 앞 명령 하나를 실행하고 그 key를 돌려준다."""
        if not self.pending:
            return None
        cmd = self.pending.pop(0)
        cmd.execute(site)
        return cmd.key


class BatteryGuard:
    """[Observer → 커맨드 생성] 배터리 이벤트를 받아 충전 '명령'을 대기열 앞에 넣는다.

    왜 여기서 바로 충전하지 않는가: 통지가 주문 실행 도중에 올 수도 있다. 그 자리에서 충전하면
    프로토타입의 '주문 도중 충전' 사고가 된다. 명령으로 미루면 충전은 명령 사이에서만 일어난다.
    """
    def __init__(self, queue: TaskQueue, threshold: int = 30) -> None:
        """명령을 넣을 대기열과 기준값. '30% 미만이면 충전'이라는 정책은 이 객체만 안다."""
        self.queue, self.threshold = queue, threshold

    def __call__(self, e: dict) -> None:
        """함수처럼 구독된다."""
        if e["pct"] < self.threshold:
            self.queue.submit(ChargeRobot(e["robot"], f"배터리 {e['pct']}%"), urgent=True)


# ---------- 전략: 경로는 그냥 함수 ----------
def nearest_first(bins: list[Bin]) -> list[Bin]:
    """[Concrete Strategy] 입구(0,0)에서 가까운 칸부터."""
    return sorted(bins, key=lambda b: b.x + b.y)


def zone_sweep(bins: list[Bin]) -> list[Bin]:
    """[Concrete Strategy] 칸 코드 순서대로 쓸고 지나간다(유리 구역)."""
    return sorted(bins, key=lambda b: b.code)


ROUTES = {"nearest": nearest_first, "sweep": zone_sweep}


# ---------- 퍼사드 + 조립 ----------
class WarehouseOps:
    """[Facade] 운영 콘솔의 정문. 번호 발급 + 명령 제출, 대기열 비우기를 한 번에."""
    def __init__(self, site: Site, queue: TaskQueue) -> None:
        """조립된 부품을 받는다(만들지 않는다)."""
        self.site, self.queue, self.seq = site, queue, 0

    def order(self, sku: str) -> str:
        """주문 번호를 발급하고 명령을 제출한다."""
        self.seq += 1
        key = f"O-{self.seq}"
        self.queue.submit(PickOrder(key, sku))
        return key

    def run_all(self) -> list[str]:
        """대기열이 빌 때까지 실행한 순서."""
        done = []
        while (key := self.queue.run_next(self.site)) is not None:
            done.append(key)
        return done

    def stock(self, sku: str) -> int:
        """재고 집계 = 순회 위의 sum 한 줄."""
        return sum(b.qty for b in self.site.inventory.walk() if b.sku == sku)


def build(route: str) -> WarehouseOps:
    """모든 조립이 여기 한 곳. '하나'는 싱글턴이 아니라 여기서 하나 만들어 나눠 줘서 지킨다."""
    inventory = Group("창고", [
        Group("A", [Group("A1", [Bin("A1-01", "MUG", 5, 1, 1), Bin("A1-02", "CUP", 3, 9, 9)])]),
        Group("B", [Group("B1", [Group("B1-1", [Bin("B1-1-01", "MUG", 4, 3, 2)])])]),  # 신축 동: 한 단 더
    ])
    robots = [Robot("R1", AcmeAdapter(AcmeSDK())), Robot("R2", RoboKoAdapter(RoboKoSDK()))]
    hub, queue = EventHub(), TaskQueue()
    hub.on("robot.battery", lambda e: print(f"    [대시보드] {e['robot']} 배터리 {e['pct']}%"))
    hub.on("robot.battery", BatteryGuard(queue))
    return WarehouseOps(Site(inventory, robots, hub, ROUTES[route]), queue)


if __name__ == "__main__":
    ops = build("nearest")
    print(f"[1] 깊이가 다른 계층의 재고 집계: MUG {ops.stock('MUG')}개")

    print("[2] 주문 넷 접수, 하나 취소 — 아직 실행 전이라 가능")
    a, b, c, d = ops.order("MUG"), ops.order("CUP"), ops.order("MUG"), ops.order("CUP")
    print(f"  {b} 취소: {ops.queue.cancel(b)}")

    print("[3] 배터리 '이벤트'가 충전 '명령'이 되어 주문 사이에 끼어든다")
    print(f"  실행 순서: {ops.run_all()}")
    print(f"  남은 MUG {ops.stock('MUG')}개")

    print("[4] 경로 전략 교체는 조립 때 이름 하나")
    for name in ("nearest", "sweep"):
        site = build(name).site
        print(f"  {name}: {[x.code for x in site.route(list(site.inventory.walk()))]}")
