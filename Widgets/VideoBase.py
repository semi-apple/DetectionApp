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
from IO.detection_functions import detect_logo
from IO.detection_functions import detect_lot
from IO.detection_functions import defects_detect
from IO.detection_functions import defects_segment
import cv2 as cv

location_id_to_camera_index = {
    0: "0x01111000",
    1: "0x01112000",
    2: "0x01113000",
    3: "0x01114000",
    4: "0x01120000",
    5: "0x01130000",
}

def get_usb_info():
    result = subprocess.run(['system_profiler', 'SPUSBDataType'], stdout=subprocess.PIPE)
    usb_info = result.stdout.decode('utf-8')
    return usb_info

def extract_location_ids(usb_info):
    location_ids = []
    lines = usb_info.split('\n')
    for line in lines:
        if 'Location ID:' in line:
            location_id = line.split('Location ID:')[-1].strip()
            location_ids.append(location_id)
    return location_ids


def list_available_cameras():
    index = 0
    arr = []
    while True:
        cap = cv.VideoCapture(index)
        if not cap.read()[0]:
            break
        else:
            arr.append(index)
        cap.release()
        index += 1
    return arr


def get_usb_device_info():
    result = subprocess.run(['system_profiler', 'SPUSBDataType'], stdout=subprocess.PIPE)
    return result.stdout.decode('utf-8')


class VideoBase(QObject):
    laptop_info = pyqtSignal(dict)

    def __init__(self, thread_labels=None, buttons=None, models=None):
        super().__init__()
        self.threads = []
        self.thread_labels = thread_labels
        self.buttons = buttons
        # self.models = models
        self.logo_model, self.defects_model, self.lot_model, self.serial_region_model, self.serial_model = \
            (models['logo'], models['defects'], models['lot'], models['serial_region'], models['serial'])
        self.image_saver = ImageSaver()

        # usb_info = get_usb_info()
        # location_ids = extract_location_ids(usb_info)

        self.buttons['detect_button'].clicked.connect(self.start_detection)
        self.buttons['capture_button'].clicked.connect(self.capture_images)
        self.buttons['stop_button'].clicked.connect(self.stop_detection)

    def start_detection(self):
        # i = 1
        # # if i:
        # usb_info = get_usb_device_info()
        # print(usb_info)
        for i in range(6):
            thread = VideoThread(i, self.defects_model)
            thread.change_pixmap_signal.connect(getattr(self, f'set_image{i}'))
            thread.start()
            self.threads.append(thread)

    def detect_images(self, original_imgs):
        logo, lot, serial = '', '', ''
        detected_imgs = []
        detected_features = {}

        for original_img, camera_port in original_imgs:
            if original_img is None:
                continue

            if camera_port == 1:  # detect logo and lot number
                try:
                    logo = detect_logo(original_img, self.logo_model)
                    lot = detect_lot(original_img, self.lot_model)

                except LogoNotFoundException as e:
                    print(f'On port {camera_port} -> {e}')
                    logo = 'Logo_Not_Found'

                except LotNumberNotFoundException as e:
                    print(f'On port {camera_port} -> {e}')
                    lot = 'Lot_Not_Found'

                finally:
                    detected_features['logo'], detected_features['lot'] = logo, lot
                    print(f'Logo: {logo}, Lot Number: {lot}')

            # if camera_port == 1:    # detect serial number
            #     try:
            #         serial = detect_serial(original_img, self.serial_region_model, self.serial_model)
            #         print(f'Serial Number: {serial}')
            #
            #     except SerialNumberNotFoundException as e:
            #         print(f'On port {camera_port} -> {e}')
            #         serial = 'Serial_Not_Found'
            #
            #     finally:
            #         detected_features['serial'] = serial

            # detected_img = defects_detect(original_img, self.defects_model)
            detected_img = defects_segment(original_img)
            detected_imgs.append((np.copy(detected_img), camera_port))
            # detected_imgs.append((np.copy(original_img), camera_port))

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
        # self.save_raw_info(folder_name='raw_imgs', imgs=original_imgs)

        """
            Whether we need to store images over here, or we could store images on Control Panel, like:
            set signal, emit to Control Panel (raw images, cv images, detected features), store images 
            and detected feature on Control Panel.
            
            One good thing to do so is that if there is a detection error occurred, we can store images 
            with correct info by fixing problem manually.
             
            One bad thing is that it is not automatic.
        """

        detected_imgs, detected_features = self.detect_images(original_imgs)
        for key, value in detected_features.items():
            print(f'{key}: {value}')
        lot = detected_features['lot']

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
