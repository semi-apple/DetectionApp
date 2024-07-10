"""
Login Window for Detection Application

This script provides a login window using PyQt5, allowing users to enter their username and password.
Upon successful login, the main Detection Application window is opened. This is part of the larger
Detection Application project.

Classes:
- LoginWindow: A QWidget-based class that creates the login interface.

Functions:
- initUI(): Initializes the user interface with input fields and login button.
- handleLogin(): Handles the login button click event to validate user credentials.
- open_main_window(): Opens the main Detection Application window upon successful login.


Author: Kun
Last Modified: 10 Jul 2024
"""

from PyQt5.QtWidgets import QMessageBox
from App.DetectionApp import *


class LoginWindow(QWidget):
    def __init__(self, master):
        super().__init__()
        self.app = master
        self.initUI()

    def initUI(self):
        # Create label, input fields, and button
        self.label_username = QLabel('Username:')
        self.text_username = QLineEdit(self)

        self.label_password = QLabel('Password:')
        self.text_password = QLineEdit(self)
        self.text_password.setEchoMode(QLineEdit.Password)

        self.button_login = QPushButton('Login', self)
        self.button_login.clicked.connect(self.handleLogin)

        # Layout
        layout = QVBoxLayout(self)
        layout.addWidget(self.label_username)
        layout.addWidget(self.text_username)
        layout.addWidget(self.label_password)
        layout.addWidget(self.text_password)
        layout.addWidget(self.button_login)

        self.setLayout(layout)
        self.setWindowTitle('Login Form')
        self.resize(300, 120)

    def handleLogin(self):
        # Placeholder functionality for login
        # if self.text_username.text() == 'admin' and self.text_password.text() == 'admin':
        if self.text_username.text() == '' and self.text_password.text() == '':
            QMessageBox.information(self, 'Login', 'Successful login!')
            self.open_main_window()
        else:
            QMessageBox.warning(self, 'Login', 'Incorrect username or password.')

    def open_main_window(self):
        self.app = DetectionApp(self.app)
        # self.app.show()
        self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    login_window = LoginWindow(app)
    login_window.show()
    sys.exit(app.exec_())
