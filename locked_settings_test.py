from src.infra.settings_repository import SettingsRepository
from pathlib import Path

r = SettingsRepository(
    core_path=Path("core_settings.yaml"),
    user_path=Path("tests/fixtures/locked_settings.yaml"),
)
try:
    r.load_user_settings()
    print("NG: 例外が発生しなかった")
except OSError as e:
    print(f"OK: OSError → {e}")