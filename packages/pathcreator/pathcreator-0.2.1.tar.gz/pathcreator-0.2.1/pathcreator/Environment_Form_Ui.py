# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Environment_Form.ui'
#
# Created: Fri Oct  9 15:40:52 2009
#      by: PyQt4 UI code generator 4.3.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_EnvironmentFrom(object):
    def setupUi(self, EnvironmentFrom):
        EnvironmentFrom.setObjectName("EnvironmentFrom")
        EnvironmentFrom.resize(QtCore.QSize(QtCore.QRect(0,0,368,137).size()).expandedTo(EnvironmentFrom.minimumSizeHint()))

        self.dockWidgetContents = QtGui.QWidget(EnvironmentFrom)
        self.dockWidgetContents.setGeometry(QtCore.QRect(0,23,368,114))
        self.dockWidgetContents.setObjectName("dockWidgetContents")

        self.gridlayout = QtGui.QGridLayout(self.dockWidgetContents)
        self.gridlayout.setObjectName("gridlayout")

        self.label_SpeedOfSound = QtGui.QLabel(self.dockWidgetContents)
        self.label_SpeedOfSound.setObjectName("label_SpeedOfSound")
        self.gridlayout.addWidget(self.label_SpeedOfSound,0,0,1,1)

        self.lineEdit_SpeedOfSound = QtGui.QLineEdit(self.dockWidgetContents)
        self.lineEdit_SpeedOfSound.setObjectName("lineEdit_SpeedOfSound")
        self.gridlayout.addWidget(self.lineEdit_SpeedOfSound,0,1,1,1)

        self.label_NFBins = QtGui.QLabel(self.dockWidgetContents)
        self.label_NFBins.setObjectName("label_NFBins")
        self.gridlayout.addWidget(self.label_NFBins,1,0,1,1)

        self.comboBox_NFBins = QtGui.QComboBox(self.dockWidgetContents)
        self.comboBox_NFBins.setEditable(False)
        self.comboBox_NFBins.setMinimumContentsLength(0)
        self.comboBox_NFBins.setObjectName("comboBox_NFBins")
        self.gridlayout.addWidget(self.comboBox_NFBins,1,1,1,1)

        self.pushButton_Load = QtGui.QPushButton(self.dockWidgetContents)
        self.pushButton_Load.setObjectName("pushButton_Load")
        self.gridlayout.addWidget(self.pushButton_Load,1,2,1,1)

        self.label_ChunkSize = QtGui.QLabel(self.dockWidgetContents)
        self.label_ChunkSize.setObjectName("label_ChunkSize")
        self.gridlayout.addWidget(self.label_ChunkSize,2,0,1,1)

        self.lineEdit_ChunkSize = QtGui.QLineEdit(self.dockWidgetContents)
        self.lineEdit_ChunkSize.setObjectName("lineEdit_ChunkSize")
        self.gridlayout.addWidget(self.lineEdit_ChunkSize,2,1,1,1)

        self.pushButton_Save = QtGui.QPushButton(self.dockWidgetContents)
        self.pushButton_Save.setObjectName("pushButton_Save")
        self.gridlayout.addWidget(self.pushButton_Save,2,2,1,1)
        EnvironmentFrom.setWidget(self.dockWidgetContents)
        self.label_SpeedOfSound.setBuddy(self.lineEdit_SpeedOfSound)
        self.label_NFBins.setBuddy(self.comboBox_NFBins)
        self.label_ChunkSize.setBuddy(self.lineEdit_ChunkSize)

        self.retranslateUi(EnvironmentFrom)
        QtCore.QMetaObject.connectSlotsByName(EnvironmentFrom)

    def retranslateUi(self, EnvironmentFrom):
        EnvironmentFrom.setWindowTitle(QtGui.QApplication.translate("EnvironmentFrom", "Environment Settings", None, QtGui.QApplication.UnicodeUTF8))
        self.label_SpeedOfSound.setText(QtGui.QApplication.translate("EnvironmentFrom", "Speed of Sound:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_NFBins.setText(QtGui.QApplication.translate("EnvironmentFrom", "Number of Frequency Bins:", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_Load.setText(QtGui.QApplication.translate("EnvironmentFrom", "Load", None, QtGui.QApplication.UnicodeUTF8))
        self.label_ChunkSize.setText(QtGui.QApplication.translate("EnvironmentFrom", "Chunk Size:", None, QtGui.QApplication.UnicodeUTF8))
        self.lineEdit_ChunkSize.setToolTip(QtGui.QApplication.translate("EnvironmentFrom", "number of samples to be rendered as a single location", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_Save.setText(QtGui.QApplication.translate("EnvironmentFrom", "Save", None, QtGui.QApplication.UnicodeUTF8))

