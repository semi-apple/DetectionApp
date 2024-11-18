@echo off
python --version >null 2>&1
if %errorlevel% neq 0 (
    echo "Python is not installed, please install Python 3.11+ and try again."
    exit /b 1
    )

echo "Creating virtual environment..."
python -m venv venv
call /venv/Scripts/activate

echo "Updating pip..."
python -m pip install --upgrade pip

echo "Installing dependencies..."
@REM pip install setuptools
@REM pip cache purge
pip install -r requirements.txt

@REM REM Uninstall torch, torchvision, torchaudio
pip uninstall torch torchvision torchaudio -y

@REM REM Purge pip cache
pip cache purge

@REM REM Install specific versions of torch, torchvision, torchaudio
pip install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu121

echo "Installation completed!"
echo "Packaging application..."
pyinstaller --onefile app\main.py

if exist dist\main.exe (
    echo "Build successful!"
    exit /b 0
) else (
    echo "Build failed: No executable found."
    exit /b 1
)
@REM pause
