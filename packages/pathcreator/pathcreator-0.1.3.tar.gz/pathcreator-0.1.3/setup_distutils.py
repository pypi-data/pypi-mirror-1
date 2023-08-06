#!/usr/bin/python 

from distutils.core import setup 

setup (name = 'pathcreator', 
					description = "Tool to create 3d sound rendering path given a listener, speakers, audio path and audio track.", 
					author = "Charles Maynard, Vis Center", 
					author_email = "cmaynard+path_creator@gmail.com", 
					version = '0.1', 
					url="http://vis.uky.edu/",
					scripts=['path_creator'],
					packages = ['pathcreator'],
					requires=['PyQt4','OpenGl', 'pygame'],
					#package_data=[''
					data_files = ['path_creator']
			 )
