import sys
import json
from PyQt6.QtCore import Qt, QMimeData
from PyQt6.QtGui import QColor, QPixmap, QDrag
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QGridLayout,
    QPushButton,
    QColorDialog,
    QVBoxLayout,
    QHBoxLayout,
    QMessageBox,
    QLineEdit,
    QLabel,
    QGroupBox,
    QScrollArea,
)


class MatrixButton(QPushButton):
    def __init__(self, row, col, parent=None):
        super().__init__(parent)
        self.row = row
        self.col = col
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        color = event.mimeData().text()
        self.setStyleSheet(f"background-color: {color}; border: 2px solid black;")
        if self.parent() and hasattr(self.parent(), "on_matrix_button_color_changed"):
            self.parent().on_matrix_button_color_changed(self.row, self.col, color)
        event.acceptProposedAction()


class ColorButton(QPushButton):
    def __init__(self, color):
        super().__init__()
        self.color = color
        self.setStyleSheet(f"background-color: {color}; border: 2px solid black;")
        self.setFixedSize(36, 36)

    def mousePressEvent(self, event):
        mime_data = QMimeData()
        mime_data.setText(self.color)
        drag = QDrag(self)
        drag.setMimeData(mime_data)
        drag.setHotSpot(event.pos())
        pixmap = QPixmap(self.size())
        self.render(pixmap)
        drag.setPixmap(pixmap)
        drag.exec(Qt.DropAction.MoveAction)

    def dropEvent(self, event):
        pass


