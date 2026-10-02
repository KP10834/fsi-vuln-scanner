; FSI 취약점 분석 — Inno Setup 설치 스크립트
; 컴파일: ISCC.exe packaging\installer.iss
; 산출물: packaging\dist\FSI-Scanner-Setup.exe

#define MyAppName "FSI 취약점 분석"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Security Tooling"
#define MyAppExe "fsi_scanner_app.exe"
#define ReleaseDir "..\app\build\windows\x64\runner\Release"

[Setup]
AppId={{B7E2F1C4-9A3D-4E57-8C21-FSIVULNSCAN01}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\FSI Scanner
DefaultGroupName={#MyAppName}
UninstallDisplayName={#MyAppName}
UninstallDisplayIcon={app}\{#MyAppExe}
OutputDir=dist
OutputBaseFilename=FSI-Scanner-Setup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
ArchitecturesInstallIn64BitMode=x64compatible
ArchitecturesAllowed=x64compatible
DisableProgramGroupPage=yes

[Languages]
Name: "korean"; MessagesFile: "compiler:Languages\Korean.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
Source: "{#ReleaseDir}\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExe}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExe}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExe}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
