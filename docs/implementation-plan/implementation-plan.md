# SpriteConvApp 実装計画

## Context

2Dゲーム開発チームが画像素材の前処理（形式変換・リサイズ・透過）を自動化するデスクトップツール。
PySide6 + Pillow + PyYAML を使用し、レイヤードアーキテクチャで設計する。

---

## ディレクトリ・ファイル構成（最終形）

```
SpriteConvApp/
├── main.py                          # エントリポイント
├── requirements.txt
├── core_settings.yaml               # コア設定（ユーザが手動編集可能）
├── user_settings.yaml               # ユーザ設定（アプリが自動保存）
├── src/
│   ├── domain/
│   │   ├── entities/
│   │   │   ├── image_file.py        # 変換対象ファイルのエンティティ
│   │   │   └── conversion_settings.py  # 変換設定（形式・倍率・透過色・AA）
│   │   ├── value_objects/
│   │   │   └── color.py             # RGB値のバリューオブジェクト
│   │   ├── services/
│   │   │   └── image_converter.py   # Pillow使用の変換ロジック（純粋関数的）
│   │   └── repositories/
│   │       ├── i_settings_repository.py   # 設定リポジトリのインタフェース
│   │       └── i_image_loader.py          # 画像ローダのインタフェース
│   ├── application/
│   │   ├── dto/
│   │   │   ├── conversion_result.py # 変換結果DTO（成功・失敗リスト）
│   │   │   └── error_item.py        # エラー1件のDTO
│   │   └── use_cases/
│   │       ├── load_images_use_case.py    # ファイル/フォルダ→ImageFileリスト
│   │       └── convert_images_use_case.py # 変換実行（スレッド外から呼ばれる）
│   ├── infra/
│   │   ├── settings_repository.py   # YAML読み書き（ISettingsRepository実装）
│   │   └── image_file_loader.py     # ファイルシステム操作（IImageLoader実装）
│   └── interface/
│       ├── main_window.py           # メインウィンドウ（全体レイアウト管理）
│       ├── view_models/
│       │   └── main_view_model.py   # UI↔アプリ層の橋渡し（Qt Signals経由）
│       ├── widgets/
│       │   ├── control_panel.py     # 左パネル（操作系ウィジェット群）
│       │   ├── thumbnail_view.py    # サムネイルグリッド（仮想スクロール）
│       │   └── log_view.py          # ログ表示ウィジェット
│       └── dialogs/
│           ├── color_picker_dialog.py  # 透過色指定ポップアップ
│           ├── result_dialog.py        # 処理完了ポップアップ
│           └── error_list_dialog.py    # エラー一覧ポップアップ
```

---

## 実装フェーズ

### Phase 1: 環境構築・プロジェクト骨格

**作業内容:**
- `pip install PySide6 Pillow PyYAML` → `requirements.txt` 生成
- `src/` 以下の全ディレクトリと `__init__.py` 作成
- `core_settings.yaml` 作成（コア設定値を記述）
- `main.py` 作成（アプリ起動の骨格のみ）

**core_settings.yaml の内容:**
```yaml
scale:
  min: 0.01
  max: 100.0
  step_direct: 0.01
  step_arrow: 0.1
  truncate_fraction: false
thumbnail:
  min_size: 64
  max_size: 256
transparency:
  tolerance: 0
  tolerance_min: 0
  tolerance_max: 255
```

---

### Phase 2: Domain 層

**`domain/value_objects/color.py`**
- `Color(r, g, b)` dataclass。0〜255のバリデーション付き。

**`domain/entities/image_file.py`**
- `ImageFile`: `path: Path`, `format: str` などを持つデータクラス。

**`domain/entities/conversion_settings.py`**
- `ConversionSettings`: `output_format`, `scale`, `use_antialias`, `transparency_color: Color | None`, `tolerance: int`

**`domain/repositories/i_settings_repository.py`**
- `ISettingsRepository` 抽象基底クラス: `load_user_settings()`, `save_user_settings()`, `load_core_settings()`

**`domain/repositories/i_image_loader.py`**
- `IImageLoader` 抽象基底クラス: `load_from_path(path) -> list[ImageFile]`

**`domain/services/image_converter.py`**
- `ImageConverter` クラス: Pillow使用。
  - `convert(image_file, settings, output_dir) -> Path`
  - GIFは1フレーム目のみ処理
  - 透過色指定時は `Image.convert("RGBA")` + フラッドフィル方式で tolerance 対応

---

### Phase 3: Infrastructure 層

**`infra/settings_repository.py`**
- `SettingsRepository(core_path, user_path)`: コンストラクタで両パスを受け取る。
- `core_settings.yaml` / `user_settings.yaml` を PyYAML で読み書き。
- `ISettingsRepository` の実装。

