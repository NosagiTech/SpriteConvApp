"""LoadImagesUseCase アプリケーション層のテストモジュール。

対象: src/application/use_cases/load_images_use_case.py
テストケース: TC-LI-001 〜 TC-LI-010
"""

from pathlib import Path

import pytest

from src.application.use_cases.load_images_use_case import LoadImagesUseCase
from src.infra.image_file_loader import ImageFileLoader


@pytest.fixture
def use_case() -> LoadImagesUseCase:
    """ImageFileLoader を注入した LoadImagesUseCase インスタンスを返す。"""
    return LoadImagesUseCase(loader=ImageFileLoader())


class TestLoadImagesUseCaseNormal:
    """TC-LI-001〜005: 正常系テスト。"""

    def test_tc_li_001_single_valid_file(
        self, use_case: LoadImagesUseCase, png_100x100: Path
    ) -> None:
        """TC-LI-001: 有効な PNG ファイルパス 1 件を渡すと 1 件が返る。"""
        result = use_case.execute([png_100x100])
        assert len(result) == 1

    def test_tc_li_002_valid_folder_path(
        self, use_case: LoadImagesUseCase, normal_dir: Path
    ) -> None:
        """TC-LI-002: 有効なフォルダパスを渡すとフォルダ内の全画像が返る。"""
        result = use_case.execute([normal_dir])
        assert len(result) > 0

    def test_tc_li_003_multiple_valid_files(
        self, use_case: LoadImagesUseCase, png_100x100: Path, jpg_file: Path
    ) -> None:
        """TC-LI-003: 複数の有効なファイルパスを渡すと全件が返る。"""
        result = use_case.execute([png_100x100, jpg_file])
        assert len(result) == 2

    def test_tc_li_004_invalid_path_without_callback_returns_empty(
        self, use_case: LoadImagesUseCase
    ) -> None:
        """TC-LI-004: warning_cb なしで不正パスを渡すと空リストが返りクラッシュしない。"""
        result = use_case.execute([Path("nonexistent.png")], warning_cb=None)
        assert result == []

    def test_tc_li_005_invalid_path_with_callback_calls_warning(
        self, use_case: LoadImagesUseCase
    ) -> None:
        """TC-LI-005: warning_cb ありで不正パスを渡すと callback が呼ばれ "[警告]" が含まれる。"""
        warnings: list[str] = []
        use_case.execute(
            [Path("nonexistent.png")],
            warning_cb=lambda msg: warnings.append(msg),
        )
        assert len(warnings) == 1
        assert "[警告]" in warnings[0]


class TestLoadImagesUseCaseBoundary:
    """TC-LI-006〜009: 境界値テスト。"""

    def test_tc_li_006_empty_path_list(
        self, use_case: LoadImagesUseCase
    ) -> None:
        """TC-LI-006: 空リストを渡すと空リストが返る。"""
        result = use_case.execute([])
        assert result == []

    def test_tc_li_007_duplicate_file_path_deduplicated(
        self, use_case: LoadImagesUseCase, png_100x100: Path
    ) -> None:
        """TC-LI-007: 同じファイルパスを 2 回渡すと重複を除き 1 件のみが返る。"""
        result = use_case.execute([png_100x100, png_100x100])
        assert len(result) == 1

    def test_tc_li_008_file_and_folder_mixed_with_overlap(
        self, use_case: LoadImagesUseCase, normal_dir: Path, png_100x100: Path
    ) -> None:
        """TC-LI-008: フォルダとフォルダ内のファイルを同時に指定すると重複を排除した件数が返る。"""
        folder_count = len(use_case.execute([normal_dir]))
        result = use_case.execute([normal_dir, png_100x100])
        assert len(result) == folder_count

    def test_tc_li_009_valid_and_invalid_mixed(
        self, use_case: LoadImagesUseCase, png_100x100: Path
    ) -> None:
        """TC-LI-009: 有効ファイルと存在しないパスが混在すると有効ファイルのみが返る。"""
        warnings: list[str] = []
        result = use_case.execute(
            [png_100x100, Path("nonexistent.png")],
            warning_cb=lambda msg: warnings.append(msg),
        )
        assert len(result) == 1
        assert len(warnings) == 1


class TestLoadImagesUseCaseAbnormal:
    """TC-LI-010: 異常系テスト。"""

    def test_tc_li_010_all_invalid_paths_returns_empty(
        self, use_case: LoadImagesUseCase
    ) -> None:
        """TC-LI-010: 全件存在しないパスを渡すと空リストが返り例外を外に出さない。"""
        result = use_case.execute(
            [Path("a.png"), Path("b.png")]
        )
        assert result == []
