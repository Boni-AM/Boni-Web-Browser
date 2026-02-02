import json
import sys
import sqlite3
from typing import Self
import bcrypt
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLineEdit, QToolBar, QAction, QWidget,
    QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QStackedWidget, QTabWidget,
    QMessageBox, QToolButton, QDialog, QTextEdit, QFileDialog, QGraphicsView, QGraphicsScene, QGraphicsRectItem,
    QGraphicsPixmapItem, QGraphicsItem
)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl, Qt, QRectF, QPointF, QSizeF
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QPen, QColor

class ResizableSquareCropItem(QGraphicsRectItem):
    def __init__(self, rect, parent=None):
        super().__init__(rect, parent)
        self.setFlags(
            QGraphicsItem.ItemIsSelectable |
            QGraphicsItem.ItemIsMovable
        )
        self.setBrush(QColor(0, 0, 0, 0))
        self.setPen(QPen(QColor(255, 255, 255), 2))
        self.setZValue(10)
        self.corner_size = 12
        self.resizing = False
        self.resizing_corner = None

    def boundingRect(self):
        return super().boundingRect().adjusted(-self.corner_size, -self.corner_size, self.corner_size, self.corner_size)

    def paint(self, painter, option, widget=None):
        super().paint(painter, option, widget)
        rect = self.rect()
        center = rect.center()
        radius = rect.width() / 2
        circle_rect = QRectF(
            center.x() - radius,
            center.y() - radius,
            radius * 2,
            radius * 2
        )
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(QPen(QColor(255, 255, 255, 100), 1, Qt.DashLine))
        painter.drawEllipse(circle_rect)
        corner_rect = QRectF(
            rect.right() - self.corner_size / 2,
            rect.bottom() - self.corner_size / 2,
            self.corner_size,
            self.corner_size
        )
        painter.setBrush(QColor(255, 255, 255))
        painter.drawRect(corner_rect)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            handle_rect = QRectF(
                self.rect().right() - self.corner_size / 2,
                self.rect().bottom() - self.corner_size / 2,
                self.corner_size,
                self.corner_size
            )
            if handle_rect.contains(event.pos()):
                self.resizing = True
                event.accept()
                return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.resizing:
            new_pos = event.pos()
            delta = new_pos - self.rect().topLeft()
            new_size = max(delta.x(), delta.y(), 40)
            new_rect = QRectF(self.rect().topLeft(), QSizeF(new_size, new_size))
            scene_rect = self.scene().sceneRect()
            if new_rect.right() > scene_rect.right():
                new_size = scene_rect.right() - self.rect().left()
            if new_rect.bottom() > scene_rect.bottom():
                new_size = min(new_size, scene_rect.bottom() - self.rect().top())
            self.setRect(QRectF(self.rect().topLeft(), QSizeF(new_size, new_size)))
            self.update()
        else:
            super().mouseMoveEvent(event)
            scene_rect = self.scene().sceneRect()
            rect = self.rect()
            pos = self.pos()
            if pos.x() < scene_rect.left():
                pos.setX(scene_rect.left())
            if pos.x() + rect.width() > scene_rect.right():
                pos.setX(scene_rect.right() - rect.width())
            if pos.y() < scene_rect.top():
                pos.setY(scene_rect.top())
            if pos.y() + rect.height() > scene_rect.bottom():
                pos.setY(scene_rect.bottom() - rect.height())
            self.setPos(pos)

    def mouseReleaseEvent(self, event):
        self.resizing = False
        super().mouseReleaseEvent(event)
