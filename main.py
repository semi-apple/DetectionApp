"""
Model Name: main.py
Description: Program entrance, load application
Author: Kun
Last Modified: 03 Jul 2024
"""
import sys
from PyQt5.QtWidgets import QApplication
from application.DetectionApp import DetectionApp
from widgets.Login import LoginWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)
    login = LoginWindow()
    detect_app = DetectionApp()
    login.accepted.connect(lambda username, level: detect_app.start_detection(username, level))
    sys.exit(app.exec_())
