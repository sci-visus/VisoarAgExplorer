from VisoarSettings import *

#from slam2dWidget 				import *

#from analysis_scripts			import *
from lookAndFeel  				import *

from pathlib import Path
from datetime import datetime
from ViSOARUIWidget import *
from slampy.utils import *


# IMPORTANT for WIndows
# Mixing C++ Qt5 and PyQt5 won't work in Windows/DEBUG mode
# because forcing the use of PyQt5 means to use only release libraries (example: Qt5Core.dll)
# but I'm in need of the missing debug version (example: Qt5Cored.dll)
# as you know, python (release) does not work with debugging versions, unless you recompile all from scratch

# on windows rememeber to INSTALL and CONFIGURE


class StartWindow(QMainWindow):
	def __init__(self):
		super().__init__()
		self.scriptNames = MASTER_SCRIPT_LIST
		self.setWindowTitle('ViSOAR Ag Explorer Prototype')
		
		self.setMinimumSize(QSize(600, 600))  
		self.setStyleSheet(LOOK_AND_FEEL)

		
		self.central_widget = QFrame()
		self.central_widget.setFrameShape(QFrame.NoFrame)

		self.viewerW = MyViewerWidget(self)

		self.viewer = self.viewerW.viewer  # MyViewer()

		# self.viewer.hide()
		self.viewer.setMinimal()
		self.viewer_subwin = self.viewerW.viewer_subwin

		self.slam_widget = Slam2DWidgetForVisoar()
		self.slam = Slam2D()
		# self.redirect_log.setCallback(self.slam.printLog)
		print("Log from ViSOARUIWidget....")
		self.slam.enable_svg = False
		self.slam_widget.setStyleSheet(LOOK_AND_FEEL)
		self.slam_widget.progress_bar.bar.setStyleSheet(PROGRESSBAR_LOOK_AND_FEEL)
		self.slam_widget.progress_bar.bar.setMinimumWidth(300)

		self.setCentralWidget(self.slam_widget )


	def on_click(self):
		print("\n")
		for currentQTableWidgetItem in self.tabWidget.selectedItems():
			print(currentQTableWidgetItem.row(), currentQTableWidgetItem.column(), currentQTableWidgetItem.text())

	def onChange(self):
		QMessageBox.information(self,
			"Tab Index Changed!",
			"Current Tab Index: ");


	def setEnabledCombobxItem(self, cbox, itemName, enabled):
		itemNumber = self.scriptNames.index(itemName)
		cbox.model().item(itemNumber).setEnabled(enabled)


# //////////////////////////////////////////////////////////////////////////////

 	 

	 
# //////////////////////////////////////////////
def Main(argv):
	SetCommandLine("__main__")
	if hasattr(Qt, 'AA_EnableHighDpiScaling'):
		QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
	if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
		QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

	app = QApplication(sys.argv)
	# app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
	# app.setAttribute(Qt.AA_EnableHighDpiScaling, True)

	app.setStyle("Fusion")

	#GuiModule.createApplication()
	GuiModule.attach()  	


	window = StartWindow()

	window.show()

	app.exec()

	#GuiModule.execApplication()
	#viewer=None  
	GuiModule.detach()
	print("All done")
	#sys.exit(0)

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



