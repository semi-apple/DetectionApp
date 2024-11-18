import sys
import cv2 as cv
import numpy as np
from PyQt5.QtWidgets import QApplication, QColorDialog, QVBoxLayout, QPushButton, QMainWindow, QWidget
from PyQt5.QtCore import Qt, QPoint


class ColorToolBar(QWidget):
    def __init__(self, update_color_callback):
        super().__init__()
        self.update_color_callback = update_color_callback
        self.old_position = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Tool Bar")
        self.setGeometry(200, 200, 200, 100)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)

        layout = QVBoxLayout()
        color_btn = QPushButton("选择颜色", self)
        color_btn.clicked.connect(self.select_color)
        layout.addWidget(color_btn)
        self.setLayout(layout)

    def select_color(self):
        color = QColorDialog.getColor(initial=Qt.green, parent=self, options=QColorDialog.DontUseNativeDialog)
        if color.isValid():
            bgr_color = (color.blue(), color.green(), color.red())
            self.update_color_callback(bgr_color)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.old_position = event.globalPos()

    def mouseMoveEvent(self, event):
        if self.old_position is not None:
            delta = event.globalPos() - self.old_position
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_position = event.globalPos()

    def mouseReleaseEvent(self, event):
        self.old_position = None


class Implement(QMainWindow):
    def __init__(self, image):
        super().__init__()
        # self.setWindowTitle("Main Windows")
        # self.setGeometry(100, 100, 800, 600)

        self.color_container = [(0, 255, 0)]

        self.toolbar = ColorToolBar(self.update_color)
        self.toolbar.show()

        self.image = cv.imread('/Users/kunzhou/Desktop/demo/keyboard/20241003122511_keyboard.jpg')
        # self.image = image
        self.start_drawing()

    def update_color(self, color):
        self.color_container[0] = color

    def start_drawing(self):
        draw_multiple_rectangles(self.image, self.color_container)


def draw_multiple_rectangles(image, color_container):
    drawing = False
    start_point = (-1, -1)
    rectangles = []

    # 调整图像大小
    target_width = 1280
    target_height = 860
    image = cv.resize(image, (target_width, target_height))

    # 定义鼠标事件处理函数
    def draw_rectangle(event, x, y, flags, param):
        # color = color_container[0]
        nonlocal drawing, start_point, rectangles

        if event == cv.EVENT_LBUTTONDOWN:
            drawing = True
            start_point = (x, y)

        elif event == cv.EVENT_MOUSEMOVE:
            if drawing:
                end_point = (x, y)
                temp_image = image.copy()
                cv.rectangle(temp_image, start_point, end_point, color_container[0], 2)
                for rect, col in rectangles:
                    cv.rectangle(temp_image, rect[0], rect[1], col, 2)
                cv.imshow('Image', temp_image)

        elif event == cv.EVENT_LBUTTONUP:
            color = color_container[0]
            drawing = False
            end_point = (x, y)
            rectangles.append(((start_point, end_point), color))

            temp_image = image.copy()
            for rect, col in rectangles:
                cv.rectangle(temp_image, rect[0], rect[1], col, 2)
            cv.imshow('Image', temp_image)

    # 设置 OpenCV 窗口
    cv.namedWindow('Image')
    cv.setMouseCallback('Image', draw_rectangle)
    cv.imshow('Image', image)

    # 按空格键退出
    while True:
        key = cv.waitKey(1) & 0xFF
        if key == ord(' '):
            break

    # 关闭窗口
    cv.destroyAllWindows()

    # 最终绘制所有矩形
    for rect, col in rectangles:
        cv.rectangle(image, rect[0], rect[1], col, 2)
    return image


# 程序入口
if __name__ == "__main__":
    app = QApplication(sys.argv)

    image = cv.imread('/Users/kunzhou/Desktop/demo/keyboard/20241003122511_keyboard.jpg')
    window = Implement(image)
    window.show()

    sys.exit(app.exec())


