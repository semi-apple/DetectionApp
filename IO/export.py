"""
Export dialog to export data

This script provides a dialog using PyQt5, allowing users to export data by selecting a date
and exporting images captured on that date to Google Drive.

Classes:
- ProgressDialog: A dialog to show the progress of file uploads.
- CalendarDialog: A dialog to select a date using a calendar widget.
- ExportFile: Main dialog for exporting files based on selected date.
- UploadWorker: QThread-based worker for handling file uploads in the background.

Author: Kun
Last Modified: 05 Sep 2024
"""
import sys

from PyQt5.QtCore import pyqtSignal, QThread
from PyQt5.QtWidgets import QApplication, QPushButton, QDialog, QVBoxLayout, QCalendarWidget, \
    QLabel, QHBoxLayout, QMessageBox
import os

from google_driver import GoogleDriveUploader

CLIENT_ID = '382624035870-r0o6a7mrh56mvteieu2g7njubr4r5k07.apps.googleusercontent.com'
CLIENT_SECRET = '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'
SCOPES = ['https://www.googleapis.com/auth/drive']

currentPath = os.path.dirname(os.path.abspath(__file__))


class ProgressDialog(QDialog):
    """
    Dialog to show the progress of file uploads.

    Attributes:
    - progress_label: QLabel to display current file being uploaded.
    - progress_bar: QLabel to show progress percentage of upload.
    - cancel_button: QPushButton to cancel the upload process.

    Methods:
    - updateProgress(filename, progress): Update the progress information with filename and progress percentage.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Upload Progress')
        self.setGeometry(100, 100, 400, 200)

        self.progress_label = QLabel('Uploading files...')
        self.progress_bar = QLabel()
        self.cancel_button = QPushButton('Cancel')
        self.cancel_button.clicked.connect(self.close)

        layout = QVBoxLayout()
        layout.addWidget(self.progress_label)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.cancel_button)
        self.setLayout(layout)

    def updateProgress(self, filename, progress):
        """
        Update the progress information with filename and progress percentage.

        Args:
        - filename (str): Name of the file being uploaded.
        - progress (int): Progress percentage of the upload.
        """
        self.progress_label.setText(f'Uploading: {filename}')
        self.progress_bar.setText(f'Progress: {progress}%')


class CalendarDialog(QDialog):
    """
    Dialog to select a date using QCalendarWidget.

    Attributes:
    - calendar: QCalendarWidget instance for selecting a date.

    Signals:
    - accepted(): Signal emitted when the date is selected and accepted.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle('Select Date')
        self.calendar = QCalendarWidget(self)
        self.calendar.clicked.connect(self.accept)

        layout = QVBoxLayout()
        layout.addWidget(self.calendar)
        self.setLayout(layout)


class ExportFile(QDialog):
    """
    Main dialog for exporting files based on selected date.

    Attributes:
    - button_open_calendar: QPushButton to open the calendar dialog.
    - button_export: QPushButton to initiate the export process.
    - display_date_label: QLabel to display the selected date.

    Methods:
    - setupUI(): Set up the UI components and connections.
    - open_calendar(): Open the calendar dialog to select a date.
    - export_files(): Start the process of exporting files based on the selected date.
    - updateProgress(filename, progress): Update the progress dialog with filename and progress.
    - cancel_upload(): Cancel the file upload process.
    - upload_finished(): Handle actions when file upload is completed.
    - closeEvent(event): Clean up actions when the dialog is closed.
    """

    def __init__(self):
        super().__init__()
        self.setupUI()
        self.uploader = GoogleDriveUploader()
        self.progress_dialog = ProgressDialog()

    def setupUI(self):
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
        selected_img_folder = []
        folder_path = ''
        dataset_path = os.path.join(currentPath, '../dataset')
        if self.display_date:
            exportDate = self.display_date.replace('-', '')
            selected_img_folder = [f for f in os.listdir(dataset_path) if exportDate == os.path.splitext(f)[0][9:17]]
            if len(selected_img_folder) == 0:
                print(f'No folder on selected date: {self.display_date}')
                return

        else:
            print('No date selected.')
            return

        self.progress_dialog.progress_bar.setText('Progress: 0 %')
        self.progress_dialog.cancel_button.clicked.connect(self.cancel_upload)
        self.progress_dialog.show()

        # Create a worker thread for uploading files
        self.worker_thread = QThread()
        self.worker = UploadWorker(selected_img_folder, dataset_path, self.uploader)
        self.worker.moveToThread(self.worker_thread)
        self.worker.progressUpdate.connect(self.updateProgress)
        self.worker_thread.started.connect(self.worker.run)
        self.worker.taskFinished.connect(self.upload_finished)
        self.worker_thread.start()

    def updateProgress(self, filename, progress):
        """
        Update the progress dialog with filename and progress.

        Args:
        - filename (str): Name of the file being uploaded.
        - progress (int): Progress percentage of the upload.
        """
        self.progress_dialog.updateProgress(filename, progress)

    def cancel_upload(self):
        if hasattr(self, 'worker'):
            self.worker.stop()
        self.progress_dialog.close()

    def upload_finished(self):
        """
        Handle actions when file upload is completed.
        """
        if hasattr(self, 'worker_thread'):
            self.worker_thread.quit()
            self.worker_thread.wait()
        self.progress_dialog.close()
        QMessageBox.information(self, 'Export Completed', 'Export completed successfully.')

    def closeEvent(self, event):
        """
        Clean up actions when the dialog is closed.

        Args:
        - event: Close event object.
        """
        # Clean up if user closes the dialog
        if hasattr(self, 'worker_thread'):
            self.worker_thread.quit()
            self.worker_thread.wait()
        self.progress_dialog.close()


class UploadWorker(QThread):
    """
    QThread-based worker for handling file uploads in the background.

    Signals:
    - progressUpdate(filename, progress): Signal emitted to update the progress of file uploads.
    - taskFinished(): Signal emitted when the upload task is completed.

    Methods:
    - run(): Main method executed when the thread starts. Uploads files and emits progress signals.
    - stop(): Stop the file upload process.
    """

    progressUpdate = pyqtSignal(str, int)
    taskFinished = pyqtSignal()

    def __init__(self, folders, dataset_path, uploader):
        """
        Initialize the worker with folders to upload, dataset path, and uploader instance.

        Args:
        - folders (list): List of folders to upload.
        - dataset_path (str): Path to the dataset directory.
        - uploader (GoogleDriveUploader): Instance of GoogleDriveUploader for uploading files.
        """

        super().__init__()
        self.folders = folders
        self.dataset_path = dataset_path
        self.uploader = uploader
        self.is_running = True

    def run(self):
        total_folders = len(self.folders)
        progress = int((0 / total_folders) * 100)
        for i, folder_name in enumerate(self.folders, start=1):
            if not self.is_running:
                break
            self.progressUpdate.emit(folder_name, progress)
            folder_path = os.path.join(self.dataset_path, folder_name)
            self.uploader.upload_folder(folder_name, folder_path)
            progress = int((i / total_folders) * 100)
            self.progressUpdate.emit(folder_name, progress)

        if self.is_running:
            self.taskFinished.emit()

    def stop(self):
        self.is_running = False


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = ExportFile()
    mainWindow.show()
    # mainWindow.display_date = '2024-09-03'
    # mainWindow.export_files()
    sys.exit(app.exec_())
