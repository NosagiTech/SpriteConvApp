"""ConversionSettings エンティティのテストモジュール。

対象: src/domain/entities/conversion_settings.py
テストケース: TC-CS-001 〜 TC-CS-019
"""

import pytest

from src.domain.entities.conversion_settings import ConversionSettings
from src.domain.value_objects.color import Color


class TestConversionSettingsNormal:
    """TC-CS-001〜008: 正常系テスト。"""

    def test_tc_cs_001_default_values(self) -> None:
        """TC-CS-001: デフォルト値で生成したとき各フィールドが仕様通りの値を持つ。"""
        s = ConversionSettings()
        assert s.output_format == "PNG"
        assert s.scale == 1.0
        assert s.use_antialias is True
        assert s.transparency_color is None
        assert s.tolerance == 0

    @pytest.mark.parametrize("fmt", ["PNG", "JPEG", "TIFF", "GIF", "BMP"])
    def test_tc_cs_002_to_006_supported_formats(self, fmt: str) -> None:
        """TC-CS-002〜006: サポートされている全フォーマットで例外なく生成される。"""
        s = ConversionSettings(output_format=fmt)
        assert s.output_format == fmt

    def test_tc_cs_007_transparency_color_none(self) -> None:
        """TC-CS-007: transparency_color=None で例外なく生成される。"""
        s = ConversionSettings(transparency_color=None)
        assert s.transparency_color is None

    def test_tc_cs_008_transparency_color_with_color_object(self) -> None:
        """TC-CS-008: transparency_color に Color オブジェクトを渡して例外なく生成される。"""
        color = Color(0, 255, 0)
        s = ConversionSettings(transparency_color=color)
        assert s.transparency_color == color


class TestConversionSettingsBoundary:
    """TC-CS-009〜012: 境界値テスト。"""

    def test_tc_cs_009_scale_minimum_valid(self) -> None:
        """TC-CS-009: scale の最小正当値 (0.01) で例外なく生成される。"""
        s = ConversionSettings(scale=0.01)
        assert s.scale == pytest.approx(0.01)

    def test_tc_cs_010_scale_maximum_valid(self) -> None:
        """TC-CS-010: scale の最大正当値 (100.0) で例外なく生成される。"""
        s = ConversionSettings(scale=100.0)
        assert s.scale == 100.0

    def test_tc_cs_011_tolerance_lower_bound(self) -> None:
        """TC-CS-011: tolerance の下限 (0) で例外なく生成される。"""
        s = ConversionSettings(tolerance=0)
        assert s.tolerance == 0

    def test_tc_cs_012_tolerance_upper_bound(self) -> None:
        """TC-CS-012: tolerance の上限 (255) で例外なく生成される。"""
        s = ConversionSettings(tolerance=255)
        assert s.tolerance == 255


class TestConversionSettingsAbnormal:
    """TC-CS-013〜019: 異常系テスト。"""

    @pytest.mark.parametrize("fmt", ["WEBP", "", "png"])
    def test_tc_cs_013_to_015_unsupported_format_raises_value_error(
        self, fmt: str
    ) -> None:
        """TC-CS-013〜015: 未対応・空・小文字フォーマットで ValueError が発生する。"""
        with pytest.raises(ValueError):
            ConversionSettings(output_format=fmt)

    @pytest.mark.parametrize("scale", [0, -1.0])
    def test_tc_cs_016_to_017_invalid_scale_raises_value_error(
        self, scale: float
    ) -> None:
        """TC-CS-016〜017: scale が 0 または負値のとき ValueError が発生する。"""
        with pytest.raises(ValueError):
            ConversionSettings(scale=scale)

    @pytest.mark.parametrize("tolerance", [-1, 256])
    def test_tc_cs_018_to_019_invalid_tolerance_raises_value_error(
        self, tolerance: int
    ) -> None:
        """TC-CS-018〜019: tolerance が範囲外のとき ValueError が発生する。"""
        with pytest.raises(ValueError):
            ConversionSettings(tolerance=tolerance)
