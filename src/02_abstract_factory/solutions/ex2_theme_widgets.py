"""연습문제 2 해설: if theme == "dark"로 위젯을 따로 만드는 CLI 코드를 추상 팩토리로.

상황: 사내 배포 도구의 CLI는 터미널 테마에 따라 Button과 Dialog를 다르게 그린다. 원래 코드는
버튼을 만드는 곳과 대화상자를 만드는 곳이 각자 `if theme == "dark"`를 검사했다(문제 본문).
그래서 한 곳이 테마 검사를 빠뜨리면 '다크 대화상자 안의 라이트 버튼'이 나왔다.
본문 클라우드 예제와 같은 구조다: 버튼·대화상자가 '함께 쓰여야 하는 제품군'이다.
"""
from __future__ import annotations

from abc import ABC, abstractmethod


class Button(ABC):
    """[Abstract Product] 버튼. 라벨은 버튼 자신의 상태다 — 버튼을 만드는 쪽(클라이언트)이 정한다."""

    def __init__(self, label: str) -> None:
        """라벨을 보관한다. 대화상자가 라벨을 정하면 '되돌리기' 같은 다른 버튼을 만들 수 없다."""
        self.label = label

    @abstractmethod
    def render(self) -> str:
        """버튼을 문자열로 그린다."""


class Dialog(ABC):
    """[Abstract Product] 대화상자. 버튼을 '안에 담는다' — 그래서 테마가 섞이면 눈에 띈다."""

    @abstractmethod
    def render(self, message: str, button: Button) -> str:
        """메시지와 버튼을 담은 대화상자를 그린다."""


class DarkButton(Button):
    """[Concrete Product] 다크 테마 버튼."""

    def render(self) -> str:
        """어두운 배경을 흉내 내 반전 괄호를 쓴다."""
        return f"▐ {self.label} ▌"


class LightButton(Button):
    """[Concrete Product] 라이트 테마 버튼."""

    def render(self) -> str:
        """밝은 테마는 평범한 대괄호."""
        return f"[ {self.label} ]"


class DarkDialog(Dialog):
    """[Concrete Product] 다크 테마 대화상자."""

    def render(self, message: str, button: Button) -> str:
        """두꺼운 테두리. 버튼은 추상 타입으로만 받고 그리기는 버튼에 맡긴다(라벨도 버튼의 것)."""
        return f"┏ {message} ┓  {button.render()}"


class LightDialog(Dialog):
    """[Concrete Product] 라이트 테마 대화상자."""

    def render(self, message: str, button: Button) -> str:
        """얇은 테두리."""
        return f"┌ {message} ┐  {button.render()}"


class WidgetFactory(ABC):
    """[Abstract Factory] 한 테마의 위젯 제품군."""

    @abstractmethod
    def create_button(self, label: str) -> Button:
        """테마에 맞는 버튼. 라벨(무엇을 하는 버튼인가)은 클라이언트가, 모양(테마)은 팩토리가 정한다."""

    @abstractmethod
    def create_dialog(self) -> Dialog:
        """테마에 맞는 대화상자."""


class DarkWidgets(WidgetFactory):
    """[Concrete Factory] 다크 제품군."""

    def create_button(self, label: str) -> Button:
        """다크 버튼."""
        return DarkButton(label)

    def create_dialog(self) -> Dialog:
        """다크 대화상자."""
        return DarkDialog()


class LightWidgets(WidgetFactory):
    """[Concrete Factory] 라이트 제품군."""

    def create_button(self, label: str) -> Button:
        """라이트 버튼."""
        return LightButton(label)

    def create_dialog(self) -> Dialog:
        """라이트 대화상자."""
        return LightDialog()


def confirm_deploy(widgets: WidgetFactory, target: str) -> str:
    """[Client] 배포 확인 화면. 테마를 묻는 if가 하나도 없다."""
    return widgets.create_dialog().render(f"{target}에 배포할까요?", widgets.create_button("확인"))


def confirm_rollback(widgets: WidgetFactory, target: str) -> str:
    """[Client] 되돌리기 확인 화면 — 원래 코드에서 버튼 테마를 "light"로 하드코딩했던 바로 그 함수.

    이제 테마 문자열을 받지 않고 팩토리만 받으므로, 버튼만 다른 테마로 만들 방법 자체가 없다.
    라벨("되돌리기")은 여전히 클라이언트가 자유롭게 정한다.
    """
    return widgets.create_dialog().render(f"{target}을 되돌릴까요?", widgets.create_button("되돌리기"))


# 테마 이름 → 팩토리. 테마 판단은 프로그램 시작 시 이 표 조회 한 번뿐이다.
THEMES: dict[str, type[WidgetFactory]] = {"dark": DarkWidgets, "light": LightWidgets}


if __name__ == "__main__":
    # 두 테마 × 두 클라이언트. 어느 조합에서도 대화상자와 버튼의 테마가 일치한다.
    for theme in ("dark", "light"):
        widgets = THEMES[theme]()
        print(f"[{theme:5}] 배포    {confirm_deploy(widgets, 'prod-seoul')}")
        print(f"[{theme:5}] 되돌리기 {confirm_rollback(widgets, 'prod-seoul')}")
