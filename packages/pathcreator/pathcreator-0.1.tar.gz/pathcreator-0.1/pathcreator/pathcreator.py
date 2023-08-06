import sys,math
from copy import copy
from PyQt4 import QtCore, QtGui, QtOpenGL, QtXml
from Path_Creator import Ui_MainWindow_Path_Creator
from point_dialog import PointDialog
from Environment_Form import Ui_EnvironmentFrom
from Audio_Dock import Audio_DockWidget
from marker_dialog import MarkerDialog
from path_point_manager import Path_Point_Manager
from point3d import Point3D
#from Error_Dialog import Ui_Dialog_Error
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT  import *
try:
    from OpenGL import GL
except ImportError:
    app = QtGui.QApplication(sys.argv)
    QtGui.QMessageBox.critical(None, "Path Creator",
            "PyOpenGL must be installed to run thisapplication.")
    sys.exit(1)



		
class EnvironmentDockWidget(QtGui.QDockWidget):
	"""Used to display environment settings"""
	def __init__(self, parent=None,sos="345",fbins=["512","1024","2048"],chunk="500"):
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


class PathCreator(QtGui.QMainWindow):
	"""Top level class for Path creation GUI. Used to author and edit audio rendering environments."""
	def __init__(self, parent=None):
		QtGui.QWidget.__init__(self, parent)
		self.ui = Ui_MainWindow_Path_Creator()
		self.ui.setupUi(self)
		self.ui.graphicsView=GLWidget(self)
		sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Expanding)
		sizePolicy.setHorizontalStretch(5)
		sizePolicy.setVerticalStretch(5)
		sizePolicy.setHeightForWidth(self.ui.graphicsView.sizePolicy().hasHeightForWidth())
		self.ui.graphicsView.setSizePolicy(sizePolicy)
		self.ui.graphicsView.setMinimumSize(QtCore.QSize(200,200))
		self.ui.graphicsView.setObjectName("graphicsView")
		self.ui.gridlayout1.addWidget(self.ui.graphicsView,0,0,1,1)
		self.ui.gridlayout.addWidget(self.ui.frame,0,1,1,1)
		self.audio_dockWidget=Audio_DockWidget()
		self.addDockWidget(QtCore.Qt.BottomDockWidgetArea,self.audio_dockWidget)
		#self.point_to_markers_dict={}
		self.point_manager=Path_Point_Manager()
		
		#connect signals and slots
		self.connect(self.ui.action_Close, QtCore.SIGNAL('triggered()'), QtCore.SLOT('close()'))
		self.connect(self.ui.action_Save, QtCore.SIGNAL('triggered()'),self.Save_Session)
		self.connect(self.ui.action_Open, QtCore.SIGNAL('triggered()'),self.Load_Session)
		#Environmnet Connections
		self.connect(self.ui.actionEdit_Environment, QtCore.SIGNAL('triggered()'),self.Edit_Environment)
		#Room Connections
		self.connect(self.ui.pushButton_Resize,QtCore.SIGNAL('clicked()'),self.Resize_Room)
		#Path Tab Connections
		self.connect(self.ui.pushButton_NewPoint, QtCore.SIGNAL('clicked()'), self.New_Path_Point_Dialog)
		self.connect(self.ui.listWidget_Path, QtCore.SIGNAL('currentRowChanged(int)'), self.Update_Selected_Point)
		self.connect(self.ui.pushButton_DeletePoint, QtCore.SIGNAL('clicked()'), self.Delete_Path_Point)
		self.connect(self.ui.pushButton_EditPoint, QtCore.SIGNAL('clicked()'), self.Edit_Path_Point_Dialog)
		self.connect(self.ui.pushButton_InsertAbovePoint, QtCore.SIGNAL('clicked()'), self.Insert_Above_Path_Point_Dialog)
		self.connect(self.ui.pushButton_InsertBelowPoint, QtCore.SIGNAL('clicked()'), self.Insert_Below_Path_Point_Dialog)
		self.connect(self.ui.pushButton_SavePath, QtCore.SIGNAL('clicked()'), self.Save_Path)
		self.connect(self.ui.pushButton_LoadPath, QtCore.SIGNAL('clicked()'), self.Load_Path)
		#Listeners Tab Connections
		self.connect(self.ui.pushButton_NewListener, QtCore.SIGNAL('clicked()'), self.New_Listeners_Point_Dialog)
		self.connect(self.ui.pushButton_DeleteListener, QtCore.SIGNAL('clicked()'), self.Delete_Listeners_Point)
		self.connect(self.ui.pushButton_EditListener, QtCore.SIGNAL('clicked()'), self.Edit_Listeners_Point_Dialog)
		self.connect(self.ui.pushButton_InsertAboveListener, QtCore.SIGNAL('clicked()'), self.Insert_Above_Listeners_Point_Dialog)
		self.connect(self.ui.pushButton_InsertBelowListener, QtCore.SIGNAL('clicked()'), self.Insert_Below_Listeners_Point_Dialog)
		self.connect(self.ui.pushButton_SaveListener, QtCore.SIGNAL('clicked()'), self.Save_Listeners)
		self.connect(self.ui.pushButton_LoadListener, QtCore.SIGNAL('clicked()'), self.Load_Listeners)
		#Speaker Tab Connections
		self.connect(self.ui.pushButton_NewSpeaker, QtCore.SIGNAL('clicked()'), self.New_Speaker_Point_Dialog)
		self.connect(self.ui.listWidget_Speakers, QtCore.SIGNAL('currentRowChanged(int)'), self.Update_Selected_Speaker)
		self.connect(self.ui.pushButton_DeleteSpeaker, QtCore.SIGNAL('clicked()'), self.Delete_Speaker_Point)
		self.connect(self.ui.pushButton_EditSpeaker, QtCore.SIGNAL('clicked()'), self.Edit_Speaker_Point_Dialog)
		self.connect(self.ui.pushButton_InsertAboveSpeaker, QtCore.SIGNAL('clicked()'), self.Insert_Above_Speaker_Point_Dialog)
		self.connect(self.ui.pushButton_InsertBelowSpeaker, QtCore.SIGNAL('clicked()'), self.Insert_Below_Speaker_Point_Dialog)
		self.connect(self.ui.pushButton_SaveSpeaker, QtCore.SIGNAL('clicked()'), self.Save_Speaker)
		self.connect(self.ui.pushButton_LoadSpeaker, QtCore.SIGNAL('clicked()'), self.Load_Speaker)
		#Audio DockWidget Conections
		#self.connect(self.audio_dockWidget.wave.markers_list,QtCore.SIGNAL("markers_updated"),self.markers_updated)
		#self.connect(self.audio_dockWidget.wave.markers_list,QtCore.SIGNAL("marker_deleted"),self.marker_deleted)
		self.connect(self.audio_dockWidget.wave.markers_list,QtCore.SIGNAL("markers_updated"),self.point_manager.markers_updated)
		self.connect(self.audio_dockWidget.wave.markers_list,QtCore.SIGNAL("marker_deleted"),self.point_manager.marker_deleted)	
		self.connect(self.audio_dockWidget.wave.markers_list,QtCore.SIGNAL("marker_selected"),self.marker_selected)
		self.connect(self.audio_dockWidget,QtCore.SIGNAL("time_updated"),self.ui.graphicsView.updateTacer)
		self.connect(self.audio_dockWidget,QtCore.SIGNAL("play_started"),self.ready_path_tracer)

		self.speaker_fname=None
		self.path_fname=None
		self.listeners_fname=None
		self.session_fname=None
		self.environment_fname=None
		self.environment_dockWidget=None
		self.room_width=6.0
		self.room_height=2.5
		self.room_depth=8.0
		#set default room values and validators
		self.Update_Room_Coords(self.room_width,self.room_height,self.room_depth)
		self.ui.lineEdit_width.setValidator(QtGui.QDoubleValidator(self.ui.lineEdit_width))
		self.ui.lineEdit_depth.setValidator(QtGui.QDoubleValidator(self.ui.lineEdit_depth))
		self.ui.lineEdit_height.setValidator(QtGui.QDoubleValidator(self.ui.lineEdit_height))
		#keep track of unsaved changes in data
		self.speakers_dirty=False
		self.listeners_dirty=False
		self.path_dirty=False
		self.environment_dirty=False
		self.room_dirty=False
		self.session_dirty=False
		self.sos=345
		self.fbins=["512","1024","2048"]
		self.fbin=512
		self.chunk_size=500
		self.markers_list=None
		self.ui.statusbar.showMessage("Ready",5000)

	def Save_Session(self):
		if(self.speakers_dirty or self.listeners_dirty or self.path_dirty or self.environment_dirty or self.room_dirty or self.session_dirty):
			if(self.speaker_fname is not None and self.path_fname is not None \
				and self.listeners_fname is not None and self.environment_fname is not None):
				if self.session_fname is None:
					self.session_fname="."
				self.session_fname=unicode(QtGui.QFileDialog.getSaveFileName(self,"Session - Save Session", self.session_fname, "Session Files (*.ses)"))
				if "." not in self.session_fname:
					self.session_fname+=".ses"
				file=QtCore.QFile(self.session_fname)
				if (not file.open(QtCore.QIODevice.WriteOnly | QtCore.QIODevice.Text)):
					QtGui.QMessageBox.warning(self, 'Application', QtCore.QString('Cannot write to file %1:\n%2.').arg(self.session_fname).arg(file.errorString()))
					return False
				else:
					doc=QtXml.QDomDocument("SessionML")
					root_el=doc.createElement("session")
					
					
					#speaker	
					spkr_el=doc.createElement("speakers_file")
					spkr_txt=doc.createTextNode(QtCore.QString(self.speaker_fname))
					spkr_el.appendChild(spkr_txt)
					root_el.appendChild(spkr_el)
					
					#listener
					lstnr_el=doc.createElement("listeners_file")
					lstnr_txt=doc.createTextNode(QtCore.QString(self.listeners_fname))
					lstnr_el.appendChild(lstnr_txt)
					root_el.appendChild(lstnr_el)
					
					#path
					path_el=doc.createElement("path_file")
					path_txt=doc.createTextNode(QtCore.QString(self.path_fname))
					path_el.appendChild(path_txt)
					root_el.appendChild(path_el)
					
					#environment
					env_el=doc.createElement("environment_file")
					env_text=doc.createTextNode(QtCore.QString(self.environment_fname))
					env_el.appendChild(env_text)
					root_el.appendChild(env_el)
					
					#room
					room_el=doc.createElement("room")
					#width
					width_el=doc.createElement('width')
					width_el_txt=doc.createTextNode(QtCore.QString(str(self.room_width)))
					width_el.appendChild(width_el_txt)
					room_el.appendChild(width_el)
					#height
					height_el=doc.createElement('height')
					height_el_txt=doc.createTextNode(QtCore.QString(str(self.room_height)))
					height_el.appendChild(height_el_txt)
					room_el.appendChild(height_el)
					#depth
					depth_el=doc.createElement('depth')
					depth_el_txt=doc.createTextNode(QtCore.QString(str(self.room_depth)))
					depth_el.appendChild(depth_el_txt)
					room_el.appendChild(depth_el)
					
					root_el.appendChild(room_el)
					doc.appendChild(root_el)

					file_text=str(doc.toString())
					file.writeData(file_text)
					file.close()
					if self.speakers_dirty:
						self.Save_Speaker()
					if self.path_dirty:
						self.Save_Path()
					if self.listeners_dirty:
						self.Save_Listeners()
					if self.environment_dirty:
						self.Save_Edit_Environment()
			else:
				QtGui.QMessageBox.warning(self,"Error","Session not ready to save.")
		else:
			QtGui.QMessageBox.warning(self,"Error","Session unchanged.")

	def Load_Session(self):
		"""Loads session from xml file"""
		reply = QtGui.QMessageBox.Yes
		if(self.speakers_dirty or self.listeners_dirty or self.path_dirty or self.environment_dirty):
			reply=QtGui.QMessageBox.question(self,"Action Confirmation","Are you sure you want to load a session file? Unsaved changes will be lost.", QtGui.QMessageBox.Yes|QtGui.QMessageBox.Default,QtGui.QMessageBox.No|QtGui.QMessageBox.Escape)
		if(reply == QtGui.QMessageBox.Yes):
			if self.session_fname is None:
				self.session_fname="."
			self.session_fname=unicode(QtGui.QFileDialog.getOpenFileName(self,"Session - Save Session", self.session_fname, "Session Files (*.ses)"))
			if len(self.session_fname) !=0:
				file=QtCore.QFile(self.session_fname)
				if (not file.open(QtCore.QIODevice.ReadOnly | QtCore.QIODevice.Text)):
					QtGui.QMessageBox.warning(self, 'Application', QtCore.QString('Cannot read file %1:\n%2.').arg(fname).arg(file.errorString()))
					return False
				else:
					doc = QtXml.QDomDocument("SessionML");
					if(not doc.setContent(file)):
						file.close()
						QtGui.QMessageBox.warning(self,"Error","Could not parse xml file.")
					file.close()
					root = doc.documentElement();
					if(root.tagName()!="session"):
						QtGui.QMessageBox.warning(self,"Error","Could not parse xml file. Root Element must be <session/>.")
					else:
						node=root.firstChild()
						while (not node.isNull()):
							if(node.toElement().tagName()=="speakers_file"):
								try:
									child=node.firstChild()
									speaker_fname=child.toText().data()
								except:
									QtGui.QMessageBox.warning(self,"Error","Could not parse xml file. Problem parsing %s."%(node.toElement().tagName()))
							elif(node.toElement().tagName()=="listeners_file"):
								try:
									child=node.firstChild()
									listeners_fname=child.toText().data()
								except:
									QtGui.QMessageBox.warning(self,"Error","Could not parse xml file. Problem parsing %s."%(node.toElement().tagName()))
							elif(node.toElement().tagName()=="path_file"):
								try:
									child=node.firstChild()
									path_fname=child.toText().data()
								except:
									QtGui.QMessageBox.warning(self,"Error","Could not parse xml file. Problem parsing %s."%(node.toElement().tagName()))
							elif(node.toElement().tagName()=="environment_file"):
								try:
									child=node.firstChild()
									environment_fname=child.toText().data()
								except:
									QtGui.QMessageBox.warning(self,"Error","Could not parse xml file. Problem parsing %s."%(node.toElement().tagName()))
							elif(node.toElement().tagName()=="room"):
								child=node.firstChild()
								while(not child.isNull()):
									if(child.toElement().tagName()=="width"):
										try:
											width=float(child.firstChild().toText().data())
										except:
											QtGui.QMessageBox.warning(self,"Error","Could not parse xml file. Problem parsing %s."%(child.toElement().tagName()))
									elif(child.toElement().tagName()=="height"):
										try:
											height=float(child.firstChild().toText().data())
										except:
											QtGui.QMessageBox.warning(self,"Error","Could not parse xml file. Problem parsing %s."%(child.toElement().tagName()))
									elif(child.toElement().tagName()=="depth"):
										try:
											depth=float(child.firstChild().toText().data())
										except:
											QtGui.QMessageBox.warning(self,"Error","Could not parse xml file. Problem parsing %s."%(child.toElement().tagName()))
									else:
										QtGui.QMessageBox.warning(self,"Error","Could not parse xml file. Problem parsing %s. Unrecognized or invalid tag."%(child.toElement().tagName()))
									child=child.nextSibling()
							else:
								QtGui.QMessageBox.warning(self,"Error","Could not parse xml file. Problem parsing %s. Unrecognized or invalid tag."%(node.toElement().tagName()))
							node=node.nextSibling()
						self.Update_Room_Coords(width,height,depth)
						self.Load_Speaker_File(speaker_fname)
						self.Load_Listeners_File(listeners_fname)
						self.Load_Path_File(path_fname)
						self.Load_Environment_File(environment_fname)
						self.session_dirty=False

	def Edit_Environment(self):
		if self.environment_dockWidget is None:
			self.environment_dockWidget=EnvironmentDockWidget(self,self.sos,self.fbins,self.chunk_size)
			self.addDockWidget(QtCore.Qt.TopDockWidgetArea,self.environment_dockWidget)
		selected=self.fbins.index(str(self.fbin))
		self.environment_dockWidget.ui.comboBox_NFBins.setCurrentIndex(selected)
		self.environment_dockWidget.show()
		self.connect(self.environment_dockWidget.ui.pushButton_Save,QtCore.SIGNAL('clicked()'),self.Save_Edit_Environment)
		self.connect(self.environment_dockWidget.ui.pushButton_Load,QtCore.SIGNAL('clicked()'),self.Load_Edit_Environment)
		self.connect(self.environment_dockWidget.ui.comboBox_NFBins,QtCore.SIGNAL('currentIndexChanged(int)'),self.Set_Environment_Dirty)
		self.connect(self.environment_dockWidget.ui.lineEdit_SpeedOfSound,QtCore.SIGNAL('textEdited(QString)'),self.Set_Environment_Dirty)
		self.connect(self.environment_dockWidget.ui.lineEdit_ChunkSize,QtCore.SIGNAL('textEdited(QString)'),self.Set_Environment_Dirty)
	
	def Set_Environment_Dirty(self):
		self.environment_dirty=True

	def Close_Edit_Environment(self):
		self.environment_dockWidget.close()

	def Save_Edit_Environment(self):
		"""Save enviroment to xml file"""
		self.environment_dirty=False
		self.sos=int(self.environment_dockWidget.ui.lineEdit_SpeedOfSound.text())
		self.fbin=int(self.environment_dockWidget.ui.comboBox_NFBins.currentText())
		self.chunk_size=int(self.environment_dockWidget.ui.lineEdit_ChunkSize.text())
		if self.environment_fname is None:
			self.environment_dirty=True
			self.environment_fname="."
		self.environment_fname=unicode(QtGui.QFileDialog.getSaveFileName(self,"Environment - Save Environment", self.environment_fname, "Environment Files (*.env)"))
		if "." not in self.environment_fname:
			self.environment_fname+=".env"
		file=QtCore.QFile(self.environment_fname)
		if (not file.open(QtCore.QIODevice.WriteOnly | QtCore.QIODevice.Text)):
			QtGui.QMessageBox.warning(self, 'Application', QtCore.QString('Cannot write to file %1:\n%2.').arg(fname).arg(file.errorString()))
			return False
		else:
			doc=QtXml.QDomDocument("EnvironmentML")
			root_el=doc.createElement("environment")
			
			sos_el=doc.createElement("speed_of_sound")
			sos_txt=doc.createTextNode(QtCore.QString(str(self.sos)))#conversion to str first prevents univode error
			sos_el.appendChild(sos_txt)
			root_el.appendChild(sos_el)
			
			fbin_el=doc.createElement("frequency_bin")
			fbin_txt=doc.createTextNode(QtCore.QString(str(self.fbin)))
			fbin_el.appendChild(fbin_txt)
			root_el.appendChild(fbin_el)
			
			chunk_size_el=doc.createElement("chunk_size")
			chunk_size_txt=doc.createTextNode(QtCore.QString(str(self.chunk_size)))
			chunk_size_el.appendChild(chunk_size_txt)
			root_el.appendChild(chunk_size_el)
			
			"""root_el.setAttribute("speed_of_sound",self.sos)
			root_el.setAttribute("frequency_bin",self.fbin)
			root_el.setAttribute("chunk_size",self.chunk_size)"""
			
			doc.appendChild(root_el)
			file_text=str(doc.toString())
			file.writeData(file_text)
			file.close()
			self.ui.statusbar.showMessage("Environment Saved",2000)

	def Load_Edit_Environment(self):
		"""Loads enviroment from xml file."""
		self.environment_dirty=False
		if self.environment_fname is None:
			self.environment_dirty=True
			self.environment_fname="."
		self.environment_fname=unicode(QtGui.QFileDialog.getOpenFileName(self,"Environment - Load Environment", self.environment_fname, "Environment Files (*.env)"))
		if len(self.environment_fname) !=0:
			file=QtCore.QFile(self.environment_fname)
			self.Load_Environment_File(self.environment_fname)
			self.environment_dockWidget.ui.lineEdit_SpeedOfSound.setText(str(self.sos))
			self.environment_dockWidget.ui.lineEdit_ChunkSize.setText(str(self.chunk_size))
			selected=self.fbins.index(str(self.fbin))
			self.environment_dockWidget.ui.comboBox_NFBins.setCurrentIndex(selected)

	def Load_Environment_File(self,fname=None):
		"""Loads enviroment from xml file."""
		if fname is not None:
			self.environment_fname=fname
			file=QtCore.QFile(self.environment_fname)
			if (not file.open(QtCore.QIODevice.ReadOnly | QtCore.QIODevice.Text)):
					QtGui.QMessageBox.warning(self, 'Application', QtCore.QString('Cannot read file %1:\n%2.').arg(fname).arg(file.errorString()))
					return False
			else:
				doc = QtXml.QDomDocument("EnvironmentML");
				if(not doc.setContent(file)):
					file.close()
					QtGui.QMessageBox.warning(self,"Error","Could not parse xml file.")
				file.close()
				root = doc.documentElement();
				if(root.tagName()!="environment"):
					QtGui.QMessageBox.warning(self,"Error","Could not parse xml file. Root Element must be <environment/>.")
				else:
					node=root.firstChild()
					while(not node.isNull()):
						if(node.toElement().tagName()=="speed_of_sound"):
							try:
								child=node.firstChild()
								self.sos=int(child.toText().data())
							except:
								QtGui.QMessageBox.warning(self,"Error","Could not parse xml file. Problem parsing %s."%(node.toElement().tagName()))
						elif(node.toElement().tagName()=="frequency_bin"):
							try:
								child=node.firstChild()
								self.fbin=int(child.toText().data())
							except:
								QtGui.QMessageBox.warning(self,"Error","Could not parse xml file. Problem parsing %s."%(node.toElement().tagName()))
						elif(node.toElement().tagName()=="chunk_size"):
							try:
								child=node.firstChild()
								self.chunk_size=child.toText().data()
							except:
								QtGui.QMessageBox.warning(self,"Error","Could not parse xml file. Problem parsing %s."%(node.toElement().tagName()))
						else:
							QtGui.QMessageBox.warning(self,"Error","Could not parse xml file. Problem parsing %s. Unrecognized or invalid tag."%(node.toElement().tagName()))
						node=node.nextSibling()
				self.session_dirty=True
				self.environment_dirty=False
					


	def Resize_Room(self):
		self.room_dirty=True
		width=float(self.ui.lineEdit_width.text())
		height=float(self.ui.lineEdit_height.text())
		depth=float(self.ui.lineEdit_depth.text())
		self.Update_Room_Coords(width,height,depth)

	def Update_Room_Coords(self,width=None,height=None,depth=None):
		if width is not None:
			self.room_width=width
		else:
			width=self.room_width
		if height is not None:
			self.room_height=height
		else:
			height=self.room_height
		if depth is not None:
			self.room_depth=depth
		else:
			depth=self.room_depth	
		self.ui.lineEdit_width.setText(str(width))
		self.ui.lineEdit_height.setText(str(height))
		self.ui.lineEdit_depth.setText(str(depth))
		self.ui.graphicsView.updateRoom(width,height,depth)


	def closeEvent(self,event):
		reply = QtGui.QMessageBox.Yes
		if(self.speakers_dirty or self.listeners_dirty or self.path_dirty):
			reply=QtGui.QMessageBox.question(self,"Action Confirmation","Are you sure you want to close the application? Unsaved changes will be lost.", QtGui.QMessageBox.Yes|QtGui.QMessageBox.Default,QtGui.QMessageBox.No|QtGui.QMessageBox.Escape)
		if(reply == QtGui.QMessageBox.Yes):
			pass
		else:
			event.ignore()

	#Path Tab Implementation
	def New_Path_Point_Dialog(self):
		self.point_dialog=PointDialog()
		self.connect(self.point_dialog.ui.buttonBox,QtCore.SIGNAL('rejected()'),self.Close_Path_Point_Dialog)
		self.connect(self.point_dialog.ui.buttonBox,QtCore.SIGNAL('accepted()'),self.Add_Path_Point_Dialog)
		self.point_dialog.show()

	def Update_Selected_Point(self,selected=-1):
		self.ui.graphicsView.path_renderer.set_selected(selected)
		self.ui.graphicsView.updateGL()
		point=self.ui.listWidget_Path.item(selected)
		try:
			marker=self.point_manager.dict[point]
			self.audio_dockWidget.wave.markers_list.highlight_selected(marker)
		except KeyError:
			self.audio_dockWidget.wave.markers_list.highlight_selected(None)

	def Close_Path_Point_Dialog(self):
		self.point_dialog.close()

	def Add_Path_Point_Dialog(self):
		try:
			xpos=float(self.point_dialog.ui.lineEdit_X.text())
			ypos=float(self.point_dialog.ui.lineEdit_Y.text())
			zpos=float(self.point_dialog.ui.lineEdit_Z.text())
			#print "X:", xpos, "Y:", ypos, "Z:", zpos
			point=Point3D(xpos,ypos,zpos)
			self.ui.listWidget_Path.addItem(point)
			count=self.ui.listWidget_Path.count()
			points_list=[]
			for i in range(0,count):
				points_list.append(self.ui.listWidget_Path.item(i))
			self.path_dirty=True
			self.ui.graphicsView.updatePath(points_list)
			#see if we want to set a marker
			self.marker_dialog=MarkerDialog(point,self)
			#self.marker_dialog.load_markers(self.markers_list)
			self.marker_dialog.load_markers(self.point_manager.markers_list)
			self.connect(self.marker_dialog.ui.pushButton_Cancel,QtCore.SIGNAL('clicked()'),self.marker_dialog.close)
			self.connect(self.marker_dialog,QtCore.SIGNAL('marker_set'),self.point_manager.attach_marker_to_point)
			self.connect(self.marker_dialog,QtCore.SIGNAL('marker_selected'),self.audio_dockWidget.wave.markers_list.highlight_selected)
			self.connect(self.point_manager,QtCore.SIGNAL('markers_updated'),self.marker_dialog.load_markers)
			self.marker_dialog.show()
		except ValueError:
			QtGui.QMessageBox.warning(self,"Error","Invalid coordinates entered, no point added.")
	
	def Delete_Path_Point(self):
		self.ui.listWidget_Path.takeItem(self.ui.listWidget_Path.currentRow())
		count=self.ui.listWidget_Path.count()
		points_list=[]
		for i in range(0,count):
			points_list.append(self.ui.listWidget_Path.item(i))
		self.path_dirty=True
		self.ui.graphicsView.updatePath(points_list)
	
	def Edit_Path_Point_Dialog(self):
		point=self.ui.listWidget_Path.currentItem()
		if(point is None):
			QtGui.QMessageBox.warning(self,"Error","No point selected, please select a point to edit.")
		else:
			self.point_dialog=PointDialog()
			self.connect(self.point_dialog.ui.buttonBox,QtCore.SIGNAL('rejected()'),self.Close_Path_Point_Dialog)
			self.connect(self.point_dialog.ui.buttonBox,QtCore.SIGNAL('accepted()'),self.Edit_Path_Point)
			self.point_dialog.set_point(point)
			self.point_dialog.show()

	def Edit_Path_Point(self):
		point=self.ui.listWidget_Path.currentItem()
		row=self.ui.listWidget_Path.currentRow()
		try:
			xpos=float(self.point_dialog.ui.lineEdit_X.text())
			ypos=float(self.point_dialog.ui.lineEdit_Y.text())
			zpos=float(self.point_dialog.ui.lineEdit_Z.text())
			#edited_point=Point3D(xpos,ypos,zpos)
			#self.ui.listWidget_Path.insertItem(row,edited_point)
			#self.ui.listWidget_Path.takeItem(row+1)
			point=self.ui.listWidget_Path.item(row)
			point.update_coords(xpos,ypos,zpos)
			count=self.ui.listWidget_Path.count()
			points_list=[]
			for i in range(0,count):
				points_list.append(self.ui.listWidget_Path.item(i))
			self.path_dirty=True
			self.ui.graphicsView.updatePath(points_list)
			#see if we want to set/update a marker
			self.marker_dialog=MarkerDialog(point,self)
			#self.marker_dialog.load_markers(self.markers_list)
			self.marker_dialog.load_markers(self.point_manager.markers_list)
			#self.marker_dialog.set_selected_marker(self.point_manager.dict[point])
			self.connect(self.marker_dialog.ui.pushButton_Cancel,QtCore.SIGNAL('clicked()'),self.marker_dialog.close)
			self.connect(self.marker_dialog,QtCore.SIGNAL('marker_set'),self.point_manager.attach_marker_to_point)
			self.connect(self.marker_dialog,QtCore.SIGNAL('marker_selected'),self.audio_dockWidget.wave.markers_list.highlight_selected)
			self.connect(self.point_manager,QtCore.SIGNAL('markers_updated'),self.marker_dialog.load_markers)
			self.marker_dialog.show()
		except ValueError:
			QtGui.QMessageBox.warning(self,"Error","Invalid coordinates entered, point unchanged.")	

	def Insert_Above_Path_Point_Dialog(self):
		point=self.ui.listWidget_Path.currentItem()
		if(point is None):
			QtGui.QMessageBox.warning(self,"Error","No point selected, please select a point to insert a point above.")
		else:
			self.point_dialog=PointDialog()
			self.connect(self.point_dialog.ui.buttonBox,QtCore.SIGNAL('rejected()'),self.Close_Path_Point_Dialog)
			self.connect(self.point_dialog.ui.buttonBox,QtCore.SIGNAL('accepted()'),self.Insert_Above_Path_Point)
			self.point_dialog.show()
	
	def Insert_Above_Path_Point(self):
		try:
			point=self.ui.listWidget_Path.currentItem()
			row=self.ui.listWidget_Path.currentRow()
			xpos=float(self.point_dialog.ui.lineEdit_X.text())
			ypos=float(self.point_dialog.ui.lineEdit_Y.text())
			zpos=float(self.point_dialog.ui.lineEdit_Z.text())
			edited_point=Point3D(xpos,ypos,zpos)
			self.ui.listWidget_Path.insertItem(row,edited_point)
			count=self.ui.listWidget_Path.count()
			points_list=[]
			for i in range(0,count):
				points_list.append(self.ui.listWidget_Path.item(i))
			self.path_dirty=True
			self.ui.graphicsView.updatePath(points_list)
		except ValueError:
			QtGui.QMessageBox.warning(self,"Error","Invalid coordinates entered, no point added.")
	
	def Insert_Below_Path_Point_Dialog(self):
		point=self.ui.listWidget_Path.currentItem()
		if(point is None):
			QtGui.QMessageBox.warning(self,"Error","No point selected, please select a point to insert a point below.")
		else:
			self.point_dialog=PointDialog()
			self.connect(self.point_dialog.ui.buttonBox,QtCore.SIGNAL('rejected()'),self.Close_Path_Point_Dialog)
			self.connect(self.point_dialog.ui.buttonBox,QtCore.SIGNAL('accepted()'),self.Insert_Below_Path_Point)
			self.point_dialog.show()
	
	def Insert_Below_Path_Point(self):
		try:
			point=self.ui.listWidget_Path.currentItem()
			row=self.ui.listWidget_Path.currentRow()
			xpos=float(self.point_dialog.ui.lineEdit_X.text())
			ypos=float(self.point_dialog.ui.lineEdit_Y.text())
			zpos=float(self.point_dialog.ui.lineEdit_Z.text())
			edited_point=Point3D(xpos,ypos,zpos)
			self.ui.listWidget_Path.insertItem(row+1,edited_point)
			count=self.ui.listWidget_Path.count()
			points_list=[]
			for i in range(0,count):
				points_list.append(self.ui.listWidget_Path.item(i))
			self.path_dirty=True
			self.ui.graphicsView.updatePath(points_list)
		except ValueError:
			QtGui.QMessageBox.warning(self,"Error","No Coordinates entered, no point added.")

	def Save_Path(self):
		#xml format
		count=self.ui.listWidget_Path.count()
		if(count>0):
			if self.path_fname is None:
				self.path_fname="."
			fname=unicode(QtGui.QFileDialog.getSaveFileName(self,"Path - Save Path", self.path_fname, "Path Files (*.path)"))
			if len(fname) !=0:
				self.path_fname=fname
				if "." not in self.path_fname:
					self.path_fname+=".path"
				self.Save_Path_File(self.path_fname)

	def Save_Path_File(self,fname=None):
		"""Saves path info to xml file"""
		count=self.ui.listWidget_Path.count()
		if fname is not None:
			self.path_fname=fname
		file=QtCore.QFile(self.path_fname)
		if (not file.open(QtCore.QIODevice.WriteOnly | QtCore.QIODevice.Text)):
			QtGui.QMessageBox.warning(self, 'Application', QtCore.QString('Cannot write to file %1:\n%2.').arg(fname).arg(file.errorString()))
			return False
		else:
			doc=QtXml.QDomDocument("PathML")
			root_el=doc.createElement("path_list")
			
			for i in range(0,count):
				path_el=doc.createElement("path_point")
				
				coord_el=doc.createElement("coordinate")
				coord_el.setAttribute("type","cartesian")
				
				c1_el=doc.createElement("c1")
				c1_txt=doc.createTextNode(str(self.ui.listWidget_Path.item(i).x))
				c1_el.appendChild(c1_txt)
				coord_el.appendChild(c1_el)
				
				c2_el=doc.createElement("c2")
				c2_txt=doc.createTextNode(str(self.ui.listWidget_Path.item(i).y))
				c2_el.appendChild(c2_txt)
				coord_el.appendChild(c2_el)
				
				c3_el=doc.createElement("c3")
				c3_txt=doc.createTextNode(str(self.ui.listWidget_Path.item(i).z))
				c3_el.appendChild(c3_txt)
				coord_el.appendChild(c3_el)
				
				path_el.appendChild(coord_el)

				root_el.appendChild(path_el)
			
			
			doc.appendChild(root_el)
			path_el=doc.createElement("path_point")

			file_text=str(doc.toString())
			file.writeData(file_text)
			file.close()
			self.path_dirty=False

	def Load_Path(self):
		count=self.ui.listWidget_Path.count()
		reply=QtGui.QMessageBox.Yes
		if(count>0 and self.path_dirty):
			reply=QtGui.QMessageBox.question(self,"Action Confirmation","Are you sure you want to load a path file? Current path will be lost.",QtGui.QMessageBox.Yes|QtGui.QMessageBox.Default,QtGui.QMessageBox.No|QtGui.QMessageBox.Escape)
		if(reply == QtGui.QMessageBox.Yes):
			if self.path_fname is None:
				self.path_fname="."
			fname=unicode(QtGui.QFileDialog.getOpenFileName(self,"Path - Save Path", self.path_fname, "Path Files (*.path)"))
			if len(fname) !=0:
				self.path_fname=fname
				if "." not in self.path_fname:
					self.path_fname+=".path"
				self.Load_Path_File(self.path_fname)

	def Load_Path_File(self,fname=None):
		if fname is not None:
			self.path_fname=fname
		file=QtCore.QFile(self.path_fname)
		if (not file.open(QtCore.QIODevice.ReadOnly | QtCore.QIODevice.Text)):
			QtGui.QMessageBox.warning(self, 'Application', QtCore.QString('Cannot read file %1:\n%2.').arg(fname).arg(file.errorString()))
			return False
		else:
			doc = QtXml.QDomDocument("PathML");
			if(not doc.setContent(file)):
				file.close()
				QtGui.QMessageBox.warning(self,"Error","Could not parse xml file.")
			file.close()
			root = doc.documentElement();
			if(root.tagName()!="path_list"):
				QtGui.QMessageBox.warning(self,"Error","Could not parse xml file. Root Element must be <path_list/>.")
			else:
				self.ui.listWidget_Path.clear()
				node = root.firstChild()
				while(not node.isNull()):
					if(node.toElement().tagName()=="path_point"):
						try:
							coord_type=node.firstChild()
						except:
							QtGui.QMessageBox.warning(self,"Error","Could not parse xml file. Problem parsing %s."%(coord_type.toElement().tagName()))
							break
						if(not coord_type.isNull()):
							if(str(coord_type.toElement().attribute("type",""))=="cartesian"):
								child=coord_type.firstChild()
								xpos=None
								ypos=None
								zpos=None
								while(not child.isNull()):
									if(child.toElement().tagName()=="c1"):
										try:
											xpos=float(child.firstChild().toText().data())
										except:
											QtGui.QMessageBox.warning(self,"Error","Could not parse xml file. Problem parsing %s." %(child.toElement().tagName()))
											break
									elif(child.toElement().tagName()=="c2"):
										try:
											ypos=float(child.firstChild().toText().data())
										except:
											QtGui.QMessageBox.warning(self,"Error","Could not parse xml file. Problem parsing %s."%(child.toElement().tagName()))
											break
									elif(child.toElement().tagName()=="c3"):
										try:
											zpos=float(child.firstChild().toText().data())
										except:
											QtGui.QMessageBox.warning(self,"Error","Could not parse xml file. Problem parsing %s."%(child.toElement().tagName()))
											break
									else:
										QtGui.QMessageBox.warning(self,"Error","Could not parse xml file. Problem parsing %s. Unknown or incorrect tag."%(child.toElement().tagName()))
										break
									#print "X:", xpos, "Y:", ypos, "Z:", zpos
									if(xpos is not None and ypos is not None and zpos is not None):
										point=Point3D(xpos,ypos,zpos)
										self.ui.listWidget_Path.addItem(point)
										count=self.ui.listWidget_Path.count()
									child=child.nextSibling()
							else:
								QtGui.QMessageBox.warning(self,"Error","Could not parse xml file. Only cartesian points supported."%(node.toElement().tagName()))
					"""else:
						 QtGui.QMessageBox.warning(self,"Error","Could not parse xml file. Problem parsing %s. Unknown or incorrect tag. "%(node.toElement().tagName()))"""
					node=node.nextSibling()
				count=self.ui.listWidget_Path.count()
				itemslist=[]
				for i in range(0,count):
					itemslist.append(self.ui.listWidget_Path.item(i))
				self.ui.graphicsView.updatePath(itemslist)
				self.path_dirty=False
				self.session_dirty=True

	#Listeners Tab Implementation
	def New_Listeners_Point_Dialog(self):
		self.point_dialog=PointDialog()
		self.connect(self.point_dialog.ui.buttonBox,QtCore.SIGNAL('rejected()'),self.Close_Listeners_Point_Dialog)
		self.connect(self.point_dialog.ui.buttonBox,QtCore.SIGNAL('accepted()'),self.Add_Listeners_Point_Dialog)
		self.point_dialog.show()

	def Close_Listeners_Point_Dialog(self):
		self.point_dialog.close()

	def Add_Listeners_Point_Dialog(self):
		try:
			xpos=float(self.point_dialog.ui.lineEdit_X.text())
			ypos=float(self.point_dialog.ui.lineEdit_Y.text())
			zpos=float(self.point_dialog.ui.lineEdit_Z.text())
			#print "X:", xpos, "Y:", ypos, "Z:", zpos
			point=Point3D(xpos,ypos,zpos)
			self.ui.listWidget_Listeners.addItem(point)
			count=self.ui.listWidget_Listeners.count()
			listener_list=[]
			for i in range(0,count):
				listener_list.append(self.ui.listWidget_Listeners.item(i))
			self.listeners_dirty=True
			self.ui.graphicsView.updateListeners(listener_list)
		except ValueError:
			QtGui.QMessageBox.warning(self,"Error","Invalid coordinates entered, no point added.")
	
	def Delete_Listeners_Point(self):
		self.ui.listWidget_Listeners.takeItem(self.ui.listWidget_Listeners.currentRow())
		count=self.ui.listWidget_Listeners.count()
		listener_list=[]
		for i in range(0,count):
			listener_list.append(self.ui.listWidget_Listeners.item(i))
		self.listeners_dirty=True
		self.ui.graphicsView.updateListeners(listener_list)
	
	def Edit_Listeners_Point_Dialog(self):
		point=self.ui.listWidget_Listeners.currentItem()
		if(point is None):
			QtGui.QMessageBox.warning(self,"Error","No point selected, please select a point to edit.")
		else:
			self.point_dialog=PointDialog()
			self.connect(self.point_dialog.ui.buttonBox,QtCore.SIGNAL('rejected()'),self.Close_Listeners_Point_Dialog)
			self.connect(self.point_dialog.ui.buttonBox,QtCore.SIGNAL('accepted()'),self.Edit_Listeners_Point)
			self.point_dialog.set_point(point)
			self.point_dialog.show()

	def Edit_Listeners_Point(self):
		point=self.ui.listWidget_Listeners.currentItem()
		row=self.ui.listWidget_Listeners.currentRow()
		try:
			xpos=float(self.point_dialog.ui.lineEdit_X.text())
			ypos=float(self.point_dialog.ui.lineEdit_Y.text())
			zpos=float(self.point_dialog.ui.lineEdit_Z.text())
			point=self.ui.listWidget_Listeners.item(row)
			point.update_coords(xpos,ypos,zpos)
			count=self.ui.listWidget_Path.count()
			count=self.ui.listWidget_Listeners.count()
			listener_list=[]
			for i in range(0,count):
				listener_list.append(self.ui.listWidget_Listeners.item(i))
			self.listeners_dirty=True
			self.ui.graphicsView.updateListeners(listener_list)
		except ValueError:
			QtGui.QMessageBox.warning(self,"Error","Invalid coordinates entered, point unchanged.")
	
	def Insert_Above_Listeners_Point_Dialog(self):
		point=self.ui.listWidget_Listeners.currentItem()
		if(point is None):
			QtGui.QMessageBox.warning(self,"Error","No point selected, please select a point to insert a point above.")
		else:
			self.point_dialog=PointDialog()
			self.connect(self.point_dialog.ui.buttonBox,QtCore.SIGNAL('rejected()'),self.Close_Listeners_Point_Dialog)
			self.connect(self.point_dialog.ui.buttonBox,QtCore.SIGNAL('accepted()'),self.Insert_Above_Listeners_Point)
			self.point_dialog.show()
	
	def Insert_Above_Listeners_Point(self):
		try:
			point=self.ui.listWidget_Listeners.currentItem()
			row=self.ui.listWidget_Listeners.currentRow()
			xpos=float(self.point_dialog.ui.lineEdit_X.text())
			ypos=float(self.point_dialog.ui.lineEdit_Y.text())
			zpos=float(self.point_dialog.ui.lineEdit_Z.text())
			edited_point=Point3D(xpos,ypos,zpos)
			self.ui.listWidget_Listeners.insertItem(row,edited_point)
			count=self.ui.listWidget_Listeners.count()
			listener_list=[]
			for i in range(0,count):
				listener_list.append(self.ui.listWidget_Listeners.item(i))
			self.listeners_dirty=True
			self.ui.graphicsView.updateListeners(listener_list)
		except ValueError:
			QtGui.QMessageBox.warning(self,"Error","Invalid coordinates entered, no point added.")
	
	def Insert_Below_Listeners_Point_Dialog(self):
		point=self.ui.listWidget_Listeners.currentItem()
		if(point is None):
			QtGui.QMessageBox.warning(self,"Error","No point selected, please select a point to insert a point below.")
		else:
			self.point_dialog=PointDialog()
			self.connect(self.point_dialog.ui.buttonBox,QtCore.SIGNAL('rejected()'),self.Close_Listeners_Point_Dialog)
			self.connect(self.point_dialog.ui.buttonBox,QtCore.SIGNAL('accepted()'),self.Insert_Below_Listeners_Point)
			self.point_dialog.show()
	
	def Insert_Below_Listeners_Point(self):
		try:
			point=self.ui.listWidget_Listeners.currentItem()
			row=self.ui.listWidget_Listeners.currentRow()
			xpos=float(self.point_dialog.ui.lineEdit_X.text())
			ypos=float(self.point_dialog.ui.lineEdit_Y.text())
			zpos=float(self.point_dialog.ui.lineEdit_Z.text())
			edited_point=Point3D(xpos,ypos,zpos)
			self.ui.listWidget_Listeners.insertItem(row+1,edited_point)
			count=self.ui.listWidget_Listeners.count()
			listener_list=[]
			for i in range(0,count):
				listener_list.append(self.ui.listWidget_Listeners.item(i))
			self.listeners_dirty=True
			self.ui.graphicsView.updateListeners(listener_list)
		except ValueError:
			QtGui.QMessageBox.warning(self,"Error","Invalid coordinates entered, no point added.")

	def Save_Listeners(self):
		if self.listeners_dirty:
			count=self.ui.listWidget_Listeners.count()
			if(count>0):
				if self.listeners_fname is None:
					self.listeners_fname="."
				fname=unicode(QtGui.QFileDialog.getSaveFileName(self,"Listeners - Save Listeners", self.listeners_fname, "Listeners Files (*.lsnr)"))
				if len(fname)!=0:
					self.listeners_fname=fname
					if "." not in self.listeners_fname:
						self.listeners_fname+=".lsnr"
					self.Save_Listeners_File(self.listeners_fname)

	def Save_Listeners_File(self,fname=None):
		count=self.ui.listWidget_Listeners.count()
		if fname is not None:
			self.listeners_fname=fname
		file=QtCore.QFile(self.listeners_fname)
		if (not file.open(QtCore.QIODevice.WriteOnly | QtCore.QIODevice.Text)):
			QtGui.QMessageBox.warning(self, 'Application', QtCore.QString('Cannot write to file %1:\n%2.').arg(fname).arg(file.errorString()))
			return False
		else:
			doc=QtXml.QDomDocument("ListnerML")
			root_el=doc.createElement("listeners_list")
			doc.appendChild(root_el)
			lsnr_el=doc.createElement("listeners_location")
			for i in range(0,count):
				lsnr_el=doc.createElement("listeners_location")
				
				coord_el=doc.createElement("coordinate")
				coord_el.setAttribute("type","cartesian")
				
				c1_el=doc.createElement("c1")
				c1_txt=doc.createTextNode(str(self.ui.listWidget_Listeners.item(i).x))
				c1_el.appendChild(c1_txt)
				coord_el.appendChild(c1_el)
				
				c2_el=doc.createElement("c2")
				c2_txt=doc.createTextNode(str(self.ui.listWidget_Listeners.item(i).y))
				c2_el.appendChild(c2_txt)
				coord_el.appendChild(c2_el)
				
				c3_el=doc.createElement("c3")
				c3_txt=doc.createTextNode(str(self.ui.listWidget_Listeners.item(i).z))
				c3_el.appendChild(c3_txt)
				coord_el.appendChild(c3_el)
				
				lsnr_el.appendChild(coord_el)

				root_el.appendChild(lsnr_el)
				
			file_text=str(doc.toString())
			file.writeData(file_text)
			file.close()
			self.listeners_dirty=False

	def Load_Listeners(self):
		count=self.ui.listWidget_Listeners.count()
		reply=QtGui.QMessageBox.Yes
		if(count>0 and self.listeners_dirty):
			reply=QtGui.QMessageBox.question(self,"Action Confirmation","Are you sure you want to load a listner file? Current listeners will be lost.",QtGui.QMessageBox.Yes|QtGui.QMessageBox.Default,QtGui.QMessageBox.No|QtGui.QMessageBox.Escape)
		if(reply == QtGui.QMessageBox.Yes):
			if self.listeners_fname is None:
				self.listeners_fname="."
			fname=unicode(QtGui.QFileDialog.getOpenFileName(self,"Listeners - Save Listeners", self.listeners_fname, "Listeners Files (*.lsnr)"))
			if len(fname)!=0:
				self.listeners_fname=fname
				if "." not in self.listeners_fname:
					self.listeners_fname+=".lsnr"
				self.Load_Listeners_File(self.listeners_fname)

	def Load_Listeners_File(self,fname=None):
		if fname is not None:
			self.listeners_fname=fname
		file=QtCore.QFile(self.listeners_fname)
		if (not file.open(QtCore.QIODevice.ReadOnly | QtCore.QIODevice.Text)):
			QtGui.QMessageBox.warning(self, 'Application', QtCore.QString('Cannot read file %1:\n%2.').arg(fname).arg(file.errorString()))
			return False
		else:
			doc = QtXml.QDomDocument("ListenerML");
			if(not doc.setContent(file)):
				file.close()
				QtGui.QMessageBox.warning(self,"Error","Could not parse xml file.")
			file.close()
			root = doc.documentElement();
			if(root.tagName()!="listeners_list"):
				QtGui.QMessageBox.warning(self,"Error","Could not parse xml file. Root Element must be <listener_list/>.")
			else:
				self.ui.listWidget_Listeners.clear()
				node = root.firstChild()
				while(not node.isNull()):
					if(node.toElement().tagName()=="listeners_location"):
						try:
							coord_type=node.firstChild()
						except:
							QtGui.QMessageBox.warning(self,"Error","Could not parse xml file. Problem parsing %s."%(coord_type.toElement().tagName()))
							break
						if(not coord_type.isNull()):
							if(str(coord_type.toElement().attribute("type",""))=="cartesian"):
								child=coord_type.firstChild()
								xpos=None
								ypos=None
								zpos=None
								while(not child.isNull()):
									if(child.toElement().tagName()=="c1"):
										try:
											xpos=float(child.firstChild().toText().data())
										except:
											QtGui.QMessageBox.warning(self,"Error","Could not parse xml file. Problem parsing %s." %(child.toElement().tagName()))
											break
									elif(child.toElement().tagName()=="c2"):
										try:
											ypos=float(child.firstChild().toText().data())
										except:
											QtGui.QMessageBox.warning(self,"Error","Could not parse xml file. Problem parsing %s."%(child.toElement().tagName()))
											break
									elif(child.toElement().tagName()=="c3"):
										try:
											zpos=float(child.firstChild().toText().data())
										except:
											QtGui.QMessageBox.warning(self,"Error","Could not parse xml file. Problem parsing %s."%(child.toElement().tagName()))
											break
									else:
										QtGui.QMessageBox.warning(self,"Error","Could not parse xml file. Problem parsing %s. Unknown or incorrect tag."%(child.toElement().tagName()))
										break
									#print "X:", xpos, "Y:", ypos, "Z:", zpos
									if(xpos is not None and ypos is not None and zpos is not None):
										point=Point3D(xpos,ypos,zpos)
										self.ui.listWidget_Listeners.addItem(point)
										count=self.ui.listWidget_Listeners.count()
									child=child.nextSibling()
							else:
								QtGui.QMessageBox.warning(self,"Error","Could not parse xml file. Only cartesian points supported."%(node.toElement().tagName()))
					"""else:
						 QtGui.QMessageBox.warning(self,"Error","Could not parse xml file. Problem parsing %s. Unknown or incorrect tag. "%(node.toElement().tagName()))"""
					node=node.nextSibling()
				count=self.ui.listWidget_Listeners.count()
				itemslist=[]
				for i in range(0,count):
					itemslist.append(self.ui.listWidget_Listeners.item(i))
				self.ui.graphicsView.updateListeners(itemslist)
				self.listeners_dirty=False
				self.session_dirty=True

	#Speakers Tab Implementation
	def New_Speaker_Point_Dialog(self):
		self.point_dialog=PointDialog()
		self.connect(self.point_dialog.ui.buttonBox,QtCore.SIGNAL('rejected()'),self.Close_Speaker_Point_Dialog)
		self.connect(self.point_dialog.ui.buttonBox,QtCore.SIGNAL('accepted()'),self.Add_Speaker_Point_Dialog)
		self.point_dialog.show()

	def Update_Selected_Speaker(self,selected=-1):
		self.ui.graphicsView.speaker_renderer.set_selected(selected)
		self.ui.graphicsView.updateGL()

	def Close_Speaker_Point_Dialog(self):
		self.point_dialog.close()

	def Add_Speaker_Point_Dialog(self):
		try:
			xpos=float(self.point_dialog.ui.lineEdit_X.text())
			ypos=float(self.point_dialog.ui.lineEdit_Y.text())
			zpos=float(self.point_dialog.ui.lineEdit_Z.text())
			#print "X:", xpos, "Y:", ypos, "Z:", zpos
			point=Point3D(xpos,ypos,zpos)
			self.ui.listWidget_Speakers.addItem(point)
			count=self.ui.listWidget_Speakers.count()
			itemslist=[]
			for i in range(0,count):
				itemslist.append(self.ui.listWidget_Speakers.item(i))
			self.ui.graphicsView.updateSpeakers(itemslist)
			self.speakers_dirty=True
		except ValueError:
			QtGui.QMessageBox.warning(self,"Error","Invalid coordinates entered, no point added.")
	
	def Delete_Speaker_Point(self):
		self.ui.listWidget_Speakers.takeItem(self.ui.listWidget_Speakers.currentRow())
		count=self.ui.listWidget_Speakers.count()
		itemslist=[]
		for i in range(0,count):
			itemslist.append(self.ui.listWidget_Speakers.item(i))
		self.speakers_dirty=True
		self.ui.graphicsView.updateSpeakers(itemslist)

	def Edit_Speaker_Point_Dialog(self):
		point=self.ui.listWidget_Speakers.currentItem()
		if(point is None):
			QtGui.QMessageBox.warning(self,"Error","No point selected, please select a point to edit.")
		else:
			self.point_dialog=PointDialog()
			self.connect(self.point_dialog.ui.buttonBox,QtCore.SIGNAL('rejected()'),self.Close_Speaker_Point_Dialog)
			self.connect(self.point_dialog.ui.buttonBox,QtCore.SIGNAL('accepted()'),self.Edit_Speaker_Point)
			self.point_dialog.set_point(point)
			self.point_dialog.show()

	def Edit_Speaker_Point(self):
		point=self.ui.listWidget_Speakers.currentItem()
		row=self.ui.listWidget_Speakers.currentRow()
		try:
			xpos=float(self.point_dialog.ui.lineEdit_X.text())
			ypos=float(self.point_dialog.ui.lineEdit_Y.text())
			zpos=float(self.point_dialog.ui.lineEdit_Z.text())
			#edited_point=Point3D(xpos,ypos,zpos)
			#self.ui.listWidget_Speakers.insertItem(row,edited_point)
			#self.ui.listWidget_Speakers.takeItem(row+1)
			point=self.ui.listWidget_Speakers.item(row)
			point.update_coords(zpos,ypos,zpos)
			count=self.ui.listWidget_Speakers.count()
			itemslist=[]
			for i in range(0,count):
				itemslist.append(self.ui.listWidget_Speakers.item(i))
			self.speakers_dirty=True
			self.ui.graphicsView.updateSpeakers(itemslist)
		except ValueError:
			QtGui.QMessageBox.warning(self,"Error","Invalid coordinates entered, point unchanged.")

	def Insert_Above_Speaker_Point_Dialog(self):
		point=self.ui.listWidget_Speakers.currentItem()
		if(point is None):
			QtGui.QMessageBox.warning(self,"Error","No point selected, please select a point to insert a point above.")
		else:
			self.point_dialog=PointDialog()
			self.connect(self.point_dialog.ui.buttonBox,QtCore.SIGNAL('rejected()'),self.Close_Speaker_Point_Dialog)
			self.connect(self.point_dialog.ui.buttonBox,QtCore.SIGNAL('accepted()'),self.Insert_Above_Speaker_Point)
			self.point_dialog.show()
	
	def Insert_Above_Speaker_Point(self):
		try:
			point=self.ui.listWidget_Speakers.currentItem()
			row=self.ui.listWidget_Speakers.currentRow()
			xpos=float(self.point_dialog.ui.lineEdit_X.text())
			ypos=float(self.point_dialog.ui.lineEdit_Y.text())
			zpos=float(self.point_dialog.ui.lineEdit_Z.text())
			edited_point=Point3D(xpos,ypos,zpos)
			self.ui.listWidget_Speakers.insertItem(row,edited_point)
			count=self.ui.listWidget_Speakers.count()
			itemslist=[]
			for i in range(0,count):
				itemslist.append(self.ui.listWidget_Speakers.item(i))
			self.speakers_dirty=True
			self.ui.graphicsView.updateSpeakers(itemslist)
		except ValueError:
			QtGui.QMessageBox.warning(self,"Error","Invalid coordinates entered, no point added.")
	
	def Insert_Below_Speaker_Point_Dialog(self):
		point=self.ui.listWidget_Speakers.currentItem()
		if(point is None):
			QtGui.QMessageBox.warning(self,"Error","No point selected, please select a point to insert a point below.")
		else:
			self.point_dialog=PointDialog()
			self.connect(self.point_dialog.ui.buttonBox,QtCore.SIGNAL('rejected()'),self.Close_Speaker_Point_Dialog)
			self.connect(self.point_dialog.ui.buttonBox,QtCore.SIGNAL('accepted()'),self.Insert_Below_Speaker_Point)
			self.point_dialog.show()
	
	def Insert_Below_Speaker_Point(self):
		try:
			point=self.ui.listWidget_Speakers.currentItem()
			row=self.ui.listWidget_Speakers.currentRow()
			xpos=float(self.point_dialog.ui.lineEdit_X.text())
			ypos=float(self.point_dialog.ui.lineEdit_Y.text())
			zpos=float(self.point_dialog.ui.lineEdit_Z.text())
			edited_point=Point3D(xpos,ypos,zpos)
			self.ui.listWidget_Speakers.insertItem(row+1,edited_point)
			count=self.ui.listWidget_Speakers.count()
			itemslist=[]
			for i in range(0,count):
				itemslist.append(self.ui.listWidget_Speakers.item(i))
			self.speakers_dirty=True
			self.ui.graphicsView.updateSpeakers(itemslist)
		except ValueError:
			QtGui.QMessageBox.warning(self,"Error","Invalid coordinates entered, no point added.")

	def Save_Speaker(self):
		if self.speakers_dirty:
			count=self.ui.listWidget_Speakers.count()
			if(count>0):
				if self.speaker_fname is None:
					self.speaker_fname="."
				fname=unicode(QtGui.QFileDialog.getSaveFileName(self,"Speakers - Save Speakers", self.speaker_fname, "Speaker Files (*.spkr)"))
				if len(fname)!=0:
					self.speaker_fname=fname
					if "." not in self.speaker_fname:
						self.speaker_fname+=".spkr"
					self.Save_Speaker_File(self.speaker_fname)

	def Save_Speaker_File(self,fname=None):
		count=self.ui.listWidget_Speakers.count()
		if fname is not None:
			self.speaker_fname=fname
		file=QtCore.QFile(self.speaker_fname)
		if (not file.open(QtCore.QIODevice.WriteOnly | QtCore.QIODevice.Text)):
			QtGui.QMessageBox.warning(self, 'Application', QtCore.QString('Cannot write to file %1:\n%2.').arg(fname).arg(file.errorString()))
			return False
		else:
			doc=QtXml.QDomDocument("SpeakerML")
			root_el=doc.createElement("speaker_list")
			#root_el.createAttribute("num_spkrs")
			doc.appendChild(root_el)
			spkr_el=doc.createElement("speaker_location")
			"""for i in range(0,count):
				spkr_el=doc.createElement("speaker_location")
				spkr_el.setAttribute("coord_type","cartesian")
				spkr_el.setAttribute("x_pos",str(self.ui.listWidget_Speakers.item(i).x))
				spkr_el.setAttribute("y_pos",str(self.ui.listWidget_Speakers.item(i).y))
				spkr_el.setAttribute("z_pos",str(self.ui.listWidget_Speakers.item(i).z))
				root_el.appendChild(spkr_el)"""
			for i in range(0,count):
				spkr_el=doc.createElement("speaker_location")
				
				coord_el=doc.createElement("coordinate")
				coord_el.setAttribute("type","cartesian")
				
				c1_el=doc.createElement("c1")
				c1_txt=doc.createTextNode(str(self.ui.listWidget_Speakers.item(i).x))
				c1_el.appendChild(c1_txt)
				coord_el.appendChild(c1_el)
				
				c2_el=doc.createElement("c2")
				c2_txt=doc.createTextNode(str(self.ui.listWidget_Speakers.item(i).y))
				c2_el.appendChild(c2_txt)
				coord_el.appendChild(c2_el)
				
				c3_el=doc.createElement("c3")
				c3_txt=doc.createTextNode(str(self.ui.listWidget_Speakers.item(i).z))
				c3_el.appendChild(c3_txt)
				coord_el.appendChild(c3_el)
				
				spkr_el.appendChild(coord_el)

				root_el.appendChild(spkr_el)
			file_text=str(doc.toString())
			file.writeData(file_text)
			file.close()
			self.speakers_dirty=False


	def Load_Speaker(self):
		count=self.ui.listWidget_Speakers.count()
		reply=QtGui.QMessageBox.Yes
		if(count>0 and self.speakers_dirty):
			reply=QtGui.QMessageBox.question(self,"Action Confirmation","Are you sure you want to load a speakers file? Current speakers will be lost.",QtGui.QMessageBox.Yes|QtGui.QMessageBox.Default,QtGui.QMessageBox.No|QtGui.QMessageBox.Escape)
		if(reply == QtGui.QMessageBox.Yes):
			if self.speaker_fname is None:
				self.speaker_fname="."
			self.speaker_fname=unicode(QtGui.QFileDialog.getOpenFileName(self,"Speakers - Save Speakers", self.speaker_fname, "Speaker Files (*.spkr)"))
			self.Load_Speaker_File(self.speaker_fname)
			
	def Load_Speaker_File(self,fname=None):
		if fname is not None:
			self.speaker_fname=fname
		if len(self.speaker_fname)!=0:
			if "." not in self.speaker_fname:
				self.speaker_fname+=".spkr"
			file=QtCore.QFile(self.speaker_fname)
			if (not file.open(QtCore.QIODevice.ReadOnly | QtCore.QIODevice.Text)):
				QtGui.QMessageBox.warning(self, 'Application', QtCore.QString('Cannot read file %1:\n%2.').arg(fname).arg(file.errorString()))
				return False
			else:
				doc = QtXml.QDomDocument("SpeakerML");
				if(not doc.setContent(file)):
					file.close()
					QtGui.QMessageBox.warning(self,"Error","Could not parse xml file.")
				file.close()
				root = doc.documentElement();
				if(root.tagName()!="speaker_list"):
					QtGui.QMessageBox.warning(self,"Error","Could not parse xml file. Root Element must be <speaker_list/>.")
				else:
					self.ui.listWidget_Speakers.clear()
					"""node = root.firstChild()
					while(not node.isNull()):
						elem = node.toElement()
						if(not elem.isNull()):
							if(elem.tagName()=="speaker_location"):
								try:
									xpos=float(elem.attribute( "x_pos", "" ))
									ypos=float(elem.attribute( "y_pos", "" ))
									zpos=float(elem.attribute( "z_pos", "" ))
									#print "X:", xpos, "Y:", ypos, "Z:", zpos
									point=Point3D(xpos,ypos,zpos)
									self.ui.listWidget_Speakers.addItem(point)
									count=self.ui.listWidget_Speakers.count()
									itemslist=[]
									for i in range(0,count):
										itemslist.append(self.ui.listWidget_Speakers.item(i))
									self.ui.graphicsView.updateSpeakers(itemslist)
								except ValueError:
									QtGui.QMessageBox.warning(self,"Error","Invalid coordinates entered, no point added.")
						node = node.nextSibling()
					self.speakers_dirty=False
					self.ui.listWidget_Listeners.clear()"""
					node = root.firstChild()
					while(not node.isNull()):
						if(node.toElement().tagName()=="speaker_location"):
							try:
								coord_type=node.firstChild()
							except:
								QtGui.QMessageBox.warning(self,"Error","Could not parse xml file. Problem parsing %s."%(coord_type.toElement().tagName()))
								break
							if(not coord_type.isNull()):
								if(str(coord_type.toElement().attribute("type",""))=="cartesian"):
									child=coord_type.firstChild()
									xpos=None
									ypos=None
									zpos=None
									while(not child.isNull()):
										if(child.toElement().tagName()=="c1"):
											try:
												xpos=float(child.firstChild().toText().data())
											except:
												QtGui.QMessageBox.warning(self,"Error","Could not parse xml file. Problem parsing %s." %(child.toElement().tagName()))
												break
										elif(child.toElement().tagName()=="c2"):
											try:
												ypos=float(child.firstChild().toText().data())
											except:
												QtGui.QMessageBox.warning(self,"Error","Could not parse xml file. Problem parsing %s."%(child.toElement().tagName()))
												break
										elif(child.toElement().tagName()=="c3"):
											try:
												zpos=float(child.firstChild().toText().data())
											except:
												QtGui.QMessageBox.warning(self,"Error","Could not parse xml file. Problem parsing %s."%(child.toElement().tagName()))
												break
										else:
											QtGui.QMessageBox.warning(self,"Error","Could not parse xml file. Problem parsing %s. Unknown or incorrect tag."%(child.toElement().tagName()))
											break
										#print "X:", xpos, "Y:", ypos, "Z:", zpos
										if(xpos is not None and ypos is not None and zpos is not None):
											point=Point3D(xpos,ypos,zpos)
											self.ui.listWidget_Speakers.addItem(point)
											count=self.ui.listWidget_Speakers.count()
										child=child.nextSibling()
								else:
									QtGui.QMessageBox.warning(self,"Error","Could not parse xml file. Only cartesian points supported."%(node.toElement().tagName()))
						else:
							QtGui.QMessageBox.warning(self,"Error","Could not parse xml file. Problem parsing %s. Unknown or incorrect tag."%(child.toElement().tagName()))
							break
						node=node.nextSibling()
					self.ui.listWidget_Speakers.addItem(point)
					count=self.ui.listWidget_Speakers.count()
					itemslist=[]
					for i in range(0,count):
						itemslist.append(self.ui.listWidget_Speakers.item(i))
					self.ui.graphicsView.updateSpeakers(itemslist)
					self.speakers_dirty=False
					self.session_dirty=True

	def markers_updated(self,markers=None):
		self.markers_list=markers
		
	def marker_deleted(self,marker):
		pass
	
	def attach_marker_to_point(self,marker,point):
		#check to see if this marker is already attached to a point
		if(marker in self.point_to_markers_dict.values()):
			cur_point=[k for k, v in self.point_to_markers_dict.iteritems() if v == marker][0]
			if(cur_point==point):
				pass
			else:
				reply = QtGui.QMessageBox.Yes
				if(self.speakers_dirty or self.listeners_dirty or self.path_dirty or self.environment_dirty):
					reply=QtGui.QMessageBox.question(self,"Marker In Use","Marker is currently attached to another point. Would you like to disconnec the marker from the current point and re-attach it to this point?", QtGui.QMessageBox.Yes|QtGui.QMessageBox.Default,QtGui.QMessageBox.No)
				if(reply == QtGui.QMessageBox.Yes):
					self.detach_marker_from_point(marker,cur_point)
					self.point_to_markers_dict[point]=marker
					print self.point_to_markers_dict
				else:
					pass
		else:
			self.point_to_markers_dict[point]=marker
			print self.point_to_markers_dict

	def detach_marker_from_point(self,marker,point=None):
		"""remove marker from point_to_markers_dict"""
		if(point is not None):
			del self.point_to_markers_dict[point]
		else:
			point=[k for k, v in self.point_to_markers_dict.iteritems() if v == marker][0]
			del self.point_to_markers_dict[point]

	def marker_selected(self,marker):
		point=self.point_manager.point_from_marker(marker)
		#if(point is not None):
		self.ui.listWidget_Path.setCurrentItem(point)
		self.audio_dockWidget.wave.markers_list.highlight_selected_quiet(marker)

	def ready_path_tracer(self):
		count=self.ui.listWidget_Path.count()
		points_list=[]
		for i in range(0,count):
			points_list.append(self.ui.listWidget_Path.item(i))
		print "****&&&&&****",points_list,self.point_manager.dict
		self.ui.graphicsView.path_tracer.update_render(points_list,self.point_manager.dict)


