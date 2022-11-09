# this must appear before creating the qapp
from PyQt5.QtWebEngineWidgets import QWebEngineView

from OpenVisus.gui import *


from PyQt5.QtCore    import *
from PyQt5.QtWidgets import *

from . slam_2d import *
from . gui_utils import *

# //////////////////////////////////////////////////////////////////////////////
class GuiRedirectLog(QtCore.QObject):

	"""Redirects console output to text widget."""
	my_signal = QtCore.pyqtSignal(str)

	# constructor
	def __init__(self, filename="~visusslam.log", ):
		super().__init__()
		print('Writing log to: {0}/{1}'.format(os.getcwd(), filename))
		self.log=open(filename,'w')
		self.callback=None
		self.messages=[]
		self.__stdout__     = sys.stdout
		self.__stderr__     = sys.stderr
		self.__excepthook__ = sys.excepthook
		sys.stdout=self
		sys.stderr=self # if you cannot see the error comment this line
		sys.excepthook = self.excepthook

	# handler
	def excepthook(self, exctype, value, traceback):
		sys.stdout    =self.__stdout__
		sys.stderr    =self.__stderr__
		sys.excepthook=self.__excepthook__
		sys.excepthook(exctype, value, traceback)
		
	# setCallback
	def setCallback(self, value):
		self.callback=value
		self.my_signal.connect(value)
		for msg in self.messages:
			self.my_signal.emit(msg)
		self.messages=[]

	# write
	def write(self, msg):
		msg=msg.replace("\n", "\n" + str(datetime.datetime.now())[0:-7] + " ")
		sys.__stdout__.write(msg)
		sys.__stdout__.flush()
		self.log.write(msg)
		if self.callback:
			self.my_signal.emit(msg)
		else:
			self.messages.append(msg)

	# flush
	def flush(self):
		sys.__stdout__.flush()
		self.log.flush()
		
# //////////////////////////////////////////////////////////////////////////////
def CreatePushButton(text,callback=None, img=None ):
	ret=QPushButton(text)
	ret.setAutoDefault(False)
	if callback:
		ret.clicked.connect(callback)
	if img:
		ret.setIcon(QtGui.QIcon(img))
	return ret
		


