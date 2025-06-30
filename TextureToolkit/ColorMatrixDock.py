from PyQt6.QtWidgets import (
    QDockWidget,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QSpinBox,
    QFrame,
    QSplitter,
    QGridLayout,
    QLabel,
    QSizePolicy,
    QLineEdit,
    QGroupBox,
    QScrollArea,
    QMessageBox,
    QComboBox,
    QSlider,
    QFileDialog,
    QColorDialog,
)
from PyQt6.QtCore import Qt, QSize, QMimeData
from PyQt6.QtGui import QPixmap, QColor, QPainter, QDrag
from PIL import Image, ImageQt
from typing import Optional, List, cast


class MatrixButton(QPushButton):
    def __init__(self, row: int, col: int, grid_ref, parent=None):
        super().__init__(parent)
        self.row = row
        self.col = col
        self.grid_ref = grid_ref
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        color = event.mimeData().text()
        self.setStyleSheet(f"background-color: {color}; border: 2px solid black;")
        self.grid_ref.set_cell_color(self.row, self.col, color)
        event.acceptProposedAction()


class ColorButton(QPushButton):
    def __init__(self, color: str):
        super().__init__()
        self.color = color
        self.setStyleSheet(f"background-color: {color}; border: 1px solid black;")
        self.setFixedSize(40, 40)

    def mousePressEvent(self, event):
        mime_data = QMimeData()
        mime_data.setText(self.color)
        drag = QDrag(self)
        drag.setMimeData(mime_data)
        drag.setHotSpot(event.pos())
        pixmap = QPixmap(self.size())
        self.render(pixmap)
        drag.setPixmap(pixmap)
        drag.exec(Qt.DropAction.MoveAction)


class FillButton(QPushButton):
    def __init__(self, axis: str, idx: int, grid_ref, parent=None):
        super().__init__(parent)
        self.axis = axis  # 'row' or 'col'
        self.idx = idx
        self.grid_ref = grid_ref
        self.setAcceptDrops(True)
        self.setFixedSize(24, 24)
        self.setText("→" if axis == "row" else "↓")
        self.setStyleSheet("border:1px solid #888; background:#eee; font-size:14px;")

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        color = event.mimeData().text()
        self.fill(color)
        event.acceptProposedAction()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            color = QColorDialog.getColor()
            if color.isValid():
                self.fill(color.name())
        else:
            super().mousePressEvent(event)

    def fill(self, color):
        if self.axis == "row":
            for c in range(self.grid_ref.cols):
                self.grid_ref.set_cell_color(self.idx, c, color)
        else:
            for r in range(self.grid_ref.rows):
                self.grid_ref.set_cell_color(r, self.idx, color)


