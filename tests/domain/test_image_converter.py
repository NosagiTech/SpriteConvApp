"""ImageConverter ドメインサービスのテストモジュール。

対象: src/domain/services/image_converter.py
テストケース: TC-IC-001 〜 TC-IC-016
  TC-IC-017（入力ファイルロック）・TC-IC-018（書き込み権限なし）は
  OS 権限操作を伴うため手動テスト対象とする。
"""

from pathlib import Path

import pytest
from PIL import Image

from src.domain.entities.conversion_settings import ConversionSettings
from src.domain.entities.image_file import ImageFile
from src.domain.services.image_converter import ImageConverter
from src.domain.value_objects.color import Color


@pytest.fixture
def converter() -> ImageConverter:
    """テスト用 ImageConverter インスタンスを返す。"""
    return ImageConverter()


def _make_image_file(path: Path, fmt: str) -> ImageFile:
    """テスト用 ImageFile を生成するヘルパー。"""
    return ImageFile(path=path, format=fmt)


class TestImageConverterNormal:
    """TC-IC-001〜012: 正常系テスト。"""

    def test_tc_ic_001_png_to_png_same_size(
        self, converter: ImageConverter, png_100x100: Path, tmp_path: Path
    ) -> None:
        """TC-IC-001: PNG→PNG 原寸変換でサイズが変わらず保存される。"""
        f = _make_image_file(png_100x100, "PNG")
        s = ConversionSettings(output_format="PNG", scale=1.0)
        out = converter.convert(f, s, tmp_path)
        with Image.open(out) as img:
            assert img.size == (100, 100)
            assert img.format == "PNG"

    def test_tc_ic_002_png_rgba_to_jpeg_white_background(
        self, converter: ImageConverter, png_rgba: Path, tmp_path: Path
    ) -> None:
        """TC-IC-002: RGBA PNG→JPEG 変換で白背景合成された RGB 画像が保存される。"""
        f = _make_image_file(png_rgba, "PNG")
        s = ConversionSettings(output_format="JPEG")
        out = converter.convert(f, s, tmp_path)
        with Image.open(out) as img:
            assert img.mode == "RGB"
            assert img.format == "JPEG"

    def test_tc_ic_003_png_rgba_to_bmp_rgb(
        self, converter: ImageConverter, png_rgba: Path, tmp_path: Path
    ) -> None:
        """TC-IC-003: RGBA PNG→BMP 変換で RGB に変換された BMP が保存される。"""
        f = _make_image_file(png_rgba, "PNG")
        s = ConversionSettings(output_format="BMP")
        out = converter.convert(f, s, tmp_path)
        with Image.open(out) as img:
            assert img.mode == "RGB"
            assert img.format == "BMP"

    def test_tc_ic_004_animated_gif_first_frame_only(
        self, converter: ImageConverter, gif_anim: Path, tmp_path: Path
    ) -> None:
        """TC-IC-004: アニメーション GIF→PNG 変換で先頭フレームのみが PNG に変換される。"""
        f = _make_image_file(gif_anim, "GIF")
        s = ConversionSettings(output_format="PNG")
        out = converter.convert(f, s, tmp_path)
        with Image.open(out) as img:
            assert img.format == "PNG"
            assert not getattr(img, "is_animated", False)

    def test_tc_ic_005_scale_up(
        self, converter: ImageConverter, png_100x100: Path, tmp_path: Path
    ) -> None:
        """TC-IC-005: scale=2.0 で 200x200 px に拡大される。"""
        f = _make_image_file(png_100x100, "PNG")
        s = ConversionSettings(scale=2.0)
        out = converter.convert(f, s, tmp_path)
        with Image.open(out) as img:
            assert img.size == (200, 200)

    def test_tc_ic_006_scale_down(
        self, converter: ImageConverter, png_100x100: Path, tmp_path: Path
    ) -> None:
        """TC-IC-006: scale=0.5 で 50x50 px に縮小される。"""
        f = _make_image_file(png_100x100, "PNG")
        s = ConversionSettings(scale=0.5)
        out = converter.convert(f, s, tmp_path)
        with Image.open(out) as img:
            assert img.size == (50, 50)

    def test_tc_ic_007_antialias_lanczos(
        self, converter: ImageConverter, png_100x100: Path, tmp_path: Path
    ) -> None:
        """TC-IC-007: use_antialias=True のとき例外なく変換され出力サイズが正しい。"""
        f = _make_image_file(png_100x100, "PNG")
        s = ConversionSettings(scale=2.0, use_antialias=True)
        out = converter.convert(f, s, tmp_path)
        with Image.open(out) as img:
            assert img.size == (200, 200)

    def test_tc_ic_008_antialias_nearest(
        self, converter: ImageConverter, png_100x100: Path, tmp_path: Path
    ) -> None:
        """TC-IC-008: use_antialias=False のとき例外なく変換され出力サイズが正しい。"""
        f = _make_image_file(png_100x100, "PNG")
        s = ConversionSettings(scale=2.0, use_antialias=False)
        out = converter.convert(f, s, tmp_path)
        with Image.open(out) as img:
            assert img.size == (200, 200)

    def test_tc_ic_009_transparency_exact_match(
        self,
        converter: ImageConverter,
        pure_white_image_path: Path,
        tmp_path: Path,
    ) -> None:
        """TC-IC-009: tolerance=0 で純白ピクセルがすべてアルファ=0 になる。"""
        f = _make_image_file(pure_white_image_path, "PNG")
        s = ConversionSettings(
            transparency_color=Color(255, 255, 255),
            tolerance=0,
            output_format="PNG",
        )
        out = converter.convert(f, s, tmp_path)
        with Image.open(out) as img:
            rgba = img.convert("RGBA")
            _, _, _, alpha = rgba.split()
            # 全ピクセルのアルファ値が 0 であることを最小値・最大値で確認
            assert alpha.getextrema() == (0, 0), "全ピクセルが透明化されていない"

    def test_tc_ic_010_transparency_with_tolerance(
        self,
        converter: ImageConverter,
        mixed_white_image_path: Path,
        tmp_path: Path,
    ) -> None:
        """TC-IC-010: tolerance=10 で許容範囲内の白系ピクセルが透明化される。

        mixed_white_image_path の構成:
        - 大半: (255, 255, 255) → 差分 0 → 透明化
        - (5, 5): (250, 250, 250) → 差分 5 ≤ 10 → 透明化
        - (6, 5): (240, 240, 240) → 差分 15 > 10 → 不透明のまま
        """
        f = _make_image_file(mixed_white_image_path, "PNG")
        s = ConversionSettings(
            transparency_color=Color(255, 255, 255),
            tolerance=10,
            output_format="PNG",
        )
        out = converter.convert(f, s, tmp_path)
        with Image.open(out) as img:
            rgba = img.convert("RGBA")
            # (5, 5) は透明化されるはず
            assert rgba.getpixel((5, 5))[3] == 0, "(5,5) が透明化されていない"
            # (6, 5) は不透明のまま
            assert rgba.getpixel((6, 5))[3] != 0, "(6,5) が誤って透明化された"

    def test_tc_ic_011_output_dir_created_automatically(
        self, converter: ImageConverter, png_100x100: Path, tmp_path: Path
    ) -> None:
        """TC-IC-011: 未存在の出力ディレクトリが自動作成されてファイルが保存される。"""
        new_dir = tmp_path / "new" / "subdir"
        assert not new_dir.exists()
        f = _make_image_file(png_100x100, "PNG")
        s = ConversionSettings()
        converter.convert(f, s, new_dir)
        assert new_dir.exists()

    def test_tc_ic_012_output_filename_based_on_stem(
        self, converter: ImageConverter, png_100x100: Path, tmp_path: Path
    ) -> None:
        """TC-IC-012: 出力ファイル名が入力ファイルの stem に準拠する。"""
        f = _make_image_file(png_100x100, "PNG")
        s = ConversionSettings(output_format="JPEG")
        out = converter.convert(f, s, tmp_path)
        assert out.name == "test_100x100.jpg"


