"""ConvertImagesUseCase アプリケーション層のテストモジュール。

対象: src/application/use_cases/convert_images_use_case.py
テストケース: TC-CI-001 〜 TC-CI-012
"""

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from src.application.dto.error_item import ErrorItem
from src.application.use_cases.convert_images_use_case import ConvertImagesUseCase
from src.domain.entities.conversion_settings import ConversionSettings
from src.domain.entities.image_file import ImageFile


def _make_file(name: str = "test.png") -> ImageFile:
    """テスト用 ImageFile を生成するヘルパー。"""
    return ImageFile(path=Path(name), format="PNG")


def _make_success_converter() -> MagicMock:
    """常に成功する ImageConverter モックを返す。"""
    mock = MagicMock()
    mock.convert.return_value = Path("out/test.png")
    return mock


def _make_error_converter(message: str = "エラー") -> MagicMock:
    """常に OSError を発生させる ImageConverter モックを返す。"""
    mock = MagicMock()
    mock.convert.side_effect = OSError(message)
    return mock


@pytest.fixture
def settings() -> ConversionSettings:
    """デフォルト変換設定を返す。"""
    return ConversionSettings()


@pytest.fixture
def three_files() -> list[ImageFile]:
    """テスト用 ImageFile リスト（3 件）を返す。"""
    return [_make_file("a.png"), _make_file("b.png"), _make_file("c.png")]


class TestConvertImagesUseCaseNormal:
    """TC-CI-001〜004: 正常系テスト（progress_cb 含む）。"""

    def test_tc_ci_001_all_success(
        self,
        three_files: list[ImageFile],
        settings: ConversionSettings,
        tmp_path: Path,
    ) -> None:
        """TC-CI-001: 全件正常変換のとき success_count=3, error_list=[] が返る。"""
        uc = ConvertImagesUseCase(converter=_make_success_converter())
        result = uc.execute(three_files, settings, tmp_path)
        assert result.success_count == 3
        assert result.error_list == []

    def test_tc_ci_002_progress_cb_called_correct_times(
        self,
        three_files: list[ImageFile],
        settings: ConversionSettings,
        tmp_path: Path,
    ) -> None:
        """TC-CI-002: progress_cb が変換ファイル数と同じ回数 (3) 呼ばれる。"""
        calls: list[tuple[int, int]] = []
        uc = ConvertImagesUseCase(converter=_make_success_converter())
        uc.execute(three_files, settings, tmp_path, progress_cb=lambda c, t: calls.append((c, t)))
        assert len(calls) == 3

    def test_tc_ci_003_progress_cb_current_increments(
        self,
        three_files: list[ImageFile],
        settings: ConversionSettings,
        tmp_path: Path,
    ) -> None:
        """TC-CI-003: progress_cb の current 引数が 1, 2, 3 の順で渡される。"""
        calls: list[tuple[int, int]] = []
        uc = ConvertImagesUseCase(converter=_make_success_converter())
        uc.execute(three_files, settings, tmp_path, progress_cb=lambda c, t: calls.append((c, t)))
        assert [c for c, _ in calls] == [1, 2, 3]

    def test_tc_ci_004_progress_cb_total_is_constant(
        self,
        three_files: list[ImageFile],
        settings: ConversionSettings,
        tmp_path: Path,
    ) -> None:
        """TC-CI-004: progress_cb の total 引数が常に 3 で渡される。"""
        calls: list[tuple[int, int]] = []
        uc = ConvertImagesUseCase(converter=_make_success_converter())
        uc.execute(three_files, settings, tmp_path, progress_cb=lambda c, t: calls.append((c, t)))
        assert all(t == 3 for _, t in calls)


