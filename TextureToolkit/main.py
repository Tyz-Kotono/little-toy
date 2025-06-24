import sys
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QWidget,
    QVBoxLayout,
    QDockWidget,
    QHBoxLayout,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from RGBAChannelMere import RGBAChannelMere
from MergeAtalas import MergeAtlasDock


class ButtonDock(QDockWidget):
    def __init__(self, parent=None):
        super().__init__("Atlas 控制", parent)
        self.setAllowedAreas(Qt.DockWidgetArea.AllDockWidgetAreas)
        self.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetMovable
            | QDockWidget.DockWidgetFeature.DockWidgetFloatable
        )
        widget = QWidget()
        layout = QVBoxLayout()
        self.toggle_btn_rgba = QPushButton()
        self.toggle_btn_rgba.setText("RGBA Atlas")
        self.toggle_btn_rgba.setIcon(QIcon.fromTheme("image-x-generic"))
        self.toggle_btn_rgba.setFixedSize(120, 32)
        layout.addWidget(
            self.toggle_btn_rgba,
            alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft,
        )
        self.toggle_btn_merge = QPushButton()
        self.toggle_btn_merge.setText("Merge Atlas")
        self.toggle_btn_merge.setIcon(QIcon.fromTheme("folder-pictures"))
        self.toggle_btn_merge.setFixedSize(120, 32)
        layout.addWidget(
            self.toggle_btn_merge,
            alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft,
        )
        layout.addStretch()
        widget.setLayout(layout)
        self.setWidget(widget)
        self.setMinimumWidth(140)
        self.setMaximumWidth(180)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Texture RGBA Channel 2x2合成工具")
        self.setGeometry(100, 100, 1000, 500)
        # 左侧Dock：按钮
        self.button_dock = ButtonDock(self)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.button_dock)
        # 右侧Dock：RGBAChannelMere
        self.dock_rgba = RGBAChannelMere(self)
        self.dock_rgba.setAllowedAreas(Qt.DockWidgetArea.AllDockWidgetAreas)
        self.dock_rgba.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetMovable
            | QDockWidget.DockWidgetFeature.DockWidgetFloatable
        )
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.dock_rgba)
        # 右侧Dock：MergeAtlasDock
        self.dock_merge = MergeAtlasDock(self)
        self.dock_merge.setAllowedAreas(Qt.DockWidgetArea.AllDockWidgetAreas)
        self.dock_merge.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetMovable
            | QDockWidget.DockWidgetFeature.DockWidgetFloatable
        )
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.dock_merge)
        self.dock_merge.hide()
        # 按钮控制Dock显示/隐藏
        self.button_dock.toggle_btn_rgba.clicked.connect(self.show_rgba_dock)
        self.button_dock.toggle_btn_merge.clicked.connect(self.show_merge_dock)

    def show_rgba_dock(self):
        self.dock_rgba.show()
        self.dock_merge.hide()

    def show_merge_dock(self):
        self.dock_merge.show()
        self.dock_rgba.hide()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
