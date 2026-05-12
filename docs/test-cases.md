# SpriteConvApp テストケース一覧

要件定義書および実装コードをもとに、各コンポーネントのテストケースを列挙する。

## 凡例

- **完了**: `[ ]` 未実施 / `[x]` 実施済み
- **ID**: `TC-<カテゴリ>-<3桁連番>` 形式
- **分類**: 正常系 / 境界値 / 異常系
- **種別**:
  - `自動` — pytest で実装済み。`pytest tests/` で実行する
  - `手動` — OS の権限操作など自動化が困難なケース。`docs/manual-testing-guide.md` の手順に従う
- **入力条件**: テスト実施時に与える値や状態
- **期待結果**: 正しく動作した場合の出力・副作用・例外

---

## 1. Color（バリューオブジェクト）

対象ファイル: `src/domain/value_objects/color.py`  
pytest ファイル: `tests/domain/test_color.py`

| 完了 | ID | 分類 | 種別 | テスト名 | 入力条件 | 期待結果 |
|:---:|---|---|:---:|---|---|---|
| [x] | TC-CLR-001 | 正常系 | 自動 | 最小値で生成 | `Color(0, 0, 0)` | 例外なく生成される |
| [x] | TC-CLR-002 | 正常系 | 自動 | 最大値で生成 | `Color(255, 255, 255)` | 例外なく生成される |
| [x] | TC-CLR-003 | 正常系 | 自動 | 任意の有効値で生成 | `Color(0, 128, 255)` | 例外なく生成される |
| [x] | TC-CLR-004 | 正常系 | 自動 | to_tuple() の戻り値 | `Color(10, 20, 30).to_tuple()` | `(10, 20, 30)` が返る |
| [x] | TC-CLR-005 | 正常系 | 自動 | イミュータブル確認 | `Color(1, 2, 3).r = 9` | `FrozenInstanceError` が発生する |
| [x] | TC-CLR-006 | 境界値 | 自動 | r=0（下限） | `Color(r=0, g=100, b=100)` | 例外なく生成される |
| [x] | TC-CLR-007 | 境界値 | 自動 | r=255（上限） | `Color(r=255, g=100, b=100)` | 例外なく生成される |
| [x] | TC-CLR-008 | 境界値 | 自動 | g=0（下限） | `Color(r=100, g=0, b=100)` | 例外なく生成される |
| [x] | TC-CLR-009 | 境界値 | 自動 | g=255（上限） | `Color(r=100, g=255, b=100)` | 例外なく生成される |
| [x] | TC-CLR-010 | 境界値 | 自動 | b=0（下限） | `Color(r=100, g=100, b=0)` | 例外なく生成される |
| [x] | TC-CLR-011 | 境界値 | 自動 | b=255（上限） | `Color(r=100, g=100, b=255)` | 例外なく生成される |
| [x] | TC-CLR-012 | 異常系 | 自動 | r が下限未満 | `Color(r=-1, g=0, b=0)` | `ValueError` が発生する |
| [x] | TC-CLR-013 | 異常系 | 自動 | r が上限超過 | `Color(r=256, g=0, b=0)` | `ValueError` が発生する |
| [x] | TC-CLR-014 | 異常系 | 自動 | g が下限未満 | `Color(r=0, g=-1, b=0)` | `ValueError` が発生する |
| [x] | TC-CLR-015 | 異常系 | 自動 | g が上限超過 | `Color(r=0, g=256, b=0)` | `ValueError` が発生する |
| [x] | TC-CLR-016 | 異常系 | 自動 | b が下限未満 | `Color(r=0, g=0, b=-1)` | `ValueError` が発生する |
| [x] | TC-CLR-017 | 異常系 | 自動 | b が上限超過 | `Color(r=0, g=0, b=256)` | `ValueError` が発生する |
| [x] | TC-CLR-018 | 異常系 | 自動 | r のみ極端に大きい値 | `Color(r=300, g=0, b=0)` | `ValueError` が発生する |

---

## 2. ConversionSettings（エンティティ）

対象ファイル: `src/domain/entities/conversion_settings.py`  
pytest ファイル: `tests/domain/test_conversion_settings.py`