class GLWidget(QtOpenGL.QGLWidget):
		"""OpenGl Widget designed to display a render environment with a sound path."""

		def __init__(self, parent=None):
				super(GLWidget, self).__init__(parent)
				glutInit(sys.argv)
				self.object = 0
				self.xRot = 0
				self.yRot = 0
				self.zRot = 0
				self.zoom=-10.0
				self.lastPos = QtCore.QPoint()
				self.trolltechGreen = QtGui.QColor.fromCmykF(0.40, 0.0, 1.0, 0.0)
				self.trolltechPurple = QtGui.QColor.fromCmykF(0.39, 0.39, 0.0, 0.0)
				self.room_box=GLRoom(6,2.5,8)
				self.speakers=[]
				self.speaker_renderer=SpeakerRenderer()
				self.path=[]
				self.path_renderer=PathRenderer()
				self.listeners=[]
				self.path_tracer=GLPathTracer()

		def minimumSizeHint(self):
				return QtCore.QSize(50, 50)

		def sizeHint(self):
				return QtCore.QSize(400, 400)

		def setXRotation(self, angle):
				angle = self.normalizeAngle(angle)
				if angle != self.xRot:
						self.xRot = angle
						#self.xRotationChanged.emit(angle)
						self.updateGL()

		def setYRotation(self, angle):
				angle = self.normalizeAngle(angle)
				if angle != self.yRot:
						self.yRot = angle
						#self.yRotationChanged.emit(angle)
						self.updateGL()

		def setZRotation(self, angle):
				angle = self.normalizeAngle(angle)
				if angle != self.zRot:
						self.zRot = angle
						#self.zRotationChanged.emit(angle)
						self.updateGL()

		def setZoom(self,move):
			if(move != 0.0):
				self.zoom=self.zoom+move
				self.updateGL()

		def updateRoom(self,width=6.0,height=2.5,depth=8.0):
			"""room coordinates"""
			self.room_box.resize(width,height,depth)
			self.updateGL()

		def initializeGL(self):
				self.qglClearColor(self.trolltechPurple.dark())
				#GL.glShadeModel(GL.GL_FLAT)
				#GL.glEnable(GL.GL_DEPTH_TEST)
				#GL.glEnable(GL.GL_CULL_FACE)
				GL.glShadeModel(GL_SMOOTH)
				GL.glClearColor(0.0, 0.0, 0.0, 0.0)
				GL.glClearDepth(1.0)
				GL.glEnable(GL_DEPTH_TEST)
				GL.glEnable (GL_BLEND); glBlendFunc (GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
				GL.glDepthFunc(GL_LEQUAL)
				GL.glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)
				gluPerspective(45, 1.0*self.width()/self.height(), 0.1, 150.0)

		def updateSpeakers(self,speakers):
				self.speakers=speakers
				self.updateGL()
				
		def updatePath(self,path):
				self.path=path
				self.updateGL()
				
		
		def updateTacer(self,t):
			self.path_tracer.update(t)
			self.updateGL()
		
		def updateListeners(self,listeners):
				self.listeners=listeners
				self.updateGL()
				
		def paintGL(self):
				GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
				GL.glLoadIdentity()
				GL.glTranslated(0.0, 0.0, self.zoom)
				GL.glRotated(self.xRot / 16.0, 1.0, 0.0, 0.0)
				GL.glRotated(self.yRot / 16.0, 0.0, 1.0, 0.0)
				GL.glRotated(self.zRot / 16.0, 0.0, 0.0, 1.0)
				self.draw()

		def resizeGL(self, width=1.0, height=1.0):
				#self.width=width
				#self.height=height
				print width,height
				print self.width(),self.height()
				width = self.width()
				height = self.height()
				side = min(width, height)
				if side < 0:
						return
				#GL.glViewport((width - side) / 2, (height - side) / 2, side, side)
				GL.glViewport(0, 0, width, height)

				GL.glMatrixMode(GL.GL_PROJECTION)
				GL.glLoadIdentity()
				#GL.glOrtho(-0.5, +0.5, +0.5, -0.5, 4.0, 15.0)
				gluPerspective(60, 1.0*self.width()/self.height(), 1.1, 150.0)
				GL.glMatrixMode(GL.GL_MODELVIEW)
				#GL.glLoadIdentity()
	
		def mousePressEvent(self, event):
				self.lastPos = QtCore.QPoint(event.pos())

		def mouseMoveEvent(self, event):
				dx = event.x() - self.lastPos.x()
				dy = event.y() - self.lastPos.y()
				if event.buttons() & QtCore.Qt.LeftButton:
						self.setXRotation(self.xRot + 8 * dy)
						self.setYRotation(self.yRot + 8 * dx)
				elif event.buttons() & QtCore.Qt.RightButton:
						self.setZoom(dy)
				self.lastPos = QtCore.QPoint(event.pos())

		def mouseReleaseEvent(self, event):
			self.updateGL()

		def normalizeAngle(self, angle):
				while angle < 0:
						angle += 360 * 16
				while angle > 360 * 16:
						angle -= 360 * 16
				return angle

		def draw(self):
				glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);	
				glTranslatef(0.0,0.0,-3.0)
				glPushMatrix()
				self.room_box.draw()
				glPopMatrix()
				"""speakers=[]
				speakers.append(Point3D(0.2,-0.5,1.2))
				speakers.append(Point3D(0.2,0.2,1.2))
				speakers.append(Point3D(0.0,0.0,1.0))
				i=0;
				self.speakers=[]"""
				self.speaker_renderer.draw(self.speakers)
				glColor3f(1.0,0.0,0.0)
				self.path_renderer.draw(self.path)
				glColor4f(0.7,0.7,0.7,.7)
				for l in self.listeners:
					current_listener=GLListener(1.75)
					glPushMatrix()
					glTranslated(l.x,l.y,l.z)
					current_listener.draw()
					glPopMatrix()
				"""for speaker in self.speakers:
					current_speaker=GLSpeaker()
					glColor3f(0.0,1.0,0.0)
					glPushMatrix()
					glTranslated(speaker.x,speaker.y,speaker.z)
					current_speaker.draw()
					glPopMatrix()"""
				self.path_tracer.draw()

