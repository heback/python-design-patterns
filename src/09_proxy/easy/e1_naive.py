"""09 프록시 — 순진한 코드: 만들자마자 원본을 받는 영상 객체와, 화면에 흩어진 검사.

상황: 위성 사진 뷰어의 SatelliteImage는 외부 라이브러리 클래스라 고칠 수 없고,
만들어지는 순간 400MB 원본을 받는다. 목록 화면에 사진 2,000장을 올리자 전부 다운로드된다.
수아는 목록 화면에 "권한 있나? 이미 받았나?" 검사를 직접 넣었다.
"""
from __future__ import annotations


class RemoteArchive:
    """원격 사진 저장소. 받을 때마다 400MB가 든다고 가정하고 누적량을 센다."""

    def __init__(self) -> None:
        """누적 다운로드량(MB)."""
        self.downloaded_mb = 0

    def fetch(self, image_id: str) -> bytes:
        """원본 다운로드 흉내."""
        self.downloaded_mb += 400
        return f"<원본 {image_id}>".encode()


class SatelliteImage:
    """외부 라이브러리의 위성 사진(고칠 수 없다)."""

    def __init__(self, image_id: str, title: str, secret: bool, archive: RemoteArchive) -> None:
        """사진 정보를 받고 원본도 곧바로 받는다."""
        self.image_id, self.title, self.secret = image_id, title, secret
        # ⚠ 문제: 목록에 올리려고 만들기만 해도 400MB를 받는다.
        self._data = archive.fetch(image_id)

    def zoom(self, region: str) -> str:
        """확대 렌더링."""
        return f"{self.title} [{region}] 확대"


class CatalogScreen:
    """목록 화면. 권한·재사용 검사를 스스로 한다."""

    def __init__(self) -> None:
        """⚠ 문제: 캐시가 이 화면의 필드라 다른 화면(비교 뷰)과 나눠 쓰지 못한다."""
        self._opened: dict[str, SatelliteImage] = {}

    def open(self, img: SatelliteImage, user_can_see_secret: bool) -> str:
        """확대해서 보여 준다."""
        # ⚠ 문제: 권한 검사가 이 화면에만 있다. 비교 뷰 담당자는 복사하는 것을 잊었다.
        if img.secret and not user_can_see_secret:
            return "권한 없음"
        self._opened.setdefault(img.image_id, img)
        return img.zoom("중심부")


if __name__ == "__main__":
    archive = RemoteArchive()
    print("[1] 목록에 사진 2,000장을 올린다(제목만 보여 줄 생각이었다)")
    images = [SatelliteImage(f"K3-{i:04}", f"동해안 {i}", i % 7 == 0, archive) for i in range(2000)]
    print(f"    다운로드 누적: {archive.downloaded_mb:,}MB")
    print("[2] 화면이 검사를 떠안아 '해결'한 모습")
    screen = CatalogScreen()
    print(f"    분석관: {screen.open(images[0], True)} / 인턴: {screen.open(images[0], False)}")
