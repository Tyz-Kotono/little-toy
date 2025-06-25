from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import Qt


class ImagePreviewWidget(QWidget):
    def __init__(self, title=None, size=180, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        if title:
            self.label_title = QLabel(title)
            self.label_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(self.label_title)
        self.label_img = QLabel()
        self.label_img.setFixedSize(size, size)
        self.label_img.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_img.setStyleSheet("border: 1px solid #888; border-radius: 4px;")
        layout.addWidget(self.label_img)
        self.setLayout(layout)

    def set_image(self, img):
        if isinstance(img, QPixmap):
            self.label_img.setPixmap(
                img.scaled(self.label_img.size(), Qt.AspectRatioMode.KeepAspectRatio)
            )
        elif isinstance(img, QImage):
            pix = QPixmap.fromImage(img)
            self.label_img.setPixmap(
                pix.scaled(self.label_img.size(), Qt.AspectRatioMode.KeepAspectRatio)
            )
        else:
            self.label_img.clear()

    def clear(self):
        self.label_img.clear()
