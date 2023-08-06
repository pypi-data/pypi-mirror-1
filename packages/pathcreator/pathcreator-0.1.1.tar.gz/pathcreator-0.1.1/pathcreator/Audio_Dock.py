from Audio_Form import Ui_AudioForm
from PyQt4 import QtCore, QtGui
import pygame
from pygame import mixer, sndarray
import time

TENTH_SECOND=100


class Audio_DockWidget(QtGui.QDockWidget):
	"""Dock Widget for used to control playback of audio and marker placment"""
	def __init__(self,file_name=None,set_points=[],parent=None):
		QtGui.QDockWidget.__init__(self,parent)
		#init ui
		self.ui=Ui_AudioForm()
		self.ui.setupUi(self)
		#self.scene=QtGui.QGraphicsScene(self)
		#self.scene.setSceneRect(0,0,self.ui.graphicsView_Audio.width(),self.ui.graphicsView_Audio.height())
		#self.scene.setSceneRect(0,0,1000,50)
		#wave is now a scene object
		self.audio_data=None
		self.wave=Wave_Viewer(0,0,1000,50,self.audio_data,self.ui.graphicsView_Audio)
		self.ui.graphicsView_Audio.setScene(self.wave)
		self.ui.pushButton_Pause.setCheckable(True)
		self.ui.pushButton_Play.setCheckable(True)
		self.ui.pushButton_Set_Point.setCheckable(True)
		#self.ui.pushButton_Mark_Point.setCheckable(True)
		#self.ui.pushButton_Zoom_In.setCheckable(True)
		#self.ui.pushButton_Zoom_Out.setCheckable(True)
		#init audio mixer
		self.disable_audio_buttons(open_file=True)
		mixer.init(11025)
		self.paused=False
		self.sound=None
		self.file_name=file_name
		self.play_timer=None
		self.zoom_factor=10 #10 percent zoom
		if(file_name is not None):
			self.load_sound(file_name)
		self.init_connections()

	def disable_audio_buttons(self,pause=False,play=False,stop=False,set_point=False,mark_point=False,zoom_in=False,zoom_out=False,open_file=False):
		self.ui.pushButton_Pause.setEnabled(pause)
		self.ui.pushButton_Play.setEnabled(play)
		self.ui.pushButton_Stop.setEnabled(stop)
		self.ui.pushButton_Set_Point.setEnabled(set_point)
		self.ui.pushButton_Mark_Point.setEnabled(mark_point)
		self.ui.pushButton_Zoom_In.setEnabled(zoom_in)
		self.ui.pushButton_Zoom_Out.setEnabled(zoom_out)
		self.ui.pushButton_Open_File.setEnabled(open_file)

	def enable_audio_buttons(self,pause=True,play=True,stop=True,set_point=True,mark_point=True,zoom_in=True,zoom_out=True,open_file=True):
		self.ui.pushButton_Pause.setEnabled(pause)
		self.ui.pushButton_Play.setEnabled(play)
		self.ui.pushButton_Stop.setEnabled(stop)
		self.ui.pushButton_Set_Point.setEnabled(set_point)
		self.ui.pushButton_Mark_Point.setEnabled(mark_point)
		self.ui.pushButton_Zoom_In.setEnabled(zoom_in)
		self.ui.pushButton_Zoom_Out.setEnabled(zoom_out)
		self.ui.pushButton_Open_File.setEnabled(open_file)

	def init_connections(self):
		"""initialize signal and slot connections"""
		self.connect(self.ui.pushButton_Open_File,QtCore.SIGNAL('clicked()'), self.open_file)
		self.connect(self.ui.pushButton_Play,QtCore.SIGNAL('clicked()'), self.play)
		self.connect(self.ui.pushButton_Pause,QtCore.SIGNAL('clicked()'), self.pause)
		self.connect(self.ui.pushButton_Stop,QtCore.SIGNAL('clicked()'), self.stop)
		self.connect(self.ui.pushButton_Mark_Point,QtCore.SIGNAL('clicked()'), self.mark_point)
		self.connect(self.ui.pushButton_Set_Point,QtCore.SIGNAL('clicked()'), self.set_point)
		self.connect(self.ui.pushButton_Zoom_In,QtCore.SIGNAL('clicked()'), self.zoom_in)
		self.connect(self.ui.pushButton_Zoom_Out,QtCore.SIGNAL('clicked()'), self.zoom_out)
		self.connect(self.ui.graphicsView_Audio,QtCore.SIGNAL('resizeEvent(QEvent)'),self.catch_resize)
	
	def catch_resize(self, event):
		self.wave.catch_resize()
	
	def open_file(self,file_name=None):
			if(file_name is not None):
				self.file_name=file_name
			if self.file_name is None:
					self.file_name="."
			self.file_name=unicode(QtGui.QFileDialog.getOpenFileName(self,"Audio - Load Wave", self.file_name, "Wave Files (*.wav)"))
			if self.file_name is not None:
				if(len(self.file_name) > 0):
					self.load_sound(self.file_name)
					self.enable_audio_buttons()
				else:
					self.file_name=None
		
	def load_sound(self,file_name=None):
		if(file_name is not None):
			self.file_name=file_name
			self.sound = mixer.Sound(file_name)
			#length of audio in seconds
			self.audio_length=self.sound.get_length()
			self.wave.set_wiper_length(self.audio_length)
			self.set_end_time()
			self.audio_data=sndarray.array(self.sound)
			self.wave.update_data(self.audio_data)
			self.update_file_name()
	
	def convert_time(self,time_in_sec=0):
		stime=time.strftime('%H:%M:%S', time.gmtime(time_in_sec))
		msec=int((time_in_sec-int(time_in_sec))*10)
		stime=stime+':'+str(msec)
		return stime#time.strftime('%H:%M:%S', time.gmtime(time_in_sec))
		
	def set_end_time(self):
		time=self.convert_time(self.audio_length)
		self.ui.label_end_time.setText(time)
	
	def set_current_time(self):
		#print dir(self.sound)
		if(pygame.mixer.get_busy()):#keep updating while audio is still playing
			self.play_time=self.play_time+TENTH_SECOND/1000.0
			time=self.convert_time(self.play_time)
			self.ui.label_current_time.setText(time)
			self.wave.update_wiper(self.play_time,self.audio_length)
			self.emit(QtCore.SIGNAL("time_updated"),self.play_time)
		else:
			self.emit(QtCore.SIGNAL("time_updated"),None)
			self.play_timer.stop()
			self.stop()
	
	def update_file_name(self):
		self.ui.lineEdit_Filename.setText(str(self.file_name))
	
	def play(self):
		if(self.sound is not None):
			self.wave.set_wiper_length(self.audio_length)
			self.ui.pushButton_Pause.setChecked(False)
			self.paused=False
			if(self.play_timer is not None):
				self.play_timer.stop()
				self.disconnect(self.play_timer,QtCore.SIGNAL("timeout()"),self.set_current_time)
			self.play_timer=QtCore.QTimer(self)
			self.play_time=0.0
			self.connect(self.play_timer,QtCore.SIGNAL("timeout()"),self.set_current_time)
			#let other components know audio is being played
			self.emit(QtCore.SIGNAL("play_started"),None)
			self.sound.stop()
			self.sound.play()
			self.play_timer.start(TENTH_SECOND)
		else:
			QtGui.QMessageBox.warning(self, 'Audio - Pause', QtCore.QString('No file present'))
			self.ui.pushButton_Play.setChecked(False)
	
	def pause(self):
		if(self.sound is not None):
			if(not self.paused):
				mixer.pause()
				self.play_timer.stop()
				self.paused=True
			else:
				mixer.unpause()
				self.play_timer.start(TENTH_SECOND)
				self.paused=False
			#self.sound.pause()

	def mark_point(self):
		if(self.sound is not None):
			self.wave.add_marker()

	def stop(self):
		if(self.sound is not None):
			self.sound.stop()
			self.play_timer.stop()
			self.wave.update_wiper(0,self.audio_length)
			self.ui.pushButton_Play.setChecked(False)
			self.ui.pushButton_Pause.setChecked(False)
			self.paused=False

	def set_point(self):
		if(self.sound is not None):
			if(self.ui.pushButton_Set_Point.isChecked()):
				self.wave.set_point_mode=True
				self.disable_audio_buttons(set_point=True)
			else:
				self.enable_audio_buttons()
				self.wave.set_point_mode=False
	
	def zoom_in(self):
		if(self.sound is not None):
			factor=1+self.zoom_factor/100.0
			matrix=self.ui.graphicsView_Audio.matrix()
			matrix.scale(factor,1.0)
			self.ui.graphicsView_Audio.setMatrix(matrix)
	
	def zoom_out(self):
		if(self.sound is not None):
			factor=1-self.zoom_factor/100.0
			matrix=self.ui.graphicsView_Audio.matrix()
			matrix.scale(factor,1.0)
			self.ui.graphicsView_Audio.setMatrix(matrix)

