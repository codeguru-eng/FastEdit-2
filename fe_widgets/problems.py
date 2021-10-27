from PyQt5.QtWidgets import *
from PyQt5.QtCore import QCoreApplication, QProcess, QSize, Qt
from settings.theme import *
from settings.font import *
from settings.settings import *
from terminal import *
from data.stylesheets import *
import os
import json
import methods


class Problems(QListWidget):
      """Console widget"""
      def __init__(self, parent=None):
            super(Problems, self).__init__(parent)