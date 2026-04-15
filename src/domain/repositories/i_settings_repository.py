"""設定リポジトリのインタフェース定義モジュール。"""

from abc import ABC, abstractmethod
from typing import Any


class ISettingsRepository(ABC):
    """設定の読み書きを担うリポジトリの抽象基底クラス。

    実装クラスは YAML ファイルや DB など任意のストレージに対応できる。
    """

    @abstractmethod
    def load_user_settings(self) -> dict[str, Any]:
        """ユーザ設定を読み込んで辞書として返す。

        Returns:
            ユーザ設定を格納した辞書。
        """

    @abstractmethod
    def save_user_settings(self, settings: dict[str, Any]) -> None:
        """ユーザ設定を永続化する。

        Args:
            settings: 保存するユーザ設定の辞書。
        """

    @abstractmethod
    def load_core_settings(self) -> dict[str, Any]:
        """コア設定（アプリ固有の固定パラメータ）を読み込んで辞書として返す。

        Returns:
            コア設定を格納した辞書。
        """