class Wave_Viewer(QtGui.QGraphicsScene):
	def __init__(self, x, y, width, height, scene=None, render_data=[], view=None, parent = None):
		QtGui.QGraphicsScene.__init__(self, x,y,width,height)
		self.render_data=render_data
		self.lines=None
		self.samples=1000
		self.view=view
		self.width=1000
		self.height=50
		self.x_delta=.1
		self.wiper=None
		self.wiper_pos=0;
		self.draw_x_axis()
		self.make_wiper(0)
		self.markers_list=Marker_List(self)
		self.mouse_pressed=False
		self.set_point_mode=False

	def update_data(self,render_data=[]):
		self.render_data=render_data
		self.lines=[]
		#self.make_lines()
		self.make_path()
	
	def catch_resize(self):
		self.width=self.view.width()#1000
		self.height=self.view.height()#50
		print "catch_resize",self.width,self.height
		self.scale(width/height)
	
	def draw_x_axis(self):
		pen=QtGui.QPen(QtGui.QColor(255,0,0,100))
		#pen.setColor(QtGui.QColor(1.0,0,0))
		self.x_axis=QtGui.QGraphicsLineItem()
		self.x_axis.setPen(pen)
		self.x_axis.setLine(0,self.height/2.0,self.width,self.height/2.0)
		self.addItem(self.x_axis)
		self.circle=QtGui.QGraphicsEllipseItem()
		self.circle.setRect(self.width/2.0-25,self.height/2.0-25,50,50)
		self.addItem(self.circle)

	def make_lines(self):
		start_x=0
		#self.x_delta=self.view.width()/float(self.width)
		self.x_delta=1
		step= int(len(self.render_data)/self.samples)
		max_val=0.0
		for i in range(0,len(self.render_data),step):
			if(self.render_data[i][1]>max_val):
				max_val=float(self.render_data[i][1])
		#max_val=max_val/10.0
		print "max",max_val
		ratio=(self.height/2.0)*1.0/max_val
		for i in range(0,len(self.render_data)-step,step):
			line=QtGui.QGraphicsLineItem()
			line.setLine(start_x,self.height/2+-1.0*float(self.render_data[i][1])*ratio,start_x+self.x_delta,self.height/2+-1.0*float(self.render_data[i+step][1])*ratio)
			start_x=start_x+self.x_delta
			self.addItem(line)
			self.lines.append(line)
		print "rendered"

	def make_path(self):
		start_x=0
		#self.x_delta=self.view.width()/float(self.width)
		self.x_delta=1
		step= int(len(self.render_data)/self.samples)
		max_val=0.0
		for i in range(0,len(self.render_data),step):
			if(self.render_data[i][1]>max_val):
				max_val=float(self.render_data[i][1])
		#max_val=max_val/10.0
		print "max",max_val
		ratio=(self.height/2.0)*1.0/max_val
		self.path=QtGui.QPainterPath(QtCore.QPointF(start_x,self.height/2+-1.0*float(self.render_data[i][1])*ratio))
		for i in range(0,len(self.render_data)-step,step):
			self.path.lineTo(start_x+self.x_delta,self.height/2+-1.0*float(self.render_data[i+step][1])*ratio)
			start_x=start_x+self.x_delta
		self.path_item=QtGui.QGraphicsPathItem(self.path)
		self.path_item.setZValue(1)
		self.addItem(self.path_item)
		print "rendered"

	def make_wiper(self,audio_length=0):
		if(self.wiper is None):
			#self.wiper=audio_wiper(0,0,10,50,self,self.scene,audio_length,self.width)
			self.audio_length=audio_length
			self.wiper=Audio_Wiper(0,0,10,50,self,self,audio_length,self.width)
			self.addItem(self.wiper)
			self.wiper.update_pos_by_time(0,audio_length)

	def set_wiper_length(self,audio_length):
		self.audio_length=audio_length
		self.wiper.set_audio_length(audio_length)

	def update_wiper(self,time=0,length=0):
		if(self.wiper is not None):
			self.audio_length=length
			self.wiper.update_pos_by_time(time,length)
	
	def update_pos_by_time(self,time=0,length=0):
		self.audio_length=length
		self.wiper.update_pos_by_time(time,length)
		
	def mousePressEvent(self,event):
		#if we're not in set point mode we handle use case for 
		if(not self.set_point_mode):
			self.mouse_pressed_point=event.scenePos()
			self.mouse_pressed=True
			print event.scenePos().x(),event.scenePos().y()
			print event.button()
			item=self.itemAt(self.mouse_pressed_point)
			if(item is not None):
				print item
				self.mouse_pressed_item=item
				if(isinstance(item,Audio_Marker)):
					self.markers_list.highlight_selected(item)
			else:
				self.mouse_pressed_item=None
		else:
			self.add_marker(event.scenePos().x())
	
	def mouseReleaseEvent(self,event):
		if(self.mouse_pressed):
			self.mouse_pressed=False
			self.mouse_pressed_item=None
			self.mouse_pressed_point=None

	def mouseMoveEvent(self,event):
		if(self.mouse_pressed):
			if(isinstance(self.mouse_pressed_item,Audio_Wiper)):
				#if we are moving while mouse is pressed on an object we move it
				pos_diff=event.scenePos().x()-self.mouse_pressed_point.x()
				self.mouse_pressed_point=event.scenePos()
				if(not self.mouse_pressed_item.move(pos_diff)):
					#we've tried to move off the scene, disable movement
					self.mouse_pressed=False
				mtime = time.strftime('%H:%M:%S', time.gmtime(self.mouse_pressed_item.time))
				print mtime	

	def mouseDoubleClickEvent(self, event):
		item=self.itemAt(event.scenePos())
		#if we've clicked on a marker
		if(isinstance(item,Audio_Marker)):
			if(event.button()==1):#right click
				item.edit_point()
			elif(event.button()==2):
				reply=QtGui.QMessageBox.No
				reply=QtGui.QMessageBox.question(None,"Delete Marker","Are you sure you want to delete this marker.", QtGui.QMessageBox.Yes|QtGui.QMessageBox.Default,QtGui.QMessageBox.No|QtGui.QMessageBox.Escape)
				if(reply==QtGui.QMessageBox.Yes):
					self.markers_list.remove_marker(item)
			else:
				pass
			

	def add_marker(self,pos=None):
		#if we don't recieve a position for the marker use the position of the wiper
		if(pos is None):
			marker=Audio_Marker(0,0,10,50,self,self,self.audio_length,self.width)
			marker.move(self.wiper.pos)
			self.markers_list.add_marker(marker)
		else:
			marker=Audio_Marker(0,0,10,50,self,self,self.audio_length,self.width)
			marker.move(pos)
			self.markers_list.add_marker(marker)
			

