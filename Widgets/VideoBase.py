"""
Model Name: VideoWindow.py
Description: create a window widget to present camera information.
Author: Kun
Last Modified: 03 Jul 2024
"""
import os
import sys

import numpy as np
from PyQt5.QtCore import QObject

_Widget_dir = os.path.dirname(os.path.abspath(__file__))

from PyQt5.QtWidgets import QLabel, QPushButton, QApplication, QGridLayout, QMainWindow, QWidget
import easyocr
from Widgets.VideoThread import *
from IO.ImageSaver import *
from Exceptions.DetectionExceptions import *
from IO.ImageSaver import ImageSaver
from IO.detection_functions import detect_logo_lot
from IO.detection_functions import segment_defect_test
from IO.detection_functions import detect_serial


class VideoBase(QObject):
    laptop_info = pyqtSignal(dict)

    def __init__(self, thread_labels=None, buttons=None, models=None):
        super().__init__()
        self.threads = []
        self.thread_labels = thread_labels
        self.buttons = buttons
        # self.models = models
        self.logo_model, self.detect_model, self.ocr_model, self.reader = \
            (models['logo'], models['detect'], models['ocr'], models['reader'])
        self.image_saver = ImageSaver()

        self.buttons['detect_button'].clicked.connect(self.start_detection)
        self.buttons['capture_button'].clicked.connect(self.capture_images)
        self.buttons['stop_button'].clicked.connect(self.stop_detection)

    def start_detection(self):
        for i in range(6):
            thread = VideoThread(i, self.detect_model)
            thread.change_pixmap_signal.connect(getattr(self, f'set_image{i}'))
            thread.start()
            self.threads.append(thread)

    def detect_defect(self, original_img):
        logo = 'dell'
        lot = 'test'
        original_imgs = []
        detected_imgs = []
        detect_defect = {}
        scratch_count, stain_count = 0, 0
        for original_img, camera_port in original_imgs:
            if original_img is None:
                continue

            if camera_port == 0:  # detect logo and lot number
                try:
                    logo, lot = detect_logo_lot(original_img, self.logo_model, self.ocr_model, self.reader)

                except LogoNotFoundException as e:
                    print(f'On port {camera_port} -> {e}')
                    # logo = 'test'
                    return

                except LotNumberNotFoundException as e:
                    print(f'On port {camera_port} -> {e}')
                    # lot = 'test'
                    return

            if camera_port == 1:    # detect serial number
                try:
                    ser = detect_serial(original_img)
                except Exception as e:
                    print(f'Cannot detect serial numebr on camera {camera_port}')
                    return

            print(f'logo: {logo}, lot: {lot}')
            detected_img = segment_defect_test(original_img)
            detected_imgs.append((np.copy(detected_img), camera_port))

        return detected_imgs

    def capture_images(self):
        logo = 'dell'
        lot = 'test'
        original_imgs = []
        detected_imgs = []
        # detect_defect = {}
        # scratch_count, stain_count = 0, 0

        # set default logo capture camera as 0
        for thread in self.threads:
            if thread.running:
                original_img = thread.capture()  # original image
                original_imgs.append((np.copy(original_img), thread.camera_port))

        self.save_raw_info(folder_name='raw_imgs', imgs=original_imgs)

        # self.save_info(folder_name=lot, lot=lot, imgs=original_imgs)

        # detected_imgs = self.detect_defect(original_imgs)
        # cv_folder = lot + '_cv'
        # self.save_info(folder_name=cv_folder, lot=lot, imgs=detected_imgs)

    def stop_detection(self):
        for thread in self.threads:
            thread.stop()
        self.threads = []
        for label in self.thread_labels:
            label.clear()

    def save_info(self, folder_name, lot, imgs):
        self.image_saver.save(folder_name=folder_name, lot=lot, imgs=imgs)

    def save_raw_info(self, folder_name, imgs):
        self.image_saver.save_raw_imgs(folder_name=folder_name, imgs=imgs)

    @pyqtSlot(QImage)
    def set_image0(self, image):
        self.thread_labels[0].setPixmap(QPixmap.fromImage(image)
                                        .scaled(self.thread_labels[0].size(), Qt.KeepAspectRatio))

    @pyqtSlot(QImage)
    def set_image1(self, image):
        self.thread_labels[1].setPixmap(QPixmap.fromImage(image)
                                        .scaled(self.thread_labels[1].size(), Qt.KeepAspectRatio))

    @pyqtSlot(QImage)
    def set_image2(self, image):
        self.thread_labels[2].setPixmap(QPixmap.fromImage(image)
                                        .scaled(self.thread_labels[2].size(), Qt.KeepAspectRatio))

    @pyqtSlot(QImage)
    def set_image3(self, image):
        self.thread_labels[3].setPixmap(QPixmap.fromImage(image)
                                        .scaled(self.thread_labels[3].size(), Qt.KeepAspectRatio))

    @pyqtSlot(QImage)
    def set_image4(self, image):
        self.thread_labels[4].setPixmap(QPixmap.fromImage(image)
                                        .scaled(self.thread_labels[4].size(), Qt.KeepAspectRatio))

    @pyqtSlot(QImage)
    def set_image5(self, image):
        self.thread_labels[5].setPixmap(QPixmap.fromImage(image)
                                        .scaled(self.thread_labels[5].size(), Qt.KeepAspectRatio))

    def closeEvent(self, event):
        self.stop_detection()
