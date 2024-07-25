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

Author: Kun
Last Modified: 10 Jul 2024
"""
import os

from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter

_Widget_dir = os.path.dirname(os.path.abspath(__file__))

import csv
from PyQt5.QtWidgets import QPushButton, QVBoxLayout, QLineEdit, QLabel, QHBoxLayout, QMainWindow, QWidget, QGridLayout, \
    QSizePolicy, QSpacerItem, QFrame, QGroupBox, QStyleOptionGroupBox, QStyle, QFormLayout
from PyQt5.QtWidgets import QApplication
from Widget.MenuBar import PanelMenuBar


class CustomGroupBox(QGroupBox):
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.title = title
        self.setContentsMargins(10, 20, 10, 20)

    def paintEvent(self, event):
        painter = QPainter(self)
        option = QStyleOptionGroupBox()
        self.initStyleOption(option)
        # option.text = self.title  # Remove the default text rendering

        # Draw the group box without the default text
        self.style().drawComplexControl(QStyle.CC_GroupBox, option, painter, self)

        # Calculate the position for the custom text inside the border line
        text_rect = self.style().subControlRect(QStyle.CC_GroupBox, option, QStyle.SC_GroupBoxLabel, self)
        text_rect.setLeft(text_rect.left() + 10)  # Adjust text position if necessary

        # Draw the custom text
        painter.drawText(text_rect, Qt.AlignVCenter | Qt.AlignLeft, self.title)


class ControlPanel(QMainWindow):
    def __init__(self, parent=None):
        super(ControlPanel, self).__init__(parent)

        self.menu_bar = PanelMenuBar(self)
        self.setMenuBar(self.menu_bar)

        self.initUI()

    def initUI(self):
        self.setWindowTitle('Control Panel')
        self.setGeometry(100, 100, 300, 200)

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        laptop_info = CustomGroupBox('Laptop Info', self)
        laptop_info.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        input_layout = QGridLayout()

        # Device Model
        self.device_model_input = QLineEdit(self)
        self.device_model_input.setPlaceholderText('Enter device model')
        self.add_input_line(label_name='Device Model: ', input_widget=self.device_model_input,
                            grid_layout=input_layout, x=0, y=0)

        # Customer Number
        self.lot_number_input = QLineEdit(self)
        self.lot_number_input.setPlaceholderText('Enter lot number')
        self.add_input_line(label_name='Lot Number: ', input_widget=self.lot_number_input,
                            grid_layout=input_layout, x=0, y=2)

        # Serial Number
        self.serial_number_input = QLineEdit(self)
        self.serial_number_input.setPlaceholderText('Enter serial number')
        self.add_input_line(label_name='Serial Number: ', input_widget=self.serial_number_input,
                            grid_layout=input_layout, x=1, y=0)

        laptop_info.setLayout(input_layout)
        main_layout.addWidget(laptop_info, alignment=Qt.AlignTop)

        damaged_info = CustomGroupBox('Laptop Info', self)
        damaged_info.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        damaged_input_layout = QGridLayout()

        self.scratches_input = QLineEdit(self)
        self.add_input_line(label_name='Scratches: ', input_widget=self.scratches_input,
                            grid_layout=damaged_input_layout, x=0, y=0)

        self.stain_input = QLineEdit(self)
        self.add_input_line(label_name='Stain: ', input_widget=self.stain_input,
                            grid_layout=damaged_input_layout, x=0, y=2)

        self.grade_input = QLineEdit(self)
        self.add_input_line(label_name='Grade: ', input_widget=self.grade_input,
                            grid_layout=damaged_input_layout, x=1, y=0)

        damaged_info.setLayout(damaged_input_layout)
        main_layout.addWidget(damaged_info, alignment=Qt.AlignTop)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        button_layout.addStretch()

        # Save Button
        save_button = QPushButton('Save', self)
        save_button.setFixedWidth(80)
        save_button.clicked.connect(self.on_click)
        button_layout.addWidget(save_button)

        # clear button
        clear_button = QPushButton('Clear', self)
        clear_button. setFixedWidth(80)
        clear_button.clicked.connect(self.clear_all_inputs)
        button_layout.addWidget(clear_button, stretch=-1)

        main_layout.addLayout(button_layout, stretch=1)


        self.show()

    def add_input_line(self, label_name, input_widget, grid_layout, x, y):
        label = QLabel(label_name, self)
        label.setAlignment(Qt.AlignRight)
        label.setFixedWidth(100)
        label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        input_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        grid_layout.addWidget(label, x, y, alignment=Qt.AlignRight)
        grid_layout.addWidget(input_widget, x, y+1)

    # def add_input_line(self, label_name, input_widget, layout):
    #     input_layout = QHBoxLayout()
    #     label = QLabel(label_name, self)
    #     input_widget.setFixedWidth(50)
    #     input_layout.addWidget(label)
    #     input_layout.addWidget(input_widget)
    #     layout.addLayout(input_layout)

    def on_click(self):
        dataset_file = os.path.join(_Widget_dir, '../dataset/dataset.csv')
        serial_number = self.serial_number_input.text()
        device_model = self.device_model_input.text()

        # Add information into dataset
        with open(dataset_file, 'a', newline='', encoding='utf-8') as dataset:
            writer = csv.writer(dataset)
            writer.writerow([serial_number, device_model])

        self.clear_all_inputs()

    def clear_all_inputs(self):
        self.serial_number_input.clear()
        self.device_model_input.clear()


if __name__ == '__main__':
    app = QApplication([])
    control_panel = ControlPanel()
    control_panel.show()
    app.exec_()
