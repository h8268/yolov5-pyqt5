import sys
import cv2
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QTimer, QThread, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap
from ultralytics import YOLO

class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(QtGui.QImage)

    def run(self):
        cap = cv2.VideoCapture(0)  # 0 为默认摄像头
        model = YOLO('yolov5s.pt')  # 加载YOLOv5模型

        while True:
            ret, cv_img = cap.read()
            if ret:
                # 将BGR转换为RGB
                rgb_img = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
                # 进行检测
                results = model(rgb_img)
                # 绘制检测结果
                if len(results) > 0:
                    annotated_img = results[0].render()[0]
                else:
                    annotated_img = rgb_img  # 如果没有检测结果，使用原图

                # 转换为QImage
                h, w, ch = annotated_img.shape
                bytes_per_line = ch * w
                qt_img = QImage(annotated_img.data, w, h, bytes_per_line, QImage.Format_RGB888).rgbSwapped()
                self.change_pixmap_signal.emit(qt_img)
            else:
                break

class App(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('YOLOv5 Video Stream')
        self.setGeometry(100, 100, 800, 600)
        self.image_label = QtWidgets.QLabel(self)
        self.image_label.resize(800, 600)
        self.start_video()

    def start_video(self):
        self.thread = VideoThread()
        self.thread.change_pixmap_signal.connect(self.update_image)
        self.thread.start()

    def update_image(self, qt_img):
        self.image_label.setPixmap(QPixmap.fromImage(qt_img))

    def closeEvent(self, event):
        self.thread.terminate()
        super().closeEvent(event)

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    ex = App()
    ex.show()
    sys.exit(app.exec_())