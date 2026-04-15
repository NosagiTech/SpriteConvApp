"""エラー一覧ダイアログモジュール。"""

import subprocess
import sys
from typing import Optional

from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from src.application.dto.error_item import ErrorItem

# テーブルの列インデックス
_COL_FILE_NAME: int = 0
_COL_ERROR_MSG: int = 1
_COL_PATH: int = 2
_COL_OPEN_EXPLORER: int = 3

# テーブル列ヘッダ
_HEADERS: list[str] = ["ファイル名", "エラー内容", "パス", ""]


class ErrorListDialog(QDialog):
    """変換エラー一覧を表示するダイアログ。

    Args:
        error_list: 表示する ErrorItem のリスト。
        parent: 親ウィジェット（省略可能）。
    """

    def __init__(
        self,
        error_list: list[ErrorItem],
        parent: Optional[QWidget] = None,
    ) -> None:
        """コンストラクタ。

        Args:
            error_list: 表示する ErrorItem のリスト。
            parent: 親ウィジェット（省略可能）。
        """
        super().__init__(parent)
        self.setWindowTitle("エラー一覧")
        self.setMinimumSize(720, 400)
        self._error_list = error_list
        self._build_ui()

    def _build_ui(self) -> None:
        """ウィジェットを生成してレイアウトに配置する。"""
        root_layout = QVBoxLayout(self)

        summary = QLabel(f"変換に失敗したファイルが {len(self._error_list)} 件あります。")
        root_layout.addWidget(summary)

        # --- テーブル ---
        table = QTableWidget(len(self._error_list), len(_HEADERS), self)
        table.setHorizontalHeaderLabels(_HEADERS)
        table.horizontalHeader().setSectionResizeMode(
            _COL_ERROR_MSG, QHeaderView.ResizeMode.Stretch
        )
        table.horizontalHeader().setSectionResizeMode(
            _COL_PATH, QHeaderView.ResizeMode.Stretch
        )
        table.verticalHeader().setVisible(False)

        for row, item in enumerate(self._error_list):
            table.setItem(row, _COL_FILE_NAME, QTableWidgetItem(item.file_path.name))
            table.setItem(row, _COL_ERROR_MSG, QTableWidgetItem(item.error_message))
            table.setItem(row, _COL_PATH, QTableWidgetItem(str(item.file_path)))

            # 「エクスプローラで開く」ボタン
            btn = QPushButton("開く")
            btn.clicked.connect(
                lambda checked, p=item.file_path: self._open_in_explorer(p)
            )
            cell_widget = QWidget()
            cell_layout = QHBoxLayout(cell_widget)
            cell_layout.addWidget(btn)
            cell_layout.setContentsMargins(4, 2, 4, 2)
            table.setCellWidget(row, _COL_OPEN_EXPLORER, cell_widget)

        root_layout.addWidget(table)

        # --- 閉じるボタン ---
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        button_box.rejected.connect(self.reject)
        root_layout.addWidget(button_box)

    @staticmethod
    def _open_in_explorer(path) -> None:
        """OS 標準のファイルマネージャでファイルの親フォルダを開く。

        Args:
            path: 対象ファイルのパス。
        """
        parent_dir = path.parent
        if sys.platform == "win32":
            subprocess.Popen(["explorer", str(parent_dir)])
        elif sys.platform == "darwin":
            subprocess.Popen(["open", str(parent_dir)])
        else:
            subprocess.Popen(["xdg-open", str(parent_dir)])
