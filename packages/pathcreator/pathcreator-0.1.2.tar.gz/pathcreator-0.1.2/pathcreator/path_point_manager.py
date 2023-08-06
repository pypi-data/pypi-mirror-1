from PyQt4 import QtCore, QtGui

class Path_Point_Manager(QtGui.QWidget):
	"""manages dict of points to markers"""
	def __init__(self,parent=None):
		QtGui.QWidget.__init__(self,parent)
		self.dict={}
		self.markers_list=None
	
	def markers_updated(self,markers=None):
		"""updates list of markers"""
		self.markers_list=markers
		self.emit(QtCore.SIGNAL("markers_updated"),self.markers_list)
		
	def marker_deleted(self,marker):
		"""make sure marker is deleted from dict when it is deleted"""
		self.detach_marker_from_point(marker)
	
	def attach_marker_to_point(self,marker,point):
		"""attach marker to a point in dict"""
		#check to see if this marker is already attached to a point
		if(marker in self.dict.values()):
			cur_point=[k for k, v in self.dict.iteritems() if v == marker][0]
			if(cur_point==point):
				pass
			else:
				reply = QtGui.QMessageBox.Yes
				reply=QtGui.QMessageBox.question(self,"Marker In Use","Marker is currently attached to another point. Would you like to disconnect the marker from the current point and re-attach it to this point?", QtGui.QMessageBox.Yes|QtGui.QMessageBox.Default,QtGui.QMessageBox.No)
				if(reply == QtGui.QMessageBox.Yes):
					self.detach_marker_from_point(marker,cur_point)
					self.dict[point]=marker
					print self.dict
				else:
					pass
		else:
			self.dict[point]=marker
			print self.dict

	def detach_marker_from_point(self,marker,point=None):
		"""remove marker from dict"""
		if(point is not None):
			del self.dict[point]
		else:
			if(marker in self.dict.values()):
				point=[k for k, v in self.dict.iteritems() if v == marker][0]
				del self.dict[point]
	
	def point_from_marker(self,marker):
		"""returns a point given a marker, if marker is not found returns None"""
		point= None
		if(marker in self.dict.values()):
				point=[k for k, v in self.dict.iteritems() if v == marker][0]
		return point

