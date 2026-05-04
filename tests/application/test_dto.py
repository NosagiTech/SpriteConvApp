"""ConversionResult / ErrorItem DTO のテストモジュール。

対象: src/application/dto/conversion_result.py
      src/application/dto/error_item.py
テストケース: TC-DTO-001 〜 TC-DTO-009
"""

from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from src.application.dto.conversion_result import ConversionResult
from src.application.dto.error_item import ErrorItem


@pytest.fixture
def sample_error_item() -> ErrorItem:
    """テスト用 ErrorItem インスタンスを返す。"""
    return ErrorItem(file_path=Path("a.png"), error_message="エラー")


class TestConversionResultNormal:
    """TC-DTO-001〜003: ConversionResult の正常系テスト。"""

    def test_tc_dto_001_has_errors_false_when_no_errors(self) -> None:
        """TC-DTO-001: error_list が空のとき has_errors が False になる。"""
        result = ConversionResult(success_count=5, error_list=[])
        assert result.has_errors is False

    def test_tc_dto_002_has_errors_true_when_errors_exist(
        self, sample_error_item: ErrorItem
    ) -> None:
        """TC-DTO-002: error_list に 1 件以上あるとき has_errors が True になる。"""
        result = ConversionResult(success_count=3, error_list=[sample_error_item])
        assert result.has_errors is True

    def test_tc_dto_003_total_count_is_success_plus_errors(
        self, sample_error_item: ErrorItem
    ) -> None:
        """TC-DTO-003: total_count が success_count + len(error_list) になる。"""
        result = ConversionResult(
            success_count=4,
            error_list=[sample_error_item, sample_error_item],
        )
        assert result.total_count == 6


class TestErrorItemNormal:
    """TC-DTO-004: ErrorItem の正常系テスト。"""

    def test_tc_dto_004_error_item_fields(self) -> None:
        """TC-DTO-004: file_path と error_message が正しく保持される。"""
        item = ErrorItem(file_path=Path("a.png"), error_message="エラー")
        assert item.file_path == Path("a.png")
        assert item.error_message == "エラー"


class TestConversionResultBoundary:
    """TC-DTO-005〜009: 境界値・イミュータブル確認テスト。"""

    def test_tc_dto_005_all_success(self) -> None:
        """TC-DTO-005: 全件成功（error_list 空）のとき total_count=10, has_errors=False。"""
        result = ConversionResult(success_count=10, error_list=[])
        assert result.total_count == 10
        assert result.has_errors is False

    def test_tc_dto_006_all_fail(self, sample_error_item: ErrorItem) -> None:
        """TC-DTO-006: 全件失敗（success_count=0）のとき total_count=2, has_errors=True。"""
        result = ConversionResult(
            success_count=0,
            error_list=[sample_error_item, sample_error_item],
        )
        assert result.total_count == 2
        assert result.has_errors is True

    def test_tc_dto_007_zero_files_processed(self) -> None:
        """TC-DTO-007: 0 件処理（空）のとき total_count=0, has_errors=False。"""
        result = ConversionResult(success_count=0, error_list=[])
        assert result.total_count == 0
        assert result.has_errors is False

    def test_tc_dto_008_conversion_result_is_immutable(self) -> None:
        """TC-DTO-008: ConversionResult のフィールドへの代入で FrozenInstanceError が発生する。"""
        result = ConversionResult(success_count=1, error_list=[])
        with pytest.raises(FrozenInstanceError):
            result.success_count = 99  # type: ignore[misc]

    def test_tc_dto_009_error_item_is_immutable(self) -> None:
        """TC-DTO-009: ErrorItem のフィールドへの代入で FrozenInstanceError が発生する。"""
        item = ErrorItem(file_path=Path("a.png"), error_message="x")
        with pytest.raises(FrozenInstanceError):
            item.error_message = "改ざん"  # type: ignore[misc]
