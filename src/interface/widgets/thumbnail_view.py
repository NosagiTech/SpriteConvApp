"""サムネイルグリッドウィジェットモジュール。"""

from pathlib import Path
from typing import Optional

from PySide6.QtCore import QRunnable, QSize, Qt, QThreadPool, Signal, QObject
from PySide6.QtGui import QDesktopServices, QIcon, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QScrollArea,
    QSizePolicy,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from src.domain.entities.image_file import ImageFile

# サムネイルのデフォルトサイズ（px）
_THUMBNAIL_SIZE: int = 128
# グリッド列数（ウィンドウ幅に応じて変わらない固定値）
_GRID_COLUMNS: int = 4


class _ThumbnailLoadSignals(QObject):
    """サムネイル読み込みスレッドからメインスレッドへのシグナル定義。"""

    loaded = Signal(int, QPixmap)   # (インデックス, ピクセルマップ)


class _ThumbnailLoadTask(QRunnable):
    """QThreadPool で実行するサムネイル読み込みタスク。

    Args:
        index: 対応するサムネイルのインデックス。
        path: 読み込む画像ファイルのパス。
        size: サムネイルの最大サイズ（正方形）。
    """

    def __init__(self, index: int, path: Path, size: int) -> None:
        """コンストラクタ。

        Args:
            index: 対応するサムネイルのインデックス。
            path: 読み込む画像ファイルのパス。
            size: サムネイルの最大サイズ。
        """
        super().__init__()
        self.signals = _ThumbnailLoadSignals()
        self._index = index
        self._path = path
        self._size = size

    def run(self) -> None:
        """画像をスケールして QPixmap を生成し、loaded シグナルを発火する。"""
        pixmap = QPixmap(str(self._path))
        if not pixmap.isNull():
            pixmap = pixmap.scaled(
                QSize(self._size, self._size),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        self.signals.loaded.emit(self._index, pixmap)


class _ThumbnailButton(QToolButton):
    """1 枚の画像に対応するサムネイルボタン。

    クリックすると OS 標準ビュアーでファイルを開く。

    Args:
        image_file: 対応する ImageFile エンティティ。
        size: サムネイルの表示サイズ。
    """

    def __init__(self, image_file: ImageFile, size: int, parent=None) -> None:
        """コンストラクタ。

        Args:
            image_file: 対応する ImageFile エンティティ。
            size: サムネイルの表示サイズ。
            parent: 親ウィジェット（省略可能）。
        """
        super().__init__(parent)
        self._image_file = image_file
        self.setFixedSize(size + 8, size + 24)
        self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.setIconSize(QSize(size, size))
        self.setText(image_file.name[:16] + ("..." if len(image_file.name) > 16 else ""))
        self.setToolTip(str(image_file.path))
        self.clicked.connect(self._open_file)

    def set_pixmap(self, pixmap: QPixmap) -> None:
        """ロード済みサムネイルを設定する。

        Args:
            pixmap: 表示する QPixmap。
        """
        if not pixmap.isNull():
            self.setIcon(QIcon(pixmap))

    def _open_file(self) -> None:
        """OS 標準ビュアーでファイルを開く。"""
        from PySide6.QtCore import QUrl
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(self._image_file.path)))


class _FlowLayout(QVBoxLayout):
    """簡易フロー風レイアウト（横に並べて折り返す QVBoxLayout ラッパ）。

    実際には QWidget + 行ごとの QHBoxLayout をネストして実現する。
    """


class ThumbnailView(QScrollArea):
    """サムネイルをグリッド状に表示するスクロールエリアウィジェット。

    画像の読み込みは QThreadPool でバックグラウンド実行し、
    完了時にサムネイルを逐次更新する。
    """

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """コンストラクタ。

        Args:
            parent: 親ウィジェット（省略可能）。
        """
        super().__init__(parent)
        self.setWidgetResizable(True)

        self._container = QWidget()
        self.setWidget(self._container)

        from PySide6.QtWidgets import QGridLayout
        self._grid = QGridLayout(self._container)
        self._grid.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        self._buttons: list[_ThumbnailButton] = []
        self._thread_pool = QThreadPool.globalInstance()

    def set_images(self, image_files: list[ImageFile]) -> None:
        """画像リストをセットし、サムネイルグリッドを再構築する。

        既存のサムネイルをクリアした後、各ファイルのロードタスクを起動する。

        Args:
            image_files: 表示する ImageFile リスト。
        """
        self._clear_grid()
        self._buttons = []

        for index, image_file in enumerate(image_files):
            btn = _ThumbnailButton(image_file, _THUMBNAIL_SIZE)
            row = index // _GRID_COLUMNS
            col = index % _GRID_COLUMNS
            self._grid.addWidget(btn, row, col)
            self._buttons.append(btn)

            task = _ThumbnailLoadTask(index, image_file.path, _THUMBNAIL_SIZE)
            task.signals.loaded.connect(self._on_thumbnail_loaded)
            self._thread_pool.start(task)

    def _on_thumbnail_loaded(self, index: int, pixmap: QPixmap) -> None:
        """バックグラウンドでロードされたサムネイルをボタンへ適用する。

        Args:
            index: 対応するボタンのインデックス。
            pixmap: ロード済みの QPixmap。
        """
        if 0 <= index < len(self._buttons):
            self._buttons[index].set_pixmap(pixmap)

    def _clear_grid(self) -> None:
        """グリッド内の全ウィジェットを削除する。"""
        while self._grid.count():
            item = self._grid.takeAt(0)
            if item and item.widget():
                item.widget().deleteLater()