class ColorMatrixGrid(QWidget):
    def __init__(
        self, rows: int = 3, cols: int = 3, parent=None, on_matrix_changed=None
    ):
        super().__init__(parent)
        self.rows = rows
        self.cols = cols
        self.color_matrix: List[List[Optional[str]]] = [
            [None] * cols for _ in range(rows)
        ]
        self.buttons: List[MatrixButton] = []
        self.history: List[ColorButton] = []
        self.marked_cells: List[tuple] = []  # 标记未填充格子
        self.on_matrix_changed = on_matrix_changed
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # 新增：矩阵区带行列批量填充按钮
        self.matrix_area = QWidget()
        self.matrix_layout = QGridLayout(self.matrix_area)
        self.matrix_layout.setSpacing(0)
        self.matrix_layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.matrix_area, stretch=1)

        self.row_fill_buttons = []
        self.col_fill_buttons = []

        # 历史颜色区域（横向+可滚动）
        self.history_widget = QWidget()
        self.history_area = QHBoxLayout(self.history_widget)
        self.history_area.setSpacing(2)
        self.history_area.setContentsMargins(0, 0, 0, 0)

        self.history_scroll = QScrollArea()
        self.history_scroll.setWidgetResizable(True)
        self.history_scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOn
        )
        self.history_scroll.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.history_scroll.setWidget(self.history_widget)
        self.history_scroll.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
        )

        history_group = QGroupBox("颜色历史")
        history_layout = QVBoxLayout(history_group)
        history_layout.setContentsMargins(0, 0, 0, 0)
        history_layout.addWidget(self.history_scroll)
        layout.addWidget(history_group)

        self.create_matrix_buttons(self.rows, self.cols)

    def set_matrix_size(self, rows: int, cols: int):
        self.rows = rows
        self.cols = cols
        self.color_matrix = [[None] * cols for _ in range(rows)]
        self.create_matrix_buttons(rows, cols)
        self.adjust_button_size()
        if self.on_matrix_changed:
            self.on_matrix_changed()

    def set_all_white(self):
        for r in range(self.rows):
            for c in range(self.cols):
                self.color_matrix[r][c] = "#FFFFFF"
        self.update_ui()
        self.adjust_button_size()
        if self.on_matrix_changed:
            self.on_matrix_changed()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.adjust_button_size()

    def adjust_button_size(self):
        area_width = self.matrix_area.width()
        area_height = self.matrix_area.height()
        rows = self.rows
        cols = self.cols
        if cols == 0 or rows == 0:
            return
        button_width = max(10, int(area_width / cols))
        button_height = max(10, int(area_height / rows))
        for button in self.buttons:
            button.setFixedSize(button_width, button_height)
        self.matrix_layout.setSpacing(0)

    def set_cell_color(self, row: int, col: int, color: str):
        self.color_matrix[row][col] = color
        self.add_to_history(QColor(color))
        # 移除标记
        if (row, col) in self.marked_cells:
            self.marked_cells.remove((row, col))
        self.update_ui()
        self.adjust_button_size()
        if self.on_matrix_changed:
            self.on_matrix_changed()

    def on_button_click(self):
        sender = self.sender()
        if sender is None:
            return
        button = cast(MatrixButton, sender)
        if button not in self.buttons:
            return
        index = self.buttons.index(button)
        row, col = divmod(index, self.cols)

        color = QColorDialog.getColor()
        if color.isValid():
            self.add_to_history(color)
            self.set_cell_color(row, col, color.name())

    def add_to_history(self, color: QColor):
        color_name = color.name()
        if color_name not in [cube.color for cube in self.history]:
            color_cube = ColorButton(color_name)
            self.history_area.insertWidget(0, color_cube)
            self.history.append(color_cube)
            if self.on_matrix_changed:
                self.on_matrix_changed()

    def update_ui(self):
        self.marked_cells.clear()
        for row in range(self.rows):
            for col in range(self.cols):
                index = row * self.cols + col
                color = self.color_matrix[row][col]
                if index < len(self.buttons):
                    if color:
                        self.buttons[index].setStyleSheet(
                            f"background-color: {color}; border: 2px solid black;"
                        )
                    else:
                        self.buttons[index].setStyleSheet(
                            "background-color: lightgrey; border: 2px solid red;"
                        )
                        self.marked_cells.append((row, col))
        self.adjust_button_size()

    def create_matrix_buttons(self, rows: int, cols: int):
        for button in self.buttons:
            button.setParent(None)
        self.buttons.clear()
        # 清理批量按钮
        for btn in getattr(self, "row_fill_buttons", []):
            btn.setParent(None)
        for btn in getattr(self, "col_fill_buttons", []):
            btn.setParent(None)
        self.row_fill_buttons = []
        self.col_fill_buttons = []
        layout = self.matrix_layout
        while layout.count():
            item = layout.takeAt(0)
            if item is not None:
                widget = item.widget()
                if widget:
                    widget.setParent(None)
        # 列批量按钮
        for c in range(cols):
            btn = FillButton("col", c, self)
            self.col_fill_buttons.append(btn)
            layout.addWidget(btn, 0, c + 1)
        # 行批量按钮
        for r in range(rows):
            btn = FillButton("row", r, self)
            self.row_fill_buttons.append(btn)
            layout.addWidget(btn, r + 1, 0)
        # 矩阵按钮
        for r in range(rows):
            for c in range(cols):
                button = MatrixButton(r, c, self)
                button.setText(f"{r * cols + c + 1}")
                button.setStyleSheet(
                    "background-color: lightgrey; border: 2px solid black;"
                )
                button.clicked.connect(self.on_button_click)
                self.buttons.append(button)
                layout.addWidget(button, r + 1, c + 1)

    def get_matrix(self) -> List[List[str]]:
        color_matrix = []
        for row in self.color_matrix:
            color_matrix.append(
                [button_color if button_color else "#FFFFFF" for button_color in row]
            )
        return color_matrix

    def on_matrix_button_color_changed(self, row: int, col: int, color: str):
        self.set_cell_color(row, col, color)


