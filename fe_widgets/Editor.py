from PyQt5 import QtCore
import PyQt5
from PyQt5.Qt import Qt
from PyQt5.Qsci import *
from PyQt5.QtCore import *
from PyQt5.QtGui import QClipboard, QColor, QFont, QFontMetrics
from PyQt5.QtWidgets import QApplication, QMenu
from .mainWidgets import *
import platform
import webbrowser
from data.fe_classes import Fe_Editor
from settings.font import *
from settings.shortcuts import *
from settings.theme import *
from settings.syntaxC import *
from data.autocompletion.pyqt5List import Modules, Widgets
from data.autocompletion.pyKeywords import Keywords
from data.autocompletion.jsKeywords import *
from data.autocompletion.pyMethods import *
from data.autocompletion.cssExtra import *
from data.autocompletion.htmlExtra import *
from data.autocompletion.jsonLists import *
from data.autocompletion.htmlParser import *
from data.calltips.python import *
from settings.editorsettings import *
from settings.settings import *
from methods import *
from resources import *
import json
import re
from syntaxChecker.CheckerPy import *
from data.regList import *
import plugins_manager
# Variable
tagsC = QColor(HtmlTag)
commentC = QColor(Comment)
attrC = QColor(HtmlAtr)
strC = QColor(String)
marginC = Theme.EditorBG
keyWordC = QColor(Keyword)

loc = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/"
path = os.path.join(loc, "data/api/addApi.fe_settings")
with open(path, "r") as file:
    _text = file.read()
data = json.loads(_text)
mainText = ""
loc = getLocation(os.path.abspath(__file__))

font2 = QFont()
font2.setItalic(True)
font2.setFamily(FontFamily.Editor)
font2.setPointSizeF(FontSize.FontSizeF)

font3 = QFont()
font3.setUnderline(True)
font3.setPointSizeF(FontSize.FontSizeF)
font3.setFamily(FontFamily.Editor)

plugin_lexer = plugins_manager.getPlugin(FE_GetLexerSupport)

class LexerJS(QsciLexerJavaScript):
      def __init__(self):
            super().__init__()
            # adding let keyword to lexer
      def keywords(self, index):
            keywords = QsciLexerJavaScript.keywords(self, index) or ''
            if index == 1:
                  return  ' let ' + keywords
                  
class LexerPython(QsciLexerPython):
      def __init__(self):
            super().__init__()
      # adding extra keywords to lexer
      def keywords(self, index):
            keywords = QsciLexerPython.keywords(self, index) or ''
            if index == 1:
                  return  ' len ' + ' __name__ ' + ' str ' + ' int ' + ' float ' + ' self ' + ' __peg_parser__ ' + ' await ' + ' nonlocal ' + ' True ' + ' False ' + keywords
 # editor area
