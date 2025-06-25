from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QComboBox


class ResolutionSelector(QWidget):
    def __init__(self, options=None, label_text="Resolution:", parent=None):
        super().__init__(parent)
        layout = QHBoxLayout()
        if label_text:
            layout.addWidget(QLabel(label_text))
        self.combo = QComboBox()
        if options is None:
            options = ["保持原分辨率", "合并分辨率(2x2)", "降采样x2", "降采样x4"]
        self.combo.addItems(options)
        layout.addWidget(self.combo)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

    def get_value(self):
        return self.combo.currentText()

    def set_value(self, value):
        idx = self.combo.findText(value)
        if idx >= 0:
            self.combo.setCurrentIndex(idx)
