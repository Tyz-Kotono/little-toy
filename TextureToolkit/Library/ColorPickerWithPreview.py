from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton, QColorDialog
from PyQt6.QtGui import QColor


class ColorPickerWithPreview(QWidget):
    def __init__(self, label_text="Color:", default_color=(200, 200, 200), parent=None):
        super().__init__(parent)
        layout = QHBoxLayout()
        if label_text:
            layout.addWidget(QLabel(label_text))
        self.color_preview = QPushButton()
        self.color_preview.setFixedSize(24, 24)
        self.color_preview.setStyleSheet(self._preview_style(default_color))
        self.color_preview.clicked.connect(self.pick_color)
        layout.addWidget(self.color_preview)
        self.label_value = QLabel(self.rgb_str(default_color))
        layout.addWidget(self.label_value)
        layout.addStretch()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        self._color = default_color

    def _preview_style(self, color):
        if isinstance(color, tuple):
            color = QColor(*color)
        return f"background: rgb({color.red()}, {color.green()}, {color.blue()}); border: 1px solid #888;"

    def pick_color(self):
        color = QColorDialog.getColor(QColor(*self._color), self, "Pick Color")
        if color.isValid():
            self.set_color((color.red(), color.green(), color.blue()))

    def set_color(self, color):
        self._color = color
        self.color_preview.setStyleSheet(self._preview_style(color))
        self.label_value.setText(self.rgb_str(color))

    def get_color(self):
        return self._color

    @staticmethod
    def rgb_str(color):
        return f"({color[0]}, {color[1]}, {color[2]})"
