import sys
from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QPushButton, QFileDialog, QLineEdit, QGridLayout, QMessageBox, QMainWindow, QInputDialog, QWidget, QDesktopWidget
from PyQt5.QtGui import QPixmap, QPainter, QPen, QBrush, QColor, QImage
from PyQt5.QtCore import Qt, QRect, QPoint
import pandas as pd
import os
import random


class ScratchAnnotatorApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.data = {
            "image_name": [],
            "file_size": [],
            "scratch_count": [],
            "region_shape_attributes": []
        }

        self.initUI()
        self.image_path = None
        self.image_size = None
        self.scratch_rects = []
        self.rect = None
        self.start_point = QPoint()
        self.end_point = QPoint()
        self.is_drawing = False

    def initUI(self):
        self.setWindowTitle('Scratch Annotator')

        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.layout = QVBoxLayout(self.main_widget)

        # Image panel
        self.image_label = QLabel(self)
        self.layout.addWidget(self.image_label)

        # Buttons
        self.grid_layout = QGridLayout()
        self.open_button = QPushButton('Open Image', self)
        self.open_button.clicked.connect(self.open_image)
        self.grid_layout.addWidget(self.open_button, 0, 0)

        self.save_button = QPushButton('Save Data', self)
        self.save_button.clicked.connect(self.save_data)
        self.grid_layout.addWidget(self.save_button, 0, 1)

        # Add grid layout to main layout
        self.layout.addLayout(self.grid_layout)

        # Entries
        self.entries_frame = QGridLayout()
        self.layout.addLayout(self.entries_frame)

    def open_image(self):
        self.image_path, _ = QFileDialog.getOpenFileName(self, 'Open Image', '../images/new', 'Image files (*.jpg *.jpeg *.png)')
        if self.image_path:
            self.image = QImage(self.image_path)
            screen_rect = QDesktopWidget().screenGeometry()
            screen_width = screen_rect.width()
            screen_height = screen_rect.height()
            self.image = self.image.scaled(screen_width, screen_height, Qt.KeepAspectRatio)
            self.image_label.setPixmap(QPixmap.fromImage(self.image))
            self.image_size = os.path.getsize(self.image_path)
            self.scratch_rects = []
            self.clear_entries()
            self.adjustSize()
            self.update()

    def save_data(self):
        if not self.image_path:
            QMessageBox.critical(self, 'Error', 'Please open an image first')
            return

        scratch_info = {}
        scratch_count = 0
        for i, (rect, length) in enumerate(self.scratch_rects):
            x_min, y_min = rect.topLeft().x(), rect.topLeft().y()
            x_max, y_max = rect.bottomRight().x(), rect.bottomRight().y()
            scratch_info[f'scratch_{i}'] = (x_min, y_min, x_max, y_max, length)
            scratch_count += 1

        image_filename = os.path.basename(self.image_path)
        self.data["image_name"].append(image_filename)
        self.data["file_size"].append(self.image_size)
        self.data["scratch_count"].append(scratch_count)
        self.data["region_shape_attributes"].append(scratch_info)

        df = pd.DataFrame(self.data)

        # Check if the file exists and append data without overwriting the header
        file_exists = os.path.isfile("scratch_annotations.csv")
        df.to_csv("scratch_annotations.csv", mode='a', header=not file_exists, index=False)

        QMessageBox.information(self, 'Success', 'Data saved to scratch_annotations.csv')

    # def paintEvent(self, event):
    #     if self.image_path and self.scratch_rects:
    #         painter = QPainter(self)
    #         painter.drawPixmap(self.image_label.pos(), QPixmap.fromImage(self.image))
    #         for rect, _ in self.scratch_rects:
    #             painter.setPen(QPen(self.get_random_color(), 2, Qt.SolidLine))
    #             painter.setBrush(QBrush(QColor(255, 0, 0, 50)))  # Semi-transparent red
    #             painter.drawRect(rect)
    #         if self.is_drawing:
    #             painter.setPen(QPen(Qt.blue, 2, Qt.SolidLine))
    #             painter.setBrush(QBrush(QColor(0, 0, 255, 50)))  # Semi-transparent blue
    #             painter.drawRect(QRect(self.start_point, self.end_point))

    def paintEvent(self, event):
        if self.image_path:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            if self.rect:
                print('painting')
                pen = QPen()
                painter.setPen(pen)
                brush = QBrush(QColor(0, 0, 255, 50))
                painter.setBrush(brush)
                painter.drawRect(self.rect)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.image_path:
            # print('mouse clicked')
            self.start_point = event.pos()
            self.end_point = self.start_point
            self.update()

    def mouseMoveEvent(self, event):
        if self.start_point and self.image_path:
            # print(1)
            self.end_point = event.pos()
            self.rect = QRect(self.start_point, self.end_point)
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.image_path:
            # print('mouse release')
            self.end_point = event.pos()
            self.rect = QRect(self.start_point, self.end_point)
            length, ok = QInputDialog.getInt(self, 'Scratch Length', 'Enter scratch length (mm):')
            if ok:
                self.scratch_rects.append((self.rect, length))
                self.add_entry(self.rect, length)
            self.update()

    def add_entry(self, rect, length):
        row = len(self.scratch_rects) - 1
        x_min, y_min = rect.topLeft().x(), rect.topLeft().y()
        x_max, y_max = rect.bottomRight().x(), rect.bottomRight().y()
        label = QLabel(f'Scratch {row + 1}:')
        entry = QLineEdit(f'{x_min}, {y_min}, {x_max}, {y_max}, {length}')
        entry.setReadOnly(True)
        self.entries_frame.addWidget(label, row, 0)
        self.entries_frame.addWidget(entry, row, 1, 1, 3)

    def clear_entries(self):
        while self.entries_frame.count():
            child = self.entries_frame.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def get_random_color(self):
        colors = [Qt.red, Qt.green, Qt.blue, Qt.yellow, Qt.cyan, Qt.magenta, Qt.gray, Qt.darkRed, Qt.darkGreen, Qt.darkBlue, Qt.darkYellow, Qt.darkCyan, Qt.darkMagenta, Qt.darkGray]
        return random.choice(colors)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ScratchAnnotatorApp()
    ex.show()
    sys.exit(app.exec_())
