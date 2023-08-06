from PyQt4 import QtCore, QtGui, QtOpenGL, QtXml
from Environment_Form_Ui import Ui_EnvironmentFrom

class EnvironmentDockWidget(QtGui.QDockWidget):
	"""Used to display environment settings"""
	def __init__(self, parent=None,sos="345",fbins=["512","1024","2048"],chunk="500"):
		"""initialize gui fields and set validators"""
		QtGui.QDockWidget.__init__(self,parent)
		self.ui=Ui_EnvironmentFrom()
		self.ui.setupUi(self)
		try:
				self.ui.lineEdit_SpeedOfSound.setText(str(sos))
				#ensure we're dealing with string values
				for bin in fbins:
					bin=str(bin)
					#ensure they can be converted back to int
					int(bin)
				self.ui.comboBox_NFBins.insertItems(0,fbins)
				self.ui.lineEdit_ChunkSize.setText(str(chunk))
		except ValueError:
			QtGui.QMessageBox.critical(None, "Environment Widget",
            "Error validating initial values.")
		self.ui.lineEdit_SpeedOfSound.setValidator(QtGui.QIntValidator(300, 400,self.ui.lineEdit_SpeedOfSound))
		self.ui.lineEdit_ChunkSize.setValidator(QtGui.QIntValidator(1, 44100,self.ui.lineEdit_SpeedOfSound))