import argparse
from PIL import Image
from PyQt6.QtWidgets import (
    QDockWidget,
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QHBoxLayout,
    QLineEdit,
)
from PyQt6.QtCore import Qt


def parse_args():
    parser = argparse.ArgumentParser(description="生成宫格纯色图片")
    parser.add_argument("--rows", type=int, required=True, help="宫格行数")
    parser.add_argument("--cols", type=int, required=True, help="宫格列数")
    parser.add_argument(
        "--colors",
        type=str,
        required=True,
        help='每格颜色列表，用逗号分隔，如 "#FF0000,#00FF00,#0000FF"',
    )
    parser.add_argument(
        "--cell_size", type=int, default=100, help="每格的像素尺寸，正方形"
    )
    parser.add_argument("--output", type=str, default="output.png", help="输出图片路径")
    return parser.parse_args()


def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip("#")
    lv = len(hex_color)
    return tuple(int(hex_color[i : i + lv // 3], 16) for i in range(0, lv, lv // 3))


def main():
    args = parse_args()
    rows, cols = args.rows, args.cols
    colors = args.colors.split(",")
    cell_size = args.cell_size
    output = args.output

    if len(colors) < rows * cols:
        raise ValueError(f"颜色数量不足，需要 {rows * cols} 个颜色")

    img = Image.new("RGB", (cols * cell_size, rows * cell_size), color=(255, 255, 255))
    for r in range(rows):
        for c in range(cols):
            idx = r * cols + c
            color = colors[idx]
            rgb = hex_to_rgb(color)
            for y in range(r * cell_size, (r + 1) * cell_size):
                for x in range(c * cell_size, (c + 1) * cell_size):
                    img.putpixel((x, y), rgb)
    img.save(output)
    print(f"已保存宫格图片到 {output}")


class ColorTextureDock(QDockWidget):
    def __init__(self, parent=None):
        super().__init__("ColorTexture 宫格生成", parent)
        self.setAllowedAreas(Qt.DockWidgetArea.AllDockWidgetAreas)
        self.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetMovable
            | QDockWidget.DockWidgetFeature.DockWidgetFloatable
        )
        widget = QWidget()
        layout = QVBoxLayout()
        # 行数
        row_layout = QHBoxLayout()
        row_layout.addWidget(QLabel("行数:"))
        self.input_rows = QLineEdit("3")
        row_layout.addWidget(self.input_rows)
        layout.addLayout(row_layout)
        # 列数
        col_layout = QHBoxLayout()
        col_layout.addWidget(QLabel("列数:"))
        self.input_cols = QLineEdit("3")
        col_layout.addWidget(self.input_cols)
        layout.addLayout(col_layout)
        # 颜色
        color_layout = QHBoxLayout()
        color_layout.addWidget(QLabel("颜色(逗号分隔):"))
        self.input_colors = QLineEdit(
            "#FF0000,#00FF00,#0000FF,#FFFF00,#00FFFF,#FF00FF,#000000,#FFFFFF,#888888"
        )
        color_layout.addWidget(self.input_colors)
        layout.addLayout(color_layout)
        # 尺寸
        size_layout = QHBoxLayout()
        size_layout.addWidget(QLabel("每格尺寸:"))
        self.input_cell_size = QLineEdit("100")
        size_layout.addWidget(self.input_cell_size)
        layout.addLayout(size_layout)
        # 输出路径
        output_layout = QHBoxLayout()
        output_layout.addWidget(QLabel("输出路径:"))
        self.input_output = QLineEdit("output.png")
        output_layout.addWidget(self.input_output)
        layout.addLayout(output_layout)
        # 生成按钮
        self.btn_generate = QPushButton("生成宫格图片")
        layout.addWidget(self.btn_generate)
        # 状态显示
        self.label_status = QLabel("")
        layout.addWidget(self.label_status)
        layout.addStretch()
        widget.setLayout(layout)
        self.setWidget(widget)
        self.btn_generate.clicked.connect(self.generate_texture)

    def generate_texture(self):
        try:
            rows = int(self.input_rows.text())
            cols = int(self.input_cols.text())
            colors = self.input_colors.text().split(",")
            cell_size = int(self.input_cell_size.text())
            output = self.input_output.text()
            if len(colors) < rows * cols:
                self.label_status.setText(f"颜色数量不足，需要 {rows * cols} 个颜色")
                return
            img = Image.new(
                "RGB", (cols * cell_size, rows * cell_size), color=(255, 255, 255)
            )
            for r in range(rows):
                for c in range(cols):
                    idx = r * cols + c
                    color = colors[idx]
                    rgb = hex_to_rgb(color)
                    for y in range(r * cell_size, (r + 1) * cell_size):
                        for x in range(c * cell_size, (c + 1) * cell_size):
                            img.putpixel((x, y), rgb)
            img.save(output)
            self.label_status.setText(f"已保存宫格图片到 {output}")
        except Exception as e:
            self.label_status.setText(f"错误: {e}")


if __name__ == "__main__":
    main()
