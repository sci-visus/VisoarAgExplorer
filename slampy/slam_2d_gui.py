# this must appear before creating the qapp
from PyQt5.QtWebEngineWidgets import QWebEngineView

from OpenVisus.gui import *

from PyQt5           import * 
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
		self.log=open(filename,'w')
		self.callback=None
		self.messages=[]
		sys.__stdout__     = sys.stdout
		sys.__stderr__     = sys.stderr
		sys.__excepthook__ = sys.excepthook
		sys.stdout=self
		sys.stderr=self
		sys.excepthook = self.excepthook

	# handler
	def excepthook(self, exctype, value, traceback):
		sys.stdout    =sys.__stdout__
		sys.stderr    =sys.__stderr__
		sys.excepthook=sys.__excepthook__
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

class Slam2DWidget(QWidget):

	# constructor
	def __init__(self):
		super(Slam2DWidget, self).__init__()
		self.slam = None
		self.redirect_log=GuiRedirectLog()
		self.redirect_log.setCallback(self.printLog)	
		self.createGui()
		

	# createPushButton
	def createPushButton(self,text,callback=None, img=None ):
		ret=QPushButton(text)
		#ret.setStyleSheet("QPushButton{background: transparent;}");
		ret.setAutoDefault(False)
		if callback:
			ret.clicked.connect(callback)
		if img:
			ret.setIcon(QtGui.QIcon(img))
		return ret

	# createGui
	def createGui(self):

		self.layout = QVBoxLayout(self)
		
		class Buttons : pass
		self.buttons=Buttons

		# create widgets
		self.viewer=Viewer()
		self.viewer.setMinimal()
		viewer_subwin = sip.wrapinstance(FromCppQtWidget(self.viewer.c_ptr()), QtWidgets.QMainWindow)	

		self.google_maps = QWebEngineView()
		self.progress_bar=ProgressLine()
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
		
		toolbar.addLayout(self.progress_bar)

		toolbar.addStretch(1)
		main_layout.addLayout(toolbar)

		center = QSplitter(QtCore.Qt.Horizontal)
		center.addWidget(self.google_maps)
		center.addWidget(viewer_subwin)
		center.setSizes([100,200])

		main_layout.addWidget(center,1)
		
		DRAW_LOG_BOX = False
		if DRAW_LOG_BOX:
			main_layout.addWidget(self.log)

		self.layout.addLayout(main_layout)
# 		central_widget = QFrame()
# 		central_widget.setLayout(main_layout)
# 		central_widget.setFrameShape(QFrame.NoFrame)
# 		self.setCentralWidget(central_widget)


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
		self.progress_bar.setRange(0,N)
		self.progress_bar.setMessage(message)
		self.progress_bar.setValue(0)
		self.progress_bar.show()
		self.processEvents()

	# advanceAction
	def advanceAction(self,I):
		self.progress_bar.setValue(max(I,self.progress_bar.value()))
		self.processEvents()

	# endAction
	def endAction(self):
		self.progress_bar.hide()
		self.processEvents()

	# showMessageBox
	def showMessageBox(self,msg):
		print(msg)
		QMessageBox.information(self, 'Information', msg)

	# showEnergy
	def showEnergy(self,camera,energy):

		if self.slam.debug_mode:
			SaveImage(self.slam.cache_dir+"/generated/%04d.%d.tif" % (camera.id,camera.keypoints.size()), energy)

		self.preview.showPreview(energy,"Extracting keypoints image(%d/%d) #keypoints(%d)" % (camera.id,len(self.slam.provider.images),camera.keypoints.size()))
		self.processEvents()

	# refreshViewer
	def refreshViewer(self,fieldname="output=voronoi()"):
		#url=self.slam.cache_dir+"/google.midx"
		url=self.slam.cache_dir+"/visus.midx"
		self.viewer.open(url)
		#print('Note: the above will fail if you don\'t have the yaml file'..)
		# make sure the RenderNode get almost RGB components
		self.viewer.setFieldName(fieldname)	

		# don't show logs
		pref=ViewerPreferences()
		pref.bShowToolbar=False
		pref.bShowTreeView=False
		pref.bShowDataflow=False
		pref.bShowLogs=False
		self.viewer.setPreferences(pref)

		if False:  #AAG: This causes this to seg fault in ViSOAR Ag Explorer
			# don't show annotations
			db=self.viewer.getDataset()
			db.setEnableAnnotations(False)

			# focus on slam dataset (not google world)
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
		self.google_maps.load(QUrl.fromLocalFile(filename))	

	def run(self,slam):
		try:
			self.slam=slam
			slam.provider.progress_bar=self.progress_bar
			slam.startAction=self.startAction
			slam.advanceAction=self.advanceAction
			slam.endAction=self.endAction
			slam.showEnergy=self.showEnergy

			self.refreshGoogleMaps()
			self.refreshViewer()
			# self.setWindowTitle("num_images({}) width({}) height({}) dtype({}) ".format(
			# 	len(self.slam.provider.images),
			# 	self.slam.width,
			# 	self.slam.height,
			# 	self.slam.dtype.toString()))

			return True
			#QApplication.instance().exec()   #Is this okay...?
		except:
				QMessageBox.information(self,
										"No data set loaded",
										"Please load a dataset before Stitching. ")
				return False
# 
# 	# rim
# 	def run(self,slam):
# 		self.slam=slam
# 		slam.provider.progress_bar=self.progress_bar
# 		slam.startAction=self.startAction
# 		slam.advanceAction=self.advanceAction
# 		slam.endAction=self.endAction
# 		slam.showEnergy=self.showEnergy
# 		self.refreshGoogleMaps()
# 		self.refreshViewer()
# 		self.setWindowTitle("num_images({}) width({}) height({}) dtype({}) ".format(len(self.slam.provider.images),self.slam.width, self.slam.height, self.slam.dtype.toString()))
# 		HideSplash()
# 		QApplication.instance().exec()

class Slam2DWindow(QMainWindow):

	# constructor
	def __init__(self):
		super(Slam2DWindow, self).__init__()
		ShowSplash()
		self.createGui()
		self.showMaximized()	

	def createGui(self):
		self.setWindowTitle("Visus SLAM")
		self.slamWidget = Slam2DWidget()

		main_layout = QVBoxLayout()

		# toolbar
		toolbar = QHBoxLayout()
		self.buttons.run_slam = self.createPushButton("Run", lambda: self.onRunClicked())

		toolbar.addWidget(self.buttons.run_slam)
		#toolbar.addLayout(self.progress_bar)


		main_layout.addWidget(self.slamWidget, 1)
		main_layout.addWidget(self.log)

		central_widget = QFrame()
		central_widget.setLayout(main_layout)
		central_widget.setFrameShape(QFrame.NoFrame)
		self.setCentralWidget(central_widget)

	def onRunClicked(self):
		self.slamWidget.slam.run()
		self.slamWidget.preview.hide()
		self.slamWidget.refreshViewer()

	def run(self,slam):
		HideSplash()
		self.slam=slam
		self.slam.run(slam)
		