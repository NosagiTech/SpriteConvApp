$file = "$PWD\tests\fixtures\locked_settings.yaml"
"key: value" | Out-File -Encoding utf8 $file

# 現在のユーザの「読み取り」アクセス権を拒否に設定
$acl = Get-Acl $file
$rule = New-Object System.Security.AccessControl.FileSystemAccessRule(
  $env:USERNAME, "Read", "Deny"
)
$acl.AddAccessRule($rule)
Set-Acl $file $acl