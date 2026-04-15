"""ファイルシステムから画像ファイルを収集するローダの実装モジュール。"""

from pathlib import Path

from PIL import Image, UnidentifiedImageError

from src.domain.entities.image_file import ImageFile
from src.domain.repositories.i_image_loader import IImageLoader

# 収集対象とする画像ファイルの拡張子（小文字で統一）
SUPPORTED_EXTENSIONS: frozenset[str] = frozenset(
    {".png", ".jpg", ".jpeg", ".tiff", ".tif", ".gif", ".bmp"}
)


class ImageFileLoader(IImageLoader):
    """ファイルシステムから画像ファイルを再帰的に収集するローダ。"""

    def load_from_path(self, path: Path) -> list[ImageFile]:
        """指定パスから ImageFile リストを構築して返す。

        パスがファイルの場合は 1 件、ディレクトリの場合は対象拡張子の
        ファイルを再帰的に収集する。Pillow で開けないファイルはスキップする。

        Args:
            path: 読み込み対象のファイルまたはディレクトリのパス。

        Returns:
            ImageFile オブジェクトのリスト。

        Raises:
            FileNotFoundError: path が存在しない場合。
        """
        if not path.exists():
            raise FileNotFoundError(f"パスが存在しません: {path}")

        candidates: list[Path] = (
            [path]
            if path.is_file()
            else self._collect_image_paths(path)
        )

        result: list[ImageFile] = []
        for file_path in candidates:
            image_file = self._try_create_image_file(file_path)
            if image_file is not None:
                result.append(image_file)
        return result

    @staticmethod
    def _collect_image_paths(directory: Path) -> list[Path]:
        """ディレクトリを再帰的に探索し、対象拡張子のファイル一覧を返す。

        Args:
            directory: 探索対象のディレクトリ。

        Returns:
            対象ファイルの Path リスト（ソート済み）。
        """
        paths: list[Path] = []
        for child in sorted(directory.rglob("*")):
            if child.is_file() and child.suffix.lower() in SUPPORTED_EXTENSIONS:
                paths.append(child)
        return paths

    @staticmethod
    def _try_create_image_file(path: Path) -> ImageFile | None:
        """ファイルを Pillow で開き、フォーマットを確認して ImageFile を生成する。

        Pillow で開けない場合や拡張子が非対応の場合は None を返す。

        Args:
            path: 対象ファイルのパス。

        Returns:
            ImageFile オブジェクト、または None（読み込み不可の場合）。
        """
        if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            return None
        try:
            with Image.open(path) as img:
                fmt = img.format or path.suffix.lstrip(".").upper()
            return ImageFile(path=path, format=fmt)
        except (UnidentifiedImageError, OSError):
            return None
