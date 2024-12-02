"""
Menu bar for Detection Application

This script provides a menu bar using PyQt5, allowing users to user some tools.
Upon successful login, the main Detection Application window is opened, and the menu bar is added on the top.

Classes:
- MenuBar: A QWidget-based class that creates the menu bar.

Structure:
- File:
    - Open (connect with action actionOpenFile): open file in folder
    - Exit (connect with action actionExitApp): exit app
- Database:
    - Open (connect with action actionOpenDatabase): open database to review data
    - Export (connect with action actionExportData): export data to ...
- Account:
    - Profile (connect with action actionProfile): open account profile
    - Signout (connect with action actionSignout): sign out current account
- Help:
    - Instructions (connect with action actionDocuments): open instruction
    - Documents (connect with action actionInstructions): open document

Functions:

Author: Kun
Last Modified: 26 Aug 2024
"""
from interfaces.export import ExportFile
from typing import Optional
from PyQt5.QtCore import pyqtSlot, QObject, QCoreApplication
from PyQt5.QtWidgets import QApplication


def get_app() -> Optional[QCoreApplication]:
    return QApplication.instance()


class BarBase(QObject):
    def __init__(self, actionDict):
        super(BarBase, self).__init__()
        self.actionDict = actionDict
        self.handle_actions()
        # self.handle_modules()

    def handle_actions(self):
        actionOpenFile = self.actionDict['openFile']
        actionOpenFile.triggered.connect(self.open_file)
        actionExitApp = self.actionDict['exitApp']
        actionExitApp.triggered.connect(self.exit_app)
        actionOpenDatabase = self.actionDict['openDatabase']
        actionOpenDatabase.triggered.connect(self.open_database)
        actionExportData = self.actionDict['exportData']
        actionExportData.triggered.connect(self.export_data)
        actionProfile = self.actionDict['profile']
        actionProfile.triggered.connect(self.acc_profile)
        actionSignout = self.actionDict['signout']
        actionSignout.triggered.connect(self.sign_out)
        actionDocuments = self.actionDict['documents']
        actionDocuments.triggered.connect(self.open_documents)
        actionInstructions = self.actionDict['instructions']
        actionInstructions.triggered.connect(self.open_instruction)

    def handle_modules(self):
        self.exportModule = ExportFile()

    @pyqtSlot()
    def open_file(self):
        print('action connected')
        pass

    @pyqtSlot()
    def open_database(self):
        pass

    @pyqtSlot()
    def export_data(self):
        self.exportModule.show()
        self.exportModule.exec_()

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

    @pyqtSlot()
    def exit_app(self):
        get_app().quit()