# //////////////////////////////////////////////////////////////////////////////
class Slam2DWidget(QWidget):

	# constructor
	def __init__(self):
		super(QWidget, self).__init__()
		self.redirect_log=GuiRedirectLog()
		self.redirect_log.setCallback(self.printLog)
		self.zoom_on_dataset=True
		self.show_annotations=True
		self.add_run_button=True
		self.show_progress_bar=True		
		self.viewer_open_filename="google.midx"


	# createGui
	def createGui(self):
		# create widgets
		self.viewer=Viewer()
		self.viewer.setMinimal()
		viewer_subwin = sip.wrapinstance(FromCppQtWidget(self.viewer.c_ptr()), QtWidgets.QMainWindow)	

		self.google_maps = QWebEngineView()
		self.preview=PreviewImage()

		self.log = QTextEdit()
		self.log.setLineWrapMode(QTextEdit.NoWrap)

		p = self.log.viewport().palette()
		p.setColor(QPalette.Base, QtGui.QColor(200,200,200))
		p.setColor(QPalette.Text, QtGui.QColor(0,0,0))
		self.log.viewport().setPalette(p)

		main_layout=QVBoxLayout()

		# toolbar
		toolbar=QHBoxLayout()
		
		if self.add_run_button:
			run_slam=CreatePushButton("Run",lambda: self.onRunClicked())
			toolbar.addWidget(run_slam)
			
		# the progress bar should be constructed because it's used in VisoarAgExplorer
		self.progress_bar=ProgressLine()
		if self.show_progress_bar:
			toolbar.addLayout(self.progress_bar)

		toolbar.addStretch(1)
		main_layout.addLayout(toolbar)

		center = QSplitter(QtCore.Qt.Horizontal)
		center.addWidget(self.google_maps)
		center.addWidget(viewer_subwin)
		center.setSizes([100,200])

		main_layout.addWidget(center,1)
		main_layout.addWidget(self.log)
		
		self.setLayout(main_layout)


	# onRunClicked
	def onRunClicked(self):
		self.slam.run()
		self.preview.hide()
		self.refreshViewer()

	# processEvents
	def processEvents(self):
		QApplication.processEvents()
		time.sleep(0.00001)

	# printLog
	def printLog(self,text):
		self.log.moveCursor(QtGui.QTextCursor.End)
		self.log.insertPlainText(text)
		self.log.moveCursor(QtGui.QTextCursor.End)	
		if hasattr(self,"__print_log__") and self.__print_log__.elapsedMsec()<200: return
		self.__print_log__=Time.now()
		self.processEvents()

	# startAction
	def startAction(self,N,message):
		print(message)
		if self.progress_bar:
			self.progress_bar.setRange(0,N)
			self.progress_bar.setMessage(message)
			self.progress_bar.setValue(0)
			self.progress_bar.show()
			self.processEvents()

	# advanceAction
	def advanceAction(self,I):
		if self.progress_bar:
			self.progress_bar.setValue(max(I,self.progress_bar.value()))
			self.processEvents()

	# endAction
	def endAction(self):
			if self.progress_bar:
				self.progress_bar.hide()
				self.processEvents()

	# showMessageBox
	def showMessageBox(self,msg):
		print(msg)
		QMessageBox.information(self, 'Information', msg)

	# showEnergy
	def showEnergy(self,camera,energy):

		if self.slam.debug_mode:
			SaveImage(os.path.join(self.slam.cache_dir,"generated","%04d.%d.tif" % (camera.id,camera.keypoints.size()), energy))

		self.preview.showPreview(energy,"Extracting keypoints image(%d/%d) #keypoints(%d)" % (camera.id,len(self.slam.provider.images),camera.keypoints.size()))
		self.processEvents()

	# refreshViewer
	def refreshViewer(self,fieldname="output=voronoi()"):
		url=os.path.join(self.slam.cache_dir, self.viewer_open_filename)
		self.viewer.open(url)
		# make sure the RenderNode get almost RGB components
		self.viewer.setFieldName(fieldname)	

		# don't show logs
		pref=ViewerPreferences()
		pref.bShowToolbar=False
		pref.bShowTreeView=False
		pref.bShowDataflow=False
		pref.bShowLogs=False
		self.viewer.setPreferences(pref)
			
		if self.show_annotations:
			db=self.viewer.getDataset()
			db.setEnableAnnotations(False)  #This crashes on my mac

		# focus on slam dataset (not google world)
		if self.zoom_on_dataset:
			db=self.viewer.getDataset()
			box=db.getChild("visus").getDatasetBounds().toAxisAlignedBox()
			self.viewer.getGLCamera().guessPosition(box)

	# refreshGoogleMaps
	def refreshGoogleMaps(self):

		images=self.slam.images
		if not images:
			return

		maps=GoogleMaps()
		maps.addPolyline([(img.lat,img.lon) for img in images],strokeColor="#FF0000")

		for I,img in enumerate(images):
			maps.addMarker(img.filenames[0], img.lat, img.lon, color="green" if I==0 else ("red" if I==len(images)-1 else "blue"))
			dx=math.cos(img.yaw)*0.00015
			dy=math.sin(img.yaw)*0.00015
			maps.addPolyline([(img.lat, img.lon),(img.lat + dx, img.lon + dy)],strokeColor="yellow")

		content=maps.generateHtml()

		filename=os.path.join(self.slam.cache_dir,"slam.html")
		SaveTextDocument(filename,content)
		self.fixAPIKey(filename)
		self.google_maps.load(QUrl.fromLocalFile(filename))

	# if Google API KEY is changes, then this function can fix slam.html
	def fixAPIKey(self, htmlFile):
		#from __future__ import division, unicode_literals
		import codecs
		from bs4 import BeautifulSoup
		if (htmlFile):
			#htmlFile = "/Volumes/TenGigaViSUSAg/2021Season/MapIR/20210527_MAPIR_02/Calibrated_4/VisusSlamFiles/slamcopy.html"
			import shutil
			shutil.copyfile(htmlFile, htmlFile + ".bk")

			f = codecs.open(htmlFile + ".bk", 'r', 'utf-8')
			contents = f.read()

			soup = BeautifulSoup(contents, 'lxml')
			scriptToChange = soup.script
			# GOOGLE API KEY, if it changes, can use this to fix old files..
			scriptToChange[
				"src"] = u"https://maps.googleapis.com/maps/api/js?libraries=visualization&key=AIzaSyDmbEL1uORNe-Ga828Tbi-lh0F0iQQbP18"

			f2 = codecs.open(htmlFile, 'w', 'utf-8')
			f2.write(str(soup))
			f2.close()
			f.close()

	# rim
	def run(self,slam):
		self.slam=slam
		slam.provider.progress_bar=self.progress_bar
		slam.startAction=self.startAction
		slam.advanceAction=self.advanceAction
		slam.endAction=self.endAction
		slam.showEnergy=self.showEnergy
		self.refreshGoogleMaps()
		self.refreshViewer()

# //////////////////////////////////////////////////////////////////////////////
class Slam2DWindow(QMainWindow):		
	
	# constructor
	def __init__(self):
		super(QMainWindow, self).__init__()
		self.setWindowTitle("Visus SLAM")
		self.widget=Slam2DWidget()
		self.widget.add_run_button=True
		self.widget.add_progress_bar=True
		self.widget.zoom_on_dataset=True
		self.widget.show_annotations=True
		self.widget.viewer_open_filename="google.midx"
		self.widget.createGui()
		self.setCentralWidget(self.widget)
		self.showMaximized()	
		ShowSplash()
		
	# run
	def run(self,slam):
		self.setWindowTitle("num_images({}) width({}) height({}) dtype({}) ".format(len(slam.provider.images),slam.width, slam.height, slam.dtype.toString()))
		self.widget.run(slam)
		HideSplash()	
		QApplication.instance().exec()
