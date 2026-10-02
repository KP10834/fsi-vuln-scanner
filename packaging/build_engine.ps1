# 엔진을 onedir(.exe + _internal)로 빌드해 Flutter 번들에 복사
$ErrorActionPreference = "Stop"
$root = Split-Path $PSScriptRoot -Parent
Set-Location $root
# Python 런타임 선택: py -3.13 우선, 없으면 PATH의 python 사용
$use313 = $false
try { & py -3.13 -c "import sys" 2>&1 | Out-Null; if ($LASTEXITCODE -eq 0) { $use313 = $true } } catch {}
$piArgs = @(
  "-m", "PyInstaller", "--noconfirm", "--onedir", "--name", "engine",
  "--add-data", "engine/criteria/fsi_2026_mapping.json;engine/criteria",
  "engine/engine_cli.py")
if ($use313) { & py -3.13 @piArgs } else { & python @piArgs }
Write-Host "엔진 빌드 완료: dist/engine/engine.exe"