class TestConvertImagesUseCaseBoundary:
    """TC-CI-005〜007: 境界値テスト。"""

    def test_tc_ci_005_empty_file_list(
        self, settings: ConversionSettings, tmp_path: Path
    ) -> None:
        """TC-CI-005: files が空リストのとき success_count=0, error_list=[], progress_cb 未呼び出し。"""
        calls: list[int] = []
        uc = ConvertImagesUseCase(converter=_make_success_converter())
        result = uc.execute([], settings, tmp_path, progress_cb=lambda c, t: calls.append(c))
        assert result.success_count == 0
        assert result.error_list == []
        assert calls == []

    def test_tc_ci_006_progress_cb_none_does_not_crash(
        self,
        three_files: list[ImageFile],
        settings: ConversionSettings,
        tmp_path: Path,
    ) -> None:
        """TC-CI-006: progress_cb=None のときクラッシュせず正常に変換結果が返る。"""
        uc = ConvertImagesUseCase(converter=_make_success_converter())
        result = uc.execute(three_files, settings, tmp_path, progress_cb=None)
        assert result.success_count == 3

    def test_tc_ci_007_single_file_progress_cb(
        self, settings: ConversionSettings, tmp_path: Path
    ) -> None:
        """TC-CI-007: 1 件のみ変換のとき progress_cb(current=1, total=1) が 1 回呼ばれる。"""
        calls: list[tuple[int, int]] = []
        uc = ConvertImagesUseCase(converter=_make_success_converter())
        uc.execute(
            [_make_file()],
            settings,
            tmp_path,
            progress_cb=lambda c, t: calls.append((c, t)),
        )
        assert calls == [(1, 1)]


class TestConvertImagesUseCaseAbnormal:
    """TC-CI-008〜012: 異常系テスト。"""

    def test_tc_ci_008_one_failure_among_three(
        self, settings: ConversionSettings, tmp_path: Path
    ) -> None:
        """TC-CI-008: 3 件中 1 件が OSError のとき success_count=2, error_list に 1 件が入る。"""
        mock = _make_success_converter()
        mock.convert.side_effect = [
            Path("out/a.png"),
            Path("out/b.png"),
            OSError("失敗"),
        ]
        uc = ConvertImagesUseCase(converter=mock)
        result = uc.execute(
            [_make_file("a.png"), _make_file("b.png"), _make_file("c.png")],
            settings,
            tmp_path,
        )
        assert result.success_count == 2
        assert len(result.error_list) == 1

    def test_tc_ci_009_processing_continues_after_error(
        self, settings: ConversionSettings, tmp_path: Path
    ) -> None:
        """TC-CI-009: 1 件目が失敗しても 2 件目の変換が実行される。"""
        mock = MagicMock()
        mock.convert.side_effect = [OSError("失敗"), Path("out/b.png")]
        uc = ConvertImagesUseCase(converter=mock)
        result = uc.execute(
            [_make_file("a.png"), _make_file("b.png")],
            settings,
            tmp_path,
        )
        assert result.success_count == 1
        assert mock.convert.call_count == 2

    def test_tc_ci_010_all_fail(
        self, settings: ConversionSettings, tmp_path: Path
    ) -> None:
        """TC-CI-010: 全件失敗のとき success_count=0, len(error_list)=全件数 になる。"""
        uc = ConvertImagesUseCase(converter=_make_error_converter())
        files = [_make_file("a.png"), _make_file("b.png")]
        result = uc.execute(files, settings, tmp_path)
        assert result.success_count == 0
        assert len(result.error_list) == 2

    def test_tc_ci_011_progress_cb_called_even_on_error(
        self, settings: ConversionSettings, tmp_path: Path
    ) -> None:
        """TC-CI-011: エラーが発生した件に対しても progress_cb が呼ばれる（finally 保証）。"""
        calls: list[int] = []
        mock = MagicMock()
        mock.convert.side_effect = [OSError("失敗"), Path("out/b.png")]
        uc = ConvertImagesUseCase(converter=mock)
        uc.execute(
            [_make_file("a.png"), _make_file("b.png")],
            settings,
            tmp_path,
            progress_cb=lambda c, t: calls.append(c),
        )
        assert calls == [1, 2]

    def test_tc_ci_012_error_item_fields(
        self, settings: ConversionSettings, tmp_path: Path
    ) -> None:
        """TC-CI-012: ErrorItem の file_path と error_message が正しく格納される。"""
        error_msg = "ファイルが開けません"
        uc = ConvertImagesUseCase(converter=_make_error_converter(error_msg))
        target = _make_file("target.png")
        result = uc.execute([target], settings, tmp_path)
        item: ErrorItem = result.error_list[0]
        assert item.file_path == target.path
        assert item.error_message == error_msg
