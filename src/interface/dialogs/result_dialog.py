"""変換結果ダイアログモジュール。"""

from typing import Optional

from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from src.application.dto.conversion_result import ConversionResult
from src.interface.dialogs.error_list_dialog import ErrorListDialog


class ResultDialog(QDialog):
    """変換処理の完了を知らせるダイアログ。

    エラーが 1 件以上存在する場合は「エラー一覧を表示」ボタンも表示する。

    Args:
        result: 変換結果 DTO。
        parent: 親ウィジェット（省略可能）。
    """

    def __init__(
        self,
        result: ConversionResult,
        parent: Optional[QWidget] = None,
    ) -> None:
        """コンストラクタ。

        Args:
            result: 変換結果 DTO。
            parent: 親ウィジェット（省略可能）。
        """
        super().__init__(parent)
        self.setWindowTitle("変換完了")
        self._result = result
        self._build_ui()

    def _build_ui(self) -> None:
        """ウィジェットを生成してレイアウトに配置する。"""
        root_layout = QVBoxLayout(self)

        # --- サマリメッセージ ---
        msg = (
            f"変換が完了しました。\n\n"
            f"成功: {self._result.success_count} 件\n"
            f"失敗: {len(self._result.error_list)} 件"
        )
        root_layout.addWidget(QLabel(msg))

        # --- ボタン群 ---
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        button_box.accepted.connect(self.accept)

        if self._result.has_errors:
            btn_errors = QPushButton("エラー一覧を表示")
            btn_errors.clicked.connect(self._show_error_list)
            button_box.addButton(btn_errors, QDialogButtonBox.ButtonRole.ActionRole)

        root_layout.addWidget(button_box)

    def _show_error_list(self) -> None:
        """ErrorListDialog を開いてエラー一覧を表示する。"""
        dialog = ErrorListDialog(self._result.error_list, parent=self)
        dialog.exec()
