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
from PyQt5.QtGui import QIcon, QPixmap, QFont, QPainter, QPainterPath
import re
from urllib.parse import quote_plus
import validators
import os
import shutil
from PIL import Image
from PyQt5.QtWidgets import QSpacerItem, QSizePolicy
from BookmarksDialog import BookmarksDialog
from ProfileImageEditorDialog import ProfileImageEditorDialog

class ProfilePopupDialog(QDialog):
    def __init__(self, username, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Profile")
        self.setFixedSize(250, 370)
        self.main_window = parent
        self.username = username

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        self.image_label = QLabel()
        self.image_label.setFixedSize(80, 80)
        self.image_label.setStyleSheet("border-radius: 40px;")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.update_profile_image()

        layout.addSpacerItem(QSpacerItem(20, 10, QSizePolicy.Minimum, QSizePolicy.Fixed))

        image_layout = QHBoxLayout()
        image_layout.addStretch()
        image_layout.addWidget(self.image_label)
        image_layout.addStretch()
        layout.addLayout(image_layout)

        self.history_btn = QPushButton("View History")
        self.history_btn.setCursor(Qt.PointingHandCursor)
        self.history_btn.setFixedSize(180, 40)
        btn_font = QFont()
        btn_font.setPointSize(int(self.history_btn.height() * 0.3))
        self.history_btn.setFont(btn_font)
        self.history_btn.setStyleSheet("""
            QPushButton {
                background-color: #0078d7;
                color: white;
                border-radius: 8px;
                margin-top: 15px;
            }
            QPushButton:hover {
                background-color: #005bb5;
            }
            QPushButton:pressed {
                background-color: #004a99;
            }
        """)
        self.history_btn.clicked.connect(self.view_history)
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(self.history_btn)
        btn_layout.addStretch()

        if username != "guest":
            self.bookmark_btn = QPushButton("Bookmarks")
            self.bookmark_btn.setCursor(Qt.PointingHandCursor)
            self.bookmark_btn.setFixedSize(180, 40)
            self.bookmark_btn.setFont(btn_font)
            self.bookmark_btn.setStyleSheet("""
                QPushButton {
                    background-color: #6f42c1;
                    color: white;
                    border-radius: 8px;
                    margin-top: 10px;
                }
                QPushButton:hover {
                    background-color: #5a32a3;
                }
                QPushButton:pressed {
                    background-color: #482983;
                }
            """)
            self.bookmark_btn.clicked.connect(self.open_bookmarks)
            bookmark_btn_layout = QHBoxLayout()
            bookmark_btn_layout.addStretch()
            bookmark_btn_layout.addWidget(self.bookmark_btn)
            bookmark_btn_layout.addStretch()
            layout.addLayout(bookmark_btn_layout)

            self.change_image_btn = QPushButton("Change Image")
            self.change_image_btn.setFixedSize(120, 30)
            self.change_image_btn.setCursor(Qt.PointingHandCursor)
            self.change_image_btn.clicked.connect(self.change_image)
            change_img_btn_layout = QHBoxLayout()
            change_img_btn_layout.addStretch()
            change_img_btn_layout.addWidget(self.change_image_btn)
            change_img_btn_layout.addStretch()
            layout.addLayout(change_img_btn_layout)

            layout.addSpacerItem(QSpacerItem(20, 10, QSizePolicy.Minimum, QSizePolicy.Fixed))

            self.edit_pic_btn = QPushButton("Edit Profile Pic")
            self.edit_pic_btn.setFixedSize(130, 30)
            self.edit_pic_btn.setCursor(Qt.PointingHandCursor)
            self.edit_pic_btn.clicked.connect(self.open_image_editor)
            edit_btn_layout = QHBoxLayout()
            edit_btn_layout.addStretch()
            edit_btn_layout.addWidget(self.edit_pic_btn)
            edit_btn_layout.addStretch()
            layout.addLayout(edit_btn_layout)

        if username == "guest":
            info_label = QLabel("You are browsing as a guest.")
            info_label.setAlignment(Qt.AlignCenter)
            info_label.setStyleSheet("font-weight: bold; color: orange; margin-top: 15px;")
            layout.addWidget(info_label)

            self.login_btn = QPushButton("Log In")
            self.login_btn.setCursor(Qt.PointingHandCursor)
            self.login_btn.setFixedSize(180, 40)
            self.login_btn.setFont(btn_font)
            self.login_btn.setStyleSheet("""
                QPushButton {
                    background-color: #28a745;
                    color: white;
                    border-radius: 8px;
                    margin-top: 10px;
                }
                QPushButton:hover {
                    background-color: #218838;
                }
                QPushButton:pressed {
                    background-color: #1e7e34;
                }
            """)
            self.login_btn.clicked.connect(self.open_login)
            login_btn_layout = QHBoxLayout()
            login_btn_layout.addStretch()
            login_btn_layout.addWidget(self.login_btn)
            login_btn_layout.addStretch()
            layout.addLayout(login_btn_layout)

        else:
            name_label = QLabel(f"Username: @{username}")
            name_label.setAlignment(Qt.AlignCenter)
            name_label.setStyleSheet("font-weight: bold; font-size: 14px; margin-top: 10px;")
            layout.addWidget(name_label)

            pw_container = QHBoxLayout()
            self.password_label = QLabel("Password: ********")
            self.password_label.setAlignment(Qt.AlignCenter)
            self.password_label.setStyleSheet("font-weight: bold; font-size: 14px;")
            self.password_label.setFixedWidth(150)
            pw_container.addWidget(self.password_label)

            self.toggle_btn = QToolButton()
            self.toggle_btn.setText("👁️")
            self.toggle_btn.setCursor(Qt.PointingHandCursor)
            self.toggle_btn.setStyleSheet("border: none; font-size: 16px;")
            self.toggle_btn.setToolTip("Show/Hide Password")
            self.toggle_btn.clicked.connect(self.toggle_password_visibility)
            pw_container.addWidget(self.toggle_btn)

            layout.addLayout(pw_container)

            self.real_password = getattr(parent, "_session_password", None)
            self.is_hidden = True
            self.bookmarks = []
            self.current_url = "https://example.com"

        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def open_bookmarks(self):
        if self.main_window and hasattr(self.main_window, "bookmarks"):
            dlg = BookmarksDialog(self.main_window.bookmarks, self)
            dlg.exec_()
        else:
            QMessageBox.warning(self, "Error", "Bookmarks not available.")

    def get_user_image_path(self):
        user_dir = os.path.join(os.path.expanduser("~"), ".boni_browser", "user_images")
        os.makedirs(user_dir, exist_ok=True)
        return os.path.join(user_dir, f"{self.username}.png")

    def change_image(self):
        if self.username == "guest":
            QMessageBox.warning(self, "Permission Denied", "Only logged-in users can change their profile image.")
            return

        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Profile Image",
            "",
            "Image Files (*.png *.jpg *.jpeg *.bmp);;All Files (*)",
            options=options
        )
        if file_path:
            user_dir = os.path.join(os.path.expanduser("~"), ".boni_browser", "user_images")
            os.makedirs(user_dir, exist_ok=True)
            original_path = os.path.join(user_dir, f"{self.username}_original.png")
            shutil.copyfile(file_path, original_path)

            with Image.open(file_path) as img:
                img = img.convert("RGB")
                img = self.resize_and_crop(img, (320, 320))
                profile_pic_path = self.get_user_image_path()
                img.save(profile_pic_path, format='PNG')

            self.update_profile_image()
            QMessageBox.information(self, "Success", "Profile image updated successfully!")

    def open_image_editor(self):
        user_dir = os.path.join(os.path.expanduser("~"), ".boni_browser", "user_images")
        original_path = os.path.join(user_dir, f"{self.username}_original.png")
        profile_path = self.get_user_image_path()

        if not os.path.exists(original_path):
            if os.path.exists(profile_path):
                shutil.copyfile(profile_path, original_path)
            else:
                QMessageBox.warning(self, "No Image", "No profile image to edit.")
                return

        editor = ProfileImageEditorDialog(original_path, self)
        if editor.exec_() == QDialog.Accepted:
            self.update_profile_image()
            if self.main_window and hasattr(self.main_window, "update_user_profile_icon"):
                self.main_window.update_user_profile_icon()
            QMessageBox.information(self, "Success", "Profile image updated successfully!")

    def toggle_password_visibility(self):
        if self.is_hidden:
            self.password_label.setText(f"Password: {self.real_password}")
            self.toggle_btn.setText("🚫")
        else:
            self.password_label.setText("Password: ********")
            self.toggle_btn.setText("👁️")
        self.is_hidden = not self.is_hidden

    def view_history(self):
        if self.main_window:
            self.main_window.view_history()

    def open_login(self):
        if self.main_window:
            self.close()
            self.main_window.open_login_dialog()

    def update_profile_image(self):
        user_image_path = self.get_user_image_path()
        size = 80
        user_dir = os.path.join(os.path.expanduser("~"), ".boni_browser", "user_images")
        original_path = os.path.join(user_dir, f"{self.username}_original.png")

        if os.path.exists(user_image_path):
            pixmap = QPixmap(user_image_path)
        else:
            pixmap = QPixmap("Untitled design (1).png")

        if not os.path.exists(original_path) and os.path.exists(user_image_path):
            shutil.copyfile(user_image_path, original_path)

        circular_pixmap = self.get_circular_pixmap(pixmap, size)
        self.image_label.setPixmap(circular_pixmap)

    def resize_and_crop(self, img, size):
        width, height = img.size
        new_width, new_height = size
        aspect = width / height
        target_aspect = new_width / new_height

        if aspect > target_aspect:
            new_w = int(height * target_aspect)
            offset = (width - new_w) // 2
            img = img.crop((offset, 0, offset + new_w, height))
        else:
            new_h = int(width / target_aspect)
            offset = (height - new_h) // 2
            img = img.crop((0, offset, width, offset + new_h))

        return img.resize(size, Image.LANCZOS)

    def get_circular_pixmap(self, pixmap, size):
        result = QPixmap(size, size)
        result.fill(Qt.transparent)
        painter = QPainter(result)
        painter.setRenderHint(QPainter.Antialiasing)
        path = QPainterPath()
        path.addEllipse(0, 0, size, size)
        painter.setClipPath(path)
        scaled = pixmap.scaled(size, size, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        painter.drawPixmap(0, 0, scaled)
        painter.end()
        return result
