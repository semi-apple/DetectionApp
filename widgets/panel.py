"""
Control Panel for Device Management

This script provides a GUI control panel using PyQt5 for entering and saving device information,
such as serial numbers and device models. The information is saved to a CSV file named 'dataset.csv'
in the 'Dataset' directory.

Classes:
- PanelBase: A QObject-based class that creates the control panel logic.

Functions:
- init_dataset(): Initializes the dataset by creating the CSV file if it doesn't already exist.
- handle_signal(): Connects button signals to their respective slot functions.
- save_to_dataset(): Handles the save button click event to save the input data to the CSV file.
- clear_all_inputs(): Clears all input fields.
- set_detected_features(): Updates input fields with detected information from the detection process.
- grade(): Sets a grade based on detected defects.

Widgets (Input Lines):
- model_input
- lot_number_input
- serial_number_input
- scratch_input
- stain_input
- grade_input

Author: Kun
Last Modified: 10 Jul 2024
"""
import os

import cv2 as cv
from PyQt5.QtCore import Qt, QObject, pyqtSlot
import csv
from interfaces.classes import Defect


_widget_dir = os.path.dirname(os.path.abspath(__file__))


def init_dataset():
    """
    Initializes the dataset directory and CSV file. Creates the directory and file with headers if they don't exist.
    """
    root_path = os.path.abspath(os.path.join(_widget_dir, '..'))
    dataset_dir_path = os.path.join(root_path, 'dataset')
    if not os.path.exists(dataset_dir_path):
        os.makedirs(dataset_dir_path)

    dataset_file = os.path.join(dataset_dir_path, 'dataset.csv')
    if not os.path.exists(dataset_file):
        fieldnames = ['model', 'serial number', 'lot number', 'grade', 'stain', 'scratch']
        with open(dataset_file, 'a', newline='', encoding='utf-8') as dataset:
            writer = csv.DictWriter(dataset, fieldnames=fieldnames)
            writer.writeheader()


class PanelBase(QObject):
    """
    The control panel class that manages user input, saves data to the dataset, and updates fields based on detection results.
    """
    def __init__(self, input_lines, panel_buttons):
        """
        Initializes the PanelBase class.

        Args:
            input_lines (dict): A dictionary mapping input line names to their corresponding input widgets.
            panel_buttons (dict): A dictionary mapping button names to their corresponding button widgets.
        """
        super(PanelBase, self).__init__()
        self.input_lines = input_lines
        self.panel_buttons = panel_buttons
        self.handle_signal()
        init_dataset()

    def handle_signal(self):
        """
        Connects the panel buttons to their respective functions.
        """
        assert 'save_button' in self.panel_buttons
        assert 'clear_button' in self.panel_buttons

        self.panel_buttons['save_button'].clicked.connect(self.save_to_dataset)
        self.panel_buttons['clear_button'].clicked.connect(self.clear_all_inputs)

    def save_to_dataset(self):
        saving_info = {}
        dataset_file = os.path.join(_widget_dir, '../dataset/dataset.csv')
        for name, input_line in self.input_lines.items():
            name = name[:-6].replace('_', ' ')
            saving_info[name] = input_line.text()

        # Skip saving if all input fields are empty
        if all(value == "" for value in saving_info.values()):
            print("No data to save. Skipping...")
            return

        # Add information into dataset
        fieldnames = ['model', 'serial number', 'lot number', 'grade', 'stain', 'scratch']
        with open(dataset_file, 'a', newline='', encoding='utf-8') as dataset:
            writer = csv.DictWriter(dataset, fieldnames=fieldnames)
            if os.path.getsize(filename=dataset_file) == 0:
                writer.writeheader()
            # writer.writerow([i for i in saving_info.values()])
            writer.writerow(saving_info)

        self.clear_all_inputs()

    def clear_all_inputs(self):
        for input_line in self.input_lines.values():
            input_line.clear()
        print('Clear Info Successful')

    @pyqtSlot(dict)
    def set_detected_features(self, detected_features):
        """
        Updates input fields with detected features from the detection process.

        Args:
            detected_features (dict): Detected features including logo, lot, serial, and defect counts.
        """
        scratch_counts = 0
        stain_counts = 0
        for defects_counts, _ in detected_features['detected_info']:
            scratch_counts += defects_counts[0]
            stain_counts += defects_counts[1]
        logo, lot, serial = \
            (detected_features['logo'].strip('\n'), detected_features['lot'].strip('\n'),
             detected_features['serial'].strip('\n'))

        self.input_lines['model_input'].setText(logo)
        self.input_lines['lot_number_input'].setText(lot)
        self.input_lines['serial_number_input'].setText(serial)
        self.input_lines['scratch_input'].setText(str(scratch_counts))
        self.input_lines['stain_input'].setText(str(stain_counts))

        grade_info = {'scratch': scratch_counts, 'stain': stain_counts}
        print('Info Update Successful')

        self.grade(grade_info)
        # self.save_to_dataset()

    def grade(self, grade_info):
        """
        Sets a grade based on the defect counts.
        Still need to be implemented.

        Args:
            grade_info (dict): A dictionary containing defect counts.
        """
        scratch_count, stain_count = grade_info['scratch'], grade_info['stain']

        # Basic grading logic (can be expanded as needed)
        if scratch_count > 10 or stain_count > 10:
            self.input_lines['grade_input'].setText('C')
        else:
            self.input_lines['grade_input'].setText('A')


