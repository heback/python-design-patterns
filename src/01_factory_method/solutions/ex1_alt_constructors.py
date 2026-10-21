"""연습문제 1 해설: datetime.fromtimestamp, dict.fromkeys는 GoF 팩토리 메서드인가?

상황: 표준 라이브러리 문서와 블로그는 classmethod 대체 생성자를 흔히 '팩토리 메서드'라고
부른다. 이 파일은 두 메서드의 동작을 실험으로 확인하고, GoF의 의도 —
"Creator의 연산이 생성 훅을 호출하고, 무엇을 만들지는 Creator의 서브클래스가 결정한다" —
에 비추어 판별한다.

결론 요약: 둘 다 GoF 팩토리 메서드가 아니라 '대체 생성자(alternative constructor)'다.
- 생성될 클래스는 '호출자가 고른 수신 클래스(cls)'로 정해진다. 하위 클래스가 생성
  결정을 오버라이드하는 훅이 아니다.
- 생성 결과를 사용하는 Creator 쪽 연산(02의 run()에 해당)이 없다. 메서드의 목적이
  '다른 입력 형식으로 같은 타입을 만든다'는 데 있다.
공통점은 하나다: cls를 통해 생성하므로 하위 클래스에서 호출하면 하위 클래스 인스턴스가 나온다.
"""
from __future__ import annotations

from datetime import datetime, timezone


class LabTimestamp(datetime):
    """datetime 하위 클래스. fromtimestamp가 어떤 클래스를 만드는지 확인하려는 실험체."""

    def label(self) -> str:
        """연구실 기록용 표기. 하위 클래스에만 있는 메서드로, 반환 타입 확인에 쓴다."""
        return self.strftime("LAB-%Y%m%d-%H%M")


class CountingDict(dict):
    """dict 하위 클래스. fromkeys 실험체."""

    def total(self) -> int:
        """값의 합. 하위 클래스 전용 메서드."""
        return sum(self.values())


if __name__ == "__main__":
    print("[1] 하위 클래스에서 호출하면 하위 클래스 인스턴스가 나온다 (cls 다형성)")
    ts = LabTimestamp.fromtimestamp(0, tz=timezone.utc)
    print(f"  {type(ts).__name__}.fromtimestamp → {type(ts).__name__}, label={ts.label()}")
    counts = CountingDict.fromkeys(["UV-Vis", "MS", "XRD"], 0)
    print(f"  {type(counts).__name__}.fromkeys → {type(counts).__name__}, total={counts.total()}")

    print("\n[2] 그러나 '무엇을 만들지'는 호출자가 수신 클래스를 고르는 순간 이미 정해졌다")
    print("  datetime.fromtimestamp(...)를 부르는 코드는 datetime을 원한다고 직접 말한 셈이다.")
    print("  GoF처럼 '프레임워크 흐름 → 훅 호출 → 하위 클래스가 선택'하는 간접층이 없다.")

    print("\n[3] 이 메서드들의 실제 목적: 같은 타입을 '다른 입력'에서 만들기")
    print(f"  datetime(1970,1,1,tzinfo=utc) == datetime.fromtimestamp(0, utc) → "
          f"{datetime(1970, 1, 1, tzinfo=timezone.utc) == datetime.fromtimestamp(0, tz=timezone.utc)}")
    print("  → 생성자 오버로딩이 없는 파이썬에서 '이름 붙은 생성자'를 만드는 관용구다.")
