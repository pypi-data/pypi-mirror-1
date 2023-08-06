# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Path_Point_Dialog.ui'
#
# Created: Tue Oct 27 14:20:13 2009
#      by: PyQt4 UI code generator 4.3.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Add_Point_Dialog(object):
    def setupUi(self, Add_Point_Dialog):
        Add_Point_Dialog.setObjectName("Add_Point_Dialog")
        Add_Point_Dialog.resize(QtCore.QSize(QtCore.QRect(0,0,379,251).size()).expandedTo(Add_Point_Dialog.minimumSizeHint()))

        self.gridlayout = QtGui.QGridLayout(Add_Point_Dialog)
        self.gridlayout.setObjectName("gridlayout")

        self.groupBox = QtGui.QGroupBox(Add_Point_Dialog)
        self.groupBox.setObjectName("groupBox")

        self.hboxlayout = QtGui.QHBoxLayout(self.groupBox)
        self.hboxlayout.setObjectName("hboxlayout")

        self.listWidget_Points = QtGui.QListWidget(self.groupBox)
        self.listWidget_Points.setObjectName("listWidget_Points")
        self.hboxlayout.addWidget(self.listWidget_Points)
        self.gridlayout.addWidget(self.groupBox,0,0,4,1)

        self.pushButton_Set_Point = QtGui.QPushButton(Add_Point_Dialog)
        self.pushButton_Set_Point.setObjectName("pushButton_Set_Point")
        self.gridlayout.addWidget(self.pushButton_Set_Point,0,1,1,1)

        self.pushButton_New_Point = QtGui.QPushButton(Add_Point_Dialog)
        self.pushButton_New_Point.setObjectName("pushButton_New_Point")
        self.gridlayout.addWidget(self.pushButton_New_Point,1,1,1,1)

        self.pushButton_Cancel = QtGui.QPushButton(Add_Point_Dialog)
        self.pushButton_Cancel.setObjectName("pushButton_Cancel")
        self.gridlayout.addWidget(self.pushButton_Cancel,2,1,1,1)

        spacerItem = QtGui.QSpacerItem(20,119,QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Expanding)
        self.gridlayout.addItem(spacerItem,3,1,1,1)

        self.retranslateUi(Add_Point_Dialog)
        QtCore.QMetaObject.connectSlotsByName(Add_Point_Dialog)

    def retranslateUi(self, Add_Point_Dialog):
        Add_Point_Dialog.setWindowTitle(QtGui.QApplication.translate("Add_Point_Dialog", "Add a Point?", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("Add_Point_Dialog", "Points", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_Set_Point.setText(QtGui.QApplication.translate("Add_Point_Dialog", "Set Point", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_New_Point.setText(QtGui.QApplication.translate("Add_Point_Dialog", "New Point", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_Cancel.setText(QtGui.QApplication.translate("Add_Point_Dialog", "Cancel", None, QtGui.QApplication.UnicodeUTF8))

