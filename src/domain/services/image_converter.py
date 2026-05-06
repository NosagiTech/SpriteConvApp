"""Pillow を用いた画像変換サービスモジュール。"""

from pathlib import Path

from PIL import Image

from src.domain.entities.conversion_settings import ConversionSettings
from src.domain.entities.image_file import ImageFile

# GIF フレームのインデックス（先頭フレームのみを処理する）
_GIF_FRAME_INDEX: int = 0

# JPEG 保存時に RGBA → RGB 変換後に使用する背景色
_JPEG_BACKGROUND_COLOR: tuple[int, int, int] = (255, 255, 255)

# フォーマットと拡張子のマッピング
_FORMAT_TO_EXTENSION: dict[str, str] = {
    "PNG": ".png",
    "JPEG": ".jpg",
    "TIFF": ".tiff",
    "GIF": ".gif",
    "BMP": ".bmp",
}


class ImageConverter:
    """Pillow を使用して画像の変換・リサイズ・透過処理を行うサービスクラス。"""

    def convert(
        self,
        image_file: ImageFile,
        settings: ConversionSettings,
        output_dir: Path,
    ) -> Path:
        """画像ファイルを変換し、出力ディレクトリに保存する。

        Args:
            image_file: 変換対象の ImageFile エンティティ。
            settings: 変換設定。
            output_dir: 変換後ファイルの保存先ディレクトリ。

        Returns:
            保存された出力ファイルの Path。

        Raises:
            OSError: ファイルの読み書きに失敗した場合。
            ValueError: 未対応フォーマットが指定された場合。
        """
        img = self._load_image(image_file)
        img = self._apply_transparency(img, settings)
        img = self._resize(img, settings)
        img = self._prepare_for_format(img, settings.output_format)

        output_path = self._build_output_path(image_file, settings, output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        img.save(output_path, format=settings.output_format)
        return output_path

    # ------------------------------------------------------------------
    # 内部処理メソッド
    # ------------------------------------------------------------------

    def _load_image(self, image_file: ImageFile) -> Image.Image:
        """画像を開き、GIF の場合は先頭フレームのみを取得する。

        Args:
            image_file: 読み込む ImageFile エンティティ。

        Returns:
            PIL Image オブジェクト。
        """
        img = Image.open(image_file.path)
        img.load()
        if getattr(img, "is_animated", False):
            img.seek(_GIF_FRAME_INDEX)
            img = img.copy()
        return img

    def _apply_transparency(
        self, img: Image.Image, settings: ConversionSettings
    ) -> Image.Image:
        """透過色が指定されている場合、フラッドフィル方式で透過処理を行う。

        tolerance に応じて許容誤差範囲内の色を透明にする。

        Args:
            img: 処理対象の PIL Image。
            settings: 変換設定。

        Returns:
            透過処理後の PIL Image。
        """
        if settings.transparency_color is None:
            return img

        img = img.convert("RGBA")
        target = settings.transparency_color.to_tuple()
        tolerance = settings.tolerance

        pixels = img.load()
        width, height = img.size

        for y in range(height):
            for x in range(width):
                r, g, b, _ = pixels[x, y]  # type: ignore[misc]
                if self._is_within_tolerance(
                    (r, g, b), target, tolerance
                ):
                    pixels[x, y] = (r, g, b, 0)  # type: ignore[misc]

        return img

    @staticmethod
    def _is_within_tolerance(
        color: tuple[int, int, int],
        target: tuple[int, int, int],
        tolerance: int,
    ) -> bool:
        """指定色がターゲット色の tolerance 範囲内かを判定する。

        Args:
            color: 判定する RGB 色。
            target: ターゲット RGB 色。
            tolerance: 許容誤差 (0〜255)。

        Returns:
            許容範囲内であれば True。
        """
        return all(abs(c - t) <= tolerance for c, t in zip(color, target))

    @staticmethod
    def _resize(img: Image.Image, settings: ConversionSettings) -> Image.Image:
        """倍率に応じて画像をリサイズする。

        Args:
            img: リサイズ対象の PIL Image。
            settings: 変換設定。

        Returns:
            リサイズ後の PIL Image。
        """
        if settings.scale == 1.0:
            return img

        new_width = max(1, int(img.width * settings.scale))
        new_height = max(1, int(img.height * settings.scale))
        resample = Image.LANCZOS if settings.use_antialias else Image.NEAREST
        return img.resize((new_width, new_height), resample=resample)

    @staticmethod
    def _prepare_for_format(
        img: Image.Image, output_format: str
    ) -> Image.Image:
        """出力フォーマットに合わせてカラーモードを変換する。

        JPEG は透過を扱えないため RGBA → RGB に変換して白背景を合成する。

        Args:
            img: 変換対象の PIL Image。
            output_format: 出力フォーマット文字列。

        Returns:
            モード変換後の PIL Image。
        """
        if output_format == "JPEG" and img.mode in ("RGBA", "LA", "P"):
            background = Image.new("RGB", img.size, _JPEG_BACKGROUND_COLOR)
            converted = img.convert("RGBA")
            background.paste(converted, mask=converted.split()[3])
            return background
        if output_format == "BMP" and img.mode == "RGBA":
            return img.convert("RGB")
        return img

    @staticmethod
    def _build_output_path(
        image_file: ImageFile,
        settings: ConversionSettings,
        output_dir: Path,
    ) -> Path:
        """出力ファイルパスを構築する。

        Args:
            image_file: 元の ImageFile エンティティ。
            settings: 変換設定。
            output_dir: 出力先ディレクトリ。

        Returns:
            出力ファイルの Path。
        """
        extension = _FORMAT_TO_EXTENSION.get(settings.output_format, ".png")
        return output_dir / (image_file.stem + extension)
