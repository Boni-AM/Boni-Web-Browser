from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton,
    QScrollArea, QWidget, QHBoxLayout
)
from PyQt5.QtCore import Qt, pyqtSignal
from functools import partial


class BookmarksDialog(QDialog):
    bookmark_clicked = pyqtSignal(str)

    def __init__(self, bookmarks, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Bookmarks")
        self.setMinimumSize(400, 500)

        layout = QVBoxLayout(self)

        title = QLabel("Your Bookmarks")
        title.setStyleSheet("font-size: 18px; font-weight: bold; padding: 10px 0;")
        layout.addWidget(title)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)

        container = QWidget()
        scroll.setWidget(container)

        bookmarks_layout = QVBoxLayout(container)
        bookmarks_layout.setAlignment(Qt.AlignTop)

        if not bookmarks:
            empty_label = QLabel("You haven't saved any bookmarks yet.")
            empty_label.setStyleSheet("color: gray; margin-top: 20px;")
            bookmarks_layout.addWidget(empty_label)
        else:
            for link in bookmarks:
                btn = QPushButton(link)
                btn.setCursor(Qt.PointingHandCursor)
                btn.setStyleSheet("""
                    QPushButton {
                        text-align: left;
                        padding: 6px 10px;
                        border: 1px solid #ddd;
                        border-radius: 4px;
                        background-color: #f9f9f9;
                        font-size: 13px;
                    }
                    QPushButton:hover {
                        background-color: #e6f2ff;
                        border: 1px solid #007acc;
                    }
                """)
                btn.clicked.connect(partial(self.open_link, link))
                bookmarks_layout.addWidget(btn)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        close_btn.setFixedHeight(32)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #007acc;
                color: white;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #005f99;
            }
        """)
        layout.addWidget(close_btn)

    def open_link(self, url):
        print("Bookmark clicked:", url)
        self.bookmark_clicked.emit(url)
        self.accept()
