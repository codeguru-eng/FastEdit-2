from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import methods
import platform

appName = methods.getAppName()
writerName = methods.getWriterName()
fullAppName = methods.getFullAppName()
version = methods.getAppVersion()
appType = methods.getAppType()
Os = platform.system()
osVersion = platform.version()

class no(QMessageBox):
      def __init__(self, parent=None):
            super(no, self).__init__(parent)
            self.setWindowIcon(QIcon("Images/txteditor.png"))
            self.setWindowTitle("Check for Updates")
            reply = self.question(parent, f"", \
                        f"No Updates available!", QMessageBox.Ok)
            if reply == QMessageBox.Ok:
                  self.close()
class yes(QMessageBox):
      def __init__(self, parent=None):
            super(yes, self).__init__(parent)
            self.setWindowIcon(QIcon("Images/txteditor.png"))
            self.setWindowTitle("Check for Updates")
            reply = self.question(parent, f"", \
                        f"Version {version} is available. Download from github!", QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                  self.close()