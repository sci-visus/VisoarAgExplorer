import os,sys,time
import os.path
import glob,traceback,datetime,time
import shutil
import subprocess
import webbrowser
import filecmp
import logging
import logging.handlers
import shlex, subprocess
import signal
import threading
import hashlib
from threading import Timer

"""
how to generate new Google Drive API credentials:

- Follow this https://pythonhosted.org/PyDrive/quickstart.html to generate credentials
- you will download a JSON file 
- Extract ClientId and Client Secret from the file
- Create a client_settings.yaml with the content

```
client_config_backend: settings
client_config:
  client_id: "<REPLACE_HERE_AS_NEEDED>"
  client_secret: "<REPLACE_HERE_AS_NEEDED>"

save_credentials: True
save_credentials_backend: file
save_credentials_file: client_secrets.json

get_refresh_token: True

oauth_scope:
  - https://www.googleapis.com/auth/drive.file
  - https://www.googleapis.com/auth/drive.install
```

"""
# 
# basically and from that you extract the info to filla `client_settings.yaml`
from pydrive.auth  import GoogleAuth
from pydrive.drive import GoogleDrive

ThisDir = os.path.dirname(os.path.realpath(__file__))

T1=datetime.datetime.now() 

# memory card -> local directory
LOCAL_DIR="c:/visoar_files"

# local diretory to google bucket name
BUCKET_NAME="/visoar_files"

# local directory to usb backup drive
BACKUP_DIR="{}/visoar_files"

# ///////////////////////////////////////////////
class LogFile:
	
	# constructor
	def __init__(self,):
		self.filename=Utils.NormalizePath(os.path.join(LOCAL_DIR,T1.strftime("%Y%m%d.%H%M%S") + ".visoar.sync.log"))
		os.makedirs(os.path.dirname(self.filename), exist_ok=True)
		
	# print
	def print(self,*args):
		message=time.strftime("[%Y/%m/%d %H:%M:%S] ") + ' '.join([str(arg) for arg in args])
		print(message)	
		with open(self.filename, 'a+') as f: # Use file to refer to the file object
			f.write(message + '\n')

log=None

	
# //////////////////////////////////////////////////////////
class Utils:
	
	@staticmethod
	def NormalizePath(filename):
		return os.path.abspath(filename).replace("\\","/")

	@staticmethod
	def GetFileSize(filename):
		return os.stat(filename).st_size 

	# return a list of fixed and external drives
	@staticmethod
	def GetUsbDrives():
		log.print("GetUsbDrives...")
		ret = []
		
		if 'darwin' in sys.platform:
			for line in os.listdir('/Volumes'):
				if not 'Macintosh HD' in line:
					ret.append('/Volumes/' + line.strip())			
			
		elif 'win' in sys.platform:
			
			def Win32Info(key):
				ret = []
				output,err = subprocess.Popen('wmic logicaldisk get {}'.format(key), shell=True, stdout=subprocess.PIPE).communicate()
				output = output.decode("utf-8").strip()
				for line in output.split('\n')[1:]:
					ret.append(line.strip())
				return ret	
				
			names=Win32Info("name")
			descriptions=Win32Info("description")
			ids=Win32Info("VolumeSerialNumber")
			
			descriptions=descriptions + ([''] * (len(names)-len(descriptions)))
			ids=ids + (['0'] * (len(names)-len(ids)))
			print("Win32", names,descriptions,ids)
			for name,description,id in zip(names,descriptions,ids):
				description=description.lower()
				print(name,description,id)
				if id=='0' or "local fixed" in description or "cd-rom" in description:
					continue
				ret.append((name,id))
			
		else:
			log.print('Unhandeled OS: List drives')
			#This code might work
			# import usb
			# busses = usb.busses()
			# for bus in busses:
			# 	devices = bus.devices
			# 	for dev in devices:
			# 		print("Device:", dev.filename)
			# 		print("  idVendor: %d (0x%04x)" % (dev.idVendor, dev.idVendor))
			# 		print("  idProduct: %d (0x%04x)" % (dev.idProduct, dev.idProduct))			
		
		log.print("External drives",ret)
		return ret
		
	
	# EjectUSBDrive (BROKEN!
	@staticmethod
	def EjectUSBDrive(drive):
		tmp_file = open('tmp.ps1','w')
		tmp_file.write("""$driveEject = New-Object -comObject Shell.Application\n""")
		tmp_file.write("""$driveEject.Namespace(17).ParseName("{}").InvokeVerb("Eject")\n""".format(drive))
		tmp_file.close()
		process = subprocess.Popen(['powershell.exe', '-ExecutionPolicy','Unrestricted','.\\tmp.ps1'],stdout=sys.stdout)
		process.communicate()
		time.sleep(2)
	
	# ComputeMd5
	@staticmethod
	def ComputeMd5(filename):
		if not os.path.isfile(filename):
			return None
		ret=None
		with open(filename, "rb") as f:
			md5_hash = hashlib.md5()
			md5_hash.update(f.read())
			return md5_hash.hexdigest()		
	
