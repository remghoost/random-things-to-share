@echo off

rem Check if either venv or .venv folder exists
if exist venv (
    set "venv_path=venv"
) else if exist .venv (
    set "venv_path=.venv"
) else (
    set "venv_path="
)

rem Check if virtual environment is activated
if "%VIRTUAL_ENV%"=="" (
    if not "%venv_path%"=="" (
        echo Virtual environment activated.
        call %venv_path%\Scripts\activate
    ) else (
        echo No virtual environment found.
        echo Creating new virtual environment...
        echo.
        python -m venv venv
        echo Virtual environment created.
        echo New virtual environment activated.
        call venv\Scripts\activate
    )
) else (
    echo.
    rem Deactivate the virtual environment
    deactivate
    echo Virtual environment deactivated.
    echo.
)