class Audio_Wiper(QtGui.QGraphicsRectItem):
	def __init__ (self, x=0, y=0, w=10, h=50, parent = None, scene = None,audio_length=0,scene_width=0):
		QtGui.QGraphicsRectItem.__init__(self,x,y,h,w)
		self.scene=scene
		#time in seconds to nearest tenth of a second
		self.time=0
		self.audio_length=audio_length
		self.scene_width=scene_width
		self.pos=0
		self.x=x
		self.y=y
		self.w=w
		self.h=h
		self.setZValue(4)
		#self.rect=QtGui.QGraphicsRectItem(self.x+self.pos,self.y,self.h,self.w)
		self.setPen(QtGui.QPen(QtGui.QColor(0,255,0)))
		self.setBrush(QtGui.QBrush(QtGui.QColor(0,255,0,127)))
	
	def set_audio_length(self,time=0):
		self.audio_length=time
	
	def set_scene_width(self,scene_width=0):
		self.scene_width=scene_width
	
	def set_time(self,time=0):
		self.time=time

	def update_pos_by_time(self,time=0,audio_length=None):
		self.time=time
		if(audio_length is not None):
			self.audio_length=audio_length
		if(self.audio_length>0):
			self.pos=time/float(self.audio_length)*self.scene_width
		else:
			self.pos=0
		self.setRect(self.x+self.pos-int(self.w/2.0),self.y,self.w,self.h)
	
	def move(self,x_delta):
		pos=self.pos+x_delta
		if(not(pos>self.scene.width)and not(pos<0)):
			self.pos=self.pos+x_delta
			self.setRect(self.x+self.pos-int(self.w/2.0),self.y,self.w,self.h)
			self.time=self.pos*float(self.audio_length)/self.scene_width
			return True
		return False
	
	def __repr__(self):
		return str(self)
		#return '<Audio Wiper: t:'+str(self)+'>'
	
	def __str__(self):
		stime=time.strftime('%H:%M:%S', time.gmtime(self.time))
		msec=int((self.time-int(self.time))*10)
		smsec=str(msec)
		if(len(smsec)<2):
			smsec="0"+smsec
		stime=stime+':'+smsec
		return stime