# //////////////////////////////////////////////////////////	
class CopyLocalFiles:
	
	# constructor
	def __init__(self,dst_dir):
		self.dst_dir=dst_dir
	
	# copyFile
	def copyFile(self,src,dst):
		
		dst=os.path.join(self.dst_dir,dst).replace("\\","/")
		
		os.makedirs(os.path.dirname(dst), exist_ok=True) # create parent directory
		
		l1=Utils.ComputeMd5(src)
		l2=Utils.ComputeMd5(dst)
		if l1==l2:
			log.print("File {} already on destination. No need to copy again".format(src),"md5",l1)
			return
		
		# copy2 preserve metadata
		shutil.copy2(src, dst)	

		# verify the new data
		l2=Utils.ComputeMd5(dst)
		if l1!=l2:
			raise Exception("MD5 check failed")
			
		log.print("CopyLocalFiles: copied {} file to local {} md5({})".format(src, dst,l1))	
		
		

# //////////////////////////////////////////////////////////
class CopyFilesToGoogleDrive:
	
	settings_file=os.path.join(ThisDir,'client_settings.yaml')
	
	# constructor
	def __init__(self,bucket_name):
		self.bucket_name=bucket_name
		self.auth=GoogleAuth(settings_file=CopyFilesToGoogleDrive.settings_file)
		self.drive=GoogleDrive(self.auth)	
		self.root={'title':'root','id':'root'}
		self.folders={} # caching the folders

	# https://pythonhosted.org/PyDrive/quickstart.html 
	# first you create Credentials as described
	# then you create a local client_settings.yaml replacing client id and client secret with right values
	def createFolder(self,name):
		
		if name in self.folders:
			return self.folders[name]
			
		nlevels=name.count("/")
		
		if nlevels>=2:
			# /visoar_files/cc/dd/ee
			parent,child=name.rsplit("/",maxsplit=1)
			parent=self.createFolder(parent)
		elif nlevels==1:
			# /visoar_files
			parent=self.root
			child=name[1:]
		else:
			raise Exception("internal error")

		# see if already exists
		files=self.drive.ListFile({'q': "'{}' in parents and trashed=false and title='{}'".format(parent['id'],child)}).GetList()
		if files: 
			ret=files[0]
			log.print("Using directory",name,"id",ret['id'])
		else:
			ret = self.drive.CreateFile({'title' : child, "parents":  [{"id": parent['id']}], 'mimeType' : 'application/vnd.google-apps.folder'})
			ret.Upload()
			log.print("Created new directory",name,"id",ret['id'])
			
		self.folders[name]=ret
		return ret
		
	# computeMd5
	def computeMd5(self, parent_id,title):
		remote_files=self.drive.ListFile({'q': "'{}' in parents and trashed=false and title='{}'".format(parent_id,title)}).GetList()
		return remote_files[0]['md5Checksum'] if remote_files else None

	# copyFile
	def copyFile(self,src, dst):
		
		dst=(self.bucket_name + "/" + dst).replace("\\","/")
		parent, child =dst.rsplit('/',maxsplit=1)
		parent=self.createFolder(parent)

		l1=Utils.ComputeMd5(src)
		l2=self.computeMd5(parent['id'],child)
		
		if l1 == l2:
			log.print("File {} already on Google drive. No need to copy again md5({})".format(src,l1))
			return 

		file = self.drive.CreateFile({'title': child, 'parents': [{'id': parent['id']}]})
		file.SetContentFile(src)
		file.Upload() 
		
		if file['title'] != child:
			raise Exception("uplod of file failed")
			
		if file['md5Checksum'] !=l1:
			raise Exception("MD5 checksum failed")
			
		log.print("CopyFilesToGoogleDrive: uploaded {} file to Google drive md5({}). MD5 check ok".format(src,l1))
	
# //////////////////////////////////////////////////////////
class CompoundCopyFiles:
	
	# ___init__
	def __init__(self):
		self.instances=[]
		
	# copyFile
	def copyFile(self,src,dst):
		for it in self.instances:
			it.copyFile(src,dst)
		
		# no need to keep it around
		if os.path.abspath(src)!=os.path.abspath(log.filename):
			os.remove(src)
	
