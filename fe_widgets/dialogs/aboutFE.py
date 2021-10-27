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

class aboutDlg(QMessageBox):
      def __init__(self, parent=None):
            super(aboutDlg, self).__init__(parent)
            self.setWindowFlags(Qt.SplashScreen)
            self.setWindowIcon(QIcon("Images\\txteditor.png"))
            txt = f"""
            <h1>About</h1>
            <p>{appName} is a open-source {appType} created by {writerName}.</p>
            <ul>
                  <li><b>App Version: </b>{version}</li>
                  <li><b>App Type: </b>{appType}</li>
                  <li><b>OS: </b>{Os}</li>
                  <li><b>OS Version: </b>{osVersion}</li>
            </ul>
            """
            self.setText(txt)
            self.show()