' Nanban auto-start (hidden): runs start_nanban.cmd with no console window.
Dim fso, dir, sh
Set fso = CreateObject("Scripting.FileSystemObject")
dir = fso.GetParentFolderName(WScript.ScriptFullName)
Set sh = CreateObject("WScript.Shell")
sh.Run """" & dir & "\start_nanban.cmd""", 0, False
