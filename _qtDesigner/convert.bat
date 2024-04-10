@echo off
for %%f in (*.ui) do (
    pyuic5.exe "%%f" -o "qtGui.py"
)