class Editor(Fe_Editor):
      """Editor Widget"""
      fold_margin             = 2
      indic_margin            = 3
      marked_text             = ""
      find_indicator_lines    = []
      selection_lock          = None
      brace_matching_indic    = 10

      multi_cursor_editing    = False
      isPythonFile            = None
      isHTMLFile              = None
      isCSSFile               = None
      isJSONFile              = None
      isSettingFile           = None

      if_name                 = """\ndef main():\n    # Code here...\n\nif __name__ == "__main__":\n\tmain()"""
      from_imp                = """from module import *"""
      init                    = """def __init__(self, parent=None):"""


      
      
      # signals
      backspacePressed__      = pyqtSignal()
      def keyPressEvent(self, event):
            """This method will decide what to do after given keys are pressed."""
            line = self.getCursorPosition()[0]
            col = self.getCursorPosition()[1]
            if event.key() == Qt.Key_Backspace:
                  self.backspacePressed__.emit()
            if MagicTyping is True:
                  if self.isPythonFile():
                        if event.key() == Qt.Key_F2:
                              if "import sys" in self.text() or "from sys import sys" in self.text():
                                    self.insert(self.if_name)
                                    self.setSelection(line+2, col+4, line+2, col + 18)
                              else:
                                    self.insertAt("import sys\n",0,0)
                                    self.insert(self.if_name)
                                    self.setSelection(line+3, col+4, line+3, col + 18)
                        elif event.key() == Qt.Key_F3:
                              self.insert(self.from_imp)
                              self.setSelection(line, col+5, line, col + 11)
                        elif event.key() == Qt.Key_F4:
                              self.insert(self.init)
                              self.setCursorPosition(line+1, col)
                  if self.isCSSFile():
                        if event.key() == Qt.Key_Backspace:
                              text = self.text(line)[col - 1:col + 1]
                              if text in self.matching_pairs2:
                                    self.delete()
            super(Editor, self).keyPressEvent(event)

      def __init__(self, parent=None):
            super(Editor, self).__init__(parent)
            self.setStyleSheet("border: none;")
            # register it to FastEdit
            self.requestFE(FE_RegisterObject, self)
            # editor
            self.requestFE(FE_SetSelectionBgColor, Selection.ColorBG)
            # signals
            self.textChanged__.connect(self.unsaved)
            self.textChanged__.connect(self.__textChanged)
            self.textChanged__.connect(self._textChanged)
            self.selectionChanged__.connect(self._onSelection)
            self.lineChanged__.connect(self.lineChanged_)
            self.characterAdded__.connect(self.character_added)
            self.backspacePressed__.connect(self.backspacePressed)
            self.cursorPosChanged__.connect(self.cursorPosChanged)
            # variables
            self.saved              = False # saved file or not
            self.path               = None  # file path or not
            self.savable            = True  # can be save or not
            self.selection_lock     = False
            self.file_watcher       = None
            # key:   marker handle
            # value: list of (error message, error index)
            # font
            self.fontM = QFont()
        
            #system = platform.system().lower()
            #if system == 'windows':
                  #self.fontM.setFamily(FontFamily.Editor)
            #else:
                  #self.fontM.setFamily(FontFamily.Editor)
        
            self.fontM.setFixedPitch(True)
            self.fontM.setPointSizeF(FontSize.FontSizeF)
            self.setFont(self.fontM)
            self.setMarginsFont(self.fontM)
            # match braces 
            #self.setMatchedBraceBackgroundColor(BraceMatchingBackgroundColor)
            #self.setMatchedBraceForegroundColor(BraceMatchingForegroundColor)
            self.setUnmatchedBraceBackgroundColor(Theme.EditorBG)
            self.setUnmatchedBraceForegroundColor(QColor(UnclosedString))
            self.setBraceMatching(BraceMatching)
            #fixed font family problem in matching braces
            self.SendScintilla(QsciScintilla.SCI_BRACEHIGHLIGHTINDICATOR, True, self.brace_matching_indic)
            self.indicatorDefine(QsciScintilla.INDIC_DOTBOX, self.brace_matching_indic)
            self.setIndicatorForegroundColor(Indicator.Color, self.brace_matching_indic)
            # wrap
            self.requestFE(FE_SetWsVisibility, QsciScintilla.WsVisible)
            self.setWhitespaceBackgroundColor(Theme.EditorBG)
            self.setWhitespaceForegroundColor(QColor("#666"))
            self.SendScintilla(QsciScintilla.SCI_SETWHITESPACESIZE , 1)
            self.SendScintilla(QsciScintilla.SCI_SETINDENTATIONGUIDES, QsciScintilla.SC_IV_LOOKFORWARD)
            self.setIndentationGuidesBackgroundColor(QColor("#666"))
            self.setTabDrawMode(QsciScintilla.TabStrikeOut)
            # font
            self.fontM = QFont()
            self.fontM.setFamily(FontFamily.Editor)
            self.fontM.setPointSizeF(FontSize.FontSizeF)
            self.setFont(self.fontM)
            self.setMarginsFont(self.fontM)
            # line number bar
            line_count  = self.requestFE(FE_GetLines)
            if line_count < 99:
                  self.requestFE(FE_SetMarginWidth, 0, str(20) + "000")
            elif line_count > 99:
                  self.requestFE(FE_SetMarginWidth, 0, str(line_count) + "000")
            self.setMarginLineNumbers(0, LineNumbersVisible)
            self.setMarginsForegroundColor(Theme.LineNumberC)
            self.setMarginsBackgroundColor(Theme.EditorBG)
            self.setMarginOptions(QsciScintilla.MoSublineSelect)
            # context menu
            self.setContextMenuPolicy(Qt.CustomContextMenu)
            self.customContextMenuRequested.connect(self.customContextMenu)
            # caret
            self.SendScintilla(QsciScintilla.SCI_SETCARETFORE, QColor('#ffffff'))
            self.requestFE(FE_SetCaretWidth, Caret.CaretWidth)
            self.setCaretLineBackgroundColor(QColor(Caret.CaretBColor))
            self.setCaretForegroundColor(QColor(Caret.CaretColor))
            self.setCaretLineVisible(True)
            self.requestFE(FE_SetCaretStyle, Caret.CaretStyle)
            # Scroll bar
            self.verticalScrollBar().setStyleSheet(Theme.VScrollBar)
            self.cornerwidget = QLabel("")
            self.setCornerWidget(self.cornerwidget)
            self.horizontalScrollBar().setStyleSheet(Theme.HScrollBar)
            self.verticalScrollBar().setContextMenuPolicy(Qt.NoContextMenu)
            self.horizontalScrollBar().setContextMenuPolicy(Qt.NoContextMenu)
            self.SendScintilla(QsciScintilla.SCI_SETSCROLLWIDTHTRACKING, True)
            self.SendScintilla(QsciScintilla.SCI_SETSCROLLWIDTH, 0)
            # tab size
            self.tWidth = 4
            self.setTabWidth(self.tWidth)
            self.cursorPosChanged__.connect(self.getlineAndCol)
            self.style = None
            # parent
            self.setHighlightingFor("text")
            self.setUtf8(True)
            self.setOverwriteMode(OverWriteMode)
            self.requestFE(FE_SetMarginSensitivity, 0, LineNumberSenstivity)
            self.setAutoIndent(Indent.AutoIndent)
            self.setIndentationsUseTabs(Indent.IndentuseTabs)
            self.requestFE(FE_SetText, mainText)
            self.setBackspaceUnindents(Indent.BackSpaceUnIndent)
            self.setAcceptDrops(AcceptDrops)
            self.setEolMode(QsciScintilla.EolUnix)
            self.setPaper(Theme.EditorBG)
            self.setMarkerBackgroundColor(QColor("#555"))
            self.setMarkerForegroundColor(QColor("#555"))
            self.setFoldMarginColors(QColor(FoldArea), QColor(FoldArea))
            self.setFold()
            self.requestFE(FE_SetMarginWidth, self.indic_margin, 10)
            self.requestFE(FE_SetMarginWidth, 1, 5)
            self.setFoldMarkersColors(Theme.LineNumberC, Theme.LineNumberC)
            self.registerImage(4, QImage.scaled(QImage("Images\\Icons\\iconFunc.png"), 100,100, Qt.KeepAspectRatio))
            self.registerImage(1, QImage.scaled(QImage("Images\\Icons\\iconClass.png"), 100,100, Qt.KeepAspectRatio))
            self.registerImage(2, QImage.scaled(QImage("Images\\Icons\\iconKeyword.png"), 100,100,Qt.KeepAspectRatio))
            self.registerImage(3, QImage.scaled(QImage("Images\\Icons\\iconColor.png"), 100,100,Qt.KeepAspectRatio))
            self.registerImage(5, QImage.scaled(QImage("Images\\Icons\\iconSuggest.png"), 100,100,Qt.KeepAspectRatio))
            self.registerImage(6, QImage.scaled(QImage("Images\\Icons\\iconModule.png"), 100,100,Qt.KeepAspectRatio))
            self.setAcceptDrops(True)
            if self.hasSelectedText():
                  self.getSelectedCharNum()
            if Selection.MultiCursorEditing == True:
                  self.setMultiCursorEditing()
            self.parseStylesheet()
            # Set delay to show word matches
            # Taken idea from eric ide.
            self.show_matched_timer = QTimer(self)
            self.show_matched_timer.setSingleShot(True)
            self.show_matched_timer.setInterval(Indicator.Delay)
            self.show_matched_timer.timeout.connect(self.match_same_words)
            
      def startFileWatcher(self):
            """Auto reload functionality."""
            if self.path:
                  self.file_watcher = QFileSystemWatcher([self.path])
                  self.file_watcher.fileChanged.connect(self.reloadFileF)
      def reloadFileF(self, filepath):
            self.reloadFile()
      def getFileName(self):
            if self.path:
                  return self.path
      def cursorPosChanged(self, line, col):
            self.show_matched_timer.stop()
            self.show_matched_timer.start()
      def backspacePressed(self):
            line = self.getCursorPosition()[0]
            col = self.getCursorPosition()[1]
            text = self.text(line)[col - 1:col + 1]
            if text in self.matching_pairs:
                  self.delete()
      def _textChanged(self):
            if self.path:
                  self.parent.setAutoSave()
                  pass
      def __textChanged(self):
            if self.parent.tabWidget.currentWidget():
                  if self.path:
                        if self.parent.splitWidget.currentWidget():
                              self.lineSplitView, self.colSplitView = self.parent.splitWidget.currentWidget().getCursorPosition()
                              scrollArea1 = self.requestFE(FE_GetScrollValue, self.parent.splitWidget.currentWidget().verticalScrollBar())
                              scrollArea2 = self.requestFE(FE_GetScrollValue, self.parent.splitWidget.currentWidget().horizontalScrollBar())
                              if self.parent.splitWidget.currentWidget().path == self.parent.tabWidget.currentWidget().path:
                                    self.parent.splitWidget.currentWidget().setDocument(self.document())
                                    self.parent.splitWidget.currentWidget().setCursorPosition(self.lineSplitView, self.colSplitView)
                                    self.parent.splitWidget.currentWidget().verticalScrollBar().setValue(scrollArea1)
                                    self.parent.splitWidget.currentWidget().horizontalScrollBar().setValue(scrollArea2)
      def parseStylesheet(self):
            sty = """
            QLabel {
                  background: #222;
            }
            """
            self.cornerwidget.setStyleSheet(sty)
      def setMultiCursorEditing(self):
            try:
                  self.multi_cursor_editing = True
                  self.requestFE(FE_SetMultiCursorEditing, True, 1, True)
                  self.parent.btn1.setText("MultiCursorEditing")
            except Exception as e:
                  print(str(e))
      def backspace(self):
            self.editorCommand(QsciScintilla.SCI_DELETEBACK)
      def lineChanged_(self):
            self.updateMarginWidth()
      def updateMarginWidth(self):
            """Update margin width if line numbers increased."""
            line_count  = self.requestFE(FE_GetLines)
            if line_count < 99:
                  self.requestFE(FE_SetMarginWidth, 0, str(20) + "000")
            elif line_count > 99:
                  self.requestFE(FE_SetMarginWidth, 0, str(line_count) + "000")
      def clearSelectionHighlights(self):
            self.setCaretLineBackgroundColor(QColor(Caret.CaretBColor))
            line, colm = self.getCursorPosition()
            self.parent.btn1.setText(f"Ln: {line+1}, Col: {colm+1}")
      def _onSelection(self):
            if self.selection_lock == False:
                  self.clearSelectionHighlights()
                  if self.hasSelectedText():
                        self.selection_lock = True
                        self.setCaretLineBackgroundColor(Editor_Dark)
                        line = self.getCursorPosition()[0] + 1
                        colm = self.getCursorPosition()[1] + 1
                        start = self.SendScintilla(QsciScintilla.SCI_GETSELECTIONSTART)
                        end = self.SendScintilla(QsciScintilla.SCI_GETSELECTIONEND)
                        self.parent.btn1.setText(f"Ln: {line}, Col: {colm} (Selected: {end-start})")
                  self.selection_lock = False
      def reloadFile(self):
            self.parent.reloadFile()
            pass
      def unsaved(self):
            self.saved = False
            self.savable = True
            self.parent.btn2.setText("Unsaved")
      def focusInEvent(self, event):
            self.parent.updateExplorerItem()
            self.parent.btn7.setText("Editor")
            if Settings.AutoReloadFile == True:
                  self.startFileWatcher()
            super().focusInEvent(event)
      def customContextMenu(self, point):
            self.menu = Menu()
            undo = self.menu.addAction("Undo")
            undo.triggered.connect(self._undo)
            redo = self.menu.addAction("Redo")
            redo.triggered.connect(self._redo)
            self.menu.addSeparator()
            cut = self.menu.addAction("Cut")
            cut.triggered.connect(self._cut)
            copy = self.menu.addAction("Copy")
            copy.triggered.connect(self._copy)
            paste = self.menu.addAction("Paste")
            paste.triggered.connect(self._paste)
            self.menu.addSeparator()
            select_all = self.menu.addAction("Select All")
            select_all.triggered.connect(self.selectAllText)
            copy_all = self.menu.addAction("Copy All")
            copy_all.triggered.connect(self.copyAll)
            self.menu.addSeparator()
            copyLine = self.menu.addAction("Copy Line")
            copyLine.triggered.connect(self.copy_line)
            deleteLine = self.menu.addAction("Delete Line")
            deleteLine.triggered.connect(self.delete_line)
            self.menu.addSeparator()
            self.showSplitViewAct()
            self.menu.addSeparator()
            if self.path:
                  addToFav = self.menu.addAction("Add to Favourite Files")
                  addToFav.triggered.connect(self.addToFav)
            self.menu.addSeparator()
            self.manageGoToDef()
            self.manageGoToRef()
            ########################################
            undo.setShortcut("Ctrl+Z")
            redo.setShortcut("Ctrl+Y")
            cut.setShortcut("Ctrl+X")
            copy.setShortcut("Ctrl+C")
            paste.setShortcut("Ctrl+V")
            select_all.setShortcut("Ctrl+A")
            copy_all.setShortcut(ShortcutKeys.CopyAll)
            deleteLine.setShortcut(ShortcutKeys.DeleteLine)
            ########################################
            self.menu.exec_(self.mapToGlobal(point))
      def manageGoToDef(self):
            if self.isPythonFile():
                  word = self.getCurrentWord()
                  x = self.menu.addAction("Go to Definition...")
                  x.triggered.connect(self.go_to_def_py)
            elif self.isJavaScriptFile() or self.isHTMLFile():
                  word = self.getCurrentWord()
                  x = self.menu.addAction("Go to Definition...")
                  x.triggered.connect(self.go_to_def_js)
      def manageGoToRef(self):
            if self.isPythonFile():
                  x = self.menu.addAction("Go to Reference...")
                  x.triggered.connect(self.go_to_ref_py)
            elif self.isJavaScriptFile() or self.isHTMLFile():
                  x = self.menu.addAction("Go to Reference...")
                  x.triggered.connect(self.go_to_ref_js)

      def hotspot_clicked(self, pos, mod):
            #word = self.getCurrentWord()
            #self.go_to_def(word, mode="py")
            ...
      def go_to_def_py(self):
            word = self.getCurrentWord()
            self.go_to_def(word, mode="py")
      def go_to_def_js(self):
            word = self.getCurrentWord()
            self.go_to_def(word, mode="js")
      def go_to_ref_py(self):
            word = self.getCurrentWord()
            self.go_to_ref(word, mode="py")
      def go_to_ref_js(self):
            word = self.getCurrentWord()
            self.go_to_ref(word, mode="js")
      def go_to_def(self, word, mode):
            if mode == "py":
                  if word == '':
                        return
                  x = self.findFirst(f"def {word}", False, True, True, True, True)
                  if x:
                        self.parent.statusBar().showMessage(f"Found definition for {word}", 3000)

                  else:
                        self.parent.statusBar().showMessage(f"No definition found for {word}", 3000)
            elif mode == "js":
                  if word == '':
                        return
                  x = self.findFirst(f"function {word}", False, True, True, True, True)
                  if x:
                        self.parent.statusBar().showMessage(f"Found definition for {word}", 3000)
                  else:
                        self.parent.statusBar().showMessage(f"No definition found for {word}", 3000)
      def go_to_ref(self, word, mode):
            if mode == "py":
                  if word == '':
                        return
                  line = self.text(self.getCursorPosition()[0])
                  if line.strip().startswith("def "):
                        x = self.findFirst(f"{word}", False, True, True, True, True)
                        if x:
                              self.parent.statusBar().showMessage(f"Found reference for {word}", 3000)

                        else:
                              self.parent.statusBar().showMessage(f"No reference found for {word}", 3000)
            elif mode == "js":
                  if word == '':
                        return
                  line = self.text(self.getCursorPosition()[0])
                  if line.strip().startswith("function "):
                        x = self.findFirst(f"{word}", False, True, True, True, True)
                        if x:
                              self.parent.statusBar().showMessage(f"Found reference for {word}", 3000)
                        else:
                              self.parent.statusBar().showMessage(f"No reference found for {word}", 3000)
      def addToFav(self):
            self.parent.addFavFilesList(self.path)
            self.parent.updateFavFiles()
      def showSplitViewAct(self):
            if self.parent.tabWidget.currentWidget() == self:
                  if self.path is None:
                        return
                  elif self.path in getFiles.filesList:
                        if self.path == getFiles.path1:
                              openInSplitView = self.menu.addAction("Open Default Settings")
                              openInSplitView.triggered.connect(lambda: self.openInSplitView(getFiles.path1D))
                        elif self.path == getFiles.path2:
                              openInSplitView = self.menu.addAction("Open Default Settings")
                              openInSplitView.triggered.connect(lambda: self.openInSplitView(getFiles.path2D))
                        elif self.path == getFiles.path3:
                              openInSplitView = self.menu.addAction("Open Default Settings")
                              openInSplitView.triggered.connect(lambda: self.openInSplitView(getFiles.path3D))
                        elif self.path == getFiles.path4:
                              openInSplitView = self.menu.addAction("Open Default Settings")
                              openInSplitView.triggered.connect(lambda: self.openInSplitView(getFiles.path4D))
                        elif self.path == getFiles.path5:
                              openInSplitView = self.menu.addAction("Open Default Settings")
                              openInSplitView.triggered.connect(lambda: self.openInSplitView(getFiles.path5D))
                        elif self.path == getFiles.path7:
                              openInSplitView = self.menu.addAction("Open Default Settings")
                              openInSplitView.triggered.connect(lambda: self.openInSplitView(getFiles.path7D))
                        elif self.path == getFiles.path8:
                              openInSplitView = self.menu.addAction("Open Default Settings")
                              openInSplitView.triggered.connect(lambda: self.openInSplitView(getFiles.path8D))
                  else:
                        openInSplitView = self.menu.addAction("Split View")
                        openInSplitView.triggered.connect(lambda: self.openInSplitView(self.path))
      def openInSplitView(self, path):
            if self.parent.splitWidget.isHidden():
                  self.parent.openInSplitView(path)
                  self.parent.splitWidget.show()
            elif self.parent.splitWidget.isVisible():
                  self.parent.openInSplitView(path)
      def copy_line(self):
            self.SendScintilla(QsciCommand.LineCopy)
      def delete_line(self):
            self.SendScintilla(QsciCommand.LineDelete)
      def selectAllText(self):
            self.selectAll()
      def copyAll(self):
            self.selectAll()
            self._copy()
      def setHighlightingFor(self, lang: str):
            if lang == "text" or lang == "plain text":
                  self.style = None
                  self.setLexer(None)
                  self.setPaper(Theme.EditorBG)
                  self.setColor(Theme.EditorC)
            elif lang == "html" or lang == "HTML":
                  self.style = "HTML"
                  self.setAutoIndent(True)
                  self.setPaper(Theme.EditorBG)
                  self.setColor(Theme.EditorC)
                  self.fontM = QFont()
                  self.fontM.setFamily(FontFamily.Editor)
                  self.fontM.setPointSizeF(FontSize.FontSizeF)
                  if plugin_lexer.html_lexer_support == True:
                        lexer = QsciLexerHTML(self)
                        lexer.setDefaultFont(self.fontM)
                        lexer.setDefaultPaper(Theme.EditorBG)
                        lexer.setDefaultColor(Theme.EditorC)
                        lexer.setColor(QColor(DefaultColor), QsciLexerHTML.Default)
                        lexer.setFont(self.fontM, QsciLexerHTML.Default)
                        lexer.setMakoTemplates(True)
                        lexer.setPaper(Theme.EditorBG, QsciLexerHTML.Default)
                        lexer.setPaper(Theme.EditorBG, QsciLexerHTML.PHPKeyword)
                        lexer.setPaper(Theme.EditorBG, QsciLexerHTML.PHPOperator)
                        lexer.setPaper(Theme.EditorBG, QsciLexerHTML.XMLEnd)
                        lexer.setPaper(Theme.EditorBG, QsciLexerHTML.XMLTagEnd)
                        lexer.setPaper(Theme.EditorBG, QsciLexerHTML.PHPDefault)
                        lexer.setColor(Theme.EditorC, QsciLexerHTML.PHPDefault)
                        lexer.setPaper(Theme.EditorBG, QsciLexerHTML.JavaScriptDefault)
                        lexer.setFont(self.fontM, QsciLexerHTML.JavaScriptDefault)
                        lexer.setFont(self.fontM, QsciLexerHTML.JavaScriptCommentLine)
                        lexer.setFont(self.fontM, QsciLexerHTML.JavaScriptCommentDoc)
                        lexer.setFont(self.fontM, QsciLexerHTML.JavaScriptComment)
                        lexer.setColor(QColor(Comment), QsciLexerHTML.JavaScriptCommentLine)
                        lexer.setPaper(Theme.EditorBG, QsciLexerHTML.JavaScriptCommentLine)
                        lexer.setColor(QColor(Comment), QsciLexerHTML.JavaScriptCommentDoc)
                        lexer.setColor(QColor(Comment), QsciLexerHTML.JavaScriptUnclosedString)
                        lexer.setPaper(Theme.EditorBG, QsciLexerHTML.JavaScriptCommentDoc)
                        lexer.setColor(QColor("#5eb1ff"), QsciLexerHTML.JavaScriptKeyword)
                        lexer.setFont(font2, QsciLexerHTML.JavaScriptKeyword)
                        lexer.setPaper(Theme.EditorBG, QsciLexerHTML.JavaScriptKeyword)
                        lexer.setColor(Theme.EditorC, QsciLexerHTML.JavaScriptDefault)
                        lexer.setFont(self.fontM, QsciLexerHTML.JavaScriptDefault)
                        lexer.setPaper(Theme.EditorBG, QsciLexerHTML.JavaScriptDefault)
                        lexer.setPaper(Theme.EditorBG, QsciLexerHTML.JavaScriptDefault)
                        lexer.setColor(QColor(Comment), QsciLexerHTML.JavaScriptCommentDoc)
                        lexer.setColor(QColor(Comment), QsciLexerHTML.JavaScriptComment)
                        lexer.setColor(QColor(Comment), QsciLexerHTML.JavaScriptCommentLine)
                        lexer.setPaper(Theme.EditorBG, QsciLexerHTML.JavaScriptComment)
                        lexer.setPaper(Theme.EditorBG, QsciLexerHTML.JavaScriptDoubleQuotedString)
                        lexer.setFont(self.fontM, QsciLexerHTML.JavaScriptDoubleQuotedString)
                        lexer.setColor(Theme.EditorC, QsciLexerHTML.JavaScriptDoubleQuotedString)
                        lexer.setColor(Theme.EditorC, QsciLexerHTML.JavaScriptComment)
                        lexer.setPaper(Theme.EditorBG, QsciLexerHTML.JavaScriptDoubleQuotedString)
                        lexer.setFont(self.fontM, QsciLexerHTML.JavaScriptSingleQuotedString)
                        lexer.setPaper(Theme.EditorBG, QsciLexerHTML.JavaScriptSingleQuotedString)
                        lexer.setColor(Theme.EditorC, QsciLexerHTML.JavaScriptSingleQuotedString)
                        lexer.setFont(self.fontM, QsciLexerHTML.JavaScriptUnclosedString)
                        lexer.setPaper(Theme.EditorBG, QsciLexerHTML.JavaScriptUnclosedString)
                        lexer.setFont(self.fontM, QsciLexerHTML.JavaScriptNumber)
                        lexer.setPaper(Theme.EditorBG, QsciLexerHTML.JavaScriptNumber)
                        lexer.setColor(QColor(Number), QsciLexerHTML.JavaScriptNumber)
                        lexer.setColor(QColor(Comment), QsciLexerHTML.JavaScriptSymbol)
                        lexer.setPaper(Theme.EditorBG, QsciLexerHTML.JavaScriptSymbol)
                        lexer.setPaper(Theme.EditorBG, QsciLexerHTML.JavaScriptRegex)
                        lexer.setColor(Theme.EditorC, QsciLexerHTML.JavaScriptRegex)
                        lexer.setPaper(Theme.EditorBG, QsciLexerHTML.JavaScriptStart)
                        lexer.setColor(Theme.EditorC, QsciLexerHTML.JavaScriptStart)
                        lexer.setPaper(Theme.EditorBG, QsciLexerHTML.JavaScriptWord)
                        lexer.setColor(Theme.EditorC, QsciLexerHTML.JavaScriptWord)
                        lexer.setFont(self.fontM, QsciLexerHTML.JavaScriptWord)
                        lexer.setFont(self.fontM, QsciLexerHTML.JavaScriptSymbol)
                        lexer.setFont(self.fontM, QsciLexerHTML.Default)
                        lexer.setColor(tagsC, QsciLexerHTML.Tag)
                        lexer.setColor(commentC, QsciLexerHTML.HTMLComment)
                        lexer.setPaper(Theme.EditorBG, QsciLexerHTML.HTMLComment)
                        lexer.setFont(font2, QsciLexerHTML.HTMLComment)
                        lexer.setFont(font2, QsciLexerHTML.SGMLComment )
                        lexer.setColor(tagsC, QsciLexerHTML.SGMLDefault )
                        lexer.setPaper(Theme.EditorBG, QsciLexerHTML.SGMLDefault )
                        lexer.setFont(self.fontM, QsciLexerHTML.SGMLDefault )
                        lexer.setColor(Theme.EditorC, QsciLexerHTML.CDATA)
                        lexer.setPaper(Theme.EditorBG, QsciLexerHTML.CDATA)
                        lexer.setFont(self.fontM, QsciLexerHTML.CDATA)
                        lexer.setColor(Theme.EditorC, QsciLexerHTML.SGMLBlockDefault )
                        lexer.setPaper(Theme.EditorBG, QsciLexerHTML.SGMLBlockDefault )
                        lexer.setFont(self.fontM, QsciLexerHTML.SGMLBlockDefault )
                        lexer.setColor(QColor("#5eb1ff"), QsciLexerHTML.SGMLParameter)
                        lexer.setPaper(Theme.EditorBG, QsciLexerHTML.SGMLParameter)
                        lexer.setFont(self.fontM, QsciLexerHTML.SGMLParameter)
                        lexer.setColor(tagsC, QsciLexerHTML.SGMLCommand)
                        lexer.setPaper(Theme.EditorBG, QsciLexerHTML.SGMLCommand)
                        lexer.setFont(self.fontM, QsciLexerHTML.SGMLCommand)
                        lexer.setColor(Theme.EditorC, QsciLexerHTML.SGMLSpecial )
                        lexer.setPaper(Theme.EditorBG, QsciLexerHTML.SGMLSpecial )
                        lexer.setFont(self.fontM, QsciLexerHTML.SGMLSpecial )
                        lexer.setColor(Theme.EditorC, QsciLexerHTML.SGMLError  )
                        lexer.setPaper(Theme.EditorBG, QsciLexerHTML.SGMLError  )
                        lexer.setFont(self.fontM, QsciLexerHTML.SGMLError  )
                        lexer.setColor(Theme.EditorC, QsciLexerHTML.SGMLParameterComment   )
                        lexer.setPaper(Theme.EditorBG, QsciLexerHTML.SGMLParameterComment   )
                        lexer.setPaper(Theme.EditorBG, QsciLexerHTML.SGMLDoubleQuotedString   )
                        lexer.setPaper(Theme.EditorBG, QsciLexerHTML.SGMLSingleQuotedString   )
                        lexer.setFont(self.fontM, QsciLexerHTML.SGMLParameterComment   )
                        lexer.setFont(font2, QsciLexerHTML.Attribute)
                        lexer.setColor(attrC, QsciLexerHTML.Attribute)
                        lexer.setFont(font2, QsciLexerHTML.UnknownAttribute)
                        lexer.setColor(attrC, QsciLexerHTML.UnknownAttribute)
                        lexer.setColor(QColor(HtmlString), QsciLexerHTML.HTMLDoubleQuotedString)
                        lexer.setColor(QColor(HtmlString), QsciLexerHTML.HTMLSingleQuotedString)
                        lexer.setColor(QColor(HtmlString), QsciLexerHTML.SGMLDoubleQuotedString )
                        lexer.setColor(QColor(HtmlString), QsciLexerHTML.SGMLSingleQuotedString )
                        lexer.setColor(QColor(HtmlString), QsciLexerHTML.HTMLNumber)
                        lexer.setColor(QColor(HtmlEntity), QsciLexerHTML.Entity)
                        lexer.setFont(self.fontM, QsciLexerHTML.Entity)
                        lexer.setColor(tagsC, QsciLexerHTML.OtherInTag)
                        lexer.setPaper(Theme.EditorBG, QsciLexerHTML.OtherInTag)
                        lexer.setColor(tagsC, QsciLexerHTML.UnknownTag)
                        lexer.setPaper(Theme.EditorBG, QsciLexerHTML.UnknownTag)
                        lexer.setColor(attrC, QsciLexerHTML.UnknownAttribute)
                        lexer.setColor(QColor(HtmlValue), QsciLexerHTML.HTMLValue)
                        lexer.setPaper(Theme.EditorBG, QsciLexerHTML.HTMLValue)
                        lexer.setFoldCompact(False)
                        self.lexerHTML = lexer
                        self.setHtmlAutoComplete()
                        self.setLexer(lexer)
            elif lang == "css" or lang == "CSS":
                  self.setAutoIndent(True)
                  self.style = "CSS"
                  if plugin_lexer.css_lexer_support is True:
                        lexerCSS = QsciLexerCSS(self)
                        lexerCSS.setDefaultFont(self.fontM)
                        lexerCSS.setDefaultPaper(Theme.EditorBG)
                        lexerCSS.setDefaultColor(Theme.EditorC)
                        lexerCSS.setColor(Theme.EditorC, QsciLexerCSS.Default)
                        lexerCSS.setColor(QColor(cssTag), QsciLexerCSS.Tag)
                        lexerCSS.setFont(self.fontM, QsciLexerCSS.Tag)
                        lexerCSS.setColor(Theme.EditorC, QsciLexerCSS.Operator)
                        lexerCSS.setPaper(Theme.EditorBG, QsciLexerCSS.Operator)
                        lexerCSS.setColor(QColor(cssAtr), QsciLexerCSS.Attribute)
                        lexerCSS.setColor(QColor(cssProperty), QsciLexerCSS.CSS1Property)
                        lexerCSS.setColor(QColor(cssProperty), QsciLexerCSS.CSS2Property)
                        lexerCSS.setColor(QColor(cssProperty), QsciLexerCSS.CSS3Property)
                        lexerCSS.setColor(QColor(cssProperty), QsciLexerCSS.UnknownProperty)
                        lexerCSS.setColor(QColor(cssValue), QsciLexerCSS.Value)
                        lexerCSS.setColor(strC, QsciLexerCSS.SingleQuotedString)
                        lexerCSS.setColor(strC, QsciLexerCSS.DoubleQuotedString)
                        lexerCSS.setColor(QColor(cssPseudoElement), QsciLexerCSS.PseudoElement)
                        lexerCSS.setColor(QColor(cssExtendPseoudoEl), QsciLexerCSS.ExtendedPseudoElement)
                        lexerCSS.setColor(QColor(cssExtendPseoudoCl), QsciLexerCSS.ExtendedPseudoClass)
                        lexerCSS.setColor(QColor(cssPseudoCl), QsciLexerCSS.PseudoClass)
                        lexerCSS.setColor(QColor(cssPseudoCl), QsciLexerCSS.UnknownPseudoClass)
                        lexerCSS.setColor(QColor(cssVar), QsciLexerCSS.Variable)
                        lexerCSS.setColor(QColor(cssClassSelector), QsciLexerCSS.ClassSelector)
                        lexerCSS.setColor(QColor(cssIdSelector), QsciLexerCSS.IDSelector)
                        lexerCSS.setColor(QColor(cssMediaRule), QsciLexerCSS.MediaRule)
                        lexerCSS.setFont(font2, QsciLexerCSS.MediaRule)
                        lexerCSS.setColor(commentC, QsciLexerCSS.Comment)
                        lexerCSS.setFont(font2, QsciLexerCSS.Comment)
                        lexerCSS.setFont(font2, QsciLexerCSS.IDSelector)
                        self.setFont(self.fontM)
                        lexerCSS.setFont(self.fontM, QsciLexerCSS.Tag)
                        lexerCSS.setFoldCompact(True)
                        self.lexerCSS = lexerCSS
                        self.setCSSAutoComplete()
                        self.setCSSCallTips()
                        self.setLexer(lexerCSS)
            elif lang == "js" or lang == "javascript" or lang == "JavaScript":
                  self.style = "JavaScript"
                  self.setAutoIndent(True)
                  self.setPaper(Theme.EditorBG)
                  self.setColor(Theme.EditorC)
                  if plugin_lexer.js_lexer_support is True:
                        lexerJs = LexerJS()
                        lexerJs.setDefaultFont(self.fontM)
                        lexerJs.setDefaultPaper(Theme.EditorBG)
                        lexerJs.setDefaultColor(QColor(Theme.EditorC))
                        lexerJs.setColor(Theme.EditorC, QsciLexerJavaScript.Default)
                        lexerJs.setColor(QColor(UnclosedString), QsciLexerJavaScript.UnclosedString)
                        lexerJs.setPaper(Theme.EditorBG, QsciLexerJavaScript.UnclosedString)
                        lexerJs.setFont(font3, QsciLexerJavaScript.UnclosedString)
                        lexerJs.setColor(commentC, QsciLexerJavaScript.Comment)
                        lexerJs.setPaper(Theme.EditorBG, QsciLexerJavaScript.Comment)
                        lexerJs.setFont(font2, QsciLexerJavaScript.Comment)
                        lexerJs.setColor(commentC, QsciLexerJavaScript.CommentLine)
                        lexerJs.setPaper(Theme.EditorBG, QsciLexerJavaScript.CommentLine)
                        lexerJs.setFont(font2, QsciLexerJavaScript.CommentLine)
                        lexerJs.setColor(commentC, QsciLexerJavaScript.CommentDoc)
                        lexerJs.setPaper(Theme.EditorBG, QsciLexerJavaScript.CommentDoc)
                        lexerJs.setFont(font2, QsciLexerJavaScript.CommentDoc)
                        lexerJs.setColor(QColor(Number), QsciLexerJavaScript.Number)
                        lexerJs.setPaper(Theme.EditorBG, QsciLexerJavaScript.HashQuotedString)
                        lexerJs.setColor(keyWordC, QsciLexerJavaScript.Keyword)
                        lexerJs.setFont(font2, QsciLexerJavaScript.Keyword)
                        lexerJs.setColor(keyWordC, QsciLexerJavaScript.KeywordSet2)
                        lexerJs.setFont(font2, QsciLexerJavaScript.KeywordSet2)
                        lexerJs.setColor(Theme.EditorC, QsciLexerJavaScript.Operator)
                        lexerJs.setColor(strC, QsciLexerJavaScript.SingleQuotedString)
                        lexerJs.setFont(self.fontM, QsciLexerJavaScript.SingleQuotedString)
                        lexerJs.setPaper(Theme.EditorBG, QsciLexerJavaScript.Regex)
                        lexerJs.setFont(self.fontM, QsciLexerJavaScript.Regex)
                        lexerJs.setColor(strC, QsciLexerJavaScript.DoubleQuotedString)
                        lexerJs.setFont(self.fontM, QsciLexerJavaScript.DoubleQuotedString)
                        lexerJs.setColor(strC, QsciLexerJavaScript.TripleQuotedVerbatimString)
                        lexerJs.setFont(self.fontM, QsciLexerJavaScript.TripleQuotedVerbatimString)
                        lexerJs.setColor(keyWordC, QsciLexerJavaScript.GlobalClass)
                        self.lexerJs = lexerJs
                        self.setJsAutoComplete()
                        self.setLexer(lexerJs)
            elif lang == "py" or lang == "python":
                  self.style = "Python"
                  self.setAutoIndent(True)
                  self.setPaper(Theme.EditorBG)
                  self.setColor(Theme.EditorC)
                  if plugin_lexer.py_lexer_support is True:
                        self.lexerPy = LexerPython()
                        self.lexerPy.setDefaultColor(Theme.EditorC)
                        self.lexerPy.setDefaultFont(self.fontM)
                        self.lexerPy.setDefaultPaper(Theme.EditorBG)
                        self.lexerPy.setColor(Theme.EditorC, QsciLexerPython.Default)
                        self.lexerPy.setFont(self.fontM, QsciLexerPython.Default)
                        self.lexerPy.setPaper(Theme.EditorBG, QsciLexerPython.Default)
                        self.lexerPy.setColor(keyWordC, QsciLexerPython.Keyword)
                        self.lexerPy.setFont(font2, QsciLexerPython.Keyword)
                        self.lexerPy.setColor(QColor(pyClassName), QsciLexerPython.ClassName)
                        self.lexerPy.setFont(self.fontM, QsciLexerPython.ClassName)
                        self.lexerPy.setColor(Theme.EditorC, QsciLexerPython.Operator)
                        self.lexerPy.setColor(QColor(Number), QsciLexerPython.Number)
                        self.lexerPy.setColor(QColor(pyDec), QsciLexerPython.Decorator)
                        self.lexerPy.setColor(QColor(pyFunName), QsciLexerPython.FunctionMethodName)
                        self.lexerPy.setFont(self.fontM, QsciLexerPython.FunctionMethodName)
                        self.lexerPy.setColor(QColor(pyFString), QsciLexerPython.SingleQuotedFString)
                        self.lexerPy.setFont(font2, QsciLexerPython.SingleQuotedFString)
                        self.lexerPy.setColor(strC, QsciLexerPython.SingleQuotedString)
                        self.lexerPy.setFont(self.fontM, QsciLexerPython.SingleQuotedString)
                        self.lexerPy.setColor(QColor(pyFString), QsciLexerPython.DoubleQuotedFString)
                        self.lexerPy.setFont(font2, QsciLexerPython.DoubleQuotedFString)
                        self.lexerPy.setColor(strC, QsciLexerPython.DoubleQuotedString)
                        self.lexerPy.setFont(self.fontM, QsciLexerPython.DoubleQuotedString)
                        self.lexerPy.setColor(QColor(pyFString), QsciLexerPython.TripleSingleQuotedFString)
                        self.lexerPy.setFont(font2, QsciLexerPython.TripleSingleQuotedFString)
                        self.lexerPy.setColor(QColor(pyFString), QsciLexerPython.TripleDoubleQuotedFString)
                        self.lexerPy.setFont(font2, QsciLexerPython.TripleDoubleQuotedFString)
                        self.lexerPy.setColor(strC, QsciLexerPython.TripleSingleQuotedString)
                        self.lexerPy.setFont(self.fontM, QsciLexerPython.TripleSingleQuotedString)
                        self.lexerPy.setColor(strC, QsciLexerPython.TripleDoubleQuotedString)
                        self.lexerPy.setFont(self.fontM, QsciLexerPython.TripleDoubleQuotedString)
                        self.lexerPy.setPaper(Theme.EditorBG, QsciLexerPython.UnclosedString)
                        self.lexerPy.setColor(QColor(UnclosedString), QsciLexerPython.UnclosedString)
                        self.lexerPy.setFont(self.fontM, QsciLexerPython.UnclosedString)
                        self.lexerPy.setColor(QColor(Comment), QsciLexerPython.Comment)
                        self.lexerPy.setFont(font2, QsciLexerPython.Comment)
                        self.lexerPy.setColor(QColor(Comment), QsciLexerPython.CommentBlock)
                        self.lexerPy.setFont(font2, QsciLexerPython.CommentBlock)
                        self.lexerPy.setHighlightSubidentifiers(True)
                        self.setHotspotUnderline(True)
                        self.lexerPy.setAutoIndentStyle(QsciScintilla.AiClosing)
                        #self.SendScintilla(QsciScintilla.SCI_STYLESETHOTSPOT, QsciLexerPython.Identifier, True)
                        #self.SCN_HOTSPOTCLICK.connect(self.hotspot_clicked)
                        self.setPythonCallTips()
                        self.setPyAutoComplete()
                        self.setLexer(self.lexerPy)
            elif lang == "json":
                  self.style = "JSON"
                  self.lexerJSON = QsciLexerJSON()
                  self.setPaper(Theme.EditorBG)
                  self.setColor(Theme.EditorC)
                  if plugin_lexer.json_lexer_support is True:
                        self.lexerJSON.setDefaultColor(Theme.EditorC)
                        self.lexerJSON.setDefaultFont(self.fontM)
                        self.lexerJSON.setDefaultPaper(Theme.EditorBG)
                        self.lexerJSON.setColor(Theme.EditorC, QsciLexerJSON.Default)
                        self.lexerJSON.setColor(keyWordC, QsciLexerJSON.Keyword)
                        self.lexerJSON.setColor(strC, QsciLexerJSON.String)
                        self.lexerJSON.setColor(QColor(jsonIri), QsciLexerJSON.IRI)
                        self.lexerJSON.setFont(font2, QsciLexerJSON.IRI)
                        self.lexerJSON.setColor(QColor(jsonProperty), QsciLexerJSON.Property)
                        self.lexerJSON.setColor(QColor(Number), QsciLexerJSON.Number)
                        self.lexerJSON.setColor(QColor(UnclosedString), QsciLexerJSON.UnclosedString)
                        self.lexerJSON.setPaper(Theme.EditorBG, QsciLexerJSON.UnclosedString)
                        self.lexerJSON.setColor(Theme.EditorC, QsciLexerJSON.Operator)
                        self.lexerJSON.setColor(QColor(Comment), QsciLexerJSON.CommentBlock)
                        self.lexerJSON.setColor(QColor(Comment), QsciLexerJSON.CommentBlock)
                        self.lexerJSON.setColor(QColor(Comment), QsciLexerJSON.CommentLine)
                        self.lexerJSON.setColor(QColor(Comment), QsciLexerJSON.CommentLine)
                        self.setJSONAutoComplete()
                        self.setLexer(self.lexerJSON)
            elif lang == "settings":
                  self.style = "JSON"
                  self.lexerSettings = QsciLexerJSON()
                  self.setPaper(Theme.EditorBG)
                  self.setColor(Theme.EditorC)
                  if plugin_lexer.json_lexer_support is True:
                        self.lexerSettings.setDefaultColor(Theme.EditorC)
                        self.lexerSettings.setDefaultFont(self.fontM)
                        self.lexerSettings.setDefaultPaper(Theme.EditorBG)
                        self.lexerSettings.setColor(Theme.EditorC, QsciLexerJSON.Default)
                        self.lexerSettings.setColor(keyWordC, QsciLexerJSON.Keyword)
                        self.lexerSettings.setColor(strC, QsciLexerJSON.String)
                        self.lexerSettings.setColor(QColor(jsonIri), QsciLexerJSON.IRI)
                        self.lexerSettings.setFont(font2, QsciLexerJSON.IRI)
                        self.lexerSettings.setColor(QColor(jsonProperty), QsciLexerJSON.Property)
                        self.lexerSettings.setColor(QColor(Number), QsciLexerJSON.Number)
                        self.lexerSettings.setColor(QColor(UnclosedString), QsciLexerJSON.UnclosedString)
                        self.lexerSettings.setPaper(Theme.EditorBG, QsciLexerJSON.UnclosedString)
                        self.lexerSettings.setColor(Theme.EditorC, QsciLexerJSON.Operator)
                        self.lexerSettings.setColor(QColor(Comment), QsciLexerJSON.CommentBlock)
                        self.lexerSettings.setColor(QColor(Comment), QsciLexerJSON.CommentBlock)
                        self.lexerSettings.setColor(QColor(Comment), QsciLexerJSON.CommentLine)
                        self.lexerSettings.setColor(QColor(Comment), QsciLexerJSON.CommentLine)
                        self.setSettingsAutoComplete()
                        self.setLexer(self.lexerSettings)
            elif lang == "xml":
                  self.style == "XML"
                  self.lexerXML = QsciLexerXML()
                  self.setPaper(Theme.EditorBG)
                  self.setColor(Theme.EditorC)
                  if plugin_lexer.json_lexer_support is True:
                        self.lexerXML.setDefaultColor(Theme.EditorC)
                        self.lexerXML.setDefaultFont(self.fontM)
                        self.lexerXML.setDefaultPaper(Theme.EditorBG)
                        self.lexerXML.setColor(QColor(DefaultColor), QsciLexerXML.Default)
                        self.lexerXML.setColor(tagsC, QsciLexerXML.Tag)
                        self.lexerXML.setColor(attrC, QsciLexerXML.Attribute)
                        self.lexerXML.setColor(attrC, QsciLexerXML.UnknownAttribute)
                        self.lexerXML.setColor(tagsC, QsciLexerXML.UnknownTag)
                        self.lexerXML.setColor(tagsC, QsciLexerXML.OtherInTag)
                        self.lexerXML.setFont(self.fontM, QsciLexerXML.Default)
                        self.lexerXML.setPaper(Theme.EditorBG, QsciLexerXML.Default)
                        self.lexerXML.setColor(QColor(HtmlString), QsciLexerHTML.HTMLDoubleQuotedString)
                        self.lexerXML.setColor(QColor(HtmlString), QsciLexerHTML.HTMLSingleQuotedString)
                        self.lexerXML.setFoldCompact(False)
                        self.setLexer(self.lexerXML)
            elif lang == "md":
                  self.style = "Markdown"
                  self.lexerMD = QsciLexerMarkdown()
                  self.setPaper(Theme.EditorBG)
                  self.setColor(Theme.EditorC)
                  if plugin_lexer.md_lexer_support is True:
                        self.lexerMD.setDefaultColor(Theme.EditorC)
                        self.lexerMD.setDefaultFont(self.fontM)
                        self.lexerMD.setDefaultPaper(Theme.EditorBG)
                        self.setLexer(self.lexerMD)
      def setSettingsAutoComplete(self):
            self.autocomplete = QsciAPIs(self.lexerSettings)
            if self.path == getFiles.path5:
                  self.autocomplete.load("data/api/fe_settings/shortcuts.api")
            elif self.path == getFiles.path1:
                  self.autocomplete.load("data/api/fe_settings/settings.api")
            elif self.path == getFiles.path7:
                  self.autocomplete.load("data/api/fe_settings/font.api")
            elif self.path == getFiles.path2:
                  self.autocomplete.load("data/api/fe_settings/console.api")
            elif self.path == getFiles.path3:
                  self.autocomplete.load("data/api/fe_settings/editor.api")
            elif self.path == getFiles.path4:
                  self.autocomplete.load("data/api/fe_settings/syntaxC.api")
            elif self.path == getFiles.path9:
                  self.autocomplete.load("data/api/fe_settings/plugins_syntax.api")
            list = ["true?2","false?2","null?2"]
            for keyword in list:
                  self.autocomplete.add(keyword)
            self.autocomplete.prepare()
            self.setAutoCompletionThreshold(AutoCompletionDelay)
            self.setAutoCompletionSource(QsciScintilla.AcsAPIs)
            self.setAutoCompletionCaseSensitivity(False)
            self.setAutoCompletionReplaceWord(AutoCompletionReplaceWord)
            self.setAutoCompletionShowSingle(True)
            self.setAutoCompletionUseSingle(QsciScintilla.AcusNever)
            self.autoCompleteFromAll()
      def setJSONAutoComplete(self):
            self.autocomplete = QsciAPIs(self.lexerJSON)
            for words in Values:
                  self.autocomplete.add(words)
            if "json" in data:
                  for files in data["json"]:
                        self.autocomplete.load(files)
            self.autocomplete.prepare()
            self.setAutoCompletionThreshold(AutoCompletionDelay)
            self.setAutoCompletionSource(QsciScintilla.AcsAll)
            self.setAutoCompletionCaseSensitivity(False)
            self.setAutoCompletionReplaceWord(AutoCompletionReplaceWord)
            self.setAutoCompletionShowSingle(True)
            self.setAutoCompletionUseSingle(QsciScintilla.AcusNever)
            self.autoCompleteFromAll()
      def setPyAutoComplete(self):
            """Set autocompletion for python using api's and lists."""
            if (
                  self.isInPyComment(self.getCursorPosition()[0], self.getCursorPosition()[1]) or
                  self.isInDoubleQuotedStringPy() or
                  self.isInSingleQuotedStringPy() or 
                  self.isInTripleSingleQuotedStringPy() or 
                  self.isInTripleDoubleQuotedStringPy()
            ):
                  self.autocomplete = None
                  self.setAutoCompletionThreshold(0)
                  return
            self.autocomplete = QsciAPIs(self.lexerPy)
            for words in Methods:
                  self.autocomplete.add(words)
            for keywords in Keywords:
                  self.autocomplete.add(keywords)
            for words in PyOthers:
                  self.autocomplete.add(words)
            for words in builtin:
                  self.autocomplete.add(words)
            if "python" in data:
                  for file in data["python"]:
                        self.autocomplete.load(file)
                        print(f"loaded python")
            self.autocomplete.prepare()
            self.setAutoCompletionThreshold(AutoCompletionDelay)
            self.setAutoCompletionSource(QsciScintilla.AcsAll)
            self.setAutoCompletionCaseSensitivity(False)
            self.setAutoCompletionReplaceWord(AutoCompletionReplaceWord)
            self.setAutoCompletionShowSingle(True)
            self.setAutoCompletionFillupsEnabled(False)
            self.setAutoCompletionUseSingle(QsciScintilla.AcusNever)
            self.autoCompleteFromAll()
      def setFold(self):
            if TreeFoldStyleEnabled is True:
                  folding = QsciScintilla.FoldStyle(self.ArrowTreeFoldStyle)
            else:
                  folding = QsciScintilla.FoldStyle(self.ArrowFoldStyle)
            self.setCustomFolding(folding, self.fold_margin)
            self.requestFE(FE_SetMarginWidth, self.fold_margin, 14)
      def unsetFold(self):
            self.setFolding(0)
      def getlineAndCol(self, line, colm):
            self.parent.btn1.setText(f"Ln: {line}, Col: {colm}")
      def getFileName(self):
            if self.path:
                  return self.path
            else:
                  return None
      def undoAct(self):
            self.undo()
      def redoAct(self):
            self.redo()
      def setJsAutoComplete(self):
            self.setAutoCompletionCaseSensitivity(False)
            self.setAutoCompletionSource(QsciScintilla.AutoCompletionSource.AcsAll)
            self.setAutoCompletionThreshold(AutoCompletionDelay)
            self.updateAutoCompleteJs()
      def setHtmlAutoComplete(self):
            self.setAutoCompletionCaseSensitivity(False)
            self.setAutoCompletionSource(QsciScintilla.AutoCompletionSource.AcsAll)
            self.setAutoCompletionThreshold(AutoCompletionDelay)
            self.updateAutoCompleteHTM()
      def updateAutoCompleteJs(self, text=None):
            self.autocomplete = QsciAPIs(self.lexerJs)
            for words in jsKeywords:
                  self.autocomplete.add(words)
            for words in JSOthers:
                  self.autocomplete.add(words)
            if "javaScript" in data:
                  for files in data["javaScript"]:
                        self.autocomplete.load(files)
            if not text:
                  firstList = []   
                  secondList = []  
                  for item in secondList:
                        self.autocomplete.add(item)
                  self.autocomplete.prepare()
      def updateAutoCompleteHTM(self, text=None):
            self.autocomplete = QsciAPIs(self.lexerHTML)
            for words in HTMLOtherList:
                  self.autocomplete.add(words)
            for words in HTMLOthers:
                  self.autocomplete.add(words)
            for words in htmlTagList:
                  self.autocomplete.add(words)
            for words in htmlAttrList:
                  self.autocomplete.add(words)
            if "html" in data:
                  for files in data["html"]:
                        self.autocomplete.load(files)
            if not text:
                  firstList = []   
                  secondList = []  
                  for item in secondList:
                        self.autocomplete.add(item)
                  self.autocomplete.prepare()
      def setCSSAutoComplete(self):
            self.setAutoCompletionCaseSensitivity(False)
            self.setAutoCompletionSource(QsciScintilla.AutoCompletionSource.AcsAPIs)
            self.setAutoCompletionThreshold(AutoCompletionDelay)
            self.updateAutoCompleteCSS()
      def updateAutoCompleteCSS(self, text=None):
            self.autocomplete = QsciAPIs(self.lexerCSS)
            for words in CSSOtherList:
                  self.autocomplete.add(words)
            for words2 in CSSOther2:
                  self.autocomplete.add(words2)
            if "css" in data:
                  for files in data["css"]:
                        self.autocomplete.load(files)
            if not text:
                  firstList = []   
                  secondList = []
                  for item in secondList:
                        self.autocomplete.add(item)
                  self.autocomplete.prepare()
      def setPythonCallTips(self):
            self.setCallTipsStyle(CallTipsStyle)
            self.setCallTipsPosition(QsciScintilla.CallTipsAboveText)
            self.setCallTipsBackgroundColor(Theme.CallTipBG)
            self.setCallTipsForegroundColor(Theme.CallTipC)
            self.setCallTipsHighlightColor(Theme.HighlightedCallTip)
            self.setCallTipsVisible(0)
      def setCSSCallTips(self):
            self.setCallTipsStyle(CallTipsStyle)
            self.setCallTipsVisible(0)
      def character_added(self, character_no):
            if self.path:
                  file_ext = getFileExt(self.path)
                  if self.isPythonFile():
                        char = chr(character_no)
                        if char not in ['(', ')', '{', '}', '[', ']', ' ', ',', "'", '"','\n', ':']:
                              return
                        line = self.getCursorPosition()[0]
                        col = self.getCursorPosition()[1]
                        if (
                              self.isInPyComment(line, col) or
                              (char != '"' and self.isInDoubleQuotedStringPy()) or
                              (char != '"' and self.isInTripleDoubleQuotedStringPy()) or
                              (char != "'" and self.isInSingleQuotedStringPy()) or
                              (char != "'" and self.isInTripleSingleQuotedStringPy())
                        ):
                              return
                        if char == " ":
                              text = self.text(line)[:col]
                              if self.import_r.fullmatch(text):
                                    self.insert("import ")
                                    self.setCursorPosition(line, col + 7)            
                        elif char == "(":
                              text = self.text(line)[:col]
                              if CompleteBraces is True:
                                    if (
                                          self.def_r.fullmatch(text) is not None or
                                          self.class_r.fullmatch(text) is not None
                                    ):
                                          self.insert("):")
                                    else:
                                          self.insert(")")
                        if CompleteBraces is True:
                              if char == "{":
                                    self.insert("}")
                              elif char == "[":
                                    self.insert("]")
                              elif char == "'":
                                    self.insert("'")
                              elif char == '"':
                                    self.insert('"')
                              elif char == ',':
                                    self.insert(' ')
                                    self.setCursorPosition(line, col + 1)

                  elif self.isCSSFile():
                        char = chr(character_no)
                        line = self.getCursorPosition()[0]
                        col = self.getCursorPosition()[1]
                        if MagicTyping is True:
                                    if char == " ":
                                          text = self.text(line)[:col]
                                          for patterns in self.list_css_r:
                                                if patterns.fullmatch(text):
                                                      self.insert("{\n}")
                                                      self.setCursorPosition(line, col + 1)
                        if CompleteBraces is True:
                              char = chr(character_no)
                              line = self.getCursorPosition()[0]
                              col = self.getCursorPosition()[1]
                              if (
                              self.isInCSSComment(line, col) or
                              (char != '"' and self.isInDoubleQuotedStringCSS()) or
                              (char != "'" and self.isInSingleQuotedStringCSS())
                              ):
                                    return  
                              elif char == "(":
                                    self.insert(")")
                              elif char == "{":
                                    self.insert("}")
                              elif char == "[":
                                    self.insert("]")
                              elif char == "'":
                                    self.insert("'")
                              elif char == '"':
                                    self.insert('"')
                              elif char == ',':
                                    self.insert(' ')
                                    self.setCursorPosition(line, col + 1)
                  elif self.isJavaScriptFile():
                        if CompleteBraces is True:
                              char = chr(character_no)
                              line = self.getCursorPosition()[0]
                              col = self.getCursorPosition()[1]
                              if char == "(":
                                    self.insert(")")
                              elif char == "{":
                                    self.insert("}")
                              elif char == "[":
                                    self.insert("]")
                              elif char == "'":
                                    self.insert("'")
                              elif char == '"':
                                    self.insert('"')
                              elif char == ',':
                                    self.insert(' ')
                                    self.setCursorPosition(line, col + 1)
                  elif self.isHTMLFile():
                        if CompleteBraces is True:
                              char = chr(character_no)
                              line = self.getCursorPosition()[0]
                              col = self.getCursorPosition()[1]
                              if (
                              self.isInHTMLComment(line, col) or
                              (char != '"' and self.isInDoubleQuotedStringHTML()) or
                              (char != "'" and self.isInSingleQuotedStringHTML())
                              ):
                                    return
                              if char == " ":
                                    text = self.text(line)[:col]
                                    if self.U_doctype_r.fullmatch(text):
                                          self.insert("html")
                                          self.setCursorPosition(line, col + 5)
                              elif char == "(":
                                    self.insert(")")
                              elif char == "{":
                                    self.insert("}")
                              elif char == "[":
                                    self.insert("]")
                              elif char == "'":
                                    self.insert("'")
                              elif char == '"':
                                    self.insert('"')
                              elif char == "<":
                                    self.insert(">")
                              elif char == ">":
                                    line_ = self.getCursorPosition()[0]
                                    col = self.getCursorPosition()[1]
                                    line = self.text(line_)
                                    line = line.strip()
                                    if self.getCursorPosition()[0]+1 == 2:
                                          if "<!DOCTYPE html" in self.text() and "</html>" not in self.text():
                                                if line.startswith("<html"):
                                                      self.insert(
                                                            "\n\t<head>\n"
                                                            "\t\t<title>Document</title>\n"
                                                            '\t\t<meta charset="utf-8">\n'
                                                            "\t<head>\n"
                                                            "\t<body>\n"
                                                            "\t\t\n"
                                                            "\t</body>\n"
                                                            "</html>"
                                                      )
                                                      self.setSelection(line_+1, col+11, line_+1, col+19)
                                                      self.updateAutoCompleteHTM()
                                    
                              elif char == "/":
                                    self.updateAutoCompleteHTM()

                  elif self.isJSONFile() or self.isSettingFile():
                        if CompleteBraces is True:
                              char = chr(character_no)
                              line = self.getCursorPosition()[0]
                              col = self.getCursorPosition()[1]
                              if char == "(":
                                    self.insert(")")
                              elif char == "{":
                                    self.insert("}")
                              elif char == "[":
                                    self.insert("]")
                              elif char == "'":
                                    self.insert("'")
                              elif char == '"':
                                    self.insert('"')
                              elif char == ":":
                                    self.insert(" ")
                                    self.setCursorPosition(line, col + 1)
                  if self.isXMLFile():
                        if CompleteBraces is True:
                              char = chr(character_no)
                              line = self.getCursorPosition()[0]
                              col = self.getCursorPosition()[1]
                              if char == "(":
                                    self.insert(")")
                              elif char == "{":
                                    self.insert("}")
                              elif char == "[":
                                    self.insert("]")
                              elif char == "<":
                                    self.insert(">")
                              elif char == "'":
                                    self.insert("'")
                              elif char == '"':
                                    self.insert('"')
                  else:
                        if Typing_CompleteBraces is True:
                              char = chr(character_no)
                              line = self.getCursorPosition()[0]
                              col = self.getCursorPosition()[1]
                              if char == "(":
                                    self.insert(")")
                              elif char == "{":
                                    self.insert("}")
                              elif char == "[":
                                    self.insert("]")
                              elif char == "'":
                                    self.insert("'")
                              elif char == '"':
                                    self.insert('"')
      def isInPyComment(self, line, col):
            txt = self.text(line)
            if col == len(txt):
                  col -= 1
            while col >= 0:
                  if txt[col] == "#":
                        return True
                  col -= 1
            return False
      def isInHTMLComment(self, line, col):
            txt = self.text(line)
            if col == len(txt):
                  col -= 1
            while col >= 0:
                  if txt[col] == "<!--":
                        return True
                  col -= 1
            return False
      def isInCSSComment(self, line, col):
            txt = self.text(line)
            if col == len(txt):
                  col -= 1
            while col >= 0:
                  if txt[col] == "/*":
                        return True
                  col -= 1
            return False
      def currentBlockStyle(self, pos):
            return self.requestFE(FE_GetCurrentBlockStyle, pos)
      def currentStyle(self):
            currentPos = self.SendScintilla(QsciScintilla.SCI_GETCURRENTPOS)
            return self.currentBlockStyle(currentPos)
      def isInDoubleQuotedStringPy(self):
            return self.currentStyle() == QsciLexerPython.DoubleQuotedString
      def isInSingleQuotedStringPy(self):
            return self.currentStyle() == QsciLexerPython.SingleQuotedString
      def isInTripleDoubleQuotedStringPy(self):
            return self.currentStyle() == QsciLexerPython.TripleDoubleQuotedString
      def isInTripleSingleQuotedStringPy(self):
            return self.currentStyle() == QsciLexerPython.TripleSingleQuotedString
      def isInDoubleQuotedStringHTML(self):
            return self.currentStyle() == QsciLexerHTML.HTMLDoubleQuotedString
      def isInSingleQuotedStringHTML(self):
            return self.currentStyle() == QsciLexerHTML.HTMLSingleQuotedString
      def isInDoubleQuotedStringCSS(self):
            return self.currentStyle() == QsciLexerCSS.DoubleQuotedString
      def isInSingleQuotedStringCSS(self):
            return self.currentStyle() == QsciLexerCSS.SingleQuotedString
      def isHTMLFile(self):
            if self.path:
                  file_ext = getFileExt(self.path)
                  if file_ext == ".html" or file_ext == ".htm":
                        return True
      def isCSSFile(self):
            if self.path:
                  file_ext = getFileExt(self.path)
                  if file_ext == ".css" or file_ext == ".qss":
                        return True
      def isJavaScriptFile(self):
            if self.path:
                  file_ext = getFileExt(self.path)
                  if file_ext == ".js" or file_ext == ".jsx":
                        return True
      def isPythonFile(self):
            if self.path:
                  file_ext = getFileExt(self.path)
                  if file_ext == ".py" or file_ext == ".pyw" or file_ext == ".pyi" or file_ext == ".pyc" or file_ext == ".pyd":
                        return True
      def isJSONFile(self):
            if self.path:
                  file_ext = getFileExt(self.path)
                  if file_ext == ".json" or file_ext == ".jsonc":
                        return True
      def isSettingFile(self):
            if self.path:
                  file_ext = getFileExt(self.path)
                  if file_ext == ".fe_settings":
                        return True
      def isXMLFile(self):
            if self.path:
                  file_ext = getFileExt(self.path)
                  if file_ext == ".ui" or file_ext == ".xml":
                        return True
      def isJavaFile(self):
            if self.path:
                  file_ext = getFileExt(self.path)
                  if file_ext == ".java":
                        return True
      def isMarkDownFile(self):
            if self.path:
                  file_ext = getFileExt(self.path)
                  if file_ext == ".md":
                        return True
      def isCTypeFile(self):
            if self.path:
                  file_ext = getFileExt(self.path)
                  if file_ext == ".c" or file_ext == ".c++" or file_ext == ".h" or file_ext == ".cpp":
                        return True
      def isCSharpFile(self):
            if self.path:
                  file_ext = getFileExt(self.path)
                  if file_ext == ".cs" or file_ext == ".c#":
                        return True
      def getWordLength(self, line, index, useWordChars=True):
            return self.requestFE(FE_GetWordLength, line, index, useWordChars)
      def selectWord(self, line, index):
            start, end = self.getWordLength(line, index)
            self.setSelection(line, start, line, end)
      def selectCurrentWord(self):
            line, index = self.getCursorPosition()
            self.selectWord(line, index)
      def getWord(self, line, index, direction=0, useWordChars=True):
            start, end = self.getWordLength(line, index, useWordChars)
            if direction == 1:
                  end = index
            elif direction == 2:
                  start = index
            if end > start:
                  text = self.text(line)
                  word = text[start:end]
            else:
                  word = ''
            return word
      def getCurrentWord(self):
            line, col = self.getCursorPosition()
            return self.getWord(line, col)
      def match_same_words(self):
            word = self.getCurrentWord()
            if not word:
                  self.clearSearchIndicators()
                  return
        
            if self.marked_text == word:
                  return
        
            self.clearSearchIndicators()
            ok = self.findFirstTarget(word, False, self.caseSensitive(), True,
                                  0, 0)
            while ok:
                  tgtPos, tgtLen = self.getFoundTarget()
                  self.setSearchIndicator(tgtPos, tgtLen)
                  ok = self.findNextTarget()
            self.marked_text = word
      def setSearchIndicator(self, startPos, indicLength):
            self.set_indicator_range(12, startPos, indicLength)
            line = self.lineIndexFromPosition(startPos)[0]
            if line not in self.find_indicator_lines:
                  self.find_indicator_lines.append(line)
      def clearSearchIndicators(self):
            self.clearAllIndicators(12)
            self.marked_text = ""
            self.find_indicator_lines = []