import os, sys, argparse

from slampy.slam_2d import Slam2DWindow
from slampy.gui_utils import *
import datetime

# //////////////////////////////////////////////////////////////////////////////
class RedirectLog(QtCore.QObject):

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



# ////////////////////////////////////////////////
def Main(args):

	parser = argparse.ArgumentParser(description="slam command.")
	parser.add_argument("--directory",   type=str, help="Directory of the source images", required=False,default="")
	parser.add_argument("--cache-dir",   type=str, help="Directory for generated files" , required=False,default="")

	# if you already know the probjecting plane
	parser.add_argument("--plane",       type=str, help="Projecting plane", required=False,default="")

	# If the user knows and specify the calibration from command line
	parser.add_argument("--calibration", type=str, help="Camera calibration", required=False,default="")

	# To force the telemetry from a JSON file (note VisusSlam save a sequence telemetry to a JSON file so you can reuse it)
	parser.add_argument("--telemetry"  , type=str, help="Telemetry file for lat,lon,alt,yaw", required=False, default="")

	# To force the physic box to be the same of another sequence
	# Example: --physic-box 'x1 x2 y1 y2' (i.e. interleaved).
	parser.add_argument("--physic-box" , type=str, help="Physic box of the MIDX", required=False,default=None) 

	args = parser.parse_args(args[1:])


	# since I'm writing data serially I can disable locks
	os.environ["VISUS_DISABLE_WRITE_LOCK"]="1"
	ShowSplash()

	# -m slampy --directory D:\GoogleSci\visus_slam\TaylorGrant (Generic)
	# -m slampy --directory D:\GoogleSci\visus_slam\Alfalfa     (Generic)
	# -m slampy --directory D:\GoogleSci\visus_slam\RedEdge     (micasense)
	# -m slampy --directory "D:\GoogleSci\visus_slam\Agricultural_image_collections\AggieAir uav Micasense example\test" (micasense)		
	# -m slampy --directory D:\GoogleSci\visus_slam\TaylorGrantSmall --cache D:\~slam\TaylorGrantSmall	
	# -m slampy --directory D:\GoogleSci\visus_slam\TaylorGrantSmall --cache D:\~slam\TaylorGrantSmall --plane 1071.61 --calibration "2222.2194 2000.0 1500.0" --telemetry D:/~slam/TaylorGrantSmall/metadata.json
	# -m slampy --directory D:\GoogleSci\visus_slam\TaylorGrantSmall --cache D:\~slam\TaylorGrantSmall	--physic-box "0.18167907760636232 0.18171277264117514 0.63092731395604973 0.63093683616193741"
	win=Slam2DWindow()

	redirect_log=RedirectLog()
	redirect_log.setCallback(win.printLog)
	win.showMaximized()

	# parse arguments
	image_directory=args.directory
	cache_dir=args.cache_dir if args.cache_dir else None
	telemetry=args.telemetry if args.telemetry else None
	plane=cdouble(args.plane) if args.plane else None
	physic_box=BoxNd.fromString(args.physic_box) if args.physic_box else None 

	calibration=None
	if args.calibration:
		f,cx,cy=[cdouble(it) for it in args.calibration.split()]
		calibration=Calibration(f,cx,cy)

	print("Running slam:")
	print("   image_directory", repr(image_directory))
	print("   cache_dir", repr(cache_dir))
	print("   telemetry", repr(telemetry))
	print("   plane", repr(plane))
	print("   calibration", (calibration.f,calibration.cx,calibration.cy) if calibration else None)
	print("   physic_box", physic_box.toString() if physic_box else None)

	win.setImageDirectory(
		image_directory, 
		cache_dir= cache_dir, 
		telemetry=cache_dir, 
		plane=plane, 
		calibration=calibration,
		physic_box=physic_box) 

	HideSplash()
	QApplication.instance().exec()
	print("All done")
	sys.exit(0)	


# //////////////////////////////////////////
if __name__ == "__main__":
	Main(sys.argv)