import PyQt5
from base.widgets.baseWebView import FE_WebViewPage
from settings.theme import *
from .mainWidgets import BrowserWindow, Menu
from .mainWidgets import MainWidget
import os
from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5.Qsci import QsciScintilla
from PyQt5.QtCore import QLine, QProcess, Qt
import sys
import platform
import subprocess
import webbrowser
from resources import *
import methods
import requestsFE
import functools
from PyQt5.QtCore import *
from PyQt5.QtGui import QColor, QCursor, QFont, QKeySequence
from .Editor import Editor
from PyQt5.QtWidgets import (QAction, QApplication, QFileDialog, QHBoxLayout, QHeaderView, QLabel, QLayout, QLineEdit, QMainWindow, QMenu, QMessageBox, QPushButton, QTabBar, QTabWidget, QToolBar, 
                                                            QVBoxLayout, QWidget)
from .TabWidget import TabWidget
from .TabWidget2 import SplitWidget
from .mainWidgets import Button
from .Explorer import Explorer
#from .toolBar import ToolBar
from .console import ConsoleWidget, OpenHTMLInBuiltinBrowser, Output
from data.user.user_data import *
from .signInForm import RegisterForm
from .assistant import Assistant
from .Outline import Outline
from settings.shortcuts import *
from data.stylesheets import *
from settings.settings import *
from settings.editorsettings import *
from settings.recentfiles import *
from settings.recentFolders import *
from Images.iconManager import *
from .changeLog import *
from .dialogs.aboutFE import *
from .dialogs.checkUpdates import *
from fe_shell import *
from fe_shell.commands import *
from symbol_map import scanner
from data.binary_files import *
from data.user.fav_files import *
from base.widgets.baseWebView import *
from PySM import *

appName = methods.getAppName()
writerName = methods.getWriterName()
fullAppName = methods.getFullAppName()
version = methods.getAppVersion()
appType = methods.getAppType()
Os = platform.system()
osVersion = platform.version()
loc = methods.getLocation(os.path.abspath(__file__))
loc = loc.replace("\\", "/")
recentList,recentFolderList,maxRecentList,favFilesList = RecentFileList,RecentFolderList,10,Favourite_Files_List

path = os.path.join(loc, "data/user/user-data.json")
with open(path, "r") as file:
      _text = file.read()
data = json.loads(_text)

path2 = os.path.join(loc, "settings/settings_folder/autoSave.fe_settings")
with open(path2, "r") as file:
      _text2 = file.read()
data2 = json.loads(_text2)

path3 = os.path.join(loc, "data/user/last_opened_files.json")
with open(path3, "r") as file:
      _text3 = file.read()
data3 = json.loads(_text3)

last_opened_files = data3["list"]
last_index        = data3["index"]
CURRENT_THEME     = None

