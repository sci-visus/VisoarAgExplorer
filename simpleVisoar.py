import sys, os

import xml.etree.ElementTree as ET
import xml.dom.minidom

from functools import partial


from OpenVisus                        import *
from OpenVisus.gui                    import *



#from VisusGuiPy                       import *
#from VisusAppKitPy                    import *
#from OpenVisus.PyUtils                import *

##from Slam.GuiUtils                    import *
#from Slam.GoogleMaps                  import *
#from Slam.ImageProvider               import *
#from Slam.ExtractKeyPoints            import *
#from Slam.FindMatches                 import *
#from Slam.GuiUtils                    import *
##from Slam.Slam2D                   	  import Slam2D


from PyQt5.QtGui 					  import QFont
from PyQt5.QtCore                     import QUrl, Qt, QSize, QDir, QRect
from PyQt5.QtWidgets                  import QApplication, QHBoxLayout, QLineEdit,QLabel, QLineEdit, QTextEdit, QGridLayout
from PyQt5.QtWidgets                  import QMainWindow, QPushButton, QVBoxLayout,QSplashScreen,QProxyStyle, QStyle, QAbstractButton
from PyQt5.QtWidgets                  import QWidget
from PyQt5.QtWebEngineWidgets         import QWebEngineView	
from PyQt5.QtWidgets                  import QTableWidget,QTableWidgetItem


#from slam2dWidget 				import *

#from analysis_scripts			import *
from lookAndFeel  				import *

from pathlib import Path
from datetime import datetime


# IMPORTANT for WIndows
# Mixing C++ Qt5 and PyQt5 won't work in Windows/DEBUG mode
# because forcing the use of PyQt5 means to use only release libraries (example: Qt5Core.dll)
# but I'm in need of the missing debug version (example: Qt5Cored.dll)
# as you know, python (release) does not work with debugging versions, unless you recompile all from scratch

# on windows rememeber to INSTALL and CONFIGURE


class StartWindow(QMainWindow):
	def __init__(self):
		super().__init__()
		self.setWindowTitle('ViSOAR Ag Explorer Prototype')
		
		self.setMinimumSize(QSize(600, 600))  
		self.setStyleSheet(LOOK_AND_FEEL)

		
		self.central_widget = QFrame()
		self.central_widget.setFrameShape(QFrame.NoFrame)

		self.viewer=Viewer()
		#self.viewer.hide()
		self.viewer.setMinimal()

		self.slam_widget = Slam2DWidgetForVisoar(self)
		self.slam_widget.setStyleSheet(LOOK_AND_FEEL)
		self.slam_widget.progress_bar.bar.setStyleSheet(PROGRESSBAR_LOOK_AND_FEEL)
		self.slam_widget.progress_bar.bar.setMinimumWidth(300)
		self.slam = Slam2D()
		self.slam_widget.slam = self.slam

		#self.tab_widget = MyTabWidget(self)
		#self.setCentralWidget(self.tab_widget)
		#self.setCentralWidget(self.slam_widget)

		viewer_subwin = sip.wrapinstance(FromCppQtWidget(self.viewer.c_ptr()), QtWidgets.QMainWindow)	
		#self.setCentralWidget(viewer_subwin )
		self.setCentralWidget(self.slam_widget )


	def on_click(self):
		print("\n")
		for currentQTableWidgetItem in self.tabWidget.selectedItems():
			print(currentQTableWidgetItem.row(), currentQTableWidgetItem.column(), currentQTableWidgetItem.text())

	def onChange(self):
		QMessageBox.information(self,
			"Tab Index Changed!",
			"Current Tab Index: ");



# //////////////////////////////////////////////////////////////////////////////

 	 

	 
# //////////////////////////////////////////////
def Main(argv):
	SetCommandLine("__main__")
	GuiModule.createApplication()
	GuiModule.attach()  	


	window = StartWindow()

	window.show()	 

	GuiModule.execApplication()
	#viewer=None  
	GuiModule.detach()
	print("All done")
	sys.exit(0)	

# //////////////////////////////////////////////
if __name__ == '__main__':
	Main(sys.argv)

	



	# 	<<project>
	# 	<projName> "Project2" </projName>
	# 	<dir> "/Users/amygooch/GIT/SCI/DATA/FromDale/ag1" </dir>
	# </project>
	# <<project>
	# 	<projName> "Project3" </projName>
	# 	<dir> "/Users/amygooch/GIT/SCI/DATA/TaylorGrant/rgb/" </dir>
	# </project>



