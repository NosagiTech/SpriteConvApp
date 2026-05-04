"""SettingsRepository インフラ層のテストモジュール。

対象: src/infra/settings_repository.py
テストケース: TC-SR-001 〜 TC-SR-010
  TC-SR-011（読み取り権限なし）は OS 権限操作を伴うため手動テスト対象とする。
"""

from pathlib import Path

import pytest

from src.infra.settings_repository import SettingsRepository

# テスト用コア設定ファイルのパス（プロジェクトルート直下）
_CORE_YAML = Path(__file__).parent.parent.parent / "core_settings.yaml"


@pytest.fixture
def repo(tmp_path: Path) -> SettingsRepository:
    """tmp_path 内のユーザ設定ファイルを使う SettingsRepository を返す。"""
    return SettingsRepository(
        core_path=_CORE_YAML,
        user_path=tmp_path / "user_settings.yaml",
    )


class TestSettingsRepositoryNormal:
    """TC-SR-001〜005: 正常系テスト。"""

    def test_tc_sr_001_load_core_settings(self) -> None:
        """TC-SR-001: core_settings.yaml を読み込むと必要なキーを含む辞書が返る。"""
        r = SettingsRepository(core_path=_CORE_YAML, user_path=Path("dummy.yaml"))
        data = r.load_core_settings()
        assert "scale" in data
        assert "thumbnail" in data
        assert "transparency" in data

    def test_tc_sr_002_load_user_settings(self, tmp_path: Path) -> None:
        """TC-SR-002: 有効な user_settings.yaml を読み込むと保存済みの値が返る。"""
        user_yaml = tmp_path / "user_settings.yaml"
        user_yaml.write_text("output_format: JPEG\nscale: 2.0\n", encoding="utf-8")
        r = SettingsRepository(core_path=_CORE_YAML, user_path=user_yaml)
        data = r.load_user_settings()
        assert data["output_format"] == "JPEG"
        assert data["scale"] == pytest.approx(2.0)

    def test_tc_sr_003_save_then_load_restores_values(
        self, repo: SettingsRepository
    ) -> None:
        """TC-SR-003: save_user_settings → load_user_settings で値が完全に復元される。"""
        original = {"output_format": "BMP", "scale": 1.5}
        repo.save_user_settings(original)
        restored = repo.load_user_settings()
        assert restored == original

    def test_tc_sr_004_japanese_values_roundtrip(
        self, repo: SettingsRepository
    ) -> None:
        """TC-SR-004: 日本語を含む値が UTF-8 で保存・復元される。"""
        data = {"output_dir": "C:/Users/テスト/出力"}
        repo.save_user_settings(data)
        restored = repo.load_user_settings()
        assert restored == data

    def test_tc_sr_005_none_value_roundtrip(
        self, repo: SettingsRepository
    ) -> None:
        """TC-SR-005: None 値が保存・復元される。"""
        data = {"transparency_color": None}
        repo.save_user_settings(data)
        restored = repo.load_user_settings()
        assert restored["transparency_color"] is None


class TestSettingsRepositoryBoundary:
    """TC-SR-006〜010: 境界値テスト。"""

    def test_tc_sr_006_user_settings_not_found_returns_empty_dict(self) -> None:
        """TC-SR-006: user_settings.yaml が存在しないとき空辞書が返る（例外なし）。"""
        r = SettingsRepository(
            core_path=_CORE_YAML,
            user_path=Path("nonexistent_user.yaml"),
        )
        result = r.load_user_settings()
        assert result == {}

    def test_tc_sr_007_core_settings_not_found_returns_empty_dict(
        self, tmp_path: Path
    ) -> None:
        """TC-SR-007: core_settings.yaml が存在しないとき空辞書が返る（例外なし）。"""
        r = SettingsRepository(
            core_path=Path("nonexistent_core.yaml"),
            user_path=tmp_path / "user.yaml",
        )
        result = r.load_core_settings()
        assert result == {}

    def test_tc_sr_008_empty_yaml_file_returns_empty_dict(
        self, tmp_path: Path
    ) -> None:
        """TC-SR-008: 空の YAML ファイルを読み込むと空辞書が返る。"""
        user_yaml = tmp_path / "empty.yaml"
        user_yaml.write_text("", encoding="utf-8")
        r = SettingsRepository(core_path=_CORE_YAML, user_path=user_yaml)
        result = r.load_user_settings()
        assert result == {}

    def test_tc_sr_009_yaml_with_list_content_returns_empty_dict(
        self, tmp_path: Path
    ) -> None:
        """TC-SR-009: YAML の内容がリスト（辞書でない）のとき空辞書が返る。"""
        user_yaml = tmp_path / "list.yaml"
        user_yaml.write_text("- item1\n- item2\n", encoding="utf-8")
        r = SettingsRepository(core_path=_CORE_YAML, user_path=user_yaml)
        result = r.load_user_settings()
        assert result == {}

    def test_tc_sr_010_parent_dir_created_automatically(
        self, tmp_path: Path
    ) -> None:
        """TC-SR-010: 存在しない親ディレクトリ配下に user_path を指定しても保存が成功する。"""
        deep_path = tmp_path / "deep" / "nested" / "user.yaml"
        r = SettingsRepository(core_path=_CORE_YAML, user_path=deep_path)
        r.save_user_settings({"key": "value"})
        assert deep_path.exists()
        restored = r.load_user_settings()
        assert restored == {"key": "value"}