**`infra/image_file_loader.py`**
- `ImageFileLoader`: `IImageLoader` の実装。
- `load_from_path()`: パスがファイルなら1件、フォルダなら対象拡張子のファイルを再帰的に収集。
- 対象拡張子: `.png .jpg .jpeg .tiff .tif .gif .bmp`

---

### Phase 4: Application 層

**`application/use_cases/load_images_use_case.py`**
- `LoadImagesUseCase(loader: IImageLoader)`
- `execute(path_list: list[Path]) -> list[ImageFile]`
- 不正ファイル（拡張子不一致）はスキップし警告リストに追加。

**`application/use_cases/convert_images_use_case.py`**
- `ConvertImagesUseCase(converter: ImageConverter)`
- `execute(files, settings, output_dir, progress_cb) -> ConversionResult`
- 1ファイルずつ処理し、例外はすべてキャッチして `error_list` に蓄積。
- `progress_cb(current, total)` で呼び出し元へ進捗通知。

**`application/dto/`**
- `ConversionResult(success_count, error_list: list[ErrorItem])`
- `ErrorItem(file_path, error_message)`

---

### Phase 5: Interface 層

**`interface/view_models/main_view_model.py`**
- `MainViewModel(QObject)`: Qt Signal を使いUIとアプリ層を接続。
  - シグナル: `progress_updated(int, int)`, `conversion_finished(ConversionResult)`, `images_loaded(list[ImageFile])`, `log_message(str)`
  - `start_conversion()`: `threading.Thread` でユースケースを起動。

**`interface/widgets/control_panel.py`**
- `ControlPanel(QWidget)`: 左パネル
  - ファイル/フォルダ読み込みボタン + パス表示
  - 出力先フォルダ指定ボタン + パス表示
  - 出力形式ドロップダウン（PNG/JPG/TIFF/GIF/BMP）
  - 透過色指定ボタン（PNG選択時のみ有効）
  - 倍率スピンボックス + アンチエイリアスチェックボックス
  - 実行ボタン（バリデーション状態に連動）

**`interface/widgets/thumbnail_view.py`**
- `ThumbnailView(QScrollArea)`: 仮想スクロール対応のサムネイルグリッド
  - `QScrollArea` + カスタム `FlowLayout` でラップ折り返し
  - 表示領域に入った時だけ `QThread` でサムネイルをロード（仮想化）
  - ローディング中はスピナーアイコン表示
  - クリックで OS 標準ビュアー起動（`QDesktopServices.openUrl`）

**`interface/widgets/log_view.py`**
- `LogView(QPlainTextEdit)`: 読み取り専用・折り返しあり・縦スクロールバー付き

**`interface/dialogs/color_picker_dialog.py`**
- `ColorPickerDialog(QDialog)`:
  - RGB 各値スピンボックス
  - HSV カラーピッカー（`QColorDialog` ベース or カスタム）
  - スポイトツール（`QScreen.grabWindow` + クロスヘアカーソル）
  - カラープレビューラベル

**`interface/dialogs/result_dialog.py`** / **`error_list_dialog.py`**
- 正常完了: OK ボタンのみ
- エラーあり: 「OK」「エラー一覧を表示」ボタン
- エラー一覧: ファイル名・エラー内容・パス・エクスプローラで開くボタン

**`interface/main_window.py`**
- `MainWindow(QMainWindow)`: 水平 `QSplitter` で左右パネルを配置
- 右パネルは垂直 `QSplitter` でサムネイル/ログを分割
- `MainViewModel` を受け取り、シグナルとスロットを接続

---

### Phase 6: 起動・依存注入・設定保存

**`main.py`**
```python
# 依存をここで組み立て（Composition Root）
settings_repo = SettingsRepository("core_settings.yaml", "user_settings.yaml")
loader = ImageFileLoader()
converter = ImageConverter()
load_uc = LoadImagesUseCase(loader)
convert_uc = ConvertImagesUseCase(converter)
view_model = MainViewModel(load_uc, convert_uc, settings_repo)
window = MainWindow(view_model)
```

**ユーザ設定の自動保存:**
- 各設定変更シグナル発火時に `SettingsRepository.save_user_settings()` を呼ぶ。
- 起動時に `load_user_settings()` で前回値を復元。

---

## 実装順序（推奨）

1. Phase 1（環境・骨格）
2. Phase 2（Domain）
3. Phase 3（Infra）
4. Phase 4（Application）
5. Phase 5 - ウィジェット群（MainWindow → ControlPanel → LogView → ThumbnailView → Dialogs）
6. Phase 6（main.py で組み立て・疎通確認）

---

## 検証方法

- `python main.py` でアプリ起動確認
- PNG/JPG/GIF を混在させてフォルダ読み込み → サムネイル表示確認
- 倍率・形式変更後に変換実行 → 出力フォルダのファイルを確認
- 存在しない出力先・ロックされたファイルを使い、エラー一覧ポップアップを確認
- `user_settings.yaml` が設定変更のたびに更新されることを確認
- アプリ再起動後に前回設定が復元されることを確認
