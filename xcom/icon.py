"""应用图标：运行时绘制，橙色渐变圆角方块 + 玻璃高光 + 收发双箭头 X 造型。"""

import math

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import (QColor, QIcon, QLinearGradient, QPainter, QPen,
                           QPixmap, QPolygonF)

SIZES = (16, 24, 32, 48, 64, 128, 256)


def _paint(size: int) -> QPixmap:
    pm = QPixmap(size, size)
    pm.fill(Qt.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.Antialiasing)

    # 橙色渐变圆角底（与主题主按钮同色系）
    body = QRectF(size * 0.04, size * 0.04, size * 0.92, size * 0.92)
    radius = size * 0.22
    grad = QLinearGradient(0, 0, 0, size)
    grad.setColorAt(0.0, QColor("#FFB04D"))
    grad.setColorAt(1.0, QColor("#F57C00"))
    p.setPen(Qt.NoPen)
    p.setBrush(grad)
    p.drawRoundedRect(body, radius, radius)

    # 上半玻璃高光
    p.setClipRect(QRectF(0, 0, size, size * 0.50))
    hl = QLinearGradient(0, size * 0.04, 0, size * 0.50)
    hl.setColorAt(0.0, QColor(255, 255, 255, 95))
    hl.setColorAt(1.0, QColor(255, 255, 255, 0))
    p.setBrush(hl)
    p.drawRoundedRect(body, radius, radius)
    p.setClipping(False)

    # X 造型：一条对角线为双向箭头（↗发送 ↙接收），另一条为纯笔画
    ink = QColor("#2A1804")
    m = size * 0.30
    p.setPen(QPen(ink, size * 0.105, Qt.SolidLine, Qt.RoundCap))
    p.drawLine(QPointF(m, m), QPointF(size - m, size - m))  # 纯笔画对角线

    # 箭头对角线：箭杆两端缩进，留出实心三角箭头
    d = 1 / math.sqrt(2)                     # ↗ 方向单位向量 (d, -d)
    head_len, head_w = size * 0.20, size * 0.105
    tip_tx = QPointF(size - m * 0.82, m * 0.82)
    tip_rx = QPointF(m * 0.82, size - m * 0.82)

    def head(tip: QPointF, sign: float) -> QPolygonF:
        bx, by = tip.x() - sign * d * head_len, tip.y() + sign * d * head_len
        px, py = d * head_w, d * head_w      # 垂直方向偏移
        return QPolygonF([tip, QPointF(bx + px, by + py),
                          QPointF(bx - px, by - py)])

    shaft = head_len * 0.85
    p.drawLine(QPointF(tip_rx.x() + d * shaft, tip_rx.y() - d * shaft),
               QPointF(tip_tx.x() - d * shaft, tip_tx.y() + d * shaft))
    p.setPen(Qt.NoPen)
    p.setBrush(ink)
    p.drawPolygon(head(tip_tx, 1.0))
    p.drawPolygon(head(tip_rx, -1.0))

    p.end()
    return pm


def app_icon() -> QIcon:
    icon = QIcon()
    for s in SIZES:
        icon.addPixmap(_paint(s))
    return icon