class PuzzleGame(QMainWindow):
    def __init__(self, rows=3, cols=4):
        super().__init__()
        self.matrix_rows = rows
        self.matrix_cols = cols
        self.matrix = [[None] * cols for _ in range(rows)]
        self.buttons = []
        self.history = []
        self.init_ui()

    def init_ui(self):
        main_widget = QWidget(self)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(8)

        # 行列输入区
        input_layout = QHBoxLayout()
        input_layout.setSpacing(5)
        self.row_input = QLineEdit(str(self.matrix_rows))
        self.row_input.setFixedWidth(40)
        self.row_input.setPlaceholderText("行")
        self.col_input = QLineEdit(str(self.matrix_cols))
        self.col_input.setFixedWidth(40)
        self.col_input.setPlaceholderText("列")
        set_btn = QPushButton("设置矩阵大小")
        set_btn.clicked.connect(self.set_matrix_size_from_input)
        input_layout.addWidget(QLabel("行:"))
        input_layout.addWidget(self.row_input)
        input_layout.addWidget(QLabel("列:"))
        input_layout.addWidget(self.col_input)
        input_layout.addWidget(set_btn)
        input_layout.addStretch()
        main_layout.addLayout(input_layout)

        # 矩阵区域
        self.matrix_area = QWidget()
        self.matrix_layout = QGridLayout(self.matrix_area)
        self.matrix_layout.setSpacing(0)
        self.matrix_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.matrix_area, stretch=1)

        # 历史颜色区域（横向+可滚动）
        self.history_widget = QWidget()
        self.history_area = QHBoxLayout(self.history_widget)
        self.history_area.setSpacing(6)
        self.history_area.setContentsMargins(8, 4, 8, 4)

        self.history_scroll = QScrollArea()
        self.history_scroll.setWidgetResizable(True)
        self.history_scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOn
        )
        self.history_scroll.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.history_scroll.setWidget(self.history_widget)

        history_group = QGroupBox("颜色历史")
        history_layout = QVBoxLayout(history_group)
        history_layout.setContentsMargins(0, 0, 0, 0)
        history_layout.addWidget(self.history_scroll)
        main_layout.addWidget(history_group)

        self.setWindowTitle("Color matrix")
        self.setGeometry(100, 100, 800, 500)
        self.setMinimumSize(400, 300)

        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        self.create_matrix_buttons(self.matrix_rows, self.matrix_cols)

    def set_matrix_size_from_input(self):
        row_text = self.row_input.text()
        col_text = self.col_input.text()
        try:
            rows = int(row_text)
            cols = int(col_text)
            if rows > 0 and cols > 0:
                self.refresh_matrix(rows, cols)
            else:
                QMessageBox.warning(self, "错误", "请输入大于0的整数。")
        except Exception:
            QMessageBox.warning(self, "错误", "请输入有效的整数。")

    def resizeEvent(self, event):
        self.adjust_button_size()

    def adjust_button_size(self):
        area_width = self.matrix_area.width()
        area_height = self.matrix_area.height()
        rows = self.matrix_rows
        cols = self.matrix_cols
        if cols == 0 or rows == 0:
            return
        button_width = int(area_width / cols)
        button_height = int(area_height / rows)
        for button in self.buttons:
            button.setFixedSize(button_width, button_height)

    def on_button_click(self):
        sender = self.sender()
        index = self.buttons.index(sender)
        row, col = divmod(index, self.matrix_cols)
        color = QColorDialog.getColor()
        if color.isValid():
            self.matrix[row][col] = color.name()
            sender.setStyleSheet(
                f"background-color: {color.name()}; border: 2px solid black;"
            )
            self.add_to_history(color)

    def add_to_history(self, color):
        color_name = color.name()
        if color_name not in [cube.color for cube in self.history]:
            color_cube = ColorButton(color_name)
            self.history_area.insertWidget(0, color_cube)
            self.history.append(color_cube)

    def save_to_json(self):
        data = {
            "rows": self.matrix_rows,
            "cols": self.matrix_cols,
            "matrix": self.matrix,
        }
        with open("matrix.json", "w") as f:
            json.dump(data, f)

    def load_from_json(self):
        try:
            with open("matrix.json", "r") as f:
                data = json.load(f)
                rows = data.get("rows", 3)
                cols = data.get("cols", 3)
                self.matrix = data["matrix"]
                self.refresh_matrix(rows, cols)
        except FileNotFoundError:
            QMessageBox.warning(self, "Error", "没有找到保存的文件.")

    def update_ui(self):
        for row in range(self.matrix_rows):
            for col in range(self.matrix_cols):
                index = row * self.matrix_cols + col
                color = self.matrix[row][col]
                if index < len(self.buttons):
                    if color:
                        self.buttons[index].setStyleSheet(
                            f"background-color: {color}; border: 2px solid black;"
                        )
                    else:
                        self.buttons[index].setStyleSheet(
                            "background-color: lightgrey; border: 2px solid black;"
                        )

    def refresh_matrix(self, rows, cols):
        self.matrix_rows = rows
        self.matrix_cols = cols
        self.matrix = [[None] * cols for _ in range(rows)]
        self.create_matrix_buttons(rows, cols)
        self.adjust_button_size()
        self.update_ui()
        self.row_input.setText(str(rows))
        self.col_input.setText(str(cols))

    def create_matrix_buttons(self, rows, cols):
        for button in self.buttons:
            button.setParent(None)
        self.buttons.clear()
        layout = self.matrix_layout
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)
        for row in range(rows):
            for col in range(cols):
                button = MatrixButton(row, col, self.matrix_area)
                button.setText(f"{row * cols + col + 1}")
                button.setStyleSheet(
                    "background-color: lightgrey; border: 2px solid black;"
                )
                button.clicked.connect(self.on_button_click)
                self.buttons.append(button)
                layout.addWidget(button, row, col)

    def get_color_matrix(self):
        color_matrix = []
        for row in self.matrix:
            color_matrix.append(
                [button_color if button_color else "#FFFFFF" for button_color in row]
            )
        return color_matrix

    def on_matrix_button_color_changed(self, row, col, color):
        self.matrix[row][col] = color


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PuzzleGame(3, 4)
    window.show()
    sys.exit(app.exec())
