from PyQt5.QtWidgets import *
from PyQt5.QtCore import QCoreApplication, QProcess, QSize, Qt
from settings.theme import *
from settings.font import *
from settings.settings import *
from data.stylesheets import *
import os
import json
import methods

loc = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/"
path = os.path.join(loc, "data/user/user-data.json")
with open(path, "r") as file:
      _text = file.read()
data = json.loads(_text)

pathShortcuts = os.path.join(loc, "settings/settings_folder/keybindings.fe_settings")
with open(pathShortcuts, "r") as file:
      _text2 = file.read()
shortcuts = json.loads(_text2)

class Assistant(QWidget):
      """Assistant widget"""
      def __init__(self, parent=None):
          super(Assistant, self).__init__(parent)
          methods.registerObject(self)
          self.commandArea = QLineEdit()
          self.commandArea.setObjectName("commandArea")
          self.commandArea.setPlaceholderText("Ask your question here...")
          self.commandArea.returnPressed.connect(self.push)
          self.outputArea  = QPlainTextEdit()
          self.outputArea.moveCursor(QTextCursor.EndOfLine)
          self.outputArea.setReadOnly(True)
          self.outputArea.setObjectName("outputArea")
          self.tell(f"Hello {self.userName()}")
          font = QFont()
          font.setFamily(FontFamily.Console)
          font.setPointSizeF(FontSize.FontSizeTerminal)
          self.outputArea.setFont(font)
          layout = QVBoxLayout(self)
          layout.addWidget(self.outputArea)
          layout.addWidget(self.commandArea)
          layout.setContentsMargins(0,0,0,0)
          layout.setSpacing(0)
          self.outputArea.verticalScrollBar().setContextMenuPolicy(Qt.NoContextMenu)
          self.commandArea.setContextMenuPolicy(Qt.NoContextMenu)
          self.onStart()
      def push(self):
            self.parent.statusBar().showMessage("", 2000)
            __text = self.commandArea.text()
            if __text:
                  if __text == "hello":
                        self.reply("Hi, friend!")
                  elif not __text.islower() and not __text.isupper():
                        self.reply("Sorry for this, but I can only understand lower text!")
                  elif __text == "how are you":
                        self.reply("I am fine.")
                  elif __text == "who are you":
                        self.reply("I am your assistant, my name is Assistant.")
                  elif "your name" in __text:
                        self.reply("My name is Assistant.")
                  elif "my name" in __text:
                        n = self.userName()
                        if n == "":
                              self.reply("I don't know your name. Please sign in!")
                              return
                        self.reply(f"Your name is {n}")
                  elif "change_name()" in __text:
                        self.saveNameDlg()
                        self.reply("But you will need to restart App to apply.")
                  elif "what is my name" in __text:
                        self.reply("I don't know but if can you tell me your name?")
                  elif __text == "what can you do":
                        self.reply("I can do basic things but I can tell you how to use SM FastEdit.")
                  elif "open a file" in __text or "open file" in __text:
                        self.reply("Click on Open File in menu bar or simply press 'Ctrl+O'.") 
                  elif "open dir" in __text or "open folder" in __text or "open folder" in __text:
                        self.reply("Click on Open Folder or simply press 'Ctrl+Shift+O'")
                  elif "save a file" in __text:
                        self.reply("Click on Save File in menu bar or simply press 'Ctrl+S'.") 
                  elif "save file as" in __text or "save as" in __text:
                        self.reply("Click on Save File As in menu bar or simply press 'Ctrl+Shift+S'.") 
                  elif "new file" in __text or "new tab" in __text:
                        self.reply("Click on New File in menu bar or simply press 'Ctrl+N'.") 
                  elif "new window" in __text:
                        self.reply("Click on New Window in menu bar or simply press 'Ctrl+Shift+N'.")
                  elif "run" in __text:
                        self.reply("Click on Run File button in status bar or simply press 'F5'.")
                  elif "good" in __text or "excellent" in __text:
                        self.reply("Thanks for your feedback😊. Please also support us on github!")
                  elif "bad" in __text:
                        self.reply("Sorry for inconvinience. Please report your issue on github!")
                  elif "thanks" in __text:
                        self.reply("Your welcome!😊")
                  elif "are you happy" in __text:
                        self.reply("Absolutely! What about you?")
                  elif "fine" in __text:
                        self.reply("Ok")
                  elif __text == "save()":
                        self.parent.saveFile()
                        self.reply(f"Saved current file.")
                  elif __text == "new()":
                        self.parent.new_file()
                        self.reply(f"Created a new file.")
                  elif __text == "current file":
                        if self.parent.tabWidget.currentWidget():
                              name = self.parent.tabWidget.tabText(self.parent.tabWidget.currentIndex())
                              self.reply(f"Current file is {name}")
                        else:
                              self.reply("No file detected in editor area!")
                  elif "about" in __text:
                        self.reply("""
                        <h1>About</h1>
                        <p>SM FastEdit is a open-source code editor created by Shaurya Mishra.</p>
                        """)
                  elif __text == "clear()":
                        self.outputArea.clear()
                  elif __text == "help()":
                        self.reply('Type "clear()" to clear chat, "help()" for help.')
                  elif __text == "keymap" or __text == "shortcuts" or "edit shortcuts" in __text:
                        path = os.path.join(loc, "settings/keybindings.json")
                        self.parent.openFile(path)
                        self.reply("Opened Keymap.")
                  elif "console settings" in __text or "config run" in __text or "edit console" in __text:
                        path = os.path.join(loc, "settings/console.json")
                        self.parent.openFile(path)
                        self.reply("Opened Keymap.")
                  elif __text == "shortcut: open file":
                        s = shortcuts["OpenFile"]
                        self.reply(f"{s}")
                  elif __text == "shortcut: save file":
                        s = shortcuts["SaveFile"]
                        self.reply(f"{s}")
                  elif __text == "shortcut: create a new file":
                        s = shortcuts["NewFile"]
                        self.reply(f"{s}")
                  elif __text == "shortcut: save file as":
                        s = shortcuts["SaveFileAs"]
                        self.reply(f"{s}")
                  elif "report" in __text:
                        self.reply("""
                        <ul>
                              <li>1. Create a file named 'report.txt'</li>
                              <li>2. Now attach this file and send a email to <i>coderguru-web@gmail.com</i></li>
                              <li>3. In two to three days you will get respone. Thank you!</li>
                        </ul>
                        """)
                  elif __text == "user_info()":
                        email = data["user-email"]
                        phone = data["phone"]
                        self.reply(f"<br>Name: {self.userName()}<br>Email: {email}<br>Phone Number: {phone}")
                  elif __text == "file_info()":
                        if self.parent.tabWidget.currentWidget():
                              if self.parent.tabWidget.currentWidget().path is None:
                                    return
                              path = self.parent.tabWidget.currentWidget().path
                              self.reply(f"<br>{methods.getFileInfo(path)}")
                        else:
                              self.reply("No file in editor!")
                  elif "themes" in __text:
                        self.reply("""
                              There are 3 themes is editor:
                              <ul>
                                    <li>1. Dark Theme (default)</li>
                                    <li>2. Light Theme</li>
                                    <li>3. Classic Theme</li>
                              </ul>
                        """)
                  elif __text == "dark_theme()" or __text == "default_theme()":
                        self.parent.defaultTheme()
                        self.reply("Dark Theme selected.")
                  elif __text == "light_theme()":
                        self.parent.lightTheme()
                        self.reply("Light Theme selected.")
                  elif __text == "classic_theme()":
                        self.parent.noTheme()
                        self.reply("Classic Theme selected.")
                  else:
                        return
                  self.commandArea.clear()
            else:
                  return
      def userName(self):
            text = self.parent.username
            return text
      def tell(self, text):
            self.outputArea.appendHtml(f"<span style='color:#158cee;'>Assistant:</span> {text}")
            self.parent.statusBar().showMessage("1 New Message - Assistant", 2000)
      def reply(self, text):
            __text = self.commandArea.text()
            self.outputArea.appendHtml(f"<span style='color:#158cee;'>You: </span>{__text}")
            self.outputArea.appendHtml(f"<span style='color:#158cee;'>Assistant:</span> {text}")
      def onStart(self):
            ...