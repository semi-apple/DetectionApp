"""
Model Name: VideoWindow.py
Description: create a window widget to present camera information.
Author: Kun
Last Modified: 03 Jul 2024
"""

from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QApplication, QGridLayout
from ultralytics import YOLO
from Widget.VideoThread import *
from IO.ImageSaver import *


class VideoWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.model = YOLO("./models/best.pt")
        self.threads = []
        self.labels = []
        self.image_saver = ImageSaver()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Video Stream')
        self.setGeometry(100, 100, 800, 600)

        grid_layout = QGridLayout(self)

        self.image_label1 = QLabel(self)
        self.image_label1.setAlignment(Qt.AlignCenter)
        self.image_label1.setScaledContents(True)
        grid_layout.addWidget(self.image_label1, 0, 0)
        self.labels.append(self.image_label1)

        self.image_label2 = QLabel(self)
        self.image_label2.setAlignment(Qt.AlignCenter)
        self.image_label2.setScaledContents(True)
        grid_layout.addWidget(self.image_label2, 0, 1)
        self.labels.append(self.image_label2)

        self.image_label3 = QLabel(self)
        self.image_label3.setAlignment(Qt.AlignCenter)
        self.image_label3.setScaledContents(True)
        grid_layout.addWidget(self.image_label3, 0, 2)
        self.labels.append(self.image_label3)

        self.image_label4 = QLabel(self)
        self.image_label4.setAlignment(Qt.AlignCenter)
        self.image_label4.setScaledContents(True)
        grid_layout.addWidget(self.image_label4, 1, 0)
        self.labels.append(self.image_label4)

        self.image_label5 = QLabel(self)
        self.image_label5.setAlignment(Qt.AlignCenter)
        self.image_label5.setScaledContents(True)
        grid_layout.addWidget(self.image_label5, 1, 1)
        self.labels.append(self.image_label5)

        self.image_label6 = QLabel(self)
        self.image_label6.setAlignment(Qt.AlignCenter)
        self.image_label6.setScaledContents(True)
        grid_layout.addWidget(self.image_label6, 1, 2)
        self.labels.append(self.image_label6)

        self.start_button = QPushButton('Start Detection', self)
        self.start_button.clicked.connect(self.start_detection)
        grid_layout.addWidget(self.start_button, 2, 0, 1, 1)

        self.capture_button = QPushButton('Capture Image', self)
        self.capture_button.clicked.connect(self.capture_images)
        grid_layout.addWidget(self.capture_button, 2, 1, 1, 1)

        self.stop_button = QPushButton('Stop Detection', self)
        self.stop_button.clicked.connect(self.stop_detection)
        grid_layout.addWidget(self.stop_button, 2, 2, 1, 1)

        self.setLayout(grid_layout)
        self.setMinimumSize(640, 480)
        self.show()

    # def start_detection(self):
    #     """
    #     old version to detect damaged information automatically.
    #     """
    #     self.thread1 = VideoThread(0, self.model)
    #     self.thread1.change_pixmap_signal.connect(self.set_image1)
    #     self.thread1.start()
    #
    #     self.thread2 = VideoThread(1, self.model)
    #     self.thread2.change_pixmap_signal.connect(self.set_image2)
    #     self.thread2.start()
    #
    #     self.thread3 = VideoThread(2, self.model)
    #     self.thread3.change_pixmap_signal.connect(self.set_image3)
    #     self.thread3.start()
    #
    #     self.thread4 = VideoThread(3, self.model)
    #     self.thread4.change_pixmap_signal.connect(self.set_image4)
    #     self.thread4.start()
    #
    #     self.thread5 = VideoThread(4, self.model)
    #     self.thread5.change_pixmap_signal.connect(self.set_image5)
    #     self.thread5.start()
    #
    #     self.thread6 = VideoThread(5, self.model)
    #     self.thread6.change_pixmap_signal.connect(self.set_image6)
    #     self.thread6.start()

    def start_detection(self):
        for i in range(6):
            thread = VideoThread(i, self.model)
            thread.change_pixmap_signal.connect(getattr(self, f'set_image{i+1}'))
            thread.start()
            self.threads.append(thread)

    def capture_images(self):
        imgs = []
        detections = []
        logo = ''
        ser = ''
        # set default logo capture camera as 0
        for i, thread in enumerate(self.threads):
            if thread.running:
                img = thread.capture()  # original image
                imgs.append(img)
                if i == 0 and img is not None:  # detect logo and serial number
                    # logo_model = YOLO('logo.pt')
                    # logo, ser = logo_model(img)
                    print('camera 0 is activated')
                detected_img = thread.detect(img)  # image contains damaged information
                detections.append(detected_img)
        self.save_info(ser, imgs)

    def stop_detection(self):
        for thread in self.threads:
            thread.stop()
        self.threads = []
        for label in self.labels:
            label.clear()

    @pyqtSlot(QImage)
    def set_image1(self, image):
        self.image_label1.setPixmap(QPixmap.fromImage(image).scaled(self.image_label1.size(), Qt.KeepAspectRatio))

    @pyqtSlot(QImage)
    def set_image2(self, image):
        self.image_label2.setPixmap(QPixmap.fromImage(image).scaled(self.image_label2.size(), Qt.KeepAspectRatio))

    @pyqtSlot(QImage)
    def set_image3(self, image):
        self.image_label3.setPixmap(QPixmap.fromImage(image).scaled(self.image_label3.size(), Qt.KeepAspectRatio))

    @pyqtSlot(QImage)
    def set_image4(self, image):
        self.image_label4.setPixmap(QPixmap.fromImage(image).scaled(self.image_label4.size(), Qt.KeepAspectRatio))

    @pyqtSlot(QImage)
    def set_image5(self, image):
        self.image_label5.setPixmap(QPixmap.fromImage(image).scaled(self.image_label4.size(), Qt.KeepAspectRatio))

    @pyqtSlot(QImage)
    def set_image6(self, image):
        self.image_label4.setPixmap(QPixmap.fromImage(image).scaled(self.image_label4.size(), Qt.KeepAspectRatio))

    def save_info(self, ser, imgs):
        self.image_saver.save(ser, imgs)

    def closeEvent(self, event):
        self.stop_detection()
        super().closeEvent(event)


if __name__ == '__main__':
    app = QApplication([])
    video_window = VideoWindow()
    video_window.show()
    app.exec_()
