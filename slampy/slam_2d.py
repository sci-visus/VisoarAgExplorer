import sys,os,platform,subprocess,glob,datetime
import cv2
import numpy
import random
import threading
import time

from OpenVisus import *
from OpenVisus.__main__ import MidxToIdx

from slampy.extract_keypoints import *
from slampy.google_maps       import *
from slampy.gps_utils         import *
from slampy.find_matches      import *
from slampy.image_provider    import *
from slampy.image_utils       import *


from . image_provider_sequoia   import ImageProviderSequoia
from . image_provider_lumenera  import ImageProviderLumenera
from . image_provider_micasense import ImageProviderRedEdge
from . image_provider_generic   import ImageProviderGeneric

# ///////////////////////////////////////////////////////////////////
def ComposeImage(v, axis):
		H = [single.shape[0] for single in v]
		W = [single.shape[1] for single in v]
		W,H=[(sum(W),max(H)),(max(W), sum(H))][axis]
		shape=list(v[0].shape)
		shape[0],shape[1]=H,W
		ret=numpy.zeros(shape=shape,dtype=v[0].dtype)
		cur=[0,0]
		for single in v:
			H,W=single.shape[0],single.shape[1]
			ret[cur[1]:cur[1]+H,cur[0]:cur[0]+W,:]=single
			cur[axis]+=[W,H][axis]
		return ret

# //////////////////////////////////////////
def SavePreview(db_filename, img_filename,width=1024):
	db=LoadDataset(db_filename)
	maxh=db.getMaxResolution()
	logic_box=db.getLogicBox()
	logic_size=db.getLogicSize()
	height=int(width*(logic_size[1]/logic_size[0]))
	tot_pixels=logic_size[0]*logic_size[1]
	deltah=int(math.log2(tot_pixels/(width*height)))
	data=db.read(logic_box=db.getLogicBox(),max_resolution=maxh-deltah)
	SaveImage(img_filename,data)
	

# ///////////////////////////////////////////////////////////////////
def FindImages(image_dir):
	ret=[]
	for filename in glob.glob(os.path.join(image_dir,"**/*.*"),recursive=True):
		if not os.path.splitext(filename)[1].lower() in ('.jpg','.png','.tif','.bmp'): continue # look for extension, must be an image
		if "~" in filename: continue # skip temporary files
		if "VisusSlamFiles" in filename: continue # default is cache_dir is indie image_dir
		print("Found image",len(ret),filename)
		ret.append(filename)

	if not ret:
		raise Exception("Cannot find any image")
	
	return ret
	
# ///////////////////////////////////////////////////////////////////
def GuessProvider(filename):
	# I need to guess what model is the drone (I use the metadata for that. see all CreateImageProviderInstance methods)
	# try with some images in the middle (more probability of taking the flight images)
	
	reader=MetadataReader()
	metadata=reader.readMetadata(filename)
	reader.close()

	print("Trying to create provider from metatada")
	acc=[]
	for key,value in metadata.items():
		print("\t",key,"=",value)
		acc.append(str(value).lower())
		
	exif_make =str(metadata["EXIF:Make"]).lower()  if "EXIF:Make"  in metadata else ""
	exif_model=str(metadata["EXIF:Model"]).lower() if "EXIF:Model" in metadata else ""
	
	if "sequoia" in exif_make or "sequoia" in exif_model:
		print("Setting Sequoia provider")
		return ImageProviderSequoia()
		
	if "lumenera" in exif_model or "lumenera" in exif_make:
		print("Setting Lumenera provider")
		return ImageProviderLumenera()		
		
	if "rededge" in " ".join(acc) or "micasense" in " ".join(acc):
		print("Setting micasense provider")
		return ImageProviderRedEdge()

	print("Setting generic provider")
	return ImageProviderGeneric()
		

