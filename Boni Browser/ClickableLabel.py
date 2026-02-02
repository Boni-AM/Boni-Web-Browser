import json
import sys
import sqlite3
from typing import Self
import bcrypt
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLineEdit, QToolBar, QAction, QWidget,
    QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QStackedWidget, QTabWidget,
    QMessageBox, QToolButton, QDialog, QTextEdit, QDialog,QFileDialog
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



class ClickableLabel(QLabel):
    clicked = pyqtSignal()

    def mousePressEvent(self, event):
        self.clicked.emit()