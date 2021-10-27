from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtWidgets import *
import sys
import os
import methods
import platform

appName = methods.getAppName()
writerName = methods.getWriterName()
fullAppName = methods.getFullAppName()
version = methods.getAppVersion()
appType = methods.getAppType()
Os = platform.system()
osVersion = platform.version()

loc = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/"
path = os.path.join(loc, "fe_widgets/web/changeLog.html")
with open(path, "r") as file:
      _text = file.read()

class ChangeLog(QWebEngineView):
	def __init__(self):
		super().__init__()
		self.setWindowTitle("Change Log: Version 2.0.0")
		self.setHtml(_text)
		self.setContextMenuPolicy(Qt.NoContextMenu)
if __name__=="__main__":
      app = QApplication(sys.argv)
      window = ChangeLog()
      window.show()
      app.exec_()