class GLRoom():
	"""Creates a 3d wireframe box used to represent the dimensions of a room."""
	def __init__(self,xdim,ydim,zdim,):
		try:
			self.xdimension=float(xdim)
			self.ydimension=float(ydim)
			self.zdimension=float(zdim)
		except:
			QtGui.QMessageBox.warning(self, 'Room Error', QtCore.QString('Can not initialize room.'))
			
	def resize(self,xdim,ydim,zdim,):
		try:
			self.xdimension=float(xdim)
			self.ydimension=float(ydim)
			self.zdimension=float(zdim)
		except:
			QtGui.QMessageBox.warning(self, 'Room Error', QtCore.QString('Can not resize room.'))
	def draw(self):
		glPushMatrix()
		glColor3f(1.0,1.0,0.0)	
		glScaled( GLdouble(self.xdimension), GLdouble(self.ydimension), GLdouble(self.zdimension))
		glutWireCube( GLdouble(1.0))
		glPopMatrix()

class GLSpeaker():
	"""Creates a recatangular volume representing a speaker."""
	def __init__(self,xdim=.1,ydim=.15,zdim=.1,):
		self.xdimension=xdim
		self.ydimension=ydim
		self.zdimension=zdim
	def resize(self,xdim,ydim,zdim,):
		self.xdimension=xdim
		self.ydimension=ydim
		self.zdimension=zdim
	def draw(self):
		#glPushMatrix()
		#glColor3f(0.0,0.0,1.0)
		glScaled(GLdouble(self.xdimension), GLdouble(self.ydimension), GLdouble(self.zdimension))
		glutSolidCube(GLdouble(1.0))
		#glPopMatrix()

