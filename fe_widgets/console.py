from urllib import request
from settings.theme import *
from settings.font import *
from settings.settings import *
from data.stylesheets import *
from terminal import *
from .problems import *
import methods
from PyQt5.QtWidgets import QAbstractScrollArea, QLabel, QLineEdit, QListWidget, QPlainTextEdit, QTabWidget, QVBoxLayout, QWidget
from PyQt5.QtCore import QCoreApplication, QProcess, QSize, Qt
import os
import json
import requestsFE
from resources import *
from fe_shell import *

loc = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/"
path = os.path.join(loc, "settings/settings_folder/console.fe_settings")
with open(path, "r") as file:
      _text = file.read()
data = json.loads(_text)

if "Run" in data:
      if "OpenHTMLFileInBuiltinBrowser" in data["Run"]:
            if data["Run"]["OpenHTMLFileInBuiltinBrowser"] is True:
                  OpenHTMLInBuiltinBrowser = True
            elif data["Run"]["OpenHTMLFileInBuiltinBrowser"] is False:
                  OpenHTMLInBuiltinBrowser = False
            elif data["Run"]["OpenHTMLFileInBuiltinBrowser"] == "previewInEditor":
                  OpenHTMLInBuiltinBrowser = "preview"
            else:
                  OpenHTMLInBuiltinBrowser = True
      else:
            OpenHTMLInBuiltinBrowser = True
else:
      OpenHTMLInBuiltinBrowser = True
if "Console" in data:
      if "CaretWidth" in data["Console"]:
            ConsoleCaretWidth             = data["Console"]["CaretWidth"]
      else:
            ConsoleCaretWidth             = 12
      if "ReadOnlyMode" in data["Console"]:
            ConsoleReadOnly               = data["Console"]["ReadOnlyMode"]
      else:
            ConsoleReadOnly               = True
      if "MinHeight" in data["Console"]:
            MinHeight                     = data["Console"]["MinHeight"]
      else:
            MinHeight                     = 180
      if "MaxHeight" in data["Console"]:
            MaxHeight                     = data["Console"]["MaxHeight"]
      else:
            MaxHeight                     = 235
else:
      ConsoleCaretWidth             = 12
      ConsoleReadOnly               = True
      MinHeight                     = 180
      MaxHeight                     = 235
class Output(QPlainTextEdit):
      def __init__(self, parent=None):
            super(Output, self).__init__(parent)            
            self.setUndoRedoEnabled(False)
            self.setCursorWidth(ConsoleCaretWidth)
            self.moveCursor(QTextCursor.EndOfLine)
            font = QFont()
            font.setFamily(FontFamily.Console)
            font.setPointSizeF(FontSize.FontSizeTerminal)
            self.setFont(font)
            self.setContextMenuPolicy(Qt.NoContextMenu)
            self.verticalScrollBar().setContextMenuPolicy(Qt.NoContextMenu)
            self.setReadOnly(ConsoleReadOnly)
            self.verticalScrollBar().setContextMenuPolicy(Qt.NoContextMenu)
            self.horizontalScrollBar().setContextMenuPolicy(Qt.NoContextMenu)
      def focusInEvent(self, event):
            self.parent.btn7.setText("Output")
            super().focusInEvent(event)
class ConsoleWidget(QTabWidget):
      def __init__(self, parent=None):
            super(ConsoleWidget, self).__init__(parent)
            self.setMinimumHeight(MinHeight)
            self.setMaximumHeight(MaxHeight)
            self.setMovable(False)
            self.setTabPosition(QTabWidget.North)
            self.setIconSize(QSize(25,25))
            a = self.addTab(Output(), "Output")
            self.setTabIcon(a, QIcon("Images\\Icons\\iconOutput.png"))
            self.setTabToolTip(a, "Output")
            b = self.addTab(requestsFE.get(FE_GetAssistant), "Assistant")
            self.setTabIcon(b, QIcon("Images\\Icons\\iconAssistant.png"))
            self.setTabToolTip(b, "Assistant")
            """
            c = self.addTab(Problems(), "Problems")
            self.setTabIcon(c, QIcon("Images\\Icons\\iconProblem.png"))
            self.setTabToolTip(c, "Problems")
            """
            d = self.addTab(Terminal(), "Terminal")
            self.setTabIcon(d, QIcon("Images\\Icons\\iconTerminal.png"))
            self.setTabToolTip(d, "Terminal")
            e = self.addTab(FE_Shell(), "FE Shell")
            self.setTabIcon(e, QIcon("Images\\txteditor.png"))
            self.setTabToolTip(e, "FE Shell")
            self.output = self.widget(a)
            self.assistant = self.widget(b).outputArea
            self.askField = self.widget(b).commandArea
            self.assistantM = self.widget(b)
            #self.problems = self.widget(c)
            self.terminal = self.widget(d)
      def focusInEvent(self, event):
            self.parent.btn7.setText("Console")
            super().focusInEvent(event)