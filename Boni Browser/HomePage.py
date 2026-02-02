import json
import sys
import sqlite3
from typing import Self
import bcrypt
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLineEdit, QToolBar, QAction, QWidget,
    QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QStackedWidget, QTabWidget,
    QMessageBox, QToolButton, QDialog, QTextEdit, QDialog, QFileDialog
)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtGui import QIcon, QPixmap
import re
from urllib.parse import quote_plus
import validators
from PyQt5.QtWidgets import QWidget, QLabel, QSpacerItem, QSizePolicy, QHBoxLayout
from PyQt5.QtGui import QPixmap, QPainter, QPen, QColor, QImage, QFont
from PyQt5.QtCore import Qt, QUrl, Qt, QRectF, QPointF
from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import pyqtSignal
import sys
import os
import shutil
import re
from urllib.parse import quote_plus
import validators
from PIL import Image
from PyQt5.QtGui import QPainter, QPainterPath, QPixmap
from PyQt5.QtCore import QSizeF
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import Qt

class HomePage(QWidget):
    def __init__(self, search_callback):
        super().__init__()
        self.search_callback = search_callback
        self.zoom_level = 1.0
        self.previous_url = None

        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignCenter)

        self.title = QLabel("Welcome to Boni")
        self.title.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.title)

        self.subtitle = QLabel("What's on your mind? 🤔")
        self.subtitle.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.subtitle)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search or enter URL...")
        self.search_input.returnPressed.connect(self.do_search)
        self.layout.addWidget(self.search_input, alignment=Qt.AlignCenter)

        self.search_btn = QPushButton("Boni Search")
        self.search_btn.clicked.connect(self.do_search)
        self.layout.addWidget(self.search_btn, alignment=Qt.AlignCenter)

        self.setLayout(self.layout)
        self.update_styles()

    def do_search(self):
        query = self.search_input.text()
        if query.strip():
            self.previous_url = "homepage"
            self.search_callback(query)

    def go_back(self):
        if self.previous_url:
            if self.previous_url == "homepage":
                self.search_input.clear()
                self.previous_url = None
                self.update_styles()
            else:
                pass

    def zoom_in(self):
        if self.zoom_level < 1.5:
            self.zoom_level += 0.1
            self.update_styles()

    def zoom_out(self):
        if self.zoom_level > 0.7:
            self.zoom_level -= 0.1
            self.update_styles()

    def update_styles(self):
        base_title_size = 36
        base_subtitle_size = 18
        base_input_width = 600
        base_input_height = 40
        base_btn_width = 200
        base_btn_height = 60
        base_btn_font = 18

        scale = self.zoom_level

        self.title.setStyleSheet(f"""
            font-size: {int(base_title_size * scale)}px;
            font-weight: bold;
            margin-bottom: {int(20 * scale)}px;
        """)

        self.subtitle.setStyleSheet(f"""
            font-size: {int(base_subtitle_size * scale)}px;
            color: #333;
            font-weight: bold;
            margin-bottom: {int(20 * scale)}px;
        """)

        self.search_input.setFixedWidth(int(base_input_width * scale))
        self.search_input.setFixedHeight(int(base_input_height * scale))
        self.search_input.setStyleSheet(f"""
            font-size: {int(16 * scale)}px;
            padding: {int(8 * scale)}px;
        """)

        self.search_btn.setFixedWidth(int(base_btn_width * scale))
        self.search_btn.setFixedHeight(int(base_btn_height * scale))
        self.search_btn.setStyleSheet(f"""
            font-size: {int(base_btn_font * scale)}px;
            padding: {int(10 * scale)}px;
        """)

    def keyPressEvent(self, event):
        if event.modifiers() == Qt.ControlModifier:
            if event.key() in (Qt.Key_Plus, Qt.Key_Equal):
                self.zoom_in()
                return
            elif event.key() == Qt.Key_Minus:
                self.zoom_out()
                return
        super().keyPressEvent(event)
