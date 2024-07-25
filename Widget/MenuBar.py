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
        # ---------------- File --------------- #
        file_menu = self.addMenu('File')

        open_folder_action = QAction('Open', self)
        open_folder_action.triggered.connect(self.open_folder)
        file_menu.addAction(open_folder_action)

        exit_action = QAction('Exit', self)
        exit_action.triggered.connect(self.destroy_app)
        file_menu.addAction(exit_action)

        # -------------- Database ------------- #
        database_menu = self.addMenu('Database')

        open_database_action = QAction('Open', self)
        open_database_action.triggered.connect(self.open_database)
        database_menu.addAction(open_database_action)

        export_data_action = QAction('Export', self)
        export_data_action.triggered.connect(self.export_data)
        database_menu.addAction(export_data_action)

        # -------------- Account -------------- #
        account_menu = self.addMenu('Account')

        acc_profile_action = QAction('Profile', self)
        acc_profile_action.triggered.connect(self.acc_profile)
        account_menu.addAction(acc_profile_action)

        signout_action = QAction('Sign out', self)
        signout_action.triggered.connect(self.sign_out)
        account_menu.addAction(signout_action)

        # --------------- Help ---------------- #
        help_menu = self.addMenu('Help')

        instruction_action = QAction('Instruction', self)
        instruction_action.triggered.connect(self.open_instruction)
        help_menu.addAction(instruction_action)

        documents_action = QAction('Documents', self)
        documents_action.triggered.connect(self.open_documents)
        help_menu.addAction(documents_action)


    @pyqtSlot()
    def destroy_app(self):
        QApplication.instance().quit()

    @pyqtSlot()
    def open_folder(self):
        pass

    @pyqtSlot()
    def open_database(self):
        pass

    @pyqtSlot()
    def export_data(self):
        pass

    @pyqtSlot()
    def acc_profile(self):
        pass

    @pyqtSlot()
    def sign_out(self):
        pass

    @pyqtSlot()
    def open_instruction(self):
        pass

    @pyqtSlot()
    def open_documents(self):
        pass


class VideoMenuBar(BarBase):
    def __init__(self, parent=None):
        super(VideoMenuBar, self).__init__(parent)


class PanelMenuBar(BarBase):
    def __init__(self, parent=None):
        super(PanelMenuBar, self).__init__(parent)

