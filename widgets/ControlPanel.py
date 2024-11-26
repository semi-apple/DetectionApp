"""
Control Panel for Device Management

This script provides a GUI control panel using PyQt5 for entering and saving device information,
such as serial numbers and device models. The information is saved to a CSV file named 'dataset.csv'
in the 'Dataset' directory.

Classes:
- ControlPanel: A QWidget-based class that creates the control panel interface.

Functions:
- initUI(): Initializes the user interface.
- add_input_line(label_name, input_widget, layout): Adds a labeled input line to the layout.
- on_click(): Handles the save button click event to save the input data to the CSV file.
- clear_all_inputs(): Clears all input fields.

Widget:
- Input Line:
    - model_input:
    - lot_number_input:
    - serial_number_input:
    - scratch_input:
    - stain_input:
    - grade_input:

Author: Kun
Last Modified: 10 Jul 2024
"""
import os

from PyQt5 import QtGui
from PyQt5.QtCore import Qt, QObject, pyqtSlot
from PyQt5.QtGui import QPainter

_Widget_dir = os.path.dirname(os.path.abspath(__file__))

import csv
from PyQt5.QtWidgets import QPushButton, QVBoxLayout, QLineEdit, QLabel, QHBoxLayout, QMainWindow, QWidget, QGridLayout, \
    QSizePolicy, QSpacerItem, QFrame, QGroupBox, QStyleOptionGroupBox, QStyle, QFormLayout
from PyQt5.QtWidgets import QApplication


class PanelBase(QObject):
    def __init__(self, input_lines, panel_buttons):
        super(PanelBase, self).__init__()
        self.input_lines = input_lines
        self.panel_buttons = panel_buttons
        self.handle_signal()

    def handle_signal(self):
        self.panel_buttons['save_button'].clicked.connect(self.save_to_dataset)
        self.panel_buttons['clear_button'].clicked.connect(self.clear_all_inputs)

    def save_to_dataset(self):
        saving_info = {}
        dataset_file = os.path.join(_Widget_dir, '../dataset/dataset.csv')
        for name, input_line in self.input_lines.items():
            name = name[:-6].replace('_', ' ')
            saving_info[name] = input_line.text()

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

    @pyqtSlot(dict)
    def set_detected_features(self, detected_features):
        # logo, lot, serial, scratch_count, stain_count = \
        #     (detected_features['logo'], detected_features['lot'], detected_features['serial'],
        #      detected_features['scratch'], detected_features['stain'])

        logo = 'hp'
        lot = '123456'
        scratch_count = '10'
        stain_count = '10'

        self.input_lines['model_input'].setText(logo)
        self.input_lines['lot_number_input'].setText(lot)
        self.input_lines['scratch_input'].setText(scratch_count)
        self.input_lines['stain_input'].setText(stain_count)

        grade_info = {'scratch': scratch_count, 'stain': stain_count}

        self.grade(grade_info)
        # self.save_to_dataset()

    def grade(self, grade_info):
        scratch_count, stain_count = grade_info['scratch'], grade_info['stain']
        self.input_lines['grade_input'].setText('A')
