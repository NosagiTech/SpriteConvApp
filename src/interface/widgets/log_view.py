"""ログ表示ウィジェットモジュール。"""

from PySide6.QtWidgets import QPlainTextEdit


class LogView(QPlainTextEdit):
    """処理ログを表示する読み取り専用ウィジェット。

    折り返しあり・縦スクロールバー付きで、常に末尾へ自動スクロールする。
    """

    def __init__(self, parent=None) -> None:
        """コンストラクタ。

        Args:
            parent: 親ウィジェット（省略可能）。
        """
        super().__init__(parent)
        self.setReadOnly(True)
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.WidgetWidth)
        self.setPlaceholderText("ログがここに表示されます...")

    def append_log(self, message: str) -> None:
        """ログメッセージを末尾に追記し、自動スクロールする。

        Args:
            message: 追加するログ文字列。
        """
        self.appendPlainText(message)
        # 常に末尾にスクロール
        scrollbar = self.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
