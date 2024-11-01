@echo off
set /p name="Please enter the name for your project: "
dotnet new bep6plugin_unity_mono -n %name% -T netstandard2.1 -U 2022.3.37

powershell -File UpdateCsproj.ps1 -name "%name%"
