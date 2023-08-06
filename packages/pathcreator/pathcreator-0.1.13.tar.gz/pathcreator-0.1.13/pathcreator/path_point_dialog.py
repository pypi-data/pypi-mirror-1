from Path_Point_Dialog_Ui import Ui_Path_Point_Dialog
from PyQt4 import QtCore, QtGui, QtOpenGL, QtXml


class Path_Point_Dialog(QtGui.QDialog):
	def __init__(self,point,parent=None):
		self.ui=Ui_Path_Point_Dialog()
		self.ui.setupUi(self)
		QtGui.QWidget.__init__(self,parent)