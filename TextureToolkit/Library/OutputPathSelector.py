from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QPushButton, QFileDialog


class OutputPathSelector(QWidget):
    def __init__(self, default_path="output.png", parent=None):
        super().__init__(parent)
        layout = QHBoxLayout()
        self.line_edit = QLineEdit(default_path)
        self.btn_select = QPushButton("...")
        self.btn_select.setFixedWidth(32)
        layout.addWidget(self.line_edit)
        layout.addWidget(self.btn_select)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        self.btn_select.clicked.connect(self.select_path)

    def select_path(self):
        file, _ = QFileDialog.getSaveFileName(
            self,
            "选择输出路径",
            self.line_edit.text(),
            "PNG Files (*.png);;All Files (*)",
        )
        if file:
            self.line_edit.setText(file)

    def get_path(self):
        return self.line_edit.text()

    def set_path(self, path):
        self.line_edit.setText(path)
