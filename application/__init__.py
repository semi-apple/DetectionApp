from .control import Controller
from .app import DetectionApp
import os
_APP_DIR = os.path.dirname(os.path.abspath(__file__))

__all__ = [
    'Controller',
    'DetectionApp',
    '_APP_DIR',
]
