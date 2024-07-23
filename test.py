from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QVBoxLayout

class SubWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Sub Window')
        self.setGeometry(300, 300, 200, 150)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Main Window')
        self.setGeometry(100, 100, 300, 200)

        self.sub_window = SubWindow(self)

        self.initUI()

    def initUI(self):
        hide_button = QPushButton('Hide Main Window', self)
        hide_button.clicked.connect(self.hide_main_window)

        layout = QVBoxLayout()
        layout.addWidget(hide_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def hide_main_window(self):
        self.hide()
        self.sub_window.show()


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
