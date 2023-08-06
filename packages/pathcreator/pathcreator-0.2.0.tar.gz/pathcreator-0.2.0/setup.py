#!/usr/bin/python
try:
	import ez_setup
	ez_setup.use_setuptools()
except ImportError:
	pass

from setuptools import setup, find_packages

setup (name = 'pathcreator', 
					description = "Tool to create 3d sound rendering path given a listener, speakers, audio path and audio track.", 
					author = "Charles Maynard, Vis Center", 
					author_email = "cmaynard+path_creator@gmail.com", 
					version = '0.2.0', 
					url="http://vis.uky.edu/",
					scripts=['path_creator'],
					packages = ['pathcreator'],
					#removed dependencies because they NEVER find the right stuff even if a simple search of PyPi does, this is rediculous
					install_requires=['PyOpenGl>=3.0', 'Pygame>=1.7.1'],
					#dependency_links=["http://www.riverbankcomputing.co.uk/software/pyqt/download"],
					#package_data={'':['*.py'],'pathcreator':['*.wav']},
					include_package_data=True,
					exclude_package_data = { 
						'pathcreator': ['*.ui'],
						'' : ['*.ui']
					},
					data_files = ['path_creator']
			 )
