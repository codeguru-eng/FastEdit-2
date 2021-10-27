from PyQt5 import QtCore
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import sys
from settings.settings import *
from settings.theme import *
from data.fileData.folderPath import *
from resources import *
import methods
from Images.iconManager import *

class IconProvider(QFileIconProvider):
      """Custom icons for file explorer"""
      def icon(self, file_path):
            if file_path.isDir():
                  return createIcon(IconFolder)
            else:
                  if (methods.getFileExt(file_path) == ".py" or 
                        methods.getFileExt(file_path) == ".pyi" or 
                        methods.getFileExt(file_path) == ".pyc" or
                        methods.getFileExt(file_path) == ".pyd" or
                        methods.getFileExt(file_path) == ".pyw"
                  ):
                        return createIcon(IconPy)
                  elif (methods.getFileExt(file_path) == ".html" or
                        methods.getFileExt(file_path) == ".htm"
                  ):
                        return createIcon(IconHTML)
                  elif methods.getFileExt(file_path) == ".css":
                        return createIcon(IconCSS)
                  elif methods.getFileExt(file_path) == ".js":
                        return createIcon(IconJS)
                  elif (methods.getFileExt(file_path) == ".fe_settings" or 
                        methods.getFileExt(file_path) == ".json" or 
                        methods.getFileExt(file_path) == ".jsonC"
                  ):
                        return createIcon(IconJSON)
                  elif (methods.getFileExt(file_path) == ".ui" or 
                        methods.getFileExt(file_path) == ".xml"
                  ):
                        return createIcon(IconXML)
                  else:
                        return createIcon(IconText)
            return QFileIconProvider.icon(self, file_path)
class Explorer(QTreeView):
      def __init__(self, parent=None):
          super().__init__(parent)
          self.folderPath = Folder_Path
          #####################
          self.fileModel = QFileSystemModel()
          self.setModel(self.fileModel)
          self.fileModel.setRootPath(QDir.rootPath())
          self.fileModel.setIconProvider(IconProvider())
          self.setSelectionMode(QTreeView.SingleSelection)
          self.header().setSectionResizeMode(QHeaderView.ResizeToContents)
          self.verticalScrollBar().setContextMenuPolicy(Qt.NoContextMenu)
          self.setFrameShape(0)
          self.setAnimated(Settings.ExplorerAnimated)
          self.setIndentation(20)
          self.setHeaderHidden(True)
          self.hideColumn(1)
          self.hideColumn(2)
          self.hideColumn(3)
          self.clearSelection()
          self.setUniformRowHeights(True)
          self.setIconSize(QSize(23,23))
      def setCurrentItem(self, path) -> None:
            index = self.model().index(path)
            scrollValue = self.parent.requestFE(FE_GetVerticalScrollValue, self)
            if index.isValid():
                  self.setCurrentIndex(index)
                  # maintain same scroll position
                  self.verticalScrollBar().setValue(scrollValue)
      def focusInEvent(self, event):
            self.parent.btn7.setText("Explorer")
            super().focusInEvent(event)