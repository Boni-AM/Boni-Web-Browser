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
from ZoomableWebEngineView import ZoomableWebEngineView


class SearchResultsPage(QWidget):
    def __init__(self, query):
        super().__init__()
        self.query = query
        layout = QVBoxLayout()

        self.label = QLabel(f"Search results for: <b>{query}</b>")
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)

        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        self.init_tabs()
        self.update_search(query)

        self.setLayout(layout)

    def init_tabs(self):
        categories = ["All", "Videos", "Images", "News"]
        for category in categories:
            web_view = ZoomableWebEngineView()
            web_view.urlChanged.connect(self._on_url_changed_visit)
            self.tabs.addTab(web_view, category)

    def update_search(self, query):
        self.query = query
        self.label.setText(f"Search results for: <b>{query}</b>")

        query_encoded = quote_plus(query)
        urls = {
            "All": f"https://www.google.com/search?q={query_encoded}",
            "Videos": f"https://www.google.com/search?tbm=vid&q={query_encoded}",
            "Images": f"https://www.google.com/search?tbm=isch&q={query_encoded}",
            "News": f"https://news.google.com/search?q={query_encoded}",
        }

        for i, category in enumerate(urls):
            web_view = self.tabs.widget(i)
            if isinstance(web_view, ZoomableWebEngineView):
                web_view.setUrl(QUrl(urls[category]))

    def _on_url_changed_visit(self, url):
        if url.isValid() and url.scheme().startswith("http"):
            main_win = self.window()
            try:
                db = main_win.db
                username = main_win.username
            except Exception:
                return
            db.save_history(username, url.toString(), entry_type='visit')
