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

from pydrive.auth  import GoogleAuth
from pydrive.drive import GoogleDrive

T1=datetime.datetime.now() 
LOCAL_DIR="c:/visoar_files"
BUCKET_NAME="/visoar_files"

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
		
		def getInfo(key):
			output,err = subprocess.Popen('wmic logicaldisk get {}'.format(key), shell=True, stdout=subprocess.PIPE).communicate()
			output=output.decode("utf-8").strip()
			ret=[]
			for line in output.split('\n')[1:]:
				ret.append(line.strip())
			print(ret)
			return ret
				
		fixed,external=[],[]
		names=getInfo("name")
		descriptions=getInfo("description");descriptions=descriptions + ([''] * (len(names)-len(descriptions)))
		ids=getInfo("VolumeSerialNumber");ids=ids + (['0'] * (len(names)-len(ids)))
		print(names,descriptions,ids)
		
		for name,description,id in zip(names,descriptions,ids):
			description=description.lower()
			print(name,description,id)
			if "local fixed" in description or "cd-rom" in description:
				fixed.append((name,id))
			else:
				external.append((name,id))
		log.print("Fixed drives",fixed)
		log.print("External drives",external)
		return external	
	
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
	def __init__(self):
		pass
	
	# copyFile
	def copyFile(self,src,dst,use_checksum=True):
		os.makedirs(os.path.dirname(dst), exist_ok=True) # create parent directory
		if use_checksum:
			l1=Utils.ComputeMd5(src)
			l2=Utils.ComputeMd5(dst)
			if l1==l2:
				log.print("File {} already on destination. No need to copy again".format(src),"md5",l1)
				return True
		shutil.copy2(src, dst)	# copy2 preserve metadata
		log.print("Copied {} file to local {} md5({})".format(src, dst,l1))	
		return True		
		
	# removeFile
	def removeFile(self,src):
		os.remove(src)
		
# //////////////////////////////////////////////////////////
class CopyFilesToGoogleDrive:
	
	settings_file='client_settings.yaml'
	
	# constructor
	def __init__(self):
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
	def copyFile(self,src,dst):

		parent, child =dst.rsplit('/',maxsplit=1)
		parent=self.createFolder(parent)

		l1=Utils.ComputeMd5(src)
		l2=self.computeMd5(parent['id'],child)
		
		if l1 == l2:
			log.print("File {} already on Google drive. No need to copy again md5({})".format(src,l1))
			return True

		file = self.drive.CreateFile({'title': child, 'parents': [{'id': parent['id']}]})
		file.SetContentFile(src)
		file.Upload() # this should raise an error?
		log.print("Uploaded {} file to Google drive md5({})".format(src,l1))
		return True
	
	
	# removeFile
	def removeFile(self,src):
		os.remove(src)	
	
