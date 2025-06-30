import sys
from PyQt6.QtWidgets import QWidget, QApplication, QColorDialog, QVBoxLayout, QLabel
from PyQt6.QtGui import QPainter, QColor, QLinearGradient, QMouseEvent, QPen, QImage
from PyQt6.QtCore import Qt, QRectF


class GradientStop:
    def __init__(self, pos: float, color: QColor):
        self.pos = pos  # 0~1
        self.color = color


class GradientPicker(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(60)
        self.setMinimumWidth(320)
        self.setMouseTracking(True)
        self.stops = [
            GradientStop(0.0, QColor("#FF0000")),
            GradientStop(1.0, QColor("#0000FF")),
        ]
        self.selected_idx = None
        self.dragging = False
        self.preview_label = QLabel()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.addStretch()
        layout.addWidget(self.preview_label)
        self.update_preview()

    def paintEvent(self, event):
        painter = QPainter(self)
        rect = self.rect().adjusted(20, 20, -20, -30)
        # 绘制渐变条
        grad = QLinearGradient(rect.left(), rect.top(), rect.right(), rect.top())
        for stop in self.stops:
            grad.setColorAt(stop.pos, stop.color)
        painter.setBrush(grad)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(rect)
        # 绘制节点
        for i, stop in enumerate(self.stops):
            x = rect.left() + stop.pos * rect.width()
            y = rect.bottom() + 8
            r = 8
            painter.setPen(QPen(Qt.GlobalColor.black, 2))
            painter.setBrush(stop.color)
            painter.drawEllipse(QRectF(x - r, y - r, 2 * r, 2 * r))
            if i == self.selected_idx:
                painter.setPen(QPen(Qt.GlobalColor.yellow, 2))
                painter.drawEllipse(QRectF(x - r - 2, y - r - 2, 2 * r + 4, 2 * r + 4))

    def mousePressEvent(self, event: QMouseEvent):
        rect = self.rect().adjusted(20, 20, -20, -30)
        # 检查是否点击节点
        for i, stop in enumerate(self.stops):
            x = rect.left() + stop.pos * rect.width()
            y = rect.bottom() + 8
            if (event.position().x() - x) ** 2 + (
                event.position().y() - y
            ) ** 2 < 10**2:
                self.selected_idx = i
                self.dragging = True
                self.update()
                return
        # 双击渐变条添加节点
        if event.button() == Qt.MouseButton.LeftButton and rect.contains(
            event.position().toPoint()
        ):
            pos = (event.position().x() - rect.left()) / rect.width()
            color = QColorDialog.getColor(QColor("#FFFFFF"), self, "选择颜色")
            if color.isValid():
                self.stops.append(GradientStop(pos, color))
                self.stops.sort(key=lambda s: s.pos)
                self.selected_idx = self.stops.index(
                    next(s for s in self.stops if s.pos == pos and s.color == color)
                )
                self.update()
                self.update_preview()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.dragging and self.selected_idx is not None:
            rect = self.rect().adjusted(20, 20, -20, -30)
            pos = (event.position().x() - rect.left()) / rect.width()
            pos = max(0.0, min(1.0, pos))
            self.stops[self.selected_idx].pos = pos
            self.stops.sort(key=lambda s: s.pos)
            self.selected_idx = self.stops.index(
                min(self.stops, key=lambda s: abs(s.pos - pos))
            )
            self.update()
            self.update_preview()

    def mouseReleaseEvent(self, event: QMouseEvent):
        self.dragging = False

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        # 右键双击节点删除
        rect = self.rect().adjusted(20, 20, -20, -30)
        for i, stop in enumerate(self.stops):
            x = rect.left() + stop.pos * rect.width()
            y = rect.bottom() + 8
            if (event.position().x() - x) ** 2 + (
                event.position().y() - y
            ) ** 2 < 10**2:
                if len(self.stops) > 2:
                    self.stops.pop(i)
                    self.selected_idx = None
                    self.update()
                    self.update_preview()
                return

    def update_preview(self):
        # 生成渐变带预览图片
        w, h = 256, 24
        img = QImage(w, h, QImage.Format.Format_RGB32)
        for x in range(w):
            t = x / (w - 1)
            color = self.get_color_at(t)
            img.setPixelColor(x, h // 2, color)
            for y in range(h):
                img.setPixelColor(x, y, color)
        pix = QPixmap.fromImage(img)
        self.preview_label.setPixmap(pix)

    def get_color_at(self, t: float) -> QColor:
        stops = sorted(self.stops, key=lambda s: s.pos)
        for i in range(1, len(stops)):
            if t <= stops[i].pos:
                t0, t1 = stops[i - 1].pos, stops[i].pos
                c0, c1 = stops[i - 1].color, stops[i].color
                if t1 == t0:
                    return c1
                ratio = (t - t0) / (t1 - t0)
                r = int(c0.red() + (c1.red() - c0.red()) * ratio)
                g = int(c0.green() + (c1.green() - c0.green()) * ratio)
                b = int(c0.blue() + (c1.blue() - c0.blue()) * ratio)
                return QColor(r, g, b)
        return stops[-1].color


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = GradientPicker()
    win.setWindowTitle("Unity风格颜色渐变拾取器")
    win.resize(400, 120)
    win.show()
    sys.exit(app.exec())
