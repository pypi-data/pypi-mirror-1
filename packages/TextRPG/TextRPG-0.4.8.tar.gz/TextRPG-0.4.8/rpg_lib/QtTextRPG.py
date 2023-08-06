#!/usr/bin/env python
# encoding: utf-8

from __future__ import division
import sys
from math import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *

class Form(QDialog):
 def __init__(self, parent=None):
  super(Form, self).__init__(parent)
  self.browser = QTextBrowser()
  self.lineedit = QLineEdit("Type an expression and press Enter")
  self.lineedit.selectAll()
  layout = QVBoxLayout()
  layout.addWidget(self.browser)
  layout.addWidget(self.lineedit)
  self.setLayout(layout)
  self.lineedit.setFocus()
  self.connect(self.lineedit, SIGNAL("returnPressed()"), self.updateUi)
  self.setWindowTitle("Calculate")

 def updateUi(self):
  try:
   text = unicode(self.lineedit.text())
   self.browser.append(str(text) + " = <b>" + str(eval(text)) + "</b>")
  except:
   self.browser.append("<font color=red>" + str(text) + " is invalid!</font>"
)

app = QApplication(sys.argv)
form = Form()
form.show()
app.exec_()

# Thread: Is it possible to pass the script file to the program to get it into a seperate thread? 
# Instead of threading: Seperate processes, communicating via tcp/sockets -> Networked games possible. 
