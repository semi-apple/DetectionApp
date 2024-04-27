from PyQt5.QtWidgets import QMainWindow, QWidget, QLabel, QVBoxLayout, QPushButton, QApplication
from ultralytics import YOLO
from Widget.VideoThread import *


class VideoWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.image_label1 = None
        self.image_label2 = None
        self.image_label3 = None
        self.start_button = None
        self.model = YOLO("models/yolov5s.pt")
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Video Stream')
        self.setGeometry(100, 100, 800, 600)
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        layout = QVBoxLayout()

        self.image_label1 = QLabel(self)
        self.image_label1.setAlignment(Qt.AlignCenter)
        self.image_label1.setScaledContents(True)
        layout.addWidget(self.image_label1)

        self.image_label2 = QLabel(self)
        self.image_label2.setAlignment(Qt.AlignCenter)
        self.image_label2.setScaledContents(True)
        layout.addWidget(self.image_label2)

        self.image_label3 = QLabel(self)
        self.image_label3.setAlignment(Qt.AlignCenter)
        self.image_label3.setScaledContents(True)
        layout.addWidget(self.image_label3)

        self.start_button = QPushButton('Start Detection', self)
        self.start_button.clicked.connect(self.start_detection)
        layout.addWidget(self.start_button)

        # central_widget = QWidget()
        self.central_widget.setLayout(layout)
        # self.setCentralWidget(central_widget)

        self.setMinimumSize(640, 480)
        self.setLayout(layout)
        self.show()

    def start_detection(self):
        self.thread1 = VideoThread(0, self.model)
        self.thread1.change_pixmap_signal.connect(self.set_image1)
        self.thread1.start()

        self.thread2 = VideoThread(1, self.model)
        self.thread2.change_pixmap_signal.connect(self.set_image2)
        self.thread2.start()

        self.thread3 = VideoThread(2, self.model)
        self.thread3.change_pixmap_signal.connect(self.set_image3)
        self.thread3.start()

    @pyqtSlot(QImage)
    def set_image1(self, image):
        self.image_label1.setPixmap(QPixmap.fromImage(image).scaled(self.image_label1.size(), Qt.KeepAspectRatio))

    @pyqtSlot(QImage)
    def set_image2(self, image):
        self.image_label2.setPixmap(QPixmap.fromImage(image).scaled(self.image_label2.size(), Qt.KeepAspectRatio))

    @pyqtSlot(QImage)
    def set_image3(self, image):
        self.image_label3.setPixmap(QPixmap.fromImage(image).scaled(self.image_label3.size(), Qt.KeepAspectRatio))

    def closeEvent(self, event):
        self.thread1.stop()
        self.thread2.stop()
        super().closeEvent(event)


if __name__ == '__main__':
    app = QApplication([])
    video_window = VideoWindow()
    video_window.show()
    app.exec_()
