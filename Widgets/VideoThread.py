"""
Model Name: VideoThread.py
Description: load video for each camera.
Author: Kun
Last Modified: 03 Jul 2024
"""
from PyQt5.QtCore import pyqtSlot
# from IO.detection_functions import *
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from ultralytics import YOLO
import cv2 as cv
import numpy as np

from Exceptions.CameraExceptions import CameraInitException


def convert_cv_qt(cv_img):
    """convert cv format to qt format"""
    rgb_image = cv.cvtColor(cv_img, cv.COLOR_BGR2RGB)
    h, w, ch = rgb_image.shape
    bytes_per_line = ch * w
    convert_to_Qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
    return convert_to_Qt_format


@pyqtSlot(np.ndarray)
def update_image(cv_img, label):
    rgb_image = cv.cvtColor(cv_img, cv.COLOR_BGR2RGB)
    h, w, ch = rgb_image.shape
    bytes_per_line = ch * w
    convert_to_Qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
    p = convert_to_Qt_format.scaled(640, 480, aspectRatioMode=Qt.IgnoreAspectRatio)
    pixmap = QPixmap.fromImage(p)
    label.setPixmap(pixmap)


class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(QImage)

    def __init__(self, camera_port=0, model=None):
        super().__init__()
        self.camera_port = camera_port
        self.model = model
        self.running = True
        # self.run

    def run(self):
        cap = cv.VideoCapture(self.camera_port)
        if cap.isOpened():
            self.running = True
        else:
            self.running = False
            print(f'Cannot init camera {self.camera_port}, please make sure the camera is installed correctly.')
            cap.release()
            # raise CameraInitException()

        while self.running:
            ret, frame = cap.read()
            if ret:
                qt_image = convert_cv_qt(frame)
                self.change_pixmap_signal.emit(qt_image)
            else:
                self.running = False
        cap.release()

    def capture(self):
        while self.running:
            cap = cv.VideoCapture(self.camera_port)
            ret, frame = cap.read()
            if ret:
                cap.release()
                return frame

    def stop(self):
        self.running = False
        self.wait()