# //////////////////////////////////////////////////////////
class SyncFiles:
	
	# constructor
	def __init__(self,src_dir,copier=None,progress=None):
		self.src_dir=src_dir
		self.copier=copier
		self.progress=progress
		
	# list all files in a directory
	def findFiles(self,dir,recursive=True):
		ret=glob.glob(dir + '/**/*', recursive=recursive)
		ret=[Utils.NormalizePath(src) for src in ret if os.path.isfile(src)]
		ret=[filename for filename in ret if not "System Volume Information" in filename]	
		return ret
		
	# run
	def run(self):
		
		log.print("Syncing folders")
		log.print("source directory", self.src_dir)
		
		t1 = time.time()
		
		nfiles,tot_bytes=0,0
		
		src_files=self.findFiles(self.src_dir)
		
		# make sure it's the last one (otherwise I will lose some logs)
		if log.filename in src_files:
			src_files.remove(log.filename)
			src_files.append(log.filename)
		
		N=len(src_files)
		
		# for all files in src dir only
		for I,src in enumerate(src_files):

			# do not user normalize path
			dst=os.path.relpath(src, self.src_dir).replace("\\","/") 

			file_size=Utils.GetFileSize(src)
			
			log.print("%d/%d" % (I,N),"Doing",src,dst,"...")
			self.copier.copyFile(src,dst)

			nfiles+=1
			tot_bytes+=file_size 
			
			kb=tot_bytes/(1024)
			sec=time.time()-t1
			kb_sec=int(kb/sec) if sec else 0
			log.print("%d/%d" % (I,N),"Done",src, dst,"{}KB".format(int(file_size/1024)),"{}KB/sec".format(kb_sec),"KB({})".format(kb))
					
			# generator for a workflow
			if self.progress:
				self.progress(I,N, src, dst, kb_sec)
				
			time.sleep(0)
					
		# try to remove all empty subdirectories 
		for sub in [os.path.join(self.src_dir,it) for it in os.listdir(self.src_dir)]:
			if os.path.isdir(sub) and not self.findFiles(sub):
				shutil.rmtree(sub, ignore_errors=True)
			
		kb=int(tot_bytes/1024)
		sec=time.time()-t1
		kb_sec=int(kb/sec) if sec else 0
		log.print("All done in","%.2fsec" % sec, "{}KB".format(kb),"{}KB/sec".format(kb_sec))


