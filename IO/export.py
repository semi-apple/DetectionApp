"""
Export dialog to export data

This script provides a dialog using PyQt5, allowing users to export data.
Select a date and export the images captured by that date.

Classes:
- MenuBar: A QWidget-based class that creates the menu bar.


Functions:



Author: Kun
Last Modified: 26 Aug 2024
"""
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QDialog, QVBoxLayout, QCalendarWidget, QWidget, \
    QLabel, QHBoxLayout, QFileDialog
import os

currentPath = os.path.dirname(os.path.abspath(__file__))


class CalendarDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle('Select Date')
        self.calendar = QCalendarWidget(self)
        self.calendar.clicked.connect(self.accept)

        layout = QVBoxLayout()
        layout.addWidget(self.calendar)
        self.setLayout(layout)


class ExportFile(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Export')
        self.setGeometry(100, 100, 400, 200)

        self.button_open_calendar = QPushButton('Select Date')
        self.button_export = QPushButton('Export')

        self.button_open_calendar.clicked.connect(self.open_calendar)
        self.button_export.clicked.connect(self.export_files)

        label_date = QLabel('Date: ')
        self.display_date_label = QLabel('')

        date_layout = QHBoxLayout()
        date_layout.addWidget(label_date)
        date_layout.addWidget(self.display_date_label)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.button_open_calendar)
        button_layout.addWidget(self.button_export)

        main_layout = QVBoxLayout()
        main_layout.addLayout(button_layout)
        main_layout.addLayout(date_layout)

        self.setLayout(main_layout)

    def open_calendar(self):
        dialog = CalendarDialog(self)
        if dialog.exec_():
            self.display_date = dialog.calendar.selectedDate().toString('yyyy-MM-dd')
            self.display_date_label.setText(self.display_date)

    def export_files(self):
        selected_files = []
        folder_path = ''
        if self.display_date:
            exportDate = self.display_date.replace('-', '')
            folder_path = os.path.join(currentPath, '../dataset')
            if folder_path:
                selected_files = [f for f in os.listdir(folder_path) if exportDate in os.path.splitext(f)[0]]
                if len(selected_files) == 0:
                    print(f'No folder on selected date: {self.display_date}')

        else:
            print('No date selected.')

        for f in selected_files:
            print(os.path.join(folder_path, f))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = ExportFile()
    mainWindow.show()
    sys.exit(app.exec_())