class SpeakerRenderer():
	"""Used to render a list of speakers at desired locations. Posibly alllowing one of the speaker to be highlighted"""
	def __init__(self,xdim=.1,ydim=.15,zdim=.1,):
		self.xdimension=xdim
		self.ydimension=ydim
		self.zdimension=zdim
		self.selected=-1
	
	def set_selected(self,selected=-1):
		self.selected=selected

	def resize(self,xdim,ydim,zdim,):
		self.xdimension=xdim
		self.ydimension=ydim
		self.zdimension=zdim
	def draw(self,speakers):
		i=0
		for speaker in speakers:
			if(self.selected==i):
				glColor4f(0.0,1.0,1.0,2.0)
				current_speaker=GLSpeaker(self.xdimension*2.0,self.ydimension*2.0,self.zdimension*2.0)
			else:
				glColor4f(0.4,0.4,1.0,0.5)
				current_speaker=GLSpeaker(self.xdimension,self.ydimension,self.zdimension)
			glPushMatrix()
			glTranslated(speaker.x,speaker.y,speaker.z)
			current_speaker.draw()
			glPopMatrix()
			i=i+1

class PathRenderer():
	"""Renders path points as a series of color coded line strips."""
	def __init__(self,mode=GL_LINE_STRIP,point_size=0.05):
		self.mode=mode
		self.startcolor=[1.0,0.0,0.0]
		self.endcolor=[0.0,1.0,0.0]
		self.point_size=point_size
		self.selected=-1

	def set_selected(self,sel=-1):
		self.selected=sel

	def draw(self,points=[]):
		glBegin(self.mode)
		if(len(points)>0):
			color_step=1.0/len(points)
		else:
			color_step=0.0
		color_val=0.0
		for point in points:
			glColor3f(self.startcolor[0]*(1.0-color_val)+self.endcolor[0]*color_val,self.startcolor[1]*(1.0-color_val)+self.endcolor[1]*color_val,self.startcolor[2]*(1.0-color_val)+self.endcolor[2]*color_val,)
			glVertex3d(point.x,point.y,point.z)
			color_val+=color_step
		glEnd()
		#glBegin(GL_POINTS)
		if(len(points)>0):
			color_step=1.0/len(points)
		else:
			color_step=0.0
		color_val=0.0
		i=0
		for point in points:
			glColor3f(self.startcolor[0]*(1.0-color_val)+self.endcolor[0]*color_val,self.startcolor[1]*(1.0-color_val)+self.endcolor[1]*color_val,self.startcolor[2]*(1.0-color_val)+self.endcolor[2]*color_val,)
			#glVertex3d(point.x,point.y,point.z)
			glPushMatrix()
			glTranslated(point.x,point.y,point.z)
			if(self.selected==i):
				glutSolidSphere(self.point_size*2.0,10,10)
			else:
				glutSolidSphere(self.point_size,10,10)
			glPopMatrix()
			i=i+1
			color_val+=color_step
		#glEnd()

