import os
from PyQt5 import QtCore
from PyQt5.QtCore import *
from PyQt5.QtGui import QCursor, QIcon
from PyQt5.QtWidgets import *
from .Editor import Editor
from settings.theme import *
from settings.settings import *
import requestsFE
from resources import *

class TabWidget(QTabWidget):
      tabChanged__ = pyqtSignal()
      def __init__(self, parent=None):
          super(TabWidget, self).__init__(parent)
          self.setMovable(Settings.TabMovable)
          self.setTabsClosable(Settings.TabClosable)
          self.setTabShape(QTabWidget.TabShape.Rounded)
          self.setLayoutDirection(Qt.LeftToRight)
          self.setUsesScrollButtons(Settings.TabScrollButtonsVisible)
          self.setIconSize(QtCore.QSize(Settings.TabIconWidth, Settings.TabIconHeight))
          self.setAcceptDrops(True)
          self.setMinimumWidth(500)
          self.__signals()
          self.currentChanged.connect(self.__signal_tab_changed)
      def __signals(self):
            self.tabCloseRequested.connect(self.remove_tab)
            self.tabChanged__.connect(self.__tabChanged)
      def __signal_tab_changed(self):
            self.tabChanged__.emit()
      def __tabChanged(self):
            self.actionSaveunsave()
            self.update_lineCol()
            self.updateFileType()
            self.updateTabWidth()
            self.parent.updateExplorerItem()
            if self.count() < 1:
                self.parent.explorer.clearSelection()
      def updateTabWidth(self):
            self.parent.updateTabWidth()
            pass
      def updateFileType(self):
          self.parent.updateFileType()
          pass
      def update_lineCol(self):
          self.parent.update_lineCol()
          pass
      def actionSaveunsave(self):
          self.parent.update_saveUnsave()
          pass
      def add_tab(self):
            editor = requestsFE.get(FE_GetEditorWidget)
            a = self.addTab(editor, QIcon("Images/Icons/iconText"), "untitled")
            self.setCurrentIndex(a)
      def remove_tab(self, indx):
            z = self.currentIndex()
            if self.widget(indx):
                if self.widget(indx).saved is False:
                    if self.widget(indx).path is None:
                        if self.widget(indx).text() == "" or self.widget(indx).text() == None:
                            self.removeTab(indx)
                            self.parent._updateOutLine()
                            return
                        else:
                            q = QMessageBox()
                            ans = q.question(self.parent, "Warning!", f"Document {self.tabText(indx)} is not saved.\nClose file anyway?"\
                                                        ,QMessageBox.Yes | QMessageBox.No)
                            if (ans== QMessageBox.Yes):
                              self.removeTab(indx)
                              self.parent._updateOutLine()
                            else:
                                return
                    elif self.widget(indx).saved is False:
                        q = QMessageBox()
                        ans = q.question(self.parent, "Warning!", f"Document {self.tabText(indx)} is not saved.\nClose file anyway?"\
                                                        ,QMessageBox.Yes | QMessageBox.No)
                        if (ans== QMessageBox.Yes):
                            if self.parent.previewHTML.urlBar.text() == f"file:///{self.widget(indx).path}":
                                self.parent.previewHTML.closePreview()
                            self.removeTab(indx)
                            self.parent._updateOutLine()
                        else:
                            return
                else:
                    if self.parent.previewHTML.urlBar.text() == f"file:///{self.widget(indx).path}":
                            self.parent.previewHTML.closePreview()
                    self.removeTab(indx)
                    self.parent._updateOutLine()
            else:
                return
      def newTab(self, widget: QWidget, txt: str):
            self.addTab(widget, txt)