| 完了 | ID | 分類 | 種別 | テスト名 | 入力条件 | 期待結果 |
|:---:|---|---|:---:|---|---|---|
| [x] | TC-CS-001 | 正常系 | 自動 | デフォルト値で生成 | `ConversionSettings()` | `output_format="PNG"`, `scale=1.0`, `use_antialias=True`, `transparency_color=None`, `tolerance=0` |
| [x] | TC-CS-002 | 正常系 | 自動 | フォーマット=PNG | `ConversionSettings(output_format="PNG")` | 例外なく生成される |
| [x] | TC-CS-003 | 正常系 | 自動 | フォーマット=JPEG | `ConversionSettings(output_format="JPEG")` | 例外なく生成される |
| [x] | TC-CS-004 | 正常系 | 自動 | フォーマット=TIFF | `ConversionSettings(output_format="TIFF")` | 例外なく生成される |
| [x] | TC-CS-005 | 正常系 | 自動 | フォーマット=GIF | `ConversionSettings(output_format="GIF")` | 例外なく生成される |
| [x] | TC-CS-006 | 正常系 | 自動 | フォーマット=BMP | `ConversionSettings(output_format="BMP")` | 例外なく生成される |
| [x] | TC-CS-007 | 正常系 | 自動 | transparency_color=None | `ConversionSettings(transparency_color=None)` | 例外なく生成される |
| [x] | TC-CS-008 | 正常系 | 自動 | transparency_color に Color を指定 | `ConversionSettings(transparency_color=Color(0,255,0))` | 例外なく生成される |
| [x] | TC-CS-009 | 境界値 | 自動 | scale の最小正当値 | `ConversionSettings(scale=0.01)` | 例外なく生成される |
| [x] | TC-CS-010 | 境界値 | 自動 | scale の最大正当値 | `ConversionSettings(scale=100.0)` | 例外なく生成される |
| [x] | TC-CS-011 | 境界値 | 自動 | tolerance の下限 | `ConversionSettings(tolerance=0)` | 例外なく生成される |
| [x] | TC-CS-012 | 境界値 | 自動 | tolerance の上限 | `ConversionSettings(tolerance=255)` | 例外なく生成される |
| [x] | TC-CS-013 | 異常系 | 自動 | 未対応フォーマット | `ConversionSettings(output_format="WEBP")` | `ValueError` が発生する |
| [x] | TC-CS-014 | 異常系 | 自動 | 空文字フォーマット | `ConversionSettings(output_format="")` | `ValueError` が発生する |
| [x] | TC-CS-015 | 異常系 | 自動 | 小文字フォーマット | `ConversionSettings(output_format="png")` | `ValueError` が発生する |
| [x] | TC-CS-016 | 異常系 | 自動 | scale=0 | `ConversionSettings(scale=0)` | `ValueError` が発生する |
| [x] | TC-CS-017 | 異常系 | 自動 | scale が負値 | `ConversionSettings(scale=-1.0)` | `ValueError` が発生する |
| [x] | TC-CS-018 | 異常系 | 自動 | tolerance が下限未満 | `ConversionSettings(tolerance=-1)` | `ValueError` が発生する |
| [x] | TC-CS-019 | 異常系 | 自動 | tolerance が上限超過 | `ConversionSettings(tolerance=256)` | `ValueError` が発生する |

---

## 3. ImageConverter（ドメインサービス）

対象ファイル: `src/domain/services/image_converter.py`  
pytest ファイル: `tests/domain/test_image_converter.py`

