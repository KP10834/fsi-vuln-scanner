# Inno Setup으로 설치형 인스톨러(FSI-Scanner-Setup.exe) 생성.
# 사전: build_engine.ps1 + build_app.ps1 로 Release 번들이 준비돼 있어야 한다.
$ErrorActionPreference = "Stop"
$root = Split-Path $PSScriptRoot -Parent
$iss = Join-Path $PSScriptRoot "installer.iss"
$release = Join-Path $root "app\build\windows\x64\runner\Release\fsi_scanner_app.exe"
if (-not (Test-Path $release)) { throw "먼저 build_app.ps1 실행 필요 (Release 번들 없음)" }

$candidates = @(
  "$env:LOCALAPPDATA\Programs\Inno Setup 6\ISCC.exe",
  "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe",
  "$env:ProgramFiles\Inno Setup 6\ISCC.exe"
)
$iscc = $candidates | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $iscc) { throw "ISCC.exe 없음. Inno Setup 6 설치 필요: winget install -e --id JRSoftware.InnoSetup --source winget" }

& $iscc $iss
Write-Host "인스톨러 생성 완료: $(Join-Path $PSScriptRoot 'dist\FSI-Scanner-Setup.exe')"