class GLListener():
	"""Draws a doll for use as a listener in audio environment."""
	def __init__(self,height=1.75):
		self.height=height
	def draw(self):
		glPushMatrix()
		glTranslated(0,-self.height*.3,0)
		#head
		glPushMatrix()
		glTranslated(0,self.height*.35,0)
		glutSolidSphere(self.height/12.0,10,10)
		glPopMatrix()
		#torso
		glPushMatrix()
		glScaled(.25,0.6,.25)
		glutSolidSphere(self.height/2.0,10,10)
		glPopMatrix()
		#right leg
		glPushMatrix()
		glTranslated(self.height*.1,self.height*-.3,0)
		glRotated(25,0,0,1)
		glScaled(self.height*.055,self.height*.2,self.height*.055)
		glutSolidSphere(self.height/2.0,10,10)
		glPopMatrix()
		#left leg
		glPushMatrix()
		glTranslated(self.height*-.1,self.height*-.3,0)
		glRotated(-25,0,0,1)
		glScaled(self.height*.06,self.height*.2,self.height*.06)
		glutSolidSphere(self.height/2.0,10,10)
		glPopMatrix()
		#right arm
		glPushMatrix()
		glTranslated(self.height*.1,self.height*.2,0)
		glRotated(65,0,0,1)
		glScaled(self.height*.055,self.height*.2,self.height*.055)
		glutSolidSphere(self.height/2.0,10,10)
		glPopMatrix()
		#left arm
		glPushMatrix()
		glTranslated(self.height*-.1,self.height*.2,0)
		glRotated(-65,0,0,1)
		glScaled(self.height*.06,self.height*.2,self.height*.06)
		glutSolidSphere(self.height/2.0,10,10)
		glPopMatrix()	
		glPopMatrix()

