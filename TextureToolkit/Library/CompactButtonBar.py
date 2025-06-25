from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton
from PyQt6.QtCore import pyqtSignal


class CompactButtonBar(QWidget):
    button_clicked = pyqtSignal(str)

    def __init__(self, buttons, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        self.buttons = {}
        for text in buttons:
            btn = QPushButton(text)
            btn.setFixedHeight(28)
            btn.setSizePolicy(
                btn.sizePolicy().horizontalPolicy(), btn.sizePolicy().verticalPolicy()
            )
            btn.clicked.connect(lambda checked, t=text: self.button_clicked.emit(t))
            layout.addWidget(btn)
            self.buttons[text] = btn
        layout.addStretch()
        self.setLayout(layout)

    def set_enabled(self, text, enabled):
        if text in self.buttons:
            self.buttons[text].setEnabled(enabled)

    def get_button(self, text):
        return self.buttons.get(text)
