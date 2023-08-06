from PyQt4 import QtCore, QtGui, QtOpenGL, QtXml
from point3d import Point3D
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


class GLWidget(QtOpenGL.QGLWidget):
		"""OpenGl Widget designed to display a render environment with a sound path."""

		def __init__(self, parent=None):
				"""Set up initial rotation and render objects"""
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
				self.ctrl_click=False;

		def minimumSizeHint(self):
				return QtCore.QSize(50, 50)

		def sizeHint(self):
				return QtCore.QSize(400, 400)

		def setXRotation(self, angle):
				"""modify x rotation"""
				angle = self.normalizeAngle(angle)
				if angle != self.xRot:
						self.xRot = angle
						#self.xRotationChanged.emit(angle)
						self.updateGL()

		def setYRotation(self, angle):
				"""modify z rotation"""
				angle = self.normalizeAngle(angle)
				if angle != self.yRot:
						self.yRot = angle
						#self.yRotationChanged.emit(angle)
						self.updateGL()

		def setZRotation(self, angle):
				"""modify z rotation"""
				angle = self.normalizeAngle(angle)
				if angle != self.zRot:
						self.zRot = angle
						#self.zRotationChanged.emit(angle)
						self.updateGL()

		def setZoom(self,move):
			"""set zoom level"""
			if(move != 0.0):
				self.zoom=self.zoom+move
				self.updateGL()

		def updateRoom(self,width=6.0,height=2.5,depth=8.0):
			"""room coordinates"""
			self.room_box.resize(width,height,depth)
			self.updateGL()

		def initializeGL(self):
				"""set up GL shading and camera perspective"""
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
				"""reset camera for new draw"""
				GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
				GL.glLoadIdentity()
				GL.glTranslated(0.0, 0.0, self.zoom)
				GL.glRotated(self.xRot / 16.0, 1.0, 0.0, 0.0)
				GL.glRotated(self.yRot / 16.0, 0.0, 1.0, 0.0)
				GL.glRotated(self.zRot / 16.0, 0.0, 0.0, 1.0)
				self.draw()

		def resizeGL(self, width=1.0, height=1.0):
				"""reset viewport for resizing of screen"""
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
				"""implement rotation and zoom controls"""
				dx = event.x() - self.lastPos.x()
				dy = event.y() - self.lastPos.y()
				if (event.buttons() & QtCore.Qt.LeftButton) and not self.ctrl_click:
						self.setXRotation(self.xRot + 8 * dy)
						self.setYRotation(self.yRot + 8 * dx)
				elif (event.buttons() & QtCore.Qt.RightButton) or self.ctrl_click:
						self.setZoom(dy)
				self.lastPos = QtCore.QPoint(event.pos())

		def contextMenuEvent(self, event):
			"""implement right-click zoom for mac compatibility"""
			self.ctrl_click=True
			self.lastPos = QtCore.QPoint(event.pos())

		def mouseReleaseEvent(self, event):
			self.ctrl_click=False
			self.updateGL()

		def normalizeAngle(self, angle):
				"""keep angle in positive range between 0 and (360*16)"""
				while angle < 0:
						angle += 360 * 16
				while angle > 360 * 16:
						angle -= 360 * 16
				return angle

		def draw(self):
				"""draw scene to screen"""
				glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);	
				glTranslatef(0.0,0.0,-3.0)
				glPushMatrix()
				self.room_box.draw()
				glPopMatrix()
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
				self.path_tracer.draw()

class GLRoom():
	"""Creates a 3d wireframe box used to represent the dimensions of a room."""
	def __init__(self,xdim,ydim,zdim,):
		"""set initial room dimnesions"""
		try:
			self.xdimension=float(xdim)
			self.ydimension=float(ydim)
			self.zdimension=float(zdim)
		except:
			QtGui.QMessageBox.warning(self, 'Room Error', QtCore.QString('Can not initialize room.'))
			
	def resize(self,xdim,ydim,zdim,):
		"""change room dimensions"""
		try:
			self.xdimension=float(xdim)
			self.ydimension=float(ydim)
			self.zdimension=float(zdim)
		except:
			QtGui.QMessageBox.warning(self, 'Room Error', QtCore.QString('Can not resize room.'))
			
	def draw(self):
		"""draw room"""
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
		"""resize room"""
		self.xdimension=xdim
		self.ydimension=ydim
		self.zdimension=zdim
		
	def draw(self):
		"""draw room"""
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
		"""set which speaker is highlighted"""
		self.selected=selected

	def resize(self,xdim,ydim,zdim,):
		"""resize speaker"""
		self.xdimension=xdim
		self.ydimension=ydim
		self.zdimension=zdim
		
	def draw(self,speakers):
		"""draw speakers"""
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
		"""set selected path point"""
		self.selected=sel

	def draw(self,points=[]):
		"""draw path points and path line"""
		glBegin(self.mode)
		if(len(points)>0):
			color_step=1.0/len(points)
		else:
			color_step=0.0
		color_val=0.0
		#draw path line
		for point in points:
			glColor3f(self.startcolor[0]*(1.0-color_val)+self.endcolor[0]*color_val,self.startcolor[1]*(1.0-color_val)+self.endcolor[1]*color_val,self.startcolor[2]*(1.0-color_val)+self.endcolor[2]*color_val,)
			glVertex3d(point.x,point.y,point.z)
			color_val+=color_step
		glEnd()
		color_val=0.0
		i=0
		#draw path spheres(points)
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

class GLListener():
	"""Draws a doll for use as a listener in audio environment."""
	def __init__(self,height=1.75):
		"""initialize listener height"""
		self.height=height
		
	def draw(self):
		"""draw lister doll"""
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
		"""initialize dicts and lists used to traverse path"""
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
		"""update position of sphere on path"""
		self.pos=self.get_pos(time)

	def draw(self):
		"""draw sphere following path"""
		if(self.path_valid and self.pos is not None):
			glPushMatrix()
			glColor3f(1.0,0.0,1.0)
			glTranslated(self.pos.x,self.pos.y,self.pos.z)
			glutSolidSphere(self.point_size,10,10)
			glPopMatrix()
			