import sys,os,platform,subprocess,glob,datetime
import cv2
import numpy
import random
import threading
import time

# this must appear before creating the qapp
from PyQt5.QtWebEngineWidgets import QWebEngineView

from OpenVisus                        import *
from OpenVisus.gui                    import *



from slampy.extract_keypoints import *
from slampy.google_maps       import *
from slampy.gps_utils         import *
from slampy.find_matches      import *
from slampy.gui_utils         import *
from slampy.image_provider    import *
from slampy.image_utils       import *
from slampy.slam_2d       import *
from slampy.slam_2d_gui       import *



import xml.etree.ElementTree as ET
from functools import partial




from PyQt5.QtGui 					  import QFont
from PyQt5.QtCore                     import QUrl, Qt, QSize, QDir, QRect
from PyQt5.QtWidgets                  import QApplication, QHBoxLayout, QLineEdit,QLabel, QLineEdit, QTextEdit, QGridLayout
from PyQt5.QtWidgets                  import QMainWindow, QPushButton, QVBoxLayout,QSplashScreen,QProxyStyle, QStyle, QAbstractButton
from PyQt5.QtWidgets                  import QWidget
from PyQt5.QtWebEngineWidgets         import QWebEngineView	
from PyQt5.QtWidgets                  import QTableWidget,QTableWidgetItem


#from analysis_scripts			import *
from lookAndFeel  				import *

# //////////////////////////////////////////////////////////////////////////////
class Slam2DWidgetForVisoar(Slam2DWidget):
	# constructor
	def __init__(self): 
		super(Slam2DWidget, self).__init__()
		self.redirect_log = GuiRedirectLog()
		self.redirect_log.setCallback(self.printLog)

		self.zoom_on_dataset = False
		self.show_annotations = False
		self.add_run_button = False
		self.add_progress_bar = True
		self.viewer_open_filename = "visus.midx"
		self.createGui()
 