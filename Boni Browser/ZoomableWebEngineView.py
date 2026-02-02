import json
import sys
import sqlite3
from typing import Self
import bcrypt
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLineEdit, QToolBar, QAction, QWidget,
    QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QStackedWidget, QTabWidget,
    QMessageBox, QToolButton, QDialog, QTextEdit, QFileDialog
)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtGui import QIcon, QPixmap
import re
from urllib.parse import quote_plus
import validators
from PyQt5.QtWidgets import QWidget, QLabel, QSpacerItem, QSizePolicy, QHBoxLayout
from PyQt5.QtGui import QPixmap, QPainter, QPen, QColor, QImage, QFont
from PyQt5.QtCore import Qt, QUrl, QRectF, QPointF
from PyQt5.QtCore import pyqtSignal
import os
import shutil
from PIL import Image
from PyQt5.QtGui import QPainter, QPainterPath, QPixmap
from PyQt5.QtCore import QSizeF


class ZoomableWebEngineView(QWebEngineView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.zoom_factor = 1.0

    def keyPressEvent(self, event):
        if event.modifiers() == Qt.ControlModifier:
            if event.key() in (Qt.Key_Plus, Qt.Key_Equal):
                self.zoom_in()
                return
            elif event.key() == Qt.Key_Minus:
                self.zoom_out()
                return
        super().keyPressEvent(event)

    def zoom_in(self):
        if self.zoom_factor < 2.0:
            self.zoom_factor += 0.1
            self.setZoomFactor(self.zoom_factor)

    def zoom_out(self):
        if self.zoom_factor > 0.2:
            self.zoom_factor -= 0.1
            self.setZoomFactor(self.zoom_factor)

    def contextMenuEvent(self, event):
        event.ignore()
