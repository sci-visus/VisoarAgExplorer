import cv2
import numpy
import random
import threading
import time
import math
import pickle

from OpenVisus                import *

from slampy.extract_keypoints import *
from slampy.find_matches      import *
from slampy.image_utils       import *


# ////////////////////////////////////////////////////////////////////////
class MultiSensorAlignment:

	# constructor
	def __init__(self, multi, altitude, calibration, cache_dir):
		self.min_keypoints = 3000
		self.max_keypoints = 6000
		self.anms = 0
		self.ratio_check = 0.8
		self.max_reproj_error = 0.01
		self.ba_tolerance = 0.005
		self.warp_matrices = None
		self.cropped_dimensions = None
		self.calibration = calibration
		self.altitude = altitude
		cached_filename=cache_dir+"/multi_alignment.info"

		if not self.openCache(cached_filename):
			self.solveSlam(multi,cache_dir+"/multi_alignment.midx")
			self.debugAlignment(multi,cache_dir+"/multi_alignment.%04d.%04d.tif")
			self.saveCache(cached_filename)

	# solveSlam
	def solveSlam(self, multi, midx_filename):

		for I,single in enumerate(multi):

			# take only the first channel of the image 
			if len(single.shape)==3: single=single[:,:,0]

			# convert to uint8 to make things comparable
			single=ConvertImageToUint8(single)

			# don't rememeber but I think micasense is doing something similar
			single=cv2.equalizeHist(single)

			multi[I]=single

		slam=Slam()
		slam.url=midx_filename
		slam.width =multi[0].shape[1]
		slam.height=multi[0].shape[0]
		slam.dtype=DType.fromString("uint8") # note the images have been converted to uint8
		slam.calibration=self.calibration

		extractor=ExtractKeyPoints(self.min_keypoints,self.max_keypoints,self.anms)

		nsensors=len(multi)
		for I in range(nsensors):
			camera = Camera()
			camera.id = I
			camera.bFixed=True if I==0 else False
			camera.pose=Pose.lookingDown(Point3d(0,0,self.altitude))
			slam.addCamera(camera)

			# work in full dim energy
			energy=multi[I] 
			(keypoints,descriptors)=extractor.doExtract(energy) 

			camera.keypoints.reserve(len(keypoints))
			for k in keypoints:
				camera.keypoints.push_back(KeyPoint(k.pt[0], k.pt[1], k.size, k.angle, k.response, k.octave, k.class_id))
			camera.descriptors=Array.fromNumPy(descriptors,TargetDim=2)

			# every camera is local to any other local camera
			for J in range(0,I-1):
				c1,c2=slam.cameras[I],slam.cameras[J]
				c1.addLocalCamera(c2)

		t2 = Time.now()
		num_matches=0
		for camera2 in slam.cameras:
			for camera1 in camera2.getAllLocalCameras():
				if camera1.id < camera2.id:
					matches,H21,err=FindMatches(slam.width,slam.height,
						camera1.id,[(k.x, k.y) for k in camera1.keypoints],Array.toNumPy(camera1.descriptors), 
						camera2.id,[(k.x, k.y) for k in camera2.keypoints],Array.toNumPy(camera2.descriptors),
						self.max_reproj_error * slam.width, self.ratio_check)
					matches=[] if err else [Match(match.queryIdx,match.trainIdx, match.imgIdx, match.distance) for match in matches]
					camera2.getEdge(camera1).setMatches(matches,err if err else str(len(matches)))
		print("Found num_matches(", num_matches, ") matches in ", t2.elapsedMsec() ,"msec")

		# slam.removeDisconnectedCameras() 
		slam.bundleAdjustment(self.ba_tolerance)

		# find cropped dimensions (i.e. inner rectangle)
		BOX=None
		for C in range(nsensors):	
			quad=Quad(slam.cameras[C].homography,Quad(multi[C].shape[1],multi[C].shape[0]))
			p0,p1,p2,p3=quad.getPoint(0),quad.getPoint(1),quad.getPoint(2),quad.getPoint(3)
			x1,x2 = float(max(p3[0],p0[0])),float(min(p1[0],p2[0]))
			y1,y2 = float(max(p0[1],p1[1])),float(min(p2[1],p3[1]))
			box=BoxNd(PointNd(x1,y1),PointNd(x2,y2))
			BOX=box if BOX is None else BOX.getIntersection(box)

		self.cropped_dimensions=[
			int(math.ceil(BOX.p1[0])), 
			int(math.ceil(BOX.p1[1])), 
			int(math.floor(BOX.size()[0])), 
			int(math.floor(BOX.size()[1]))]	

		print("cropped_dimensions", self.cropped_dimensions,"width",self.cropped_dimensions[2], "height",self.cropped_dimensions[3])

		# warp matrices
		self.warp_matrices=[numpy.matmul(
			MatrixToNumPy(Matrix(1.0,0.0,float(-self.cropped_dimensions[0]),  0.0,1.0,float(-self.cropped_dimensions[1]),  0.0,0.0,1.0)),
			MatrixToNumPy(H)) for H in [slam.cameras[C].homography for C in range(nsensors)] ]
		print("warp_matrices", self.warp_matrices)

	# openCache
	def openCache(self, filename):
		try:
			d=pickle.load(open(filename,"rb"))
			self.cropped_dimensions=d["cropped_dimensions"]
			self.warp_matrices=d["warp_matrices"]
			print("Loaded multi alignment from cache")
			print("\tcropped_dimensions",self.cropped_dimensions)
			print("\twarp_matrices",self.warp_matrices)
			return True
		except:
			return False

	# saveCache
	def saveCache(self, filename):
		os.makedirs(os.path.dirname(filename), exist_ok=True)
		pickle.dump({
			"cropped_dimensions": self.cropped_dimensions,
			"warp_matrices": self.warp_matrices}, 
			open(filename,"wb"))	

	# warpPerspective
	def warpPerspective(self,single,C):
		W,H=self.cropped_dimensions[2],self.cropped_dimensions[3]
		return cv2.warpPerspective(single, self.warp_matrices[C], (W,H), flags=cv2.INTER_LANCZOS4)

	# debugAlignment
	def debugAlignment(self,multi,filename_template):
		nsensors=len(multi)
		for I in range(nsensors):
			for J in range(I+1,nsensors):
				SaveUint8Image(
					filename_template % (I,J) ,
					InterleaveChannels([self.warpPerspective(multi[I], I),self.warpPerspective(multi[J], J)]))	

	# doAlign
	def doAlign(self,  multi):
		return [self.warpPerspective(multi[C],C) for C in range(len(multi))]

