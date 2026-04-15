"""変換対象画像ファイルのエンティティモジュール。"""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ImageFile:
    """変換対象となる画像ファイルを表すエンティティ。

    Attributes:
        path: ファイルの絶対パス。
        format: Pillow が認識する画像フォーマット文字列 (例: "PNG", "JPEG")。
    """

    path: Path
    format: str

    @property
    def name(self) -> str:
        """ファイル名（拡張子あり）を返す。

        Returns:
            ファイル名文字列。
        """
        return self.path.name

    @property
    def stem(self) -> str:
        """ファイル名（拡張子なし）を返す。

        Returns:
            拡張子を除いたファイル名文字列。
        """
        return self.path.stem
