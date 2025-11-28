; installer.iss - Inno Setup script for Mise

[Setup]
AppId={{fa98809b-2fa6-4884-88b7-4cc33e314996}
AppName=Mise
AppVersion=0.1.2
AppPublisher=Timothy Elder
DefaultDirName={pf}\Mise
DefaultGroupName=Mise
OutputBaseFilename=Mise-0.1.2-setup
Compression=lzma
SolidCompression=yes
DisableDirPage=no
DisableProgramGroupPage=no
SetupIconFile=src\mise\assets\mise.ico

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop icon"; GroupDescription: "Additional icons:"; Flags: unchecked

[Files]
; Copy the entire PyInstaller output folder
Source: "dist\*"; DestDir: "{app}"; Flags: recursesubdirs

[Icons]
Name: "{group}\Mise"; Filename: "{app}\Mise.exe"
Name: "{commondesktop}\Mise"; Filename: "{app}\Mise.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\Mise.exe"; Description: "Launch Mise"; Flags: nowait postinstall skipifsilent