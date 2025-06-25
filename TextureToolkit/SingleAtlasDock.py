from PyQt6.QtWidgets import (
    QDockWidget,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QComboBox,
    QColorDialog,
    QSizePolicy,
    QSpinBox,
    QFrame,
    QFileDialog,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QImage, QPainter, QColor
from PIL import Image
import io


class SingleAtlasDock(QDockWidget):
    def __init__(self, parent=None):
        super().__init__("Single Atlas", parent)
        self.setAllowedAreas(Qt.DockWidgetArea.RightDockWidgetArea)
        self.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetMovable
            | QDockWidget.DockWidgetFeature.DockWidgetClosable
        )
        self.input_path = None
        self.input_img = None
        self.output_img = None
        self.fill_color = (200, 200, 200, 255)
        self.init_ui()

    def init_ui(self):
        widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        # 顶部按钮行
        btn_layout = QHBoxLayout()
        self.btn_select = QPushButton("选择图片")
        self.btn_select.setSizePolicy(
            QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed
        )
        self.btn_select.clicked.connect(self.select_image)
        btn_layout.addWidget(self.btn_select)
        self.btn_process = QPushButton("合成序列帧贴图")
        self.btn_process.setSizePolicy(
            QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed
        )
        self.btn_process.clicked.connect(self.process_image)
        self.btn_process.setEnabled(False)
        btn_layout.addWidget(self.btn_process)
        self.btn_save = QPushButton("保存输出")
        self.btn_save.setSizePolicy(
            QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed
        )
        self.btn_save.clicked.connect(self.save_output)
        self.btn_save.setEnabled(False)
        btn_layout.addWidget(self.btn_save)
        # 新增模式选择
        btn_layout.addWidget(QLabel("模式:"))
        self.combo_mode = QComboBox()
        self.combo_mode.addItems(["全部重复单张", "单张加颜色"])
        btn_layout.addWidget(self.combo_mode)
        btn_layout.addWidget(QLabel("行数:"))
        self.spin_rows = QSpinBox()
        self.spin_rows.setRange(1, 12)
        self.spin_rows.setValue(2)
        btn_layout.addWidget(self.spin_rows)
        btn_layout.addWidget(QLabel("列数:"))
        self.spin_cols = QSpinBox()
        self.spin_cols.setRange(1, 12)
        self.spin_cols.setValue(2)
        btn_layout.addWidget(self.spin_cols)
        self.color_preview = QFrame()
        self.color_preview.setFixedSize(24, 24)
        self.color_preview.setStyleSheet(
            f"background: rgb({self.fill_color[0]}, {self.fill_color[1]}, {self.fill_color[2]}); border: 1px solid #888;"
        )
        self.color_preview.setCursor(Qt.CursorShape.PointingHandCursor)
        self.color_preview.mousePressEvent = self.pick_fill_color
        btn_layout.addWidget(self.color_preview)
        btn_layout.addWidget(QLabel("输出分辨率:"))
        self.combo_res = QComboBox()
        self.combo_res.addItems(
            [
                "保持原分辨率",
                "合并分辨率(拼接)",
                "降采样x2",
                "降采样x4",
                "单张分辨率",
                "合并分辨率x2",
            ]
        )
        self.combo_res.setSizePolicy(
            QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed
        )
        self.combo_res.currentIndexChanged.connect(self.preview_refresh)
        btn_layout.addWidget(self.combo_res)
        btn_layout.addStretch()
        main_layout.addLayout(btn_layout)
        # 预览区
        preview_layout = QHBoxLayout()
        # 输入预览
        input_layout = QVBoxLayout()
        self.label_input = QLabel("输入预览")
        self.label_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_input.setStyleSheet("border: 1px solid #888; border-radius: 4px;")
        self.label_input.setPixmap(self.make_checkerboard())
        input_layout.addWidget(self.label_input)
        self.label_input_res = QLabel("")
        self.label_input_res.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_input_res.setFixedHeight(36)
        input_layout.addWidget(self.label_input_res)
        preview_layout.addLayout(input_layout)
        # 输出预览
        output_layout = QVBoxLayout()
        self.label_output = QLabel("输出预览")
        self.label_output.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_output.setStyleSheet("border: 1px solid #888; border-radius: 4px;")
        self.label_output.setPixmap(self.make_checkerboard())
        output_layout.addWidget(self.label_output)
        self.label_output_res = QLabel("")
        self.label_output_res.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_output_res.setFixedHeight(36)
        output_layout.addWidget(self.label_output_res)
        preview_layout.addLayout(output_layout)
        main_layout.addLayout(preview_layout)
        widget.setLayout(main_layout)
        self.setWidget(widget)

    def make_checkerboard(self, w=180, h=180, grid=12):
        pix = QPixmap(w, h)
        pix.fill(QColor(220, 220, 220))
        painter = QPainter(pix)
        color1 = QColor(200, 200, 200)
        color2 = QColor(255, 255, 255)
        for y in range(0, h, grid):
            for x in range(0, w, grid):
                if (x // grid + y // grid) % 2 == 0:
                    painter.fillRect(x, y, grid, grid, color1)
                else:
                    painter.fillRect(x, y, grid, grid, color2)
        painter.end()
        return pix

    def select_image(self):
        file, _ = QFileDialog.getOpenFileName(
            self, "选择图片", "", "Images (*.png *.jpg *.bmp *.tga)"
        )
        if file:
            self.input_path = file
            self.input_img = Image.open(file).convert("RGBA")
            # 合成棋盘格和图片
            preview = self.make_checkerboard()
            pixmap = QPixmap(file).scaled(180, 180, Qt.AspectRatioMode.KeepAspectRatio)
            painter = QPainter(preview)
            x = (preview.width() - pixmap.width()) // 2
            y = (preview.height() - pixmap.height()) // 2
            painter.drawPixmap(x, y, pixmap)
            painter.end()
            self.label_input.setPixmap(preview)
            w, h = self.input_img.size
            self.label_input_res.setText(f"输入分辨率: {w}x{h}")
            self.btn_process.setEnabled(True)
            self.btn_save.setEnabled(False)
            # 输出区重置
            self.label_output.setPixmap(self.make_checkerboard())
            self.label_output_res.clear()
            self.output_img = None

    def process_image(self):
        if not self.input_img:
            return
        img = self.input_img
        w, h = img.size
        rows = self.spin_rows.value()
        cols = self.spin_cols.value()
        mode = self.combo_res.currentText()
        # 新增：合成模式
        fill_mode = self.combo_mode.currentText()
        # 生成序列帧合成贴图
        new_img = Image.new("RGBA", (w * cols, h * rows), self.fill_color)
        if fill_mode == "全部重复单张":
            for r in range(rows):
                for c in range(cols):
                    new_img.paste(img, (c * w, r * h))
        else:  # 单张加颜色
            new_img.paste(img, (0, 0))
        # 根据分辨率策略调整输出
        if mode == "保持原分辨率":
            out_img = new_img.resize((w, h), Image.Resampling.LANCZOS)
        elif mode == "合并分辨率(拼接)":
            out_img = new_img
        elif mode == "降采样x2":
            out_img = new_img.resize((w, h), Image.Resampling.LANCZOS)
        elif mode == "降采样x4":
            out_img = new_img.resize((w // 2, h // 2), Image.Resampling.LANCZOS)
        elif mode == "单张分辨率":
            out_img = img
        elif mode == "合并分辨率x2":
            out_img = new_img.resize(
                (w * cols // 2, h * rows // 2), Image.Resampling.LANCZOS
            )
        else:
            out_img = new_img
        self.output_img = out_img
        # 显示输出预览（叠加棋盘格）
        buf = io.BytesIO()
        out_img.save(buf, format="PNG")
        qt_img = QImage.fromData(buf.getvalue())
        preview = self.make_checkerboard()
        pixmap = QPixmap.fromImage(qt_img).scaled(
            180, 180, Qt.AspectRatioMode.KeepAspectRatio
        )
        painter = QPainter(preview)
        x = (preview.width() - pixmap.width()) // 2
        y = (preview.height() - pixmap.height()) // 2
        painter.drawPixmap(x, y, pixmap)
        painter.end()
        self.label_output.setPixmap(preview)
        ow, oh = out_img.size
        self.label_output_res.setText(f"输出分辨率: {ow}x{oh}")
        self.btn_save.setEnabled(True)

    def pick_fill_color(self, event):
        color = QColorDialog.getColor(QColor(*self.fill_color[:3]), self, "选择填充色")
        if color.isValid():
            self.fill_color = (color.red(), color.green(), color.blue(), 255)
            self.color_preview.setStyleSheet(
                f"background: rgb({self.fill_color[0]}, {self.fill_color[1]}, {self.fill_color[2]}); border: 1px solid #888;"
            )
            self.preview_refresh()

    def preview_refresh(self):
        if self.output_img is not None:
            self.process_image()

    def save_output(self):
        if self.output_img is None:
            return
        file, selected_filter = QFileDialog.getSaveFileName(
            self,
            "保存输出",
            "output.png",
            "PNG Files (*.png);;JPEG Files (*.jpg *.jpeg);;BMP Files (*.bmp);;All Files (*)",
        )
        if file:
            if selected_filter.startswith("PNG"):
                fmt = "PNG"
            elif selected_filter.startswith("JPEG"):
                fmt = "JPEG"
            elif selected_filter.startswith("BMP"):
                fmt = "BMP"
            else:
                fmt = None
            self.output_img.save(file, format=fmt)
