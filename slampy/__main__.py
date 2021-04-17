import os, sys, argparse, datetime
from . slam_2d import *

# //////////////////////////////////////////
if __name__ == "__main__":

	# -m slampy --image-dir D:\GoogleSci\visus_slam\TaylorGrant (Generic)
	# -m slampy --image-dir D:\GoogleSci\visus_slam\Alfalfa     (Generic)
	# -m slampy --image-dir D:\GoogleSci\visus_slam\RedEdge     (micasense)
	# -m slampy --image-dir "D:\GoogleSci\visus_slam\Agricultural_image_collections\AggieAir uav Micasense example\test" (micasense)		
	# -m slampy --image-dir D:\GoogleSci\visus_slam\TaylorGrantSmall --cache D:\~slam\TaylorGrantSmall	
	# -m slampy --image-dir D:\GoogleSci\visus_slam\TaylorGrantSmall --cache D:\~slam\TaylorGrantSmall --plane 1071.61 --calibration "2222.2194 2000.0 1500.0" --telemetry D:/~slam/TaylorGrantSmall/metadata.json
	# -m slampy --image-dir D:\GoogleSci\visus_slam\TaylorGrantSmall --cache D:\~slam\TaylorGrantSmall	--physic-box "0.18167907760636232 0.18171277264117514 0.63092731395604973 0.63093683616193741"

	# set name=/visus-agricultural/Field_Images/Blackadder Farms Ptr/Sams 6.24.20
	# set PYTHONPATH=build\RelWithDebInfo;.;.\VisoarAgExplorer
	# python -m slampy --remote-dir "GoogleDrone:%name%" --image-dir "D:/visus-slam/image-dir%name%" --cache-dir "D:/visus-slam/cache-dir%name%" --idx-filename "D:/visus-slam/idx-dir%name%/visus.idx"

	"""
	"/visus-agricultural/Field_Images/Blackadder Farms Ptr/Shape Behind Toris",
	"/visus-agricultural/Field_Images/Blackadder Farms Ptr/South of Joes",
	"/visus-agricultural/Field_Images/Bobby Tinsley/Ferrel, Kell 10.14.20 10.15.20",
	"/visus-agricultural/Field_Images/Cap Phillips/Digmans",
	"/visus-agricultural/Field_Images/David Schug/6-12-20 Branch 50, New Ground",
	"/visus-agricultural/Field_Images/David Schug/6-12-20 Shop 26, 8",
	"/visus-agricultural/Field_Images/Moody Farms/#10 8.25.20 2",
	"/visus-agricultural/Field_Images/Moody Farms/#12 8.25.20 2",
	"/visus-agricultural/Field_Images/Moody Farms/#19 8.25.20",
	"/visus-agricultural/Field_Images/Terry Grimes/Radar, D11,D12 11.19.20",
	"/visus-agricultural/Field_Images/Todd Cullen/56 East 30 6.24.20",
	"/visus-agricultural/Field_Images/Todd Cullen/James 41 6.17.20",
	"/visus-agricultural/Field_Images/W&W Farms/106 9.10.20"
	"""

	print("Got args",repr(sys.argv))

	parser = argparse.ArgumentParser(description="slam command.")
	
	# remote directory
	parser.add_argument("--remote-dir",   type=str, help="Directory of the remote images (to rclone sync)", required=False,default="")
			
	# image directory
	parser.add_argument("--image-dir", "--directory", type=str, help="Directory of the source images", required=False,default="")
	
	# cache dir
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
	
	# save idx
	parser.add_argument("--idx-filename" , type=str, help="idx filename", required=False,default="")

	# parse arguments
	args = parser.parse_args(sys.argv[1:])

	# since I'm writing data serially I can disable locks
	os.environ["VISUS_DISABLE_WRITE_LOCK"]="1"
	
	Slam2D.Run(
		remote_dir=args.remote_dir,
		image_dir=args.image_dir,
		cache_dir=args.cache_dir if args.cache_dir else None,
		telemetry=args.telemetry if args.telemetry else None,
		plane=cdouble(args.plane) if args.plane else None,
		calibration=args.calibration,
		physic_box=BoxNd.fromString(args.physic_box) if args.physic_box else None ,
		batch=args.batch, 
		idx_filename=args.idx_filename
	)

	print("All done")
	sys.exit(0)	

