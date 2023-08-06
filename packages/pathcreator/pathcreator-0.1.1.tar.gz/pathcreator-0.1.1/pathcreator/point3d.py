from PyQt4 import QtCore, QtGui, QtOpenGL, QtXml


class Point3D(QtGui.QListWidgetItem):
	"""Class representing traditional 3d point as three floating point numbers"""
	def __init__(self,xpos=0.0,ypos=0.0,zpos=0.0):
		QtGui.QStandardItem.__init__(self,QtCore.QString("X: "+str(xpos)+" Y: "+str(ypos)+" Z: "+str(zpos)))
		self.x=xpos
		self.y=ypos
		self.z=zpos
		#self.marker=None

	def __str__(self):
		return "X: "+str(self.x)+" Y: "+str(self.y)+" Z: "+str(self.z)
	def __repr__(self):
		return str(self)

	def set_marker(self, marker):
		"""function links point in path to marker"""
		self.marker=marker

	def update_coords(self, c1, c2, c3):
		try:
			self.x=float(c1)
			self.y=float(c2)
			self.z=float(c3)
		except ValueError:
			QtGui.QMessageBox.critical(None, "Point Error",
            "Error updating point, point value not a real number.")