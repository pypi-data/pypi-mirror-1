import sys
import unittest
from PyQt4 import QtCore, QtGui, QtOpenGL, QtXml
try:
	from point3d import Point3D
	from marker_dialog import MarkerDialog
except ImportError:
	print "Marker Dialog tests failed, could not find marker dialog implementation."

class MarkerDialogTestCase(unittest.TestCase):
	def checkInstantiation(self):
		"""check that we can create a marker"""
		try:
			app = QtGui.QApplication(sys.argv)
			marker_dialog=None
			point=Point3D()
			marker_dialog=MarkerDialog(point)
		except:
			info_str=""
			for info in sys.exc_info():
				info_str= info_str+(str(info))
			self.fail("Could not instantiate Marker Dialog for some reason: "+info_str)
		else:
			assert marker_dialog != None, 'Could not instantiate Marker Dialog'

def suite():
	testSuite=unittest.TestSuite()
	testSuite.addTest(MarkerDialogTestCase("checkInstantiation"))
	return testSuite

def main():
	runner = unittest.TextTestRunner()
	runner.run(suite())

if __name__=="__main__":
	main()
