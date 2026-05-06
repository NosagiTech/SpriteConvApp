$file = "$PWD\tests\fixtures\locked_settings.yaml"
$acl = Get-Acl $file
$rule = New-Object System.Security.AccessControl.FileSystemAccessRule(
  $env:USERNAME, "Read", "Deny"
)
$acl.RemoveAccessRule($rule)
Set-Acl $file $acl
Remove-Item $file