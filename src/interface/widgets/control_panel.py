"""左コントロールパネルウィジェットモジュール。"""

from pathlib import Path
from typing import Optional

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFileDialog,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from src.domain.entities.conversion_settings import SUPPORTED_OUTPUT_FORMATS
from src.domain.value_objects.color import Color
from src.interface.dialogs.color_picker_dialog import ColorPickerDialog


class ControlPanel(QWidget):
    """操作系 UI をまとめた左パネルウィジェット。

    シグナル:
        files_selected(list[Path]): ファイル / フォルダ選択時に発火。
        output_dir_selected(Path): 出力先フォルダ選択時に発火。
        format_changed(str): 出力フォーマット変更時に発火。
        scale_changed(float): 倍率変更時に発火。
        antialias_changed(bool): アンチエイリアス変更時に発火。
        transparency_color_changed(object): 透過色変更時に発火（Color or None）。
        execute_clicked(): 実行ボタン押下時に発火。
    """

    files_selected = Signal(list)         # list[Path]
    output_dir_selected = Signal(Path)
    format_changed = Signal(str)
    scale_changed = Signal(float)
    antialias_changed = Signal(bool)
    transparency_color_changed = Signal(object)   # Color | None
    execute_clicked = Signal()

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """コンストラクタ。

        Args:
            parent: 親ウィジェット（省略可能）。
        """
        super().__init__(parent)
        self._current_transparency_color: Optional[Color] = None
        self._build_ui()
        self._connect_signals()
        self._update_transparency_button_state()

    # ------------------------------------------------------------------
    # UI 構築
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        """ウィジェットを生成してレイアウトに配置する。"""
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(8, 8, 8, 8)

        root_layout.addWidget(self._build_input_group())
        root_layout.addWidget(self._build_output_group())
        root_layout.addWidget(self._build_format_group())
        root_layout.addWidget(self._build_scale_group())
        root_layout.addStretch()
        root_layout.addWidget(self._build_execute_button())

    def _build_input_group(self) -> QGroupBox:
        """入力ファイル / フォルダ指定グループを構築する。"""
        group = QGroupBox("入力")
        layout = QVBoxLayout(group)

        self._input_path_edit = QLineEdit()
        self._input_path_edit.setReadOnly(True)
        self._input_path_edit.setPlaceholderText("ファイルまたはフォルダを選択...")

        btn_row = QHBoxLayout()
        btn_files = QPushButton("ファイルを追加")
        btn_folder = QPushButton("フォルダを追加")
        btn_row.addWidget(btn_files)
        btn_row.addWidget(btn_folder)

        self._btn_files = btn_files
        self._btn_folder = btn_folder

        layout.addWidget(self._input_path_edit)
        layout.addLayout(btn_row)
        return group

    def _build_output_group(self) -> QGroupBox:
        """出力先フォルダ指定グループを構築する。"""
        group = QGroupBox("出力先")
        layout = QVBoxLayout(group)

        self._output_path_edit = QLineEdit()
        self._output_path_edit.setReadOnly(True)
        self._output_path_edit.setPlaceholderText("出力先フォルダを選択...")

        self._btn_output = QPushButton("フォルダを選択")

        layout.addWidget(self._output_path_edit)
        layout.addWidget(self._btn_output)
        return group

    def _build_format_group(self) -> QGroupBox:
        """出力フォーマット・透過色グループを構築する。"""
        group = QGroupBox("フォーマット")
        layout = QVBoxLayout(group)

        # 出力フォーマット選択
        fmt_row = QHBoxLayout()
        fmt_row.addWidget(QLabel("出力形式:"))
        self._combo_format = QComboBox()
        self._combo_format.addItems(SUPPORTED_OUTPUT_FORMATS)
        fmt_row.addWidget(self._combo_format)
        layout.addLayout(fmt_row)

        # 透過色指定
        transparency_row = QHBoxLayout()
        self._btn_transparency = QPushButton("透過色を指定")
        self._transparency_preview = QLabel()
        self._transparency_preview.setFixedSize(24, 24)
        self._transparency_preview.setFrameShape(QFrame.Shape.Box)
        self._btn_clear_transparency = QPushButton("クリア")
        transparency_row.addWidget(self._btn_transparency)
        transparency_row.addWidget(self._transparency_preview)
        transparency_row.addWidget(self._btn_clear_transparency)
        layout.addLayout(transparency_row)

        return group

    def _build_scale_group(self) -> QGroupBox:
        """倍率・アンチエイリアスグループを構築する。"""
        group = QGroupBox("リサイズ")
        layout = QVBoxLayout(group)

        scale_row = QHBoxLayout()
        scale_row.addWidget(QLabel("倍率:"))
        self._spin_scale = QDoubleSpinBox()
        self._spin_scale.setRange(0.01, 100.0)
        self._spin_scale.setSingleStep(0.1)
        self._spin_scale.setDecimals(2)
        self._spin_scale.setValue(1.0)
        scale_row.addWidget(self._spin_scale)
        layout.addLayout(scale_row)

        self._chk_antialias = QCheckBox("アンチエイリアスを使用")
        self._chk_antialias.setChecked(True)
        layout.addWidget(self._chk_antialias)

        return group

    def _build_execute_button(self) -> QPushButton:
        """実行ボタンを生成して返す。"""
        self._btn_execute = QPushButton("変換実行")
        self._btn_execute.setMinimumHeight(36)
        return self._btn_execute

    # ------------------------------------------------------------------
    # シグナル接続
    # ------------------------------------------------------------------

    def _connect_signals(self) -> None:
        """各ウィジェットのシグナルをスロットへ接続する。"""
        self._btn_files.clicked.connect(self._on_files_clicked)
        self._btn_folder.clicked.connect(self._on_folder_clicked)
        self._btn_output.clicked.connect(self._on_output_clicked)
        self._combo_format.currentTextChanged.connect(self._on_format_changed)
        self._spin_scale.valueChanged.connect(self.scale_changed)
        self._chk_antialias.toggled.connect(self.antialias_changed)
        self._btn_transparency.clicked.connect(self._on_transparency_clicked)
        self._btn_clear_transparency.clicked.connect(self._on_clear_transparency)
        self._btn_execute.clicked.connect(self.execute_clicked)

    # ------------------------------------------------------------------
    # スロット
    # ------------------------------------------------------------------

    def _on_files_clicked(self) -> None:
        """ファイル選択ダイアログを開き、選択パスリストを発火する。"""
        paths, _ = QFileDialog.getOpenFileNames(
            self,
            "画像ファイルを選択",
            "",
            "画像ファイル (*.png *.jpg *.jpeg *.tiff *.tif *.gif *.bmp);;すべてのファイル (*)",
        )
        if paths:
            path_objects = [Path(p) for p in paths]
            self._input_path_edit.setText("; ".join(paths))
            self.files_selected.emit(path_objects)

    def _on_folder_clicked(self) -> None:
        """フォルダ選択ダイアログを開き、選択パスリストを発火する。"""
        folder = QFileDialog.getExistingDirectory(self, "フォルダを選択")
        if folder:
            self._input_path_edit.setText(folder)
            self.files_selected.emit([Path(folder)])

    def _on_output_clicked(self) -> None:
        """出力先フォルダ選択ダイアログを開き、選択パスを発火する。"""
        folder = QFileDialog.getExistingDirectory(self, "出力先フォルダを選択")
        if folder:
            self._output_path_edit.setText(folder)
            self.output_dir_selected.emit(Path(folder))

    def _on_format_changed(self, fmt: str) -> None:
        """フォーマット変更時に透過色ボタンの有効状態を更新してシグナルを発火する。

        Args:
            fmt: 新しく選択されたフォーマット文字列。
        """
        self._update_transparency_button_state()
        self.format_changed.emit(fmt)

    def _on_transparency_clicked(self) -> None:
        """ColorPickerDialog を開き、選択色を ViewModel へ通知する。"""
        dialog = ColorPickerDialog(self._current_transparency_color, parent=self)
        if dialog.exec() and dialog.selected_color is not None:
            self._current_transparency_color = dialog.selected_color
            self._update_transparency_preview()
            self.transparency_color_changed.emit(self._current_transparency_color)

    def _on_clear_transparency(self) -> None:
        """透過色をクリアして ViewModel へ通知する。"""
        self._current_transparency_color = None
        self._update_transparency_preview()
        self.transparency_color_changed.emit(None)

    # ------------------------------------------------------------------
    # UI 状態の更新
    # ------------------------------------------------------------------

    def _update_transparency_button_state(self) -> None:
        """現在のフォーマットが PNG の場合のみ透過色ボタンを有効にする。"""
        is_png = self._combo_format.currentText() == "PNG"
        self._btn_transparency.setEnabled(is_png)
        self._btn_clear_transparency.setEnabled(is_png)

    def _update_transparency_preview(self) -> None:
        """透過色プレビューラベルを現在の色で更新する。"""
        from PySide6.QtGui import QColor, QPixmap
        if self._current_transparency_color is None:
            self._transparency_preview.clear()
            return
        c = self._current_transparency_color
        pixmap = QPixmap(24, 24)
        pixmap.fill(QColor(c.r, c.g, c.b))
        self._transparency_preview.setPixmap(pixmap)

    # ------------------------------------------------------------------
    # 外部からの状態適用
    # ------------------------------------------------------------------

    def apply_settings(
        self,
        output_format: str,
        scale: float,
        use_antialias: bool,
        transparency_color: Optional[Color],
        output_dir: Optional[Path],
    ) -> None:
        """ViewModel から復元した設定を各 UI ウィジェットへ反映する。

        シグナルを発火させずに値のみ更新する。

        Args:
            output_format: 出力フォーマット文字列。
            scale: 倍率。
            use_antialias: アンチエイリアスフラグ。
            transparency_color: 透過色、または None。
            output_dir: 出力先ディレクトリ、または None。
        """
        # シグナルを一時的にブロックして UI を更新
        self._combo_format.blockSignals(True)
        self._spin_scale.blockSignals(True)
        self._chk_antialias.blockSignals(True)

        idx = self._combo_format.findText(output_format)
        if idx >= 0:
            self._combo_format.setCurrentIndex(idx)

        self._spin_scale.setValue(scale)
        self._chk_antialias.setChecked(use_antialias)
        self._current_transparency_color = transparency_color
        self._update_transparency_preview()
        self._update_transparency_button_state()

        if output_dir:
            self._output_path_edit.setText(str(output_dir))

        self._combo_format.blockSignals(False)
        self._spin_scale.blockSignals(False)
        self._chk_antialias.blockSignals(False)
