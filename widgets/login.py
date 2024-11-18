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
import sys

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QMessageBox, QLabel, QLineEdit, QPushButton, QVBoxLayout, QApplication, QDialog
from exceptions.user_login_exception import UserNotFoundException, IncorrectPasswordException

USERS = {'Admin': {'password': '123456', 'level': 0}, }


class LoginWindow(QDialog):
    accepted = pyqtSignal(str, int)
    rejected = pyqtSignal()

    def __init__(self, parent=None):
        super(LoginWindow, self).__init__(parent)
        self.initUI()
        self.show()

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
        self.setWindowTitle('Greenbox Computer Vision (GVS)')
        self.resize(300, 120)

    def handleLogin(self):
        # Placeholder functionality for login
        try:
            username, user_level = self.getUserInfo()
            QMessageBox.information(self, 'Login Successful!', f'Welcome, {username}!')
            self.accepted.emit(username, user_level)
            self.close()

        except Exception as e:
            return
        # self.accepted.emit('haha', 1)
        # self.close()

    def getUserInfo(self):
        # return 'Admin', 0
        username = self.text_username.text()
        password = self.text_password.text()
        try:
            if username not in USERS:
                raise UserNotFoundException(username)

            if USERS[username]['password'] != password:
                raise IncorrectPasswordException(username)

            return username, USERS[username]['level']

        except Exception as e:
            QMessageBox.warning(self, 'Login', str(e))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec_())
