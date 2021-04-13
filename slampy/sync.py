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


# from VisoarAgExplorer.slampy.utils import *
# from VisoarAgExplorer.slampy.sync import *
from slampy.utils import *
#from slampy.sync import *

"""
=====================================================================================

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

====================================================================================
"""
# 
# basically and from that you extract the info to filla `client_settings.yaml`
from pydrive.auth  import GoogleAuth
from pydrive.drive import GoogleDrive

ThisDir = os.path.dirname(os.path.realpath(__file__))


# //////////////////////////////////////////////////////////	
class SyncLocalToLocal:
	
	# constructor
	def __init__(self,dst_dir):
		self.dst_dir=dst_dir
		self.log=LogFile.getLogger()
	
	# copyFile
	def copyFile(self,src,dst):
		
		dst=os.path.join(self.dst_dir,dst).replace("\\","/")
		
		os.makedirs(os.path.dirname(dst), exist_ok=True) # create parent directory
		
		l1=Utils.ComputeLocalMd5(src)
		l2=Utils.ComputeLocalMd5(dst)
		if l1==l2:
			self.log.print("File {} already on destination. No need to copy again".format(src),"md5",l1)
			return
		
		# copy2 preserve metadata
		shutil.copy2(src, dst)	

		# verify the new data
		l2=Utils.ComputeLocalMd5(dst)
		if l1!=l2:
			raise Exception("MD5 check failed")
			
		self.log.print("SyncLocalToLocal: copied {} file to local {} md5({})".format(src, dst,l1))	
		
		

# //////////////////////////////////////////////////////////
class SyncLocalToGoogleDrive:
	
	settings_file=os.path.join(ThisDir,'client_settings.yaml')
	
	# constructor
	def __init__(self,bucket_name):
		self.bucket_name=bucket_name
		self.auth=GoogleAuth(settings_file=SyncLocalToGoogleDrive.settings_file)
		self.drive=GoogleDrive(self.auth)	
		self.root={'title':'root','id':'root'}
		self.folders={} # caching the folders
		self.log=LogFile.getLogger()

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
			self.log.print("Using directory",name,"id",ret['id'])
		else:
			ret = self.drive.CreateFile({'title' : child, "parents":  [{"id": parent['id']}], 'mimeType' : 'application/vnd.google-apps.folder'})
			ret.Upload()
			self.log.print("Created new directory",name,"id",ret['id'])
			
		self.folders[name]=ret
		return ret
		
	# computeRemoteMd5
	def computeRemoteMd5(self, parent_id,title):
		remote_files=self.drive.ListFile({'q': "'{}' in parents and trashed=false and title='{}'".format(parent_id,title)}).GetList()
		return remote_files[0]['md5Checksum'] if remote_files else None

	# copyFile
	def copyFile(self,src, dst):
		
		dst=(self.bucket_name + "/" + dst).replace("\\","/")
		parent, child =dst.rsplit('/',maxsplit=1)
		parent=self.createFolder(parent)

		l1=Utils.ComputeLocalMd5(src)
		l2=self.computeRemoteMd5(parent['id'],child)
		
		if l1 == l2:
			self.log.print("File {} already on Google drive. No need to copy again md5({})".format(src,l1))
			return 

		file = self.drive.CreateFile({'title': child, 'parents': [{'id': parent['id']}]})
		file.SetContentFile(src)
		file.Upload() 
		
		if file['title'] != child:
			raise Exception("uplod of file failed")
			
		if file['md5Checksum'] !=l1:
			raise Exception("MD5 checksum failed")
			
		self.log.print("SyncLocalToGoogleDrive: uploaded {} file to Google drive md5({}). MD5 check ok".format(src,l1))
	
# //////////////////////////////////////////////////////////
class CleanLocalFiles:
	
	# constructor
	def __init__(self):
		self.log=LogFile.getLogger()
	
	# copyFile
	def copyFile(self,src,dst):
		if os.path.abspath(src)!=os.path.abspath(self.log.filename):
			os.remove(src)

	
# //////////////////////////////////////////////////////////
class CompoundCopyFiles:
	
	# ___init__
	def __init__(self):
		self.instances=[]
		
	# copyFile
	def copyFile(self,src,dst):
		for it in self.instances:
			it.copyFile(src,dst)
	
# //////////////////////////////////////////////////////////
class SyncFiles:
	
	# constructor
	def __init__(self,src_dir,copier=None,progress=None):
		self.src_dir=src_dir
		self.copier=copier
		self.progress=progress
		self.log=LogFile.getLogger()
		
	# list all files in a directory
	def findFiles(self,dir,recursive=True):
		ret=glob.glob(dir + '/**/*', recursive=recursive)
		ret=[Utils.NormalizePath(src) for src in ret if os.path.isfile(src)]
		ret=[filename for filename in ret if not "System Volume Information" in filename]	
		return ret
		
	# run
	def run(self):
		
		self.log.print("Syncing folders")
		self.log.print("source directory", self.src_dir)
		
		t1 = time.time()
		
		nfiles,tot_bytes=0,0
		
		src_files=self.findFiles(self.src_dir)
		
		# make sure it's the last one (otherwise I will lose some logs)
		if self.log.filename in src_files:
			src_files.remove(self.log.filename)
			src_files.append(self.log.filename)
		
		N=len(src_files)
		
		# for all files in src dir only
		for I,src in enumerate(src_files):

			# do not user normalize path
			dst=os.path.relpath(src, self.src_dir).replace("\\","/") 

			file_size=Utils.GetFileSize(src)
			
			self.log.print("%d/%d" % (I,N),"Doing",src,dst,"...")
			self.copier.copyFile(src,dst)

			nfiles+=1
			tot_bytes+=file_size 
			
			kb=tot_bytes/(1024)
			sec=time.time()-t1
			kb_sec=int(kb/sec) if sec else 0
			self.log.print("%d/%d" % (I,N),"Done",src, dst,"{}KB".format(int(file_size/1024)),"{}KB/sec".format(kb_sec),"KB({})".format(kb))
					
			# generator for a workflow
			if self.progress:
				self.progress(I,N, src, dst, kb_sec)
				
			time.sleep(0)
					
		# try to remove all empty subdirectories 
		for sub in [os.path.join(self.src_dir,it) for it in os.listdir(self.src_dir)]:
			if os.path.isdir(sub) and not self.findFiles(sub):
				print("Removing empty directory",sub)
				shutil.rmtree(sub, ignore_errors=True)
			
		kb=int(tot_bytes/1024)
		sec=time.time()-t1
		kb_sec=int(kb/sec) if sec else 0
		self.log.print("All done in","%.2fsec" % sec, "{}KB".format(kb),"{}KB/sec".format(kb_sec))


