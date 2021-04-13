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

__log__=None

# ///////////////////////////////////////////////
class LogFile:
	
	# constructor
	def __init__(self,filename):
		global __log__
		__log__=self
		self.filename=filename
		os.makedirs(os.path.dirname(self.filename), exist_ok=True)
		
	# print
	def print(self,*args):
		message=time.strftime("[%Y/%m/%d %H:%M:%S] ") + ' '.join([str(arg) for arg in args])
		print(message)	
		with open(self.filename, 'a+') as f: # Use file to refer to the file object
			f.write(message + '\n')
			
	@staticmethod
	def getLogger():
		global __log__
		if not __log__: 
			raise Exception("please set the log filename")
		return __log__
		

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
	def GetDrives():
		ret = []
		
		if 'darwin' in sys.platform:
			for line in os.listdir('/Volumes'):
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
				if id=='0' or "cd-rom" in description: continue
				ret.append(name)
			
		else:
			#This code might work
			# import usb
			# busses = usb.busses()
			# for bus in busses:
			# 	devices = bus.devices
			# 	for dev in devices:
			# 		print("Device:", dev.filename)
			# 		print("  idVendor: %d (0x%04x)" % (dev.idVendor, dev.idVendor))
			# 		print("  idProduct: %d (0x%04x)" % (dev.idProduct, dev.idProduct))			
			pass
		
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
	
	# ComputeLocalMd5
	@staticmethod
	def ComputeLocalMd5(filename):
		if not os.path.isfile(filename):
			return None
		ret=None
		with open(filename, "rb") as f:
			md5_hash = hashlib.md5()
			md5_hash.update(f.read())
			return md5_hash.hexdigest()		