from Point_Dialog_Ui import Ui_Dialog_New_Point
from PyQt4 import QtCore, QtGui, QtOpenGL, QtXml

class PointDialog(QtGui.QDialog):
	def __init__(self, parent=None):
		QtGui.QWidget.__init__(self,parent)
		self.ui=Ui_Dialog_New_Point()
		self.ui.setupUi(self)
		self.ui.lineEdit_X.setValidator(QtGui.QDoubleValidator(self.ui.lineEdit_X))
		self.ui.lineEdit_Y.setValidator(QtGui.QDoubleValidator(self.ui.lineEdit_Y))
		self.ui.lineEdit_Z.setValidator(QtGui.QDoubleValidator(self.ui.lineEdit_Z))

	def set_point(self,point):
		self.ui.lineEdit_X.setText(QtCore.QString(str(point.x)))
		self.ui.lineEdit_Y.setText(QtCore.QString(str(point.y)))
		self.ui.lineEdit_Z.setText(QtCore.QString(str(point.z)))

	#def close(self):
	#	self.close()