# ///////////////////////////////////////////////////////////////////
class Slam2D(Slam):

	# constructor
	def __init__(self):

		super(Slam2D,self).__init__()

		self.width              = 0
		self.height             = 0
		self.dtype              = DType()
		self.calibration        = Calibration()
		self.image_dir          = ""
		self.cache_dir          = ""

		self.debug_mode         = False # True
		self.energy_size        = 1280 
		self.min_num_keypoints  = 3000
		self.max_num_keypoints  = 6000
		self.anms               = 1300
		self.max_reproj_error   = 0.01 
		self.ratio_check        = 0.8
		self.calibration.bFixed = False 
		self.ba_tolerance       = 0.005

		self.images             = []
		self.extractor          = None

		# you can override using a physic_box from another sequence
		self.physic_box         = None 

		self.enable_svg              = True
		self.enable_color_matching   = False
		self.do_bundle_adjustment    = True
		
	# setImageDirectory
	def setImageDirectory(self, image_dir, cache_dir=None, telemetry=None, plane=None, calibration=None, physic_box=None):
		
		self.image_dir=image_dir
		
		print("Finding images in",image_dir)
		images=FindImages(image_dir)
		# images=images[0:10]
		
		cache_dir=cache_dir if cache_dir else os.path.abspath(os.path.join(self.image_dir,"./VisusSlamFiles"))
		self.cache_dir=cache_dir
		TryRemoveFiles(self.cache_dir+'/~*')
		os.makedirs(self.cache_dir,exist_ok=True)
		
		self.provider=GuessProvider(images[int(max(len(images)/2-1,0))])
		self.provider.telemetry=telemetry
		self.provider.plane=plane
		self.provider.image_dir=self.image_dir
		self.provider.cache_dir=self.cache_dir
		self.provider.calibration=calibration
		self.provider.setImages(images)
		
		array=Array.fromNumPy(self.generateImage(self.provider.images[0]),TargetDim=2) 
		self.width=array.getWidth()
		self.height=array.getHeight()
		self.dtype=array.dtype
		self.calibration=self.provider.calibration
		self.physic_box=physic_box

		for img in self.provider.images:
			camera=self.addCamera(img)
			self.createIdx(camera)

		self.guessInitialPoses()
		self.refreshQuads()
		self.saveMidx()
		self.guessLocalCameras()
		self.debugMatchesGraph()
		self.debugSolution()

	# addCamera
	def addCamera(self,img):
		self.images.append(img)
		camera=Camera()
		camera.id=len(self.cameras)
		camera.color = Color.random()
		for filename in img.filenames:
			camera.filenames.append(filename)
		super().addCamera(camera)
		return camera

	# createIdx
	def createIdx(self, camera):
		camera.idx_filename="./idx/{:04d}.idx".format(camera.id)
		field=Field("myfield", self.dtype)
		field.default_layout="row_major"
		CreateIdx(url=self.cache_dir + "/" + camera.idx_filename, 
				dim=2,
				filename_template="./{:04d}.bin".format(camera.id), 
				blocksperfile=-1,
				fields=[field],
				dims=(self.width, self.height))

	# startAction
	def startAction(self,N,message):
		print("Starting action",N,message,"...")

	# advanceAction
	def advanceAction(self,I):
		# print("Advance action",I)
		pass

	# endAction
	def endAction(self):
		print("End action")

	# showEnergy
	def showEnergy(self,camera,energy):
		pass

	# guessLocalCameras
	def guessLocalCameras(self):

		box = self.getQuadsBox()

		x1i = math.floor(box.p1[0]); x2i = math.ceil(box.p2[0])
		y1i = math.floor(box.p1[1]); y2i = math.ceil(box.p2[1])
		rect=(x1i, y1i, (x2i - x1i), (y2i - y1i))

		subdiv=cv2.Subdiv2D(rect)

		find_camera=dict()
		for camera in self.cameras:
			center = camera.quad.centroid()
			center = (numpy.float32(center.x),numpy.float32(center.y))
			if center in find_camera:
				print("The following cameras seems to be in the same position: ",find_camera[center].id,camera.id)
			else:
				find_camera[center] = camera
				subdiv.insert(center)

		cells, centers=subdiv.getVoronoiFacetList([])
		assert(len(cells) == len(centers))

		# find edges
		edges=dict()
		for Cell in range(len(cells)):
			cell = cells[Cell]
			center = (numpy.float32(centers[Cell][0]), numpy.float32(centers[Cell][1]))

			camera = find_camera[center]

			for I in range(len(cell)):
				pt0 = cell[(I + 0) % len(cell)]
				pt1 = cell[(I + 1) % len(cell)]
				k0=(pt0[0], pt0[1], pt1[0], pt1[1]) 
				k1=(pt1[0], pt1[1], pt0[0], pt0[1]) 

				if not k0 in edges: edges[k0]=set()
				if not k1 in edges: edges[k1]=set()

				edges[k0].add(camera)
				edges[k1].add(camera)
				
		for k in edges:
			adjacent = tuple(edges[k])
			for A in range(0,len(adjacent)-1):
				for B in range(A+1,len(adjacent)):
					camera1 = adjacent[A]
					camera2 = adjacent[B]
					camera1.addLocalCamera(camera2)

		# insert prev and next
		N=self.cameras.size()
		for I in range(N):
			camera2 = self.cameras[I]

			# insert prev and next
			if (I-1) >= 0:
				camera2.addLocalCamera(self.cameras[I - 1])

			if (I+1) < N:
				camera2.addLocalCamera(self.cameras[I + 1])

		#enlarge a little 
		if True:

			new_local_cameras={}

			for camera1 in self.cameras:

				new_local_cameras[camera1]=set()

				for camera2 in camera1.getAllLocalCameras():

					# euristic to say: do not take cameras on the same drone flight "row"
					prev2=self.previousCamera(camera2)
					next2=self.nextCamera(camera2)
					if prev2!=camera1 and next2!=camera1:
						if prev2: new_local_cameras[camera1].add(prev2)
						if next2: new_local_cameras[camera1].add(next2)

			for camera1 in new_local_cameras:
				for camera3 in new_local_cameras[camera1]:
					camera1.addLocalCamera(camera3)
					
		# draw the image
		if True:
			w = float(box.size()[0])
			h = float(box.size()[1])

			W = int(4096)
			H = int(h * (W/w))
			out = numpy.zeros((H, W, 3), dtype="uint8")
			out.fill(255)

			def toScreen(p):
				return [
					int(0+(p[0]-box.p1[0])*(W/w)),
					int(H-(p[1]-box.p1[1])*(H/h))]

			for I in range(len(cells)):
				cell=cells[I]
				center=(numpy.float32(centers[I][0]), numpy.float32(centers[I][1]))
				camera2 = find_camera[center]
				center=toScreen(center)
				cell=numpy.array([toScreen(it) for it in cell],dtype=numpy.int32)
				cv2.fillConvexPoly(out, cell, [random.randint(0,255) ,random.randint(0,255) ,random.randint(0,255) ])
				cv2.polylines(out, [cell], True, [0,0,0], 3)
				cv2.putText(out, str(camera2.id), (int(center[0]),int(center[1])), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1.0, [0,0,0])

			SaveImage(self.cache_dir+"/~local_cameras.png", out)

	# guessInitialPoses
	def guessInitialPoses(self):
		lat0,lon0=self.images[0].lat, self.images[0].lon
		for I,camera in enumerate(self.cameras):
			lat,lon,alt=self.images[I].lat, self.images[I].lon,self.images[I].alt
			x,y=GPSUtils.gpsToLocalCartesian(lat,lon,lat0,lon0)
			world_center=Point3d(x,y,alt)
			img=self.images[I]
			q = Quaternion(Point3d(0, 0, 1), -img.yaw) *  Quaternion(Point3d(1, 0, 0), math.pi)
			camera.pose = Pose(q, world_center).inverse()

	# saveMidx
	def saveMidx(self):

		print("Saving midx")
		lat0,lon0=self.images[0].lat,self.images[0].lon

		logic_box = self.getQuadsBox()

		# instead of working in range -180,+180 -90,+90 (worldwise ref frame) I normalize the range in [0,1]*[0,1]
		# physic box is in the range [0,1]*[0,1]
		# logic_box is in pixel coordinates
		# NOTE: I can override the physic box by command line
		physic_box=self.physic_box
		if physic_box is not None:
			print("Using physic_box forced by the user", physic_box.toString())
		else:
			physic_box=BoxNd.invalid()
			for I, camera in enumerate(self.cameras):
				quad=self.computeWorldQuad(camera)
				for point in quad.points:
					lat,lon=GPSUtils.localCartesianToGps(point.x, point.y,lat0, lon0)
					alpha,beta=GPSUtils.gpsToUnit(lat,lon)
					physic_box.addPoint(PointNd(Point2d(alpha,beta)))

		logic_centers=[]
		for I, camera in enumerate(self.cameras):
			p=camera.getWorldCenter()
			lat,lon,alt=*GPSUtils.localCartesianToGps(p.x, p.y, lat0, lon0),p.z
			alpha,beta=GPSUtils.gpsToUnit(lat,lon)
			alpha=(alpha-physic_box.p1[0])/float(physic_box.size()[0])
			beta =(beta -physic_box.p1[1])/float(physic_box.size()[1])
			logic_x=logic_box.p1[0]+alpha*logic_box.size()[0]
			logic_y=logic_box.p1[1]+beta *logic_box.size()[1]
			logic_centers.append((logic_x,logic_y))

		lines=[]

		# this is the midx
		lines.append("<dataset typename='IdxMultipleDataset' logic_box='%s %s %s %s' physic_box='%s %s %s %s'>" % (
			cstring(int(logic_box.p1[0])),cstring(int(logic_box.p2[0])),cstring(int(logic_box.p1[1])),cstring(int(logic_box.p2[1])),
			cstring10(physic_box.p1[0]),cstring10(physic_box.p2[0]),cstring10(physic_box.p1[1]),cstring10(physic_box.p2[1])))
		lines.append("")

		# dump some information about the slam
		lines.append("<slam width='%s' height='%s' dtype='%s' calibration='%s %s %s' />" % (
			cstring(self.width),cstring(self.height),self.dtype.toString(),
			cstring(self.calibration.f),cstring(self.calibration.cx),cstring(self.calibration.cy)))
		lines.append("")

		# this is the default field
		lines.append("<field name='blend'><code>output=voronoi()</code></field>")
		lines.append("")

		# how to go from logic_box (i.e. pixel) -> physic box ([0,1]*[0,1])
		lines.append("<translate x='%s' y='%s'>" % (cstring10(physic_box.p1[0]),cstring10(physic_box.p1[1])))
		lines.append("<scale     x='%s' y='%s'>" % (cstring10(physic_box.size()[0]/logic_box.size()[0]),cstring10(physic_box.size()[1]/logic_box.size()[1])))
		lines.append("<translate x='%s' y='%s'>" % (cstring10(-logic_box.p1[0]),cstring10(-logic_box.p1[1])))
		lines.append("")

		if self.enable_svg:
			W=int(1024)
			H=int(W*(logic_box.size()[1]/float(logic_box.size()[0])))

			lines.append("<svg width='%s' height='%s' viewBox='%s %s %s %s' >" % (
				cstring(W),
				cstring(H),
				cstring(int(logic_box.p1[0])),
				cstring(int(logic_box.p1[1])),
				cstring(int(logic_box.p2[0])),
				cstring(int(logic_box.p2[1]))))

			lines.append("<g stroke='#000000' stroke-width='1' fill='#ffff00' fill-opacity='0.3'>")
			for I, camera in enumerate(self.cameras):
				lines.append("\t<poi point='%s,%s' />" % (cstring(logic_centers[I][0]),cstring(logic_centers[I][1])))
			lines.append("</g>")

			lines.append("<g fill-opacity='0.0' stroke-opacity='0.5' stroke-width='2'>")
			for I, camera in enumerate(self.cameras):
				lines.append("\t<polygon points='%s' stroke='%s' />" % (camera.quad.toString(","," "),camera.color.toString()[0:7]))
			lines.append("</g>")

			lines.append("</svg>")
			lines.append("")

		for I, camera in enumerate(self.cameras):
			p=camera.getWorldCenter()
			lat,lon,alt=*GPSUtils.localCartesianToGps(p.x, p.y, lat0, lon0),p.z
			lines.append("<dataset url='%s' color='%s' quad='%s' filenames='%s' q='%s' t='%s' lat='%s' lon='%s' alt='%s' />" %(
				camera.idx_filename,
				camera.color.toString(),
				camera.quad.toString(),
				";".join(camera.filenames),
				camera.pose.q.toString(),
				camera.pose.t.toString(),
				cstring10(lat),cstring10(lon),cstring10(alt)))
			
		lines.append("")
		lines.append("</translate>")
		lines.append("</scale>")
		lines.append("</translate>")
		lines.append("")
		lines.append("</dataset>")

		SaveTextDocument(self.cache_dir+"/visus.midx","\n".join(lines))

		SaveTextDocument(self.cache_dir+"/google.midx",
"""
<dataset name='slam' typename='IdxMultipleDataset'>
	<field name='voronoi'><code>output=voronoi()</code></field>
	<dataset typename='GoogleMapsDataset' tiles='http://mt1.google.com/vt/lyrs=s' physic_box='0.0 1.0 0.0 1.0' />
	<dataset name='visus'   url='./visus.midx' />
</dataset>
""")

	# debugMatchesGraph
	def debugMatchesGraph(self):

		box = self.getQuadsBox()

		w = float(box.size()[0])
		h = float(box.size()[1])

		W = int(4096)
		H = int(h * (W/w))
		out = numpy.zeros((H, W, 4), dtype="uint8")
		out.fill(255)

		def getImageCenter(camera):
			p=camera.quad.centroid()
			return (
				int(0+(p[0]-box.p1[0])*(W/w)),
				int(H-(p[1]-box.p1[1])*(H/h)))

		for bGoodMatches in [False,True]:
			for A in self.cameras :
				local_cameras=A.getAllLocalCameras()
				for J in range(local_cameras.size()):
					B=local_cameras[J]
					edge=A.getEdge(B)
					if A.id < B.id and bGoodMatches == (True if edge.isGood() else False):
						p0 = getImageCenter(A)
						p1 = getImageCenter(B)
						color = [0,0,0, 255] if edge.isGood() else [211,211,211, 255]
						cv2.line(out, p0, p1, color, 1)
						num_matches = edge.matches.size()
						if num_matches>0:
							cx=int(0.5*(p0[0]+p1[0]))
							cy=int(0.5*(p0[1]+p1[1]))
							cv2.putText(out, str(num_matches), (cx,cy), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1.0, color)

		for camera in self.cameras :
			center=getImageCenter(camera)
			cv2.putText(out, str(camera.id), (center[0],center[1]), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1.0, [0,0,0,255])
			
		SaveImage(GuessUniqueFilename(self.cache_dir+"/~matches%d.png"), out)

	# debugSolution
	def debugSolution(self):

		box = self.getQuadsBox()

		w = float(box.size()[0])
		h = float(box.size()[1])

		W = int(4096)
		H = int(h * (W/w))
		out = numpy.zeros((H, W, 4), dtype="uint8")
		out.fill(255)

		def toScreen(p):
			return (
				int(0+(p[0]-box.p1[0])*(W/w)),
				int(H-(p[1]-box.p1[1])*(H/h)))

		for camera2 in self.cameras:
			color=(int(255*camera2.color.getRed()),int(255*camera2.color.getGreen()),int(255*camera2.color.getBlue()),255)
			points=numpy.array([toScreen(it) for it in camera2.quad.points],dtype=numpy.int32)
			cv2.polylines(out, [points], True, color, 3)
			cv2.putText(out, str(camera2.id), toScreen(camera2.quad.points[0]), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1.0, color)

		SaveImage(GuessUniqueFilename(self.cache_dir+"/~solution%d.png"), out)

	# doPostIterationAction
	def doPostIterationAction(self):
		self.debugSolution()
		self.debugMatchesGraph()

	# convertAndExtract
	def convertAndExtract(args):
		I, (img, camera) = args

		self.advanceAction(I)

		# create idx and extract keypoints
		keypoint_filename = self.cache_dir+"/keypoints/%04d" % (camera.id,)
		idx_filename      = self.cache_dir+"/" + camera.idx_filename

		if not self.loadKeyPoints(camera,keypoint_filename) or not os.path.isfile(idx_filename):

			full = self.generateImage(img)
			Assert(isinstance(full, numpy.ndarray))

			dataset = LoadDataset(idx_filename)
			dataset.compressDataset(["zip"],Array.fromNumPy(full,TargetDim=2, bShareMem=True)) # write zipped full 

			energy=ConvertImageToGrayScale(full)
			energy=ResizeImage(energy, self.energy_size)
			(keypoints,descriptors)=self.extractor.doExtract(energy)

			vs=self.width  / float(energy.shape[1])
			if keypoints:
				camera.keypoints.clear()
				camera.keypoints.reserve(len(keypoints))
				for keypoint in keypoints:
					camera.keypoints.push_back(KeyPoint(vs*keypoint.pt[0], vs*keypoint.pt[1], keypoint.size, keypoint.angle, keypoint.response, keypoint.octave, keypoint.class_id))
				camera.descriptors=Array.fromNumPy(descriptors,TargetDim=2) 

			self.saveKeyPoints(camera,keypoint_filename)

			energy=cv2.cvtColor(energy, cv2.COLOR_GRAY2RGB)
			for keypoint in keypoints:
				cv2.drawMarker(energy, (int(keypoint.pt[0]), int(keypoint.pt[1])), (0, 255, 255), cv2.MARKER_CROSS, 5)
			energy=cv2.flip(energy, 0)
			energy=ConvertImageToUint8(energy)

			if False:
				quad_box=camera.quad.getBoundingBox()
				VS = self.energy_size / max(quad_box.size()[0],quad_box.size()[1])
				T=Matrix.scale(2,VS) * camera.homography * Matrix.scale(2,vs)
				quad_box=Quad(T,Quad(energy.shape[1],energy.shape[0])).getBoundingBox()
				warped=cv2.warpPerspective(energy,  MatrixToNumPy(Matrix.translate(-quad_box.p1) * T),  (int(quad_box.size()[0]),int(quad_box.size()[1])))
				energy=ComposeImage([warped,energy],1)

			self.showEnergy(camera,energy)

	# convertToIdxAndExtractKeyPoints
	def convertToIdxAndExtractKeyPoints(self):

		t1=Time.now()

		# convert to idx and find keypoints (don't use threads for IO ! it will slow down things)
		# NOTE I'm disabling write-locks
		self.startAction(len(self.cameras),"Converting idx and extracting keypoints...")

		if not self.extractor:
			self.extractor=ExtractKeyPoints(self.min_num_keypoints,self.max_num_keypoints,self.anms)

		if self.enable_color_matching:
			color_matching_ref = None

		for I,(img,camera) in enumerate(zip(self.images,self.cameras)):
			self.advanceAction(I)

			# create idx and extract keypoints
			keypoint_filename = self.cache_dir+"/keypoints/%04d" % (camera.id,)
			idx_filename      = self.cache_dir+"/" + camera.idx_filename
			
			if not self.loadKeyPoints(camera,keypoint_filename) or not os.path.isfile(idx_filename) or not os.path.isfile(idx_filename.replace(".idx",".bin")):
				
				full = self.generateImage(img)
				Assert(isinstance(full, numpy.ndarray))

				# Match Histograms
				if self.enable_color_matching:
					if color_matching_ref:
						print("doing color matching...")
						MatchHistogram(full, color_matching_ref) 
					else:
						color_matching_ref = full

				dataset = LoadDataset(idx_filename)
				
				# slow: first write then compress
				#dataset.write(full)
				#dataset.compressDataset(["lz4"],Array.fromNumPy(full,TargetDim=2, bShareMem=True)) # write zipped full 

				# fast: compress in-place
				comp=["lz4"]#,"jpg-JPEG_QUALITYGOOD-JPEG_SUBSAMPLING_420-JPEG_OPTIMIZE" ,"jpg-JPEG_QUALITYGOOD-JPEG_SUBSAMPLING_420-JPEG_OPTIMIZE","jpg-JPEG_QUALITYGOOD-JPEG_SUBSAMPLING_420-JPEG_OPTIMIZE"]
				dataset.compressDataset(comp,Array.fromNumPy(full,TargetDim=2, bShareMem=True)) # write zipped full 

				energy=ConvertImageToGrayScale(full)
				energy=ResizeImage(energy, self.energy_size)
				(keypoints,descriptors)=self.extractor.doExtract(energy)

				vs=self.width  / float(energy.shape[1])
				if keypoints:
					camera.keypoints.clear()
					camera.keypoints.reserve(len(keypoints))
					for keypoint in keypoints:
						camera.keypoints.push_back(KeyPoint(vs*keypoint.pt[0], vs*keypoint.pt[1], keypoint.size, keypoint.angle, keypoint.response, keypoint.octave, keypoint.class_id))
					camera.descriptors=Array.fromNumPy(descriptors,TargetDim=2) 

				self.saveKeyPoints(camera,keypoint_filename)

				energy=cv2.cvtColor(energy, cv2.COLOR_GRAY2RGB)
				for keypoint in keypoints:
					cv2.drawMarker(energy, (int(keypoint.pt[0]), int(keypoint.pt[1])), (0, 255, 255), cv2.MARKER_CROSS, 5)
				energy=cv2.flip(energy, 0)
				energy=ConvertImageToUint8(energy)

				if False:
					quad_box=camera.quad.getBoundingBox()
					VS = self.energy_size / max(quad_box.size()[0],quad_box.size()[1])
					T=Matrix.scale(2,VS) * camera.homography * Matrix.scale(2,vs)
					quad_box=Quad(T,Quad(energy.shape[1],energy.shape[0])).getBoundingBox()
					warped=cv2.warpPerspective(energy,  MatrixToNumPy(Matrix.translate(-quad_box.p1) * T),  (int(quad_box.size()[0]),int(quad_box.size()[1])))
					energy=ComposeImage([warped,energy],1)

				self.showEnergy(camera,energy)
				
			print("Done",camera.filenames[0],I,"of",len(self.cameras))

		print("done in",t1.elapsedMsec(),"msec")

	# findMatches
	def findMatches(self,camera1,camera2):

		if camera1.keypoints.empty() or camera2.keypoints.empty():
			camera2.getEdge(camera1).setMatches([],"No keypoints")
			return 0

		matches,H21,err=FindMatches(self.width,self.height,
			camera1.id,[(k.x, k.y) for k in camera1.keypoints],Array.toNumPy(camera1.descriptors), 
			camera2.id,[(k.x, k.y) for k in camera2.keypoints],Array.toNumPy(camera2.descriptors),
			self.max_reproj_error * self.width, self.ratio_check)

		if self.debug_mode and H21 is not None and len(matches)>0:
			points1=[(k.x, k.y) for k in camera1.keypoints]
			points2=[(k.x, k.y) for k in camera2.keypoints]
			DebugMatches(self.cache_dir+"/debug_matches/%s/%04d.%04d.%d.png" %(err if err else "good",camera1.id,camera2.id,len(matches)), 
				self.width, self.height, 
				Array.toNumPy(ArrayUtils.loadImage(self.cache_dir+"/energy/~%04d.tif" % (camera1.id,))), [points1[match.queryIdx] for match in matches], H21, 
				Array.toNumPy(ArrayUtils.loadImage(self.cache_dir+"/energy/~%04d.tif" % (camera2.id,))), [points2[match.trainIdx] for match in matches], numpy.identity(3,dtype='float32'))

		if err:
			camera2.getEdge(camera1).setMatches([],err)
			return 0

		matches=[Match(match.queryIdx,match.trainIdx, match.imgIdx, match.distance) for match in matches]
		camera2.getEdge(camera1).setMatches(matches,str(len(matches)))
		return len(matches)

	# findAllMatches
	def findAllMatches(self,nthreads=8):
		t1 = Time.now()
		jobs=[]
		for camera2 in self.cameras:
			for camera1 in camera2.getAllLocalCameras():
				if camera1.id < camera2.id:
					jobs.append(lambda pair=(camera1,camera2): self.findMatches(pair[0],pair[1]))
		self.startAction(len(jobs),"Finding all matches")
		results=RunJobsInParallel(jobs,advance_callback=lambda ndone: self.advanceAction(ndone))
		num_matches=sum(results)
		print("Found num_matches(", num_matches, ") matches in ", t1.elapsedMsec() ,"msec")

	# generateImage
	def generateImage(self,img):
		t1=Time.now()
		print("Generating image",img.filenames[0])	
		ret = InterleaveChannels(self.provider.generateMultiImage(img))
		print("done",img.id,"range",ComputeImageRange(ret),"shape",ret.shape, "dtype",ret.dtype,"in",t1.elapsedMsec(),"msec")
		return ret

	# run
	def run(self):

		# if it's the first time, I need to find key point matches
		if self.cameras[0].keypoints.size()==0:
			self.convertToIdxAndExtractKeyPoints()
			if self.do_bundle_adjustment:
				print("Finding matches...")
				self.findAllMatches()
				print("removeDisconnectedCameras...")
				self.removeDisconnectedCameras()
				print("debugMatchesGraph...")
				self.debugMatchesGraph()

		if self.do_bundle_adjustment:
			print("Doing bundle adjustment...")
			tolerances=(10.0*self.ba_tolerance,1.0*self.ba_tolerance)
			self.startAction(len(tolerances),"Refining solution...")
			for I,tolerance in enumerate(tolerances):
				self.advanceAction(I)
				self.bundleAdjustment(tolerance)
				self.removeOutlierMatches(self.max_reproj_error * self.width)
				self.removeDisconnectedCameras()
				self.removeCamerasWithTooMuchSkew()
			self.endAction()
		else:
			print("Skipping bundle adjustment...")

		self.saveMidx()
		SavePreview(self.cache_dir+"/visus.midx",self.cache_dir+"/preview.png")
		print("Finished")


	# ////////////////////////////////////////////////
	@staticmethod
	def Run(remote_dir=None,image_dir=None, cache_dir=None,telemetry=None,plane=None,calibration=None,physic_box=None,batch=False, idx_filename=None):
		
		if isinstance(calibration,str) and len(calibration):
			f,cx,cy=[cdouble(it) for it in calibration.split()]
			calibration=Calibration(f,cx,cy)
		else:
			calibration=None
				
		print("Running slam:")
		print("\t","remote_dir", repr(remote_dir))
		print("\t","image_dir", repr(image_dir))
		print("\t","cache_dir", repr(cache_dir))
		print("\t","telemetry", repr(telemetry))
		print("\t","plane", repr(plane))
		print("\t","calibration", (calibration.f,calibration.cx,calibration.cy) if calibration else None)
		print("\t","physic_box", physic_box.toString() if physic_box else None)		
		print("\t","batch", batch)
		print("\t","idx_filename",idx_filename)
		
		# I need to download the sequence locally otherwise is going to be too slow
		# TODO: switch to pydrive
		if remote_dir is not None and remote_dir!=image_dir :
			
			print("Need to sync",remote_dir,image_dir)
			
			# just not to repeat the same sync over and over
			if os.path.exists(image_dir+ "/~sync.done"):
				print("sync already done")
			else:
				cmd=["rclone","sync","-v",remote_dir,image_dir]
				print("Running:",cmd)
				subprocess.run(cmd, shell=False, check=True, stdout=sys.stdout, stderr=sys.stderr) 
				open(image_dir+ "/~sync.done", 'w').close()
			
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
		
		# in case it was automatically asssigned
		if not cache_dir:
			cache_dir=slam.cache_dir 
			
		if batch:
			slam.run()
		else:
			gui.run(slam)
			
		# convert to idx and produce preview
		if idx_filename:
			MidxToIdx(["--midx", cache_dir+"/visus.midx","--idx", idx_filename])	
			idx_dir=os.path.dirname(idx_filename)
			SavePreview(idx_filename,idx_dir+"/preview.png")
			
