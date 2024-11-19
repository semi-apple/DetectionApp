python -m venv venv

./venv/Scripts/Activate

pip install ultralytics

pip uninstall torch torchvision torchaudio

pip cache purge

pip install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu121
