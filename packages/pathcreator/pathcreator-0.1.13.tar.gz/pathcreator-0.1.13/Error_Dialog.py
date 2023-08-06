# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Error_Dialog.ui'
#
# Created: Wed Aug 26 11:46:37 2009
#      by: PyQt4 UI code generator 4.3.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Dialog_Error(object):
    def setupUi(self, Dialog_Error):
        Dialog_Error.setObjectName("Dialog_Error")
        Dialog_Error.resize(QtCore.QSize(QtCore.QRect(0,0,396,127).size()).expandedTo(Dialog_Error.minimumSizeHint()))

        self.gridlayout = QtGui.QGridLayout(Dialog_Error)
        self.gridlayout.setObjectName("gridlayout")

        self.label = QtGui.QLabel(Dialog_Error)

        font = QtGui.QFont()
        font.setPointSize(15)
        font.setWeight(75)
        font.setBold(True)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.gridlayout.addWidget(self.label,0,0,1,1)

        self.textEdit = QtGui.QTextEdit(Dialog_Error)
        self.textEdit.setReadOnly(True)
        self.textEdit.setObjectName("textEdit")
        self.gridlayout.addWidget(self.textEdit,0,1,1,1)

        self.pushButton = QtGui.QPushButton(Dialog_Error)
        self.pushButton.setObjectName("pushButton")
        self.gridlayout.addWidget(self.pushButton,1,1,1,1)

        self.retranslateUi(Dialog_Error)
        QtCore.QObject.connect(self.pushButton,QtCore.SIGNAL("clicked()"),Dialog_Error.accept)
        QtCore.QMetaObject.connectSlotsByName(Dialog_Error)

    def retranslateUi(self, Dialog_Error):
        Dialog_Error.setWindowTitle(QtGui.QApplication.translate("Dialog_Error", "Error", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Dialog_Error", "Error:", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton.setText(QtGui.QApplication.translate("Dialog_Error", "Close", None, QtGui.QApplication.UnicodeUTF8))