class ColorMatrixDock(QDockWidget):
    def __init__(self, parent=None):
        super().__init__("Color Matrix / 颜色矩阵", parent)
        self.setAllowedAreas(Qt.DockWidgetArea.RightDockWidgetArea)
        self.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetMovable
            | QDockWidget.DockWidgetFeature.DockWidgetClosable
        )
        self.init_ui()

    def init_ui(self):
        widget = QWidget()
        main_layout = QVBoxLayout()

        # 顶部控制区
        control_layout = QHBoxLayout()
        control_layout.addWidget(QLabel("行数:"))
        self.spin_rows = QSpinBox()
        self.spin_rows.setRange(1, 12)
        self.spin_rows.setValue(3)
        control_layout.addWidget(self.spin_rows)
        control_layout.addWidget(QLabel("列数:"))
        self.spin_cols = QSpinBox()
        self.spin_cols.setRange(1, 12)
        self.spin_cols.setValue(3)
        control_layout.addWidget(self.spin_cols)
        self.btn_generate = QPushButton("生成矩阵")
        control_layout.addWidget(self.btn_generate)
        self.btn_clear = QPushButton("清除颜色")
        control_layout.addWidget(self.btn_clear)
        # 默认填充色
        control_layout.addWidget(QLabel("默认填充色:"))
        self.default_color = "#FFFFFF"
        self.btn_default_color = QPushButton()
        self.btn_default_color.setFixedSize(32, 32)
        self.btn_default_color.setStyleSheet(
            f"background:{self.default_color}; border:1px solid #888;"
        )
        self.btn_default_color.clicked.connect(self.pick_default_color)
        control_layout.addWidget(self.btn_default_color)
        control_layout.addWidget(QLabel("导出分辨率:"))
        self.combo_resolution = QComboBox()
        self.combo_resolution.addItems(
            ["256x256", "512x512", "1024x1024", "256x512", "512x256", "自定义..."]
        )
        control_layout.addWidget(self.combo_resolution)
        self.spin_custom_w = QSpinBox()
        self.spin_custom_w.setRange(8, 4096)
        self.spin_custom_w.setValue(256)
        self.spin_custom_w.setVisible(False)
        control_layout.addWidget(self.spin_custom_w)
        self.spin_custom_h = QSpinBox()
        self.spin_custom_h.setRange(8, 4096)
        self.spin_custom_h.setValue(256)
        self.spin_custom_h.setVisible(False)
        control_layout.addWidget(self.spin_custom_h)
        control_layout.addStretch()
        main_layout.addLayout(control_layout)

        # 新增：矩阵区宽高控制
        size_layout = QHBoxLayout()
        size_layout.addWidget(QLabel("矩阵宽度:"))
        self.slider_width = QSlider()
        self.slider_width.setOrientation(Qt.Orientation.Horizontal)
        self.slider_width.setRange(100, 800)
        self.slider_width.setValue(300)
        self.spin_width = QSpinBox()
        self.spin_width.setRange(100, 800)
        self.spin_width.setValue(300)
        size_layout.addWidget(self.slider_width)
        size_layout.addWidget(self.spin_width)
        size_layout.addWidget(QLabel("矩阵高度:"))
        self.slider_height = QSlider()
        self.slider_height.setOrientation(Qt.Orientation.Horizontal)
        self.slider_height.setRange(100, 800)
        self.slider_height.setValue(300)
        self.spin_height = QSpinBox()
        self.spin_height.setRange(100, 800)
        self.spin_height.setValue(300)
        size_layout.addWidget(self.slider_height)
        size_layout.addWidget(self.spin_height)
        size_layout.addStretch()
        main_layout.addLayout(size_layout)

        # 输出控制区（移除输出路径控件）
        output_layout = QHBoxLayout()
        self.btn_save = QPushButton("保存图片")
        output_layout.addWidget(self.btn_save)
        output_layout.addStretch()
        main_layout.addLayout(output_layout)

        # 主体区
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # 左侧：颜色矩阵编辑区
        self.matrix_grid = ColorMatrixGrid(3, 3, on_matrix_changed=self.update_preview)
        self.matrix_grid.matrix_area.setFixedSize(300, 300)
        splitter.addWidget(self.matrix_grid)

        # 右侧：图片预览区
        right_frame = QFrame()
        right_layout = QVBoxLayout()
        right_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_preview = QLabel()
        self.label_preview.setFixedSize(200, 200)
        self.label_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_preview.setStyleSheet(
            "border: 1px solid #888; border-radius: 4px; background: #fafafa;"
        )
        right_layout.addWidget(
            self.label_preview, alignment=Qt.AlignmentFlag.AlignCenter
        )
        self.label_status = QLabel("")
        right_layout.addWidget(
            self.label_status, alignment=Qt.AlignmentFlag.AlignCenter
        )
        right_layout.addStretch()
        right_frame.setLayout(right_layout)
        splitter.addWidget(right_frame)
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 1)
        main_layout.addWidget(splitter)

        widget.setLayout(main_layout)
        self.setWidget(widget)

        # 信号连接
        self.btn_generate.clicked.connect(self.on_generate)
        self.btn_save.clicked.connect(self.save_output)
        self.btn_clear.clicked.connect(self.on_clear)
        self.spin_rows.valueChanged.connect(self.on_generate)
        self.spin_cols.valueChanged.connect(self.on_generate)
        self.combo_resolution.currentIndexChanged.connect(self.on_resolution_changed)
        self.spin_custom_w.valueChanged.connect(self.update_preview)
        self.spin_custom_h.valueChanged.connect(self.update_preview)
        self.slider_width.valueChanged.connect(self.spin_width.setValue)
        self.spin_width.valueChanged.connect(self.slider_width.setValue)
        self.slider_height.valueChanged.connect(self.spin_height.setValue)
        self.spin_height.valueChanged.connect(self.slider_height.setValue)
        self.slider_width.valueChanged.connect(self.on_matrix_area_size_changed)
        self.slider_height.valueChanged.connect(self.on_matrix_area_size_changed)
        self.spin_width.valueChanged.connect(self.on_matrix_area_size_changed)
        self.spin_height.valueChanged.connect(self.on_matrix_area_size_changed)
        # 初始化
        self.on_generate()

    def on_generate(self):
        rows = self.spin_rows.value()
        cols = self.spin_cols.value()
        self.matrix_grid.set_matrix_size(rows, cols)
        self.update_preview()

    def on_clear(self):
        self.matrix_grid.set_all_white()
        self.update_preview()

    def on_resolution_changed(self):
        idx = self.combo_resolution.currentIndex()
        is_custom = idx == self.combo_resolution.count() - 1
        self.spin_custom_w.setVisible(is_custom)
        self.spin_custom_h.setVisible(is_custom)
        self.update_preview()

    def get_export_resolution(self):
        idx = self.combo_resolution.currentIndex()
        if idx == 0:
            return 256, 256
        elif idx == 1:
            return 512, 512
        elif idx == 2:
            return 1024, 1024
        elif idx == 3:
            return 256, 512
        elif idx == 4:
            return 512, 256
        else:
            return self.spin_custom_w.value(), self.spin_custom_h.value()

    def update_preview(self):
        color_matrix = self.matrix_grid.get_matrix()
        rows = len(color_matrix)
        cols = len(color_matrix[0]) if rows > 0 else 0
        if rows == 0 or cols == 0:
            self.label_preview.clear()
            return
        export_w, export_h = self.get_export_resolution()
        from PIL import Image, ImageQt

        img = Image.new("RGB", (cols, rows), color=self.hex_to_rgb(self.default_color))
        for r in range(rows):
            for c in range(cols):
                color = color_matrix[r][c]
                rgb = (
                    self.hex_to_rgb(color)
                    if color
                    else self.hex_to_rgb(self.default_color)
                )
                img.putpixel((c, r), rgb)
        img = img.resize((export_w, export_h), resample=Image.Resampling.NEAREST)
        qimg = ImageQt.ImageQt(img)
        pix = QPixmap.fromImage(qimg)
        self.label_preview.setPixmap(
            pix.scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio)
        )

    def save_output(self):
        try:
            color_matrix = self.matrix_grid.get_matrix()
            rows = len(color_matrix)
            cols = len(color_matrix[0]) if rows > 0 else 0
            export_w, export_h = self.get_export_resolution()
            if rows == 0 or cols == 0:
                self.label_status.setText("Matrix not generated")
                return
            file, selected_filter = QFileDialog.getSaveFileName(
                self,
                "保存输出",
                "colormatrix.png",
                "PNG Files (*.png);;JPEG Files (*.jpg *.jpeg);;BMP Files (*.bmp);;All Files (*)",
            )
            if not file:
                return
            if selected_filter.startswith("PNG"):
                fmt = "PNG"
            elif selected_filter.startswith("JPEG"):
                fmt = "JPEG"
            elif selected_filter.startswith("BMP"):
                fmt = "BMP"
            else:
                fmt = None
            from PIL import Image

            img = Image.new(
                "RGB", (cols, rows), color=self.hex_to_rgb(self.default_color)
            )
            for r in range(rows):
                for c in range(cols):
                    color = color_matrix[r][c]
                    rgb = (
                        self.hex_to_rgb(color)
                        if color
                        else self.hex_to_rgb(self.default_color)
                    )
                    img.putpixel((c, r), rgb)
            img = img.resize((export_w, export_h), resample=Image.Resampling.NEAREST)
            img.save(file, format=fmt)
            self.label_status.setText(f"Saved to {file}")
            QMessageBox.information(self, "保存成功", f"已保存到: {file}")
        except Exception as e:
            self.label_status.setText(f"Error: {e}")

    def hex_to_rgb(self, hex_color: str) -> tuple:
        hex_color = hex_color.lstrip("#")
        lv = len(hex_color)
        return tuple(int(hex_color[i : i + lv // 3], 16) for i in range(0, lv, lv // 3))

    def on_matrix_area_size_changed(self):
        w = self.spin_width.value()
        h = self.spin_height.value()
        self.matrix_grid.matrix_area.setFixedSize(w, h)
        self.matrix_grid.adjust_button_size()

    def pick_default_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.default_color = color.name()
            self.btn_default_color.setStyleSheet(
                f"background:{self.default_color}; border:1px solid #888;"
            )
            # 同步填充所有未填充格子
            for row, col in self.matrix_grid.marked_cells[:]:
                self.matrix_grid.set_cell_color(row, col, self.default_color)
            # 无论是否有未填充格子，都刷新预览
            self.update_preview()
