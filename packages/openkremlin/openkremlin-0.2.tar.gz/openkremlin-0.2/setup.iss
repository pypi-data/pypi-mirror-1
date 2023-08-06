[Setup]
AppName=OpenKremlin
AppVerName=OpenKremlin 0.2
DefaultDirName={pf}\OpenKremlin
DefaultGroupName=OpenKremlin
DisableProgramGroupPage=yes
; LicenseFile=COPYING.txt
OutputBaseFilename=setup
Compression=lzma
SolidCompression=yes
ChangesAssociations=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Files]
Source: "dist\unkgb.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\Crypto.Cipher.XOR.pyd"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\Crypto.Cipher.ARC4.pyd"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\Crypto.Cipher.Blowfish.pyd"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\Crypto.Cipher.CAST.pyd"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\bz2.pyd"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\select.pyd"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\library.zip"; DestDir: "{app}"; Flags: ignoreversion
; Source: "dist\MSVCR71.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\python26.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\unicodedata.pyd"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\w9xpopen.exe"; DestDir: "{app}"; Flags: ignoreversion
; NOTE: Don't use "Flags: ignoreversion" on any shared system files

;;;;;;;;;;;;;;;TkInter Crud;;;;;;;;;;;;;;;;;;

Source: "dist\tcl85.dll"; DestDir: "{app}\."; CopyMode: alwaysoverwrite
Source: "dist\tk85.dll"; DestDir: "{app}\."; CopyMode: alwaysoverwrite
Source: "dist\_ctypes.pyd"; DestDir: "{app}\."; CopyMode: alwaysoverwrite
Source: "dist\_tkinter.pyd"; DestDir: "{app}\."; CopyMode: alwaysoverwrite
Source: "dist\tcl\tcl8.5\auto.tcl"; DestDir: "{app}\.\tcl\tcl8.5"; CopyMode: alwaysoverwrite
Source: "dist\tcl\tcl8.5\clock.tcl"; DestDir: "{app}\.\tcl\tcl8.5"; CopyMode: alwaysoverwrite
Source: "dist\tcl\tcl8.5\history.tcl"; DestDir: "{app}\.\tcl\tcl8.5"; CopyMode: alwaysoverwrite
Source: "dist\tcl\tcl8.5\init.tcl"; DestDir: "{app}\.\tcl\tcl8.5"; CopyMode: alwaysoverwrite
Source: "dist\tcl\tcl8.5\package.tcl"; DestDir: "{app}\.\tcl\tcl8.5"; CopyMode: alwaysoverwrite
Source: "dist\tcl\tcl8.5\parray.tcl"; DestDir: "{app}\.\tcl\tcl8.5"; CopyMode: alwaysoverwrite
Source: "dist\tcl\tcl8.5\safe.tcl"; DestDir: "{app}\.\tcl\tcl8.5"; CopyMode: alwaysoverwrite
Source: "dist\tcl\tcl8.5\tclIndex"; DestDir: "{app}\.\tcl\tcl8.5"; CopyMode: alwaysoverwrite
Source: "dist\tcl\tcl8.5\tm.tcl"; DestDir: "{app}\.\tcl\tcl8.5"; CopyMode: alwaysoverwrite
Source: "dist\tcl\tcl8.5\word.tcl"; DestDir: "{app}\.\tcl\tcl8.5"; CopyMode: alwaysoverwrite
Source: "dist\tcl\tk8.5\bgerror.tcl"; DestDir: "{app}\.\tcl\tk8.5"; CopyMode: alwaysoverwrite
Source: "dist\tcl\tk8.5\button.tcl"; DestDir: "{app}\.\tcl\tk8.5"; CopyMode: alwaysoverwrite
Source: "dist\tcl\tk8.5\choosedir.tcl"; DestDir: "{app}\.\tcl\tk8.5"; CopyMode: alwaysoverwrite
Source: "dist\tcl\tk8.5\clrpick.tcl"; DestDir: "{app}\.\tcl\tk8.5"; CopyMode: alwaysoverwrite
Source: "dist\tcl\tk8.5\comdlg.tcl"; DestDir: "{app}\.\tcl\tk8.5"; CopyMode: alwaysoverwrite
Source: "dist\tcl\tk8.5\console.tcl"; DestDir: "{app}\.\tcl\tk8.5"; CopyMode: alwaysoverwrite
Source: "dist\tcl\tk8.5\dialog.tcl"; DestDir: "{app}\.\tcl\tk8.5"; CopyMode: alwaysoverwrite
Source: "dist\tcl\tk8.5\entry.tcl"; DestDir: "{app}\.\tcl\tk8.5"; CopyMode: alwaysoverwrite
Source: "dist\tcl\tk8.5\focus.tcl"; DestDir: "{app}\.\tcl\tk8.5"; CopyMode: alwaysoverwrite
Source: "dist\tcl\tk8.5\license.terms"; DestDir: "{app}\.\tcl\tk8.5"; CopyMode: alwaysoverwrite
Source: "dist\tcl\tk8.5\listbox.tcl"; DestDir: "{app}\.\tcl\tk8.5"; CopyMode: alwaysoverwrite
Source: "dist\tcl\tk8.5\menu.tcl"; DestDir: "{app}\.\tcl\tk8.5"; CopyMode: alwaysoverwrite
Source: "dist\tcl\tk8.5\mkpsenc.tcl"; DestDir: "{app}\.\tcl\tk8.5"; CopyMode: alwaysoverwrite
Source: "dist\tcl\tk8.5\msgbox.tcl"; DestDir: "{app}\.\tcl\tk8.5"; CopyMode: alwaysoverwrite
Source: "dist\tcl\tk8.5\obsolete.tcl"; DestDir: "{app}\.\tcl\tk8.5"; CopyMode: alwaysoverwrite
Source: "dist\tcl\tk8.5\optMenu.tcl"; DestDir: "{app}\.\tcl\tk8.5"; CopyMode: alwaysoverwrite
Source: "dist\tcl\tk8.5\palette.tcl"; DestDir: "{app}\.\tcl\tk8.5"; CopyMode: alwaysoverwrite
Source: "dist\tcl\tk8.5\panedwindow.tcl"; DestDir: "{app}\.\tcl\tk8.5"; CopyMode: alwaysoverwrite
Source: "dist\tcl\tk8.5\pkgIndex.tcl"; DestDir: "{app}\.\tcl\tk8.5"; CopyMode: alwaysoverwrite
Source: "dist\tcl\tk8.5\safetk.tcl"; DestDir: "{app}\.\tcl\tk8.5"; CopyMode: alwaysoverwrite
Source: "dist\tcl\tk8.5\scale.tcl"; DestDir: "{app}\.\tcl\tk8.5"; CopyMode: alwaysoverwrite
Source: "dist\tcl\tk8.5\scrlbar.tcl"; DestDir: "{app}\.\tcl\tk8.5"; CopyMode: alwaysoverwrite
Source: "dist\tcl\tk8.5\spinbox.tcl"; DestDir: "{app}\.\tcl\tk8.5"; CopyMode: alwaysoverwrite
Source: "dist\tcl\tk8.5\tclIndex"; DestDir: "{app}\.\tcl\tk8.5"; CopyMode: alwaysoverwrite
Source: "dist\tcl\tk8.5\tearoff.tcl"; DestDir: "{app}\.\tcl\tk8.5"; CopyMode: alwaysoverwrite
Source: "dist\tcl\tk8.5\text.tcl"; DestDir: "{app}\.\tcl\tk8.5"; CopyMode: alwaysoverwrite
Source: "dist\tcl\tk8.5\tk.tcl"; DestDir: "{app}\.\tcl\tk8.5"; CopyMode: alwaysoverwrite
Source: "dist\tcl\tk8.5\tkfbox.tcl"; DestDir: "{app}\.\tcl\tk8.5"; CopyMode: alwaysoverwrite
Source: "dist\tcl\tk8.5\unsupported.tcl"; DestDir: "{app}\.\tcl\tk8.5"; CopyMode: alwaysoverwrite
Source: "dist\tcl\tk8.5\xmfbox.tcl"; DestDir: "{app}\.\tcl\tk8.5"; CopyMode: alwaysoverwrite
Source: "dist\tcl\tk8.5\msgs\cs.msg"; DestDir: "{app}\.\tcl\tk8.5\msgs"; CopyMode: alwaysoverwrite
Source: "dist\tcl\tk8.5\msgs\da.msg"; DestDir: "{app}\.\tcl\tk8.5\msgs"; CopyMode: alwaysoverwrite
Source: "dist\tcl\tk8.5\msgs\de.msg"; DestDir: "{app}\.\tcl\tk8.5\msgs"; CopyMode: alwaysoverwrite
Source: "dist\tcl\tk8.5\msgs\el.msg"; DestDir: "{app}\.\tcl\tk8.5\msgs"; CopyMode: alwaysoverwrite
Source: "dist\tcl\tk8.5\msgs\en.msg"; DestDir: "{app}\.\tcl\tk8.5\msgs"; CopyMode: alwaysoverwrite
Source: "dist\tcl\tk8.5\msgs\en_gb.msg"; DestDir: "{app}\.\tcl\tk8.5\msgs"; CopyMode: alwaysoverwrite
Source: "dist\tcl\tk8.5\msgs\eo.msg"; DestDir: "{app}\.\tcl\tk8.5\msgs"; CopyMode: alwaysoverwrite
Source: "dist\tcl\tk8.5\msgs\es.msg"; DestDir: "{app}\.\tcl\tk8.5\msgs"; CopyMode: alwaysoverwrite
Source: "dist\tcl\tk8.5\msgs\fr.msg"; DestDir: "{app}\.\tcl\tk8.5\msgs"; CopyMode: alwaysoverwrite
Source: "dist\tcl\tk8.5\msgs\hu.msg"; DestDir: "{app}\.\tcl\tk8.5\msgs"; CopyMode: alwaysoverwrite
Source: "dist\tcl\tk8.5\msgs\it.msg"; DestDir: "{app}\.\tcl\tk8.5\msgs"; CopyMode: alwaysoverwrite
Source: "dist\tcl\tk8.5\msgs\nl.msg"; DestDir: "{app}\.\tcl\tk8.5\msgs"; CopyMode: alwaysoverwrite
Source: "dist\tcl\tk8.5\msgs\pl.msg"; DestDir: "{app}\.\tcl\tk8.5\msgs"; CopyMode: alwaysoverwrite
Source: "dist\tcl\tk8.5\msgs\pt.msg"; DestDir: "{app}\.\tcl\tk8.5\msgs"; CopyMode: alwaysoverwrite
Source: "dist\tcl\tk8.5\msgs\ru.msg"; DestDir: "{app}\.\tcl\tk8.5\msgs"; CopyMode: alwaysoverwrite
Source: "dist\tcl\tk8.5\msgs\sv.msg"; DestDir: "{app}\.\tcl\tk8.5\msgs"; CopyMode: alwaysoverwrite
Source: "dist\tcl\tk8.5\ttk\altTheme.tcl"; DestDir: "{app}\.\tcl\tk8.5\ttk"; CopyMode: alwaysoverwrite
Source: "dist\tcl\tk8.5\ttk\aquaTheme.tcl"; DestDir: "{app}\.\tcl\tk8.5\ttk"; CopyMode: alwaysoverwrite
Source: "dist\tcl\tk8.5\ttk\button.tcl"; DestDir: "{app}\.\tcl\tk8.5\ttk"; CopyMode: alwaysoverwrite
Source: "dist\tcl\tk8.5\ttk\clamTheme.tcl"; DestDir: "{app}\.\tcl\tk8.5\ttk"; CopyMode: alwaysoverwrite
Source: "dist\tcl\tk8.5\ttk\classicTheme.tcl"; DestDir: "{app}\.\tcl\tk8.5\ttk"; CopyMode: alwaysoverwrite
Source: "dist\tcl\tk8.5\ttk\combobox.tcl"; DestDir: "{app}\.\tcl\tk8.5\ttk"; CopyMode: alwaysoverwrite
Source: "dist\tcl\tk8.5\ttk\cursors.tcl"; DestDir: "{app}\.\tcl\tk8.5\ttk"; CopyMode: alwaysoverwrite
Source: "dist\tcl\tk8.5\ttk\defaults.tcl"; DestDir: "{app}\.\tcl\tk8.5\ttk"; CopyMode: alwaysoverwrite
Source: "dist\tcl\tk8.5\ttk\entry.tcl"; DestDir: "{app}\.\tcl\tk8.5\ttk"; CopyMode: alwaysoverwrite
Source: "dist\tcl\tk8.5\ttk\fonts.tcl"; DestDir: "{app}\.\tcl\tk8.5\ttk"; CopyMode: alwaysoverwrite
Source: "dist\tcl\tk8.5\ttk\menubutton.tcl"; DestDir: "{app}\.\tcl\tk8.5\ttk"; CopyMode: alwaysoverwrite
Source: "dist\tcl\tk8.5\ttk\notebook.tcl"; DestDir: "{app}\.\tcl\tk8.5\ttk"; CopyMode: alwaysoverwrite
Source: "dist\tcl\tk8.5\ttk\panedwindow.tcl"; DestDir: "{app}\.\tcl\tk8.5\ttk"; CopyMode: alwaysoverwrite
Source: "dist\tcl\tk8.5\ttk\progress.tcl"; DestDir: "{app}\.\tcl\tk8.5\ttk"; CopyMode: alwaysoverwrite
Source: "dist\tcl\tk8.5\ttk\scale.tcl"; DestDir: "{app}\.\tcl\tk8.5\ttk"; CopyMode: alwaysoverwrite
Source: "dist\tcl\tk8.5\ttk\scrollbar.tcl"; DestDir: "{app}\.\tcl\tk8.5\ttk"; CopyMode: alwaysoverwrite
Source: "dist\tcl\tk8.5\ttk\sizegrip.tcl"; DestDir: "{app}\.\tcl\tk8.5\ttk"; CopyMode: alwaysoverwrite
Source: "dist\tcl\tk8.5\ttk\treeview.tcl"; DestDir: "{app}\.\tcl\tk8.5\ttk"; CopyMode: alwaysoverwrite
Source: "dist\tcl\tk8.5\ttk\ttk.tcl"; DestDir: "{app}\.\tcl\tk8.5\ttk"; CopyMode: alwaysoverwrite
Source: "dist\tcl\tk8.5\ttk\utils.tcl"; DestDir: "{app}\.\tcl\tk8.5\ttk"; CopyMode: alwaysoverwrite
Source: "dist\tcl\tk8.5\ttk\winTheme.tcl"; DestDir: "{app}\.\tcl\tk8.5\ttk"; CopyMode: alwaysoverwrite
Source: "dist\tcl\tk8.5\ttk\xpTheme.tcl"; DestDir: "{app}\.\tcl\tk8.5\ttk"; CopyMode: alwaysoverwrite

[Icons]
Name: "{group}\OpenKremlin"; Filename: "{app}\unkgb.exe"
Name: "{group}\{cm:UninstallProgram,OpenKremlin}"; Filename: "{uninstallexe}"
[Registry]
Root: HKCR; Subkey: ".kgb"; ValueType: string; ValueName: ""; ValueData: "OpenKremlinDecrypt"; Flags: uninsdeletevalue
Root: HKCR; Subkey: "OpenKremlinDecrypt"; ValueType: string; ValueName: ""; ValueData: "OpenKremlin Decrypt"; Flags: uninsdeletekey
Root: HKCR; Subkey: "OpenKremlinDecrypt\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\unkgb.exe,0"
Root: HKCR; Subkey: "OpenKremlinDecrypt\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\unkgb.exe"" ""%1"""
