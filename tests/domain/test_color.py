"""Color バリューオブジェクトのテストモジュール。

対象: src/domain/value_objects/color.py
テストケース: TC-CLR-001 〜 TC-CLR-018
"""

import pytest
from dataclasses import FrozenInstanceError

from src.domain.value_objects.color import Color


class TestColorNormal:
    """TC-CLR-001〜005: 正常系テスト。"""

    def test_tc_clr_001_create_with_min_values(self) -> None:
        """TC-CLR-001: 最小値 (0, 0, 0) で例外なく生成される。"""
        color = Color(0, 0, 0)
        assert color.r == 0
        assert color.g == 0
        assert color.b == 0

    def test_tc_clr_002_create_with_max_values(self) -> None:
        """TC-CLR-002: 最大値 (255, 255, 255) で例外なく生成される。"""
        color = Color(255, 255, 255)
        assert color.r == 255
        assert color.g == 255
        assert color.b == 255

    def test_tc_clr_003_create_with_arbitrary_valid_values(self) -> None:
        """TC-CLR-003: 任意の有効値 (0, 128, 255) で例外なく生成される。"""
        color = Color(0, 128, 255)
        assert color.r == 0
        assert color.g == 128
        assert color.b == 255

    def test_tc_clr_004_to_tuple_returns_correct_value(self) -> None:
        """TC-CLR-004: to_tuple() が (r, g, b) のタプルを返す。"""
        result = Color(10, 20, 30).to_tuple()
        assert result == (10, 20, 30)

    def test_tc_clr_005_immutable(self) -> None:
        """TC-CLR-005: フィールドへの代入で FrozenInstanceError が発生する。"""
        color = Color(1, 2, 3)
        with pytest.raises(FrozenInstanceError):
            color.r = 9  # type: ignore[misc]


class TestColorBoundary:
    """TC-CLR-006〜011: 境界値テスト。"""

    @pytest.mark.parametrize("r, g, b", [
        (0,   100, 100),   # TC-CLR-006: r=0（下限）
        (255, 100, 100),   # TC-CLR-007: r=255（上限）
        (100,   0, 100),   # TC-CLR-008: g=0（下限）
        (100, 255, 100),   # TC-CLR-009: g=255（上限）
        (100, 100,   0),   # TC-CLR-010: b=0（下限）
        (100, 100, 255),   # TC-CLR-011: b=255（上限）
    ])
    def test_tc_clr_006_to_011_boundary_values(self, r: int, g: int, b: int) -> None:
        """TC-CLR-006〜011: 各チャンネルの上限・下限で例外なく生成される。"""
        color = Color(r, g, b)
        assert color.r == r
        assert color.g == g
        assert color.b == b


class TestColorAbnormal:
    """TC-CLR-012〜018: 異常系テスト。"""

    @pytest.mark.parametrize("r, g, b", [
        (-1,   0,   0),    # TC-CLR-012: r が下限未満
        (256,  0,   0),    # TC-CLR-013: r が上限超過
        (0,   -1,   0),    # TC-CLR-014: g が下限未満
        (0,  256,   0),    # TC-CLR-015: g が上限超過
        (0,    0,  -1),    # TC-CLR-016: b が下限未満
        (0,    0, 256),    # TC-CLR-017: b が上限超過
        (300,  0,   0),    # TC-CLR-018: r が極端に大きい値
    ])
    def test_tc_clr_012_to_018_out_of_range_raises_value_error(
        self, r: int, g: int, b: int
    ) -> None:
        """TC-CLR-012〜018: 範囲外の値を渡すと ValueError が発生する。"""
        with pytest.raises(ValueError):
            Color(r, g, b)
