from PyQt6.QtWidgets import (
    QDockWidget,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QSpinBox,
    QLineEdit,
    QFrame,
    QColorDialog,
    QSizePolicy,
    QSplitter,
    QGridLayout,
    QFileDialog,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QColor, QPainter
from PIL import Image


class ColorTextureDock(QDockWidget):
    def __init__(self, parent=None):
        super().__init__("Color Texture", parent)
        self.setAllowedAreas(Qt.DockWidgetArea.AllDockWidgetAreas)
        self.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetMovable
            | QDockWidget.DockWidgetFeature.DockWidgetFloatable
        )
        self.init_ui()

    def init_ui(self):
        widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        # 顶部按钮区
        btn_frame = QFrame()
        btn_layout = QHBoxLayout()
        btn_layout.setContentsMargins(8, 8, 8, 4)
        btn_layout.setSpacing(6)
        btn_layout.addWidget(QLabel("Rows:"))
        self.spin_rows = QSpinBox()
        self.spin_rows.setRange(1, 12)
        self.spin_rows.setValue(3)
        btn_layout.addWidget(self.spin_rows)
        btn_layout.addWidget(QLabel("Cols:"))
        self.spin_cols = QSpinBox()
        self.spin_cols.setRange(1, 12)
        self.spin_cols.setValue(3)
        btn_layout.addWidget(self.spin_cols)
        self.btn_generate = QPushButton("Generate Matrix")
        self.btn_generate.setSizePolicy(
            QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed
        )
        btn_layout.addWidget(self.btn_generate)
        btn_layout.addWidget(QLabel("Cell Size:"))
        self.input_cell_size = QLineEdit("40")
        self.input_cell_size.setFixedWidth(60)
        btn_layout.addWidget(self.input_cell_size)
        btn_layout.addWidget(QLabel("Output:"))
        self.input_output = QLineEdit("color_matrix.png")
        self.input_output.setFixedWidth(180)
        btn_layout.addWidget(self.input_output)
        self.btn_save = QPushButton("Save")
        self.btn_save.setSizePolicy(
            QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed
        )
        btn_layout.addWidget(self.btn_save)
        btn_layout.addStretch()
        btn_frame.setLayout(btn_layout)
        # 分割线
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        line.setStyleSheet("color: #bbb; background: #bbb; height: 1px;")
        # 主体区
        splitter = QSplitter(Qt.Orientation.Horizontal)
        # 左侧：颜色矩阵编辑区
        self.matrix_frame = QFrame()
        self.matrix_frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.matrix_layout = QGridLayout()
        self.matrix_layout.setSpacing(4)
        self.matrix_frame.setLayout(self.matrix_layout)
        splitter.addWidget(self.matrix_frame)
        # 右侧：输出预览区
        right_frame = QFrame()
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(8, 8, 8, 8)
        self.label_preview = QLabel()
        self.label_preview.setFixedSize(200, 200)
        self.label_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_preview.setStyleSheet("border: 1px solid #888; border-radius: 4px;")
        right_layout.addWidget(self.label_preview)
        self.label_status = QLabel("")
        right_layout.addWidget(self.label_status)
        right_layout.addStretch()
        right_frame.setLayout(right_layout)
        splitter.addWidget(right_frame)
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 1)
        # 组装主布局
        main_layout.addWidget(btn_frame)
        main_layout.addWidget(line)
        main_layout.addWidget(splitter)
        widget.setLayout(main_layout)
        self.setWidget(widget)
        # 数据
        self.color_matrix = []
        # 信号
        self.btn_generate.clicked.connect(self.generate_matrix)
        self.btn_save.clicked.connect(self.save_output)
        self.spin_rows.valueChanged.connect(self.clear_matrix)
        self.spin_cols.valueChanged.connect(self.clear_matrix)
        # 初始化
        self.generate_matrix()

    def clear_matrix(self):
        for i in reversed(range(self.matrix_layout.count())):
            item = self.matrix_layout.itemAt(i)
            widget = item.widget() if item else None
            if widget:
                widget.setParent(None)
        self.color_matrix = []
        self.update_preview()

    def generate_matrix(self):
        self.clear_matrix()
        rows = self.spin_rows.value()
        cols = self.spin_cols.value()
        self.color_matrix = [["#FFFFFF" for _ in range(cols)] for _ in range(rows)]
        for r in range(rows):
            for c in range(cols):
                btn = QPushButton()
                btn.setStyleSheet(
                    f"background:{self.color_matrix[r][c]}; border:1px solid #888;"
                )
                btn.setFixedSize(32, 32)
                btn.clicked.connect(self.make_pick_color(r, c, btn))
                btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
                self.matrix_layout.addWidget(btn, r, c)
        self.update_preview()

    def make_pick_color(self, r, c, btn):
        def pick_color():
            color = QColorDialog.getColor(
                QColor(self.color_matrix[r][c]), self, "Pick Color"
            )
            if color.isValid():
                hex_color = color.name()
                self.color_matrix[r][c] = hex_color
                btn.setStyleSheet(f"background:{hex_color}; border:1px solid #888;")
                self.update_preview()

        return pick_color

    def update_preview(self):
        try:
            rows = len(self.color_matrix)
            cols = len(self.color_matrix[0]) if rows > 0 else 0
            if rows == 0 or cols == 0:
                self.label_preview.clear()
                return
            cell_size = 200 // max(rows, cols)
            pix = QPixmap(cell_size * cols, cell_size * rows)
            pix.fill(QColor(255, 255, 255))
            painter = QPainter(pix)
            for r in range(rows):
                for c in range(cols):
                    color = QColor(self.color_matrix[r][c])
                    painter.fillRect(
                        c * cell_size, r * cell_size, cell_size, cell_size, color
                    )
            painter.end()
            self.label_preview.setPixmap(
                pix.scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio)
            )
        except Exception:
            self.label_preview.clear()

    def save_output(self):
        try:
            rows = len(self.color_matrix)
            cols = len(self.color_matrix[0]) if rows > 0 else 0
            cell_size = int(self.input_cell_size.text())
            output = self.input_output.text()
            if rows == 0 or cols == 0:
                self.label_status.setText("Matrix not generated")
                return
            img = Image.new(
                "RGB", (cols * cell_size, rows * cell_size), color=(255, 255, 255)
            )
            for r in range(rows):
                for c in range(cols):
                    rgb = self.hex_to_rgb(self.color_matrix[r][c])
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
