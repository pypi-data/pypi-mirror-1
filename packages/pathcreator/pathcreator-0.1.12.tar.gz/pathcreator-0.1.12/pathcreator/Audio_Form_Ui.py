# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Audio_Form.ui'
#
# Created: Tue Oct 20 13:16:27 2009
#      by: PyQt4 UI code generator 4.3.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_AudioForm(object):
    def setupUi(self, AudioForm):
        AudioForm.setObjectName("AudioForm")
        AudioForm.resize(QtCore.QSize(QtCore.QRect(0,0,744,322).size()).expandedTo(AudioForm.minimumSizeHint()))

        self.dockWidgetContents = QtGui.QWidget(AudioForm)
        self.dockWidgetContents.setGeometry(QtCore.QRect(0,23,744,299))
        self.dockWidgetContents.setObjectName("dockWidgetContents")

        self.gridlayout = QtGui.QGridLayout(self.dockWidgetContents)
        self.gridlayout.setObjectName("gridlayout")

        self.frame = QtGui.QFrame(self.dockWidgetContents)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame.sizePolicy().hasHeightForWidth())
        self.frame.setSizePolicy(sizePolicy)
        self.frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtGui.QFrame.Raised)
        self.frame.setObjectName("frame")

        self.gridlayout1 = QtGui.QGridLayout(self.frame)
        self.gridlayout1.setObjectName("gridlayout1")

        self.graphicsView_Audio = QtGui.QGraphicsView(self.frame)
        self.graphicsView_Audio.setMinimumSize(QtCore.QSize(400,100))
        self.graphicsView_Audio.setMaximumSize(QtCore.QSize(16777215,120))
        self.graphicsView_Audio.setObjectName("graphicsView_Audio")
        self.gridlayout1.addWidget(self.graphicsView_Audio,0,0,1,5)

        self.label_start_time = QtGui.QLabel(self.frame)
        self.label_start_time.setObjectName("label_start_time")
        self.gridlayout1.addWidget(self.label_start_time,1,0,1,1)

        spacerItem = QtGui.QSpacerItem(265,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.gridlayout1.addItem(spacerItem,1,1,1,1)

        self.label_current_time = QtGui.QLabel(self.frame)
        self.label_current_time.setObjectName("label_current_time")
        self.gridlayout1.addWidget(self.label_current_time,1,2,1,1)

        spacerItem1 = QtGui.QSpacerItem(265,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.gridlayout1.addItem(spacerItem1,1,3,1,1)

        self.label_end_time = QtGui.QLabel(self.frame)
        self.label_end_time.setObjectName("label_end_time")
        self.gridlayout1.addWidget(self.label_end_time,1,4,1,1)
        self.gridlayout.addWidget(self.frame,0,0,1,1)

        self.gridlayout2 = QtGui.QGridLayout()
        self.gridlayout2.setObjectName("gridlayout2")

        self.label_4 = QtGui.QLabel(self.dockWidgetContents)
        self.label_4.setObjectName("label_4")
        self.gridlayout2.addWidget(self.label_4,0,0,1,1)

        self.lineEdit_Filename = QtGui.QLineEdit(self.dockWidgetContents)
        self.lineEdit_Filename.setObjectName("lineEdit_Filename")
        self.gridlayout2.addWidget(self.lineEdit_Filename,0,1,1,2)

        self.label_5 = QtGui.QLabel(self.dockWidgetContents)
        self.label_5.setObjectName("label_5")
        self.gridlayout2.addWidget(self.label_5,0,3,1,1)

        self.lineEdit_Length = QtGui.QLineEdit(self.dockWidgetContents)
        self.lineEdit_Length.setObjectName("lineEdit_Length")
        self.gridlayout2.addWidget(self.lineEdit_Length,0,4,1,2)

        self.label_6 = QtGui.QLabel(self.dockWidgetContents)
        self.label_6.setObjectName("label_6")
        self.gridlayout2.addWidget(self.label_6,0,6,1,1)

        self.lineEdit_Current_Point = QtGui.QLineEdit(self.dockWidgetContents)
        self.lineEdit_Current_Point.setObjectName("lineEdit_Current_Point")
        self.gridlayout2.addWidget(self.lineEdit_Current_Point,0,7,1,2)

        self.pushButton_Open_File = QtGui.QPushButton(self.dockWidgetContents)
        self.pushButton_Open_File.setObjectName("pushButton_Open_File")
        self.gridlayout2.addWidget(self.pushButton_Open_File,0,9,1,1)

        self.groupBox = QtGui.QGroupBox(self.dockWidgetContents)
        self.groupBox.setObjectName("groupBox")

        self.vboxlayout = QtGui.QVBoxLayout(self.groupBox)
        self.vboxlayout.setObjectName("vboxlayout")

        self.pushButton_Zoom_In = QtGui.QPushButton(self.groupBox)
        self.pushButton_Zoom_In.setObjectName("pushButton_Zoom_In")
        self.vboxlayout.addWidget(self.pushButton_Zoom_In)

        self.pushButton_Zoom_Out = QtGui.QPushButton(self.groupBox)
        self.pushButton_Zoom_Out.setObjectName("pushButton_Zoom_Out")
        self.vboxlayout.addWidget(self.pushButton_Zoom_Out)
        self.gridlayout2.addWidget(self.groupBox,0,10,2,1)

        self.pushButton_Play = QtGui.QPushButton(self.dockWidgetContents)
        self.pushButton_Play.setObjectName("pushButton_Play")
        self.gridlayout2.addWidget(self.pushButton_Play,1,0,1,2)

        self.pushButton_Pause = QtGui.QPushButton(self.dockWidgetContents)
        self.pushButton_Pause.setObjectName("pushButton_Pause")
        self.gridlayout2.addWidget(self.pushButton_Pause,1,2,1,3)

        self.pushButton_Mark_Point = QtGui.QPushButton(self.dockWidgetContents)
        self.pushButton_Mark_Point.setObjectName("pushButton_Mark_Point")
        self.gridlayout2.addWidget(self.pushButton_Mark_Point,1,5,1,3)

        self.pushButton_Stop = QtGui.QPushButton(self.dockWidgetContents)
        self.pushButton_Stop.setObjectName("pushButton_Stop")
        self.gridlayout2.addWidget(self.pushButton_Stop,1,8,1,1)

        self.pushButton_Set_Point = QtGui.QPushButton(self.dockWidgetContents)
        self.pushButton_Set_Point.setObjectName("pushButton_Set_Point")
        self.gridlayout2.addWidget(self.pushButton_Set_Point,1,9,1,1)
        self.gridlayout.addLayout(self.gridlayout2,1,0,1,1)
        AudioForm.setWidget(self.dockWidgetContents)
        self.label_4.setBuddy(self.lineEdit_Filename)
        self.label_5.setBuddy(self.lineEdit_Length)
        self.label_6.setBuddy(self.lineEdit_Current_Point)

        self.retranslateUi(AudioForm)
        QtCore.QMetaObject.connectSlotsByName(AudioForm)

    def retranslateUi(self, AudioForm):
        AudioForm.setWindowTitle(QtGui.QApplication.translate("AudioForm", "Audio Controls", None, QtGui.QApplication.UnicodeUTF8))
        self.label_start_time.setText(QtGui.QApplication.translate("AudioForm", "00:00:00", None, QtGui.QApplication.UnicodeUTF8))
        self.label_current_time.setText(QtGui.QApplication.translate("AudioForm", "00:00:00", None, QtGui.QApplication.UnicodeUTF8))
        self.label_end_time.setText(QtGui.QApplication.translate("AudioForm", "00:00:00", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("AudioForm", "Filename:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_5.setText(QtGui.QApplication.translate("AudioForm", "Length:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_6.setText(QtGui.QApplication.translate("AudioForm", "Current Point:", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_Open_File.setText(QtGui.QApplication.translate("AudioForm", "Open File", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("AudioForm", "Zoom", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_Zoom_In.setText(QtGui.QApplication.translate("AudioForm", "In", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_Zoom_Out.setText(QtGui.QApplication.translate("AudioForm", "Out", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_Play.setText(QtGui.QApplication.translate("AudioForm", "Play", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_Pause.setText(QtGui.QApplication.translate("AudioForm", "Pause", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_Mark_Point.setText(QtGui.QApplication.translate("AudioForm", "Mark Point", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_Stop.setText(QtGui.QApplication.translate("AudioForm", "Stop", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_Set_Point.setText(QtGui.QApplication.translate("AudioForm", "Set Point", None, QtGui.QApplication.UnicodeUTF8))

