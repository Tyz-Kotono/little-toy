from PyQt6.QtWidgets import (
    QFileDialog,
    QMessageBox,
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
    QListWidget,
    QListWidgetItem,
    QFrame,
    QSplitter,
    QAbstractItemView,
    QStyle,
    QCheckBox,
    QSlider,
    QListView,
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPixmap, QImage, QPainter, QColor, QIcon
from PIL import Image
import os
import io


class AdaptiveListWidget(QListWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.base_icon_size = 64
        self.setViewMode(QListView.ViewMode.IconMode)
        self.setResizeMode(QListView.ResizeMode.Adjust)
        self.setMovement(QListView.Movement.Free)
        self.setSpacing(8)
        self.setIconSize(QSize(self.base_icon_size, self.base_icon_size))
        self.setUniformItemSizes(True)

    def setBaseIconSize(self, size):
        self.base_icon_size = size
        self.updateIconSize()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.updateIconSize()

    def updateIconSize(self):
        # 计算每行能放多少个，自动调整icon size
        viewport = self.viewport()
        if viewport is None:
            return
        w = viewport.width()
        if w < 64:
            icon_size = 32
        else:
            # 让每行尽量多放，icon+label+spacing
            count = max(1, w // (self.base_icon_size + 24))
            icon_size = max(32, min(w // count - 16, 192))
        self.setIconSize(QSize(icon_size, icon_size))


class MergeAtlasDock(QDockWidget):
    def __init__(self, parent=None):
        super().__init__("Merge Atlas", parent)
        self.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea
        )
        self.image_paths = []
        self.folder_path = None
        self.output_img = None
        self.fill_color = (200, 200, 200, 255)
        self.icon_size = 64
        self.show_name = True
        self.init_ui()

    def init_ui(self):
        widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        # 顶部按钮行（紧凑+底部分割线）
        btn_frame = QFrame()
        btn_frame.setFrameShape(QFrame.Shape.NoFrame)
        btn_layout = QHBoxLayout()
        btn_layout.setContentsMargins(8, 8, 8, 4)
        btn_layout.setSpacing(6)
        self.btn_select_folder = QPushButton("选择文件夹")
        self.btn_select_folder.setSizePolicy(
            QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed
        )
        self.btn_select_folder.clicked.connect(self.select_folder)
        btn_layout.addWidget(self.btn_select_folder)
        self.btn_select_images = QPushButton("选择图片")
        self.btn_select_images.setSizePolicy(
            QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed
        )
        self.btn_select_images.clicked.connect(self.select_images)
        btn_layout.addWidget(self.btn_select_images)
        self.btn_merge = QPushButton("合并序列帧贴图")
        self.btn_merge.setSizePolicy(
            QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed
        )
        self.btn_merge.clicked.connect(self.merge_images)
        self.btn_merge.setEnabled(False)
        btn_layout.addWidget(self.btn_merge)
        self.btn_save = QPushButton("保存输出")
        self.btn_save.setSizePolicy(
            QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed
        )
        self.btn_save.clicked.connect(self.save_output)
        self.btn_save.setEnabled(False)
        btn_layout.addWidget(self.btn_save)
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
        self.btn_color = QPushButton("填充色")
        self.btn_color.clicked.connect(self.choose_color)
        btn_layout.addWidget(self.btn_color)
        self.color_preview = QFrame()
        self.color_preview.setFixedSize(24, 24)
        self.color_preview.setStyleSheet(
            f"background: {self.qcolor_str(self.fill_color)}; border: 1px solid #888;"
        )
        btn_layout.addWidget(self.color_preview)
        self.label_color_tip = QLabel(self.rgb_str(self.fill_color))
        btn_layout.addWidget(self.label_color_tip)
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
        btn_frame.setLayout(btn_layout)
        # 分割线
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        line.setStyleSheet("color: #bbb; background: #bbb; height: 1px;")
        # 用QSplitter分隔按钮区和主体区
        top_splitter = QSplitter(Qt.Orientation.Vertical)
        btn_container = QWidget()
        btn_container_layout = QVBoxLayout()
        btn_container_layout.setContentsMargins(0, 0, 0, 0)
        btn_container_layout.setSpacing(0)
        btn_container_layout.addWidget(btn_frame)
        btn_container_layout.addWidget(line)
        btn_container.setLayout(btn_container_layout)
        top_splitter.addWidget(btn_container)
        # 主体区：QSplitter分隔图片列表和预览
        splitter = QSplitter(Qt.Orientation.Horizontal)
        # 左侧：图片列表+上下移动按钮+数量
        left_frame = QFrame()
        left_frame.setFrameShape(QFrame.Shape.StyledPanel)
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(4)
        # 上移/下移按钮和显示name复选框
        move_btn_layout = QHBoxLayout()
        self.btn_up = QPushButton("上移")
        self.btn_up.setFixedHeight(24)
        self.btn_up.clicked.connect(self.move_up)
        move_btn_layout.addWidget(self.btn_up)
        self.btn_down = QPushButton("下移")
        self.btn_down.setFixedHeight(24)
        self.btn_down.clicked.connect(self.move_down)
        move_btn_layout.addWidget(self.btn_down)
        self.chk_show_name = QCheckBox("显示name")
        self.chk_show_name.setChecked(True)
        self.chk_show_name.stateChanged.connect(self.toggle_show_name)
        move_btn_layout.addWidget(self.chk_show_name)
        move_btn_layout.addStretch()
        left_layout.addLayout(move_btn_layout)
        # 缩略图大小滑竿
        slider_layout = QHBoxLayout()
        slider_layout.addWidget(QLabel("缩略图大小"))
        self.slider_icon = QSlider(Qt.Orientation.Horizontal)
        self.slider_icon.setMinimum(32)
        self.slider_icon.setMaximum(192)
        self.slider_icon.setValue(self.icon_size)
        self.slider_icon.setSingleStep(8)
        self.slider_icon.valueChanged.connect(self.change_icon_size)
        slider_layout.addWidget(self.slider_icon)
        left_layout.addLayout(slider_layout)
        self.list_widget = AdaptiveListWidget()
        self.list_widget.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self.list_widget.setBaseIconSize(self.icon_size)
        self.list_widget.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        left_layout.addWidget(self.list_widget)
        # 数组数量显示
        self.label_count = QLabel()
        self.label_count.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_count.setFixedHeight(24)
        left_layout.addWidget(self.label_count)
        # 图片分辨率显示
        self.label_img_res = QLabel()
        self.label_img_res.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_img_res.setFixedHeight(36)
        left_layout.addWidget(self.label_img_res)
        left_frame.setLayout(left_layout)
        splitter.addWidget(left_frame)
        # 右侧：预览区
        right_frame = QFrame()
        right_frame.setFrameShape(QFrame.Shape.StyledPanel)
        preview_layout = QVBoxLayout()
        preview_layout.setContentsMargins(0, 0, 0, 0)
        preview_layout.setSpacing(4)
        self.label_preview = QLabel("输出预览")
        self.label_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_preview.setStyleSheet("border: 1px solid #888; border-radius: 4px;")
        self.label_preview.setPixmap(self.make_checkerboard())
        preview_layout.addWidget(self.label_preview)
        self.label_res = QLabel("")
        self.label_res.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_res.setFixedHeight(36)
        preview_layout.addWidget(self.label_res)
        right_frame.setLayout(preview_layout)
        splitter.addWidget(right_frame)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        top_splitter.addWidget(splitter)
        top_splitter.setStretchFactor(0, 0)
        top_splitter.setStretchFactor(1, 1)
        main_layout.addWidget(top_splitter)
        widget.setLayout(main_layout)
        self.setWidget(widget)

    def qcolor_str(self, color):
        return f"rgb({color[0]}, {color[1]}, {color[2]})"

    def rgb_str(self, color):
        return f"({color[0]}, {color[1]}, {color[2]})"

    def update_color_preview(self):
        self.color_preview.setStyleSheet(
            f"background: {self.qcolor_str(self.fill_color)}; border: 1px solid #888;"
        )
        self.label_color_tip.setText(self.rgb_str(self.fill_color))

    def make_checkerboard(self, w=360, h=360, grid=16):
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

    def refresh_list(self):
        self.list_widget.clear()
        res_set = set()
        res_map = {}
        for path in self.image_paths:
            icon = QIcon(path)
            name = os.path.basename(path) if self.show_name else ""
            # 名字超长自动省略
            if len(name) > 16:
                name = name[:12] + "..." + name[-4:]
            item = QListWidgetItem(icon, name)
            self.list_widget.addItem(item)
            try:
                img = Image.open(path)
                res = f"{img.width}x{img.height}"
                res_set.add(res)
                res_map.setdefault(res, []).append(name)
            except Exception:
                pass
        self.label_count.setText(f"图片数量: {len(self.image_paths)}")
        self.list_widget.setBaseIconSize(self.icon_size)
        # 分辨率显示
        if len(res_set) == 1:
            self.label_img_res.setText(f"图片分辨率: {list(res_set)[0]}")
        elif len(res_set) > 1:
            diff = []
            for r, names in res_map.items():
                diff.append(f"<span style='color:red'>{r}: {', '.join(names)}</span>")
            self.label_img_res.setText("分辨率不一致:<br>" + "<br>".join(diff))
        else:
            self.label_img_res.setText("")

    def toggle_show_name(self, state):
        self.show_name = state == Qt.CheckState.Checked
        self.refresh_list()
        self.preview_refresh()

    def change_icon_size(self, value):
        self.icon_size = value
        self.list_widget.setBaseIconSize(self.icon_size)
        self.preview_refresh()

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "选择图片文件夹", "")
        if folder:
            self.folder_path = folder
            self.image_paths = [
                os.path.join(folder, f)
                for f in os.listdir(folder)
                if f.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".tga"))
            ]
            self.refresh_list()
            self.btn_merge.setEnabled(bool(self.image_paths))
            self.btn_save.setEnabled(False)
            self.label_preview.setPixmap(self.make_checkerboard())
            self.label_res.clear()
            self.output_img = None
            self.preview_refresh()

    def select_images(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "选择图片", "", "Images (*.png *.jpg *.bmp *.tga)"
        )
        if files:
            self.image_paths = files
            self.folder_path = None
            self.refresh_list()
            self.btn_merge.setEnabled(bool(self.image_paths))
            self.btn_save.setEnabled(False)
            self.label_preview.setPixmap(self.make_checkerboard())
            self.label_res.clear()
            self.output_img = None
            self.preview_refresh()

    def choose_color(self):
        color = QColorDialog.getColor(QColor(*self.fill_color), self, "选择填充色")
        if color.isValid():
            self.fill_color = (color.red(), color.green(), color.blue(), 255)
            self.update_color_preview()

    def move_up(self):
        row = self.list_widget.currentRow()
        if row > 0:
            self.image_paths[row - 1], self.image_paths[row] = (
                self.image_paths[row],
                self.image_paths[row - 1],
            )
            self.refresh_list()
            self.list_widget.setCurrentRow(row - 1)
            self.preview_refresh()

    def move_down(self):
        row = self.list_widget.currentRow()
        if 0 <= row < len(self.image_paths) - 1:
            self.image_paths[row + 1], self.image_paths[row] = (
                self.image_paths[row],
                self.image_paths[row + 1],
            )
            self.refresh_list()
            self.list_widget.setCurrentRow(row + 1)
            self.preview_refresh()

    def preview_refresh(self):
        # 只刷新预览，不保存
        self.merge_images(preview_only=True)

    def merge_images(self, preview_only=False):
        if not self.image_paths:
            return
        # 拖拽排序后同步image_paths
        self.sync_image_paths_from_list()
        rows = self.spin_rows.value()
        cols = self.spin_cols.value()
        total = rows * cols
        imgs = []
        img_sizes = []
        for path in self.image_paths[:total]:
            img = Image.open(path).convert("RGBA")
            imgs.append(img)
            img_sizes.append(img.size)
        # 统一尺寸为第一张图片的尺寸
        if imgs:
            w, h = imgs[0].size
        else:
            w, h = 128, 128
        # 填充不足
        while len(imgs) < total:
            fill = Image.new("RGBA", (w, h), self.fill_color)
            imgs.append(fill)
            img_sizes.append((w, h))
        # 合成
        mode = (
            self.combo_res.currentText()
            if hasattr(self, "combo_res")
            else "合并分辨率(拼接)"
        )
        if mode == "保持原分辨率":
            out_w, out_h = w, h
        elif mode == "合并分辨率(拼接)":
            out_w, out_h = w * cols, h * rows
        elif mode == "降采样x2":
            out_w, out_h = max(1, w * cols // 2), max(1, h * rows // 2)
        elif mode == "降采样x4":
            out_w, out_h = max(1, w * cols // 4), max(1, h * rows // 4)
        elif mode == "单张分辨率":
            out_w, out_h = w, h
        elif mode == "合并分辨率x2":
            out_w, out_h = w * cols * 2, h * rows * 2
        else:
            out_w, out_h = w * cols, h * rows
        atlas = Image.new("RGBA", (w * cols, h * rows), (0, 0, 0, 0))
        for idx, img in enumerate(imgs):
            r = idx // cols
            c = idx % cols
            atlas.paste(img, (c * w, r * h))
        # 输出分辨率调整
        if (out_w, out_h) != atlas.size:
            atlas = atlas.resize((out_w, out_h), Image.Resampling.LANCZOS)
        if not preview_only:
            self.output_img = atlas
        # 预览
        buf = io.BytesIO()
        atlas.thumbnail((360, 360), Image.Resampling.LANCZOS)
        atlas.save(buf, format="PNG")
        qt_img = QImage.fromData(buf.getvalue())
        preview = self.make_checkerboard()
        pixmap = QPixmap.fromImage(qt_img)
        painter = QPainter(preview)
        x = (preview.width() - pixmap.width()) // 2
        y = (preview.height() - pixmap.height()) // 2
        painter.drawPixmap(x, y, pixmap)
        painter.end()
        self.label_preview.setPixmap(preview)
        self.label_res.setText(f"输出分辨率: {out_w}x{out_h}")
        if not preview_only:
            self.btn_save.setEnabled(True)

    def sync_image_paths_from_list(self):
        # 拖拽排序后同步image_paths
        new_paths = []
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if item is None:
                continue
            name = item.text()
            for path in self.image_paths:
                if os.path.basename(path) == name or not self.show_name:
                    new_paths.append(path)
                    break
        self.image_paths = new_paths

    def save_output(self):
        if self.output_img is None:
            QMessageBox.warning(self, "未生成图片", "请先合并后再保存！")
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
            QMessageBox.information(self, "保存成功", f"已保存到: {file}")
