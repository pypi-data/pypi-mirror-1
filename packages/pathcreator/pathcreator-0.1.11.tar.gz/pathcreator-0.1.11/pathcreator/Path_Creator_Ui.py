# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Path_Creator.ui'
#
# Created: Mon Oct 12 13:58:09 2009
#      by: PyQt4 UI code generator 4.3.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_MainWindow_Path_Creator(object):
    def setupUi(self, MainWindow_Path_Creator):
        MainWindow_Path_Creator.setObjectName("MainWindow_Path_Creator")
        MainWindow_Path_Creator.resize(QtCore.QSize(QtCore.QRect(0,0,929,544).size()).expandedTo(MainWindow_Path_Creator.minimumSizeHint()))

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(MainWindow_Path_Creator.sizePolicy().hasHeightForWidth())
        MainWindow_Path_Creator.setSizePolicy(sizePolicy)

        self.centralwidget = QtGui.QWidget(MainWindow_Path_Creator)
        self.centralwidget.setGeometry(QtCore.QRect(0,26,929,495))

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(5)
        sizePolicy.setVerticalStretch(5)
        sizePolicy.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy)
        self.centralwidget.setMinimumSize(QtCore.QSize(400,350))
        self.centralwidget.setObjectName("centralwidget")

        self.hboxlayout = QtGui.QHBoxLayout(self.centralwidget)
        self.hboxlayout.setObjectName("hboxlayout")

        self.gridlayout = QtGui.QGridLayout()
        self.gridlayout.setSizeConstraint(QtGui.QLayout.SetNoConstraint)
        self.gridlayout.setMargin(3)
        self.gridlayout.setObjectName("gridlayout")

        self.frame = QtGui.QFrame(self.centralwidget)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(2)
        sizePolicy.setVerticalStretch(2)
        sizePolicy.setHeightForWidth(self.frame.sizePolicy().hasHeightForWidth())
        self.frame.setSizePolicy(sizePolicy)
        self.frame.setMinimumSize(QtCore.QSize(0,0))
        self.frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtGui.QFrame.Raised)
        self.frame.setObjectName("frame")

        self.gridlayout1 = QtGui.QGridLayout(self.frame)
        self.gridlayout1.setObjectName("gridlayout1")

        self.graphicsView = QtGui.QGraphicsView(self.frame)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(5)
        sizePolicy.setVerticalStretch(5)
        sizePolicy.setHeightForWidth(self.graphicsView.sizePolicy().hasHeightForWidth())
        self.graphicsView.setSizePolicy(sizePolicy)
        self.graphicsView.setMinimumSize(QtCore.QSize(200,200))
        self.graphicsView.setObjectName("graphicsView")
        self.gridlayout1.addWidget(self.graphicsView,0,0,1,1)

        self.groupBox = QtGui.QGroupBox(self.frame)
        self.groupBox.setEnabled(True)
        self.groupBox.setMinimumSize(QtCore.QSize(0,50))
        self.groupBox.setObjectName("groupBox")

        self.hboxlayout1 = QtGui.QHBoxLayout(self.groupBox)
        self.hboxlayout1.setObjectName("hboxlayout1")

        self.label = QtGui.QLabel(self.groupBox)
        self.label.setObjectName("label")
        self.hboxlayout1.addWidget(self.label)

        self.lineEdit_width = QtGui.QLineEdit(self.groupBox)
        self.lineEdit_width.setObjectName("lineEdit_width")
        self.hboxlayout1.addWidget(self.lineEdit_width)

        self.label_2 = QtGui.QLabel(self.groupBox)
        self.label_2.setObjectName("label_2")
        self.hboxlayout1.addWidget(self.label_2)

        self.lineEdit_height = QtGui.QLineEdit(self.groupBox)
        self.lineEdit_height.setObjectName("lineEdit_height")
        self.hboxlayout1.addWidget(self.lineEdit_height)

        self.label_3 = QtGui.QLabel(self.groupBox)
        self.label_3.setObjectName("label_3")
        self.hboxlayout1.addWidget(self.label_3)

        self.lineEdit_depth = QtGui.QLineEdit(self.groupBox)
        self.lineEdit_depth.setObjectName("lineEdit_depth")
        self.hboxlayout1.addWidget(self.lineEdit_depth)

        self.pushButton_Resize = QtGui.QPushButton(self.groupBox)
        self.pushButton_Resize.setObjectName("pushButton_Resize")
        self.hboxlayout1.addWidget(self.pushButton_Resize)
        self.gridlayout1.addWidget(self.groupBox,1,0,1,1)
        self.gridlayout.addWidget(self.frame,0,1,1,1)

        self.tabWidget = QtGui.QTabWidget(self.centralwidget)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred,QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(2)
        sizePolicy.setHeightForWidth(self.tabWidget.sizePolicy().hasHeightForWidth())
        self.tabWidget.setSizePolicy(sizePolicy)
        self.tabWidget.setMinimumSize(QtCore.QSize(200,300))
        self.tabWidget.setObjectName("tabWidget")

        self.tabPath = QtGui.QWidget()
        self.tabPath.setGeometry(QtCore.QRect(0,0,296,443))

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(2)
        sizePolicy.setHeightForWidth(self.tabPath.sizePolicy().hasHeightForWidth())
        self.tabPath.setSizePolicy(sizePolicy)
        self.tabPath.setObjectName("tabPath")

        self.vboxlayout = QtGui.QVBoxLayout(self.tabPath)
        self.vboxlayout.setSizeConstraint(QtGui.QLayout.SetMinimumSize)
        self.vboxlayout.setObjectName("vboxlayout")

        self.groupBox_PointControls = QtGui.QGroupBox(self.tabPath)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox_PointControls.sizePolicy().hasHeightForWidth())
        self.groupBox_PointControls.setSizePolicy(sizePolicy)
        self.groupBox_PointControls.setObjectName("groupBox_PointControls")

        self.gridlayout2 = QtGui.QGridLayout(self.groupBox_PointControls)
        self.gridlayout2.setObjectName("gridlayout2")

        self.pushButton_NewPoint = QtGui.QPushButton(self.groupBox_PointControls)
        self.pushButton_NewPoint.setObjectName("pushButton_NewPoint")
        self.gridlayout2.addWidget(self.pushButton_NewPoint,0,0,1,2)

        self.pushButton_EditPoint = QtGui.QPushButton(self.groupBox_PointControls)
        self.pushButton_EditPoint.setObjectName("pushButton_EditPoint")
        self.gridlayout2.addWidget(self.pushButton_EditPoint,1,0,1,1)

        self.pushButton_DeletePoint = QtGui.QPushButton(self.groupBox_PointControls)
        self.pushButton_DeletePoint.setObjectName("pushButton_DeletePoint")
        self.gridlayout2.addWidget(self.pushButton_DeletePoint,2,0,1,1)

        self.pushButton_InsertBelowPoint = QtGui.QPushButton(self.groupBox_PointControls)
        self.pushButton_InsertBelowPoint.setObjectName("pushButton_InsertBelowPoint")
        self.gridlayout2.addWidget(self.pushButton_InsertBelowPoint,2,1,1,1)

        self.pushButton_InsertAbovePoint = QtGui.QPushButton(self.groupBox_PointControls)
        self.pushButton_InsertAbovePoint.setObjectName("pushButton_InsertAbovePoint")
        self.gridlayout2.addWidget(self.pushButton_InsertAbovePoint,1,1,1,1)

        self.pushButton_SavePath = QtGui.QPushButton(self.groupBox_PointControls)
        self.pushButton_SavePath.setObjectName("pushButton_SavePath")
        self.gridlayout2.addWidget(self.pushButton_SavePath,3,0,1,1)

        self.pushButton_LoadPath = QtGui.QPushButton(self.groupBox_PointControls)
        self.pushButton_LoadPath.setObjectName("pushButton_LoadPath")
        self.gridlayout2.addWidget(self.pushButton_LoadPath,3,1,1,1)
        self.vboxlayout.addWidget(self.groupBox_PointControls)

        self.groupBox_PointsList = QtGui.QGroupBox(self.tabPath)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(2)
        sizePolicy.setHeightForWidth(self.groupBox_PointsList.sizePolicy().hasHeightForWidth())
        self.groupBox_PointsList.setSizePolicy(sizePolicy)
        self.groupBox_PointsList.setObjectName("groupBox_PointsList")

        self.vboxlayout1 = QtGui.QVBoxLayout(self.groupBox_PointsList)
        self.vboxlayout1.setObjectName("vboxlayout1")

        self.listWidget_Path = QtGui.QListWidget(self.groupBox_PointsList)
        self.listWidget_Path.setObjectName("listWidget_Path")
        self.vboxlayout1.addWidget(self.listWidget_Path)
        self.vboxlayout.addWidget(self.groupBox_PointsList)
        self.tabWidget.addTab(self.tabPath,"")

        self.tabListeners = QtGui.QWidget()
        self.tabListeners.setGeometry(QtCore.QRect(0,0,296,443))
        self.tabListeners.setObjectName("tabListeners")

        self.vboxlayout2 = QtGui.QVBoxLayout(self.tabListeners)
        self.vboxlayout2.setObjectName("vboxlayout2")

        self.groupBox_ListenerControls = QtGui.QGroupBox(self.tabListeners)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox_ListenerControls.sizePolicy().hasHeightForWidth())
        self.groupBox_ListenerControls.setSizePolicy(sizePolicy)
        self.groupBox_ListenerControls.setObjectName("groupBox_ListenerControls")

        self.gridlayout3 = QtGui.QGridLayout(self.groupBox_ListenerControls)
        self.gridlayout3.setObjectName("gridlayout3")

        self.pushButton_NewListener = QtGui.QPushButton(self.groupBox_ListenerControls)
        self.pushButton_NewListener.setObjectName("pushButton_NewListener")
        self.gridlayout3.addWidget(self.pushButton_NewListener,0,0,1,2)

        self.pushButton_EditListener = QtGui.QPushButton(self.groupBox_ListenerControls)
        self.pushButton_EditListener.setObjectName("pushButton_EditListener")
        self.gridlayout3.addWidget(self.pushButton_EditListener,1,0,1,1)

        self.pushButton_DeleteListener = QtGui.QPushButton(self.groupBox_ListenerControls)
        self.pushButton_DeleteListener.setObjectName("pushButton_DeleteListener")
        self.gridlayout3.addWidget(self.pushButton_DeleteListener,2,0,1,1)

        self.pushButton_InsertBelowListener = QtGui.QPushButton(self.groupBox_ListenerControls)
        self.pushButton_InsertBelowListener.setObjectName("pushButton_InsertBelowListener")
        self.gridlayout3.addWidget(self.pushButton_InsertBelowListener,2,1,1,1)

        self.pushButton_InsertAboveListener = QtGui.QPushButton(self.groupBox_ListenerControls)
        self.pushButton_InsertAboveListener.setObjectName("pushButton_InsertAboveListener")
        self.gridlayout3.addWidget(self.pushButton_InsertAboveListener,1,1,1,1)

        self.pushButton_SaveListener = QtGui.QPushButton(self.groupBox_ListenerControls)
        self.pushButton_SaveListener.setObjectName("pushButton_SaveListener")
        self.gridlayout3.addWidget(self.pushButton_SaveListener,3,0,1,1)

        self.pushButton_LoadListener = QtGui.QPushButton(self.groupBox_ListenerControls)
        self.pushButton_LoadListener.setObjectName("pushButton_LoadListener")
        self.gridlayout3.addWidget(self.pushButton_LoadListener,3,1,1,1)
        self.vboxlayout2.addWidget(self.groupBox_ListenerControls)

        self.groupBox_ListenerList = QtGui.QGroupBox(self.tabListeners)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(2)
        sizePolicy.setVerticalStretch(2)
        sizePolicy.setHeightForWidth(self.groupBox_ListenerList.sizePolicy().hasHeightForWidth())
        self.groupBox_ListenerList.setSizePolicy(sizePolicy)
        self.groupBox_ListenerList.setObjectName("groupBox_ListenerList")

        self.vboxlayout3 = QtGui.QVBoxLayout(self.groupBox_ListenerList)
        self.vboxlayout3.setObjectName("vboxlayout3")

        self.listWidget_Listeners = QtGui.QListWidget(self.groupBox_ListenerList)
        self.listWidget_Listeners.setObjectName("listWidget_Listeners")
        self.vboxlayout3.addWidget(self.listWidget_Listeners)
        self.vboxlayout2.addWidget(self.groupBox_ListenerList)
        self.tabWidget.addTab(self.tabListeners,"")

        self.tabSpeakers = QtGui.QWidget()
        self.tabSpeakers.setGeometry(QtCore.QRect(0,0,296,443))
        self.tabSpeakers.setObjectName("tabSpeakers")

        self.vboxlayout4 = QtGui.QVBoxLayout(self.tabSpeakers)
        self.vboxlayout4.setObjectName("vboxlayout4")

        self.groupBox_SpeakerControls = QtGui.QGroupBox(self.tabSpeakers)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox_SpeakerControls.sizePolicy().hasHeightForWidth())
        self.groupBox_SpeakerControls.setSizePolicy(sizePolicy)
        self.groupBox_SpeakerControls.setObjectName("groupBox_SpeakerControls")

        self.gridlayout4 = QtGui.QGridLayout(self.groupBox_SpeakerControls)
        self.gridlayout4.setObjectName("gridlayout4")

        self.pushButton_NewSpeaker = QtGui.QPushButton(self.groupBox_SpeakerControls)
        self.pushButton_NewSpeaker.setObjectName("pushButton_NewSpeaker")
        self.gridlayout4.addWidget(self.pushButton_NewSpeaker,0,0,1,2)

        self.pushButton_EditSpeaker = QtGui.QPushButton(self.groupBox_SpeakerControls)
        self.pushButton_EditSpeaker.setObjectName("pushButton_EditSpeaker")
        self.gridlayout4.addWidget(self.pushButton_EditSpeaker,1,0,1,1)

        self.pushButton_DeleteSpeaker = QtGui.QPushButton(self.groupBox_SpeakerControls)
        self.pushButton_DeleteSpeaker.setObjectName("pushButton_DeleteSpeaker")
        self.gridlayout4.addWidget(self.pushButton_DeleteSpeaker,2,0,1,1)

        self.pushButton_InsertBelowSpeaker = QtGui.QPushButton(self.groupBox_SpeakerControls)
        self.pushButton_InsertBelowSpeaker.setObjectName("pushButton_InsertBelowSpeaker")
        self.gridlayout4.addWidget(self.pushButton_InsertBelowSpeaker,2,1,1,1)

        self.pushButton_InsertAboveSpeaker = QtGui.QPushButton(self.groupBox_SpeakerControls)
        self.pushButton_InsertAboveSpeaker.setObjectName("pushButton_InsertAboveSpeaker")
        self.gridlayout4.addWidget(self.pushButton_InsertAboveSpeaker,1,1,1,1)

        self.pushButton_SaveSpeaker = QtGui.QPushButton(self.groupBox_SpeakerControls)
        self.pushButton_SaveSpeaker.setObjectName("pushButton_SaveSpeaker")
        self.gridlayout4.addWidget(self.pushButton_SaveSpeaker,3,0,1,1)

        self.pushButton_LoadSpeaker = QtGui.QPushButton(self.groupBox_SpeakerControls)
        self.pushButton_LoadSpeaker.setObjectName("pushButton_LoadSpeaker")
        self.gridlayout4.addWidget(self.pushButton_LoadSpeaker,3,1,1,1)
        self.vboxlayout4.addWidget(self.groupBox_SpeakerControls)

        self.groupBox_SpeakerList = QtGui.QGroupBox(self.tabSpeakers)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(2)
        sizePolicy.setVerticalStretch(2)
        sizePolicy.setHeightForWidth(self.groupBox_SpeakerList.sizePolicy().hasHeightForWidth())
        self.groupBox_SpeakerList.setSizePolicy(sizePolicy)
        self.groupBox_SpeakerList.setObjectName("groupBox_SpeakerList")

        self.vboxlayout5 = QtGui.QVBoxLayout(self.groupBox_SpeakerList)
        self.vboxlayout5.setObjectName("vboxlayout5")

        self.listWidget_Speakers = QtGui.QListWidget(self.groupBox_SpeakerList)
        self.listWidget_Speakers.setObjectName("listWidget_Speakers")
        self.vboxlayout5.addWidget(self.listWidget_Speakers)
        self.vboxlayout4.addWidget(self.groupBox_SpeakerList)
        self.tabWidget.addTab(self.tabSpeakers,"")
        self.gridlayout.addWidget(self.tabWidget,0,0,1,1)
        self.hboxlayout.addLayout(self.gridlayout)
        MainWindow_Path_Creator.setCentralWidget(self.centralwidget)

        self.menubar = QtGui.QMenuBar(MainWindow_Path_Creator)
        self.menubar.setGeometry(QtCore.QRect(0,0,929,26))
        self.menubar.setObjectName("menubar")

        self.menu_File = QtGui.QMenu(self.menubar)
        self.menu_File.setObjectName("menu_File")

        self.menu_Enviroment = QtGui.QMenu(self.menubar)
        self.menu_Enviroment.setObjectName("menu_Enviroment")
        MainWindow_Path_Creator.setMenuBar(self.menubar)

        self.statusbar = QtGui.QStatusBar(MainWindow_Path_Creator)
        self.statusbar.setGeometry(QtCore.QRect(0,521,929,23))
        self.statusbar.setObjectName("statusbar")
        MainWindow_Path_Creator.setStatusBar(self.statusbar)

        self.action_New = QtGui.QAction(MainWindow_Path_Creator)
        self.action_New.setObjectName("action_New")

        self.action_Open = QtGui.QAction(MainWindow_Path_Creator)
        self.action_Open.setObjectName("action_Open")

        self.action_Save = QtGui.QAction(MainWindow_Path_Creator)
        self.action_Save.setObjectName("action_Save")

        self.action_Close = QtGui.QAction(MainWindow_Path_Creator)
        self.action_Close.setObjectName("action_Close")

        self.actionEdit_Environment = QtGui.QAction(MainWindow_Path_Creator)
        self.actionEdit_Environment.setObjectName("actionEdit_Environment")

        self.actionGenerate_Environment_File = QtGui.QAction(MainWindow_Path_Creator)
        self.actionGenerate_Environment_File.setObjectName("actionGenerate_Environment_File")
        self.menu_File.addAction(self.action_New)
        self.menu_File.addAction(self.action_Open)
        self.menu_File.addAction(self.action_Save)
        self.menu_File.addAction(self.action_Close)
        self.menu_Enviroment.addAction(self.actionEdit_Environment)
        self.menu_Enviroment.addAction(self.actionGenerate_Environment_File)
        self.menubar.addAction(self.menu_File.menuAction())
        self.menubar.addAction(self.menu_Enviroment.menuAction())

        self.retranslateUi(MainWindow_Path_Creator)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow_Path_Creator)

    def retranslateUi(self, MainWindow_Path_Creator):
        MainWindow_Path_Creator.setWindowTitle(QtGui.QApplication.translate("MainWindow_Path_Creator", "Path Creator", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("MainWindow_Path_Creator", "Room Dimensions", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("MainWindow_Path_Creator", "Width:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("MainWindow_Path_Creator", "Height:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("MainWindow_Path_Creator", "Depth:", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_Resize.setText(QtGui.QApplication.translate("MainWindow_Path_Creator", "Resize", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_PointControls.setTitle(QtGui.QApplication.translate("MainWindow_Path_Creator", "Point Controls", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_NewPoint.setText(QtGui.QApplication.translate("MainWindow_Path_Creator", "New", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_EditPoint.setText(QtGui.QApplication.translate("MainWindow_Path_Creator", "Edit", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_DeletePoint.setText(QtGui.QApplication.translate("MainWindow_Path_Creator", "Delete", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_InsertBelowPoint.setText(QtGui.QApplication.translate("MainWindow_Path_Creator", "Insert Below", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_InsertAbovePoint.setText(QtGui.QApplication.translate("MainWindow_Path_Creator", "Insert Above", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_SavePath.setText(QtGui.QApplication.translate("MainWindow_Path_Creator", "Save", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_LoadPath.setText(QtGui.QApplication.translate("MainWindow_Path_Creator", "Load", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_PointsList.setTitle(QtGui.QApplication.translate("MainWindow_Path_Creator", "Points", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabPath), QtGui.QApplication.translate("MainWindow_Path_Creator", "Path", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_ListenerControls.setTitle(QtGui.QApplication.translate("MainWindow_Path_Creator", "Listener Controls", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_NewListener.setText(QtGui.QApplication.translate("MainWindow_Path_Creator", "New", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_EditListener.setText(QtGui.QApplication.translate("MainWindow_Path_Creator", "Edit", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_DeleteListener.setText(QtGui.QApplication.translate("MainWindow_Path_Creator", "Delete", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_InsertBelowListener.setText(QtGui.QApplication.translate("MainWindow_Path_Creator", "Insert Below", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_InsertAboveListener.setText(QtGui.QApplication.translate("MainWindow_Path_Creator", "Insert Above", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_SaveListener.setText(QtGui.QApplication.translate("MainWindow_Path_Creator", "Save", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_LoadListener.setText(QtGui.QApplication.translate("MainWindow_Path_Creator", "Load", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_ListenerList.setTitle(QtGui.QApplication.translate("MainWindow_Path_Creator", "Listeners", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabListeners), QtGui.QApplication.translate("MainWindow_Path_Creator", "Listeners", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_SpeakerControls.setTitle(QtGui.QApplication.translate("MainWindow_Path_Creator", "Speaker Controls", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_NewSpeaker.setText(QtGui.QApplication.translate("MainWindow_Path_Creator", "New", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_EditSpeaker.setText(QtGui.QApplication.translate("MainWindow_Path_Creator", "Edit", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_DeleteSpeaker.setText(QtGui.QApplication.translate("MainWindow_Path_Creator", "Delete", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_InsertBelowSpeaker.setText(QtGui.QApplication.translate("MainWindow_Path_Creator", "Insert Below", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_InsertAboveSpeaker.setText(QtGui.QApplication.translate("MainWindow_Path_Creator", "Insert Above", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_SaveSpeaker.setText(QtGui.QApplication.translate("MainWindow_Path_Creator", "Save", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_LoadSpeaker.setText(QtGui.QApplication.translate("MainWindow_Path_Creator", "Load", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_SpeakerList.setTitle(QtGui.QApplication.translate("MainWindow_Path_Creator", "Speakers", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabSpeakers), QtGui.QApplication.translate("MainWindow_Path_Creator", "Speakers", None, QtGui.QApplication.UnicodeUTF8))
        self.menu_File.setTitle(QtGui.QApplication.translate("MainWindow_Path_Creator", "&File", None, QtGui.QApplication.UnicodeUTF8))
        self.menu_Enviroment.setTitle(QtGui.QApplication.translate("MainWindow_Path_Creator", "&Enviroment", None, QtGui.QApplication.UnicodeUTF8))
        self.action_New.setText(QtGui.QApplication.translate("MainWindow_Path_Creator", "&New", None, QtGui.QApplication.UnicodeUTF8))
        self.action_Open.setText(QtGui.QApplication.translate("MainWindow_Path_Creator", "&Open", None, QtGui.QApplication.UnicodeUTF8))
        self.action_Save.setText(QtGui.QApplication.translate("MainWindow_Path_Creator", "&Save", None, QtGui.QApplication.UnicodeUTF8))
        self.action_Close.setText(QtGui.QApplication.translate("MainWindow_Path_Creator", "&Close", None, QtGui.QApplication.UnicodeUTF8))
        self.actionEdit_Environment.setText(QtGui.QApplication.translate("MainWindow_Path_Creator", "Edit Environment", None, QtGui.QApplication.UnicodeUTF8))
        self.actionGenerate_Environment_File.setText(QtGui.QApplication.translate("MainWindow_Path_Creator", "Generate Environment File", None, QtGui.QApplication.UnicodeUTF8))