| 完了 | ID | 分類 | 種別 | テスト名 | 入力条件 | 期待結果 | 備考 |
|:---:|---|---|:---:|---|---|---|---|
| [x] | TC-IC-001 | 正常系 | 自動 | PNG→PNG 原寸変換 | PNG 画像, `scale=1.0`, `output_format="PNG"` | 同サイズの PNG ファイルが出力先に保存される |
| [x] | TC-IC-002 | 正常系 | 自動 | PNG→JPEG 変換（RGBA画像） | RGBA モード PNG, `output_format="JPEG"` | 白背景合成された JPEG が保存される（透過なし） |
| [x] | TC-IC-003 | 正常系 | 自動 | PNG→BMP 変換（RGBA画像） | RGBA モード PNG, `output_format="BMP"` | RGB に変換された BMP が保存される |
| [x] | TC-IC-004 | 正常系 | 自動 | GIF→PNG（アニメーション GIF） | アニメーション GIF, `output_format="PNG"` | 先頭フレームのみが PNG に変換される |
| [x] | TC-IC-005 | 正常系 | 自動 | 拡大リサイズ（scale=2.0） | 100x100 px PNG, `scale=2.0` | 200x200 px の出力ファイルになる |
| [x] | TC-IC-006 | 正常系 | 自動 | 縮小リサイズ（scale=0.5） | 100x100 px PNG, `scale=0.5` | 50x50 px の出力ファイルになる |
| [x] | TC-IC-007 | 正常系 | 自動 | LANCZOS（アンチエイリアス=True） | PNG, `use_antialias=True`, `scale=2.0` | LANCZOS でリサイズされたファイルが保存される |
| [x] | TC-IC-008 | 正常系 | 自動 | NEAREST（アンチエイリアス=False） | PNG, `use_antialias=False`, `scale=2.0` | NEAREST でリサイズされたファイルが保存される |
| [x] | TC-IC-009 | 正常系 | 自動 | 透過色の完全一致除去 | 白背景 PNG, `transparency_color=Color(255,255,255)`, `tolerance=0` | 白ピクセルがすべてアルファ=0 になる |
| [x] | TC-IC-010 | 正常系 | 自動 | 透過色の許容誤差あり | 白近似背景 PNG, `transparency_color=Color(255,255,255)`, `tolerance=10` | 許容範囲内の白系ピクセルが透明化される |
| [x] | TC-IC-011 | 正常系 | 自動 | 出力先フォルダが未存在 | 存在しない出力ディレクトリを指定 | ディレクトリが自動作成され、ファイルが保存される |
| [x] | TC-IC-012 | 正常系 | 自動 | 出力ファイル名は元ファイルの stem に準拠 | 入力ファイル名 `test_100x100.png`, `output_format="JPEG"` | 出力ファイル名が `test_100x100.jpg` になる |
| [x] | TC-IC-013 | 境界値 | 自動 | 最小倍率（scale=0.01）でも1px保証 | 10x10 px PNG, `scale=0.01` | 出力サイズが最低 1x1 px になる（クラッシュしない） |
| [x] | TC-IC-014 | 境界値 | 自動 | scale=1.0 のとき resize をスキップ | PNG, `scale=1.0` | リサイズ処理が呼ばれない（画像サイズが変わらない） |
| [x] | TC-IC-015 | 境界値 | 自動 | tolerance=0 で完全一致のみ透明化 | 背景色と 1 違いのピクセルを含む PNG, `tolerance=0` | 完全一致ピクセルのみ透明化され、隣接色は不変 |
| [x] | TC-IC-016 | 境界値 | 自動 | tolerance=255 で全ピクセル透明化 | カラー PNG, `transparency_color=Color(0,0,0)`, `tolerance=255` | すべてのピクセルが透明化される |
| [x] | TC-IC-017 | 異常系 | 手動 | 入力ファイルがロック中（OSError） | 他プロセスがロックしたファイルを読み込み | `OSError` が発生する | 変換時でなく読み込み時に補足することを確認済
| [x] | TC-IC-018 | 異常系 | 手動 | 出力先の書き込み権限なし | 書き込み不可ディレクトリへの保存 | `OSError`（またはその派生例外）が発生する |

---

## 4. ImageFileLoader（インフラ層）

対象ファイル: `src/infra/image_file_loader.py`  
pytest ファイル: `tests/infra/test_image_file_loader.py`

