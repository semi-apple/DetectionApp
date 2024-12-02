@echo off
python --version >null 2>&1
if %errorlevel% neq 0 (
    echo "Python is not installed, please install Python 3.11+ and try again."
    exit /b 1
)

echo "Creating virtual environment..."
if exist venv (
    echo "Virtual environment already exists. Skipping creation..."
) else (
    echo "Creating virtual environment..."
    python -m venv venv
    if %errorlevel% neq 0 (
        echo "Failed to create virtual environment."
        exit /b 1
    )
)

@REM echo "Activating virtual environment..."
@REM call venv\Scripts\activate.bat
@REM if %errorlevel% neq 0 (
@REM     echo "Failed to activate virtual environment."
@REM     exit /b 1
@REM )

echo "Updating pip..."
python -m pip install --upgrade pip

echo "Installing dependencies..."
@REM pip install setuptools
@REM pip cache purge
python -m pip install -r requirements.txt

@REM REM Uninstall torch, torchvision, torchaudio
python -m pip uninstall torch torchvision torchaudio -y

@REM REM Purge pip cache
python -m pip cache purge

@REM REM Install specific versions of torch, torchvision, torchaudio
python -m pip install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu121

echo "Installation completed!"
echo "Packaging application..."
@REM pyinstaller --onefile app\main.py

@REM if exist dist\main.exe (
@REM     echo "Build successful!"
@REM     exit /b 0
@REM ) else (
@REM     echo "Build failed: No executable found."
@REM     exit /b 1
@REM )
@REM @REM pause

call /venv/Scripts/activate

