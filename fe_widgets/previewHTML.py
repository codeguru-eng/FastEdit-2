from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import *
import sys
import methods
from base.widgets.baseWebView import *
from .mainWidgets import *

class PreviewWidget(QWidget):
    previewClosed = pyqtSignal()
    isClosed        = False
    def __init__(self, parent=None):
        super(PreviewWidget, self).__init__(parent)
        methods.registerObject(self)
        ######## Start ################
        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(5, 5, 5, 5)
        toolBar = QToolBar()
        self.urlBar = QLineEdit()
        self.urlBar.setObjectName("urlBar")
        self.urlBar.setReadOnly(True)
        closeBtn = QPushButton()
        closeBtn.setStyleSheet("""
            QPushButton{
            border: none;
            background: rgb(10, 82, 190);
                  color: #fff;
                  font-size: 15px;
                  padding: 5px 10px;
            }
            QPushButton:hover {
            background: rgb(10, 82, 190);
                  color: #fff;
            }
            QPushButton:pressed {
            background: rgb(10, 82, 250);
            }
        """)
        closeBtn.setIcon(QIcon("Images\\Icons\\cil-x.png"))
        closeBtn.setStatusTip("Close Preview Window")
        closeBtn.clicked.connect(self.closePreview)
        maxButton = QPushButton()
        maxButton.setStyleSheet("""
            QPushButton{
            border: none;
            background: rgb(10, 82, 190);
                  color: #fff;
                  font-size: 15px;
                  padding: 5px 10px;
            }
            QPushButton:hover {
            background: rgb(10, 82, 190);
                  color: #fff;
            }
            QPushButton:pressed {
            background: rgb(10, 82, 250);
            }
        """)
        maxButton.setIcon(QIcon("Images\\Icons\\cil-window-maximize.png"))
        maxButton.setStatusTip("Maximize Preview Window")
        maxButton.clicked.connect(self.max)
        self.label = QLabel("Preview")
        self.label.setObjectName("previewHTMLLabel")
        toolBar.addWidget(self.label)
        toolBar.addWidget(self.urlBar)
        toolBar.addWidget(maxButton)
        toolBar.addWidget(closeBtn)
        self.webview = FE_WebViewBase()
        self.webview.urlChanged.connect(self.url_changed)
        layout.addWidget(toolBar)
        layout.addWidget(self.webview)
        self.setMaximumWidth(800)
        self.setMinimumWidth(300)
    def closePreview(self):
        self.close()
        self.previewClosed.emit()
        self.isClosed = True
    def url_changed(self, url):
        url = url.toString()
        self.urlBar.setText(url)
    def max(self):
        self.browser = BrowserWindow()
        self.browser.urlBar.setText(self.urlBar.text())
        self.browser.loadURL(self.urlBar.text())
        self.browser.setWindowTitle(f"Browser")
        self.browser.showMaximized()
        self.closePreview()
    def load_url(self, url):
        self.webview.load_url(url)
        self.show()
        self.isClosed = False