"""
Menu bar for Detection Application

This script provides a menu bar using PyQt5, allowing users to user some tools.
Upon successful login, the main Detection Application window is opened, and the menu bar is added on the top.

Classes:
- MenuBar: A QWidget-based class that creates the menu bar.

Functions:
- initUI(): Initializes the user interface with input fields and login button.
- handleLogin(): Handles the login button click event to validate user credentials.
- open_main_window(): Opens the main Detection Application window upon successful login.


Author: Kun
Last Modified: 22 Jul 2024
"""
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QMenuBar, QAction, QApplication, QMenu


class BarBase(QMenuBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.master = parent
        self.initUI()
        self.setNativeMenuBar(False)

    def initUI(self):
        file_menu = self.addMenu('File')

        add_action = QAction('Add', self)
        add_action.triggered.connect(self.add_file)
        file_menu.addAction(add_action)

        exit_action = QAction('Exit', self)
        exit_action.triggered.connect(self.destroy_app)
        file_menu.addAction(exit_action)

        help_menu = self.addMenu('Help')


    @pyqtSlot()
    def destroy_app(self):
        QApplication.instance().quit()

    @pyqtSlot()
    def add_file(self):
        pass


class VideoMenuBar(BarBase):
    def __init__(self, parent=None):
        super(VideoMenuBar, self).__init__(parent)


class PanelMenuBar(BarBase):
    def __init__(self, parent=None):
        super(PanelMenuBar, self).__init__(parent)

