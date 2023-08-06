from Marker_Dialog import Ui_Add_Marker_Dialog
from PyQt4 import QtCore, QtGui, QtOpenGL, QtXml


class MarkerDialog(QtGui.QDialog):
	def __init__(self,point,parent=None):
		QtGui.QWidget.__init__(self,parent)
		self.ui=Ui_Add_Marker_Dialog()
		self.ui.setupUi(self)
		self.point=point
		self.marker_selected=False
		self.markers=None
		self.marker_list=None
		self.connect(self.ui.listWidget_Markers, QtCore.SIGNAL('currentRowChanged(int)'), self.update_selected_marker)
		self.connect(self.ui.pushButton_Set_Marker,QtCore.SIGNAL('clicked()'),self.set_marker)
		self.connect(self.ui.pushButton_New_Marker,QtCore.SIGNAL('clicked()'),self.new_marker)

	def load_markers(self, marker_list=None):
		self.ui.listWidget_Markers.clear()
		if(marker_list is not None):
			self.marker_list=marker_list
			self.markers={}
			for marker in self.marker_list:
				self.ui.listWidget_Markers.addItem(str(marker))
				self.markers[str(marker)]=marker
				#self.set_selected_marker(self.dict[point])
		else:
			self.ui.pushButton_Set_Marker.setEnabled(False)
	
	def update_selected_marker(self, selected=-1):
		if(selected>-1):
			self.marker_selected=True
			self.selected_marker=selected
			m_name=self.ui.listWidget_Markers.item(selected)
			self.emit(QtCore.SIGNAL("marker_selected"),self.markers[str(m_name.text())])
		else:
			QtGui.QMessageBox.warning(self, 'Error', QtCore.QString('Invalid Selection'))
	
	def set_selected_marker(self, marker=None):
		i = self.marker_list.index(marker)
		if(i>-1):
			self.update_selected_marker(i)
	
	def set_marker(self):
		if(not self.marker_selected):
			QtGui.QMessageBox.warning(self, 'Error', QtCore.QString('No marker selected.'))
		else:
			m_name=self.ui.listWidget_Markers.currentItem()
			#print m_name , str(m_name) , m_name.text()
			marker=self.markers[str(m_name.text())]
			self.emit(QtCore.SIGNAL("marker_set"),marker,self.point)
			self.close()
	
	def new_marker(self):
		pass