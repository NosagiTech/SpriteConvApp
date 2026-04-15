"""画像ローダのインタフェース定義モジュール。"""

from abc import ABC, abstractmethod
from pathlib import Path

from src.domain.entities.image_file import ImageFile


class IImageLoader(ABC):
    """ファイルシステムから画像を収集するローダの抽象基底クラス。"""

    @abstractmethod
    def load_from_path(self, path: Path) -> list[ImageFile]:
        """指定パスから ImageFile リストを構築して返す。

        パスがファイルの場合は 1 件、ディレクトリの場合は対象拡張子の
        ファイルを再帰的に収集して返す。

        Args:
            path: 読み込み対象のファイルまたはディレクトリのパス。

        Returns:
            ImageFile オブジェクトのリスト。
        """
