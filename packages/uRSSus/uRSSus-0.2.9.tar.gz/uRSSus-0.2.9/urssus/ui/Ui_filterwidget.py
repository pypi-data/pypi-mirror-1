# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'urssus/ui/filterwidget.ui'
#
# Created: Sun Aug  3 19:33:02 2008
#      by: PyQt4 UI code generator 4.4.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(559,28)
        self.horizontalLayout = QtGui.QHBoxLayout(Form)
        self.horizontalLayout.setMargin(0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.clear = QtGui.QToolButton(Form)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/editclear.svg"),QtGui.QIcon.Normal,QtGui.QIcon.Off)
        self.clear.setIcon(icon)
        self.clear.setAutoRaise(True)
        self.clear.setObjectName("clear")
        self.horizontalLayout.addWidget(self.clear)
        self.label = QtGui.QLabel(Form)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.filter = QtGui.QLineEdit(Form)
        self.filter.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.filter.setObjectName("filter")
        self.horizontalLayout.addWidget(self.filter)
        self.label_2 = QtGui.QLabel(Form)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout.addWidget(self.label_2)
        self.statusCombo = QtGui.QComboBox(Form)
        self.statusCombo.setFocusPolicy(QtCore.Qt.NoFocus)
        self.statusCombo.setObjectName("statusCombo")
        self.horizontalLayout.addWidget(self.statusCombo)
        self.label.setBuddy(self.filter)
        self.label_2.setBuddy(self.statusCombo)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QtGui.QApplication.translate("Form", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.clear.setText(QtGui.QApplication.translate("Form", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Form", "Sear&ch:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("Form", "Status:", None, QtGui.QApplication.UnicodeUTF8))
        self.statusCombo.addItem(QtGui.QApplication.translate("Form", "All Articles", None, QtGui.QApplication.UnicodeUTF8))
        self.statusCombo.addItem(QtGui.QApplication.translate("Form", "Unread", None, QtGui.QApplication.UnicodeUTF8))
        self.statusCombo.addItem(QtGui.QApplication.translate("Form", "Important", None, QtGui.QApplication.UnicodeUTF8))

import icons_rc