class Audio_Marker(Audio_Wiper):
	def __init__(self, x=0, y=0, w=10, h=50, parent = None, scene = None,audio_length=0, scene_width=0):
		Audio_Wiper.__init__(self, x, y, w, h, parent, scene, audio_length, scene_width)
		self.point=None
		self.setPen(QtGui.QPen(QtGui.QColor(0,0,155)))
		self.setBrush(QtGui.QBrush(QtGui.QColor(0,0,155,127)))
		self.setZValue(3)
		
	def set_point(self,point):
		"""function links marker to point in path, returning a pointer of itself to the requesting point object"""
		self.point.update_point=point
		return self
	
	def edit_point(self,point=None):
		"""edit point connected to marker"""
		if(point is not None):
			self.point=point
		else:
			pass

	def set_active(self):
		self.setPen(QtGui.QPen(QtGui.QColor(255,0,0)))
		self.setBrush(QtGui.QBrush(QtGui.QColor(200,0,255,127)))
		
	def set_unactive(self):
		self.setPen(QtGui.QPen(QtGui.QColor(0,0,155)))
		self.setBrush(QtGui.QBrush(QtGui.QColor(0,0,155,127)))
	
	def __lt__(self,other):
		return (self.time<other.time)
	
	def __le__(self,other):
		return (self.time<=other.time)
	
	def __eq__(self,other):
		return (self.time==other.time)
	
	def __ne__(self,other):
		return (self.time!=other.time)
	
	def __gt__(self,other):
		return (self.time>other.time)
	
	def __ge__(self,other):
		return (self.time>=other.time)

