import sys
import unittest
from PyQt4 import QtCore, QtGui, QtOpenGL, QtXml, QtTest
try:
	from audio_dock import Audio_DockWidget
except ImportError:
	print "Audio Dock dialog tests failed, could not find Audio Dock implementation."

class AudioDockTestCase(unittest.TestCase):
	def checkInstantiation(self):
		"""check that we can create a point"""
		try:
			app = QtGui.QApplication(sys.argv)
			audio_dock=None
			audio_dock=Audio_DockWidget()
		except:
			info_str=""
			for info in sys.exc_info():
				info_str= info_str+(str(info))
			self.fail("Could not instantiate Audio_Dock for some reason: "+info_str)
		else:
			assert audio_dock != None, 'Could not instantiate Audio Dock'
	
	def check_open_file(self):
		"""check that open file dialog works"""
		app = QtGui.QApplication(sys.argv)
		audio_dock=None
		audio_dock=Audio_DockWidget()
		audio_dock.open_file("caratspeeda.wav")

		
		
def suite():
	"""run test suite"""
	testSuite=unittest.TestSuite()
	testSuite.addTest(AudioDockTestCase("checkInstantiation"))
	#testSuite.addTest(AudioDockTestCase("check_open_file"))
	return testSuite


def main():
	"""run program"""
	runner = unittest.TextTestRunner()
	runner.run(suite())

if __name__=="__main__":
	"""if this file is ran directly call main"""
	main()
