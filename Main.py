import os,sys,platform,subprocess,glob
from VisoarAgExplorer 				import *

from OpenVisus                        import *
from OpenVisus.gui                    import *

from PyQt5           import QtCore 
from PyQt5.QtWidgets import *


# ////////////////////////////////////////////////////////////////////////////////////////////
def GetArg(name,default_value=""):

	for I in range(0,len(sys.argv)):
		if sys.argv[I]==name:
			ret=sys.argv[I+1]
			sys.argv=sys.argv[0:I] + sys.argv[I+2:]
			return ret
	return default_value


# //////////////////////////////////////////////////////////////////////////////
class Logger(QtCore.QObject):

	"""Redirects console output to text widget."""
	my_signal = QtCore.pyqtSignal(str)

	# constructor
	def __init__(self, terminal=None, filename="", qt_callback=None):
		super().__init__()
		self.terminal=terminal
		self.log=open(filename,'w')
		self.my_signal.connect(qt_callback)

	# write
	def write(self, message):
		message=message.replace("\n", "\n" + str(datetime.datetime.now())[0:-7] + " ")
		self.terminal.write(message)
		self.log.write(message)
		self.my_signal.emit(str(message))

	# flush
	def flush(self):
		self.terminal.flush()
		self.log.flush()


# ////////////////////////////////////////////////////////////////////////////////////////////
class ExceptionHandler(QtCore.QObject):

	# __init__
	def __init__(self):
		super(ExceptionHandler, self).__init__()
		sys.__excepthook__ = sys.excepthook
		sys.excepthook = self.handler

	# handler
	def handler(self, exctype, value, traceback):
		sys.stdout=sys.__stdout__
		sys.stderr=sys.__stderr__
		sys.excepthook=sys.__excepthook__
		sys.excepthook(exctype, value, traceback)

# ////////////////////////////////////////////////////////////////////////////////////////////
def Main():
	
	# set PYTHONPATH=D:\projects\OpenVisus\build\RelWithDebInfo
	# example: -m OpenVisus slam    "D:\GoogleSci\visus_slam\TaylorGrant"
	# example: -m OpenVisus slam3d  "D:\GoogleSci\visus_dataset\male\RAW\Fullcolor\fullbody"

	SetCommandLine("__main__")
	app = QApplication(sys.argv)
	GuiModule.attach()  

	# since I'm writing data serially I can disable locks
	os.environ["VISUS_DISABLE_WRITE_LOCK"]="1"
	
	ShowSplash()
	
	args=sys.argv
	if args[1]=="VisoarAgExplorer":
		win=VisoarAgExplorer()
		

	else:
		raise Exception("internal error")

	#win.resize(1280,1024)
	#win.show()
	win.showMaximized()

	_stdout = sys.stdout
	_stderr = sys.stderr

	logger=Logger(terminal=sys.stdout, filename="~visusslam.log", qt_callback=win.printLog)

	sys.stdout = logger
	sys.stderr = logger

	if len(args)==3:
		win.setCurrentDir(args[2])
	else:
		win.chooseDirectory()

	exception_handler = ExceptionHandler()

	HideSplash()
	print("!!!HERE")
	app.exec()

	sys.stdout = _stdout
	sys.stderr = _stderr
	GuiModule.detach()	
	
	


