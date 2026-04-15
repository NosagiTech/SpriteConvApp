"""透過色指定ダイアログモジュール。"""

from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPixmap
from PySide6.QtWidgets import (
    QColorDialog,
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from src.domain.value_objects.color import Color

# プレビューラベルのサイズ
_PREVIEW_SIZE: int = 48


class ColorPickerDialog(QDialog):
    """RGB 値と HSV カラーピッカーで透過色を指定するダイアログ。

    Attributes:
        selected_color: ダイアログ確定後の Color バリューオブジェクト。None なら未選択。
    """

    def __init__(
        self,
        initial_color: Optional[Color] = None,
        parent: Optional[QWidget] = None,
    ) -> None:
        """コンストラクタ。

        Args:
            initial_color: ダイアログを開いた時点の初期色。省略時は白。
            parent: 親ウィジェット（省略可能）。
        """
        super().__init__(parent)
        self.setWindowTitle("透過色の指定")
        self.setModal(True)

        self.selected_color: Optional[Color] = None
        init = initial_color or Color(255, 255, 255)
        self._current_qcolor = QColor(init.r, init.g, init.b)

        self._build_ui()
        self._update_preview()

    # ------------------------------------------------------------------
    # UI 構築
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        """ウィジェットを生成してレイアウトに配置する。"""
        root_layout = QVBoxLayout(self)

        # --- RGB スピンボックス行 ---
        rgb_layout = QHBoxLayout()
        self._spin_r = self._make_spin(label="R", value=self._current_qcolor.red())
        self._spin_g = self._make_spin(label="G", value=self._current_qcolor.green())
        self._spin_b = self._make_spin(label="B", value=self._current_qcolor.blue())

        for label_text, spin in (("R", self._spin_r), ("G", self._spin_g), ("B", self._spin_b)):
            lbl = QLabel(label_text)
            rgb_layout.addWidget(lbl)
            rgb_layout.addWidget(spin)

        root_layout.addLayout(rgb_layout)

        # --- カラーピッカーボタン + プレビュー ---
        picker_layout = QHBoxLayout()
        self._preview_label = QLabel()
        self._preview_label.setFixedSize(_PREVIEW_SIZE, _PREVIEW_SIZE)
        self._preview_label.setFrameShape(QLabel.Shape.Box)

        btn_picker = QPushButton("カラーピッカーで選択")
        btn_picker.clicked.connect(self._open_color_dialog)

        picker_layout.addWidget(self._preview_label)
        picker_layout.addWidget(btn_picker)
        root_layout.addLayout(picker_layout)

        # --- ボタンボックス ---
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self._on_accepted)
        button_box.rejected.connect(self.reject)
        root_layout.addWidget(button_box)

    @staticmethod
    def _make_spin(label: str, value: int) -> QSpinBox:
        """0〜255 の範囲を持つスピンボックスを生成する。

        Args:
            label: アクセシビリティ用のラベル文字列。
            value: 初期値。

        Returns:
            設定済み QSpinBox。
        """
        spin = QSpinBox()
        spin.setRange(0, 255)
        spin.setValue(value)
        spin.setAccessibleName(label)
        return spin

    # ------------------------------------------------------------------
    # スロット
    # ------------------------------------------------------------------

    def _open_color_dialog(self) -> None:
        """QColorDialog を開き、選択色をスピンボックスとプレビューへ反映する。"""
        color = QColorDialog.getColor(self._current_qcolor, self, "色を選択")
        if not color.isValid():
            return
        self._current_qcolor = color
        self._spin_r.setValue(color.red())
        self._spin_g.setValue(color.green())
        self._spin_b.setValue(color.blue())
        self._update_preview()

    def _update_preview(self) -> None:
        """プレビューラベルの背景色を現在の QColor で更新する。"""
        r = self._spin_r.value()
        g = self._spin_g.value()
        b = self._spin_b.value()
        pixmap = QPixmap(_PREVIEW_SIZE, _PREVIEW_SIZE)
        pixmap.fill(QColor(r, g, b))
        self._preview_label.setPixmap(pixmap)

    def _on_accepted(self) -> None:
        """OK ボタン押下時にスピンボックスの値から Color を確定し、ダイアログを閉じる。"""
        try:
            self.selected_color = Color(
                r=self._spin_r.value(),
                g=self._spin_g.value(),
                b=self._spin_b.value(),
            )
        except ValueError:
            self.selected_color = None
        self.accept()
