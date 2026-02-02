from PyQt5.QtWebEngineWidgets import QWebEngineView
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
from ZoomableWebEngineView import ZoomableWebEngineView
from HomePage import HomePage
from ProfilePopupDialog import ProfilePopupDialog
from LoginWidget import LoginWidget
from ClickableLabel import ClickableLabel
from Database import Database
from BookmarksDialog import BookmarksDialog

class BoniBrowser(QMainWindow):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.username = "guest"
        self.setWindowTitle("Boni Browser")
        self.resize(1000, 700)

        self.tabs = QTabWidget(self)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.setCentralWidget(self.tabs)

        self.home_page = HomePage(self.handle_search)
        self.tabs.addTab(self.home_page, "Home")
        self.tabs.setCurrentIndex(0)

        self.init_toolbar()
        self.tabs.currentChanged.connect(self.on_tab_changed)
        self.installEventFilter(self)
        self.webview = QWebEngineView()
        self.bookmarks = []
        self.bookmarks_file = os.path.join(os.path.expanduser("~"), ".boni_browser", "bookmarks.json")

        self.load_bookmarks()
        self.bookmarks = self.load_bookmarks()

    import json
    import os

    from PyQt5.QtCore import Qt, QEvent
    from PyQt5.QtWidgets import QMessageBox

    def eventFilter(self, obj, event):
        if event.type() == event.KeyPress:
            key = event.key()
            modifiers = event.modifiers()

            if modifiers == Qt.ControlModifier:
                if key == Qt.Key_W:
                    self.close_current_tab()
                    return True
                elif key == Qt.Key_T:
                    self.open_new_tab()
                    return True
                elif key in (Qt.Key_Plus, Qt.Key_Equal):
                    self.zoom_in_current()
                    return True
                elif key == Qt.Key_Minus:
                    self.zoom_out_current()
                    return True
                elif key == Qt.Key_R:
                    self.reload_page()
                    return True

            if key == Qt.Key_F11:
                self.toggle_fullscreen()
                return True

            if key == Qt.Key_F5:
                self.reload_page()
                return True
            elif event.key() == Qt.Key_S and event.modifiers() == Qt.ControlModifier:
                self.bookmark_current_page()
                return True

        return super().eventFilter(obj, event)

    def init_toolbar(self):
        toolbar = QToolBar("Navigation")
        toolbar.setMovable(False)
        self.addToolBar(Qt.TopToolBarArea, toolbar)

        new_tab_button = QAction("New Tab", self)
        new_tab_button.triggered.connect(self.open_new_tab)
        toolbar.addAction(new_tab_button)

        self.back_btn = QPushButton("←")
        self.back_btn.clicked.connect(self.go_back)
        self.back_btn.setEnabled(False)
        toolbar.addWidget(self.back_btn)

        self.forward_btn = QPushButton("→")
        self.forward_btn.clicked.connect(self.go_forward)
        self.forward_btn.setEnabled(False)
        toolbar.addWidget(self.forward_btn)

        self.reload_btn = QToolButton()
        self.reload_btn.setIcon(QIcon.fromTheme("view-refresh"))
        if self.reload_btn.icon().isNull():
            self.reload_btn.setText("🔄")
        self.reload_btn.setToolTip("Reload Page")
        self.reload_btn.clicked.connect(self.reload_page)
        toolbar.addWidget(self.reload_btn)

        toolbar.addWidget(QLabel("URL:"))
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search or enter URL...")
        self.search_bar.returnPressed.connect(self.on_search_bar_enter)
        toolbar.addWidget(self.search_bar)

        search_btn = QToolButton()
        search_btn.setIcon(QIcon.fromTheme("system-search"))
        if search_btn.icon().isNull():
            search_btn.setText("🔍")
        search_btn.setToolTip("Search")
        search_btn.clicked.connect(self.on_search_bar_enter)
        toolbar.addWidget(search_btn)

        zoom_in_btn = QPushButton("Zoom In")
        zoom_in_btn.clicked.connect(self.zoom_in_current)
        toolbar.addWidget(zoom_in_btn)

        zoom_out_btn = QPushButton("Zoom Out")
        zoom_out_btn.clicked.connect(self.zoom_out_current)
        toolbar.addWidget(zoom_out_btn)

        clear_hist_btn = QPushButton("Clear History")
        clear_hist_btn.clicked.connect(self.clear_history)
        toolbar.addWidget(clear_hist_btn)

        self.login_btn = QPushButton("Login / Signup")
        self.login_btn.clicked.connect(self.open_login_dialog)

        self.user_icon = ClickableLabel()

        pixmap = QPixmap("Untitled design (1).png")
        size = 30
        circular_pixmap = self.get_circular_pixmap(pixmap, size)

        self.user_icon.setPixmap(circular_pixmap)
        self.user_icon.setFixedSize(size, size)
        self.user_icon.setStyleSheet("border-radius: 15px;")
        self.user_icon.clicked.connect(self.on_user_icon_clicked)

        self.user_label = QLabel(f"User: {self.username}")
        self.user_label.setStyleSheet("margin-left: 10px; font-weight: bold;")

        login_layout = QHBoxLayout()
        login_layout.setContentsMargins(0, 0, 0, 0)
        login_layout.setSpacing(2)
        login_layout.addWidget(self.login_btn)
        login_layout.addWidget(self.user_icon)

        login_widget_container = QWidget()
        login_widget_container.setLayout(login_layout)

        toolbar.addWidget(login_widget_container)
        toolbar.addWidget(self.user_label)

    def reload_page(self):
        current = self.tabs.currentWidget()
        if isinstance(current, ZoomableWebEngineView):
            current.reload()

    def open_new_tab(self):
        new_tab_page = HomePage(self.handle_search)
        new_tab_index = self.tabs.addTab(new_tab_page, "New Tab")
        self.tabs.setCurrentIndex(new_tab_index)
        self.search_bar.setText("")

    def close_tab(self, index):
        if self.tabs.count() == 1:
            self.close()
        else:
            self.tabs.removeTab(index)

    def close_current_tab(self):
        current_index = self.tabs.currentIndex()
        if self.tabs.count() > 1:
            self.tabs.removeTab(current_index)
        else:
            self.close()

    def open_login_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Login / Signup")

        login_widget = LoginWidget(self.db, self.handle_login, dialog=dialog)

        layout = QVBoxLayout()
        layout.addWidget(login_widget)
        dialog.setLayout(layout)

        dialog.exec_()

    def handle_login(self, username, password=None):
        self.username = username
        self._session_password = password
        self.is_logged_in = True
        self.update_user_label()
        self.update_user_profile_icon()
        self.bookmarks = self.load_bookmarks()

    def update_user_label(self):
        self.user_label.setText(f"User: {self.username}")

    def handle_search(self, query):
        if not query.strip():
            return

        if self.is_valid_url(query):
            url = QUrl(query if query.startswith("http") else "http://" + query)
            self.show_url(url.toString())
        else:
            self.db.save_history(self.username, query, entry_type='search')
            search_url = f"https://www.google.com/search?q={quote_plus(query)}"
            self.show_url(search_url)

    def show_url(self, url):
        current = self.tabs.currentWidget()

        if isinstance(current, ZoomableWebEngineView):
            current.setUrl(QUrl(url))
            self.search_bar.setText(url)

        elif isinstance(current, HomePage):
            web_view = ZoomableWebEngineView()
            web_view.setUrl(QUrl(url))
            web_view.urlChanged.connect(lambda url, w=web_view: self.update_url_bar(url, w))
            web_view.titleChanged.connect(lambda title, w=web_view: self.update_tab_title(title, w))
            web_view.urlChanged.connect(self._on_url_changed_visit)

            index = self.tabs.currentIndex()
            self.tabs.removeTab(index)
            self.tabs.insertTab(index, web_view, "Loading...")
            self.tabs.setCurrentIndex(index)
            self.search_bar.setText(url)

        else:
            web_view = ZoomableWebEngineView()
            web_view.setUrl(QUrl(url))
            web_view.urlChanged.connect(lambda url, w=web_view: self.update_url_bar(url, w))
            web_view.titleChanged.connect(lambda title, w=web_view: self.update_tab_title(title, w))
            web_view.urlChanged.connect(self._on_url_changed_visit)

            index = self.tabs.currentIndex()
            self.tabs.removeTab(index)
            self.tabs.insertTab(index, web_view, "Loading...")
            self.tabs.setCurrentIndex(index)
            self.search_bar.setText(url)

    def is_valid_url(self, url):
        url = url.strip()
        if re.match(r"^(https?://|www\.)", url):
            return validators.url(url if url.startswith("http") else "http://" + url)
        return False

    def on_search_bar_enter(self):
        query = self.search_bar.text().strip()
        self.handle_search(query)

    def zoom_in_current(self):
        current = self.tabs.currentWidget()
        if isinstance(current, ZoomableWebEngineView):
            current.zoom_in()
        elif isinstance(current, HomePage):
            current.zoom_in()

    def zoom_out_current(self):
        current = self.tabs.currentWidget()
        if isinstance(current, ZoomableWebEngineView):
            current.zoom_out()
        elif isinstance(current, HomePage):
            current.zoom_out()

    def go_back(self):
        current = self.tabs.currentWidget()
        if isinstance(current, ZoomableWebEngineView) and current.history().canGoBack():
            current.back()

    def go_forward(self):
        current = self.tabs.currentWidget()
        if isinstance(current, ZoomableWebEngineView) and current.history().canGoForward():
            current.forward()

    def clear_history(self):
        history = self.db.get_user_history(self.username)
        if not history:
            QMessageBox.information(self, "No History", "There is no history to be removed.")
        else:
            reply = QMessageBox.question(
                self,
                "Confirm Clear History",
                "Are you sure you want to delete your browsing history?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.db.clear_user_history(self.username)
                QMessageBox.information(self, "History", "Browsing history cleared.")

    def update_url_bar(self, url, web_view):
        if self.tabs.currentWidget() == web_view:
            self.search_bar.setText(url.toString())
        self.back_btn.setEnabled(web_view.history().canGoBack())
        self.forward_btn.setEnabled(web_view.history().canGoForward())

    def update_tab_title(self, title, web_view):
        index = self.tabs.indexOf(web_view)
        if index != -1:
            self.tabs.setTabText(index, title if title else "New Tab")

    def _on_url_changed_visit(self, url):
        if url.scheme() in ['http', 'https']:
            self.db.save_history(self.username, url.toString(), entry_type='visit')

    def on_tab_changed(self, index):
        current = self.tabs.widget(index)
        if isinstance(current, ZoomableWebEngineView):
            self.search_bar.setText(current.url().toString())
            self.back_btn.setEnabled(current.history().canGoBack())
            self.forward_btn.setEnabled(current.history().canGoForward())
        else:
            self.search_bar.setText("")
            self.back_btn.setEnabled(False)
            self.forward_btn.setEnabled(False)

    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def on_user_icon_clicked(self):
        dialog = ProfilePopupDialog(self.username, self)
        dialog.exec_()

    def get_circular_pixmap(self, pixmap, size):
        scaled_pixmap = pixmap.scaled(size, size, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)

        result = QPixmap(size, size)
        result.fill(Qt.transparent)

        painter = QPainter(result)
        painter.setRenderHint(QPainter.Antialiasing)

        path = QPainterPath()
        path.addEllipse(0, 0, size, size)
        painter.setClipPath(path)

        x_offset = (scaled_pixmap.width() - size) // 2
        y_offset = (scaled_pixmap.height() - size) // 2
        source_rect = scaled_pixmap.rect().adjusted(x_offset, y_offset, -x_offset, -y_offset)

        painter.drawPixmap(result.rect(), scaled_pixmap, source_rect)
        painter.end()

        return result

    def update_user_profile_icon(self):
        user_dir = os.path.join(os.path.expanduser("~"), ".boni_browser", "user_images")
        profile_path = os.path.join(user_dir, f"{self.username}.png")

        if os.path.exists(profile_path):
            pixmap = QPixmap(profile_path)
            circular_pixmap = self.get_circular_pixmap(pixmap, 31)
            self.user_icon.setPixmap(circular_pixmap)

    def get_bookmarks_filepath(self):
        user_dir = os.path.join(os.path.expanduser("~"), ".boni_browser", "bookmarks")
        os.makedirs(user_dir, exist_ok=True)
        return os.path.join(user_dir, f"{self.username}_bookmarks.json")

    def save_bookmarks(self):
        filepath = self.get_bookmarks_filepath()
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(self.bookmarks, f, ensure_ascii=False, indent=4)
        except Exception as e:
            QMessageBox.warning(self, "Bookmark Save Error", f"Could not save bookmarks:\n{str(e)}")

    def load_bookmarks(self):
        filepath = self.get_bookmarks_filepath()
        if os.path.exists(filepath):
            with open(filepath, "r") as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    return []
        return []

    def closeEvent(self, event):
        self.save_bookmarks()
        super().closeEvent(event)

    def show_bookmarks_dialog(self):
        dialog = BookmarksDialog(self.bookmarks, self)
        dialog.bookmark_clicked.connect(self.show_url)
        dialog.exec_()

def main():
    app = QApplication(sys.argv)
    db = Database()
    browser = BoniBrowser(db)
    browser.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
