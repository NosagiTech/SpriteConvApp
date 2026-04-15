"""画像変換処理の結果を表す DTO モジュール。"""

from dataclasses import dataclass, field

from src.application.dto.error_item import ErrorItem


@dataclass(frozen=True)
class ConversionResult:
    """画像変換処理全体の結果を保持する DTO。

    Attributes:
        success_count: 正常に変換できたファイル数。
        error_list: 変換に失敗したファイルのエラー情報リスト。
    """

    success_count: int
    error_list: list[ErrorItem] = field(default_factory=list)

    @property
    def has_errors(self) -> bool:
        """エラーが 1 件以上存在するかを返す。

        Returns:
            エラーありなら True。
        """
        return len(self.error_list) > 0

    @property
    def total_count(self) -> int:
        """処理を試みたファイルの総数を返す。

        Returns:
            成功数 + エラー数。
        """
        return self.success_count + len(self.error_list)