class TestImageConverterBoundary:
    """TC-IC-013〜016: 境界値テスト。"""

    def test_tc_ic_013_min_scale_ensures_at_least_1px(
        self, converter: ImageConverter, png_10x10: Path, tmp_path: Path
    ) -> None:
        """TC-IC-013: scale=0.01 の極小倍率でも最低 1x1 px が保証される。"""
        f = _make_image_file(png_10x10, "PNG")
        s = ConversionSettings(scale=0.01)
        out = converter.convert(f, s, tmp_path)
        with Image.open(out) as img:
            assert img.size[0] >= 1
            assert img.size[1] >= 1

    def test_tc_ic_014_scale_one_skips_resize(
        self, converter: ImageConverter, png_100x100: Path, tmp_path: Path
    ) -> None:
        """TC-IC-014: scale=1.0 のときリサイズをスキップし画像サイズが変わらない。"""
        f = _make_image_file(png_100x100, "PNG")
        s = ConversionSettings(scale=1.0)
        out = converter.convert(f, s, tmp_path)
        with Image.open(out) as img:
            assert img.size == (100, 100)

    def test_tc_ic_015_tolerance_zero_exact_match_only(
        self,
        converter: ImageConverter,
        mixed_white_image_path: Path,
        tmp_path: Path,
    ) -> None:
        """TC-IC-015: tolerance=0 で完全一致のピクセルのみ透明化され、隣接色は不変。

        mixed_white_image_path の (6, 5) は (240, 240, 240) → 不透明のまま。
        """
        f = _make_image_file(mixed_white_image_path, "PNG")
        s = ConversionSettings(
            transparency_color=Color(255, 255, 255),
            tolerance=0,
            output_format="PNG",
        )
        out = converter.convert(f, s, tmp_path)
        with Image.open(out) as img:
            rgba = img.convert("RGBA")
            # 純白のピクセルは透明化される
            assert rgba.getpixel((0, 0))[3] == 0, "(0,0) が透明化されていない"
            # 差分がある (6, 5) は不透明のまま
            assert rgba.getpixel((6, 5))[3] != 0, "(6,5) が誤って透明化された"

    def test_tc_ic_016_tolerance_255_makes_all_pixels_transparent(
        self,
        converter: ImageConverter,
        solid_red_image_path: Path,
        tmp_path: Path,
    ) -> None:
        """TC-IC-016: tolerance=255 で全ピクセルが透明化される。"""
        f = _make_image_file(solid_red_image_path, "PNG")
        s = ConversionSettings(
            transparency_color=Color(0, 0, 0),
            tolerance=255,
            output_format="PNG",
        )
        out = converter.convert(f, s, tmp_path)
        with Image.open(out) as img:
            rgba = img.convert("RGBA")
            _, _, _, alpha = rgba.split()
            assert alpha.getextrema() == (0, 0), "全ピクセルが透明化されていない"
