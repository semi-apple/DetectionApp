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
import threading
import time

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

    def __init__(self, camera_port=0):
        super().__init__()
        self.camera_port = camera_port
        self.running = True
        self.cap = None
        self.lock = threading.Lock()
        # self.run

    def run(self):
        with self.lock:
            self.cap = cv.VideoCapture(self.camera_port, cv.CAP_DSHOW)
            if not self.cap.isOpened():
                self.running = False
                print(f'Cannot init camera {self.camera_port}, please make sure the camera is installed correctly.')
                self.cap.release()
                return

        while self.running:
            with self.lock:
                ret, frame = self.cap.read()
            if ret:
                qt_image = convert_cv_qt(frame)
                self.change_pixmap_signal.emit(qt_image)
            else:
                print(f'Failed to capture image from camera {self.camera_port}')
                self.running = False
        
        with self.lock:
            self.cap.release()
            self.cap = None

    def capture(self):
        with self.lock:
            if not self.running:
                return None
            
            ret, frame = self.cap.read()
        # cap.release()
        if ret:
            return frame
        else:
            return None
        

    def stop(self):
        self.running = False
        self.wait()