class MainWindow(QMainWindow):
      """
      Main class
      """
      process                 = None
      recentMenu              = None
      recentFolderMenu        = None
      favFilesMenu            = None
      registered              = data["registered"]
      username                = data["user-name"]
      AutoSave                = data2["AutoSave"]

      # signals
      fileReloaded__          = pyqtSignal(str)
      settingsFileOpened__    = pyqtSignal(str)
      settingsFileSaved__     = pyqtSignal(str, QDateTime)
      fileSaved__             = pyqtSignal(str, QDateTime)
      fileOpened__            = pyqtSignal(str)
      themeChanged__          = pyqtSignal(str, QDateTime)



      def __init__(self, parent = None):
            super(MainWindow, self).__init__(parent)
            self.settings = QSettings()
            #################################################
            shell = FE_Shell
            shell.parent = self
            output = Output
            output.parent = self
            self.userInfoDialog = UserDetails()
            self.registerForm = RegisterForm()
            self.registerForm.parent = self
            baseWebView = FE_WebViewPage
            baseWebView.parent = self
            assistant = Assistant
            assistant.parent = self
            editor = Editor
            editor.parent = self
            self.settings = QSettings()
            self.timer = QtCore.QTime()
            self.setWindowTitle(f"SM FastEdit 2 ({self.getUsername()})")
            self.setWindowIcon(createIcon("Images\\txteditor.png"))
            self.setMinimumSize(1500, 700)
            self.widget3 = QWidget()
            layoutW3 = QVBoxLayout(self.widget3)
            layoutW3.setContentsMargins(0,0,0,0)
            splitter3 = QSplitter()
            self.widgetOutline = QWidget()
            layoutOu = QVBoxLayout(self.widgetOutline)
            self.outline = requestsFE.get(FE_GetOutlineWidget)
            self.outline.parent = self
            self.labelO = QLabel("Outline")
            self.labelO.setStyleSheet("border: none;")
            self.labelO.setFixedHeight(35)
            self.widgetOutline.setMaximumWidth(Settings.ExplorerBarMaxWidth)
            layoutOu.setSpacing(0)
            layoutOu.addWidget(self.labelO)
            layoutOu.addWidget(self.outline)
            layoutOu.setContentsMargins(0,0,0,0)
            self.tabWidget = TabWidget()
            self.splitWidget = SplitWidget()
            self.splitWidget.hide()
            self.splitWidget.parent = self
            self.previewHTML = requestsFE.get(FE_GetPreviewWidget)
            self.previewHTML.hide()
            self.previewHTML.parent = self
            splitter3.addWidget(self.tabWidget)
            splitter3.addWidget(self.splitWidget)
            splitter3.addWidget(self.previewHTML)
            splitter3.addWidget(self.widgetOutline)
            layoutW3.addWidget(splitter3)
            splitter3.setContentsMargins(0,0,0,0)
            self.consoleWidget = ConsoleWidget()
            self.consoleWidget.parent = self
            self.output = self.consoleWidget.output
            self.assistant = self.consoleWidget.assistant
            self.assistantM = self.consoleWidget.assistantM
            self.widget2 = MainWidget()
            layout3 = QVBoxLayout(self.widget2)
            splitter1 = QSplitter()
            layout3.addWidget(splitter1)
            splitter1.setOrientation(Qt.Vertical)
            splitter1.addWidget(self.widget3)
            splitter1.addWidget(self.consoleWidget)
            layout3.setAlignment(self.consoleWidget, Qt.AlignBottom)
            layout3.setContentsMargins(0,0,0,0)
            layout3.setSpacing(5)
            self.mainWidget = QWidget()
            self.explorerBar = QWidget()
            self.explorerBar.setMaximumWidth(Settings.ExplorerBarMaxWidth)
            self.explorerBar.setMinimumWidth(Settings.ExplorerBarMinWidth)
            layout = QSplitter(self.mainWidget)
            layout.addWidget(self.explorerBar)
            layout.addWidget(self.widget2)
            layout.setContentsMargins(0,0,0,0)
            layout2 = QVBoxLayout(self.explorerBar)
            # explorer
            self.explorer = Explorer()
            self.explorer.parent = self
            self.explorer.clicked.connect(self.explorerOpenFile)
            layout2.setContentsMargins(0,0,0,0)
            self.explorerBar.hide()
            #################################
            self.labelH = QLabel()
            self.labelH.setStyleSheet("border: none;")
            self.labelH.setStatusTip(self.explorer.folderPath)
            self.labelH.setFixedHeight(35)
            layout2.setSpacing(0)
            layout2.addWidget(self.labelH)
            layout2.addWidget(self.explorer)
            self.setCentralWidget(layout)
            self.tabWidget.parent = self
            self.btn2 = QPushButton()
            self.btn2.clicked.connect(self.saveFile)
            self.btn2.setStatusTip("Click to save file")
            self.btn2.setCursor(QCursor(Qt.PointingHandCursor))
            self.btn2.hide()
            self.btn1 = QPushButton()
            self.btn1.clicked.connect(self.gotolineDLG)
            self.btn1.hide()
            self.btn1.setCursor(QCursor(Qt.PointingHandCursor))
            self.btn3 = QPushButton("Run File")
            self.btn3.clicked.connect(self.runFile)
            self.btn3.setCursor(QCursor(Qt.PointingHandCursor))
            self.btn3.hide()
            self.btn5 = QPushButton(f"Tab Width: 4")
            self.tabwidthMenu = QMenu()
            w1 = self.tabwidthMenu.addAction("1 Space")
            w1.triggered.connect(self.tWidth1)
            w2 = self.tabwidthMenu.addAction("2 Spaces")
            w2.triggered.connect(self.tWidth2)
            w3 = self.tabwidthMenu.addAction("3 Spaces")
            w3.triggered.connect(self.tWidth3)
            w4 = self.tabwidthMenu.addAction("4 Spaces")
            w4.triggered.connect(self.tWidth4)
            w5 = self.tabwidthMenu.addAction("5 Spaces")
            w5.triggered.connect(self.tWidth5)
            w6 = self.tabwidthMenu.addAction("6 Spaces")
            w6.triggered.connect(self.tWidth6)
            w7 = self.tabwidthMenu.addAction("7 Spaces")
            w7.triggered.connect(self.tWidth7)
            w8 = self.tabwidthMenu.addAction("8 Spaces")
            w8.triggered.connect(self.tWidth8)
            self.btn5.setMenu(self.tabwidthMenu)
            self.btn5.setCursor(QCursor(Qt.PointingHandCursor))
            self.btn5.hide()
            self.btn4 = QLabel("Plain Text")
            self.btn4.setCursor(QCursor(Qt.PointingHandCursor))
            self.btn4.hide()
            self.btn7 = QPushButton()
            self.btn7.setCursor(QCursor(Qt.PointingHandCursor))
            self.moreBtn = QPushButton()
            self.moreBtn.setStyleSheet("""
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
            self.moreBtn.setIconSize(QSize(16,16))
            self.moreBtn.setIcon(createIcon("Images\\icon_more.png"))
            self.moreBtn.setCursor(QCursor(Qt.PointingHandCursor))
            self.moreMenu = QMenu()
            hideStatusBar = self.moreMenu.addAction("Hide Status Bar")
            hideStatusBar.triggered.connect(self.hideStatusBar)
            self.moreBtn.setMenu(self.moreMenu)
            self.statusBar().addPermanentWidget(self.btn1)
            self.statusBar().addPermanentWidget(self.btn3)
            self.statusBar().addPermanentWidget(self.btn2) 
            self.statusBar().addPermanentWidget(self.btn5) 
            self.statusBar().addPermanentWidget(self.btn4)
            self.statusBar().addPermanentWidget(self.moreBtn)
            # menus and actions
            self.menuBarMain = self.menuBar()
            fMenu       = self.menuBarMain.addMenu("&File")
            eMenu       = self.menuBarMain.addMenu("&Find")
            vMenu       = self.menuBarMain.addMenu("&View")
            gMenu       = self.menuBarMain.addMenu("&Go")
            sMenu       = self.menuBarMain.addMenu("&Settings")
            rMenu       = self.menuBarMain.addMenu("&Console")
            self.aMenu  = self.menuBarMain.addMenu("&Data")
            hMenu       = self.menuBarMain.addMenu("&Help")
            # file menu
            recentFilesMenu = self.recentFilesMenu()
            recentFoldersMenuM = self.recentFoldersMenuM()
            favFilesMenu = self._favFilesMenu()
            newFile = fMenu.addAction("New File")
            newFile.triggered.connect(self.new_file)
            fMenu.addSeparator()
            openMenu = fMenu.addMenu("Open...")
            openFile = openMenu.addAction("Open File")
            openFile.triggered.connect(self.openFileDialog)
            openMultiple = openMenu.addAction("Open Multiple Files")
            openMultiple.triggered.connect(self.openMultipleFilesDialog)
            fMenu.addMenu(recentFilesMenu)
            fMenu.addMenu(recentFoldersMenuM)
            fMenu.addMenu(favFilesMenu)
            openDeletedFile = openMenu.addAction("Open Last Deleted File")
            openDeletedFile.triggered.connect(self.openLastDeletedFile)
            openFolder = openMenu.addAction("Open Folder")
            openFolder.triggered.connect(self.openDirectoryByDlg)
            fMenu.addSeparator()
            saveFile = fMenu.addAction("Save File")
            saveFile.triggered.connect(self.saveFile)
            saveFileAs = fMenu.addAction("Save As...")
            saveFileAs.triggered.connect(self.saveAs)
            fMenu.addSeparator()
            copyPath = fMenu.addAction("Copy File Path")
            copyPath.triggered.connect(self.copyPath)
            settingMenu = fMenu.addMenu("Settings")
            checkupdates = settingMenu.addAction("Check for Updates...")
            checkupdates.triggered.connect(self.checkUpdateDlg)
            settingMenu.addSeparator()
            theme_Menu = settingMenu.addMenu("Change Theme")
            default1 = theme_Menu.addAction("FastEdit Dark")
            default1.triggered.connect(self.defaultTheme)
            light1 = theme_Menu.addAction("FastEdit Light")
            light1.triggered.connect(self.lightTheme)
            no_Theme = theme_Menu.addAction("FastEdit Classic")
            no_Theme.triggered.connect(self.noTheme)
            settingMenu.addSeparator()
            change_ShortCuts = settingMenu.addAction("Open Shortcuts...")
            change_ShortCuts.triggered.connect(self.openShortcutSettings)
            change_Font = settingMenu.addAction("Open Font...")
            change_Font.triggered.connect(self.openFontSettings)
            open_EditorSettings = settingMenu.addAction("Open Editor Settings...")
            open_EditorSettings.triggered.connect(self.openEditorSettings)
            settingMenu.addSeparator()
            open_Settings = settingMenu.addAction("Open Other Settings...")
            open_Settings.triggered.connect(self.openOtherSettings)
            fMenu.addSeparator()
            self.autoSave = fMenu.addAction("Auto Save")
            self.autoSave.triggered.connect(self.autoSaveTrue)
            fMenu.addSeparator()
            refresh = fMenu.addAction("Reload File...")
            refresh.triggered.connect(self.reloadFile)
            rename_file = fMenu.addAction("Rename File")
            rename_file.triggered.connect(self.rename_file_dlg)
            delete_file = fMenu.addAction("Delete File")
            delete_file.triggered.connect(self.delete_file)
            fMenu.addSeparator()
            closeFile = fMenu.addAction("Close File")
            closeFile.triggered.connect(self.remove_tab)
            closeAllFile = fMenu.addAction("Close All...")
            closeAllFile.triggered.connect(self.close_all)
            closeFolder = fMenu.addAction("Close Folder")
            closeFolder.triggered.connect(self.closeDirectory)
            closeWindow = fMenu.addAction("Close Window")
            closeWindow.triggered.connect(self.close)
            fMenu.addSeparator()
            leave = fMenu.addAction("Leave")
            leave.triggered.connect(self.leave)
            # find menu
            focusfind = eMenu.addAction("Find")
            focusfind.triggered.connect(self.findDLG)
            eMenu.addSeparator()
            replace = eMenu.addAction("Replace")
            replace.triggered.connect(self.replaceDLG)
            replaceAll = eMenu.addAction("Replace All")
            replaceAll.triggered.connect(self.replaceAllDLG)
            # view menu
            self.fullScreen = vMenu.addAction("Full Screen")
            self.fullScreen.triggered.connect(self.full_screen)
            self.focusMode = vMenu.addAction("Toggle Focus Mode")
            self.focusMode.triggered.connect(self.focus_mode)
            minimize = vMenu.addAction("Minimize")
            minimize.triggered.connect(self.showMinimized)
            maximize = vMenu.addAction("Maximize")
            maximize.triggered.connect(self.showMaximized)
            vMenu.addSeparator()
            self.showStatusBar = vMenu.addAction("Toggle Status Bar")
            self.showStatusBar.triggered.connect(self.toggle_status_bar)
            showEditor = vMenu.addAction("Toggle Editor Area")
            showEditor.triggered.connect(self.toggle_editor)
            toggleExplorer = vMenu.addAction("Toggle Explorer")
            toggleExplorer.triggered.connect(self.toggle_explorer)
            toggle_console = vMenu.addAction("Toggle Console Area")
            toggle_console.triggered.connect(self.toggleConsoleWidget)
            vMenu.addSeparator()
            readOnly = vMenu.addAction("Toggle Read Only")
            readOnly.triggered.connect(self.toggleReadOnly)
            vMenu.addSeparator()
            wrapMenu = vMenu.addMenu("Word Wrap")
            yesWrap = wrapMenu.addAction("Word Wrap: True")
            yesWrap.triggered.connect(self.yes_wrap_mode)
            noWrap = wrapMenu.addAction("Word Wrap: False")
            noWrap.triggered.connect(self.no_wrap_mode)
            wspaceMenu = vMenu.addMenu("White Spaces")
            wSpaceV = wspaceMenu.addAction("Visible")
            wSpaceV.triggered.connect(self.wSpace_visible)
            wSpaceIV = wspaceMenu.addAction("Invisible")
            wSpaceIV.triggered.connect(self.wSpace_invisible)
            vMenu.addSeparator()
            zoomIn = vMenu.addAction("ZoomIn")
            zoomIn.triggered.connect(self.zoomIn)
            zoomOut = vMenu.addAction("ZoomOut")
            zoomOut.triggered.connect(self.zoomOut)
            reset = vMenu.addAction("Reset Zoom")
            reset.triggered.connect(self.resetZoom)
            # go menu
            goBack = gMenu.addAction("Go Back")
            goBack.triggered.connect(self.goBackTab)
            goForward = gMenu.addAction("Go Forward")
            goForward.triggered.connect(self.goForwardTab)
            gMenu.addSeparator()
            goToLine = gMenu.addAction("Go to Line")
            goToLine.triggered.connect(self.gotolineDLG)
            gMenu.addSeparator()
            openByPath = gMenu.addAction("Go to File/Folder")
            openByPath.triggered.connect(self.openFileByPathDlg)
            goToTerminal = gMenu.addAction("Go to Terminal")
            goToTerminal.triggered.connect(self.goToTerminal)
            open_shell = gMenu.addAction("Go to Shell")
            open_shell.triggered.connect(self.open_shell)
            # setting menu
            check_updates = sMenu.addAction("Check for Updates...")
            check_updates.triggered.connect(self.checkUpdateDlg)
            sMenu.addSeparator()
            themeMenu = sMenu.addMenu("Change Theme")
            default = themeMenu.addAction("FastEdit Dark")
            default.triggered.connect(self.defaultTheme)
            light = themeMenu.addAction("FastEdit Light")
            light.triggered.connect(self.lightTheme)
            noTheme = themeMenu.addAction("FastEdit Classic")
            noTheme.triggered.connect(self.noTheme)
            sMenu.addSeparator()
            changeShortCuts = sMenu.addAction("Open Shortcuts...")
            changeShortCuts.triggered.connect(self.openShortcutSettings)
            changeFont = sMenu.addAction("Open Font...")
            changeFont.triggered.connect(self.openFontSettings)
            openEditorSettings = sMenu.addAction("Open Editor Settings...")
            openEditorSettings.triggered.connect(self.openEditorSettings)
            openIconManager = sMenu.addAction("Open Icon Manager")
            openIconManager.triggered.connect(self.openIconManager)
            openSyntaxColor = sMenu.addAction("Customize Syntax Colouring")
            openSyntaxColor.triggered.connect(self.openSyntaxColoringSettings)
            sMenu.addSeparator()
            openSettings = sMenu.addAction("Open Other Settings...")
            openSettings.triggered.connect(self.openOtherSettings)
            sMenu.addSeparator()
            customAutocompletionItems = sMenu.addAction("Add Autocompletion Items")
            customAutocompletionItems.triggered.connect(self.openAddCompletions)
            addApiFiles = sMenu.addAction("Add Api Files")
            addApiFiles.triggered.connect(self.addApiFile)
            sMenu.addSeparator()
            reloadSettings = sMenu.addAction("Reload with new Settings")
            reloadSettings.triggered.connect(self.reloadSettings)
            # run menu
            run = rMenu.addAction("Run File...")
            run.triggered.connect(self.runFile)
            restart = rMenu.addAction("Restart")
            restart.triggered.connect(self.restartFile)
            closeRun = rMenu.addAction("Stop...")
            closeRun.triggered.connect(self.closeRun)
            rMenu.addSeparator()
            new_console = rMenu.addAction("New/Clear Output")
            new_console.triggered.connect(self.newConsole)
            show_console = rMenu.addAction("Toggle Console")
            show_console.triggered.connect(self.toggleConsole)
            rMenu.addSeparator()
            config_console = rMenu.addAction("Configure Console")
            config_console.triggered.connect(self.openConsoleSettings)
            # data menu
            self.registerItem = self.aMenu.addAction("Register")
            self.registerItem.triggered.connect(self.showRegisterForm)
            self.unregisteract = self.aMenu.addAction("Unregister")
            self.unregisteract.triggered.connect(self.unregisterdlg)
            self.userDetails = self.aMenu.addAction("Open User Data")
            self.userDetails.triggered.connect(self.showUserDetails)
            # help menu
            goToAssistant = hMenu.addAction("Ask from Assistant")
            goToAssistant.triggered.connect(self.gotoAssistant)
            hMenu.addSeparator()
            changelogs = hMenu.addAction("Change log...")
            changelogs.triggered.connect(self.showChangeLog)
            sendReport = hMenu.addAction("Send Report")
            sendReport.triggered.connect(self.sendReport)
            about = hMenu.addAction("About FastEdit")
            about.triggered.connect(self.aboutDLG)
            ######### Shortcuts #############
            newFile.setShortcut(ShortcutKeys.NewFile)
            openFile.setShortcut(ShortcutKeys.OpenFile)
            openFolder.setShortcut(ShortcutKeys.OpenFolder)
            saveFile.setShortcut(ShortcutKeys.SaveFile)
            saveFileAs.setShortcut(ShortcutKeys.SaveFileAs)
            refresh.setShortcut(ShortcutKeys.ReloadFile)
            copyPath.setShortcut(ShortcutKeys.CopyPath)
            rename_file.setShortcut(ShortcutKeys.RenameFile)
            delete_file.setShortcut(ShortcutKeys.DeleteFile)
            closeFile.setShortcut(ShortcutKeys.CloseFile)
            closeAllFile.setShortcut(ShortcutKeys.CloseAll)
            closeFolder.setShortcut(ShortcutKeys.CloseFolder)
            closeWindow.setShortcut(ShortcutKeys.CloseWindow)
            focusfind.setShortcut(ShortcutKeys.Find)
            replace.setShortcut(ShortcutKeys.ReplaceOne)
            replaceAll.setShortcut(ShortcutKeys.ReplaceAll)
            self.fullScreen.setShortcut(ShortcutKeys.ToggleFullScreen)
            self.focusMode.setShortcut(ShortcutKeys.ToggleFocusMode)
            zoomIn.setShortcut(ShortcutKeys.ZoomIn)
            zoomOut.setShortcut(ShortcutKeys.ZoomOut)
            readOnly.setShortcut(ShortcutKeys.ToggleReadOnly)
            toggle_console.setShortcut(ShortcutKeys.ToggleConsoleArea)
            showEditor.setShortcut(ShortcutKeys.ToggleEditorArea)
            toggleExplorer.setShortcut(ShortcutKeys.ToggleExplorer)
            self.showStatusBar.setShortcut(ShortcutKeys.ToggleStatusBar)
            goToLine.setShortcut(ShortcutKeys.GoToLine)
            goToTerminal.setShortcut(ShortcutKeys.GoToTerminal)
            open_shell.setShortcut(ShortcutKeys.GoToShell)
            openByPath.setShortcut(ShortcutKeys.GoToFileFolder)
            run.setShortcut(ShortcutKeys.RunFile)
            closeRun.setShortcut(ShortcutKeys.StopRun)
            restart.setShortcut(ShortcutKeys.ReloadRun)
            about.setShortcut(ShortcutKeys.About)
            goToAssistant.setShortcut(ShortcutKeys.AskFromAssistant)
            #################################
            self.onStart()
            self.__signals()
      def open_shell(self):
            self.consoleWidget.show()
            self.consoleWidget.setCurrentIndex(3)
            self.consoleWidget.widget(3).commandArea.setFocus()
      def __signals(self):
            self.fileSaved__.connect(self.file_saved)
            self.settingsFileSaved__.connect(self.settingsFileSaved)
            self.themeChanged__.connect(self.themeChanged)
      def themeChanged(self, theme, time):
            info(f"Theme changed to {theme}")
            time = time.toString("hh:mm")
            self.consoleWidget.widget(3).showOutput(f"Theme changed to {theme} at {time}")
      def updateExplorerItem(self):
            if self.tabWidget.currentWidget():
                  if self.tabWidget.currentWidget().path:
                        self.explorer.setCurrentItem(self.tabWidget.currentWidget().path)
      def settingsFileSaved(self, file, time):
            time = time.toString("hh:mm:ss")
            self.statusBar().showMessage(f"Applying Settings...", 2000)
            self.reloadSettings()
      def file_saved(self, file, time):
            self.updateExplorerItem()
            time = time.toString("hh:mm:ss")
            self.statusBar().showMessage(f"Saved {file}, at {time}", 2000)
      def requestFE(self, request: int, value1=None, value2=None,value3=None,value4=None):
            if request == 1:
                  self.openFile(value1)
            elif request == 2:
                  self.openDirectory(value1)
            elif request == 3:
                  if self.tabWidget.currentWidget():
                        return self.tabWidget.currentWidget().text()
            elif request == 4:
                  return (self.width(), self.height())
            elif request == 5:
                  if self.tabWidget.currentWidget():
                        return self.tabWidget.currentWidget().getCursorPosition()
            elif request == 6:
                  if self.tabWidget.currentWidget():
                        return self.tabWidget.currentWidget().getCursorPosition()[0]
            elif request == 7:
                  if self.tabWidget.currentWidget():
                        return self.tabWidget.currentWidget().getCursorPosition()[1]
            elif request == 16:
                  self.close()
                  subprocess.Popen(["python", "runApp.py"])
            elif request == 18:
                  if self.registered is True:
                        return self.username
                  else:
                        return "Unregistered"
            elif request == 8:
                  if self.tabWidget.currentWidget():
                        self.tabWidget.currentWidget().setText(value1)
            elif request == 9:
                  if self.tabWidget.currentWidget():
                        self.tabWidget.currentWidget().setCursorPosition(value1)
            elif request == 10:
                  self.tabWidget.remove_tab(value1)
            elif request == 11:
                  if self.tabWidget.currentWidget():
                        self.tabWidget.currentWidget().setHighlightingFor(value1)
            elif request == 12:
                  if self.tabWidget.currentWidget() is None:
                        return
                  self.tabWidget.currentWidget().setTabWidth(value1)
                  self.btn5.setText(f"Tab Width: {value1}")
            elif request == 13:
                  self.addRecentLists(value1)
            elif request == 14:
                  self.addRecentFolder(value1)
            elif request == 15:
                  subprocess.Popen(["python", value1])
            elif request == 17:
                  return value1.verticalScrollBar().value()  
            elif request == 19:
                  return sys.version_info[0]
            elif request == 20:
                  # close all programs
                  QApplication.instance().closeAllWindows()
      def openInSplitView(self, path):
            editor = self.tabWidget.currentWidget()
            if editor:
                  if editor.path:
                        self.openFileInSplitView(path)
      def reloadSettings(self):
            """After saving changes in fe_settings file reopen the application with new settings."""
            self.requestFE(FE_RestartApp)
      def checkAutoSave(self):
            if self.AutoSave is True:
                  self.autoSave.setText("Auto Save (On)")
            else:
                  self.autoSave.setText("Auto Save (Off)")
      def setAutoSave(self):
            if self.AutoSave is True:
                  self.saveFile()
                  self.autoSave.setText("Auto Save (On)")
                  self.statusBar().showMessage("", 5000)
      def autoSaveTrue(self):
            if self.AutoSave is False:
                  self.AutoSave = True
                  file = os.path.join(loc, "settings/settings_folder/autoSave.fe_settings")
                  methods.updateJson(file, "AutoSave", self.AutoSave)
                  self.autoSave.setText("Auto Save (True)")
            elif self.AutoSave is True:
                  self.AutoSave = False
                  file = os.path.join(loc, "settings/settings_folder/autoSave.fe_settings")
                  methods.updateJson(file, "AutoSave", self.AutoSave)
                  self.autoSave.setText("Auto Save (False)")
      def goToTerminal(self):
            self.consoleWidget.show()
            self.consoleWidget.setCurrentIndex(2)
            self.consoleWidget.widget(2).commandArea.setFocus()
            self.consoleWidget.widget(2).outputArea.moveCursor(QTextCursor.EndOfLine)
            self.consoleWidget.widget(2).outputArea.verticalScrollBar().setValue(self.consoleWidget.widget(2).outputArea.verticalScrollBar().maximum())
      def updateTabWidth(self):
            if self.tabWidget.currentWidget() is None:
                  return
            self.btn5.setText(f"Tab Width: {self.tabWidget.currentWidget().tabWidth()}")
      def tWidth1(self):
            self.requestFE(FE_SetTabWidth, 1)
      def tWidth2(self):
            self.requestFE(FE_SetTabWidth, 2)
      def tWidth3(self):
            self.requestFE(FE_SetTabWidth, 3)
      def tWidth4(self):
            self.requestFE(FE_SetTabWidth, 4)
      def tWidth5(self):
            self.requestFE(FE_SetTabWidth, 5)
      def tWidth6(self):
            self.requestFE(FE_SetTabWidth, 6)
      def tWidth7(self):
            self.requestFE(FE_SetTabWidth, 7)
      def tWidth8(self):
            self.requestFE(FE_SetTabWidth, 8)

      def updateOutline(self, text, filepath):
            symbols, symbols_simplified = scanner.obtain_symbols(text, simple=True)
            self.outline.symbols_index = sorted(symbols_simplified.keys())
            self.outline.update_symbols_tree(symbols, filepath)
      def sendReport(self):
            self.mainDlg = QWebEngineView()
            self.mainDlg.setWindowTitle("Send Report")
            self.setWindowIcon(createIcon("Images/txteditor.png"))
            path = os.path.join(loc, "fe_widgets/web/sendEmail.html")
            self.mainDlg.setFixedSize(400,400)
            self.mainDlg.load(QUrl(path))
            self.mainDlg.show() 
      def clearUserData(self):
            """Clear all user data."""
            path = os.path.join(loc, "data/fileData/folderPath.json")
            with open(path, "r") as file:
                  _text = file.read()
            dataF = json.loads(_text)
            self.clearRecentList()
            self.clearRecentFolders()
            path = os.path.join(loc, "data/fileData/folderPath.json")
            methods.updateJson(path, "path", "")
            self.explorer.folderPath = dataF["path"]
            self.defaultTheme()
      def updateMarginWidth(self):
            if self.tabWidget.currentWidget():
                  self.tabWidget.currentWidget().updateMarginWidth()
      def setCompleterFor(self, a1: str) -> list[str]:
            if a1 == "openByPathCompleter":
                  list1 = recentList + recentFolderList
                  return list1
      def onStart(self):
            """Method to open application with same settings."""
            self.setTheme()
            self.consoleWidget.hide()
            self.updateRecentLists()
            self.updateFavFiles()
            self.updateRecentFolders()
            self.openDirectoryOnStart()
            self.checkIfSignedIn()
            self.setRegistered()
            self.widgetOutline.hide()
            self.updateWindowTitle()
            self.updateTabWidth()
            self.checkAutoSave()
            self.openMultipleFiles(last_opened_files)
            self.tabWidget.setCurrentIndex(last_index)
      def showUserDetails(self):
            if self.registered is False:
                  return
            elif self.registered is True:
                  self.qDlg = QWidget()
                  self.qDlg.setStyleSheet("background: #555;margin: 0")
                  self.qDlg.setWindowTitle("Show User Details - SM FastEdit")
                  self.qDlg.setWindowIcon(createIcon("Images\\txteditor.png"))
                  layout = QHBoxLayout(self.qDlg)
                  self.passwordFieldCh = QLineEdit()
                  self.passwordFieldCh.setStyleSheet("background: #555;padding: 12px 20px;border: none;font-size: 18px;color: #fff;selection-background-color: rgba(255,255,255,0.2);")
                  self.passwordFieldCh.setPlaceholderText("Please tell password...")
                  self.passwordFieldCh.returnPressed.connect(self.showDetailsOfUser)
                  layout.addWidget(self.passwordFieldCh)
                  self.qDlg.show()
      def showDetailsOfUser(self):
            if self.passwordFieldCh.text() == data["password"]:
                  self.userInfoDialog.show()
                  self.qDlg.close()
            else:
                  self.wrongPassowrdDlg()
                  self.qDlg.close()
      def wrongPassowrdDlg(self):
            self.q = QMessageBox()
            self.q.setWindowFlags(Qt.SplashScreen)
            ans = self.q.question(self, "Warning!", f"Wrong password!"\
                                    ,QMessageBox.Ok)
            if (ans == QMessageBox.Ok):
                  self.q.close()
      def setRegistered(self):
            if self.registered is False:
                  self.registerItem.setText("Register")
                  self.unregisteract.setDisabled(True)
                  self.username = data["user-name"]
                  self.userDetails.setDisabled(True)
            elif self.registered is True:
                  self.registerItem.setDisabled(True)
                  return
      def getUsername(self):
            return self.requestFE(FE_GetUserName)
      def checkIfSignedIn(self):
            if self.registered is False:
                  self.registerItem.setText("Register")
                  self.unregisteract.setDisabled(True)
            elif self.registered is True:
                  self.registerItem.setDisabled(True)
                  return
      def unregisterdlg(self):
            if self.registered is False:
                  return
            elif self.registered is True:
                  self.qDlg = QWidget()
                  self.qDlg.setWindowTitle("Unregister - SM FastEdit")
                  self.qDlg.setWindowIcon(createIcon("Images\\txteditor.png"))
                  self.qDlg.setStyleSheet("background: #555;margin: 0")
                  layout = QHBoxLayout(self.qDlg)
                  self.passwordFieldCh = QLineEdit()
                  self.passwordFieldCh.setStyleSheet("background: #555;padding: 12px 20px;border: none;font-size: 18px;color: #fff;selection-background-color: rgba(255,255,255,0.2);")
                  self.passwordFieldCh.setPlaceholderText("Please tell password...")
                  self.passwordFieldCh.returnPressed.connect(self.unregister)
                  layout.addWidget(self.passwordFieldCh)
                  self.qDlg.show()
      def unregister(self):
            if self.passwordFieldCh.text() == data["password"]:
                  q = QMessageBox()
                  ans = q.question(self, "Warning!", f"Do you really want to unregister from SM FastEdit?"\
                                    ,QMessageBox.No | QMessageBox.Yes)
                  if (ans== QMessageBox.No):
                        return
                  methods.updateJson(path, "user-name", "")
                  methods.updateJson(path, "user-email", "")
                  methods.updateJson(path, "password", "")
                  methods.updateJson(path, "phone", "")
                  self.registered = False
                  self.username = ""
                  methods.updateJson(path, "registered", self.registered)
                  self.clearUserData()
                  self.reloadSettings()
                  self.qDlg.close()
            else:
                  self.wrongPassowrdDlg()
                  self.qDlg.close()
      def showRegisterForm(self):
            self.registerForm.show()
            self.checkIfSignedIn()
      def gotoAssistant(self):
            self.consoleWidget.show()
            self.consoleWidget.setCurrentIndex(1)
            self.consoleWidget.askField.setFocus()
      def updateLexer(self, filename):
            file_ext = methods.getFileExt(filename)
            if file_ext == ".html" or file_ext == ".htm":
                  edi = self.tabWidget.currentWidget()
                  edi.setHighlightingFor("html")
                  index = self.tabWidget.currentIndex()
                  self.tabWidget.setTabIcon(index, createIcon(IconHTML))
            elif file_ext == ".md":
                  edi = self.tabWidget.currentWidget()
                  edi.setHighlightingFor("text")
                  index = self.tabWidget.currentIndex()
                  self.tabWidget.setTabIcon(index, createIcon(IconText))
            elif file_ext == ".css" or file_ext == ".qss":
                  edi = self.tabWidget.currentWidget()
                  edi.setHighlightingFor("css")
                  index = self.tabWidget.currentIndex()
                  self.tabWidget.setTabIcon(index, createIcon(IconCSS))
            elif file_ext == ".js":
                  edi = self.tabWidget.currentWidget()
                  edi.setHighlightingFor("js")
                  index = self.tabWidget.currentIndex()
                  self.tabWidget.setTabIcon(index, createIcon(IconJS))
            elif file_ext == ".py" or file_ext == ".pyi" or file_ext == ".pyc" or file_ext == ".pyd" or file_ext == ".pyw":
                  edi = self.tabWidget.currentWidget()
                  edi.setHighlightingFor("py")
                  index = self.tabWidget.currentIndex()
                  self.tabWidget.setTabIcon(index, createIcon(IconPy))
            elif file_ext == ".json":
                  edi = self.tabWidget.currentWidget()
                  edi.setHighlightingFor("json")
                  index = self.tabWidget.currentIndex()
                  self.tabWidget.setTabIcon(index, createIcon(IconJSON))
            elif file_ext == ".xml" or file_ext == ".ui":
                  edi = self.tabWidget.currentWidget()
                  edi.setHighlightingFor("xml")
                  index = self.tabWidget.currentIndex()
                  self.tabWidget.setTabIcon(index, createIcon(IconXML))
            elif file_ext == ".fe_settings":
                  edi = self.tabWidget.currentWidget()
                  edi.setHighlightingFor("settings")
                  index = self.tabWidget.currentIndex()
                  self.tabWidget.setTabIcon(index, createIcon(IconJSON))
            elif file_ext == ".md":
                  edi = self.tabWidget.currentWidget()
                  edi.setHighlightingFor("md")
                  index = self.tabWidget.currentIndex()
                  self.tabWidget.setTabIcon(index, createIcon(IconHTML))
            else: 
                  edi = self.tabWidget.currentWidget()
                  edi.setHighlightingFor("text")
                  index = self.tabWidget.currentIndex()
                  self.tabWidget.setTabIcon(index, createIcon(IconText))
      def updateLexerForSplitView(self, filename):
            file_ext = methods.getFileExt(filename)
            if file_ext == ".html" or file_ext == ".htm":
                  edi = self.splitWidget.currentWidget()
                  edi.setHighlightingFor("html")
                  index = self.splitWidget.currentIndex()
                  self.splitWidget.setTabIcon(index, createIcon(IconHTML))
            elif file_ext == ".md":
                  edi = self.splitWidget.currentWidget()
                  edi.setHighlightingFor("text")
                  index = self.splitWidget.currentIndex()
                  self.splitWidget.setTabIcon(index, createIcon(IconText))
            elif file_ext == ".css" or file_ext == ".qss":
                  edi = self.splitWidget.currentWidget()
                  edi.setHighlightingFor("css")
                  index = self.splitWidget.currentIndex()
                  self.splitWidget.setTabIcon(index, createIcon(IconCSS))
            elif file_ext == ".js":
                  edi = self.splitWidget.currentWidget()
                  edi.setHighlightingFor("js")
                  index = self.splitWidget.currentIndex()
                  self.splitWidget.setTabIcon(index, createIcon(IconJS))
            elif file_ext == ".py" or file_ext == ".pyi" or file_ext == ".pyc" or file_ext == ".pyd" or file_ext == ".pyw":
                  edi = self.splitWidget.currentWidget()
                  edi.setHighlightingFor("py")
                  index = self.splitWidget.currentIndex()
                  self.splitWidget.setTabIcon(index, createIcon(IconPy))
            elif file_ext == ".json":
                  edi = self.splitWidget.currentWidget()
                  edi.setHighlightingFor("json")
                  index = self.splitWidget.currentIndex()
                  self.splitWidget.setTabIcon(index, createIcon(IconJSON))
            elif file_ext == ".xml" or file_ext == ".ui":
                  edi = self.splitWidget.currentWidget()
                  edi.setHighlightingFor("xml")
                  index = self.splitWidget.currentIndex()
                  self.splitWidget.setTabIcon(index, createIcon(IconXML))
            elif file_ext == ".fe_settings":
                  edi = self.splitWidget.currentWidget()
                  edi.setHighlightingFor("settings")
                  index = self.splitWidget.currentIndex()
                  self.splitWidget.setTabIcon(index, createIcon(IconJSON))
            elif file_ext == ".md":
                  edi = self.splitWidget.currentWidget()
                  edi.setHighlightingFor("md")
                  index = self.splitWidget.currentIndex()
                  self.splitWidget.setTabIcon(index, createIcon(IconHTML))
            else: 
                  edi = self.splitWidget.currentWidget()
                  edi.setHighlightingFor("text")
                  index = self.splitWidget.currentIndex()
                  self.splitWidget.setTabIcon(index, createIcon(IconText))
      def openFileByPathDlg(self):
            self.openByPathDlg = QWidget()
            self.openByPathDlg.setWindowFlags(Qt.SplashScreen)
            self.openByPathDlg.setStyleSheet("background: #555;")
            self.openByPathDlg.setFixedSize(600,60)
            list1 = self.setCompleterFor("openByPathCompleter")
            completer = QCompleter(list1)
            completer.popup().setObjectName("completer")
            completer.popup().setStyleSheet(completerStyle)
            completer.setCaseSensitivity(Qt.CaseInsensitive)
            layout = QVBoxLayout(self.openByPathDlg)
            layout.setContentsMargins(0,0,0,0)
            self.pathfield = QLineEdit()
            self.pathfield.setCompleter(completer)
            if self.explorer.folderPath:
                  self.pathfield.setText(f"{self.explorer.folderPath}/")
            self.pathfield.setStyleSheet("padding: 12px 20px;border: none;font-size: 18px;color: #fff;selection-background-color: rgba(255,255,255,0.2);")
            self.pathfield.returnPressed.connect(self.openByPath)
            layout.addWidget(self.pathfield)
            self.openByPathDlg.show()
      def openByPath(self):
            """Similar to Sublime Text's go to anything."""
            _text = self.pathfield.text()
            _text = _text.replace("\\","/")
            if os.path.isdir(_text) is True:
                  self.openDirectory(_text)
                  self.openByPathDlg.close()
            elif os.path.isfile(_text) is True:
                  self.openFile(_text)
                  self.openByPathDlg.close()
            else:
                  self.statusBar().showMessage("Invalid file or folder name!",2000)
      def recentFilesMenu(self):
            self.recentMenu = Menu("Open Recent Files...")
            clearRecent = self.recentMenu.addAction("Clear Recent Files")
            clearRecent.triggered.connect(self.clearRecentList)
            self.recentMenu.addSeparator()
            return self.recentMenu
      def _favFilesMenu(self):
            self.favFilesMenu = Menu("Open Favourite Files...")
            clearRecent = self.favFilesMenu.addAction("Clear Favourite Files")
            clearRecent.triggered.connect(self.clearFavFilesList)
            self.favFilesMenu.addSeparator()
            return self.favFilesMenu
      def recentFoldersMenuM(self):
            self.recentFolderMenu = Menu("Open Recent Folders...")
            clearRecentFolder = self.recentFolderMenu.addAction("Clear Recent Folders")
            clearRecentFolder.triggered.connect(self.clearRecentFolders)
            self.recentFolderMenu.addSeparator()
            return self.recentFolderMenu
      def updateRecentLists(self):
            def new_file_function(file):
                  try:
                        self.openFile(file)
                        self.tabWidget.currentWidget().setFocus()
                  except:
                        pass
            for recent_file in reversed(recentList):
                  recent_file_name = recent_file
                  if len(recent_file_name) > 150:
                        recent_file_name = "...{}".format(os.path.splitdrive(recent_file)[1][-150:])
                  new_file_action = QAction(recent_file_name, self.recentMenu)
                  temp_function = functools.partial(new_file_function, recent_file)
                  new_file_action.triggered.connect(temp_function)
                  self.recentMenu.addAction(new_file_action)
      def updateRecentFolders(self):
            def new_folder_function(folderpath):
                  try:
                        self.openDirectory(folderpath)
                  except:
                        pass
            for recent_folder in reversed(recentFolderList):
                  recent_folder_name = recent_folder
                  if len(recent_folder_name) > 150:
                        recent_folder_name = "...{}".format(os.path.splitdrive(recent_folder)[1][-150:])
                  new_folder_action = QAction(recent_folder_name, self.recentFolderMenu)
                  temp_function = functools.partial(new_folder_function, recent_folder)
                  new_folder_action.triggered.connect(temp_function)
                  self.recentFolderMenu.addAction(new_folder_action)
      def updateFavFiles(self):
            def new_file_function(file):
                  try:
                        self.openFile(file)
                  except:
                        pass
            for file in favFilesList:
                  name = file
                  if len(name) > 150:
                        name = "...{}".format(os.path.splitdrive(file)[1][-150:])
                  new_action = QAction(name, self.favFilesMenu)
                  temp_function = functools.partial(new_file_function, file)
                  new_action.triggered.connect(temp_function)
                  self.favFilesMenu.addAction(new_action)
      def clearRecentFolders(self):
            recentFolderList.clear()
            filepath = os.path.join(loc, "settings\\recentFolders.json")
            jsonFile = open(filepath, "r")
            data = json.load(jsonFile) 
            jsonFile.close()
            tmp = data
            data.clear()
            recentFolderList.clear()
            self.recentFolderMenu.clear()
            jsonFile = open(filepath, "w+")
            jsonFile.write(json.dumps(data))
            jsonFile.close()
      def clearRecentList(self):
            recentList.clear()
            filepath = os.path.join(loc, "settings\\recentfiles.json")
            jsonFile = open(filepath, "r")
            data = json.load(jsonFile) 
            jsonFile.close()
            tmp = data
            data["list"].clear()
            recentList.clear()
            self.recentMenu.clear()
            jsonFile = open(filepath, "w+")
            jsonFile.write(json.dumps(data))
            jsonFile.close()
      def addRecentLists(self, new_file):
            recentList.clear() # clear old list
            if platform == "Windows":
                  new_file = new_file.replace("\\", "/")
            filepath = os.path.join(loc, "settings\\recentfiles.json")
            jsonFile = open(filepath, "r")
            data = json.load(jsonFile)
            jsonFile.close()
            tmp = data["list"]
            if new_file not in data["list"]:
                  if len(data["list"]) > maxRecentList:
                        data["list"].pop(0)
                  data["list"].append(new_file)
                  for i in data["list"]:
                        recentList.clear()
                        recentList.append(i)
            jsonFile = open(filepath, "w+")
            jsonFile.write(json.dumps(data))
            jsonFile.close()
      def addFavFilesList(self, new_file):
            favFilesList.clear()
            if platform == "Windows":
                  new_file = new_file.replace("\\", "/")
            filepath = os.path.join(loc, "data\\user\\fav_files.json")
            jsonFile = open(filepath, "r")
            data = json.load(jsonFile)
            jsonFile.close()
            tmp = data["list"]
            if new_file not in data["list"]:
                  if len(data["list"]) > maxRecentList:
                        self.statusBar().showMessage("Maximum favourite files reached!", 2000)
                        return
                  data["list"].append(new_file)
                  for i in data["list"]:
                        favFilesList.clear()
                        favFilesList.append(i)
            jsonFile = open(filepath, "w+")
            jsonFile.write(json.dumps(data))
            jsonFile.close()
      def removeFromFavFilesList(self, file_to_remove):
            favFilesList.clear()
            if platform == "Windows":
                  file_to_remove = file_to_remove.replace("\\", "/")
            filepath = os.path.join(loc, "data\\user\\fav_files.json")
            jsonFile = open(filepath, "r")
            data = json.load(jsonFile)
            jsonFile.close()
            tmp = data["list"]
            if file_to_remove in data["list"]:
                  data["list"].remove(file_to_remove)
                  self.updateFavFiles()
            jsonFile = open(filepath, "w+")
            jsonFile.write(json.dumps(data))
            jsonFile.close()
      def clearFavFilesList(self):
            favFilesList.clear()
            filepath = os.path.join(loc, "data\\user\\fav_files.json")
            jsonFile = open(filepath, "r")
            data = json.load(jsonFile) 
            jsonFile.close()
            tmp = data
            data["list"].clear()
            favFilesList.clear()
            self.favFilesMenu.clear()
            jsonFile = open(filepath, "w+")
            jsonFile.write(json.dumps(data))
            jsonFile.close()
      def addRecentFolder(self, new_folder):
            recentFolderList.clear() # clear old list
            if platform == "Windows":
                  new_folder = new_folder.replace("\\", "/")
            while len(recentFolderList) > maxRecentList:
                  recentFolderList.pop(0)
            filepath = os.path.join(loc, "settings\\recentFolders.json")
            jsonFile = open(filepath, "r")
            data = json.load(jsonFile)
            jsonFile.close()
            tmp = data
            if len(data) > maxRecentList:
                  data.pop(0)
            if new_folder not in reversed(data):
                  data.append(new_folder)
                  for i in data:
                        recentFolderList.clear()
                        recentFolderList.append(i)
            jsonFile = open(filepath, "w+")
            jsonFile.write(json.dumps(data))
            jsonFile.close()
      def updateFileType(self):
            if not self.tabWidget.currentWidget():
                  return
            editor = self.tabWidget.currentWidget()
            if editor.path:
                  if editor.isHTMLFile():
                        self.btn4.setText("HTML")
                  elif editor.isMarkDownFile():
                        self.btn4.setText("Markdown")
                  elif editor.isCSSFile():
                        self.btn4.setText("CSS") 
                  elif editor.isJavaScriptFile():
                        self.btn4.setText("JavaScript") 
                  elif editor.isPythonFile():
                        self.btn4.setText("Python") 
                  elif editor.isJSONFile() or editor.isSettingFile():
                        self.btn4.setText("JSON")
                  elif editor.isCTypeFile():
                        self.btn4.setText("C/C++")
                  elif editor.isXMLFile():
                        self.btn4.setText("XML")
                  elif editor.isCSharpFile():
                        self.btn4.setText("C-Sharp")
                  elif editor.isJavaFile():
                        self.btn4.setText("Java")
                  else:
                        self.btn4.setText("Plain Text")
            else:
                  self.btn4.setText("Plain Text")
      def openLastDeletedFile(self):
            """It will open log.txt file. In which last deleted file's text is saved."""
            path = os.path.join(loc, "data/user/last_deleted_file.txt")
            self.openFile(path)
      def checkUpdateDlg(self):
            if version == "2.0.0":
                  updateDialog = no(self)
                  updateDialog.show()
            else:
                  updateDia = yes(self)
                  updateDia.show()
      def copyPath(self):
            editor = self.tabWidget.currentWidget()
            if editor:
                  if editor.path:
                        self.copyPathDailog = QWidget()
                        self.copyPathDailog.setWindowFlag(Qt.SplashScreen)
                        self.copyPathDailog.setStyleSheet("background: #333;border: none;")
                        layout = QHBoxLayout(self.copyPathDailog)
                        layout.setContentsMargins(0,0,0,0)
                        layout.setSpacing(0)
                        self.lineEdit = QLineEdit()
                        self.lineEdit.setReadOnly(True)
                        self.lineEdit.setStyleSheet("background: #555;padding: 12px 20px;border: none;font-size: 18px;color: #fff;selection-background-color: rgba(255,255,255,0.2);")
                        self.lineEdit.setText(editor.path)
                        btn = Button()
                        btn.set_Text("Copy")
                        btn.clicked.connect(self.copyPathAct)
                        layout.addWidget(self.lineEdit)
                        layout.addWidget(btn)
                        self.copyPathDailog.show()
                  else:
                        return
            else:
                  return
      def copyPathAct(self):
            self.lineEdit.selectAll()
            self.lineEdit.copy()
            self.copyPathDailog.close()
      def newConsole(self):
            self.consoleWidget.show()
            self.output.clear()
            self.consoleWidget.setCurrentIndex(0)
            if self.process:
                  self.process.kill()
                  self.process = None
      def toggleConsole(self):
            if self.consoleWidget.isHidden():
                  self.consoleWidget.show()
                  self.consoleWidget.setCurrentIndex(0)
            elif self.consoleWidget.isVisible():
                  self.consoleWidget.hide()
      def toggleConsoleWidget(self):
            if self.consoleWidget.isHidden():
                  self.consoleWidget.show()
            elif self.consoleWidget.isVisible():
                  self.consoleWidget.hide()
      def setTheme(self):
            if ThemeC == "Dark":
                  self.defaultTheme()
            elif ThemeC == "Light":
                  self.lightTheme()
            elif ThemeC == "Classic":
                  self.noTheme()
      def defaultTheme(self):
            if self.currentTheme() == 0:
                  return
            self.setStyleSheet(Theme.Window_Dark)
            self.menuBarMain.setStyleSheet(Theme.MenuDark)
            self.moreMenu.setStyleSheet(Theme.MenuDark)
            self.tabwidthMenu.setStyleSheet(Theme.MenuDark)
            self.recentMenu.setStyleSheet(Theme.MenuDark)
            self.recentFolderMenu.setStyleSheet(Theme.MenuDark)
            self.explorerBar.setStyleSheet(Theme.ExplorerBarDark)
            self.widgetOutline.setStyleSheet(Theme.OutlineBarDark)
            self.explorer.setStyleSheet(Theme.ExplorerDark)
            self.outline.setStyleSheet(Theme.OutlineDark)
            #self.consoleWidget.problems.setStyleSheet(Theme.OutlineDark)
            self.outline.tree.horizontalScrollBar().setStyleSheet(Theme.ExplorerScrollDark)
            self.outline.tree.verticalScrollBar().setStyleSheet(Theme.ExplorerScrollDark)
            self.outline.tree.setStyleSheet(Theme.OutlineTreeDark)
            self.labelH.setStyleSheet(Theme.ExplorerLabelDark)
            self.labelO.setStyleSheet(Theme.OutlineBarLabelD)
            self.explorer.verticalScrollBar().setStyleSheet(Theme.ExplorerScrollDark)
            self.tabWidget.setStyleSheet(Theme.TabDark)
            self.splitWidget.setStyleSheet(Theme.TabDark)
            self.consoleWidget.setStyleSheet(Theme.ConsoleTabDark)
            self.output.setStyleSheet(Theme.ConsoleDark)
            self.output.verticalScrollBar().setStyleSheet(Theme.ConsoleDarkScroll)
            self.consoleWidget.terminal.outputArea.verticalScrollBar().setStyleSheet(Theme.ConsoleDarkScroll)
            self.consoleWidget.widget(3).outputArea.verticalScrollBar().setStyleSheet(Theme.ConsoleDarkScroll)
            self.assistant.verticalScrollBar().setStyleSheet(Theme.ConsoleDarkScroll)
            self.userInfoDialog.setStyleSheet(Theme.UserDark)
            self.registerForm.setStyleSheet(Theme.UserDark)
            CURRENT_THEME = 0
            filepath = os.path.join(loc, "settings/theme.json")
            methods.updateJson(filepath, "Theme", "Dark")
            current_time = QDateTime.currentDateTime()
            self.themeChanged__.emit("dark", current_time)
      def lightTheme(self):
            if self.currentTheme() == 1:
                  return
            self.setStyleSheet(Theme.Window_Light)
            self.menuBarMain.setStyleSheet(Theme.MenuLight)
            self.moreMenu.setStyleSheet(Theme.MenuLight)
            self.tabwidthMenu.setStyleSheet(Theme.MenuLight)
            self.recentMenu.setStyleSheet(Theme.MenuLight)
            self.recentFolderMenu.setStyleSheet(Theme.MenuLight)
            self.explorerBar.setStyleSheet(Theme.ExplorerBarLight)
            self.widgetOutline.setStyleSheet(Theme.OutlineBarLight)
            self.explorer.setStyleSheet(Theme.ExplorerLight)
            self.outline.setStyleSheet(Theme.OutlineLight)
            #self.consoleWidget.problems.setStyleSheet(Theme.OutlineLight)
            self.outline.tree.setStyleSheet(Theme.OutlineTreeLight)
            self.outline.tree.verticalScrollBar().setStyleSheet(Theme.ConsoleLightScroll)
            self.outline.tree.horizontalScrollBar().setStyleSheet(Theme.ConsoleLightScroll)
            self.labelH.setStyleSheet(Theme.ExplorerLabelLight)
            self.labelO.setStyleSheet(Theme.OutlineBarLabelL)
            self.explorer.verticalScrollBar().setStyleSheet(Theme.ExplorerScrollLight)
            self.tabWidget.setStyleSheet(Theme.TabLight)
            self.splitWidget.setStyleSheet(Theme.TabLight)
            self.output.setStyleSheet(Theme.ConsoleLight)
            self.consoleWidget.setStyleSheet(Theme.ConsoleTabLight)
            self.consoleWidget.terminal.outputArea.verticalScrollBar().setStyleSheet(Theme.ConsoleLightScroll)
            self.consoleWidget.widget(3).outputArea.verticalScrollBar().setStyleSheet(Theme.ConsoleLightScroll)
            self.output.verticalScrollBar().setStyleSheet(Theme.ConsoleLightScroll)
            self.assistant.verticalScrollBar().setStyleSheet(Theme.ConsoleLightScroll)
            self.userInfoDialog.setStyleSheet(Theme.UserLight)
            self.registerForm.setStyleSheet(Theme.UserLight)
            CURRENT_THEME = 1
            filepath = os.path.join(loc, "settings\\theme.json")
            methods.updateJson(filepath, "Theme", "Light")
            current_time = QDateTime.currentDateTime()
            self.themeChanged__.emit("light", current_time)
      def noTheme(self):
            if self.currentTheme() == 2:
                  return
            self.setStyleSheet("")
            self.menuBarMain.setStyleSheet("image: none;")
            self.recentFolderMenu.setStyleSheet("image: none;")
            self.moreMenu.setStyleSheet("image: none;")
            self.tabwidthMenu.setStyleSheet("image: none;")
            self.recentMenu.setStyleSheet("image: none;")
            self.explorerBar.setStyleSheet("image: none;")
            self.widgetOutline.setStyleSheet("image: none;")
            self.explorer.setStyleSheet("background: #f1f1f1;")
            self.outline.tree.verticalScrollBar().setStyleSheet("")
            self.outline.tree.setStyleSheet("image: none;")
            #self.consoleWidget.problems.verticalScrollBar().setStyleSheet("image: none;")
            #self.consoleWidget.problems.setStyleSheet("image: none;")
            self.outline.tree.horizontalScrollBar().setStyleSheet("image: none;")
            self.consoleWidget.terminal.outputArea.verticalScrollBar().setStyleSheet("")
            self.consoleWidget.widget(3).outputArea.verticalScrollBar().setStyleSheet("")
            self.labelH.setStyleSheet("""
            QLabel {
                        padding-left: 2px;
                        image:none;
                        font-family: verdana;
                        color: #444;
                        font-size: 18px;
                        background: #f1f1f1;
       }
            """)
            self.labelO.setStyleSheet("""
            QLabel {
                        padding-left: 2px;
                        image:none;
                        font-family: verdana;
                        color: #444;
                        font-size: 18px;
                        background: #f1f1f1;
       }
            """)
            self.explorer.verticalScrollBar().setStyleSheet("""
            QScrollBar:vertical {
                                    width: 10px;
                        }
            """)
            self.consoleWidget.setStyleSheet("image: none;")
            self.output.setStyleSheet("")
            self.outline.setStyleSheet("""
            QListWidget {
                  background: #eee;
                  color: #000;
                  min-width: 300px;
                  font-size: 13px;
                  border: none;
            }
            QListWidget::item {
                  background: #eee;
                  color: #000;
            }
            QListWidget::item {
                  background: #eee;
                  color: #000;
            }
            QListWidget::item:hover {
                  background: #ddd;
                  color: #000;
            }
            QListWidget::item:selected {
                  background: #ccc;
                  color: #000;
            }
            """)

            self.tabWidget.setStyleSheet("image: none;")
            self.splitWidget.setStyleSheet("image: none;")
            self.userInfoDialog.setStyleSheet("image: none;")
            self.registerForm.setStyleSheet("image: none;")
            CURRENT_THEME = 2
            filepath = os.path.join(loc, "settings\\theme.json")
            methods.updateJson(filepath, "Theme", "Classic")
            current_time = QDateTime.currentDateTime()
            self.themeChanged__.emit("classic", current_time)
      def currentTheme(self) -> int:
            return CURRENT_THEME
      def closeDirectory(self):
            if self.explorer.folderPath:
                  self.explorer.folderPath = None
                  path = os.path.join(loc, "data\\fileData\\folderPath.json")
                  methods.updateJson(path, "path", "")
                  self.explorer.setRootIndex(self.explorer.fileModel.index(self.explorer.folderPath))
                  self.close_all()
                  self.explorerBar.hide()
                  self.statusBar().showMessage("Closed folder.",2000)
            else:
                  return
      def remove_tab(self): # remove current tab 
            index = self.tabWidget.currentIndex()
            self.tabWidget.remove_tab(index)
      def showChangeLog(self):
            self.changeLogWin = ChangeLog()
            self.changeLogWin.show()
      def aboutDLG(self):
            self.aboutDlg = aboutDlg(self)
            self.aboutDlg.setWindowFlags(Qt.SplashScreen)
            self.aboutDlg.setWindowIcon(createIcon("Images\\txteditor.png"))
            txt = f"""
            <h1>About</h1>
            <p>{appName} is a open-source {appType} created by {writerName}.</p>   
            <ul>                                                                   
                  <li><b>App Version: </b>{self.getVersion()}</li>                 
                  <li><b>App Type: </b>{appType}</li>                              
                  <li><b>OS: </b>{Os}</li>                                         
                  <li><b>OS Version: </b>{osVersion}</li>                          
                  <li><b>Icon Provider: </b><a>{IconProvider}</a></li>   
            </ul>                                                                  
            """                                                                    
            self.aboutDlg.setText(txt)                                             
            self.aboutDlg.show()                                                     
      def getVersion(self):
            if version == None:
                  return "ERROR INTERNET DISCONNECTED"
            else:
                  return version
      def replaceAllDLG(self):
            if self.isVisible():
                  if self.tabWidget.currentWidget():
                        self.replacedlg2 = QWidget()
                        self.replacedlg2.setFixedSize(300,150)
                        self.replacedlg2.setWindowFlag(Qt.SplashScreen)
                        self.replacedlg2.setStyleSheet("background: #333;margin: 0;")
                        self.replacedlg2.setWindowTitle("Replace All")
                        ####################################
                        layoutM = QVBoxLayout(self.replacedlg2)
                        layoutM.setContentsMargins(0,0,0,0)
                        layoutM.setSpacing(0)
                        ####################################
                        layout = QHBoxLayout(self.replacedlg2)
                        layout.setContentsMargins(0,0,0,0)

                        self.findfield3 = QLineEdit()
                        if self.tabWidget.currentWidget().hasSelectedText():
                                          self.findfield.setText(self.tabWidget.currentWidget().selectedText())
                        self.findfield3.setStyleSheet("background: #555;padding: 12px 20px;border: none;font-size: 18px;color: #fff;selection-background-color: rgba(255,255,255,0.2);")
                        self.findfield3.setFocus(True)
                        self.findfield3.returnPressed.connect(self.findAct3)
                        btn = Button()
                        btn.setIcon(createIcon("Images\\Icons\\cil-x.png"))
                        btn.clicked.connect(self.replacedlg2.close)
                        ####################################
                        self.replaceField2 = QLineEdit()
                        self.replaceField2.setPlaceholderText("Replace...")
                        self.replaceField2.setStyleSheet("background: #555;padding: 12px 20px;border: none;font-size: 18px;color: #fff;selection-background-color: rgba(255,255,255,0.2);")
                        self.replaceField2.returnPressed.connect(self.replaceAllAct)
                        ####################################
                        layoutM.addLayout(layout)
                        layout.addWidget(self.findfield3)
                        layout.addWidget(btn)
                        layoutM.addWidget(self.replaceField2)
                        self.replacedlg2.show()
                  else: 
                        return
            else:
                  return
      def replaceDLG(self):
            if self.tabWidget.currentWidget():
                  self.replacedlg = QWidget()
                  self.replacedlg.setFixedSize(300,150)
                  self.replacedlg.setWindowFlag(Qt.SplashScreen)
                  self.replacedlg.setStyleSheet("background: #333;margin: 0;")
                  self.replacedlg.setWindowTitle("Replace")
                  ####################################
                  layoutM = QVBoxLayout(self.replacedlg)
                  layoutM.setContentsMargins(0,0,0,0)
                  layoutM.setSpacing(0)
                  ####################################
                  layout = QHBoxLayout(self.replacedlg)
                  layout.setContentsMargins(0,0,0,0)
                  self.findfield2 = QLineEdit()
                  if self.tabWidget.currentWidget().hasSelectedText():
                                    self.findfield.setText(self.tabWidget.currentWidget().selectedText())
                  self.findfield2.setPlaceholderText("Find...")
                  self.findfield2.setStyleSheet("background: #555;padding: 12px 20px;border: none;font-size: 18px;color: #fff;selection-background-color: rgba(255,255,255,0.2);")
                  self.findfield2.setFocus(True)
                  self.findfield2.returnPressed.connect(self.findAct2)
                  btn = Button()
                  btn.setIcon(createIcon("Images\\Icons\\cil-x.png"))
                  btn.clicked.connect(self.replacedlg.close)
####################################
                  self.replaceField = QLineEdit()
                  self.replaceField.setPlaceholderText("Replace...")
                  self.replaceField.setStyleSheet("background: #555;padding: 12px 20px;border: none;font-size: 18px;color: #fff;selection-background-color: rgba(255,255,255,0.2);")
                  self.replaceField.returnPressed.connect(self.replaceAct)
####################################
                  layoutM.addLayout(layout)
                  layout.addWidget(self.findfield2)
                  layout.addWidget(btn)
                  layoutM.addWidget(self.replaceField)
                  self.replacedlg.show()
            else:
                  return
      def findDLG(self):
            editor = self.tabWidget.currentWidget()
            if editor:
                  self.finddlg = QWidget()
                  self.finddlg.setFixedSize(300,50)
                  self.finddlg.setWindowFlag(Qt.SplashScreen)
                  self.finddlg.setStyleSheet("background: #555;")
                  self.finddlg.setWindowTitle("Find")
                  layout = QHBoxLayout(self.finddlg)
                  self.findfield = QLineEdit()
                  if editor.hasSelectedText():
                        self.findfield.setText(editor.selectedText())
                  self.findfield.setStyleSheet("padding: 12px 20px;border: none;font-size: 18px;color: #fff;selection-background-color: rgba(255,255,255,0.2);")
                  self.findfield.setFocus(True)
                  self.findfield.returnPressed.connect(self.findAct)
                  self.findfield.textChanged.connect(self.findAct)
                  btn = Button()
                  btn.setIcon(createIcon("Images\\Icons\\cil-x.png"))
                  btn.clicked.connect(self.finddlg.close)
                  layout.addWidget(self.findfield)
                  layout.addWidget(btn)
                  layout.setContentsMargins(0,0,0,0)
                  self.finddlg.show()
            else:
                  return
      def findAct(self):
            text = self.findfield.text()
            if text == '':
                  self.statusBar().showMessage("Error! Cannot find a blank text.", 2000) 
                  return
            else:
                  x = self.tabWidget.currentWidget().findFirst(text, False, False, False, True, True) # case sensitive
                  if x == False:
                        l = len(self.findfield.text())
                        self.findfield.setSelection(0, l)
                        self.findfield.setFocus()
                        self.statusBar().showMessage(f"{text} not found", 3000)
      def findAct2(self):
            text = self.findfield2.text()
            if text == '':
                  self.statusBar().showMessage("Error! Cannot find a blank text.", 2000) 
                  return
            else:
                  x = self.tabWidget.currentWidget().findFirst(text, False, False, False, True, True) # case sensitive
                  if x == False:
                        l = len(self.findfield2.text())
                        self.findfield2.setSelection(0, l)
                        self.findfield2.setFocus()
                        self.statusBar().showMessage(f"{text} not found", 3000)
      def findAct3(self):
            text = self.findfield3.text()
            if text == '':
                  self.statusBar().showMessage("Error! Cannot find a blank text.", 2000) 
                  return
            else:
                  x = self.tabWidget.currentWidget().findFirst(text, False, False, False, True, True) # case sensitive
                  if x == False:
                        l = len(self.findfield3.text())
                        self.findfield3.setSelection(0, l)
                        self.findfield3.setFocus()
                        self.statusBar().showMessage(f"{text} not found", 3000)
      def replaceAllAct(self):
            editor = self.tabWidget.currentWidget()
            if not editor.text() == "":
                  if not self.findfield3.text() == "":
                        line = editor.getCursorPosition()[0]
                        col = editor.getCursorPosition()[1]
                        selected_text = self.findfield3.text()
                        new_text = editor.text().replace(selected_text, self.replaceField2.text())
                        editor.setText(new_text)
                        editor.setCursorPosition(line, col)
                  else:
                        self.statusBar().showMessage("Nothing to replace")
            else:
                  self.statusBar().showMessage("No text to replace")
      def replaceAct(self):
            editor = self.tabWidget.currentWidget()
            if not editor.text() == "":
                  if not self.findfield2.text() == "":
                        line = editor.getCursorPosition()[0]
                        col = editor.getCursorPosition()[1]
                        selected_text = self.findfield2.text()
                        new_text = editor.text().replace(selected_text, self.replaceField.text(), 1)
                        editor.setText(new_text)
                        editor.setCursorPosition(line, col)
                  else:
                        self.statusBar().showMessage("Nothing to replace")
            else:
                  self.statusBar().showMessage("No text to replace")
      def update_lineCol(self):
            editor = self.tabWidget.currentWidget()
            if editor:
                  line = editor.getCursorPosition()[0] + 1
                  colm = editor.getCursorPosition()[1] + 1
                  self.btn1.setText(f"Ln: {line}, Col: {colm}")
      def _updateOutLine(self):
            if self.tabWidget.currentWidget():

                  text = self.tabWidget.currentWidget().text()
                  if self.tabWidget.currentWidget().isPythonFile():
                        text = self.tabWidget.currentWidget().text()
                        text = text.encode("utf-8")
                        self.updateOutline(text, self.tabWidget.currentWidget().path)
                        self.widgetOutline.show()
                  else:
                        self.widgetOutline.hide()
            else:
                  self.widgetOutline.hide()
      def update_saveUnsave(self):
            editor = self.tabWidget.currentWidget()
            if editor:
                  if editor.path:
                        if editor.saved == False:
                              self.btn2.setText("Unsaved")
                              self.updateWindowTitle()
                              self._updateOutLine()
                              if self.previewHTML.isVisible():
                                    if self.previewHTML.urlBar.text() != f"file:///{editor.path}":
                                          self.previewHTML.hide()
                              elif self.previewHTML.isHidden() and self.previewHTML.isClosed is False:
                                    if self.previewHTML.urlBar.text() == f"file:///{editor.path}":
                                                self.previewHTML.show()
                        else:
                              self.btn2.setText("Saved")
                              self.updateWindowTitle()
                              self._updateOutLine()
                              if self.previewHTML.isVisible():
                                    if self.previewHTML.urlBar.text() != f"file:///{editor.path}":
                                          self.previewHTML.hide()
                              elif self.previewHTML.isHidden() and self.previewHTML.isClosed is False:
                                    if self.previewHTML.urlBar.text() == f"file:///{editor.path}":
                                                self.previewHTML.show()
                  else:
                        self.btn2.setText("Unsaved")
                        self.setWindowTitle(f"untitled - SM FastEdit 2 ({self.getUsername()})")
            else:
                  self.btn2.hide()
                  self.btn1.hide()
                  self.btn3.hide()
                  self.btn4.hide()
                  self.btn5.hide()
                  self.setWindowTitle(f"SM FastEdit 2 ({self.getUsername()})")
      def runFile(self):
            editor = self.tabWidget.currentWidget()
            if not editor:
                  return
            if editor.path == "" or editor.path == None:
                  self.statusBar().showMessage("Cannot run this type of file.", 2000)
                  return
            else:
                  if editor.isHTMLFile():
                        if OpenHTMLInBuiltinBrowser is True:
                              self.btn3.setText("Opening...")
                              self.consoleWidget.show()
                              self.consoleWidget.setCurrentIndex(0)
                              self.output.setFocus()
                              self.output.clear()
                              self.browser = BrowserWindow()
                              editor = self.tabWidget.currentWidget()
                              self.browser.urlBar.setText(editor.path)
                              self.browser.loadURL(editor.path)
                              self.browser.setWindowTitle(f"Browser")
                              self.showBrowser()
                              self.statusBar().showMessage("Opened Browser successfully.",3000)
                              self.output.appendPlainText(f"[Opened {editor.path} in Browser]")
                              self.btn3.setText("Run File")
                        elif OpenHTMLInBuiltinBrowser is False:
                              self.btn3.setText("Opening...")
                              self.consoleWidget.show()
                              self.consoleWidget.setCurrentIndex(0)
                              self.output.setFocus()
                              self.output.clear()
                              editor = self.tabWidget.currentWidget()
                              webbrowser.open_new_tab(editor.path)
                              self.output.appendPlainText(f"[Opened {editor.path} in Browser]")
                              self.statusBar().showMessage("Opened Browser successfully.",3000)
                              self.btn3.setText("Run File")
                        elif OpenHTMLInBuiltinBrowser == "preview":
                              self.btn3.setText("Preview HTML started...")
                              editor = self.tabWidget.currentWidget()
                              self.previewHTML.load_url(editor.path)
                              self.consoleWidget.show()
                              self.consoleWidget.setCurrentIndex(0)
                              self.output.setFocus()
                              self.output.clear()
                              self.btn3.setText("Run File")
                  elif editor.isPythonFile():
                        self.output.clear()
                        if self.process is None:
                              self.btn3.setText("Running...")
                              self.consoleWidget.widget(3).tell(f"Running py -u {editor.path}")
                              self.consoleWidget.show()
                              self.consoleWidget.setCurrentIndex(0)
                              self.output.setFocus()
                              self.output.appendPlainText(f"[Running {editor.path}]")
                              self.process = QProcess()
                              self.process.readyReadStandardOutput.connect(self.onOutPut)
                              self.process.readyReadStandardError.connect(self.onError)
                              self.process.started.connect(self.timer.start)
                              self.process.finished.connect(self.afterFinished)
                              try:
                                    self.process.start("python", [f"{editor.path}"])
                              except Exception as e:
                                    self.statusBar().showMessage(str(e),2000)
                        elif self.process is not None:
                              self.process.kill()
                  else:
                        return
      def onOutPut(self):
            data = self.process.readAllStandardOutput()
            stdout = bytes(data).decode("utf8")
            self.output.appendPlainText(stdout)
      def onError(self):
            data = self.process.readAllStandardError()
            stderr = bytes(data).decode("utf8")
            self.output.appendPlainText(stderr)
      def afterFinished(self):
            process_execution_time = self.timer.elapsed()
            self.output.appendPlainText(f"[Finished in {process_execution_time / 1000}s]")
            self.consoleWidget.widget(3).tell(f"Finished in {process_execution_time / 1000}s")
            self.process = None
            self.btn3.setText("Run File")
      def restartFile(self):
            editor = self.tabWidget.currentWidget()
            if not editor:
                  return
            if editor.path == "" or editor.path == None:
                  self.statusBar().showMessage("Cannot run this type of file.", 2000)
                  return
            else:
                  if editor.isHTMLFile():
                        if self.browser:
                              self.browser.close()
                              self.browser.webView.reload()
                              self.browser.show()
                        else:
                              return
                  elif editor.isPythonFile():
                        if self.process:
                              self.process.kill()
                              self.process = None
                              self.runFile()
                        else:
                              return
                  else:
                        return
      def showBrowser(self):
            if self.browser.urlBar.text() == "":
                  self.statusBar().showMessage("Cannot run this type of file.", 2000)
                  return
            else:
                  self.browser.showMaximized()
      def closeRun(self):
            editor = self.tabWidget.currentWidget()
            if not editor:
                  return
            if editor.path == "" or editor.path == None:
                  self.statusBar().showMessage("Cannot run this type of file.", 2000)
                  return
            else:
                  if editor.isHTMLFile():
                        if self.browser:
                              self.browser.close()
                        else:
                              return
                  elif editor.isPythonFile():
                        if self.process:
                              self.process.kill()
                        else:
                              return
      def reloadFile(self):
            if self.tabWidget.count() == 0 or self.tabWidget.currentWidget().path == None:
                  return
            editor = self.tabWidget.currentWidget()
            line = editor.getCursorPosition()[0]
            col = editor.getCursorPosition()[1]
            scrollValue = self.requestFE(FE_GetVerticalScrollValue, self.tabWidget.currentWidget())
            if not os.path.exists(editor.path):
                  self.statusBar().showMessage("Path is unreachable", 2000)
                  return
            with open(editor.path, "r", encoding=Encoding) as file:
                  text = file.read()
            editor.setText(text)
            editor.setCursorPosition(line, col)
            editor.saved = True
            editor.savable = False
            editor.verticalScrollBar().setValue(scrollValue)
            self.btn2.setText("Saved")
            path = os.path.basename(editor.path)
            self.statusBar().showMessage(f"Reloaded {path} successfully.", 5000)
            self.fileReloaded__.emit(editor.path)
      def explorerOpenFile(self, index):
            if self.explorer.fileModel.isDir(index):
                  if self.explorer.isExpanded(index):
                        self.explorer.collapse(index)
                  else:
                        self.explorer.expand(index)
                  return
            filePath = self.explorer.fileModel.filePath(index)
            self.openFile(filePath)
      def wSpace_visible(self):
            editor = self.tabWidget.currentWidget()
            if editor:
                  editor.requestFE(FE_SetWsVisibility, QsciScintilla.WsVisible)
      def wSpace_invisible(self):
            editor = self.tabWidget.currentWidget()
            if editor:
                  editor.requestFE(FE_SetWsVisibility, QsciScintilla.WsInvisible)
      def close_all(self):
            if self.documentsUnsaved() == True:
                  message = "Documents are not saved!\nClose them?"
                  reply = QMessageBox.question(self, "Warning", message, QMessageBox.Yes | QMessageBox.No)
                  if reply == QMessageBox.No:
                        return
            for i in range(self.tabWidget.count()):
                  self.tabWidget.clear()
      def toggleReadOnly(self):
            editor = self.tabWidget.currentWidget()
            if not editor:
                  return
            if editor.isReadOnly():
                  editor.setReadOnly(False)
            else:
                  editor.setReadOnly(True)
      def gotolineDLG(self):
            if self.tabWidget.currentWidget():
                  self.gotoWin = QWidget()
                  self.gotoWin.setWindowTitle("Go to line")
                  self.gotoWin.setFixedSize(300,50)
                  self.gotoWin.setWindowFlag(Qt.SplashScreen)
                  self.gotoWin.setStyleSheet("background: #555;")
                  layout = QHBoxLayout(self.gotoWin)
                  self.go_field = QLineEdit()
                  self.go_field.setStyleSheet("padding: 12px 20px;border: none;font-size: 18px;color: #fff;selection-background-color: rgba(255,255,255,0.2);")
                  self.go_field.setFocus(True)
                  self.go_field.returnPressed.connect(self.goToLineAct)
                  btn = Button()
                  btn.setText("Close")
                  btn.clicked.connect(self.gotoWin.close)
                  layout.addWidget(self.go_field)
                  layout.addWidget(btn)
                  layout.setContentsMargins(0,0,0,0)
                  self.gotoWin.show()
      def goToLineAct(self):
            if self.go_field.text().isdigit():
                  ln = int(self.go_field.text()) - 1
                  editor = self.tabWidget.currentWidget()
                  editor.setFocus(True)
                  editor.setCursorPosition(ln, 0)
                  self.gotoWin.close()
      def goForwardTab(self):
            index = self.tabWidget.currentIndex()
            newindex = index + 1
            self.tabWidget.setCurrentIndex(newindex)
      def goBackTab(self):
            index = self.tabWidget.currentIndex()
            newindex = index - 1
            self.tabWidget.setCurrentIndex(newindex)
      def yes_wrap_mode(self):
            editor = self.tabWidget.currentWidget()
            if not editor:
                  return
            editor.setWrapMode(QsciScintilla.WrapMode.WrapWord)
      def no_wrap_mode(self):
            editor = self.tabWidget.currentWidget()
            if not editor:
                  return
            editor.setWrapMode(QsciScintilla.WrapMode.WrapNone)
      def focus_mode(self):
            if self.isFullScreen() and self.statusBar().isHidden() and self.consoleWidget.isHidden() and self.explorerBar.isHidden():
                  self.showNormal()
                  self.statusBar().show()
                  if self.tabWidget.currentWidget():
                        if self.tabWidget.currentWidget().path:
                              if self.tabWidget.currentWidget().path:
                                    if self.tabWidget.currentWidget().isPythonFile():
                                          self.widgetOutline.show()
            else:
                  self.showFullScreen()
                  self.statusBar().hide()
                  self.consoleWidget.hide()
                  self.explorerBar.hide()
                  self.widgetOutline.hide()
      def hideStatusBar(self):
            self.statusBar().hide()
            self.showStatusBar.setChecked(False)
      def toggle_editor(self):
            if self.tabWidget.isVisible():
                  self.tabWidget.hide()
            elif self.tabWidget.isHidden():
                  self.tabWidget.show()
      def toggle_status_bar(self):
            if self.statusBar().isVisible():
                  self.statusBar().hide()
            elif self.statusBar().isHidden():
                  self.statusBar().show()
      def toggle_explorer(self):
            if self.explorerBar.isVisible():
                  self.explorerBar.hide()
            elif self.explorerBar.isHidden():
                  self.explorerBar.show()
      def full_screen(self):
            if not self.isFullScreen():
                  self.showFullScreen()
                  self.fullScreen.setText("Normal")
            elif self.isFullScreen():
                  self.showNormal()
                  self.fullScreen.setText("Full Screen")
      def zoomIn(self):
            editor = self.tabWidget.currentWidget()
            if not editor:
                  return
            editor.zoomIn(2)
            self.updateMarginWidth()
      def zoomOut(self):
            editor = self.tabWidget.currentWidget()
            if not editor:
                  return
            editor.zoomOut(2)
            self.updateMarginWidth()
      def resetZoom(self):
            editor = self.tabWidget.currentWidget()
            if not editor:
                  return
            editor.zoomTo(0)
            self.updateMarginWidth()
      def new_file(self):
            self.tabWidget.add_tab()
            self.tabWidget.currentWidget().saved = False
            self.tabWidget.currentWidget().savable = True
            self.btn1.show()
            self.btn2.show()
            self.btn4.show()
            self.btn5.show()
      def rename_file_dlg(self):
            editor = self.tabWidget.currentWidget()
            if editor:
                  if editor.path is not None:
                        self.renameDlg = QWidget()
                        self.renameDlg.setWindowTitle("Go to line")
                        self.renameDlg.setFixedSize(300,50)
                        self.renameDlg.setWindowFlag(Qt.SplashScreen)
                        self.renameDlg.setStyleSheet("background: #555;")
                        layout = QHBoxLayout(self.renameDlg)
                        self.rename_field = QLineEdit()
                        file_name = os.path.splitext(editor.path)[0]
                        ext_name = os.path.splitext(editor.path)[1]
                        self.rename_field.setText(f"{os.path.basename(file_name)}{ext_name}")
                        self.rename_field.setStyleSheet("padding: 12px 20px;border: none;font-size: 18px;color: #fff;selection-background-color: rgba(255,255,255,0.2);")
                        self.rename_field.setFocus(True)
                        btn = Button()
                        btn.setText("Rename")
                        btn.clicked.connect(self.rename_file)
                        layout.addWidget(self.rename_field)
                        layout.addWidget(btn)
                        layout.setContentsMargins(0,0,0,0)
                        self.renameDlg.show()
                  else:
                        return
            else:
                  return
      def rename_file(self):
            editor = self.tabWidget.currentWidget()
            index = self.tabWidget.currentIndex()
            if editor:
                  if editor.path:
                        newName = self.rename_field.text()
                        folder = os.path.dirname(editor.path)
                        os.rename(editor.path, f"{folder}/{newName}")
                        self.tabWidget.setTabText(index, f"{newName}")
                        self.statusBar().showMessage("File name changed successfully!", 2000)
                        self.renameDlg.close()
                        self.updateWindowTitle()
                        self.updateFileType()
                        self.updateLexer(editor.path)
                        path = editor.path
                        self.remove_tab()
                        self.openFile(path)
                  else:
                        return
            else:
                  return
      def delete_file(self):
            editor = self.tabWidget.currentWidget()
            index = self.tabWidget.currentIndex()
            if editor:
                  if editor.path is not None:
                        with open(editor.path) as f:
                              text = f.read()
                        q = QMessageBox()
                        ans = q.question(self, "Warning!", f"Do you want to delete {editor.path}?",QMessageBox.Yes | QMessageBox.No)
                        if (ans== QMessageBox.Yes):
                              logfile = os.path.join(loc, "data/user/last_deleted_file.txt")
                              with open(logfile, "w") as log:
                                                log.write(text)
                              self.statusBar().showMessage(f"Deleting {editor.path}...",2000)
                              os.remove(editor.path)
                              self.tabWidget.removeTab(index)
                              self.statusBar().showMessage(f"File {editor.path} deleted successfully!", 5000)
                        else:
                              return
            else:
                  return
      def openDirectoryOnStart(self):
            if self.explorer.folderPath:
                  self.explorerBar.show()
                  self.explorer.setRootIndex(self.explorer.fileModel.index(self.explorer.folderPath))
                  self.labelH.setText(QDir(self.explorer.folderPath).dirName())
      def openDirectoryByDlg(self):
            dialog = QFileDialog(self)
            dialog.setViewMode(QFileDialog.List)
            dialog.setDirectory(os.getcwd())
            folderName = dialog.getExistingDirectory(self, "Open folder")
            self.openDirectory(folderName)
      def updateWindowTitle(self):
            editor = self.tabWidget.currentWidget()
            if editor:
                  if editor.path:
                        file_name = QFileInfo(editor.path).fileName()
                        folder_name = QDir(os.path.dirname(editor.path)).dirName()
                        if editor.saved is True:
                              self.setWindowTitle(f"{file_name} - {folder_name} - SM FastEdit 2 ({self.getUsername()})")
                        elif editor.saved is False:
                              self.setWindowTitle(f"{file_name} - {folder_name} - SM FastEdit 2 ({self.getUsername()})")
                  else:
                        self.setWindowTitle(f"untitled - SM FastEdit 2 ({self.getUsername()})")
            else:
                  self.setWindowTitle(f"SM FastEdit 2 ({self.getUsername()})")
      def openDirectory(self, folderpath):
            """Open directory from given folder path"""
            folderName = folderpath
            if folderName:
                  index = self.checkOpenedFolder(folderName)
                  if index != None:
                        return
                  try:
                        filepath = os.path.join(loc, "data\\fileData\\folderPath.json")
                        methods.updateJson(filepath, "path", folderName)
                        self.explorer.folderPath = folderName
                        self.explorerBar.show()
                        if Settings.CloseFilesOnOpeningFolder is True:
                              self.close_all()
                              self.explorer.setRootIndex(self.explorer.fileModel.index(self.explorer.folderPath))
                        elif Settings.CloseFilesOnOpeningFolder is False:
                              self.explorer.setRootIndex(self.explorer.fileModel.index(self.explorer.folderPath))
                        self.addRecentFolder(self.explorer.folderPath)
                        self.updateRecentFolders()
                        self.labelH.setText(QDir(self.explorer.folderPath).dirName())
                        self.labelH.setStatusTip(self.explorer.folderPath)
                        self.widgetOutline.hide()
                  except Exception as e:
                        self.statusBar().showMessage("Folder open action denied", 2000)
                        warning(str(e))
      def checkOpenedFile(self, path, tabWidget):
            """Check if same files are opened in editor area."""
            same_index = None
            path = path.replace("\\", "/")
            for i in range(tabWidget.count()):
                  if (tabWidget.widget(i).path == path): 
                        same_index = i
                        break
            return same_index
      def checkOpenedFolder(self, foldername):
            """Check if same folders are opened in editor area."""
            same_index = None
            path = foldername.replace("\\", "/")
            if (self.explorer.folderPath == path): 
                  same_index = 1
            return same_index
      def openShortcutSettings(self):
            filePath = os.path.join(loc, "settings/settings_folder/keybindings.fe_settings")
            self.openFile(filePath)
      def openFontSettings(self):
            filePath = os.path.join(loc, "settings/settings_folder/font.fe_settings")
            self.openFile(filePath)
      def openEditorSettings(self):
            filePath = os.path.join(loc, "settings/settings_folder/editor.fe_settings")
            self.openFile(filePath)
      def openOtherSettings(self):
            filePath = os.path.join(loc, "settings/settings_folder/settings.fe_settings")
            self.openFile(filePath)
      def openAddCompletions(self):
            filePath = os.path.join(loc, "data/autocompletion/addMore.fe_settings")
            self.openFile(filePath)
      def openConsoleSettings(self):
            filePath = os.path.join(loc, "settings/settings_folder/console.fe_settings")
            self.openFile(filePath)
      def openIconManager(self):
            filePath = os.path.join(loc, "Images/iconManager.fe_settings")
            self.openFile(filePath)
      def openSyntaxColoringSettings(self):
            filePath = os.path.join(loc, "settings/settings_folder/editorTheme.fe_settings")
            self.openFile(filePath)
      def addApiFile(self):
            filePath = os.path.join(loc, "data/api/addApi.fe_settings")
            self.openFile(filePath)
      def openFileDialog(self):
            dialog = QFileDialog(self)
            dialog.setViewMode(QFileDialog.List)
            dialog.setDirectory(os.getcwd())
            filename = dialog.getOpenFileName(self, "Open")[0]
            self.openFile(filename)
      def openMultipleFilesDialog(self):
            dialog = QFileDialog(self)
            dialog.setViewMode(QFileDialog.List)
            dialog.setDirectory(os.getcwd())
            filename = dialog.getOpenFileNames(self, "Open")
            self.openMultipleFiles(filename[0])
      def openFile(self, path):
            """Open given file path in editor."""
            filename = path
            if filename:
                  filePath = filename
                  if os.path.isfile(filePath) == False:
                        return
                  index = self.checkOpenedFile(filePath, self.tabWidget)
                  if index != None:
                        self.tabWidget.setCurrentIndex(index)
                        return
                  sFile = os.path.join(loc, "data/user/user-data.json")
                  sFile = sFile.lower()
                  if filename.lower() == sFile:
                        self.statusBar().showMessage("This file is a secured part of FastEdit. We cannot open this file!")
                        return
                  sFile2 = os.path.join(loc, "settings/recentfiles.json")
                  sFile2 = sFile2.lower()
                  if filename.lower() == sFile2:
                        self.statusBar().showMessage("This file is a secured part of FastEdit. We cannot open this file!")
                        return
                  size = methods.getFileSize(filePath)
                  if size > 50:
                        q = QMessageBox()
                        q.question(self, "Warning!","This file is too much larger in size. Your PC may get effected!", QMessageBox.Yes, QMessageBox.No)
                        return
                  try:
                        with open(filePath, 'r+', encoding=Encoding) as f:
                              text = f.read()
                        editor = requestsFE.get(FE_GetEditorWidget)
                        editor.setText(text) 
                        editor.path = filePath
                        self.tabWidget.newTab(editor, os.path.basename(editor.path))
                        x = self.tabWidget.count()   # number of tabs
                        index = x - 1
                        self.tabWidget.setCurrentIndex(index)
                        self.tabWidget.currentWidget().saved = True
                        self.tabWidget.currentWidget().savable = False
                        self.btn2.setText("Saved")
                        self.btn2.show()
                        self.btn1.show()
                        self.btn3.show()
                        self.btn4.show()
                        self.btn5.show()
                        self.updateExplorerItem()
                        info(methods.getFileSize(self.tabWidget.currentWidget().path))
                        self.fileOpened__.emit(self.tabWidget.currentWidget().path)
                        sFile3 = os.path.join(loc, "data/api/addApi.fe_settings")
                        sFile3 = sFile3.lower()
                        file1 = os.path.join(loc, "settings/settings_folder/settings.fe_settings")
                        file1 = file1.lower()
                        if filename.lower() == sFile3:
                              self.consoleWidget.show()
                              self.consoleWidget.setCurrentIndex(1)
                              self.assistantM.tell("""
                              <br>You have opened <i>addApi.fe_settings</i>. Before editing please see this guide:<br>
                              <ul>
                                    <li>1. Create a new file with exetension .api or .bas.</li><br>
                                    <li>2. After saving the api file in the folder, add a key in addApi.fe_settings file like this:</li>
                                    <code>
                                    "html": "data/api/myapifile.api"
                                    </code>
                              </ul>
                              """)
                        if methods.getFileExt(filename) == ".fe_settings":
                              self.settingsFileOpened__.emit(filename)
                        self.updateWindowTitle()
                        self.updateLexer(editor.path)
                        self.addRecentLists(editor.path)
                        self.updateRecentLists()
                        self._updateOutLine()
                  except Exception as e:
                        self.statusBar().showMessage("Cannot open this type of file in editor!", 2000)
                        if methods.getFileExt(filePath) in binaryFileExtensions:
                              self.browser = BrowserWindow()
                              self.browser.urlBar.setText(filename)
                              self.browser.loadURL(filename)
                              self.browser.setWindowTitle(f"Browser")
                              self.showBrowser()
                        warning(str(e))
      def openFileInSplitView(self, path):
            """Open given file path in splitfile."""
            if path:
                  index = self.checkOpenedFile(path, self.splitWidget)
                  if index != None:
                        self.splitWidget.setCurrentIndex(index)
                        return
                  with open(path, 'r+', encoding=Encoding) as f:
                        text = f.read()
                  self.splitWidget.show()
                  editor = requestsFE.get(FE_GetEditorWidget)
                  editor.setText(text)
                  editor.path = path
                  self.splitWidget.newTab(editor, os.path.basename(editor.path))
                  x = self.splitWidget.count()   # number of tabs
                  index = x - 1
                  # Due to a bug after clicking on "split view" save button text changes into "Unsaved". 
                  # So I fixed this by this code:
                  if self.tabWidget.currentWidget().saved is True:
                        self.btn2.setText("Saved")
                  self.splitWidget.setCurrentIndex(index)
                  self.splitWidget.currentWidget().saved = True
                  self.splitWidget.currentWidget().savable = False
                  self.splitWidget.currentWidget().setReadOnly(True)
                  self.splitWidget.currentWidget().SendScintilla(QsciScintilla.SCI_SETCARETSTYLE, QsciScintilla.CARETSTYLE_INVISIBLE)
                  self.updateLexerForSplitView(self.splitWidget.currentWidget().path)
      def openMultipleFiles(self, pathList):
            """Open multiple files  in editor."""
            for path in pathList:
                  filename = path
                  if filename:
                        filePath = filename
                        if os.path.isfile(filePath) == False:
                              return
                        index = self.checkOpenedFile(filePath, self.tabWidget)
                        if index != None:
                              self.tabWidget.setCurrentIndex(index)
                              return
                        sFile = os.path.join(loc, "data/user/user-data.json")
                        sFile = sFile.lower()
                        if filename.lower() == sFile:
                              self.statusBar().showMessage("This file is a secured part of FastEdit. We cannot open this file!")
                              return
                        sFile2 = os.path.join(loc, "settings/recentfiles.json")
                        sFile2 = sFile2.lower()
                        if filename.lower() == sFile2:
                              self.statusBar().showMessage("This file is a secured part of FastEdit. We cannot open this file!")
                              return
                        size = methods.getFileSize(filePath)
                        if size > 50:
                              q = QMessageBox()
                              q.question(self, "Warning!","This file is too much larger in size. Your PC may effected!")
                        try:
                              with open(filePath, 'r+', encoding=Encoding) as f:
                                    text = f.read()
                              editor = requestsFE.get(FE_GetEditorWidget)
                              editor.setText(text) 
                              editor.path = filePath
                              self.tabWidget.newTab(editor, os.path.basename(editor.path))
                              x = self.tabWidget.count()   # number of tabs
                              index = x - 1
                              self.tabWidget.setCurrentIndex(index)
                              self.tabWidget.currentWidget().saved = True
                              self.tabWidget.currentWidget().savable = False
                              self.btn2.setText("Saved")
                              self.btn2.show()
                              self.btn1.show()
                              self.btn3.show()
                              self.btn4.show()
                              self.btn5.show()
                              self.fileOpened__.emit(self.tabWidget.currentWidget().path)
                              self.updateWindowTitle()
                              self.updateLexer(filename)
                              self.addRecentLists(filename)
                              self._updateOutLine()
                              self.updateRecentLists()
                        except Exception as e:
                              self.statusBar().showMessage("Cannot open this type of file in editor!", 2000)
                              if methods.getFileExt(filePath) in binaryFileExtensions:
                                    self.browser = BrowserWindow()
                                    self.browser.urlBar.setText(filename)
                                    self.browser.loadURL(filename)
                                    self.browser.setWindowTitle(f"Browser")
                                    self.showBrowser()
                              warning(str(e))
      def saveFile(self):
            self.save()
            pass
      def save(self):
            """Save changes of opened file or saved file."""
            if self.tabWidget.count() == 0:
                  self.statusBar().showMessage("Create a new file to save.")
                  return
            filename = self.tabWidget.currentWidget().path
            index = self.tabWidget.currentIndex()
            if not filename:
                  self.saveAs()
            if self.tabWidget.currentWidget().saved is True:
                  return
            else:
                  text = self.tabWidget.currentWidget().text()
                  try:
                        if not os.path.exists(filename):
                              self.statusBar().showMessage("Path is unreachable", 2000)
                              return
                        if methods.getFileExt(filename) == ".fe_settings":
                              #message = "This file is a FastEdit settings file. After saving this file app will restart automatically. Do you want app to restart?"
                              #q = QMessageBox()
                              #q = q.question(None, "Warning", message, QMessageBox.Yes | QMessageBox.No)
                              #if q == QMessageBox.Yes:
                              with open(filename, 'w', encoding=Encoding) as file:
                                    file.write(text)
                                    self.tabWidget.currentWidget().saved = True
                                    self.tabWidget.currentWidget().savable = False
                                    if self.documentsUnsaved() is True:
                                          qm = QMessageBox()
                                          q = qm.question(self, "Warning", "To implement settings please save all other modified files! And then, click on reload new settings", QMessageBox.Ok)
                                          if q == QMessageBox.Ok:
                                                qm.close()
                                    else:
                                          self.reloadSettings()
                              #else:
                                    #return
                        with open(filename, 'w', encoding=Encoding) as file:
                              file.write(text)
                              self.statusBar().showMessage(filename + " saved", 5000)
                              fname = os.path.basename(filename)
                              self.tabWidget.setTabText(index, fname)
                              self.btn2.setText("Saved")
                              self.tabWidget.currentWidget().saved = True
                              self.tabWidget.currentWidget().savable = False
                              current_time = QDateTime.currentDateTime()
                              self.fileSaved__.emit(self.tabWidget.currentWidget().path, current_time)
                              self.btn2.show()
                              self.btn3.show()
                              self.btn4.show()
                              self.btn5.show()
                              self._updateOutLine()
                  except Exception as e:
                        self.statusBar().showMessage(str(e), 5000)
                        warning(str(e))
      def saveAs(self):
            """Save untitled file to a specific folder."""
            if self.tabWidget.count() == 0:
                  self.statusBar().showMessage("Create a new file to save.")
                  return

            dialog = QFileDialog(self)
            dialog.setViewMode(QFileDialog.List)
            dialog.setDirectory(os.getcwd())

            filename = dialog.getSaveFileName(self, "Save As")
            if filename[0]:
                  fullpath = filename[0]
                  text = self.tabWidget.currentWidget().text()
                  try:
                        with open(fullpath, 'w', encoding=Encoding) as file:
                              file.write(text)
                        self.tabWidget.currentWidget().path = fullpath
                        fname = os.path.basename(fullpath)
                        index = self.tabWidget.currentIndex()
                        self.tabWidget.setTabText(index, fname)
                        self.btn2.setText("Saved")
                        self.btn3.show()
                        self.btn4.show()
                        self.btn5.show()
                        self.updateExplorerItem()
                        self.tabWidget.currentWidget().saved = True
                        self.tabWidget.currentWidget().savable = False
                        current_time = QDateTime.currentDateTime()
                        self.fileSaved__.emit(self.tabWidget.currentWidget().path, current_time)
                        self.updateWindowTitle()
                        self.updateLexer(self.tabWidget.currentWidget().path)
                        self.updateFileType()
                        self._updateOutLine()
                  except Exception as e:
                        self.statusBar().showMessage(str(e), 5000)
            else:
                  self.statusBar().showMessage('File not saved !', 5000)
      def documentsUnsaved(self, tabwidget=None):
            """Check if there are any unsaved documents."""
            def check_documents(window):
                  if window.count() > 0:
                        for i in range(0, window.count()):
                              if window.widget(i).savable == True:
                                    if window.widget(i).saved == False:
                                          return True
                  return False
            if tabwidget is None:
                  if (check_documents(self.tabWidget)):
                        return True
                  else:
                        return False
            else:
                  return check_documents(tabwidget)
      def leave(self):
            """To quit application"""
            self.requestFE(FE_Leave)
      def __addLastOpenedFiles(self, new_file, index):
            """Add last opened files list in last_opened_file.json file."""
            last_opened_files.clear()
            if platform == "Windows":
                  new_file = new_file.replace("\\", "/")
            filepath = os.path.join(loc, "data\\user\\last_opened_files.json")
            jsonFile = open(filepath, "r")
            data = json.load(jsonFile)
            jsonFile.close()
            tmp = data["list"]
            tmp2 = data["index"]
            data["index"] = index
            if new_file not in data["list"]:
                  data["list"].append(new_file)
                  for i in data["list"]:
                        last_opened_files.clear()
                        last_opened_files.append(i)
            jsonFile = open(filepath, "w+")
            jsonFile.write(json.dumps(data))
            jsonFile.close()
      def addLastOpenedFiles(self):
            methods.updateJson(path3, "list", []) # clear old list
            if self.tabWidget.currentWidget():
                  for i in range(self.tabWidget.count()):
                              index = self.tabWidget.currentIndex()
                              self.__addLastOpenedFiles(self.tabWidget.widget(i).path, index)
      def closeEvent(self, event):
            if self.documentsUnsaved() is True:
                  message = "Documents are not saved!\nLeave anyway?"
                  ans = QMessageBox.question(self, "Warning", message, QMessageBox.Yes | QMessageBox.No)
                  if ans == QMessageBox.Yes:
                        if self.process:
                              self.process.kill()
                              self.output.clear()
                              self.process = None
                        tabs = self.tabWidget.count()
                        file = os.path.join(loc, "settings/tabCount.json")
                        methods.updateJson(file, "count", tabs)
                        terminal_text = self.consoleWidget.terminal.outputArea.toPlainText()
                        filepath = os.path.join(loc, "data/user/terminal_log.txt")
                        log_file = open(filepath, "w+")
                        log_file.write(terminal_text)
                        log_file.close()
                        self.addLastOpenedFiles()
                        self.close()
                  else:
                        event.ignore()
            else:
                  tabs = self.tabWidget.count()
                  file = os.path.join(loc, "settings/tabCount.json")
                  methods.updateJson(file, "count", tabs)
                  terminal_text = self.consoleWidget.terminal.outputArea.toPlainText()
                  filepath = os.path.join(loc, "data/user/terminal_log.txt")
                  log_file = open(filepath, "w+")
                  log_file.write(terminal_text)
                  log_file.close()
                  self.addLastOpenedFiles()
                  self.close()