class GLPathTracer(QtCore.QObject):
	"""Follow an audio path as it plays through the 2d rendering space"""
	def __init__(self,parent=None):
		QtCore.QObject.__init__(self,parent)
		self.render_points_list=[]
		self.render_points_dict={}
		self.render_times_dict=None
		self.render_times_list=[]
		self.path_valid=False
		self.pos=None
		self.point_size=0.2

	def update_render(self,points_list,points_dict):
		"""takes an ordered points list and a dict of points to arrival times"""
		self.render_points_list=points_list
		self.render_points_dict=points_dict
		#create a list of render times in the same order as the points to be rendered
		if(len(self.render_points_list)>0):
			for point in self.render_points_list:
				if(point in self.render_points_dict.keys()):
					self.render_times_list.append(self.render_points_dict[point])
			#if we have the same number of points and times we have a valid path
			if(len(self.render_points_list) == len(self.render_times_list)):
				self.path_valid=self.validate_render_times()
			self.generate_path_plan()

	def validate_render_times(self):
		"""for a render time to be valid the times must be monotonically increasing"""
		cur_time=self.render_times_list[0]
		valid=True
		for time in self.render_times_list:
			if(cur_time>time):
				valid = False
				break
			else:
				cur_time=time
		return valid

	def generate_path_plan(self):
		"""creates a path for tracer using a list to point and times"""
		if(self.path_valid):
			#make a mapping of times in chronological order to paths
			self.render_times_dict={}
			for time in self.render_times_list:
				if(time in self.render_points_dict.values()):
					point=[k for k, v in self.render_points_dict.iteritems() if v == time][0]
				self.render_times_dict[time]=point
		else:
			self.render_times_dict=None
	
	def get_pos(self, t):
		"""takes time in seconds and converts it to location on path, returns None if no valid position is found"""
		pos=None
		if(self.path_valid):
			found_in_path=False
			start_time=self.render_times_list[0]
			end_time=self.render_times_list[0]
			#print "start_time:",start_time,"end_time:",end_time
			#if the t is within the range of possible times, find the times before and after t
			if(start_time.time <= t <=self.render_times_list[-1].time):
				for time in self.render_times_list:
					start_time=end_time
					end_time=time
					if(end_time.time >= t):
						found_in_path=True
						break
				#print "start_time:",start_time,"end_time:",end_time
			if(found_in_path):
				try:
					start_point=self.render_times_dict[start_time]
					end_point=self.render_times_dict[end_time]
				except KeyError:
					print "****************", self.render_times_dict
					raise KeyError
				t_val=float(t-start_time.time)/float(end_time.time-start_time.time)
				x_val=start_point.x*(1-t_val)+end_point.x*(t_val)
				y_val=start_point.y*(1-t_val)+end_point.y*(t_val)
				z_val=start_point.z*(1-t_val)+end_point.z*(t_val)
				pos=Point3D(x_val,y_val,z_val)
		#print "Position:",pos
		return pos
	
	def update(self,time):
		self.pos=self.get_pos(time)

	def draw(self):
		if(self.path_valid and self.pos is not None):
			glPushMatrix()
			glColor3f(1.0,0.0,1.0)
			glTranslated(self.pos.x,self.pos.y,self.pos.z)
			glutSolidSphere(self.point_size,10,10)
			glPopMatrix()
			

def start():
	app = QtGui.QApplication(sys.argv)
	myapp = PathCreator()
	myapp.show()
	sys.exit(app.exec_())


if __name__ == "__main__":
	app = QtGui.QApplication(sys.argv)
	myapp = PathCreator()
	myapp.show()
	sys.exit(app.exec_())
