"""
Model Name: ImageSaver.py
Description: save images into dateset
Author: Kun
Last Modified: 03 Jul 2024
"""
import os
import cv2 as cv
from datetime import datetime

TRANSFER = {0: 'top', 1: 'bottom', 2: 'left', 3: 'right', 4: 'screen', 5: 'keyboard'}


class ImageSaver:
    def __init__(self, save_directory='dataset'):
        self.root_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        self.save_directory = os.path.join(self.root_directory, save_directory)
        if not os.path.exists(self.save_directory):
            os.makedirs(self.save_directory)

    def save(self, folder_name, lot, imgs):
        save_directory = os.path.join(self.save_directory, folder_name)
        if not os.path.exists(save_directory):
            os.makedirs(save_directory)

        # Create the file path
        for i, image in enumerate(imgs):
            if image is None:
                break
            file_path = os.path.join(save_directory, f'{lot}_{TRANSFER[i]}.png')

            # Save the image
            cv.imwrite(file_path, image)
            print(f'Saved image: {file_path}')

    def save_raw_imgs(self, folder_name, imgs):
        current_time = datetime.now()
        formatted_time = current_time.strftime("%Y%m%d%H%M%S")

        save_directory = os.path.join(self.save_directory, f'{folder_name}_{formatted_time}')
        if not os.path.exists(save_directory):
            os.makedirs(save_directory)

        # Create the file path
        for i, image in enumerate(imgs):
            if image is None:
                break
            file_path = os.path.join(save_directory, f'{formatted_time}_{TRANSFER[i]}.png')

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
