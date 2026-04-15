"""メイン画面の ViewModel モジュール。

UI 層とアプリケーション層を Qt シグナルで橋渡しする。
"""

import threading
from pathlib import Path
from typing import Any, Optional

from PySide6.QtCore import QObject, Signal

from src.application.dto.conversion_result import ConversionResult
from src.application.use_cases.convert_images_use_case import ConvertImagesUseCase
from src.application.use_cases.load_images_use_case import LoadImagesUseCase
from src.domain.entities.conversion_settings import (
    SUPPORTED_OUTPUT_FORMATS,
    ConversionSettings,
)
from src.domain.entities.image_file import ImageFile
from src.domain.repositories.i_settings_repository import ISettingsRepository
from src.domain.value_objects.color import Color

# ユーザ設定キー定数
_KEY_OUTPUT_FORMAT: str = "output_format"
_KEY_SCALE: str = "scale"
_KEY_USE_ANTIALIAS: str = "use_antialias"
_KEY_TRANSPARENCY_COLOR: str = "transparency_color"
_KEY_OUTPUT_DIR: str = "output_dir"

# デフォルト値
_DEFAULT_OUTPUT_FORMAT: str = "PNG"
_DEFAULT_SCALE: float = 1.0
_DEFAULT_USE_ANTIALIAS: bool = True


