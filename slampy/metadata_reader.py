import json
import subprocess
import os,platform

WIN32=platform.system()=="Windows" or platform.system()=="win32"
APPLE=platform.system()=="Darwin"

__this_dir__= os.path.dirname(os.path.abspath(__file__))
exiftool_command = os.path.join(__this_dir__,"exiftool.exe") if WIN32 else "exiftool"

# micasense source code need to find exiftool
os.environ['exiftoolpath']=exiftool_command

# ///////////////////////////////////////////////////////////////
class MetadataReader(object):
   
   # constructor
	def __init__(self):
		cmd=[exiftool_command, "-stay_open", "True",  "-@", "-","-common_args", "-G", "-n"]
		print(" ".join(cmd))
		self.process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,stderr=subprocess.DEVNULL)
		
	# close
	def close(self):
		self.process.stdin.write(b"-stay_open\nFalse\n")
		self.process.stdin.flush()
		self.process.communicate()
		del self.process

	# readMetadata
	def readMetadata(self,filename):
		
		print("Reading metadata",filename)
		self.process.stdin.write(b"-j\n" + filename.encode() + b"\n-execute\n")
		self.process.stdin.flush()	
		
		output = b""
		while not output.strip().endswith(b"{ready}"):
			output+=os.read(self.process.stdout.fileno(), 4096)
		output=output.strip()[:-len(b"{ready}")].decode("utf-8")
			
		ret=json.loads(output)[0]
		return ret