| 完了 | ID | 分類 | 種別 | テスト名 | 入力条件 | 期待結果 |
|:---:|---|---|:---:|---|---|---|
| [x] | TC-IFL-001 | 正常系 | 自動 | PNG ファイルを直接指定 | 有効な PNG ファイルのパス | `[ImageFile(path=..., format="PNG")]` が返る |
| [x] | TC-IFL-002 | 正常系 | 自動 | JPEG ファイルを直接指定 | 有効な JPG ファイルのパス | `format="JPEG"` の `ImageFile` が返る |
| [x] | TC-IFL-003 | 正常系 | 自動 | GIF ファイルを直接指定 | 有効な GIF ファイルのパス | `format="GIF"` の `ImageFile` が返る |
| [x] | TC-IFL-004 | 正常系 | 自動 | 複数画像を含むフォルダ指定 | 画像ファイルが複数入ったフォルダ | 全件の `ImageFile` リストが返る |
| [x] | TC-IFL-005 | 正常系 | 自動 | サブフォルダを含むフォルダ指定 | ルート + サブフォルダに画像が分散したフォルダ | 再帰的に全件が収集される |
| [x] | TC-IFL-006 | 正常系 | 自動 | 大文字拡張子のファイル（.PNG） | 拡張子が `.PNG` のファイル | 収集対象として認識される |
| [x] | TC-IFL-007 | 正常系 | 自動 | 大文字拡張子のファイル（.JPG） | 拡張子が `.JPG` のファイル | 収集対象として認識される |
| [x] | TC-IFL-008 | 境界値 | 自動 | 空のフォルダを指定 | 画像ファイルが 0 件のフォルダ | 空リスト `[]` が返る |
| [x] | TC-IFL-009 | 境界値 | 自動 | 対象外拡張子のみのフォルダ | `.txt`, `.csv` のみのフォルダ | 空リスト `[]` が返る |
| [x] | TC-IFL-010 | 境界値 | 自動 | .txt ファイルを直接指定 | 拡張子 `.txt` のファイルのパス | 空リスト `[]` が返る（スキップ） |
| [x] | TC-IFL-011 | 境界値 | 自動 | フォルダに対象外と対象が混在 | `.png` と `.txt` が混在するフォルダ | `.png` のみが返る |
| [x] | TC-IFL-012 | 異常系 | 自動 | 存在しないパスを指定 | 存在しないファイルパス | `FileNotFoundError` が発生する |
| [x] | TC-IFL-013 | 異常系 | 自動 | 破損した画像ファイルを指定 | Pillow で開けない壊れた PNG ファイル | スキップされ、空リスト `[]` が返る |
| [x] | TC-IFL-014 | 異常系 | 自動 | .png 拡張子だが内容はテキスト | 内容がテキストの `.png` ファイル | `UnidentifiedImageError` をキャッチしスキップされる |

---

## 5. SettingsRepository（インフラ層）

対象ファイル: `src/infra/settings_repository.py`  
pytest ファイル: `tests/infra/test_settings_repository.py`

| 完了 | ID | 分類 | 種別 | テスト名 | 入力条件 | 期待結果 | 備考 |
|:---:|---|---|:---:|---|---|---|---|
| [x] | TC-SR-001 | 正常系 | 自動 | core_settings.yaml の読み込み | 有効な `core_settings.yaml` | `scale`, `thumbnail`, `transparency` キーを含む辞書が返る |
| [x] | TC-SR-002 | 正常系 | 自動 | user_settings.yaml の読み込み | 有効な `user_settings.yaml` | 保存済みのキーと値が辞書として返る |
| [x] | TC-SR-003 | 正常系 | 自動 | save → load で値が復元される | 任意の辞書を `save_user_settings()` した後 `load_user_settings()` | 保存した辞書と同一の辞書が返る |
| [x] | TC-SR-004 | 正常系 | 自動 | 日本語値の保存・復元 | `{"output_dir": "C:/Users/テスト"}` を save | load 後も同一文字列が返る（UTF-8 保証） |
| [x] | TC-SR-005 | 正常系 | 自動 | None 値の保存・復元 | `{"transparency_color": None}` を save | load 後も `None` が返る |
| [x] | TC-SR-006 | 境界値 | 自動 | ユーザ設定ファイルが存在しない | `user_settings.yaml` が存在しない状態で `load_user_settings()` | 空辞書 `{}` が返る（例外なし） |
| [x] | TC-SR-007 | 境界値 | 自動 | コア設定ファイルが存在しない | `core_settings.yaml` が存在しない状態で `load_core_settings()` | 空辞書 `{}` が返る（例外なし） |
| [x] | TC-SR-008 | 境界値 | 自動 | YAML の内容が空（ファイルは存在するが 0 バイト） | 空の YAML ファイルを `load_user_settings()` | 空辞書 `{}` が返る |
| [x] | TC-SR-009 | 境界値 | 自動 | YAML の内容がリスト（辞書でない） | `- item1\n- item2` が書かれた YAML ファイル | 空辞書 `{}` が返る |
| [x] | TC-SR-010 | 境界値 | 自動 | 出力先親ディレクトリが存在しない | 存在しないディレクトリ配下を `user_path` に指定して save | 親ディレクトリが自動作成され、保存成功する |
| [x] | TC-SR-011 | 異常系 | 手動 | 読み取り不可ファイル | 権限を除去した YAML ファイルを load | `OSError`（またはその派生例外）が発生する | 使用ファイル: xxx_locked_yaml.ps1, locked_settings_test.py

