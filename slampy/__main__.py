import os, sys, argparse, datetime
from . slam_2d import *


# //////////////////////////////////////////
if __name__ == "__main__":

	# python -m slampy --image-dir D:\GoogleSci\visus_slam\TaylorGrant       --cache-dir D:\visus-slam\cache-dir\TaylorGrant  (Generic)
	# python -m slampy --image-dir D:\GoogleSci\visus_slam\Alfalfa           --cache-dir D:\visus-slam\cache-dir\Alfalfa      (Generic)
	# python -m slampy --image-dir D:\GoogleSci\visus_slam\RedEdge           --cache-dir D:\visus-slam\cache-dir\RedEdge      (micasense)
	# python -m slampy --image-dir D:\GoogleSci\visus_slam\TaylorGrantSmall  --cache-dir D:\visus-slam\cache-dir\TaylorGrantSmall1	
	# python -m slampy --image-dir D:\GoogleSci\visus_slam\TaylorGrantSmall  --cache-dir D:\visus-slam\cache-dir\TaylorGrantSmall2 --plane 1071.61 --calibration "2222.2194 2000.0 1500.0" --telemetry D:/~slam/TaylorGrantSmall/metadata.json
	# python -m slampy --image-dir D:\GoogleSci\visus_slam\TaylorGrantSmall  --cache-dir D:\visus-slam\cache-dir\TaylorGrantSmall3	--physic-box "0.18167907760636232 0.18171277264117514 0.63092731395604973 0.63093683616193741"
	# python -m slampy --image-dir "D:/visus-slam/image-dir/visus-agricultural/Field_Images/Blackadder Farms Ptr/Shape Behind Toris" --cache-dir "D:/visus-slam/cache-dir/visus-agricultural/Field_Images/Blackadder Farms Ptr/Shape Behind Toris" 

	"""
	Example of full 'pipeline' in win32
	
	set name=visus-agricultural/Field_Images/Blackadder Farms Ptr/South of Joes
	rclone -v sync "WasabiDrone:/%name%" "D:/visus-slam/image-dir/%name%"
	python -m slampy --image-dir "D:/visus-slam/image-dir/%name%" --cache-dir "D:/visus-slam/cache-dir/%name%"
	python -m slampy preview "D:/visus-slam/cache-dir/%name%/visus.midx" "D:/visus-slam/cache-dir/%name%/preview.png" 1024
	python -m slampy midx-to-idx --midx "D:/visus-slam/cache-dir/%name%/visus.midx" --idx "D:/visus-slam/idx-dir/%name%/visus.idx"
	python -m slampy preview "D:/visus-slam/idx-dir/%name%/visus.idx" "D:/visus-slam/idx-dir/%name%/visus.png" 1024
	"""
	
	"""
	"/visus-agricultural/Field_Images/Blackadder Farms Ptr/Shape Behind Toris",    ****PROBLEM**** 
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

	action=sys.argv[1] if len(sys.argv)>=2 else ""
	action_args=sys.argv[2:]
		
	# forward to OpenVisus
	if action=="midx-to-idx":
		from OpenVisus.__main__ import MidxToIdx
		MidxToIdx(action_args)
		
	# example: python -m slampy preview /path/to/visus.idx /path/to/preview.png 1024
	elif action=="preview":
		db_filename, img_filename,width = action_args
		print("Got args",repr(sys.argv))
		SaveDatasetPreview(db_filename, img_filename,width=int(width))
		
	else:
		print("Got args",repr(sys.argv))
		parser = argparse.ArgumentParser(description="slam command.")
		
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
		parser.add_argument("--batch" , help="Enable batching", action='store_true') 
		
		# max-images
		parser.add_argument("--max-images" , type=int, help="ilimit number of images for debugging", required=False,default=0)	

		# max-images
		parser.add_argument("--debug-mode" , type=bool, help="debug mode", required=False,default=False)	

		# parse arguments
		args = parser.parse_args(sys.argv[1:])

		Slam2D.Run(
			image_dir=args.image_dir,
			cache_dir=args.cache_dir if args.cache_dir else None,
			telemetry=args.telemetry if args.telemetry else None,
			plane=cdouble(args.plane) if args.plane else None,
			calibration=args.calibration,
			physic_box=BoxNd.fromString(args.physic_box) if args.physic_box else None ,
			batch=args.batch, 
			max_images=args.max_images,
			debug_mode=args.debug_mode
		)

	print("All done")
	sys.exit(0)	

