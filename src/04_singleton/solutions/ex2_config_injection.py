"""연습문제 2 해설: Config.instance()를 직접 부르는 세 모듈을 생성자 주입으로 바꾸고 테스트에서 가짜 설정을 넣는다.

상황: EMR의 병동 알림 기능은 세 모듈(병상 배정, 투약 알림, 야간 당직 호출)이 각자 메서드 안에서
Config.instance()로 설정을 꺼내 썼다(문제 본문). 그래서 "야간 시간대에 투약 알림이 몇 분 전에
나가는가"를 테스트하려면 전역 설정 객체의 값을 바꿨다가 되돌려야 했다.

해설의 단계:
1. 모듈이 실제로 필요로 하는 것만 담은 좁은 설정 타입(WardSettings)을 정의한다.
2. 각 모듈은 생성자에서 그것을 받는다. Config.instance() 호출은 모듈에서 사라진다.
3. 운영 composition root만 실제 설정을 읽어 주입한다. 테스트는 원하는 값으로 직접 만든다.
"""
from __future__ import annotations

from dataclasses import dataclass, replace


@dataclass(frozen=True)
class WardSettings:
    """병동 알림에 필요한 설정만 담은 값 객체.

    전역 Config 전체를 넘기지 않는 이유: 모듈이 '무엇에' 의존하는지 타입이 정확히 말하게 하려는 것이다
    (인터페이스 분리 원칙). frozen이라 한 모듈이 설정을 바꿔 다른 모듈에 영향을 주는 일도 없다.
    """

    beds_per_ward: int
    med_alert_minutes: int
    night_start_hour: int


class BedAssigner:
    """병상 배정 모듈."""

    def __init__(self, settings: WardSettings) -> None:
        """설정을 주입받는다 — 전역 접근이 사라졌다."""
        self.settings = settings

    def has_room(self, occupied: int) -> bool:
        """남은 병상이 있는가."""
        return occupied < self.settings.beds_per_ward


class MedicationAlert:
    """투약 알림 모듈."""

    def __init__(self, settings: WardSettings) -> None:
        """설정을 주입받는다."""
        self.settings = settings

    def alert_at(self, dose_minute: int) -> int:
        """투약 시각(자정 기준 분) 몇 분 전에 알릴지. 야간에는 두 배 일찍 알린다."""
        lead = self.settings.med_alert_minutes
        if dose_minute // 60 >= self.settings.night_start_hour:
            lead *= 2  # 야간 인력이 적어 준비 시간이 더 필요하다는 병동 규칙
        return dose_minute - lead


class NightCall:
    """야간 당직 호출 모듈."""

    def __init__(self, settings: WardSettings) -> None:
        """설정을 주입받는다."""
        self.settings = settings

    def is_night(self, hour: int) -> bool:
        """야간 시간대인가."""
        return hour >= self.settings.night_start_hour


def load_settings_from_config_file() -> WardSettings:
    """[Composition Root 일부] 운영에서는 설정 파일·환경 변수를 읽는다. 예제에서는 고정값."""
    return WardSettings(beds_per_ward=30, med_alert_minutes=15, night_start_hour=22)


if __name__ == "__main__":
    print("[1] 운영: 설정을 한 번 읽어 세 모듈에 나눠 준다")
    settings = load_settings_from_config_file()
    beds, meds, night = BedAssigner(settings), MedicationAlert(settings), NightCall(settings)
    print(f"  병상 여유(28명 입원)? {beds.has_room(28)}, 23:00 투약 알림 시각(분): {meds.alert_at(23 * 60)}, "
          f"23시는 야간? {night.is_night(23)}")

    print("\n[2] 테스트: 전역 상태를 건드리지 않고 경계값만 바꾼 가짜 설정을 넣는다")
    # replace로 '운영 설정에서 하나만 바꾼' 테스트 설정을 만든다. 원래 settings는 그대로다.
    early_night = replace(settings, night_start_hour=20)
    assert MedicationAlert(early_night).alert_at(21 * 60) == 21 * 60 - 30
    assert MedicationAlert(settings).alert_at(21 * 60) == 21 * 60 - 15
    print("  야간 시작 20시 설정: 21시 투약은 30분 전 알림 — 통과")
    print("  운영 설정(22시)은 영향받지 않음: 21시 투약은 15분 전 알림 — 통과")
