"""패턴 조합: 로봇 창고 WMS — 변경 축마다 가장 가벼운 해법, 그리고 넣지 않은 패턴들.

상황: 02_naive_wms.py의 WMS 클래스에는 변경 축 여섯 개(제조사 SDK, 경로 알고리즘, 주문 대기·취소,
배터리 대응, 알림 채널, 재고 계층)가 묶여 있었다. 도윤의 팀은 "패턴을 몇 개 넣을까"가 아니라
"변경 축이 몇 개인가"부터 셌고, 축마다 가장 가벼운 해법을 골랐다.

변경 축 → 선택 (괄호는 교재의 장. 여섯 축에 일곱 패턴 — 컴포지트와 반복자가 한 축을 함께 맡는다)
- 제조사 SDK 모양이 다르다          → 어댑터(5): AcmeAdapter, RoboKoAdapter → RobotDriver(Protocol)
- 경로 알고리즘을 구역별로 바꾼다    → 전략(10): 그냥 함수(nearest_first, zone_sweep) + 이름표 dict
- 주문을 쌓고, 실행 전 취소한다     → 커맨드(12): PickOrder/ChargeRobot 객체 + TaskQueue(호출자)
- 알림 채널이 늘어난다              → 옵저버(11): EventHub에 콜러블 구독
- 재고 계층의 깊이가 바뀐다          → 컴포지트(7) + 반복자(15): Group/Bin, walk() 제너레이터
- 배터리 대응 정책                   → 새 패턴 없이 옵저버+커맨드 조합(11·12장이 이 장으로 미룬 것):
  배터리 '이벤트'를 받은 관찰자가 충전 '명령'을 만들어 대기열 앞에 넣는다(BatteryGuard docstring 참고).
02의 축이 아닌 별도 요구 하나: 운영 콘솔과 야간 배치가 '번호 발급+제출', '대기열 비우기' 흐름을 공유
→ 퍼사드(8): WarehouseOps.

넣지 않은 것: 상태 패턴(로봇 상태는 Enum 셋 — 행동 차이가 작다), 추상 팩토리(시뮬레이션/실환경은
'제품군'이 아니라 드라이버 하나의 차이 — 주입으로 충분), 싱글턴, 템플릿 메서드, 빌더, 데코레이터, 프록시.
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, ClassVar, Iterator, Protocol


# ===========================================================================
# 컴포지트 + 반복자 — 재고 계층
# ===========================================================================

@dataclass
class Bin:
    """[Leaf] 칸 하나. 재귀가 멈추는 곳."""

    code: str
    sku: str
    qty: int
    x: int
    y: int

    def walk(self) -> Iterator[Bin]:
        """자기 자신 하나를 내보낸다. Group과 같은 질문(walk)에 답하므로 클라이언트가 구별하지 않는다."""
        yield self


@dataclass
class Group:
    """[Composite] 구역·랙·선반 — 이름만 다르고 역할은 같으므로 클래스 하나로 충분하다.

    계층 단계마다 Zone/Rack/Shelf 클래스를 만들지 않은 이유: 7장 트레이드오프는 "깊이가 고정되고
    계층마다 역할이 다르면" 공통 인터페이스가 억지 메서드를 만든다고 경고했다. 여기는 그 반대 —
    계층마다 역할이 같고 깊이가 데이터로 바뀐다 — 이므로 단계별 클래스 대신 Group 하나가 맞다.
    """

    name: str
    children: list[Group | Bin] = field(default_factory=list)

    def walk(self) -> Iterator[Bin]:
        """[반복자] yield from 재귀 — 깊이가 몇 단이든 칸들의 평평한 스트림이 된다(15장)."""
        for child in self.children:
            yield from child.walk()


def stock(node: Group | Bin, sku: str) -> int:
    """재고 집계는 순회 위의 sum 한 줄. 02의 4중 반복문이 사라졌다."""
    return sum(b.qty for b in node.walk() if b.sku == sku)


# ===========================================================================
# 어댑터 — 두 제조사 SDK를 우리 인터페이스로
# ===========================================================================

class AcmeSDK:
    """[Adaptee] 제조사 A의 SDK: 좌표는 mm, 배터리는 0~100 정수. 우리가 고칠 수 없다."""

    def __init__(self) -> None:
        """시뮬레이션 상태."""
        self._battery = 45

    def goto(self, x_mm: int, y_mm: int) -> None:
        """mm 좌표로 이동한다. 이동마다 배터리가 준다."""
        self._battery -= 20

    def grab(self, bin_code: str) -> None:
        """칸 코드로 집는다."""

    def battery_pct(self) -> int:
        """남은 배터리(%)."""
        return self._battery

    def dock(self) -> None:
        """충전기에 도킹한다."""
        self._battery = 100


class RoboKoSDK:
    """[Adaptee] 제조사 B의 SDK: 칸 이름 문자열로 이동, 상태는 dict, 배터리는 0.0~1.0."""

    def __init__(self) -> None:
        """시뮬레이션 상태."""
        self._bat = 0.5

    def move(self, cell: str) -> None:
        """칸 이름으로 이동한다."""
        self._bat -= 0.15

    def pick(self, slot: int) -> None:
        """칸 안의 슬롯 번호로 집는다(칸 코드 끝 두 자리)."""

    def get_status(self) -> dict[str, float]:
        """상태 묶음."""
        return {"bat": self._bat}

    def charge(self) -> None:
        """충전한다."""
        self._bat = 1.0


class RobotDriver(Protocol):
    """[Target] 우리 도메인이 로봇에게 원하는 최소한(5장: 'SDK들의 공통분모'가 아니라 '우리가 알고 싶은 것')."""

    def go_and_pick(self, b: Bin) -> None:
        """칸으로 가서 하나 집는다."""
        ...

    def battery(self) -> int:
        """배터리(%) — 단위 차이는 어댑터가 흡수한다."""
        ...

    def recharge(self) -> None:
        """충전한다."""
        ...


class AcmeAdapter:
    """[Adapter] 칸 좌표(m)를 mm로 번역한다."""

    def __init__(self, sdk: AcmeSDK) -> None:
        """Adaptee를 합성으로 감싼다(객체 어댑터)."""
        self._sdk = sdk

    def go_and_pick(self, b: Bin) -> None:
        """이동 + 집기 두 호출을 우리 어휘 하나로."""
        self._sdk.goto(b.x * 1000, b.y * 1000)
        self._sdk.grab(b.code)

    def battery(self) -> int:
        """이미 % 정수다."""
        return self._sdk.battery_pct()

    def recharge(self) -> None:
        """도킹이 곧 충전."""
        self._sdk.dock()


class RoboKoAdapter:
    """[Adapter] 칸 코드를 이름/슬롯으로, 0~1 배터리를 %로 번역한다."""

    def __init__(self, sdk: RoboKoSDK) -> None:
        """Adaptee를 감싼다."""
        self._sdk = sdk

    def go_and_pick(self, b: Bin) -> None:
        """칸 이름으로 이동하고 슬롯 번호로 집는다."""
        self._sdk.move(b.code)
        self._sdk.pick(int(b.code[-2:]))

    def battery(self) -> int:
        """0.9 → 90. 반올림해 부동소수 오차(0.6000000001 같은)를 숨긴다."""
        return round(self._sdk.get_status()["bat"] * 100)

    def recharge(self) -> None:
        """충전."""
        self._sdk.charge()


# ===========================================================================
# 로봇 — 상태 패턴을 '쓰지 않은' 자리
# ===========================================================================

class Status(Enum):
    """로봇 상태. 상태별로 다른 것은 '받을 수 있는 작업인가' 하나뿐이라 Enum이면 충분하다(13장 6절)."""

    IDLE = "대기"
    BUSY = "작업"
    CHARGING = "충전"


@dataclass
class Robot:
    """로봇 하나 = 이름 + 드라이버(어댑터) + 상태."""

    name: str
    driver: RobotDriver
    status: Status = Status.IDLE


# ===========================================================================
# 옵저버 — 통지 허브
# ===========================================================================

Listener = Callable[[dict[str, object]], None]


class EventHub:
    """[Subject] 이벤트 이름별 콜러블 구독(11장 03의 단순판). 발행자는 구독자를 모른다."""

    def __init__(self) -> None:
        """이벤트 이름 → 구독자 목록."""
        self._subs: dict[str, list[Listener]] = defaultdict(list)

    def on(self, event: str, fn: Listener) -> None:
        """구독한다."""
        self._subs[event].append(fn)

    def emit(self, event: str, **data: object) -> None:
        """통지한다. 목록을 복사해 순회 — 통지 도중 구독이 바뀌어도 이번 통지는 흔들리지 않는다."""
        for fn in list(self._subs[event]):
            fn({"event": event, **data})


# ===========================================================================
# 커맨드 — 요청을 객체로: 대기, 취소, 우선 처리
# ===========================================================================

RoutePlanner = Callable[[tuple[int, int], list[Bin]], list[Bin]]


@dataclass
class Context:
    """명령이 실행될 때 필요한 것들. 명령이 수신자를 필드로 들지 않고 인자로 받게 하는 묶음(12장 5절)."""

    inventory: Group
    robots: list[Robot]
    hub: EventHub
    route: RoutePlanner


class Command(Protocol):
    """[Command] 실행 계약. 이 시스템에는 undo가 필요 없어 execute 하나다(피킹은 되돌릴 수 없는 물리 동작).

    key와 cancellable을 계약에 둔 이유: 호출자(TaskQueue)가 취소 여부를 판단할 때 구체 명령 타입을
    isinstance로 묻지 않게 하려는 것이다. 취소 가능성은 명령 자신이 밝힌다.
    """

    @property
    def key(self) -> str:
        """취소·추적에 쓰는 식별자."""
        ...

    @property
    def cancellable(self) -> bool:
        """대기 중에 취소할 수 있는가."""
        ...

    @property
    def label(self) -> str:
        """로그용 이름. 왜 실행되었는지도 담는다."""
        ...

    def execute(self, ctx: Context) -> None:
        """실행한다."""
        ...


@dataclass
class PickOrder:
    """[Concrete Command] 주문 하나. 대기열에 있는 동안은 그냥 데이터라서 취소할 수 있다."""

    order_id: str
    sku: str
    qty: int
    # ClassVar: 취소 가능성은 명령 '종류'의 성질이다. 인스턴스마다 바꿀 수 있는 생성자 인자가 되면 안 된다.
    cancellable: ClassVar[bool] = True  # 고객 요청이므로 출고 전이면 취소할 수 있다

    @property
    def key(self) -> str:
        """주문 번호가 곧 식별자."""
        return self.order_id

    @property
    def label(self) -> str:
        """로그용 이름."""
        return f"주문 {self.order_id}({self.sku}×{self.qty})"

    def execute(self, ctx: Context) -> None:
        """가장 배터리가 많은 대기 로봇에게 경로대로 피킹시킨다."""
        robot = max((r for r in ctx.robots if r.status is Status.IDLE), key=lambda r: r.driver.battery())
        candidates = [b for b in ctx.inventory.walk() if b.sku == self.sku and b.qty > 0]
        robot.status = Status.BUSY
        picked = 0
        for b in ctx.route((0, 0), candidates):  # [전략] 어떤 순서로 돌지는 주입된 함수가 정한다
            take = min(b.qty, self.qty - picked)
            for _ in range(take):  # 단순화: 한 번에 하나씩 집으며 매번 이동한다
                robot.driver.go_and_pick(b)
            b.qty -= take
            picked += take
            if picked == self.qty:
                break
        robot.status = Status.IDLE
        ctx.hub.emit("order.done", order=self.order_id, robot=robot.name, picked=picked)
        # 배터리 판단은 여기서 하지 않고 '사실'만 알린다. 대응 정책은 구독자의 몫이다.
        ctx.hub.emit("robot.battery", robot=robot.name, pct=robot.driver.battery())


@dataclass
class ChargeRobot:
    """[Concrete Command] 충전. 주문과 같은 대기열을 타므로 명령 '사이'에서만 실행된다.

    reason을 필드로 둔 이유: 실행 이력(label)에 '왜 충전했는가'가 남게 하려는 것이다.
    cancellable=False로 정한 이유: 배터리 부족 충전은 안전 조치라 운영자의 일반 취소 대상이 아니다.
    """

    robot_name: str
    reason: str
    cancellable: ClassVar[bool] = False  # ClassVar라 호출자가 ChargeRobot(..., cancellable=True)로 뒤집을 수 없다

    @property
    def key(self) -> str:
        """로봇별 충전 식별자."""
        return f"charge-{self.robot_name}"

    @property
    def label(self) -> str:
        """로그용 이름 + 사유."""
        return f"충전 {self.robot_name}({self.reason})"

    def execute(self, ctx: Context) -> None:
        """해당 로봇을 충전한다."""
        robot = next(r for r in ctx.robots if r.name == self.robot_name)
        robot.status = Status.CHARGING
        robot.driver.recharge()
        robot.status = Status.IDLE
        ctx.hub.emit("robot.charged", robot=robot.name, pct=robot.driver.battery())


class TaskQueue:
    """[Invoker] 명령을 쌓고 하나씩 실행한다. 명령의 구체 타입을 모른다 — key/cancellable/label만 본다."""

    def __init__(self) -> None:
        """대기 중인 명령들."""
        self._pending: list[Command] = []

    def submit(self, cmd: Command, *, urgent: bool = False) -> None:
        """뒤에 붙이거나(일반), 맨 앞에 끼운다(긴급)."""
        if urgent:
            self._pending.insert(0, cmd)
        else:
            self._pending.append(cmd)

    def cancel(self, key: str) -> bool:
        """아직 실행되지 않은 명령을 뺀다. 요청이 객체이기 때문에 가능한 일(02에서는 불가능했다).

        취소할 수 없다고 스스로 밝힌 명령(cancellable=False)은 남겨 두고 False를 돌려준다.
        """
        before = len(self._pending)
        self._pending = [c for c in self._pending if not (c.key == key and c.cancellable)]
        return len(self._pending) < before

    def run_next(self, ctx: Context) -> Command | None:
        """맨 앞 명령 하나를 실행한다."""
        if not self._pending:
            return None
        cmd = self._pending.pop(0)
        cmd.execute(ctx)
        return cmd

    def labels(self) -> list[str]:
        """대기열 미리보기."""
        return [c.label for c in self._pending]


# ===========================================================================
# 옵저버 + 커맨드 — 이벤트를 받아 '명령을 만든다'
# ===========================================================================

class BatteryGuard:
    """[Concrete Observer → Client of Command] 배터리 이벤트를 받아 충전 명령을 대기열 앞에 넣는다.

    왜 여기서 바로 robot.driver.recharge()를 부르지 않는가? (설계 근거 — 아래 1)은 이 데모 출력이
    직접 보여 주는 것이 아니다. 지금 PickOrder는 execute의 맨 끝에서 통지하므로 직접 충전해도 충전 시점은
    주문 사이로 같다. 달라지는 것은 실행 이력에 충전 항목·사유가 남지 않고, ChargeRobot이 내던 robot.charged
    이벤트(대시보드의 "충전 완료" 줄)도 나오지 않는다는 점이다.)
    1) 재진입: 관찰자는 통지가 발행자 실행의 어느 시점에 오는지 알 수 없다. 발행자가 피킹마다 배터리를
       알리도록 바뀌면 직접 충전은 곧바로 02의 '주문 처리 도중 충전' 사고가 된다. 명령으로 미루면 발행
       시점과 무관하게 '명령 사이'에서만 충전된다.
    2) 일관성: 충전도 명령이 되면 대기열·우선순위·실행 이력을 주문과 같은 경로로 타고, 사유가 이력에 남는다.
    3) 정책 분리: '몇 % 미만이면 충전'은 이 관찰자만 안다. 발행자(PickOrder)는 사실만 알린다.
    """

    def __init__(self, queue: TaskQueue, threshold: int = 30) -> None:
        """명령을 넣을 대기열과 임계값."""
        self.queue = queue
        self.threshold = threshold

    def __call__(self, e: dict[str, object]) -> None:
        """콜러블 관찰자. 임계값 미만이면 긴급 충전 명령을 만든다."""
        pct = e["pct"]
        if isinstance(pct, int) and pct < self.threshold:
            reason = f"배터리 {pct}% < {self.threshold}%"
            self.queue.submit(ChargeRobot(str(e["robot"]), reason), urgent=True)


# ===========================================================================
# 전략 — 경로 알고리즘은 그냥 함수
# ===========================================================================

def nearest_first(start: tuple[int, int], bins: list[Bin]) -> list[Bin]:
    """[Concrete Strategy] 출발점에서 맨해튼 거리가 가까운 칸부터."""
    return sorted(bins, key=lambda b: abs(b.x - start[0]) + abs(b.y - start[1]))


def zone_sweep(start: tuple[int, int], bins: list[Bin]) -> list[Bin]:
    """[Concrete Strategy] 칸 코드 순서대로 구역을 쓸고 지나간다(통로 혼잡이 적다)."""
    return sorted(bins, key=lambda b: b.code)


ROUTES: dict[str, RoutePlanner] = {"nearest": nearest_first, "sweep": zone_sweep}


# ===========================================================================
# 퍼사드 — 운영자용 정문
# ===========================================================================

class WarehouseOps:
    """[Facade] 운영 콘솔과 야간 배치가 공유하는 단순한 API. 서브시스템(대기열·허브·재고)은 숨기지 않는다(8장).

    퍼사드의 몫은 공유되는 흐름인 order()(번호 발급 + 명령 생성·제출)와 run_all()(대기열 비우기)이다.
    cancel()과 stock()은 한 줄 위임에 가까운 편의 메서드로, 8장 기준으로는 퍼사드의 가치가 아니다.
    """

    def __init__(self, ctx: Context, queue: TaskQueue) -> None:
        """조립된 서브시스템들을 받는다(생성은 composition root의 일)."""
        self.ctx, self.queue = ctx, queue
        self._seq = 0

    def order(self, sku: str, qty: int) -> str:
        """주문을 접수하고 주문 번호를 돌려준다. 운영자는 커맨드 객체를 몰라도 된다."""
        self._seq += 1
        oid = f"O-{self._seq:03d}"
        self.queue.submit(PickOrder(oid, sku, qty))
        return oid

    def cancel(self, key: str) -> bool:
        """명령 취소. 주문이면 주문 번호가 key다. 취소 불가 명령은 False."""
        return self.queue.cancel(key)

    def run_all(self) -> list[str]:
        """대기열을 비울 때까지 실행하고, 실행된 명령 이름을 돌려준다."""
        done = []
        while (cmd := self.queue.run_next(self.ctx)) is not None:
            done.append(cmd.label)
        return done

    def stock(self, sku: str) -> int:
        """창고 전체 재고."""
        return stock(self.ctx.inventory, sku)


# ===========================================================================
# Composition root — 모든 조립이 여기 한 곳
# ===========================================================================

def build(route: str) -> WarehouseOps:
    """창고를 조립한다. 싱글턴 없이 '하나'는 여기서 하나 만들어 나눠 주는 것으로 보장한다(4장)."""
    inventory = Group("창고", [
        Group("A", [Group("A1", [Group("A1-1", [Bin("A1-1-01", "MUG", 5, 1, 1), Bin("A1-1-02", "CUP", 3, 2, 1)])])]),
        Group("B", [Group("B1", [Group("B1-1", [Bin("B1-1-01", "MUG", 4, 8, 6)]),
                                 Group("B1-2", [Bin("B1-2-01", "PLATE", 9, 9, 6)])])]),
    ])
    robots = [Robot("R1", AcmeAdapter(AcmeSDK())), Robot("R2", RoboKoAdapter(RoboKoSDK()))]
    hub, queue = EventHub(), TaskQueue()
    ctx = Context(inventory, robots, hub, ROUTES[route])
    # 구독 배선도 조립의 일부다. 누가 무엇을 듣는지가 이 몇 줄에 다 보인다.
    hub.on("order.done", lambda e: print(f"    [대시보드] {e['order']} 완료: {e['robot']}가 {e['picked']}개"))
    hub.on("robot.battery", lambda e: print(f"    [대시보드] {e['robot']} 배터리 {e['pct']}%"))
    hub.on("robot.battery", BatteryGuard(queue))
    hub.on("robot.charged", lambda e: print(f"    [대시보드] {e['robot']} 충전 완료 {e['pct']}%"))
    return WarehouseOps(ctx, queue)


if __name__ == "__main__":
    ops = build(route="nearest")
    print("[1] 재고 조회 — 계층 깊이와 무관한 집계(컴포지트 + 반복자)")
    print(f"  MUG {ops.stock('MUG')}개, PLATE {ops.stock('PLATE')}개")

    print("\n[2] 주문 세 건 접수 후 하나 취소 — 아직 실행 전이라 가능(커맨드)")
    a, b, c = ops.order("MUG", 2), ops.order("PLATE", 1), ops.order("CUP", 1)
    print(f"  {b} 취소: {ops.cancel(b)} / 대기열: {ops.queue.labels()}")

    print("\n[3] 실행 — 배터리 경고 '이벤트'가 충전 '명령'이 되어 대기열 앞에 끼어든다(옵저버 + 커맨드)")
    executed = ops.run_all()
    print(f"  실행 순서: {executed}")
    print(f"  남은 MUG {ops.stock('MUG')}개")

    print("\n[4] 충전 명령은 스스로 '취소 불가'를 밝힌다 — 호출자는 타입을 묻지 않고 cancellable만 본다")
    ops.queue.submit(ChargeRobot("R1", "안전: 배터리 셀 온도 경고 후 보호 충전"))
    print(f"  charge-R1 취소 시도: {ops.cancel('charge-R1')} / 대기열: {ops.queue.labels()}")
    print(f"  실행: {ops.run_all()}")

    print("\n[5] 경로 전략 교체는 조립 시점의 이름 하나 — 같은 주문, 다른 방문 순서")
    for route in ("nearest", "sweep"):
        o = build(route)
        order = [x.code for x in o.ctx.route((9, 9), [bn for bn in o.ctx.inventory.walk() if bn.sku == "MUG"])]
        print(f"  {route:7}: (9,9)에서 출발한 MUG 방문 순서 {order}")
