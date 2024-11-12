REM Activate venv vWindwos
python -m venv venv
./venv/Scripts/activate

REM Install requirements from requirements.txt
pip install setuptools
pip cache purge
pip install -r requirements.txt

REM Uninstall torch, torchvision, torchaudio
pip uninstall torch torchvision torchaudio -y

REM Purge pip cache
pip cache purge

REM Install specific versions of torch, torchvision, torchaudio
pip install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu121
