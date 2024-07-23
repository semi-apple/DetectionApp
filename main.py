"""
Model Name: main.py
Description: Program entrance, load application
Author: Kun
Last Modified: 03 Jul 2024
"""
from App.WindowController import *

if __name__ == '__main__':
    app = QApplication(sys.argv)
    controller = WindowController()
    sys.exit(app.exec_())
