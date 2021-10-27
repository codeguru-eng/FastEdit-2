import os
from settings.theme import *
from PyQt5.QtCore import QFile, QUrl, Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import * 
from PyQt5.QtWebEngineWidgets import *
from data.stylesheets import *
from base.widgets.baseWebView import *


class Menu(QMenu):
	"""Used this widget for context menu of editor""" 
	def __init__(self, parent=None):
            super().__init__(parent)
            self.setStyleSheet(Theme.MenuDark)
class Button(QPushButton):
	def __init__(self, parent=None):
		super().__init__(parent)
		self.setStyleSheet(Theme.DialogButton)
	def set_Text(self, text: str):
		self.setText(text)
class MainWidget(QWidget):
	def __init__(self,parent=None):
	    super().__init__(parent)
	    self.setStyleSheet(auto_completer_)
class BrowserWindow(QWidget):
	def __init__(self, parent=None):
		super().__init__(parent)
		self.setStyleSheet("""
		QWidget {
			background: #222;
			color: #fff;
		}
		QPushButton{
			border: none;
			color: #fff;
                  font-size: 17px;
                  padding: 6px 20px;
                  background: #222;
			margin: 0;
		}
		QPushButton:hover {
			background: rgb(10, 82, 190);
		}
		QPushButton:pressed {
			background: rgb(10, 82, 250);
		}
		QLineEdit {
			padding: 10px 20px;
			border: none;
			background: #222;
			font-family: verdana;
			font-size: 16px;
		}
		QLineEdit:hover {
			background: #222;
		}
		QLineEdit:focus {
			background: #333;
		}
		""")
		self.toolBar = QToolBar()
		self.toolBar.setContentsMargins(0,0,0,0)
		self.webView = FE_WebViewBase()
		self.webView.setContextMenuPolicy(Qt.NoContextMenu)
		layout = QVBoxLayout(self)
		layout.setSpacing(0)
		layout.setContentsMargins(0,0,0,0)
		layout.addWidget(self.toolBar)
		layout.addWidget(self.webView)
		reloadBtn = QPushButton()
		reloadBtn.setText("Reload")
		reloadBtn.clicked.connect(self.webView.reload)
		self.urlBar = QLineEdit()
		self.urlBar.setReadOnly(True)
		self.urlBar.setPlaceholderText("Enter url here...")
		self.goBtn = QPushButton()
		self.goBtn.setText("Go")
		self.toolBar.addWidget(reloadBtn)
		self.toolBar.addWidget(self.urlBar)
		self.toolBar.addWidget(self.goBtn)
		self.urlBar.returnPressed.connect(self.loadTextInUrl)
		self.goBtn.clicked.connect(self.loadTextInUrl)
	def loadTextInUrl(self):
		url = self.urlBar.text()
		self.loadURL(url)
	def loadURL(self, url: str):
		self.webView.load(QUrl(url))
	def focusInEvent(self, event):
		self.parent.btn7.setText("PreviewWidget")
		super().focusInEvent(event)