---

## 6. LoadImagesUseCase（アプリケーション層）

対象ファイル: `src/application/use_cases/load_images_use_case.py`  
pytest ファイル: `tests/application/test_load_images_use_case.py`

| 完了 | ID | 分類 | 種別 | テスト名 | 入力条件 | 期待結果 |
|:---:|---|---|:---:|---|---|---|
| [x] | TC-LI-001 | 正常系 | 自動 | 有効なファイルパス 1 件 | `[valid_png_path]` | 1 件の `ImageFile` リストが返る |
| [x] | TC-LI-002 | 正常系 | 自動 | 有効なフォルダパス | `[valid_folder_path]`（画像複数件含む） | 全件の `ImageFile` リストが返る |
| [x] | TC-LI-003 | 正常系 | 自動 | 複数ファイルパス | `[png_path, jpg_path]` | 2 件の `ImageFile` リストが返る |
| [x] | TC-LI-004 | 正常系 | 自動 | warning_cb なしで不正パスが混在 | `[invalid_path]`, `warning_cb=None` | 空リスト `[]` が返り、クラッシュしない |
| [x] | TC-LI-005 | 正常系 | 自動 | warning_cb ありで不正パスが混在 | `[invalid_path]`, `warning_cb=記録用コールバック` | `warning_cb` が呼ばれ、メッセージに "[警告]" が含まれる |
| [x] | TC-LI-006 | 境界値 | 自動 | 空リストを渡す | `path_list=[]` | 空リスト `[]` が返る |
| [x] | TC-LI-007 | 境界値 | 自動 | 同じファイルパスを 2 回渡す | `[png_path, png_path]` | 重複を除き 1 件のみが返る |
| [x] | TC-LI-008 | 境界値 | 自動 | ファイルとフォルダが混在し、重複あり | フォルダ内の画像ファイルを個別にも指定 | 重複を除いた件数のリストが返る |
| [x] | TC-LI-009 | 境界値 | 自動 | 有効ファイルと存在しないパスが混在 | `[valid_path, invalid_path]` | 有効ファイルのみが返る |
| [x] | TC-LI-010 | 異常系 | 自動 | 全件存在しないパス | `[invalid_path1, invalid_path2]` | 空リスト `[]` が返る（例外を外に出さない） |

---

## 7. ConvertImagesUseCase（アプリケーション層）

対象ファイル: `src/application/use_cases/convert_images_use_case.py`  
pytest ファイル: `tests/application/test_convert_images_use_case.py`

