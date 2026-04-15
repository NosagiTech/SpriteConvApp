"""YAML ファイルを用いた設定リポジトリの実装モジュール。"""

from pathlib import Path
from typing import Any

import yaml

from src.domain.repositories.i_settings_repository import ISettingsRepository


class SettingsRepository(ISettingsRepository):
    """PyYAML を用いてコア設定・ユーザ設定を YAML ファイルへ読み書きするリポジトリ。

    Args:
        core_path: コア設定ファイル (core_settings.yaml) のパス。
        user_path: ユーザ設定ファイル (user_settings.yaml) のパス。
    """

    def __init__(self, core_path: Path, user_path: Path) -> None:
        """コンストラクタ。

        Args:
            core_path: コア設定ファイルのパス。
            user_path: ユーザ設定ファイルのパス。
        """
        self._core_path = core_path
        self._user_path = user_path

    def load_user_settings(self) -> dict[str, Any]:
        """ユーザ設定 YAML を読み込んで辞書として返す。

        ファイルが存在しない場合は空辞書を返す。

        Returns:
            ユーザ設定の辞書。
        """
        return self._load_yaml(self._user_path)

    def save_user_settings(self, settings: dict[str, Any]) -> None:
        """ユーザ設定を YAML ファイルへ書き出す。

        Args:
            settings: 保存するユーザ設定の辞書。
        """
        self._user_path.parent.mkdir(parents=True, exist_ok=True)
        with self._user_path.open("w", encoding="utf-8") as f:
            yaml.dump(
                settings,
                f,
                allow_unicode=True,
                default_flow_style=False,
                sort_keys=False,
            )

    def load_core_settings(self) -> dict[str, Any]:
        """コア設定 YAML を読み込んで辞書として返す。

        ファイルが存在しない場合は空辞書を返す。

        Returns:
            コア設定の辞書。
        """
        return self._load_yaml(self._core_path)

    @staticmethod
    def _load_yaml(path: Path) -> dict[str, Any]:
        """YAML ファイルを安全に読み込む。

        Args:
            path: 読み込むファイルのパス。

        Returns:
            読み込んだ辞書。ファイルが存在しない場合は空辞書。
        """
        if not path.exists():
            return {}
        with path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return data if isinstance(data, dict) else {}
