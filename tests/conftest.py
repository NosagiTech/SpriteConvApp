"""pytest 共有フィクスチャ定義モジュール。

テスト全体で使い回すパス定数・PIL 画像生成ヘルパーを提供する。
"""

from pathlib import Path

import pytest
from PIL import Image

# ---------------------------------------------------------------------------
# テストデータルートパス
# ---------------------------------------------------------------------------
_FIXTURES_DIR = Path(__file__).parent / "fixtures"
_NORMAL_DIR = _FIXTURES_DIR / "normal"
_ABNORMAL_DIR = _FIXTURES_DIR / "abnormal"


# ---------------------------------------------------------------------------
# 既存フィクスチャファイルへのパスフィクスチャ
# ---------------------------------------------------------------------------

@pytest.fixture
def normal_dir() -> Path:
    """normal/ フィクスチャディレクトリのパスを返す。"""
    return _NORMAL_DIR


@pytest.fixture
def abnormal_dir() -> Path:
    """abnormal/ フィクスチャディレクトリのパスを返す。"""
    return _ABNORMAL_DIR


@pytest.fixture
def png_100x100() -> Path:
    """100x100 px の PNG ファイルパス。"""
    return _NORMAL_DIR / "test_100x100.png"


@pytest.fixture
def png_10x10() -> Path:
    """10x10 px の PNG ファイルパス。"""
    return _NORMAL_DIR / "test_10x10.png"


@pytest.fixture
def png_rgba() -> Path:
    """RGBA モード PNG ファイルパス。"""
    return _NORMAL_DIR / "test_rgba.png"


@pytest.fixture
def png_rgb() -> Path:
    """RGB モード PNG ファイルパス。"""
    return _NORMAL_DIR / "test_rgb.png"


@pytest.fixture
def png_near_white() -> Path:
    """白に近い色が含まれる PNG ファイルパス。"""
    return _NORMAL_DIR / "test_near_white.png"


@pytest.fixture
def png_white_bg() -> Path:
    """白背景 PNG ファイルパス。"""
    return _NORMAL_DIR / "test_white_bg.png"


@pytest.fixture
def gif_anim() -> Path:
    """アニメーション GIF ファイルパス。"""
    return _NORMAL_DIR / "test_anim.gif"


@pytest.fixture
def gif_static() -> Path:
    """静止画 GIF ファイルパス。"""
    return _NORMAL_DIR / "test_static.gif"


@pytest.fixture
def jpg_file() -> Path:
    """JPEG ファイルパス。"""
    return _NORMAL_DIR / "test.jpg"


@pytest.fixture
def bmp_file() -> Path:
    """BMP ファイルパス。"""
    return _NORMAL_DIR / "test.bmp"


@pytest.fixture
def tiff_file() -> Path:
    """TIFF ファイルパス。"""
    return _NORMAL_DIR / "test.tiff"


@pytest.fixture
def png_uppercase() -> Path:
    """拡張子が大文字 (.PNG) の PNG ファイルパス。"""
    return _NORMAL_DIR / "test_uppercase.PNG"


@pytest.fixture
def broken_png() -> Path:
    """Pillow で開けない壊れた PNG ファイルパス。"""
    return _ABNORMAL_DIR / "broken.png"


@pytest.fixture
def fake_png() -> Path:
    """内容がテキストの偽装 PNG ファイルパス。"""
    return _ABNORMAL_DIR / "fake.png"


@pytest.fixture
def txt_file() -> Path:
    """テキストファイルパス（非画像）。"""
    return _ABNORMAL_DIR / "test.txt"


# ---------------------------------------------------------------------------
# テスト用プログラム生成画像フィクスチャ（ピクセル値が既知）
# ---------------------------------------------------------------------------

@pytest.fixture
def pure_white_image_path(tmp_path: Path) -> Path:
    """全ピクセルが純白 (255, 255, 255) の 10x10 RGB PNG を生成して返す。"""
    path = tmp_path / "pure_white.png"
    img = Image.new("RGB", (10, 10), (255, 255, 255))
    img.save(path, format="PNG")
    return path


@pytest.fixture
def mixed_white_image_path(tmp_path: Path) -> Path:
    """純白と白に近い色が混在する 10x10 RGB PNG を生成して返す。

    ピクセル構成:
    - 大半: (255, 255, 255) 純白
    - (5, 5): (250, 250, 250) 白から差分 5（tolerance=10 なら透明化対象）
    - (6, 5): (240, 240, 240) 白から差分 15（tolerance=10 なら不透明のまま）
    """
    path = tmp_path / "mixed_white.png"
    img = Image.new("RGB", (10, 10), (255, 255, 255))
    img.putpixel((5, 5), (250, 250, 250))
    img.putpixel((6, 5), (240, 240, 240))
    img.save(path, format="PNG")
    return path


@pytest.fixture
def solid_red_image_path(tmp_path: Path) -> Path:
    """全ピクセルが赤 (128, 0, 0) の 10x10 RGB PNG を生成して返す。"""
    path = tmp_path / "solid_red.png"
    img = Image.new("RGB", (10, 10), (128, 0, 0))
    img.save(path, format="PNG")
    return path
