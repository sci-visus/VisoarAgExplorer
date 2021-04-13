#from VisoarAgExplorer.slampy.sync import *
from  slampy.sync import *

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

# memory card -> local directory
if (sys.platform.startswith('win')):
	LOCAL_DIR="c:/visoar_files"
else:
	LOCAL_DIR="/User/"


ThisDir = os.path.dirname(os.path.realpath(__file__))


T1=datetime.datetime.now() 

# ////////////////////////////////////////////////////////////
class MyWorker(QObject):
	finished = pyqtSignal()
	progress = pyqtSignal(int,int,str,str,int)
	
	# constructor
	def __init__(self,sync):
		QObject.__init__(self)
		self.sync=sync
		self.sync.progress=self.onProgress
		
	# onProgress
	def onProgress(self,I,N,src,dst,kb_sec):
		self.progress.emit(I,N,src,dst,kb_sec)

	# run
	def run(self):
		self.error_message=None
		try:
			self.sync.run()
		except Exception:
			self.error_message="Error happened {}".format(str(traceback.format_exc()))
		self.finished.emit()
	
# ////////////////////////////////////////////////////////////
class VisoarMoveDataWidget(QWidget):
	
	# constructor
	def __init__(self,parent=None):
		QMainWindow.__init__(self,parent)
		self.parent = parent
		self.processingData = False

		self.log=LogFile.getLogger()
		self.log.print("Got arguments", sys.argv)
		self.processingData = False

		self.setWindowTitle("Sync files")
		self.resize(600,200)
		self.sensors={}
		self.main_layout = QVBoxLayout()

		self.progressFrame = QFrame()
		self.progressLayout = QFormLayout()
		self.progressFrame.setLayout(self.progressLayout)

		self.setLayout(self.main_layout)
		self.refreshGui()

	def setDirSource(self,dirLine):
		self.dir = str(
			QFileDialog.getExistingDirectory(self, "Select Directory containing Images"))
		LOCAL_DIR = self.dir
		sensor_num = self.sensors[self.dir] if self.dir in self.sensors else len(self.sensors)
		dirLine.setText("{}/{}-myfield/sensor{}".format(LOCAL_DIR, T1.strftime("%Y%m%d-%H%M%S"), sensor_num))
		
	# creatDumpMemoryCardWidget
	def creatDumpMemoryCardWidget(self):
		
		widget = QWidget()
		sub=QGridLayout()
		widget.setLayout(sub)
		
		drives=Utils.GetDrives()
		drives.reverse()		
		
		sub.addWidget(QLabel("Memory card"),0,0)
		src_dir=self.createComboBox(drives)
		src_dir.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)		
		clean=QCheckBox("Clean")
		clean.setChecked(False)
		sub.addLayout(self.hlayout([src_dir,clean]),0,1)
		
		sub.addWidget(QLabel("Destination"),1,0)
		dst_dir=QLineEdit()
		sub.addWidget(dst_dir,1,1)

		self.setDirSourceBtn = QPushButton(' . . . ', self)
		self.setDirSourceBtn.resize(180, 40)
		self.setDirSourceBtn.clicked.connect(lambda: self.setDirSource(dst_dir))
		#self.setDirSourceBtn.setStyleSheet(GREEN_PUSH_BUTTON)
		self.setDirSourceBtn.setToolTip('Specify directory of image for stitching')
		sub.addWidget(self.setDirSourceBtn, 1, 2)

	
		def guessDestinationDir(src_dir):
			sensor_num=self.sensors[src_dir] if src_dir in self.sensors else len(self.sensors)
			return "{}/{}-myfield/sensor{}".format(LOCAL_DIR, T1.strftime("%Y%m%d-%H%M%S"),sensor_num)

		src_dir.currentIndexChanged.connect(lambda: dst_dir.setText(guessDestinationDir(src_dir.currentText())))
		dst_dir.setText(guessDestinationDir(src_dir.currentText()))
		
		def onRun(src_dir, dst_dir, clean):
			self.progressFrame.show()
			self.log.print("*** Dumping memory card","src_dir",src_dir, "dst_dir", dst_dir,"clean",clean)
			
			# assign sensor number if needed
			if not src_dir in self.sensors:
				self.sensors[src_dir]=len(self.sensors)
				
			self.setRunning(True)
			copier=CompoundCopyFiles()
			copier.instances.append(SyncLocalToLocal(dst_dir))
			if clean:
				copier.instances.append(CleanLocalFiles())
			sync=SyncFiles(src_dir+"/",copier=copier)
			self.runSyncInBackground(sync)

		button=self.createButton('Run',callback=lambda : onRun(
			src_dir.currentText(),
			dst_dir.text(), 
			clean.isChecked()))
			
		filler=QLabel("")
		filler.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
		sub.addLayout(self.hlayout([filler,button]),2,0,1,2)
		self.buttons.append(button)		
		
		return widget
		
	# createCopyFilesToGoogleWidget
	def createCopyFilesToGoogleWidget(self):
		
		drives=Utils.GetDrives()
		
		widget = QWidget()
		sub=QGridLayout()
		widget.setLayout(sub)
		
		sub.addWidget(QLabel("Local directory"),0,0)
		src_dir=QLineEdit()
		src_dir.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
		src_dir.setText(LOCAL_DIR)
		clean=QCheckBox("Clean")
		clean.setChecked(True)			
		sub.addLayout(self.hlayout([src_dir,clean]),0,1)
		
		sub.addWidget(QLabel("Google Destination"),1,0)
		bucket_name=QLineEdit()
		bucket_name.setText("/visoar_files")
		sub.addWidget(bucket_name,1,1)
		
		sub.addWidget(QLabel("Backup"),2,0)
		backup_dir=QLineEdit()
		backup_dir.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
		backup_dir.setText("{}/visoar_files".format(drives[-1]))
		backup_enabled=QCheckBox("Enabled")
		backup_enabled.setChecked(True)
		backup_enabled.toggled.connect(lambda: backup_dir.setEnabled(backup_enabled.isChecked()))  
		
		sub.addLayout(self.hlayout([backup_dir,backup_enabled]),2,1)
		
		# createCopyFilesToGoogleWidget
		def onRun(src_dir, bucket_name, backup_dir, clean):
			self.progressFrame.show()
			self.log.print("*** Copying", src_dir," to google drive bucket",bucket_name, "backup to",backup_dir, "clean",clean)
			self.setRunning(True)
			copier=CompoundCopyFiles()
			
			# first copy to google drive
			if bucket_name:
				copier.instances.append(SyncLocalToGoogleDrive(bucket_name)) 
			
			# eventually copy to external usb drive
			if backup_dir:
				copier.instances.append(SyncLocalToLocal(backup_dir))
				
			if clean:
				copier.instances.append(CleanLocalFiles())
			
			sync=SyncFiles(src_dir,copier=copier)
			self.runSyncInBackground(sync)	
					
		button=self.createButton('Run',callback=lambda : onRun(
			src_dir.text(), 
			bucket_name.text(), 
			backup_dir.text() if backup_enabled.isChecked() else None,  
			clean.isChecked()))
			
		filler=QLabel("")
		filler.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
		sub.addLayout(self.hlayout([filler,button]),3,0,1,2)
		self.buttons.append(button)		
		
		return widget
		
		
	#  refreshGui
	def refreshGui(self):

		self.buttons=[]

		self.clearLayout(self.main_layout)
		self.clearLayout(self.progressLayout)

		self.main_layout.addLayout(self.hlayout([
			self.createButton('Home', callback=self.parent.goHome),
			self.createButton('Refresh GUI',callback=self.refreshGui),
			self.createButton('Check for updates',callback=self.checkForUpdates),
		]))

		#self.main_layout.addWidget(self.separator())

		self.prog=QLineEdit();self.prog.setEnabled(False)
		#Only show this stuff if processing card:
		self.progressLayout.addRow(
			QLabel('Processing Image Number'),
			self.prog)

		self.src=QLineEdit();self.src.setEnabled(False)
		self.progressLayout.addRow(
			QLabel('Processing Image file'),
			self.src
		)

		self.dst=QLineEdit();self.dst.setEnabled(False)
		self.kb_sec=QLineEdit();self.kb_sec.setEnabled(False)
		self.progressLayout.addRow(
			QLabel('File to be saved'),
			self.dst
		)

		self.progress = QProgressBar(self)
		self.progress.setValue(0)
		self.progressLayout.addRow(
			QLabel('KB/sec'),
			self.kb_sec)
		self.progressLayout.addRow( QLabel('Progression'), self.progress)

		self.main_layout.addWidget(self.progressFrame)
		if (not self.processingData):
			self.progressFrame.hide()
		else:
			self.progressFrame.show()


		tabwidget = QTabWidget()
		self.main_layout.addWidget(tabwidget)
		tabwidget.addTab(self.creatDumpMemoryCardWidget(), "Dump memory card")
		tabwidget.addTab(self.createCopyFilesToGoogleWidget(), "Upload data to Google")			

	# createComboBox
	def createComboBox(self,options=[],callback=None):
		ret=QComboBox()
		ret.addItems(options)
		if callback:
			ret.currentIndexChanged.connect(callback)
		return ret
		
	# separator
	def separator(self):
		line = QLabel(" ")
		#line.setFrameShape(QFrame.HLine)
		#line.setFrameShadow(QFrame.Sunken)
		return line

	# hlayout
	def hlayout(self,items):
		ret=QHBoxLayout()	
		for item in items:
			try:
				ret.addWidget(item)
			except:
				ret.addLayout(item)
		return ret
			
	# vlayout
	def vlayout(self,items):
		ret=QVBoxLayout()	
		for item in items:
			if item.widget() is not None:
				ret.addWidget(item)
			else:
				ret.addLayout(item)
		return ret
			
	# clearLayout
	def clearLayout(self, layout):
		if layout is  None: return
		while layout.count():
			item = layout.takeAt(0)
			widget = item.widget()
			if widget is not None:
				widget.deleteLater()
			else:
				self.clearLayout(item.layout())	
		
	# checkForUpdates
	def checkForUpdates(self):
		print("Checking for updates")	

		import git
		g = git.Git(os.path.join(ThisDir,".."))
		retcode=g.pull('origin','master')
		if retcode.startswith('Already'): 
			message="Software is already updated"
			self.log.print(message)
			QMessageBox.about(self, "Ok", message)
		else:
			message="Software has been updated. You NEED TO RESTART"
			self.log.print(message)
			QMessageBox.about(self, "Error", message)
				
	# createButton
	def createButton(self,text,callback=None):
		ret=QPushButton(text)
		if callback is not None:
			ret.clicked.connect(callback)
		return ret
		
	# onProgress
	def onProgress(self,I,N,src,dst,kb_sec):
		self.progress.setValue(int(100*I/N))
		self.prog.setText("{} of {}".format(I + 1, N))  # AAG: added +1.. count is 0 based but N isn't?
		self.src.setText(src)
		self.dst.setText(dst)
		self.kb_sec.setText(str(kb_sec))
		
	# setRunning
	def setRunning(self,val):
		
		self.progress.setValue(0)
		
		if val:
			self.prog.setText("")
			self.dst.setText("")
			self.src.setText("")
			self.kb_sec.setText("")
			
		for button in self.buttons: 
			button.setEnabled(not val)
				
	# threadFinished
	def threadFinished(self):
		
		self.setRunning(False)
		self.progress.setValue(100)

		if self.worker.error_message:
			message="Error copying files. Please retry ({})".format(self.worker.error_message)
			self.log.print(message)
			QMessageBox.about(self, "Error", message)
		else:
			message="Finished syncing files"
			self.log.print(message)
	
	# runSyncInBackground
	def runSyncInBackground(self,sync,finished=None):
		self.thread = QThread()
		self.worker = MyWorker(sync)
		self.worker.moveToThread(self.thread)
		self.thread.started.connect(self.worker.run)
		if finished:
			self.worker.finished.connect(finished)
		self.worker.finished.connect(self.thread.quit)
		self.worker.finished.connect(self.worker.deleteLater)
		self.thread.finished.connect(self.thread.deleteLater)
		self.worker.finished.connect(self.threadFinished)
		self.worker.progress.connect(self.onProgress)
		self.thread.start()

# //////////////////////////////////////////////////////////
if __name__ == "__main__":
	
	# create the log filename
	LogFile(Utils.NormalizePath(os.path.join(LOCAL_DIR,T1.strftime("%Y%m%d.%H%M%S") + ".visoar.sync.log")))
	
	app=QApplication([])
	gui=VisoarMoveDataWidget()
	gui.show()
	sys.exit(app.exec_())
	
