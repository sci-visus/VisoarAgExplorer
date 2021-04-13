import os, sys, argparse, datetime
from . slam_2d import *

# ////////////////////////////////////////////////
def Main(args):

	# -m slampy --directory D:\GoogleSci\visus_slam\TaylorGrant (Generic)
	# -m slampy --directory D:\GoogleSci\visus_slam\Alfalfa     (Generic)
	# -m slampy --directory D:\GoogleSci\visus_slam\RedEdge     (micasense)
	# -m slampy --directory "D:\GoogleSci\visus_slam\Agricultural_image_collections\AggieAir uav Micasense example\test" (micasense)		
	# -m slampy --directory D:\GoogleSci\visus_slam\TaylorGrantSmall --cache D:\~slam\TaylorGrantSmall	
	# -m slampy --directory D:\GoogleSci\visus_slam\TaylorGrantSmall --cache D:\~slam\TaylorGrantSmall --plane 1071.61 --calibration "2222.2194 2000.0 1500.0" --telemetry D:/~slam/TaylorGrantSmall/metadata.json
	# -m slampy --directory D:\GoogleSci\visus_slam\TaylorGrantSmall --cache D:\~slam\TaylorGrantSmall	--physic-box "0.18167907760636232 0.18171277264117514 0.63092731395604973 0.63093683616193741"

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
	
	# enable/disable batch
	parser.add_argument("--batch" , type=bool, help="Enable batching", required=False,default=False) 

	# parse arguments
	args = parser.parse_args(args[1:])
	image_dir=args.directory
	cache_dir=args.cache_dir if args.cache_dir else None
	telemetry=args.telemetry if args.telemetry else None
	plane=cdouble(args.plane) if args.plane else None
	physic_box=BoxNd.fromString(args.physic_box) if args.physic_box else None 
	batch=args.batch

	calibration=None
	if args.calibration:
		f,cx,cy=[cdouble(it) for it in args.calibration.split()]
		calibration=Calibration(f,cx,cy)

	print("Running slam:")
	print("\t","image_dir", repr(image_dir))
	print("\t","cache_dir", repr(cache_dir))
	print("\t","telemetry", repr(telemetry))
	print("\t","plane", repr(plane))
	print("\t","calibration", (calibration.f,calibration.cx,calibration.cy) if calibration else None)
	print("\t","physic_box", physic_box.toString() if physic_box else None)		
	print("\t","batch", batch)		

	# since I'm writing data serially I can disable locks
	os.environ["VISUS_DISABLE_WRITE_LOCK"]="1"
	
	gui=None
	if not batch:
		from . slam_2d_gui import Slam2DWindow
		gui=Slam2DWindow()
		
		if not image_dir:
			from PyQt5.QtWidgets import QFileDialog
			image_dir = QFileDialog.getExistingDirectory(None, "Choose directory...","",QFileDialog.ShowDirsOnly) 

	if not image_dir: 
		print("Specify an image directory")
		sys.exit(-1)
		
	slam = Slam2D()
	slam.setImageDirectory(image_dir,  cache_dir= cache_dir, telemetry=cache_dir, plane=plane, calibration=calibration, physic_box=physic_box) 	
		
	if batch:
		slam.run()
	else:
		gui.run(slam)
	
	print("All done")
	sys.exit(0)	


# //////////////////////////////////////////
if __name__ == "__main__":
	Main(sys.argv)