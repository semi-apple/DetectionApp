import csv
from PyQt5.QtWidgets import QPushButton, QVBoxLayout, QWidget, QLineEdit, QLabel, QHBoxLayout
from PyQt5.QtWidgets import QApplication


class ControlPanel(QWidget):
    def __init__(self):
        super().__init__()

        # Serial Number
        self.serial_number_input = QLineEdit(self)
        self.serial_number_input.setPlaceholderText('Enter serial number')

        # Device Model
        self.device_model_input = QLineEdit(self)
        self.device_model_input.setPlaceholderText('Enter device model')

        # Save Button
        self.save_button = QPushButton('Save', self)
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Control Panel')
        self.setGeometry(100, 100, 300, 200)
        layout = QVBoxLayout(self)  # Layout directly set to self, the QWidget

        # Adding input lines
        self.add_input_line('Serial Number: ', self.serial_number_input, layout)
        self.add_input_line('Device Model: ', self.device_model_input, layout)

        # Connect the button to on_click method
        self.save_button.clicked.connect(self.on_click)
        layout.addWidget(self.save_button)

        self.show()

    def add_input_line(self, label_name, input_widget, layout):
        input_layout = QHBoxLayout()
        label = QLabel(label_name, self)
        input_layout.addWidget(label)
        input_layout.addWidget(input_widget)
        layout.addLayout(input_layout)

    def on_click(self):
        dataset_file = 'Dataset/dataset.csv'
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
