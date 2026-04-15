"""画像変換を実行するユースケースモジュール。"""

from pathlib import Path
from typing import Callable, Optional

from src.application.dto.conversion_result import ConversionResult
from src.application.dto.error_item import ErrorItem
from src.domain.entities.conversion_settings import ConversionSettings
from src.domain.entities.image_file import ImageFile
from src.domain.services.image_converter import ImageConverter


class ConvertImagesUseCase:
    """ImageFile リストを ConversionSettings に従って変換するユースケース。

    Args:
        converter: 画像変換ロジックを持つ ImageConverter サービス。
    """

    def __init__(self, converter: ImageConverter) -> None:
        """コンストラクタ。

        Args:
            converter: ImageConverter インスタンス。
        """
        self._converter = converter

    def execute(
        self,
        files: list[ImageFile],
        settings: ConversionSettings,
        output_dir: Path,
        progress_cb: Optional[Callable[[int, int], None]] = None,
    ) -> ConversionResult:
        """ファイルリストを 1 件ずつ変換し、結果を返す。

        変換中に例外が発生した場合はキャッチして ErrorItem として蓄積し、
        処理を継続する。

        Args:
            files: 変換対象の ImageFile リスト。
            settings: 変換設定。
            output_dir: 出力先ディレクトリ。
            progress_cb: 進捗通知コールバック ``progress_cb(current, total)``。省略可能。

        Returns:
            変換結果を格納した ConversionResult。
        """
        total = len(files)
        success_count = 0
        error_list: list[ErrorItem] = []

        for index, image_file in enumerate(files, start=1):
            try:
                self._converter.convert(image_file, settings, output_dir)
                success_count += 1
            except Exception as exc:  # noqa: BLE001
                error_list.append(
                    ErrorItem(
                        file_path=image_file.path,
                        error_message=str(exc),
                    )
                )
            finally:
                if progress_cb:
                    progress_cb(index, total)

        return ConversionResult(
            success_count=success_count,
            error_list=error_list,
        )
