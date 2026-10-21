"""연습문제 3 해설: undo가 필요 없는 CLI 하위 명령에는 dict[str, Callable]로 충분하다.

상황: 사내 배포 도구 'shipit'에 status / deploy / logs 하위 명령이 있다. 각 명령은 한 번
실행되고 끝나며, 되돌리기·큐잉·로그 재생이 필요 없다. 커맨드 패턴의 '요청의 객체화'는
함수가 이미 해 준다 — 함수는 일급 객체라 dict에 담아 이름으로 고를 수 있다.
"""
from __future__ import annotations

from typing import Callable


def status(args: list[str]) -> None:
    """현재 배포 상태."""
    print("    prod: v1.4.2 (정상)")


def deploy(args: list[str]) -> None:
    """배포. 인자 파싱은 각 함수의 몫 — 실제로는 argparse 하위 파서를 쓴다."""
    print(f"    {args[0] if args else 'latest'} 배포 시작")


def logs(args: list[str]) -> None:
    """최근 로그."""
    print("    [12:00] deploy ok")


# 이름 → 함수. 새 하위 명령 = 함수 하나 + 이 줄 하나. 클래스 계층 없이 OCP를 만족한다.
COMMANDS: dict[str, Callable[[list[str]], None]] = {"status": status, "deploy": deploy, "logs": logs}


def main(argv: list[str]) -> int:
    """CLI 진입점. 알 수 없는 명령은 사용 가능한 목록과 함께 실패한다."""
    name, *rest = argv or ["status"]
    if name not in COMMANDS:
        print(f"    알 수 없는 명령 {name!r}. 가능: {', '.join(COMMANDS)}")
        return 2
    COMMANDS[name](rest)
    return 0


if __name__ == "__main__":
    for argv in (["status"], ["deploy", "v1.5.0"], ["rollback"]):
        print(f"$ shipit {' '.join(argv)}")
        main(argv)
