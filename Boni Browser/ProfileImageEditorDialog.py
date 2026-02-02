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
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsPixmapItem, QGraphicsItem
from ResizableSquareCropItem import ResizableSquareCropItem
from PyQt5.QtWidgets import QGraphicsView
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout

class ProfileImageEditorDialog(QDialog):
    def __init__(self, image_path, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Profile Image")
        self.setMinimumSize(420, 480)
        self.image_path = image_path
        self.pixmap = QPixmap(image_path)
        self.image_width = self.pixmap.width()
        self.image_height = self.pixmap.height()

        self.scene = QGraphicsScene(self)
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)
        self.view.setFixedSize(400, 400)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.image_item = QGraphicsPixmapItem(self.pixmap)
        self.image_item.setFlags(QGraphicsItem.ItemIsSelectable)
        self.scene.addItem(self.image_item)
        self.scene.setSceneRect(0, 0, self.image_width, self.image_height)

        self.view.resetTransform()
        view_width = min(self.image_width, 400)
        view_height = min(self.image_height, 400)
        self.view.setFixedSize(view_width, view_height)
        self.scene.setSceneRect(0, 0, self.image_width, self.image_height)

        side = min(self.image_width, self.image_height, 200)
        x = (self.image_width - side) // 2
        y = (self.image_height - side) // 2

        self.crop_rect = ResizableSquareCropItem(QRectF(0, 0, side, side))
        self.crop_rect.setPos(x, y)
        self.scene.addItem(self.crop_rect)

        layout = QVBoxLayout()
        layout.addWidget(self.view)

        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("Save Image")
        self.save_btn.clicked.connect(self.save_crop)
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)

        btn_layout.addStretch()
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addStretch()

        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def save_crop(self):
        reply = QMessageBox.question(
            self,
            "Confirm Save",
            "Are you sure you want to save the image in Instagram format (320x320)?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.No:
            return

        try:
            with Image.open(self.image_path) as img:
                img = img.convert("RGB")
                img.thumbnail((320, 320), Image.LANCZOS)
                final_img = Image.new("RGB", (320, 320), (255, 255, 255))
                offset_x = (320 - img.width) // 2
                offset_y = (320 - img.height) // 2
                final_img.paste(img, (offset_x, offset_y))

                user_dir = os.path.join(os.path.expanduser("~"), ".boni_browser", "user_images")
                os.makedirs(user_dir, exist_ok=True)
                profile_path = os.path.join(user_dir, f"{self.parent().username}.png")
                final_img.save(profile_path, format='PNG')

            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save image:\n{str(e)}")
