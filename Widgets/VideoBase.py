"""
Model Name: VideoWindow.py
Description: create a window widget to present camera information.
Author: Kun
Last Modified: 03 Jul 2024
"""
import os
import sys

from PyQt5.QtCore import QObject

_Widget_dir = os.path.dirname(os.path.abspath(__file__))

import cv2
from PyQt5.QtWidgets import QLabel, QPushButton, QApplication, QGridLayout, QMainWindow, QWidget
import easyocr
from Widgets.VideoThread import *
from IO.ImageSaver import *
from Exceptions.DetectionExceptions import *
from IO.ImageSaver import ImageSaver


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

    def capture_images(self):
        logo = 'dell'
        lot = 'test'
        original_imgs = []
        detect_imgs = []
        detect_defect = {}
        scratch_count, stain_count = 0, 0

        # set default logo capture camera as 0
        for thread in self.threads:
            if thread.running:
                original_img = thread.capture()  # original image
                original_imgs.append(np.copy(original_img))
                if thread.camera_port == 0 and original_img is not None:  # detect logo and lot number
                    try:
                        logo, lot = detect_logo_lot(original_img, self.logo_model, self.ocr_model, self.reader)

                    except LogoNotFoundException as e:
                        print(f'On port {thread.camera_port} -> {e}')
                        # logo = 'test'
                        continue

                    except LotNumberNotFoundException as e:
                        print(f'On port {thread.camera_port} -> {e}')
                        # lot = 'test'
                        continue

                    print(f'logo: {logo}, lot: {lot}')

                # lot = '000'
                # image contains damaged information
                detect_img, temp_scratch_count, temp_stain_count = thread.detect_frame(original_img)
                print(f'temp_scratch: {temp_scratch_count}, temp_stain: {temp_stain_count}')
                scratch_count += temp_scratch_count
                stain_count += temp_stain_count
                detect_imgs.append(detect_img)

        # emit signal
        detect_defect['logo'] = 'dell'
        detect_defect['lot'] = lot
        detect_defect['scratch'] = scratch_count
        detect_defect['stain'] = stain_count
        detect_defect = {k: str(v) for k, v in detect_defect.items()}

        self.laptop_info.emit(detect_defect)

        self.save_info(folder_name=lot, lot=lot, imgs=original_imgs)
        cv_folder = lot + '_cv'
        self.save_info(folder_name=cv_folder, lot=lot, imgs=detect_imgs)

    def stop_detection(self):
        for thread in self.threads:
            thread.stop()
        self.threads = []
        for label in self.thread_labels:
            label.clear()

    def save_info(self, folder_name, lot, imgs):
        self.image_saver.save(folder_name=folder_name, lot=lot, imgs=imgs)

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