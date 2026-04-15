"""SpriteConvApp エントリポイント。

依存オブジェクトをここで組み立て（Composition Root）、アプリケーションを起動する。
"""

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from src.application.use_cases.convert_images_use_case import ConvertImagesUseCase
from src.application.use_cases.load_images_use_case import LoadImagesUseCase
from src.domain.services.image_converter import ImageConverter
from src.infra.image_file_loader import ImageFileLoader
from src.infra.settings_repository import SettingsRepository
from src.interface.main_window import MainWindow
from src.interface.view_models.main_view_model import MainViewModel

# 設定ファイルのパス
_CORE_SETTINGS_PATH: Path = Path("core_settings.yaml")
_USER_SETTINGS_PATH: Path = Path("user_settings.yaml")


def main() -> None:
    """アプリケーションのエントリポイント。

    依存関係を組み立ててメインウィンドウを起動する。
    """
    app = QApplication(sys.argv)
    app.setApplicationName("SpriteConvApp")

    # --- 依存オブジェクトの組み立て ---
    settings_repo = SettingsRepository(_CORE_SETTINGS_PATH, _USER_SETTINGS_PATH)
    loader = ImageFileLoader()
    converter = ImageConverter()
    load_uc = LoadImagesUseCase(loader)
    convert_uc = ConvertImagesUseCase(converter)
    view_model = MainViewModel(load_uc, convert_uc, settings_repo)

    # --- メインウィンドウの起動 ---
    window = MainWindow(view_model)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
