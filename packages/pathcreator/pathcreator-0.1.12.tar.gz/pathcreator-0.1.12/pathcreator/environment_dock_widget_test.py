import sys
import unittest
from PyQt4 import QtCore, QtGui, QtOpenGL, QtXml
try:
	from environment_dock_widget import EnvironmentDockWidget
except ImportError:
	print "Environment Dock tests failed, could not find environment dock implementation."

class  EnvironmentDockWidgetTestCase(unittest.TestCase):
	def checkInstantiation(self):
		"""check that we can create a environment dock widget"""
		try:
			app = QtGui.QApplication(sys.argv)
			env_dialog=None
			env_dialog=EnvironmentDockWidget()
		except:
			info_str=""
			for info in sys.exc_info():
				info_str= info_str+(str(info))
			self.fail("Could not instantiate Environment Dock Widget for some reason: "+info_str)
		else:
			assert env_dialog != None, 'Could not instantiate Environment Dock Widget'
	
	def checkInstantiationWithParameters(self):
		try:
			app = QtGui.QApplication(sys.argv)
			env_dialog=None
			env_dialog=EnvironmentDockWidget(None,"345",["512","1024","2048"],"500")
		except:
			info_str=""
			for info in sys.exc_info():
				info_str= info_str+(str(info))
			self.fail("Could not instantiate Environment Dock Widget for some reason: "+info_str)
		else:
			assert env_dialog != None, 'Could not instantiate Environment Dock Widget'
	

def suite():
	testSuite=unittest.TestSuite()
	testSuite.addTest(EnvironmentDockWidgetTestCase("checkInstantiation"))
	testSuite.addTest(EnvironmentDockWidgetTestCase("checkInstantiationWithParameters"))
	return testSuite

def main():
	runner = unittest.TextTestRunner()
	runner.run(suite())

if __name__=="__main__":
	main()
