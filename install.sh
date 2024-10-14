#!/bin/bash

# Install requirements from requirements.txt
pip install -r requirements.txt

# Uninstall torch, torchvision, torchaudio
pip uninstall torch torchvision torchaudio

# Purge pip cache
pip cache purge

# Install specific versions of torch, torchvision, torchaudio
pip install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu121
