"""変換設定を保持するエンティティモジュール。"""

from dataclasses import dataclass, field
from typing import Optional

from src.domain.value_objects.color import Color

# サポートする出力フォーマット一覧
SUPPORTED_OUTPUT_FORMATS: list[str] = ["PNG", "JPEG", "TIFF", "GIF", "BMP"]

# 倍率のデフォルト値
DEFAULT_SCALE: float = 1.0


@dataclass
class ConversionSettings:
    """画像変換に必要な設定を保持するエンティティ。

    Attributes:
        output_format: 出力ファイルの画像フォーマット (例: "PNG", "JPEG")。
        scale: リサイズ倍率。1.0 で原寸大。
        use_antialias: リサイズ時にアンチエイリアスを適用するか。
        transparency_color: 透過色として指定する Color。None の場合は透過処理なし。
        tolerance: 透過色の許容誤差 (0〜255)。
    """

    output_format: str = "PNG"
    scale: float = DEFAULT_SCALE
    use_antialias: bool = True
    transparency_color: Optional[Color] = field(default=None)
    tolerance: int = 0

    def __post_init__(self) -> None:
        """フィールド値の妥当性を検証する。

        Raises:
            ValueError: フォーマットや倍率が不正な場合。
        """
        if self.output_format not in SUPPORTED_OUTPUT_FORMATS:
            raise ValueError(
                f"サポートされていない出力フォーマット: {self.output_format}。"
                f"有効な値: {SUPPORTED_OUTPUT_FORMATS}"
            )
        if self.scale <= 0:
            raise ValueError(f"倍率は正の値でなければなりません。指定値: {self.scale}")
        if not (0 <= self.tolerance <= 255):
            raise ValueError(
                f"tolerance は 0〜255 の範囲でなければなりません。指定値: {self.tolerance}"
            )
