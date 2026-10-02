$ErrorActionPreference = "Stop"
$root = Split-Path $PSScriptRoot -Parent
Set-Location "$root\app"
flutter pub get
flutter build windows --release
$bundle = "$root\app\build\windows\x64\runner\Release"
$engineSrc = "$root\dist\engine"
if (-not (Test-Path $engineSrc)) { throw "먼저 build_engine.ps1 실행 필요" }
Copy-Item -Recurse -Force $engineSrc "$bundle\engine"
Write-Host "앱 빌드 완료: $bundle (engine 번들 포함). 실행: $bundle\fsi_scanner_app.exe"
