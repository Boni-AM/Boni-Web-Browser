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

class LoginWidget(QWidget):
    def __init__(self, db, login_callback, dialog = None):
        super().__init__()
        self.db = db
        self.login_callback = login_callback
        self.dialog = dialog

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)

        self.toggle_password_btn = QToolButton(self.password_input)
        self.toggle_password_btn.setCursor(Qt.PointingHandCursor)
        self.toggle_password_btn.setStyleSheet("border: none; padding: 0px;")
        self.toggle_password_btn.setText("🚫")
        self.toggle_password_btn.setToolTip("Show/Hide Password")
        self.toggle_password_btn.clicked.connect(self.toggle_password_visibility)
        self.toggle_password_btn.setFixedSize(20, 20)
        self.password_input.setTextMargins(0, 0, 25, 0)

        def resize_event(event):
            self.toggle_password_btn.move(self.password_input.width() - 25, (self.password_input.height() - 20) // 2)
            QLineEdit.resizeEvent(self.password_input, event)

        self.password_input.resizeEvent = resize_event

        self.login_btn = QPushButton("Login")
        self.signup_btn = QPushButton("Sign Up")

        self.message_label = QLabel("")
        self.message_label.setStyleSheet("color: red;")

        self.login_btn.clicked.connect(self.login)
        self.signup_btn.clicked.connect(self.signup)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("<h3>Login / Signup</h3>"))
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_input)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.login_btn)
        btn_layout.addWidget(self.signup_btn)

        layout.addLayout(btn_layout)
        layout.addWidget(self.message_label)
        self.setLayout(layout)

    def toggle_password_visibility(self):
        if self.password_input.echoMode() == QLineEdit.Password:
            self.password_input.setEchoMode(QLineEdit.Normal)
            self.toggle_password_btn.setText("👁️")
        else:
            self.password_input.setEchoMode(QLineEdit.Password)
            self.toggle_password_btn.setText("🚫")

    def login(self):
        user = self.username_input.text().strip()
        pwd = self.password_input.text().strip()

        if not user or not pwd:
            self.show_message("Please enter username and password.", error=True)
            return

        if not self.db.user_exists(user):
            self.show_message("User does not exist. Please sign up.", error=True)
            return

        if self.db.verify_user(user, pwd):
            self.show_message("")
            self.login_callback(user, pwd)
            if self.dialog:
                self.dialog.accept()
        else:
            self.show_message("Incorrect password.", error=True)

    def signup(self):
        user = self.username_input.text().strip()
        pwd = self.password_input.text().strip()

        if not user or not pwd:
            self.show_message("Please enter username and password.", error=True)
            return

        if len(user) < 6 or len(user) > 30:
            self.show_message("Username must be 6–30 characters long.", error=True)
            return

        if not re.match(r'^[a-zA-Z0-9.]+$', user):
            self.show_message("Username can only contain letters, numbers, and dots.", error=True)
            return

        if '..' in user or user.startswith('.') or user.endswith('.'):
            self.show_message("Username cannot start/end with dot or contain consecutive dots.", error=True)
            return

        if len(pwd) < 8:
            self.show_message("Password must be at least 8 characters long.", error=True)
            return

        if pwd.lower() in ['12345678', 'password', 'qwertyuiop', 'letmein', 'admin']:
            self.show_message("Please choose a stronger password.", error=True)
            return

        if not re.search(r'[A-Za-z]', pwd) or not re.search(r'[0-9]', pwd) or not re.search(r'[^A-Za-z0-9]', pwd):
            self.show_message("Password must include letters, numbers, and symbols.", error=True)
            return

        if self.db.add_user(user, pwd):
            self.show_message("Account created! You can now log in.", error=False)
        else:
            self.show_message("User already exists.", error=True)

    def show_message(self, text, error=True):
        color = "red" if error else "green"
        self.message_label.setText(text)
        self.message_label.setStyleSheet(f"color: {color}; font-weight: bold;")

    def verify_user(self, username, password):
        cursor = self.conn.cursor()
        cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        if result:
            hashed = result[0]
            return bcrypt.checkpw(password.encode('utf-8'), hashed)
        return False
