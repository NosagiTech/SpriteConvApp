"""ImageFileLoader インフラ層のテストモジュール。

対象: src/infra/image_file_loader.py
テストケース: TC-IFL-001 〜 TC-IFL-014
"""

from pathlib import Path

import pytest
from PIL import Image

from src.infra.image_file_loader import ImageFileLoader


@pytest.fixture
def loader() -> ImageFileLoader:
    """テスト用 ImageFileLoader インスタンスを返す。"""
    return ImageFileLoader()


class TestImageFileLoaderNormal:
    """TC-IFL-001〜007: 正常系テスト。"""

    def test_tc_ifl_001_single_png_file(
        self, loader: ImageFileLoader, png_100x100: Path
    ) -> None:
        """TC-IFL-001: 有効な PNG ファイルを指定すると format="PNG" の ImageFile が返る。"""
        result = loader.load_from_path(png_100x100)
        assert len(result) == 1
        assert result[0].format == "PNG"
        assert result[0].path == png_100x100

    def test_tc_ifl_002_single_jpeg_file(
        self, loader: ImageFileLoader, jpg_file: Path
    ) -> None:
        """TC-IFL-002: 有効な JPEG ファイルを指定すると format="JPEG" の ImageFile が返る。"""
        result = loader.load_from_path(jpg_file)
        assert len(result) == 1
        assert result[0].format == "JPEG"

    def test_tc_ifl_003_single_gif_file(
        self, loader: ImageFileLoader, gif_static: Path
    ) -> None:
        """TC-IFL-003: 有効な GIF ファイルを指定すると format="GIF" の ImageFile が返る。"""
        result = loader.load_from_path(gif_static)
        assert len(result) == 1
        assert result[0].format == "GIF"

    def test_tc_ifl_004_folder_with_multiple_images(
        self, loader: ImageFileLoader, normal_dir: Path
    ) -> None:
        """TC-IFL-004: 複数の画像を含むフォルダを指定すると全件が返る。"""
        result = loader.load_from_path(normal_dir)
        assert len(result) > 1

    def test_tc_ifl_005_recursive_folder_search(
        self, loader: ImageFileLoader, tmp_path: Path
    ) -> None:
        """TC-IFL-005: サブフォルダを含むフォルダを指定すると再帰的に全件が収集される。"""
        sub = tmp_path / "sub"
        sub.mkdir()
        for fname, parent in [("a.png", tmp_path), ("b.png", sub)]:
            Image.new("RGB", (4, 4), (0, 0, 0)).save(parent / fname)

        result = loader.load_from_path(tmp_path)
        assert len(result) == 2

    def test_tc_ifl_006_uppercase_png_extension(
        self, loader: ImageFileLoader, png_uppercase: Path
    ) -> None:
        """TC-IFL-006: 拡張子が大文字 (.PNG) のファイルが収集対象として認識される。"""
        result = loader.load_from_path(png_uppercase)
        assert len(result) == 1

    def test_tc_ifl_007_uppercase_jpg_extension(
        self, loader: ImageFileLoader, tmp_path: Path
    ) -> None:
        """TC-IFL-007: 拡張子が大文字 (.JPG) のファイルが収集対象として認識される。"""
        path = tmp_path / "test_upper.JPG"
        Image.new("RGB", (4, 4), (0, 0, 0)).save(path, format="JPEG")
        result = loader.load_from_path(path)
        assert len(result) == 1


class TestImageFileLoaderBoundary:
    """TC-IFL-008〜011: 境界値テスト。"""

    def test_tc_ifl_008_empty_folder(
        self, loader: ImageFileLoader, tmp_path: Path
    ) -> None:
        """TC-IFL-008: 画像ファイルが 0 件のフォルダを指定すると空リストが返る。"""
        result = loader.load_from_path(tmp_path)
        assert result == []

    def test_tc_ifl_009_folder_with_non_image_files_only(
        self, loader: ImageFileLoader, tmp_path: Path
    ) -> None:
        """TC-IFL-009: .txt / .csv のみのフォルダを指定すると空リストが返る。"""
        (tmp_path / "data.txt").write_text("hello")
        (tmp_path / "data.csv").write_text("a,b,c")
        result = loader.load_from_path(tmp_path)
        assert result == []

    def test_tc_ifl_010_txt_file_direct_path(
        self, loader: ImageFileLoader, txt_file: Path
    ) -> None:
        """TC-IFL-010: .txt ファイルを直接指定すると空リストが返る（スキップ）。"""
        result = loader.load_from_path(txt_file)
        assert result == []

    def test_tc_ifl_011_folder_with_mixed_extensions(
        self, loader: ImageFileLoader, tmp_path: Path
    ) -> None:
        """TC-IFL-011: .png と .txt が混在するフォルダを指定すると .png のみが返る。"""
        Image.new("RGB", (4, 4), (0, 0, 0)).save(tmp_path / "img.png")
        (tmp_path / "note.txt").write_text("text")
        result = loader.load_from_path(tmp_path)
        assert len(result) == 1
        assert result[0].path.suffix.lower() == ".png"


class TestImageFileLoaderAbnormal:
    """TC-IFL-012〜014: 異常系テスト。"""

    def test_tc_ifl_012_nonexistent_path_raises_file_not_found(
        self, loader: ImageFileLoader
    ) -> None:
        """TC-IFL-012: 存在しないパスを指定すると FileNotFoundError が発生する。"""
        with pytest.raises(FileNotFoundError):
            loader.load_from_path(Path("nonexistent/path.png"))

    def test_tc_ifl_013_broken_png_is_skipped(
        self, loader: ImageFileLoader, broken_png: Path
    ) -> None:
        """TC-IFL-013: 破損した PNG ファイルはスキップされ、空リストが返る。"""
        result = loader.load_from_path(broken_png)
        assert result == []

    def test_tc_ifl_014_fake_png_content_is_skipped(
        self, loader: ImageFileLoader, fake_png: Path
    ) -> None:
        """TC-IFL-014: .png 拡張子だが内容がテキストのファイルはスキップされ、空リストが返る。"""
        result = loader.load_from_path(fake_png)
        assert result == []
