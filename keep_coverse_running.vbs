Option Explicit

Dim shell, fileSystem, rootPath, pythonPath, appPath, command
Set shell = CreateObject("WScript.Shell")
Set fileSystem = CreateObject("Scripting.FileSystemObject")
rootPath = fileSystem.GetParentFolderName(WScript.ScriptFullName)

pythonPath = rootPath & "\.venv\Scripts\python.exe"
If Not fileSystem.FileExists(pythonPath) Then pythonPath = "python.exe"
appPath = rootPath & "\app_server.py"
watchdogPath = rootPath & "\restart_coverse.py"
command = Chr(34) & pythonPath & Chr(34) & " " & Chr(34) & watchdogPath & Chr(34)
shell.CurrentDirectory = rootPath

Do
    shell.Run command, 0, True
    WScript.Sleep 5000
Loop
