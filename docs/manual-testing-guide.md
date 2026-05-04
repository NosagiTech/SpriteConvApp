# 手動テスト実施手順書

`docs/test-cases.md` で **種別=手動** に分類されたテストケースの実施手順書。

> **自動テストとの使い分け**  
> 種別=自動のケース（105 件）は pytest で実行する。
>
> ```powershell
> # 仮想環境を有効化してから実行
> .venv\Scripts\Activate.ps1
> pytest tests/
> ```
>
> 本書の対象は、OS の権限操作を伴うため自動化が困難な **3 件** のみ。

---

## 対象テストケース一覧

| ID | 分類 | テスト名 | 対象ファイル |
|---|---|---|---|
| TC-IC-017 | 異常系 | 入力ファイルがロック中（OSError） | `src/domain/services/image_converter.py` |
| TC-IC-018 | 異常系 | 出力先の書き込み権限なし（OSError） | `src/domain/services/image_converter.py` |
| TC-SR-011 | 異常系 | 読み取り不可ファイル（OSError） | `src/infra/settings_repository.py` |

---

## 事前準備（共通）

```powershell
# プロジェクトルートへ移動
cd c:\Users\zat_a\claude_ws\SpriteConvApp

# 仮想環境の有効化（PowerShell）
.venv\Scripts\Activate.ps1

# Python 対話シェルを起動（プロジェクトルートから）
python
```

```python
# シェル起動後に一度だけ実行
from pathlib import Path
FIXTURES = Path("tests/fixtures")
NORMAL   = FIXTURES / "normal"
```

---

## TC-IC-017 入力ファイルがロック中（OSError）

**目的:** 別プロセスがロックしているファイルを変換しようとしたとき `OSError` が発生することを確認する。

### 手順

1. エクスプローラで `tests/fixtures/normal/test_100x100.png` を別の画像ビューア等で開いた状態にする
   （または PowerShell で下記のようにロックする）

   ```powershell
   # ロック用（別の PowerShell ウィンドウで実行し、そのままにしておく）
   $fs = [System.IO.File]::Open(
     "$PWD\tests\fixtures\normal\test_100x100.png",
     [System.IO.FileMode]::Open,
     [System.IO.FileAccess]::ReadWrite,
     [System.IO.FileShare]::None
   )
   ```

2. Python シェルで以下を実行する

   ```python
   from src.domain.services.image_converter import ImageConverter
   from src.domain.entities.image_file import ImageFile
   from src.domain.entities.conversion_settings import ConversionSettings

   f = ImageFile(path=NORMAL / "test_100x100.png", format="PNG")
   s = ConversionSettings()
   try:
       ImageConverter().convert(f, s, Path("tests/convert_result/TC-IC-017"))
       print("NG: 例外が発生しなかった")
   except OSError as e:
       print(f"OK: OSError → {e}")
   ```

3. ロックを解除する（画像ビューアを閉じる、または PowerShell で `$fs.Close()`）

**期待結果:** `OK: OSError →` に続いてエラーメッセージが表示される。

---

## TC-IC-018 出力先の書き込み権限なし（OSError）

**目的:** 書き込み不可ディレクトリへの保存試行時に `OSError` が発生することを確認する。

### 手順

1. PowerShell で出力先フォルダを作成し、書き込み権限を拒否に設定する

   ```powershell
   $dir = "$PWD\tests\convert_result\TC-IC-018"
   New-Item -ItemType Directory -Force -Path $dir

   # 現在のユーザの「書き込み」アクセス権を拒否に設定
   $acl = Get-Acl $dir
   $rule = New-Object System.Security.AccessControl.FileSystemAccessRule(
     $env:USERNAME, "Write", "Deny"
   )
   $acl.AddAccessRule($rule)
   Set-Acl $dir $acl
   ```

2. Python シェルで以下を実行する

   ```python
   from src.domain.services.image_converter import ImageConverter
   from src.domain.entities.image_file import ImageFile
   from src.domain.entities.conversion_settings import ConversionSettings

   f = ImageFile(path=NORMAL / "test_100x100.png", format="PNG")
   s = ConversionSettings()
   try:
       ImageConverter().convert(f, s, Path("tests/convert_result/TC-IC-018"))
       print("NG: 例外が発生しなかった")
   except OSError as e:
       print(f"OK: OSError → {e}")
   ```

3. PowerShell でアクセス権の拒否ルールを削除して元に戻す

   ```powershell
   $acl = Get-Acl $dir
   $rule = New-Object System.Security.AccessControl.FileSystemAccessRule(
     $env:USERNAME, "Write", "Deny"
   )
   $acl.RemoveAccessRule($rule)
   Set-Acl $dir $acl
   ```

**期待結果:** `OK: OSError →` に続いてエラーメッセージが表示される。

---

## TC-SR-011 読み取り不可ファイル（OSError）

**目的:** 読み取り権限を持たない YAML ファイルを読み込もうとしたとき `OSError` が発生することを確認する。

### 手順

1. PowerShell で一時的な YAML ファイルを作成し、読み取り権限を拒否に設定する

   ```powershell
   $file = "$PWD\tests\fixtures\locked_settings.yaml"
   "key: value" | Out-File -Encoding utf8 $file

   # 現在のユーザの「読み取り」アクセス権を拒否に設定
   $acl = Get-Acl $file
   $rule = New-Object System.Security.AccessControl.FileSystemAccessRule(
     $env:USERNAME, "Read", "Deny"
   )
   $acl.AddAccessRule($rule)
   Set-Acl $file $acl
   ```

2. Python シェルで以下を実行する

   ```python
   from src.infra.settings_repository import SettingsRepository

   r = SettingsRepository(
       core_path=Path("core_settings.yaml"),
       user_path=Path("tests/fixtures/locked_settings.yaml"),
   )
   try:
       r.load_user_settings()
       print("NG: 例外が発生しなかった")
   except OSError as e:
       print(f"OK: OSError → {e}")
   ```

3. PowerShell でアクセス権の拒否ルールを削除し、ファイルも削除する

   ```powershell
   $acl = Get-Acl $file
   $rule = New-Object System.Security.AccessControl.FileSystemAccessRule(
     $env:USERNAME, "Read", "Deny"
   )
   $acl.RemoveAccessRule($rule)
   Set-Acl $file $acl
   Remove-Item $file
   ```

**期待結果:** `OK: OSError →` に続いてエラーメッセージが表示される。

---

## テスト完了後の作業

各テストの実施後、`docs/test-cases.md` の該当行の `[ ]` を `[x]` に変更すること。
