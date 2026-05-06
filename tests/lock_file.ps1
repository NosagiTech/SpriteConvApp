# ロック用（別の PowerShell ウィンドウで実行し、そのままにしておく）
$fs = [System.IO.File]::Open(
  "$PWD\tests\fixtures\normal\test_100x100.png",
  [System.IO.FileMode]::Open,
  [System.IO.FileAccess]::ReadWrite,
  [System.IO.FileShare]::None
)

pause

$fs.Close()