from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import sys
import os
import json
import methods

loc = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/"
path = os.path.join(loc, "data/user/user-data.json")
with open(path, "r") as file:
	_text = file.read()
data = json.loads(_text)

class Done(QMessageBox):
	def __init__(self):
		super().__init__()
		self.setText("<h3>Registered successfully!</h3>")
		self.setWindowTitle("Info!")

class RegisterForm(QWidget):
	def __init__(self, parent=None):
		super(RegisterForm, self).__init__(parent)
		self.setFixedSize(500,600)
		self.setWindowTitle("Register - SM FastEdit")
		self.setWindowIcon(QIcon("Images\\txteditor.png"))
		layout = QVBoxLayout(self)
		heading = QLabel("""
			<h1>Register to SM FastEdit</h1>
			<p>Register now with SM FastEdit to secure your files and projects.</p>
			<p><b>Note:</b> App will close after this process. And after <br>registering to app you will not be able to edit data again.</p>
		""")
		heading.setFixedHeight(120)
		self.nameField = QLineEdit()
		self.nameField.setPlaceholderText("Your Name...")
		self.emailField = QLineEdit()
		self.emailField.setPlaceholderText("Your Email...")
		self.passwordField = QLineEdit()
		self.passwordField.setPlaceholderText("Create Password...")
		self.phoneNumberField = QLineEdit()
		self.phoneNumberField.setPlaceholderText("Your Phone Number...")
		registerButton = QPushButton("Register")
		registerButton.clicked.connect(self.register)
		layout.addWidget(heading)
		layout.addWidget(self.nameField)
		layout.addWidget(self.emailField)
		layout.addWidget(self.passwordField)
		layout.addWidget(self.phoneNumberField)
		layout.addWidget(registerButton)
	def saveName(self):
		methods.updateJson(path, "user-name", f"{self.nameField.text()}")
		self.parent.username = self.nameField.text()
	def saveEmail(self):
		methods.updateJson(path, "user-email", f"{self.emailField.text()}")
	def savePassword(self):
		methods.updateJson(path, "password", f"{self.passwordField.text()}")
	def savePhoneNumber(self):
		if self.phoneNumberField.text() is None or self.passwordField.text() == "":
			return
		methods.updateJson(path, "phone", f"{self.phoneNumberField.text()}")
	def register(self):
		if self.nameField.text() is None or self.nameField.text() == "":
			return
		if self.emailField.text() is None or self.emailField.text() == "":
			return
		if self.passwordField.text() is None or self.passwordField.text() == "":
			return
		self.saveName()
		self.saveEmail()
		self.savePassword()
		self.savePhoneNumber()
		self.close()
		self.done = Done()
		self.done.show()
		methods.updateJson(path, "registered", True)
		self.parent.registered = data["registered"]
		self.parent.setRegistered()
		self.parent.checkIfSignedIn()
		self.parent.reloadSettings()