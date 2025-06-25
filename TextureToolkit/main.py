import sys
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QWidget,
    QVBoxLayout,
    QDockWidget,
    QHBoxLayout,
    QMenu,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from RGBAChannelMere import RGBAChannelMere
from MergeAtalas import MergeAtlasDock
from ColorMatrixDock import ColorMatrixDock
from SingleAtlasDock import SingleAtlasDock


class ButtonDock(QDockWidget):
    def __init__(self, parent=None):
        super().__init__("Atlas 控制", parent)
        self.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea)
        self.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetMovable
            | QDockWidget.DockWidgetFeature.DockWidgetClosable
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
        self.toggle_btn_colormatrix = QPushButton()
        self.toggle_btn_colormatrix.setText("颜色矩阵")
        self.toggle_btn_colormatrix.setIcon(QIcon.fromTheme("color-picker"))
        self.toggle_btn_colormatrix.setFixedSize(120, 32)
        layout.addWidget(
            self.toggle_btn_colormatrix,
            alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft,
        )
        self.toggle_btn_singleatlas = QPushButton()
        self.toggle_btn_singleatlas.setText("Single Atlas")
        self.toggle_btn_singleatlas.setIcon(QIcon.fromTheme("image-x-generic"))
        self.toggle_btn_singleatlas.setFixedSize(120, 32)
        layout.addWidget(
            self.toggle_btn_singleatlas,
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
        self.button_dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea)
        self.button_dock.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetMovable
            | QDockWidget.DockWidgetFeature.DockWidgetClosable
        )
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.button_dock)
        self.button_dock.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.button_dock.customContextMenuRequested.connect(
            lambda pos: self.show_dock_menu(
                self.button_dock, Qt.DockWidgetArea.LeftDockWidgetArea, pos
            )
        )
        # 右侧Dock：RGBAChannelMere
        self.dock_rgba = RGBAChannelMere(self)
        self.dock_rgba.setAllowedAreas(Qt.DockWidgetArea.RightDockWidgetArea)
        self.dock_rgba.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetMovable
            | QDockWidget.DockWidgetFeature.DockWidgetClosable
        )
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.dock_rgba)
        self.dock_rgba.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.dock_rgba.customContextMenuRequested.connect(
            lambda pos: self.show_dock_menu(
                self.dock_rgba, Qt.DockWidgetArea.RightDockWidgetArea, pos
            )
        )
        # 右侧Dock：MergeAtlasDock
        self.dock_merge = MergeAtlasDock(self)
        self.dock_merge.setAllowedAreas(Qt.DockWidgetArea.RightDockWidgetArea)
        self.dock_merge.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetMovable
            | QDockWidget.DockWidgetFeature.DockWidgetClosable
        )
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.dock_merge)
        self.dock_merge.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.dock_merge.customContextMenuRequested.connect(
            lambda pos: self.show_dock_menu(
                self.dock_merge, Qt.DockWidgetArea.RightDockWidgetArea, pos
            )
        )
        # 右侧Dock：ColorMatrixDock
        self.dock_colormatrix = ColorMatrixDock(self)
        self.dock_colormatrix.setAllowedAreas(Qt.DockWidgetArea.RightDockWidgetArea)
        self.dock_colormatrix.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetMovable
            | QDockWidget.DockWidgetFeature.DockWidgetClosable
        )
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.dock_colormatrix)
        # 右侧Dock：SingleAtlasDock
        self.dock_singleatlas = SingleAtlasDock(self)
        self.dock_singleatlas.setAllowedAreas(Qt.DockWidgetArea.RightDockWidgetArea)
        self.dock_singleatlas.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetMovable
            | QDockWidget.DockWidgetFeature.DockWidgetClosable
        )
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.dock_singleatlas)
        # 让Merge和RGBA初始并排
        self.splitDockWidget(self.dock_rgba, self.dock_merge, Qt.Orientation.Horizontal)
        self.dock_merge.hide()
        self.dock_colormatrix.hide()
        self.dock_singleatlas.hide()
        # 按钮控制Dock显示/隐藏
        self.button_dock.toggle_btn_rgba.clicked.connect(self.show_rgba_dock)
        self.button_dock.toggle_btn_merge.clicked.connect(self.show_merge_dock)
        self.button_dock.toggle_btn_colormatrix.clicked.connect(
            self.show_colormatrix_dock
        )
        self.button_dock.toggle_btn_singleatlas.clicked.connect(
            self.show_singleatlas_dock
        )

    def show_dock_menu(self, dock, area, pos):
        menu = QMenu()
        action_restore = menu.addAction("还原到默认位置")
        action = menu.exec(dock.mapToGlobal(pos))
        if action == action_restore:
            if dock is self.button_dock:
                # ButtonDock始终在左侧最上方
                self.removeDockWidget(self.button_dock)
                self.addDockWidget(
                    Qt.DockWidgetArea.LeftDockWidgetArea, self.button_dock
                )
            elif dock in [self.dock_rgba, self.dock_merge]:
                # 右侧Dock还原时，先移除再添加，保持左侧ButtonDock不变
                self.removeDockWidget(dock)
                self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, dock)

    def show_rgba_dock(self):
        self.dock_rgba.show()
        self.dock_merge.hide()
        self.dock_colormatrix.hide()
        self.dock_singleatlas.hide()

    def show_merge_dock(self):
        self.dock_merge.show()
        self.dock_rgba.hide()
        self.dock_colormatrix.hide()
        self.dock_singleatlas.hide()

    def show_colormatrix_dock(self):
        self.dock_colormatrix.show()
        self.dock_rgba.hide()
        self.dock_merge.hide()
        self.dock_singleatlas.hide()

    def show_singleatlas_dock(self):
        self.dock_singleatlas.show()
        self.dock_rgba.hide()
        self.dock_merge.hide()
        self.dock_colormatrix.hide()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
