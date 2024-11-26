from PyQt5.QtWidgets import QLabel, QDialog, QVBoxLayout
from PyQt5.QtGui import QPainter, QPen, QPixmap
from PyQt5.QtCore import Qt, QRect, pyqtSignal


class SelectionWindow(QDialog):
    selected_area = pyqtSignal(QRect)

    def __init__(self, image_path, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Selection Window")
        self.image_label = QLabel(self)
        self.image_label.setPixmap(QPixmap(image_path))

        layout = QVBoxLayout()
        layout.addWidget(self.image_label)
        self.setLayout(layout)

        self.selection_rect = QRect()
        self.is_selecting = False

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_selecting = True
            self.selection_rect.setTopLeft(event.pos())
            self.selection_rect.setBottomRight(event.pos())

    def mouseMoveEvent(self, event):
        if self.is_selecting:
            self.selection_rect.setBottomRight(event.pos())
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_selecting = False
            self.selected_area.emit(self.selection_rect)
            self.accept()

    def paintEvent(self, event):
        if self.is_selecting:
            painter = QPainter(self.image_label.pixmap())
            pen = QPen(Qt.red, 2)
            painter.setPen(pen)
            painter.drawRect(self.selection_rect)
            self.image_label.update()
