"""変換エラー 1 件を表す DTO モジュール。"""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ErrorItem:
    """画像変換処理で発生したエラー 1 件を保持する DTO。

    Attributes:
        file_path: エラーが発生したファイルのパス。
        error_message: エラーの内容を示す文字列。
    """

    file_path: Path
    error_message: str
