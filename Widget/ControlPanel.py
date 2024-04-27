import csv
from PyQt5.QtWidgets import QMainWindow, QPushButton, QVBoxLayout, QWidget, QLineEdit, QLabel, QHBoxLayout
from PyQt5.QtWidgets import QApplication


class ControlPanel(QMainWindow):
    def __init__(self):
        super().__init__()

        # Serial Number
        self.serial_number_input = QLineEdit(self)
        self.serial_number_input.setPlaceholderText('Inter serial number')

        # Device Model
        self.device_model_input = QLineEdit(self)
        self.device_model_input.setPlaceholderText('Inter device model')

        # other metadata

        self.save_button = QPushButton('Save', self)
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Control Panel')
        self.setGeometry(100, 100, 300, 200)
        layout = QVBoxLayout()

        # set input line
        self.add_input_line('Serial Number: ', self.serial_number_input, layout)
        self.add_input_line('Device Model: ', self.device_model_input, layout)

        self.save_button.clicked.connect(self.on_click)
        layout.addWidget(self.save_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def add_input_line(self, label_name, input_widget, layout):
        input_layout = QHBoxLayout()
        label = QLabel(label_name, self)
        input_layout.addWidget(label)
        input_layout.addWidget(input_widget)
        layout.addLayout(input_layout)

    def on_click(self):
        dataset_file = '../Dataset/dataset.csv'
        serial_number = self.serial_number_input.text()
        device_model = self.device_model_input.text()

        # add information into dataset
        with open(dataset_file, 'a', newline='', encoding='utf-8') as dataset:
            writer = csv.writer(dataset)
            writer.writerow([serial_number, device_model])

        self.clear_all_inputs()

    def clear_all_inputs(self):
        layout = self.centralWidget().layout()

        for i in range(layout.count()):
            widget = layout.itemAt(i).widget()

            if isinstance(widget, QLineEdit):
                widget.clear()


if __name__ == '__main__':
    app = QApplication([])
    control_panel = ControlPanel()
    control_panel.show()
    app.exec_()