# //////////////////////////////////////////////////////////
class SyncFiles:
	
	# constructor
	def __init__(self,src_dir,dst_dir,copier=None,purge=False, progress=None):
		self.src_dir=src_dir
		self.dst_dir=dst_dir
		self.copier=copier
		self.purge=purge
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
		log.print("target directory", self.dst_dir)
		
		t1 = time.time()
		
		nfiles,tot_bytes=0,0
		
		dst_files=[]
		src_files=self.findFiles(self.src_dir)
		
		# make sure it's the last one (otherwise I will lose some logs)
		if log.filename in src_files:
			src_files.remove(log.filename)
			src_files.append(log.filename)
		
		N=len(src_files)
		
		# for all files in src dir only
		for I,src in enumerate(src_files):

			# do not user normalize path
			dst=self.dst_dir + "/" + os.path.relpath(src, self.src_dir)
			dst=dst.replace("\\","/") 
			
			file_size=Utils.GetFileSize(src)
			
			log.print("%d/%d" % (I,N),"Doing",src,dst,"...")
			self.copier.copyFile(src,dst)

			nfiles+=1
			tot_bytes+=file_size 
			dst_files.append(dst)
			
			kb=tot_bytes/(1024)
			sec=time.time()-t1
			kb_sec=int(kb/sec) if sec else 0
			log.print("%d/%d" % (I,N),"Done",src,dst,"{}KB".format(int(file_size/1024)),"{}KB/sec".format(kb_sec),"KB({})".format(kb))
					
			# generator for a workflow
			if self.progress:
				self.progress(I,N, src, dst, kb_sec)
			
			# purge source file only if equals
			if self.purge:
				self.copier.removeFile(src)
				log.print("%d/%d" % (I,N),"rm",src)
				
			time.sleep(0)
					
		# try to remove all empty subdirectories
		if self.purge and not self.findFiles(src_dir):
			for it in os.listdir(src_dir):
				shutil.rmtree(os.path.join(src_dir, it), ignore_errors=True)
			
		kb=int(tot_bytes/1024)
		sec=time.time()-t1
		kb_sec=int(kb/sec) if sec else 0
		log.print("All done in","%.2fsec" % sec, "{}KB".format(kb),"{}KB/sec".format(kb_sec))
		return nfiles,tot_bytes,dst_files


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
		self.resize(600,200)
		self.sensors={}
		self.createGui()
		
	#  createGui
	def createGui(self):
		
		main_layout = QVBoxLayout()
		
		
		self.field_name=QLineEdit()
		self.field_name.setText("myfield")
		
		self.prog=QLineEdit();self.prog.setEnabled(False)
		self.src=QLineEdit();self.src.setEnabled(False)
		self.dst=QLineEdit();self.dst.setEnabled(False)
		self.kb_sec=QLineEdit();self.kb_sec.setEnabled(False)
		
		self.progress = QProgressBar(self)
		self.progress.setValue(0)	
			
		main_layout.addWidget(QLabel('Field name'))
		main_layout.addWidget(self.field_name)
		main_layout.addWidget(QLabel('Current'))
		main_layout.addWidget(self.prog)
		main_layout.addWidget(QLabel('Source'))
		main_layout.addWidget(self.src)
		main_layout.addWidget(QLabel('Destination'))
		main_layout.addWidget(self.dst)
		main_layout.addWidget(QLabel('KB/sec'))
		main_layout.addWidget(self.kb_sec)
		main_layout.addWidget(QLabel('Progression'))
		main_layout.addWidget(self.progress)
		
		self.buttons_layout=QHBoxLayout()
		main_layout.addLayout(self.buttons_layout)
		self.setLayout(main_layout)
		
		self.refreshButtons()
		
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
		
		self.buttons=[]
		self.clearLayout(self.buttons_layout)
		
		for drive, id in Utils.GetUsbDrives():
			
			if not id in self.sensors:
				self.sensors[id]=len(self.sensors)
				
			button=self.createButton('Dump USB {}'.format(drive),callback=lambda : self.copyLocalFiles(drive, self.sensors[id]))
			self.buttons_layout.addWidget(button)
			self.buttons.append(button)
				
		if os.path.isfile(CopyFilesToGoogleDrive.settings_file):
			button=self.createButton('Upload to gdrive',callback=self.copyFilesToGoogleDrive)
			self.buttons_layout.addWidget(button)
		self.buttons.append(button)
			
		button=self.createButton('Refresh',callback=self.refreshButtons)
		self.buttons_layout.addWidget(button)
		self.buttons.append(button)
		
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
			message="Finished Dumping memory card"
			log.print(message)

	# runSyncInBackground
	def runSyncInBackground(self,sync):
		self.thread = QThread()
		self.worker = MyWorker(sync)
		self.worker.moveToThread(self.thread)
		self.thread.started.connect(self.worker.run)
		self.worker.finished.connect(self.thread.quit)
		self.worker.finished.connect(self.worker.deleteLater)
		self.thread.finished.connect(self.thread.deleteLater)
		self.worker.finished.connect(self.threadFinished)
		self.worker.progress.connect(self.onProgress)
		self.thread.start()
		

	# copyLocalFiles 
	# NOTE: if you have two memory card for different sensors they will end up in the same directory
	def copyLocalFiles(self, drive, num_sensor):
		log.print("*** Dumping usb drive")		
		
		dst_dir=LOCAL_DIR
		dst_dir+='/{}'.format(T1.strftime("%Y%m%d-%H%M%S"))
		if len(self.field_name.text()):
			dst_dir+='-{}'.format(self.field_name.text())
		dst_dir+="/sensor{}".format(num_sensor)
		dst_dir=Utils.NormalizePath(dst_dir) 		
		
		self.setRunning(True)
		sync=SyncFiles(drive,dst_dir,copier=CopyLocalFiles(), purge=False)
		self.runSyncInBackground(sync)

	# copyFilesToGoogleDrive
	def copyFilesToGoogleDrive(self):
		log.print("*** Copying file to google drive")	
		src_dir=LOCAL_DIR
		dst_dir=BUCKET_NAME
		self.setRunning(True)
		sync=SyncFiles(src_dir,dst_dir,copier=CopyFilesToGoogleDrive(), purge=False)
		self.runSyncInBackground(sync)


# //////////////////////////////////////////////////////////
if __name__ == "__main__":
	app=QApplication([])
	gui=VisoarMoveDataFromCardWidget()
	gui.show()
	sys.exit(app.exec_())
	
	
	

