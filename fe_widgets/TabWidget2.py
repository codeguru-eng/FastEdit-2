import os
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor, QIcon
from PyQt5.QtWidgets import *
from .Editor import Editor
from settings.theme import *
from settings.settings import *
from resources import *
import requestsFE

class SplitWidget(QTabWidget):
      def __init__(self, parent=None):
          super(SplitWidget, self).__init__(parent)
          self.setMovable(Settings.TabMovable)
          self.setTabsClosable(True)
          self.tabCloseRequested.connect(self.remove_tab)
          self.setTabShape(QTabWidget.TabShape.Rounded)
          self.setLayoutDirection(Qt.LeftToRight)
          self.setUsesScrollButtons(Settings.TabScrollButtonsVisible)
          self.setIconSize(QtCore.QSize(Settings.TabIconWidth, Settings.TabIconHeight))
          self.setAcceptDrops(True)
          self.setMaximumWidth(800)
          self.setMinimumWidth(300)
      def add_tab(self):
            editor = requestsFE.get(FE_GetEditorWidget)
            a = self.addTab(editor, QIcon("Images/Icons/iconText"), "untitled")
            self.setCurrentIndex(a)
      def newTab(self, widget: QWidget, txt: str):
            self.addTab(widget, txt)
      def remove_tab(self, index):
            if self.count() == 1:
                  self.removeTab(index)
                  self.hide()
            else:
                  self.removeTab(index)