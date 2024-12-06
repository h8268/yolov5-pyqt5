
import torch
import cv2
from PyQt5 import QtWidgets, QtMultimedia, QtMultimediaWidgets
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QFileDialog, QDialog, QLabel, QVBoxLayout, QMainWindow, QAction, QToolBar, QPushButton, \
    QComboBox, QSplitter, QWidget, QHBoxLayout, QSlider, QTableWidget, QTableWidgetItem, QTextEdit, QInputDialog, \
    QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QMessageBox
from PyQt5.QtCore import Qt, QSize, QUrl, QTimer, QDateTime
import sys
import os
from datetime import datetime

class AlgorithmInterface(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(AlgorithmInterface, self).__init__(parent)
        self.parent = parent  # 保存对MainWindow的引用
        self.setWindowTitle("算法界面")
        self.setGeometry(100, 100, 800, 600)
        self.create_layout()
        self.add_default_algorithms()  # 添加默认算法

    def create_layout(self):
        layout = QVBoxLayout(self)

        # 标题：算法选择
        self.title_label = QLabel("算法选择")
        layout.addWidget(self.title_label)

        # 算法类别列表
        self.algorithm_list = QComboBox()  # 或者使用 QListWidget 如果您想要一个列表而不是下拉框
        self.algorithm_list.addItems(["图像类算法", "视频类算法", "文本类算法"])
        layout.addWidget(self.algorithm_list)

        # 表格控件
        self.table_widget = QTableWidget()
        self.table_widget.setRowCount(0)  # 初始化时不设置行数，可以动态添加
        self.table_widget.setColumnCount(4)  # 设置列数为4
        self.table_widget.setHorizontalHeaderLabels(["序号", "算法名称", "算法功能", "算法选用"])
        layout.addWidget(self.table_widget)

        # 算法描述文本框
        self.algorithm_description = QTextEdit()
        self.algorithm_description.setPlaceholderText("算法描述")
        layout.addWidget(self.algorithm_description)

        # 参数设置文本框
        self.parameter_settings = QTextEdit()
        self.parameter_settings.setPlaceholderText("参数设置")
        layout.addWidget(self.parameter_settings)

        # 按钮区域
        button_layout = QHBoxLayout()
        layout.addLayout(button_layout)

        # 添加算法按钮
        add_button = QPushButton("添加算法")
        add_button.clicked.connect(self.add_algorithm)
        button_layout.addWidget(add_button)

        # 修改算法按钮
        modify_button = QPushButton("修改算法")
        modify_button.clicked.connect(self.modify_algorithm)
        button_layout.addWidget(modify_button)

        # 删除算法按钮
        delete_button = QPushButton("删除算法")
        delete_button.clicked.connect(self.delete_algorithm)
        button_layout.addWidget(delete_button)

        # 运行算法按钮
        run_button = QPushButton("运行算法")
        run_button.clicked.connect(self.run_algorithm)
        button_layout.addWidget(run_button)

    def add_default_algorithms(self):
        # 添加默认算法到列表和表格
        default_algorithms = [
            {"name": "YOLOv5", "function": "图像识别"},
            # 可以在这里添加更多默认算法
        ]
        for algo in default_algorithms:
            self.add_algorithm(algo["name"], algo["function"])

    def add_algorithm(self, algorithm_name=None, algorithm_function=None):
        # 如果没有提供算法名称和功能，则通过对话框获取
        if not algorithm_name or not algorithm_function:
            algorithm_name, ok_name = QInputDialog.getText(self, "添加算法", "请输入算法名称:")
            if not ok_name or not algorithm_name:
                return
            algorithm_function, ok_function = QInputDialog.getText(self, "添加算法", "请输入算法功能:")
            if not ok_function or not algorithm_function:
                return

        current_row_count = self.table_widget.rowCount()
        self.table_widget.insertRow(current_row_count)
        self.table_widget.setItem(current_row_count, 0, QTableWidgetItem(str(current_row_count + 1)))
        self.table_widget.setItem(current_row_count, 1, QTableWidgetItem(algorithm_name))
        self.table_widget.setItem(current_row_count, 2, QTableWidgetItem(algorithm_function))
        self.table_widget.setItem(current_row_count, 3, QTableWidgetItem("否"))


    def modify_algorithm(self):
        # 获取选中的行
        selected_row = self.table_widget.currentRow()
        if selected_row != -1:  # 确保选中了一行
            # 弹出对话框让用户修改算法信息
            algorithm_name, ok = QtWidgets.QInputDialog.getText(self, "修改算法", "请输入新的算法名称:")
            if ok and algorithm_name:
                self.table_widget.setItem(selected_row, 1, QTableWidgetItem(algorithm_name))
            # 可以继续添加修改算法功能和选用状态的逻辑

        else:
            QtWidgets.QMessageBox.information(self, "提示", "请先选择一个算法进行修改。")


    def delete_algorithm(self):
        # 获取选中的行
        selected_row = self.table_widget.currentRow()
        if selected_row != -1:  # 确保选中了一行
            # 弹出确认对话框确认删除
            res = QtWidgets.QMessageBox.question(self, "确认", "确定要删除这个算法吗?")
            if res == QtWidgets.QMessageBox.Yes:
                self.table_widget.removeRow(selected_row)
        else:
            QtWidgets.QMessageBox.information(self, "提示", "请先选择一个算法进行删除。")



    def run_algorithm(self):
        # 运行算法逻辑
        if self.parent:
            # results_text = self.parent.run_yolo_algorithm()  # 调用 MainWindow 中的方法并获取结果
            self.parent.run_yolo_and_display()
            self.close()

    # def display_results(self, results_text):
    #     # 将结果显示在算法描述文本框中
    #     self.algorithm_description.setText(results_text)

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle("智能计算与推荐")
        self.setGeometry(100, 100, 1000, 800)

        # 当前目录和图像列表
        self.image_list = []
        self.current_index = -1  # 当前显示的图像索引

        # 初始化视频播放器相关组件
        self.video_slider = None

        # 创建菜单栏、工具栏和布局
        self.create_menu_bar()
        self.create_tool_bar()
        self.create_main_layout()

    # def run_yolo_algorithm(self):
    #     try:
    #         current_image_path = self.get_current_image_path()
    #         if not current_image_path:
    #             raise ValueError("无法获取当前图像路径")
    #
    #         # 使用YOLOv5进行图像推理
    #         model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)
    #         results = model(current_image_path)
    #
    #         # 将结果转换为文本格式
    #         results_text = results.pandas().xyxy[0].to_string(index=False)
    #         return results_text  # 返回结果文本
    #
    #     except Exception as e:
    #         error_message = f"Error running Yolo algorithm: {e}"
    #         return error_message  # 返回错误信息
        # 加载YOLOv5模型
        # 确保您的设备支持CUDA
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

        # 加载模型
        self.model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True).to(device)


    def run_yolo_and_display(self):

        current_image_path = self.get_current_image_path()
        if not current_image_path:
            QtWidgets.QMessageBox.information(self, "提示", "请先选择一个图像文件。")
            return


        # 使用YOLOv5进行图像推理

        results = self.model(current_image_path)

        # 将检测结果绘制到图片上
        annotated_image = results.render()[0]
        annotated_pixmap = self.convert_cv_qt(annotated_image)

        # 显示标注后的图片
        scene = QGraphicsScene()  # 创建一个新的场景
        pixmap_item = QGraphicsPixmapItem(annotated_pixmap)  # 创建一个QGraphicsPixmapItem对象
        scene.addItem(pixmap_item)  # 将图像项添加到场景中
        self.image_view.setScene(scene)  # 将场景设置到QGraphicsView

    def convert_cv_qt(self, cv_img):
        """将OpenCV图像转换为QPixmap"""
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        qt_img = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888).rgbSwapped()
        return QPixmap.fromImage(qt_img)

    def get_current_image_path(self):
        """获取当前显示的图像路径"""
        if self.current_index >= 0 and self.current_index < len(self.image_list):
            return self.image_list[self.current_index]
        return None



    def display_image_and_info(self, file_path):
        # 显示图片
        pixmap = QPixmap(file_path)
        scene = QGraphicsScene()
        scene.addPixmap(pixmap)  # 将 QPixmap 添加到场景中
        self.image_view.setScene(scene)  # 设置 QGraphicsView 的场景

        # 更新图像信息展示
        file_info = os.path.basename(file_path)
        file_size = pixmap.size()
        file_type = os.path.splitext(file_info)[-1].upper()
        load_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        info_text = (
            f"加载路径：{file_path}\n"
            f"文件名：{file_info}\n"
            f"图像大小：{file_size.width()} x {file_size.height()} pixels\n"
            f"图像类型：{file_type}\n"
            f"加载日期：{load_date}"
        )
        self.image_info_display.setText(info_text)

        # 调整 QGraphicsView 以适应场景大小
        self.image_view.setFixedSize(pixmap.size())
        self.image_view.setDragMode(QGraphicsView.ScrollHandDrag)  # 允许拖动查看大图



    def save_file(self):
        # 打开保存文件对话框
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self, "保存文件", "", "All Files (*);;Text Files (*.txt)",
                                                   options=options)
        if file_path:
            # 在这里实现保存逻辑（例如保存当前显示的数据）
            print(f"文件已保存到: {file_path}")

    def create_menu_bar(self):
        menu_bar = self.menuBar()

        # 创建“数据”菜单并添加二级目录
        data_menu = menu_bar.addMenu("数据")
        open_action = QAction("打开", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.show_data_type_dialog)
        data_menu.addAction(open_action)

        save_action = QAction("保存", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_file)
        data_menu.addAction(save_action)

        exit_action = QAction("退出", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        data_menu.addAction(exit_action)

        # 创建其他菜单
        menu_bar.addMenu("应用")
        menu_bar.addMenu("控制")

        # 创建“算法”菜单
        algorithm_menu = menu_bar.addMenu("算法")  # 定义algorithm_menu变量
        algorithm_action = QAction("切换到算法界面", self)
        algorithm_action.triggered.connect(self.switch_to_algorithm_interface)
        algorithm_menu.addAction(algorithm_action)  # 使用algorithm_menu变量添加动作

    def switch_to_algorithm_interface(self):
        if not hasattr(self, 'algorithm_interface') or self.algorithm_interface is None:
            self.algorithm_interface = AlgorithmInterface(self)  # 创建算法界面实例
        self.algorithm_interface.show()  # 显示算法界面
        self.algorithm_interface.raise_()  # 将算法界面置顶

    def create_tool_bar(self):
        tool_bar = QToolBar("工具栏")
        self.addToolBar(tool_bar)

        # 添加打开和保存按钮
        open_action = QAction("打开", self)
        open_action.triggered.connect(self.show_data_type_dialog)
        tool_bar.addAction(open_action)

        save_action = QAction("保存", self)
        save_action.triggered.connect(self.save_file)
        tool_bar.addAction(save_action)

    def create_main_layout(self):
        # 设置主窗口的中央小部件
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # 创建一个垂直布局管理器
        self.layout = QVBoxLayout(self.central_widget)

        # 创建一个标签作为主标签
        self.main_label = QLabel("数据显示器")
        self.main_label.setAlignment(Qt.AlignCenter)
        self.main_label.setFixedHeight(50)
        self.layout.addWidget(self.main_label)

        # 创建一个分割器，用于分隔数据展示区和图像信息区域
        self.splitter = QSplitter(Qt.Horizontal)
        self.layout.addWidget(self.splitter)



        # 图像显示区域使用 QGraphicsView
        self.image_view = QGraphicsView()
        self.image_view.setDragMode(QGraphicsView.ScrollHandDrag)  # 允许拖动查看大图
        self.layout.addWidget(self.image_view)

        # 图像信息展示区域
        self.image_info_display = QLabel("图像信息区域")
        self.image_info_display.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.image_info_display.setWordWrap(True)
        self.layout.addWidget(self.image_info_display)

        # 创建按钮区域
        self.button_layout = QHBoxLayout()
        self.layout.addLayout(self.button_layout)

    def show_data_type_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("数据类型选择")

        layout = QVBoxLayout()
        label = QLabel("请选择数据类型：")
        layout.addWidget(label)

        # 下拉菜单选择数据类型
        self.data_type_combo = QComboBox()
        self.data_type_combo.addItems(["图像数据", "文本数据", "视频数据"])
        layout.addWidget(self.data_type_combo)

        # 确定按钮，选择数据类型后弹出文件选择对话框
        confirm_button = QPushButton("确定")
        confirm_button.clicked.connect(lambda: self.data_type_selected(dialog))
        layout.addWidget(confirm_button)

        dialog.setLayout(layout)
        dialog.exec_()

    def data_type_selected(self, dialog):
        selected_type = self.data_type_combo.currentText()
        dialog.accept()  # 关闭数据类型选择对话框

        if selected_type == "图像数据":
            self.open_file("png|jpg|jpeg|webp")
            self.setup_image_buttons()
        elif selected_type == "文本数据":
            self.open_file("txt")
            self.hide_buttons()
        elif selected_type == "视频数据":
            print("进入视频播放")
            self.open_file("mp4|avi|mkv")

    def setup_image_buttons(self):
        # 清空旧按钮并设置图像数据相关按钮
        self.clear_buttons()
        self.previous_button = QPushButton("上一张")
        self.previous_button.clicked.connect(self.show_previous_image)
        self.button_layout.addWidget(self.previous_button)

        self.next_button = QPushButton("下一张")
        self.next_button.clicked.connect(self.show_next_image)
        self.button_layout.addWidget(self.next_button)

    def setup_video_player(self, file_path):
        # 清空旧按钮
        self.clear_buttons()

        # 如果有之前的视频播放任务，先释放资源
        if hasattr(self, "video_cap") and self.video_cap is not None:
            self.video_cap.release()

        # 初始化 OpenCV VideoCapture
        self.video_cap = cv2.VideoCapture(file_path)
        if not self.video_cap.isOpened():
            print("无法打开视频文件")
            return

        # 创建视频控制按钮
        self.play_button = QPushButton("播放")
        self.play_button.clicked.connect(self.play_video)
        self.button_layout.addWidget(self.play_button)

        self.pause_button = QPushButton("暂停")
        self.pause_button.clicked.connect(self.pause_video)
        self.button_layout.addWidget(self.pause_button)

        # 创建进度条
        self.video_slider = QSlider(Qt.Horizontal)
        self.video_slider.setRange(0, 100)
        self.video_slider.sliderMoved.connect(self.set_video_position)
        self.layout.addWidget(self.video_slider)

        # 创建 QTimer 用于定时更新帧
        self.timer = QTimer(self)
        self.timer.start(30)
        self.timer.timeout.connect(self.update_video_frame)

        # 启用滑动条
        self.video_slider.setEnabled(True)

        # 显示视频文件信息
        self.display_video_info(file_path)

    def hide_buttons(self):
        # 隐藏按钮
        self.clear_buttons()

    def clear_buttons(self):
        # 清空按钮布局中的所有组件
        for i in reversed(range(self.button_layout.count())):
            self.button_layout.itemAt(i).widget().deleteLater()
        if hasattr(self, "video_slider") and self.video_slider:
            self.video_slider.deleteLater()
            self.video_slider = None

    def open_file(self, file_types):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "选择文件", "",
                                                   f"{file_types} Files (*.{file_types.lower().replace('|', ' *.')});;All Files (*)",
                                                   options=options)
        if file_path:
            if "txt" in file_types:
                self.display_text_and_info(file_path)
            elif "mp4" in file_types or "avi" in file_types or "mkv" in file_types:
                self.setup_video_player(file_path)
            else:
                self.load_image_list(os.path.dirname(file_path))  # 更新图像列表
                self.current_index = self.image_list.index(file_path)  # 设置当前索引
                self.display_image_and_info(file_path)  # 显示选中的图像

    def display_text_and_info(self, file_path):
        # 显示文本内容
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.data_display.setText(content)
        self.data_display.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        file_time = QDateTime.fromSecsSinceEpoch(int(os.path.getmtime(file_path))).toString("yyyy-MM-dd hh:mm:ss")
        self.image_info_display.setText(
            f"文件名: {file_name}\n大小: {file_size} bytes\n修改日期: {file_time}"
        )

    def play_video(self):
        if self.video_cap:
            self.timer.start(30)  # 每 30 毫秒更新一帧

    def pause_video(self):
        if self.video_cap:
            self.timer.stop()


    def update_video_frame(self):
        if self.video_cap:
            ret, frame = self.video_cap.read()
            if ret:
                # 转换为 RGB 格式
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                height, width, channel = rgb_frame.shape
                qimage = QImage(rgb_frame.data, width, height, QImage.Format_RGB888)

                # 创建 QGraphicsScene 和 QGraphicsPixmapItem
                scene = QGraphicsScene()
                pixmap_item = QGraphicsPixmapItem(QPixmap.fromImage(qimage))
                scene.addItem(pixmap_item)  # 将 QGraphicsPixmapItem 添加到场景中

                # 将场景设置到 QGraphicsView
                self.image_view.setScene(scene)

                # 更新滑动条位置
                current_frame = self.video_cap.get(cv2.CAP_PROP_POS_FRAMES)
                total_frames = self.video_cap.get(cv2.CAP_PROP_FRAME_COUNT)
                if total_frames > 0:
                    self.video_slider.setValue(int((current_frame / total_frames) * 100))
            else:
                # 视频播放完毕，停止定时器
                self.timer.stop()

    def set_video_position(self, position):
        if self.video_cap:
            total_frames = self.video_cap.get(cv2.CAP_PROP_FRAME_COUNT)
            target_frame = (position / 100) * total_frames
            self.video_cap.set(cv2.CAP_PROP_POS_FRAMES, target_frame)

    def display_video_info(self, file_path):
        # 获取视频文件的基础信息
        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)  # 文件大小
        file_time = QDateTime.fromSecsSinceEpoch(int(os.path.getmtime(file_path))).toString("yyyy-MM-dd hh:mm:ss")

        # 使用 OpenCV 获取视频的详细信息
        video_cap = cv2.VideoCapture(file_path)
        if video_cap.isOpened():
            width = int(video_cap.get(cv2.CAP_PROP_FRAME_WIDTH))  # 宽度
            height = int(video_cap.get(cv2.CAP_PROP_FRAME_HEIGHT))  # 高度
            fps = video_cap.get(cv2.CAP_PROP_FPS)  # 帧率
            frame_count = int(video_cap.get(cv2.CAP_PROP_FRAME_COUNT))  # 总帧数
            duration = frame_count / fps if fps > 0 else 0  # 视频时长（秒）
            video_cap.release()
        else:
            width, height, fps, frame_count, duration, encoding_format = 0, 0, 0, 0, 0, "N/A"

        # 格式化显示信息
        info_text = (
            f"加载路径：{file_path}\n"
            f"文件名：{file_name}\n"
            f"视频大小：{width} x {height} pixels\n"
            f"帧率：{fps:.2f}\n"
            f"总帧数：{frame_count}\n"
            f"视频时长：{duration:.2f} 秒\n"
            f"修改日期：{file_time}\n"
            f"文件大小：{file_size} bytes"
        )
        self.image_info_display.setText(info_text)

    def load_image_list(self, directory):
        self.image_list = [os.path.join(directory, f).replace("\\", "/") for f in os.listdir(directory) if
                           f.lower().endswith(('png', 'jpg', 'jpeg', 'webp'))]
        if self.image_list:  # 确保列表不为空
            self.current_index = 0  # 设置当前索引为第一个图像
            self.display_image_and_info(self.image_list[self.current_index])  # 显示第一个图像

    def display_image_and_info(self, file_path):
        pixmap = QPixmap(file_path)
        scene = QGraphicsScene()
        scene.addPixmap(pixmap)
        self.image_view.setScene(scene)

        file_info = os.path.basename(file_path)
        file_size = pixmap.size()
        file_type = os.path.splitext(file_info)[-1].upper()
        load_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        info_text = (
            f"加载路径：{file_path}\n"
            f"文件名：{file_info}\n"
            f"图像大小：{file_size.width()} x {file_size.height()} pixels\n"
            f"图像类型：{file_type}\n"
            f"加载日期：{load_date}"
        )
        self.image_info_display.setText(info_text)

        self.image_view.setFixedSize(pixmap.size())
        self.image_view.setDragMode(QGraphicsView.ScrollHandDrag)
    def show_previous_image(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.display_image_and_info(self.image_list[self.current_index])

    def show_next_image(self):
        if self.current_index < len(self.image_list) - 1:
            self.current_index += 1
            self.display_image_and_info(self.image_list[self.current_index])



app = QtWidgets.QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec_())

