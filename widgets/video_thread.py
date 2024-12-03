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
import cv2 as cv
import numpy as np
import threading


def convert_cv_qt(cv_img):
    """convert cv format to qt format"""
    rgb_image = cv.cvtColor(cv_img, cv.COLOR_BGR2RGB)
    h, w, ch = rgb_image.shape
    bytes_per_line = ch * w
    convert_to_Qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
    return convert_to_Qt_format


class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(QImage)

    def __init__(self, camera_port=0):
        super().__init__()
        self.camera_port = camera_port
        self.running = True
        self.cap = None

    def run(self):
        self.cap = cv.VideoCapture(self.camera_port, cv.CAP_DSHOW)
        if not self.cap.isOpened():
            print(f'Cannot init camera {self.camera_port}, please make sure the camera is installed correctly.')
            self.running = False
            return

        while self.running:
            ret, frame = self.cap.read()
            if ret:
                qt_image = convert_cv_qt(frame)
                self.change_pixmap_signal.emit(qt_image)
            else:
                print(f'Failed to capture image from camera {self.camera_port}')
                self.running = False

        self.cap.release()

    def capture(self):
        if not self.running or not self.cap.isOpened():
            return None

        ret, frame = self.cap.read()
        return frame if ret else None

    def stop(self):
        self.running = False
        self.wait()
