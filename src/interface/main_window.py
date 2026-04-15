"""メインウィンドウモジュール。"""

from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QMainWindow,
    QProgressBar,
    QSplitter,
    QStatusBar,
    QWidget,
)

from src.application.dto.conversion_result import ConversionResult
from src.domain.entities.image_file import ImageFile
from src.interface.dialogs.result_dialog import ResultDialog
from src.interface.view_models.main_view_model import MainViewModel
from src.interface.widgets.control_panel import ControlPanel
from src.interface.widgets.log_view import LogView
from src.interface.widgets.thumbnail_view import ThumbnailView

# ウィンドウのデフォルトサイズ
_DEFAULT_WIDTH: int = 1100
_DEFAULT_HEIGHT: int = 700


class MainWindow(QMainWindow):
    """アプリケーションのメインウィンドウ。

    水平 QSplitter で左コントロールパネルと右コンテンツエリアを分割し、
    右エリアはさらに垂直 QSplitter でサムネイルビューとログビューに分割する。

    Args:
        view_model: UI 操作を仲介する MainViewModel。
        parent: 親ウィジェット（省略可能）。
    """

    def __init__(
        self,
        view_model: MainViewModel,
        parent: Optional[QWidget] = None,
    ) -> None:
        """コンストラクタ。

        Args:
            view_model: MainViewModel インスタンス。
            parent: 親ウィジェット（省略可能）。
        """
        super().__init__(parent)
        self._vm = view_model
        self.setWindowTitle("SpriteConvApp - 画像一括変換ツール")
        self.resize(_DEFAULT_WIDTH, _DEFAULT_HEIGHT)

        self._build_ui()
        self._connect_view_model()
        self._restore_ui_from_view_model()

    # ------------------------------------------------------------------
    # UI 構築
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        """メインウィンドウのレイアウトを構築する。"""
        # 左パネル
        self._control_panel = ControlPanel()

        # 右上: サムネイルビュー
        self._thumbnail_view = ThumbnailView()

        # 右下: ログビュー
        self._log_view = LogView()

        # 右: 縦スプリッタ
        right_splitter = QSplitter(Qt.Orientation.Vertical)
        right_splitter.addWidget(self._thumbnail_view)
        right_splitter.addWidget(self._log_view)
        right_splitter.setStretchFactor(0, 3)
        right_splitter.setStretchFactor(1, 1)

        # 全体: 横スプリッタ
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        main_splitter.addWidget(self._control_panel)
        main_splitter.addWidget(right_splitter)
        main_splitter.setStretchFactor(0, 0)
        main_splitter.setStretchFactor(1, 1)
        main_splitter.setSizes([280, _DEFAULT_WIDTH - 280])

        self.setCentralWidget(main_splitter)

        # ステータスバー + プログレスバー
        self._progress_bar = QProgressBar()
        self._progress_bar.setVisible(False)
        self._progress_bar.setMaximumWidth(200)
        status_bar: QStatusBar = self.statusBar()
        status_bar.addPermanentWidget(self._progress_bar)

    # ------------------------------------------------------------------
    # シグナル接続
    # ------------------------------------------------------------------

    def _connect_view_model(self) -> None:
        """ViewModel のシグナルと UI スロットを接続する。"""
        # ViewModel → View
        self._vm.images_loaded.connect(self._on_images_loaded)
        self._vm.log_message.connect(self._log_view.append_log)
        self._vm.progress_updated.connect(self._on_progress_updated)
        self._vm.conversion_finished.connect(self._on_conversion_finished)

        # View → ViewModel
        self._control_panel.files_selected.connect(self._vm.load_images)
        self._control_panel.output_dir_selected.connect(self._vm.set_output_dir)
        self._control_panel.format_changed.connect(self._vm.set_output_format)
        self._control_panel.scale_changed.connect(self._vm.set_scale)
        self._control_panel.antialias_changed.connect(self._vm.set_use_antialias)
        self._control_panel.transparency_color_changed.connect(
            self._vm.set_transparency_color
        )
        self._control_panel.execute_clicked.connect(self._vm.start_conversion)

    def _restore_ui_from_view_model(self) -> None:
        """ViewModel が保持する前回設定を ControlPanel に反映する。"""
        s = self._vm.settings
        self._control_panel.apply_settings(
            output_format=s.output_format,
            scale=s.scale,
            use_antialias=s.use_antialias,
            transparency_color=s.transparency_color,
            output_dir=self._vm.output_dir,
        )

    # ------------------------------------------------------------------
    # スロット
    # ------------------------------------------------------------------

    def _on_images_loaded(self, images: list[ImageFile]) -> None:
        """画像読み込み完了時にサムネイルビューを更新する。

        Args:
            images: 読み込まれた ImageFile のリスト。
        """
        self._thumbnail_view.set_images(images)

    def _on_progress_updated(self, current: int, total: int) -> None:
        """変換進捗に応じてプログレスバーを更新する。

        Args:
            current: 完了したファイル数。
            total: 全ファイル数。
        """
        self._progress_bar.setVisible(True)
        self._progress_bar.setMaximum(total)
        self._progress_bar.setValue(current)

    def _on_conversion_finished(self, result: ConversionResult) -> None:
        """変換完了後にプログレスバーを非表示にして結果ダイアログを表示する。

        Args:
            result: 変換結果 DTO。
        """
        self._progress_bar.setVisible(False)
        dialog = ResultDialog(result, parent=self)
        dialog.exec()
