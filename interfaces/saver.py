"""
Model Name: ImageSaver.py
Description: Handles saving images into the dataset directory.

Classes:
- ImageSaver: Provides functionality to save processed and raw images into organized directories.

Author: Kun
Last Modified: 03 Jul 2024
"""
import os
import cv2 as cv
from datetime import datetime
import numpy as np

# Mapping of camera ports to descriptive names
TRANSFER = {0: 'top', 1: 'bottom', 2: 'left', 3: 'right', 4: 'screen', 5: 'keyboard'}


class ImageSaver:
    """
    A class to handle saving images into organized dataset directories.

    Attributes:
        root_directory (str): The root directory of the project.
        save_directory (str): The directory where images will be saved.
    """
    def __init__(self, save_directory='dataset'):
        """
        Initialize the ImageSaver.

        Args:
            save_directory (str): Name of the folder to store the dataset. Default is 'dataset'.
        """
        self.root_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        self.save_directory = os.path.join(self.root_directory, save_directory)
        if not os.path.exists(self.save_directory):
            os.makedirs(self.save_directory)

    def save(self, folder_name, lot, imgs):
        """
        Save processed images into a specific folder.

        Args:
            folder_name (str): Name of the sub-folder to save the images.
            lot (str): Identifier for the lot (e.g., lot number).
            imgs (list[tuple]): List of tuples containing the image and corresponding camera port.
        """
        save_directory = os.path.join(self.save_directory, folder_name)
        if not os.path.exists(save_directory):
            os.makedirs(save_directory)

        # Create the file path
        for image, camera_port in imgs:
            if image is None:
                break
            file_path = os.path.join(save_directory, f'{lot}_{TRANSFER[camera_port]}.jpg')

            # Save the image
            cv.imwrite(file_path, image)
            print(f'Saved image: {file_path}')

    def save_raw_imgs(self, folder_name, imgs):
        """
        Save original images into a timestamped folder (for test).

        Args:
            folder_name (str): Name of the sub-folder to save the images.
            imgs (list[tuple]): List of tuples containing the image and corresponding camera port.
        """
        current_time = datetime.now()
        formatted_time = current_time.strftime("%Y%m%d%H%M%S")

        save_directory = os.path.join(self.save_directory, f'{folder_name}_{formatted_time}')
        if not os.path.exists(save_directory):
            os.makedirs(save_directory)

        # Create the file path
        for image, camera_port in imgs:
            if image is None:
                break

            assert isinstance(image, np.ndarray), "Image is not a numpy array"
            file_path = os.path.join(save_directory, f'{formatted_time}_{TRANSFER[camera_port]}.jpg')

            # Save the image
            cv.imwrite(file_path, image)
            print(f'Saved image: {file_path}')


if __name__ == '__main__':
    saver = ImageSaver()
    lot = 'test001'
    imgs = []
    img = cv.imread('../image001.jpg')
    imgs.append(img)
    saver.save(lot, lot, imgs)