class Marker_List(QtGui.QWidget):
	def __init__(self,scene,parent=None):
		QtGui.QWidget.__init__(self,parent)
		self.scene=scene
		self.markers=[]
		self.points=[]
		self.x=0
		self.y=0
		self.w=10
		self.h=10

	def add_marker_by_time(self,time=0):
		marker=None
		for m in self.markers:
			if(m.time==time):
				marker=m
				break
		if(markers is None):
			marker=Audio_Marker(self.x,self.y,self.w,self.h,self,self.scene,0,self.scene.width)
			marker.set_time(time)
			self.markers.append(marker)
			self.scene.addItem(marker)
			self.highlight_selected(marker)
			self.emit(QtCore.SIGNAL("markers_updated"),self.markers)
		else:
			QtGui.QMessageBox.warning(scene, 'Audio - Add Marker', QtCore.QString('Marker already present at this time point'))

	def remove_marker_by_time(self, time=0):
		marker=None
		for m in self.markers:
			if(m.time==time):
				marker=m
				break
		if(marker is not None):
			#remove from list, and from scene
			del self.markers[self.markers.index(marker)]
			self.scene.removeItem(marker)
			self.emit(QtCore.SIGNAL("markers_updated"),self.markers)
			self.emit(QtCore.SIGNAL("marker_deleted"),marker)
			del marker
		else:
			QtGui.QMessageBox.warning(self, 'Audio - Del Marker', QtCore.QString('Marker does not exist'))

	def add_marker(self,marker):
		if marker in self.markers:
			QtGui.QMessageBox.warning(self, 'Audio - Add Marker', QtCore.QString('Marker already exists'))
		else:
			self.markers.append(marker)
			self.scene.addItem(marker)
			self.highlight_selected(marker)
			self.emit(QtCore.SIGNAL("markers_updated"),self.markers)

	def remove_marker(self,marker):
		if(marker in self.markers):
			del self.markers[self.markers.index(marker)]
			self.scene.removeItem(marker)
			self.emit(QtCore.SIGNAL("markers_updated"),self.markers)
			self.emit(QtCore.SIGNAL("marker_deleted"),marker)
			del marker
		else:
			QtGui.QMessageBox.warning(None, 'Audio - Del Marker', QtCore.QString('Marker does not exist'))
	
	def highlight_selected(self, marker):
		"""highlight selected marker"""
		print marker
		for m in self.markers:
			m.set_unactive()
		if(marker is not None):
			marker.set_active()
			self.emit(QtCore.SIGNAL("marker_selected"),marker)

	def highlight_selected_quiet(self, marker):
		"""highlight selected mark, suppress "marker_selected" signal"""
		print marker
		for m in self.markers:
			m.set_unactive()
		if(marker is not None):
			marker.set_active()
