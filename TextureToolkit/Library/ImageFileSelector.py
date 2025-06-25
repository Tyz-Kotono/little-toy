from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QPushButton, QFileDialog


class ImageFileSelector(QWidget):
    def __init__(self, label_text=None, default_path="", parent=None):
        super().__init__(parent)
        layout = QHBoxLayout()
        if label_text:
            from PyQt6.QtWidgets import QLabel

            layout.addWidget(QLabel(label_text))
        self.line_edit = QLineEdit(default_path)
        self.btn_select = QPushButton("...")
        self.btn_select.setFixedWidth(32)
        layout.addWidget(self.line_edit)
        layout.addWidget(self.btn_select)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        self.btn_select.clicked.connect(self.select_file)

    def select_file(self):
        file, _ = QFileDialog.getOpenFileName(
            self, "选择图片", self.line_edit.text(), "Images (*.png *.jpg *.bmp *.tga)"
        )
        if file:
            self.line_edit.setText(file)

    def get_path(self):
        return self.line_edit.text()

    def set_path(self, path):
        self.line_edit.setText(path)
