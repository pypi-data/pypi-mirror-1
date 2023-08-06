import sys
import unittest
from PyQt4 import QtCore, QtGui, QtOpenGL, QtXml
try:
	from point3d import Point3D
	from point_dialog import PointDialog
except ImportError:
	print "Point dialog tests failed, could not find point implementation."

class PointDialogTestCase(unittest.TestCase):
	def checkInstantiation(self):
		"""check that we can create a point"""
		try:
			app = QtGui.QApplication(sys.argv)
			point_dialog=None
			point_dialog=PointDialog()
		except:
			info_str=""
			for info in sys.exc_info():
				info_str= info_str+(str(info))
			self.fail("Could not instantiate Point Dialog for some reason: "+info_str)
		else:
			assert point_dialog != None, 'Could not instantiate Point Dialog'
	
	def checkSetPoint(self):
		"""check that we can set a point to a valid value"""
		app = QtGui.QApplication(sys.argv)
		point=Point3D(1,2,3)
		point_dialog=None
		point_dialog=PointDialog()
		try:
			point_dialog.set_point(point)
		except:
			info_str=""
			for info in sys.exc_info():
				info_str= info_str+(str(info))
			self.fail("Could not set point in Point Dialog for some reason: "+info_str)
		else:
			assert (float(point_dialog.ui.lineEdit_X.text())==1 and float(point_dialog.ui.lineEdit_Y.text())==2 and float(point_dialog.ui.lineEdit_Z.text())==3), 'Could not set point in Point Dialog'
	
	def checkInstantiatePointWithString(self):
		app = QtGui.QApplication(sys.argv)
		try:
			point=Point3D("this","should","fail")
		except ValueError:
			pass
		else:
			self.fail("Point set using string")	

	def checkUpdatePointWithString(self):
		point=Point3D(1,2,3)
		try:
			point.update_coords("this","should","fail")
		except ValueError:
			pass
		else:
			self.fail("Point updated using string")


		
		
def suite():
	testSuite=unittest.TestSuite()
	testSuite.addTest(PointDialogTestCase("checkInstantiation"))
	testSuite.addTest(PointDialogTestCase("checkSetPoint"))
	testSuite.addTest(PointDialogTestCase("checkInstantiatePointWithString"))
	testSuite.addTest(PointDialogTestCase("checkUpdatePointWithString"))
	return testSuite


def main():
	runner = unittest.TextTestRunner()
	runner.run(suite())

if __name__=="__main__":
	main()