class MainViewModel(QObject):
    """UI とアプリケーション層を繋ぐ ViewModel。

    Qt シグナルを通じてスレッドセーフに UI へ状態変化を通知する。

    Args:
        load_uc: 画像読み込みユースケース。
        convert_uc: 画像変換ユースケース。
        settings_repo: 設定リポジトリ。
    """

    # シグナル定義
    progress_updated = Signal(int, int)          # (current, total)
    conversion_finished = Signal(object)         # ConversionResult
    images_loaded = Signal(list)                 # list[ImageFile]
    log_message = Signal(str)                    # ログ文字列

    def __init__(
        self,
        load_uc: LoadImagesUseCase,
        convert_uc: ConvertImagesUseCase,
        settings_repo: ISettingsRepository,
        parent: Optional[QObject] = None,
    ) -> None:
        """コンストラクタ。

        Args:
            load_uc: LoadImagesUseCase インスタンス。
            convert_uc: ConvertImagesUseCase インスタンス。
            settings_repo: ISettingsRepository の実装インスタンス。
            parent: 親 QObject（省略可能）。
        """
        super().__init__(parent)
        self._load_uc = load_uc
        self._convert_uc = convert_uc
        self._settings_repo = settings_repo

        self._image_files: list[ImageFile] = []
        self._output_dir: Optional[Path] = None
        self._settings = ConversionSettings()
        self._is_converting: bool = False

        self._restore_user_settings()

    # ------------------------------------------------------------------
    # プロパティ
    # ------------------------------------------------------------------

    @property
    def image_files(self) -> list[ImageFile]:
        """現在読み込まれている ImageFile リスト。"""
        return self._image_files

    @property
    def output_dir(self) -> Optional[Path]:
        """出力先ディレクトリ。"""
        return self._output_dir

    @property
    def settings(self) -> ConversionSettings:
        """現在の変換設定。"""
        return self._settings

    @property
    def is_converting(self) -> bool:
        """変換処理が実行中かどうか。"""
        return self._is_converting

    # ------------------------------------------------------------------
    # 画像読み込み
    # ------------------------------------------------------------------

    def load_images(self, path_list: list[Path]) -> None:
        """指定パスリストから画像を読み込み、images_loaded シグナルを発火する。

        Args:
            path_list: 読み込むファイル / ディレクトリのパスリスト。
        """
        self.log_message.emit("画像を読み込んでいます...")
        images = self._load_uc.execute(
            path_list,
            warning_cb=lambda msg: self.log_message.emit(msg),
        )
        self._image_files = images
        self.images_loaded.emit(images)
        self.log_message.emit(f"{len(images)} 件の画像を読み込みました。")

    # ------------------------------------------------------------------
    # 設定変更
    # ------------------------------------------------------------------

    def set_output_dir(self, path: Path) -> None:
        """出力先ディレクトリを更新する。

        Args:
            path: 新しい出力先ディレクトリのパス。
        """
        self._output_dir = path
        self._save_user_settings()

    def set_output_format(self, fmt: str) -> None:
        """出力フォーマットを更新する。

        Args:
            fmt: 新しい出力フォーマット文字列（例: "PNG"）。
        """
        self._update_settings(output_format=fmt)

    def set_scale(self, scale: float) -> None:
        """変換倍率を更新する。

        Args:
            scale: 新しい倍率。
        """
        self._update_settings(scale=scale)

    def set_use_antialias(self, use_antialias: bool) -> None:
        """アンチエイリアスフラグを更新する。

        Args:
            use_antialias: アンチエイリアスを使用するか。
        """
        self._update_settings(use_antialias=use_antialias)

    def set_transparency_color(self, color: Optional[Color]) -> None:
        """透過色を更新する。

        Args:
            color: 透過色の Color、または None（透過処理なし）。
        """
        self._update_settings(transparency_color=color)

    def set_tolerance(self, tolerance: int) -> None:
        """透過色の許容誤差を更新する。

        Args:
            tolerance: 新しい許容誤差 (0〜255)。
        """
        self._update_settings(tolerance=tolerance)

    # ------------------------------------------------------------------
    # 変換実行
    # ------------------------------------------------------------------

    def start_conversion(self) -> None:
        """画像変換をバックグラウンドスレッドで開始する。

        変換中に呼び出した場合は無視する。
        入力画像・出力先が未設定の場合はログへ警告を出す。
        """
        if self._is_converting:
            return
        if not self._image_files:
            self.log_message.emit("[警告] 読み込まれた画像がありません。")
            return
        if self._output_dir is None:
            self.log_message.emit("[警告] 出力先フォルダが設定されていません。")
            return

        self._is_converting = True
        self.log_message.emit("変換を開始します...")

        thread = threading.Thread(target=self._run_conversion, daemon=True)
        thread.start()

    def _run_conversion(self) -> None:
        """変換処理の本体（バックグラウンドスレッドで実行）。"""
        try:
            result: ConversionResult = self._convert_uc.execute(
                files=self._image_files,
                settings=self._settings,
                output_dir=self._output_dir,  # type: ignore[arg-type]
                progress_cb=lambda cur, tot: self.progress_updated.emit(cur, tot),
            )
            self.log_message.emit(
                f"変換完了: 成功 {result.success_count} 件 / エラー {len(result.error_list)} 件"
            )
            self.conversion_finished.emit(result)
        except Exception as exc:  # noqa: BLE001
            self.log_message.emit(f"[エラー] 変換処理で予期しない例外が発生しました: {exc}")
        finally:
            self._is_converting = False

    # ------------------------------------------------------------------
    # ユーザ設定の保存 / 復元
    # ------------------------------------------------------------------

    def _save_user_settings(self) -> None:
        """現在の設定状態をユーザ設定ファイルへ書き出す。"""
        color = self._settings.transparency_color
        color_data: Optional[dict[str, int]] = (
            {"r": color.r, "g": color.g, "b": color.b} if color else None
        )
        data: dict[str, Any] = {
            _KEY_OUTPUT_FORMAT: self._settings.output_format,
            _KEY_SCALE: self._settings.scale,
            _KEY_USE_ANTIALIAS: self._settings.use_antialias,
            _KEY_TRANSPARENCY_COLOR: color_data,
            _KEY_OUTPUT_DIR: str(self._output_dir) if self._output_dir else "",
        }
        self._settings_repo.save_user_settings(data)

    def _restore_user_settings(self) -> None:
        """ユーザ設定ファイルから前回の設定を復元する。"""
        data = self._settings_repo.load_user_settings()
        if not data:
            return

        fmt = data.get(_KEY_OUTPUT_FORMAT, _DEFAULT_OUTPUT_FORMAT)
        if fmt not in SUPPORTED_OUTPUT_FORMATS:
            fmt = _DEFAULT_OUTPUT_FORMAT

        scale = float(data.get(_KEY_SCALE, _DEFAULT_SCALE))
        use_antialias = bool(data.get(_KEY_USE_ANTIALIAS, _DEFAULT_USE_ANTIALIAS))

        color: Optional[Color] = None
        color_data = data.get(_KEY_TRANSPARENCY_COLOR)
        if isinstance(color_data, dict):
            try:
                color = Color(
                    r=int(color_data.get("r", 0)),
                    g=int(color_data.get("g", 0)),
                    b=int(color_data.get("b", 0)),
                )
            except ValueError:
                color = None

        output_dir_str: str = data.get(_KEY_OUTPUT_DIR, "")
        self._output_dir = Path(output_dir_str) if output_dir_str else None

        try:
            self._settings = ConversionSettings(
                output_format=fmt,
                scale=scale,
                use_antialias=use_antialias,
                transparency_color=color,
            )
        except ValueError:
            self._settings = ConversionSettings()

    def _update_settings(self, **kwargs: Any) -> None:
        """現在の設定に変更を加えた新しい ConversionSettings を生成し保存する。

        Args:
            **kwargs: 変更するフィールド名と新しい値。
        """
        current = {
            "output_format": self._settings.output_format,
            "scale": self._settings.scale,
            "use_antialias": self._settings.use_antialias,
            "transparency_color": self._settings.transparency_color,
            "tolerance": self._settings.tolerance,
        }
        current.update(kwargs)
        try:
            self._settings = ConversionSettings(**current)
        except ValueError as exc:
            self.log_message.emit(f"[警告] 設定値が不正です: {exc}")
        self._save_user_settings()
