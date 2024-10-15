"""
Model Name: VideoWindow.py
Description: create a window widget to present camera information.
Author: Kun
Last Modified: 03 Jul 2024
"""
import os
import subprocess

# import sys

from PyQt5.QtCore import QObject, pyqtSlot, Qt, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap
import numpy as np

_Widget_dir = os.path.dirname(os.path.abspath(__file__))

from Widgets.VideoThread import VideoThread
from Exceptions.DetectionExceptions import (SerialNumberNotFoundException, LotNumberNotFoundException,
                                            LogoNotFoundException)
from Exceptions.CameraExceptions import CameraInitException
from IO.ImageSaver import ImageSaver
from IO.detection_functions import *
# from IO.detection_functions import detect_lot
# from IO.detection_functions import defects_detect
# from IO.detection_functions import defects_segment
import cv2 as cv
from Exceptions.DetectionExceptions import *

class VideoBase(QObject):
    laptop_info = pyqtSignal(dict)

    def __init__(self, thread_labels=None, buttons=None, models=None):
        super().__init__()
        self.threads = []
        self.thread_labels = thread_labels
        self.buttons = buttons
        # self.models = models
        self.init_model(models)
        self.image_saver = ImageSaver()

        # usb_info = get_usb_info()
        # location_ids = extract_location_ids(usb_info)

        self.buttons['detect_button'].clicked.connect(self.start_detection)
        self.buttons['capture_button'].clicked.connect(self.capture_images)
        self.buttons['stop_button'].clicked.connect(self.stop_detection)

    def init_model(self, models):
        self.logo_model = models['logo']
        self.top_bottom_model = models['top_bottom']
        self.lot_model = models['lot']
        self.serial_region_model = models['serial_region']
        self.serial_model = models['serial']
        self.laptop_model = models['laptop']
        try:
            self.keyboard_model = models['keyboard']
            self.screen_model = models['screen']
        except:
            self.keyboard_model = None
            self.screen_model = None

    def start_detection(self):
        for i in range(6):
            thread = VideoThread(i, self.defects_model)
            thread.change_pixmap_signal.connect(getattr(self, f'set_image{i}'))
            thread.start()
            self.threads.append(thread)

    def detect_images(self, original_imgs):
        logo, lot, serial = '', '', ''
        detected_imgs = []
        detected_features = {}
        detected_img = None

        for original_img, camera_port in original_imgs:
            if original_img is None:
                continue

            if camera_port == 0:  # top image, detect logo and lot number
                try:
                    logo = detect_logo(original_img, self.logo_model)
                    lot = detect_lot(original_img, self.lot_model)
                    detected_img = defects_segment(original_img, self.top_bottom_model)

                except LogoNotFoundException as e:
                    print(f'On port {camera_port} -> {e}')
                    logo = 'Logo_Not_Found'

                except LotNumberNotFoundException as e:
                    print(f'On port {camera_port} -> {e}')
                    lot = 'Lot_Not_Found'

                finally:
                    detected_features['logo'], detected_features['lot'] = logo, lot
                    print(f'Logo: {logo}, Lot Number: {lot}')

            elif camera_port == 1: # bottom image, detect serial number
                try:
                    serial = detect_serial(original_img, self.serial_region_model, self.serial_model)
                    print(f'Serial Number: {serial}')
                    detected_img = defects_segment(original_img, self.top_bottom_model)

                except SerialNumberNotFoundException as e:
                    print(f'On port {camera_port} -> {e}')
                    serial = 'Serial_Not_Found'

                finally:
                    detected_features['serial'] = serial

            elif camera_port == 2: # keyboard
                try:
                    detected_img = defects_segment(original_img, self.keyboard_model)
                except DetectionException as e:
                    print(f'On port {camera_port} -> {e}')
                    detected_img = original_img

            elif camera_port == 3: # screen
                try:
                    detected_img = defects_segment(original_img, self.screen_model)
                except DetectionException as e:
                    print(f'On port {camera_port} -> {e}')
                    detected_img = original_img

            detected_imgs.append((detected_img, camera_port))

        return detected_imgs, detected_features

    def capture_images(self):
        original_imgs = []

        # set default logo capture camera as 0
        for thread in self.threads:
            # if thread.running and thread.camera_port == 1: # on port 0
            if thread.running:
                original_img = thread.capture()  # original image
                original_imgs.append((np.copy(original_img), thread.camera_port))

        # capture images
        self.save_raw_info(folder_name='raw_imgs', imgs=original_imgs)

        """
            Whether we need to store images over here, or we could store images on Control Panel, like:
            set signal, emit to Control Panel (raw images, cv images, detected features), store images 
            and detected feature on Control Panel.
            
            One good thing to do so is that if there is a detection error occurred, we can store images 
            with correct info by fixing problem manually.
             
            One bad thing is that it is not automatic.
        """

        # detected_imgs, detected_features = self.detect_images(original_imgs)
        # for key, value in detected_features.items():
        #     print(f'{key}: {value}')
        # lot = detected_features['lot']

        # self.save_info(folder_name=lot, lot=lot, imgs=original_imgs)
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