# ///////////////////////////////////////////////////////////
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

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
class VisoarMoveDataFromCardWidget(QWidget):
	
	# constructor
	def __init__(self,parent=None):
		QMainWindow.__init__(self,parent)
		
		global log
		if log is None:
			log=LogFile()
			log.print("Got arguments", sys.argv)
		
		self.setWindowTitle("Sync files")
		self.resize(400,200)
		self.sensors={}
		self.createGui()
		
	# checkForUpdates
	def checkForUpdates(self):
		print("Checking for updates")	

		import git
		g = git.Git(os.path.join(ThisDir,".."))
		retcode=g.pull('origin','master')
		if retcode.startswith('Already'): 
			message="Software is already updated"
			log.print(message)
			QMessageBox.about(self, "Ok", message)
		else:
			message="Software has been updated. You NEED TO RESTART"
			log.print(message)
			QMessageBox.about(self, "Error", message)
		
		
	def separator(self):
		line = QLabel(" ")
		#line.setFrameShape(QFrame.HLine)
		#line.setFrameShadow(QFrame.Sunken)
		return line
		
	#  createGui
	def createGui(self):
		
		main_layout = QVBoxLayout()
		self.setLayout(main_layout)
		
		main_layout.addLayout(self.hlayout([
			self.createButton('Refresh GUI',callback=self.refreshButtons),
			self.createButton('Check for updates',callback=self.checkForUpdates),
		]))
		
		main_layout.addWidget(self.separator())
		
		self.prog=QLineEdit();self.prog.setEnabled(False)
		main_layout.addWidget(QLabel('Current'))
		main_layout.addWidget(self.prog)		
		
		self.src=QLineEdit();self.src.setEnabled(False)
		main_layout.addWidget(QLabel('Source'))
		main_layout.addWidget(self.src)
				
		self.dst=QLineEdit();self.dst.setEnabled(False)
		self.kb_sec=QLineEdit();self.kb_sec.setEnabled(False)
		main_layout.addWidget(QLabel('Destination'))
		main_layout.addWidget(self.dst)		
		
		self.progress = QProgressBar(self)
		self.progress.setValue(0)	
		main_layout.addWidget(QLabel('KB/sec'))
		main_layout.addWidget(self.kb_sec)		
			
		main_layout.addWidget(QLabel('Progression'))
		main_layout.addWidget(self.progress)
		
		main_layout.addWidget(self.separator())
		
		main_layout.addLayout(self.refreshButtons())

		
		
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
		
	# 	refreshButtons
	def refreshButtons(self):
		
		if not "buttons_layout" in dir(self):
			self.buttons_layout=QVBoxLayout()
		
		self.buttons=[]
		button=None
		self.clearLayout(self.buttons_layout)
		
		# assign unique usb IDs
		usb_drives=Utils.GetUsbDrives()
		for drive, id in usb_drives:
			if not id in self.sensors:
				self.sensors[id]=len(self.sensors)		

			
		if usb_drives:
			
			hlayout=QHBoxLayout()
			self.buttons_layout.addLayout(hlayout)
			
			hlayout.addWidget(QLabel("Dump memory card"))
			
			field_name=QLineEdit()
			field_name.setText("myfield")
			hlayout.addWidget(QLabel('Field name'))
			hlayout.addWidget(field_name)

			for drive, id in usb_drives:
				button=self.createButton('Dump USB {}'.format(drive),callback=lambda : self.dumpMemoryCard(drive, field_name.text(), self.sensors[id]))
				hlayout.addWidget(button)
				self.buttons.append(button)
				
		# google
		if os.path.isfile(CopyFilesToGoogleDrive.settings_file):
			
			hlayout=QHBoxLayout()
			self.buttons_layout.addLayout(hlayout)			
			
			hlayout.addWidget(QLabel("Google Drive"))
			
			button=self.createButton('Upload',callback=lambda: self.copyToCloud(drive=None))
			hlayout.addWidget(button)
			self.buttons.append(button)
			
			# also add the option to copy the data to external USB
			for drive, id in usb_drives:
				button=self.createButton('Upload and copy to {}'.format(drive),callback=lambda : self.copyToCloud(drive=drive))
				hlayout.addWidget(button)
				self.buttons.append(button)
				
		return self.buttons_layout
				
	# createButton
	def createButton(self,text,callback=None):
		ret=QPushButton(text)
		if callback is not None:
			ret.clicked.connect(callback)
		return ret
		
	# onProgress
	def onProgress(self,I,N,src,dst,kb_sec):
		self.progress.setValue(int(100*I/N))
		self.prog.setText("{}/{}".format(I,N))
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
		
		if self.worker.error_message:
			message="Error copying files. Please retry ({})".format(self.worker.error_message)
			log.print(message)
			QMessageBox.about(self, "Error", message)
		else:
			message="Finished syncing files"
			log.print(message)
	
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

	# dumpMemoryCard 
	# NOTE: if you have two memory card for different sensors they will end up in the same directory
	def dumpMemoryCard(self, drive, field_name, num_sensor):
		log.print("*** Dumping usb drive")		
		
		dst_dir=Utils.NormalizePath("{}/{}-{}/sensor{}".format(LOCAL_DIR, T1.strftime("%Y%m%d-%H%M%S"),field_name,num_sensor))
		
		self.setRunning(True)
		src_dir=drive
		
		copier=CompoundCopyFiles()
		copier.instances.append(CopyLocalFiles(dst_dir))
		
		sync=SyncFiles(src_dir,copier=copier)
		
		def onFinished():
			#Utils.EjectUSBDrive(drive)
			#self.refreshButtons()	
			pass
		
		self.runSyncInBackground(sync,finished=onFinished)

	# copyToCloud
	def copyToCloud(self,drive=None):
		log.print("*** Copying file to google drive","and copying to drive {}".format(drive) if drive else "")	
		
		self.setRunning(True)
		
		copier=CompoundCopyFiles()
		
		# first copy to google drive
		copier.instances.append(CopyFilesToGoogleDrive(BUCKET_NAME)) 
		
		# eventually copy to external usb drive
		if drive:
			copier.instances.append(CopyLocalFiles(BACKUP_DIR.format(drive)))
		
		src_dir=LOCAL_DIR
		sync=SyncFiles(src_dir,copier=copier)
		self.runSyncInBackground(sync)


# //////////////////////////////////////////////////////////
if __name__ == "__main__":
	app=QApplication([])
	gui=VisoarMoveDataFromCardWidget()
	gui.show()
	sys.exit(app.exec_())
	
	
	

