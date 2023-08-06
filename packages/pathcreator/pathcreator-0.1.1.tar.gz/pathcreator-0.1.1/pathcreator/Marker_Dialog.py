# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Marker_Dialog.ui'
#
# Created: Mon Oct 26 12:11:08 2009
#      by: PyQt4 UI code generator 4.3.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Add_Marker_Dialog(object):
    def setupUi(self, Add_Marker_Dialog):
        Add_Marker_Dialog.setObjectName("Add_Marker_Dialog")
        Add_Marker_Dialog.resize(QtCore.QSize(QtCore.QRect(0,0,382,250).size()).expandedTo(Add_Marker_Dialog.minimumSizeHint()))

        self.gridlayout = QtGui.QGridLayout(Add_Marker_Dialog)
        self.gridlayout.setObjectName("gridlayout")

        self.groupBox_Markers = QtGui.QGroupBox(Add_Marker_Dialog)
        self.groupBox_Markers.setObjectName("groupBox_Markers")

        self.hboxlayout = QtGui.QHBoxLayout(self.groupBox_Markers)
        self.hboxlayout.setObjectName("hboxlayout")

        self.listWidget_Markers = QtGui.QListWidget(self.groupBox_Markers)
        self.listWidget_Markers.setObjectName("listWidget_Markers")
        self.hboxlayout.addWidget(self.listWidget_Markers)
        self.gridlayout.addWidget(self.groupBox_Markers,0,0,4,1)

        self.pushButton_Set_Marker = QtGui.QPushButton(Add_Marker_Dialog)
        self.pushButton_Set_Marker.setObjectName("pushButton_Set_Marker")
        self.gridlayout.addWidget(self.pushButton_Set_Marker,0,1,1,1)

        self.pushButton_New_Marker = QtGui.QPushButton(Add_Marker_Dialog)
        self.pushButton_New_Marker.setObjectName("pushButton_New_Marker")
        self.gridlayout.addWidget(self.pushButton_New_Marker,1,1,1,1)

        self.pushButton_Cancel = QtGui.QPushButton(Add_Marker_Dialog)
        self.pushButton_Cancel.setObjectName("pushButton_Cancel")
        self.gridlayout.addWidget(self.pushButton_Cancel,2,1,1,1)

        spacerItem = QtGui.QSpacerItem(20,127,QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Expanding)
        self.gridlayout.addItem(spacerItem,3,1,1,1)

        self.retranslateUi(Add_Marker_Dialog)
        QtCore.QMetaObject.connectSlotsByName(Add_Marker_Dialog)

    def retranslateUi(self, Add_Marker_Dialog):
        Add_Marker_Dialog.setWindowTitle(QtGui.QApplication.translate("Add_Marker_Dialog", "Add a Marker?", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_Markers.setTitle(QtGui.QApplication.translate("Add_Marker_Dialog", "Markers", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_Set_Marker.setText(QtGui.QApplication.translate("Add_Marker_Dialog", "Set Marker", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_New_Marker.setText(QtGui.QApplication.translate("Add_Marker_Dialog", "New Marker", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_Cancel.setText(QtGui.QApplication.translate("Add_Marker_Dialog", "Cancel", None, QtGui.QApplication.UnicodeUTF8))

