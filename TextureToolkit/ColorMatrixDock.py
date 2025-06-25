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
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPixmap, QColor, QPainter
from PIL import Image
from Library.OutputPathSelector import OutputPathSelector


class ColorMatrixGrid(QWidget):
    def __init__(self, rows=3, cols=3, parent=None):
        super().__init__(parent)
        self.rows = rows
        self.cols = cols
        self.spacing = 2
        self.margin = 2
        self.color_matrix = [["#FFFFFF" for _ in range(cols)] for _ in range(rows)]
        self.buttons = []
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.init_buttons()

    def set_matrix_size(self, rows, cols):
        old = self.color_matrix
        new = []
        for r in range(rows):
            row = []
            for c in range(cols):
                if r < len(old) and c < len(old[r]):
                    row.append(old[r][c])
                else:
                    row.append("#FFFFFF")
            new.append(row)
        self.color_matrix = new
        self.rows = rows
        self.cols = cols
        self.init_buttons()
        self.update()

    def set_all_white(self):
        for r in range(self.rows):
            for c in range(self.cols):
                self.color_matrix[r][c] = "#FFFFFF"
        self.update()

    def init_buttons(self):
        for btn in self.buttons:
            btn.setParent(None)
        self.buttons = []
        for r in range(self.rows):
            for c in range(self.cols):
                btn = QPushButton()
                btn.setStyleSheet(
                    f"background:{self.color_matrix[r][c]}; border:1px solid #888;"
                )
                btn.setParent(self)
                btn.clicked.connect(self.make_pick_color(r, c, btn))
                btn.setCursor(Qt.CursorShape.PointingHandCursor)
                btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
                self.buttons.append(btn)
        self.update()

    def make_pick_color(self, r, c, btn):
        def pick_color():
            from PyQt6.QtWidgets import QColorDialog

            color = QColorDialog.getColor(
                QColor(self.color_matrix[r][c]), self, "选择颜色"
            )
            if color.isValid():
                hex_color = color.name()
                self.color_matrix[r][c] = hex_color
                btn.setStyleSheet(f"background:{hex_color}; border:1px solid #888;")
                self.update()

        return pick_color

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.layout_buttons()

    def layout_buttons(self):
        if self.rows == 0 or self.cols == 0:
            return
        w = self.width() - 2 * self.margin
        h = self.height() - 2 * self.margin
        cell_size = min(
            (w - (self.cols - 1) * self.spacing) // self.cols,
            (h - (self.rows - 1) * self.spacing) // self.rows,
        )
        for r in range(self.rows):
            for c in range(self.cols):
                idx = r * self.cols + c
                btn = self.buttons[idx]
                x = self.margin + c * (cell_size + self.spacing)
                y = self.margin + r * (cell_size + self.spacing)
                btn.setGeometry(x, y, cell_size, cell_size)
                btn.setStyleSheet(
                    f"background:{self.color_matrix[r][c]}; border:1px solid #888;"
                )

    def sizeHint(self):
        # 默认正方形
        return QSize(200, 200)

    def get_matrix(self):
        return self.color_matrix


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
        # 顶部按钮区
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(QLabel("行数:"))
        self.spin_rows = QSpinBox()
        self.spin_rows.setRange(1, 12)
        self.spin_rows.setValue(3)
        btn_layout.addWidget(self.spin_rows)
        btn_layout.addWidget(QLabel("列数:"))
        self.spin_cols = QSpinBox()
        self.spin_cols.setRange(1, 12)
        self.spin_cols.setValue(3)
        btn_layout.addWidget(self.spin_cols)
        self.btn_generate = QPushButton("生成矩阵")
        btn_layout.addWidget(self.btn_generate)
        btn_layout.addWidget(QLabel("输出路径:"))
        self.output_selector = OutputPathSelector("colormatrix.png")
        btn_layout.addWidget(self.output_selector)
        self.btn_save = QPushButton("保存图片")
        btn_layout.addWidget(self.btn_save)
        self.btn_clear = QPushButton("清除颜色")
        btn_layout.addWidget(self.btn_clear)
        btn_layout.addStretch()
        main_layout.addLayout(btn_layout)
        # 主体区
        splitter = QSplitter(Qt.Orientation.Horizontal)
        # 左侧：颜色矩阵编辑区
        self.matrix_grid = ColorMatrixGrid(3, 3)
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
        # 信号
        self.btn_generate.clicked.connect(self.on_generate)
        self.btn_save.clicked.connect(self.save_output)
        self.btn_clear.clicked.connect(self.on_clear)
        self.spin_rows.valueChanged.connect(self.on_generate)
        self.spin_cols.valueChanged.connect(self.on_generate)
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

    def update_preview(self):
        color_matrix = self.matrix_grid.get_matrix()
        rows = len(color_matrix)
        cols = len(color_matrix[0]) if rows > 0 else 0
        if rows == 0 or cols == 0:
            self.label_preview.clear()
            return
        cell_size = 200 // max(rows, cols)
        pix = QPixmap(cell_size * cols, cell_size * rows)
        pix.fill(QColor(255, 255, 255))
        painter = QPainter(pix)
        for r in range(rows):
            for c in range(cols):
                color = QColor(color_matrix[r][c])
                painter.fillRect(
                    c * cell_size, r * cell_size, cell_size, cell_size, color
                )
        painter.end()
        self.label_preview.setPixmap(
            pix.scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio)
        )

    def save_output(self):
        try:
            color_matrix = self.matrix_grid.get_matrix()
            rows = len(color_matrix)
            cols = len(color_matrix[0]) if rows > 0 else 0
            cell_size = 40
            output = self.output_selector.get_path()
            if rows == 0 or cols == 0:
                self.label_status.setText("Matrix not generated")
                return
            img = Image.new(
                "RGB", (cols * cell_size, rows * cell_size), color=(255, 255, 255)
            )
            for r in range(rows):
                for c in range(cols):
                    rgb = self.hex_to_rgb(color_matrix[r][c])
                    for y in range(r * cell_size, (r + 1) * cell_size):
                        for x in range(c * cell_size, (c + 1) * cell_size):
                            img.putpixel((x, y), rgb)
            img.save(output)
            self.label_status.setText(f"Saved to {output}")
        except Exception as e:
            self.label_status.setText(f"Error: {e}")

    def hex_to_rgb(self, hex_color):
        hex_color = hex_color.lstrip("#")
        lv = len(hex_color)
        return tuple(int(hex_color[i : i + lv // 3], 16) for i in range(0, lv, lv // 3))
