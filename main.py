"""
Model Name: main.py
Description: Program entrance, load application
Author: Kun
Last Modified: 03 Jul 2024
"""
from Widget.LogInWindow import *

if __name__ == '__main__':
    app = QApplication(sys.argv)
    login = LoginWindow(app)
    login.show()
    sys.exit(app.exec_())
