import sys
import os
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QFileDialog,
    QComboBox,
    QMessageBox,
    QProgressBar,
    QCheckBox,
    QDockWidget,
    QScrollArea,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QPixmap, QIcon, QMovie
from youtube_downloader import YouTubeDownloader
from twitter_downloader import TwitterDownloader

APP_AUTHOR = "tyz_kotono"
APP_VERSION = "1.2"


class GifPreviewDock(QDockWidget):
    def __init__(self, parent=None):
        super().__init__("GIF 预览", parent)
        self.setAllowedAreas(
            Qt.DockWidgetArea.RightDockWidgetArea | Qt.DockWidgetArea.LeftDockWidgetArea
        )
        self.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetMovable
            | QDockWidget.DockWidgetFeature.DockWidgetFloatable
        )

        # 创建预览内容
        self.preview_widget = QWidget()
        self.preview_layout = QVBoxLayout()

        # GIF 显示标签
        self.gif_label = QLabel()
        self.gif_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.gif_label.setMinimumSize(300, 200)
        self.preview_layout.addWidget(self.gif_label)

        # 控制按钮
        control_layout = QHBoxLayout()

        self.play_btn = QPushButton("播放/暂停")
        self.play_btn.clicked.connect(self.toggle_play)
        control_layout.addWidget(self.play_btn)

        self.stop_btn = QPushButton("停止")
        self.stop_btn.clicked.connect(self.stop_movie)
        control_layout.addWidget(self.stop_btn)

        self.preview_layout.addLayout(control_layout)

        # 文件信息标签
        self.info_label = QLabel("未加载 GIF 文件")
        self.preview_layout.addWidget(self.info_label)

        self.preview_widget.setLayout(self.preview_layout)
        self.setWidget(self.preview_widget)

        # 初始化 QMovie
        self.movie = None

        # 默认隐藏
        self.hide()

    def load_gif(self, gif_path):
        """加载并播放 GIF"""
        if self.movie:
            self.movie.stop()
            self.movie.deleteLater()

        self.movie = QMovie(gif_path)
        if self.movie.isValid():
            # 设置 GIF 大小
            movie_size = self.movie.currentPixmap().size()
            scaled_size = movie_size.scaled(
                300, 200, Qt.AspectRatioMode.KeepAspectRatio
            )
            self.movie.setScaledSize(scaled_size)
            self.gif_label.setMovie(self.movie)
            self.movie.start()

            # 更新信息
            self.info_label.setText(f"文件: {os.path.basename(gif_path)}")
            self.show()
        else:
            self.gif_label.setText("无法加载 GIF 文件")
            self.info_label.setText("加载失败")

    def toggle_play(self):
        """播放/暂停 GIF"""
        if self.movie and self.movie.isValid():
            if self.movie.state() == QMovie.MovieState.Running:
                self.movie.setPaused(True)
            else:
                self.movie.setPaused(False)

    def stop_movie(self):
        """停止 GIF 播放"""
        if self.movie and self.movie.isValid():
            self.movie.stop()
            self.movie.start()

    def closeEvent(self, event):
        """关闭时停止播放"""
        if self.movie:
            self.movie.stop()
        super().closeEvent(event)


class DownloadThread(QThread):
    progress = pyqtSignal(str)
    finished = pyqtSignal(bool, str)
    gif_created = pyqtSignal(str)  # 新增：GIF 创建完成信号

    def __init__(self, platform, url, output_path, **kwargs):
        super().__init__()
        self.platform = platform
        self.url = url
        self.output_path = output_path
        self.kwargs = kwargs

    def run(self):
        try:

            def progress_hook(d):
                if d["status"] == "downloading":
                    if "total_bytes" in d and d["total_bytes"]:
                        percent = d["downloaded_bytes"] / d["total_bytes"] * 100
                        self.progress.emit(f"下载中... {percent:.1f}%")
                    else:
                        self.progress.emit("下载中...")
                elif d["status"] == "finished":
                    self.progress.emit("下载完成，正在处理...")

            if self.platform == "YouTube":
                downloader = YouTubeDownloader()
                downloader.download_video(
                    self.url,
                    self.output_path,
                    format_id=self.kwargs.get("format_id"),
                    subtitle_lang=self.kwargs.get("subtitle_lang"),
                    progress_callback=progress_hook,
                )
            else:  # Twitter
                downloader = TwitterDownloader()
                downloader.download_video(
                    self.url,
                    self.output_path,
                    convert_to_gif=self.kwargs.get("convert_to_gif", False),
                    progress_callback=progress_hook,
                )

                # 如果是 GIF 转换，发送信号
                if self.kwargs.get("convert_to_gif", False):
                    # 查找生成的 GIF 文件
                    for file in os.listdir(self.output_path):
                        if file.endswith(".gif"):
                            gif_path = os.path.join(self.output_path, file)
                            self.gif_created.emit(gif_path)
                            break

            self.finished.emit(True, "下载完成！")
        except Exception as e:
            self.finished.emit(False, f"下载失败: {e}")


