# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Point_Dialog.ui'
#
# Created: Thu Sep 10 11:29:22 2009
#      by: PyQt4 UI code generator 4.3.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Dialog_New_Point(object):
    def setupUi(self, Dialog_New_Point):
        Dialog_New_Point.setObjectName("Dialog_New_Point")
        Dialog_New_Point.resize(QtCore.QSize(QtCore.QRect(0,0,248,152).size()).expandedTo(Dialog_New_Point.minimumSizeHint()))

        self.gridlayout = QtGui.QGridLayout(Dialog_New_Point)
        self.gridlayout.setObjectName("gridlayout")

        self.label = QtGui.QLabel(Dialog_New_Point)
        self.label.setObjectName("label")
        self.gridlayout.addWidget(self.label,0,0,1,1)

        self.lineEdit_X = QtGui.QLineEdit(Dialog_New_Point)
        self.lineEdit_X.setObjectName("lineEdit_X")
        self.gridlayout.addWidget(self.lineEdit_X,0,1,1,1)

        self.label_2 = QtGui.QLabel(Dialog_New_Point)
        self.label_2.setObjectName("label_2")
        self.gridlayout.addWidget(self.label_2,1,0,1,1)

        self.lineEdit_Y = QtGui.QLineEdit(Dialog_New_Point)
        self.lineEdit_Y.setObjectName("lineEdit_Y")
        self.gridlayout.addWidget(self.lineEdit_Y,1,1,1,1)

        self.label_3 = QtGui.QLabel(Dialog_New_Point)
        self.label_3.setObjectName("label_3")
        self.gridlayout.addWidget(self.label_3,2,0,1,1)

        self.lineEdit_Z = QtGui.QLineEdit(Dialog_New_Point)
        self.lineEdit_Z.setObjectName("lineEdit_Z")
        self.gridlayout.addWidget(self.lineEdit_Z,2,1,1,1)

        self.buttonBox = QtGui.QDialogButtonBox(Dialog_New_Point)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridlayout.addWidget(self.buttonBox,3,1,1,1)
        self.label.setBuddy(self.lineEdit_X)
        self.label_2.setBuddy(self.lineEdit_Y)
        self.label_3.setBuddy(self.lineEdit_Z)

        self.retranslateUi(Dialog_New_Point)
        QtCore.QObject.connect(self.buttonBox,QtCore.SIGNAL("accepted()"),Dialog_New_Point.accept)
        QtCore.QObject.connect(self.buttonBox,QtCore.SIGNAL("rejected()"),Dialog_New_Point.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog_New_Point)
        Dialog_New_Point.setTabOrder(self.lineEdit_X,self.lineEdit_Y)
        Dialog_New_Point.setTabOrder(self.lineEdit_Y,self.lineEdit_Z)
        Dialog_New_Point.setTabOrder(self.lineEdit_Z,self.buttonBox)

    def retranslateUi(self, Dialog_New_Point):
        Dialog_New_Point.setWindowTitle(QtGui.QApplication.translate("Dialog_New_Point", "New Point", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Dialog_New_Point", "X Position:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("Dialog_New_Point", "Y Position:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("Dialog_New_Point", "Z Position:", None, QtGui.QApplication.UnicodeUTF8))

