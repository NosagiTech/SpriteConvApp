"""画像ファイルを読み込むユースケースモジュール。"""

from pathlib import Path
from typing import Callable, Optional

from src.domain.entities.image_file import ImageFile
from src.domain.repositories.i_image_loader import IImageLoader


class LoadImagesUseCase:
    """ファイル / フォルダのパスリストから ImageFile リストを構築するユースケース。

    Args:
        loader: 画像を収集する IImageLoader の実装。
    """

    def __init__(self, loader: IImageLoader) -> None:
        """コンストラクタ。

        Args:
            loader: IImageLoader の実装インスタンス。
        """
        self._loader = loader

    def execute(
        self,
        path_list: list[Path],
        warning_cb: Optional[Callable[[str], None]] = None,
    ) -> list[ImageFile]:
        """パスリストを走査し、有効な ImageFile のリストを返す。

        無効なパス（存在しない・画像として開けない）はスキップし、
        warning_cb が指定されていれば警告メッセージを通知する。

        Args:
            path_list: 読み込むファイルまたはディレクトリのパスリスト。
            warning_cb: スキップ時に呼び出されるコールバック。省略可能。

        Returns:
            読み込みに成功した ImageFile のリスト（重複を除く）。
        """
        seen_paths: set[Path] = set()
        result: list[ImageFile] = []

        for path in path_list:
            try:
                images = self._loader.load_from_path(path)
            except FileNotFoundError as exc:
                if warning_cb:
                    warning_cb(f"[警告] {exc}")
                continue

            for image_file in images:
                if image_file.path in seen_paths:
                    continue
                seen_paths.add(image_file.path)
                result.append(image_file)

        return result
