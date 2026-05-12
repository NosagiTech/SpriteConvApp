from src.domain.services.image_converter import ImageConverter
from src.domain.entities.image_file import ImageFile
from src.domain.entities.conversion_settings import ConversionSettings
from pathlib import Path

FIXTURES = Path("tests/fixtures")
NORMAL   = FIXTURES / "normal"

f = ImageFile(path=NORMAL / "test_100x100.png", format="PNG")
s = ConversionSettings()
try:
    ImageConverter().convert(f, s, Path("tests/convert_result/TC-IC-018"))
    print("NG: 例外が発生しなかった")
except OSError as e:
    print(f"OK: OSError → {e}")