class VideoDownloader(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"XToolkit 视频下载器 v{APP_VERSION}")
        self.setGeometry(200, 200, 800, 500)
        self.download_thread = None
        self.youtube_downloader = YouTubeDownloader()
        self.twitter_downloader = TwitterDownloader()
        self.setup_icon()
        self.init_ui()
        self.setup_dock()
        self.add_about_menu()

    def setup_icon(self):
        """设置程序图标"""
        icon_path = os.path.join(os.path.dirname(__file__), "Icon", "Icon.jpg")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

    def setup_dock(self):
        """设置 Dock 窗口"""
        self.gif_dock = GifPreviewDock(self)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.gif_dock)

    def init_ui(self):
        # 创建中央窗口部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()

        # 链接输入
        self.url_label = QLabel("请输入视频链接:")
        self.url_input = QLineEdit()
        layout.addWidget(self.url_label)
        layout.addWidget(self.url_input)

        # 平台选择
        self.platform_label = QLabel("请选择平台:")
        self.platform_combo = QComboBox()
        self.platform_combo.addItems(["Twitter", "YouTube"])  # 修改顺序，Twitter 在前
        self.platform_combo.currentTextChanged.connect(self.on_platform_change)
        layout.addWidget(self.platform_label)
        layout.addWidget(self.platform_combo)

        # 画质选择（仅YouTube）
        self.quality_label = QLabel("请选择画质:")
        self.quality_combo = QComboBox()
        layout.addWidget(self.quality_label)
        layout.addWidget(self.quality_combo)
        self.quality_label.hide()
        self.quality_combo.hide()

        # 字幕选择（仅YouTube）
        self.subtitle_label = QLabel("请选择字幕:")
        self.subtitle_combo = QComboBox()
        layout.addWidget(self.subtitle_label)
        layout.addWidget(self.subtitle_combo)
        self.subtitle_label.hide()
        self.subtitle_combo.hide()

        # Twitter GIF 转换选项
        self.gif_checkbox = QCheckBox("转换为 GIF 动图")
        layout.addWidget(self.gif_checkbox)
        self.gif_checkbox.show()  # 默认显示，因为默认是 Twitter

        # 下载位置
        self.path_label = QLabel("请选择下载位置:")
        self.path_input = QLineEdit()
        self.path_btn = QPushButton("浏览")
        self.path_btn.clicked.connect(self.choose_path)
        path_layout = QHBoxLayout()
        path_layout.addWidget(self.path_input)
        path_layout.addWidget(self.path_btn)
        layout.addWidget(self.path_label)
        layout.addLayout(path_layout)

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # 状态标签
        self.status_label = QLabel("")
        layout.addWidget(self.status_label)

        # 检测按钮
        self.detect_btn = QPushButton("检测视频信息")
        self.detect_btn.clicked.connect(self.detect_info)
        layout.addWidget(self.detect_btn)

        # 下载按钮
        self.download_btn = QPushButton("下载")
        self.download_btn.clicked.connect(self.download_video)
        layout.addWidget(self.download_btn)

        # GIF 预览按钮（仅 Twitter GIF 模式时显示）
        self.preview_btn = QPushButton("预览 GIF")
        self.preview_btn.clicked.connect(self.preview_gif)
        self.preview_btn.show()  # 默认显示，因为默认是 Twitter
        layout.addWidget(self.preview_btn)

        central_widget.setLayout(layout)

    def on_platform_change(self, text):
        if text == "YouTube":
            self.quality_label.show()
            self.quality_combo.show()
            self.subtitle_label.show()
            self.subtitle_combo.show()
            self.gif_checkbox.hide()
            self.preview_btn.hide()
        else:
            self.quality_label.hide()
            self.quality_combo.hide()
            self.subtitle_label.hide()
            self.subtitle_combo.hide()
            self.gif_checkbox.show()
            self.preview_btn.show()

    def choose_path(self):
        path = QFileDialog.getExistingDirectory(self, "选择下载文件夹")
        if path:
            self.path_input.setText(path)

    def detect_info(self):
        url = self.url_input.text().strip()
        platform = self.platform_combo.currentText()
        if not url:
            QMessageBox.warning(self, "提示", "请输入视频链接")
            return

        try:
            if platform == "YouTube":
                info = self.youtube_downloader.get_video_info(url)
                formats = self.youtube_downloader.get_available_formats(info)
                subtitles = self.youtube_downloader.get_available_subtitles(info)

                # 更新画质选项
                self.quality_combo.clear()
                for label, format_id in formats:
                    self.quality_combo.addItem(label, format_id)

                # 更新字幕选项
                self.subtitle_combo.clear()
                for label, lang in subtitles:
                    self.subtitle_combo.addItem(label, lang)

                QMessageBox.information(self, "检测完成", "已获取画质和字幕选项")
            else:
                info = self.twitter_downloader.get_video_info(url)
                QMessageBox.information(
                    self, "检测完成", f'Twitter 视频: {info.get("title", "未知标题")}'
                )
        except Exception as e:
            QMessageBox.critical(self, "错误", f"检测失败: {e}")

    def download_video(self):
        url = self.url_input.text().strip()
        platform = self.platform_combo.currentText()
        path = self.path_input.text().strip()

        if not url or not path:
            QMessageBox.warning(self, "提示", "请填写完整信息")
            return

        # 准备下载参数
        kwargs = {}
        if platform == "YouTube":
            if self.quality_combo.currentData():
                kwargs["format_id"] = self.quality_combo.currentData()
            if self.subtitle_combo.currentData():
                kwargs["subtitle_lang"] = self.subtitle_combo.currentData()
        else:  # Twitter
            kwargs["convert_to_gif"] = self.gif_checkbox.isChecked()

        # 禁用按钮，显示进度条
        self.download_btn.setEnabled(False)
        self.detect_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # 不确定进度
        self.status_label.setText("准备下载...")

        # 启动下载线程
        self.download_thread = DownloadThread(platform, url, path, **kwargs)
        self.download_thread.progress.connect(self.update_progress)
        self.download_thread.finished.connect(self.download_finished)
        self.download_thread.gif_created.connect(self.on_gif_created)
        self.download_thread.start()

    def update_progress(self, message):
        self.status_label.setText(message)

    def download_finished(self, success, message):
        self.progress_bar.setVisible(False)
        self.download_btn.setEnabled(True)
        self.detect_btn.setEnabled(True)
        self.status_label.setText("")

        if success:
            QMessageBox.information(self, "完成", message)
        else:
            QMessageBox.critical(self, "错误", message)

    def on_gif_created(self, gif_path):
        """GIF 创建完成后的回调"""
        reply = QMessageBox.question(
            self,
            "GIF 创建完成",
            f"GIF 文件已保存到: {gif_path}\n是否立即预览？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.show_gif_preview(gif_path)

    def preview_gif(self):
        """手动预览 GIF 按钮"""
        path = self.path_input.text().strip()
        if not path:
            QMessageBox.warning(self, "提示", "请先选择下载位置")
            return

        # 查找 GIF 文件
        gif_files = []
        for file in os.listdir(path):
            if file.endswith(".gif"):
                gif_files.append(os.path.join(path, file))

        if not gif_files:
            QMessageBox.information(self, "提示", "未找到 GIF 文件")
            return

        if len(gif_files) == 1:
            self.show_gif_preview(gif_files[0])
        else:
            # 多个 GIF 文件时让用户选择
            file_path, _ = QFileDialog.getOpenFileName(
                self, "选择要预览的 GIF 文件", path, "GIF 文件 (*.gif)"
            )
            if file_path:
                self.show_gif_preview(file_path)

    def show_gif_preview(self, gif_path):
        """显示 GIF 预览窗口"""
        self.gif_dock.load_gif(gif_path)

    def add_about_menu(self):
        menubar = self.menuBar()
        if menubar is not None:
            help_menu = menubar.addMenu("帮助")
            if help_menu is not None:
                about_action = help_menu.addAction("关于")
                if about_action is not None:
                    about_action.triggered.connect(self.show_about_dialog)

    def show_about_dialog(self):
        QMessageBox.information(
            self,
            "关于",
            f"XToolkit v{APP_VERSION}\n作者: {APP_AUTHOR}\n\n一个支持YouTube和Twitter视频下载的工具。",
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # 设置应用程序图标
    icon_path = os.path.join(os.path.dirname(__file__), "Icon", "Icon.jpg")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    win = VideoDownloader()
    win.show()
    sys.exit(app.exec())