| 完了 | ID | 分類 | 種別 | テスト名 | 入力条件 | 期待結果 |
|:---:|---|---|:---:|---|---|---|
| [x] | TC-CI-001 | 正常系 | 自動 | 全件正常変換 | 3 件のファイル、変換が全件成功 | `success_count=3`, `error_list=[]` |
| [x] | TC-CI-002 | 正常系 | 自動 | progress_cb の呼び出し回数 | 3 件のファイル、`progress_cb` を記録するモック | `progress_cb` が 3 回呼ばれる |
| [x] | TC-CI-003 | 正常系 | 自動 | progress_cb の引数（current） | 3 件のファイル | `current` が 1, 2, 3 の順に渡される |
| [x] | TC-CI-004 | 正常系 | 自動 | progress_cb の引数（total） | 3 件のファイル | `total` が常に 3 で渡される |
| [x] | TC-CI-005 | 境界値 | 自動 | files が空リスト | `files=[]` | `success_count=0`, `error_list=[]`, `progress_cb` 呼ばれない |
| [x] | TC-CI-006 | 境界値 | 自動 | progress_cb=None | `progress_cb=None` | クラッシュせず正常に変換結果が返る |
| [x] | TC-CI-007 | 境界値 | 自動 | 1 件のみ変換 | 1 件のファイル | `progress_cb(current=1, total=1)` が 1 回呼ばれる |
| [x] | TC-CI-008 | 異常系 | 自動 | 変換失敗（OSError）が 1 件発生 | 3 件中 1 件が OSError を発生させるモック | `success_count=2`, `error_list` に 1 件の `ErrorItem` が含まれる |
| [x] | TC-CI-009 | 異常系 | 自動 | エラー後も処理が継続する | 1 件目が失敗、2 件目が成功 | 2 件目の変換が実行される |
| [x] | TC-CI-010 | 異常系 | 自動 | 全件失敗 | 全ファイルが例外を発生させるモック | `success_count=0`, `len(error_list)=全件数` |
| [x] | TC-CI-011 | 異常系 | 自動 | エラー発生時も progress_cb が呼ばれる | 失敗するファイルがある | 失敗した件に対しても `progress_cb` が呼ばれる（`finally` 保証） |
| [x] | TC-CI-012 | 異常系 | 自動 | ErrorItem のフィールド確認 | 1 件が OSError(`"ファイルが開けません"`) で失敗 | `ErrorItem.file_path` が対象ファイルのパス、`error_message` が `"ファイルが開けません"` |

---

## 8. ConversionResult / ErrorItem（DTO）

対象ファイル: `src/application/dto/conversion_result.py`, `src/application/dto/error_item.py`  
pytest ファイル: `tests/application/test_dto.py`

| 完了 | ID | 分類 | 種別 | テスト名 | 入力条件 | 期待結果 |
|:---:|---|---|:---:|---|---|---|
| [x] | TC-DTO-001 | 正常系 | 自動 | エラーなし時の has_errors | `ConversionResult(success_count=5, error_list=[])` | `has_errors == False` |
| [x] | TC-DTO-002 | 正常系 | 自動 | エラーあり時の has_errors | `ConversionResult(success_count=3, error_list=[ErrorItem(...)])` | `has_errors == True` |
| [x] | TC-DTO-003 | 正常系 | 自動 | total_count の算出 | `success_count=4`, `error_list` に 2 件 | `total_count == 6` |
| [x] | TC-DTO-004 | 正常系 | 自動 | ErrorItem のフィールド確認 | `ErrorItem(file_path=Path("a.png"), error_message="エラー")` | `file_path` と `error_message` が正しく保持される |
| [x] | TC-DTO-005 | 境界値 | 自動 | 全件成功（error_list 空） | `ConversionResult(success_count=10, error_list=[])` | `total_count=10`, `has_errors=False` |
| [x] | TC-DTO-006 | 境界値 | 自動 | 全件失敗（success_count=0） | `ConversionResult(success_count=0, error_list=[item1, item2])` | `total_count=2`, `has_errors=True` |
| [x] | TC-DTO-007 | 境界値 | 自動 | 0 件処理（空） | `ConversionResult(success_count=0, error_list=[])` | `total_count=0`, `has_errors=False` |
| [x] | TC-DTO-008 | 境界値 | 自動 | イミュータブル確認（ConversionResult） | `result.success_count = 99` | `FrozenInstanceError` が発生する |
| [x] | TC-DTO-009 | 境界値 | 自動 | イミュータブル確認（ErrorItem） | `item.error_message = "改ざん"` | `FrozenInstanceError` が発生する |
