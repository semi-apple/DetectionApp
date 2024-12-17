"""
Model Name: detection.py
Description: create thread to run detection.
Author: Kun
Last Modified: 17 Dec 2024
"""
from PyQt5.QtCore import QThread, pyqtSignal
import numpy as np
from PyQt5.QtCore import pyqtSignal, QThread
from interfaces.detection_functions import detect_lot_asset_barcode, segment_with_sahi, detect_logo
from exceptions.detection_exceptions import (LotNumberNotFoundException, AssetNumberNotFoundException, 
                                             LogoNotFoundException, SerialNumberNotFoundException)


class DetectionThread(QThread):
    detected_info = pyqtSignal(tuple)

    def __init__(self, models):
        super().__init__()
        self.init_models(models)
        self.images = []
        self.running = True
        
    def init_models(self, models):
        self.top_bottom_model = models['top_bottom']
        self.lot_asset_barcode_model = models['lot_asset_barcode']
        self.logo_model = models['logo']
        # self.lot_model = models['lot']
        self.serial_region_model = models['serial_region']
        self.serial_model = models['serial']
        # self.barcode_model = models['barcode']
        self.keyboard_model = models['keyboard']
        self.screen_model = models['screen']

    def run(self):
        while self.running:
            if self.images:
                detected_imgs, detected_features, defects_list = self.detect_images(self.images)
                self.detected_info.emit((detected_imgs, detected_features, defects_list))
                self.images = []
                print('Detection finished!')
                
    def add_images(self, images):
        self.images = images
        
    def detect_images(self, original_imgs: list) -> object:
        """
        Performs detection on the captured images.

        Args:
            original_imgs (list): List of original images captured by cameras.

        Returns:
            tuple: Detected images, features, and defect lists.
        """
        logo, lot, serial = '', '', ''
        detected_imgs = []
        detected_features = {}
        detected_info = []
        defects_list = []
        models_list = [self.top_bottom_model, self.top_bottom_model, self.keyboard_model, self.screen_model]
        for img, camera_port in original_imgs:
            if img is None:
                continue
            if camera_port == 1:  # detect logo and lot number
                logo, lot, asset = None, None, None  # Initialize variables
                # Detect logo
                try:
                    logo = detect_logo(img, self.logo_model)
                except LogoNotFoundException as e:
                    print(f'On port {camera_port} -> {e}')
                    logo = 'Logo_Not_Found'

                # Detect lot number
                try:
                    lot, asset = detect_lot_asset_barcode(img, self.lot_asset_barcode_model)
                except LotNumberNotFoundException as e:
                    print(f'On port {camera_port} -> {e}')
                    lot = 'Lot_Not_Found'
                    asset = 'Asset_Not_Found'
                except AssetNumberNotFoundException as e:
                    print(f'On port {camera_port} -> {e}')
                    asset = 'Asset_Not_Found'

            if camera_port == 2:  # detect serial number
                try:
                    serial = detect_serial(img, self.serial_region_model, self.serial_model)
                    print(f'Serial Number: {serial}')

                except SerialNumberNotFoundException as e:
                    print(f'On port {camera_port} -> {e}')
                    serial = 'Serial_Not_Found'                    

            detected_img, defects_counts, defects = segment_with_sahi(img, 2, models_list[camera_port - 1]) 
            if defects_counts is not None:
                detected_info.append((defects_counts, camera_port))
            if defects is not None:
                defects_list.append((defects, camera_port))
            detected_imgs.append((np.copy(detected_img), camera_port))


        detected_features['serial'], detected_features['logo'], detected_features['lot'], detected_features['asset'] = \
            serial, logo, lot, asset
        print(f'Logo: {logo}, Lot Number: {lot}')
        detected_features['detected_info'] = detected_info
        
        return detected_imgs, detected_features, defects_list

    def stop(self):
        self.running = False
