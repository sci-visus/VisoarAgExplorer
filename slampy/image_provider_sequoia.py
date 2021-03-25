
import pytz
import base64
import struct

from slampy.image_provider import *

# ///////////////////////////////////////////////////////////////////////////////////////////////
# https://github.com/rasmusfenger/micasense_imageprocessing_sequoia/blob/master/Sequoia%20Image%20Processing%20Tutorial.ipynb
class ImageProviderSequoia(ImageProvider):
	
	#  constructor
	def __init__(self):
		super().__init__( )

	# build_powers_coefficients
	def buildPowersCoefficients(self,powers, coefficients):
		#return: List of tuples of the form (n, m, coefficient)
		powers_coefficients = []
		power_items = powers.split(',')
		coefficient_items = coefficients.split(',')
		for i in range(0, len(power_items), 2):
			powers_coefficients.append((int(power_items[i]), int(power_items[i + 1]), float(coefficient_items[int(i / 2)])))
		return powers_coefficients				
			
	# vignetting
	def vignetting(self,powers_coefficients, x, y):
		value = 0.0
		for entry in powers_coefficients:
			value = value + entry[2] * math.pow(x, entry[0]) * math.pow(y, entry[1])
		return value	
		
	# vignette_correction
	# Python code is written by seanmcleod and modified by Rasmus Fenger-Nielsen
	# https://forum.developer.parrot.com/t/vignetting-correction-sample-code/5614
	def vignette_correction(self,metadata, xDim, yDim):
		polynomial2DName = metadata['XMP:VignettingPolynomial2DName']
		polynomial2D = metadata['XMP:VignettingPolynomial2D']
		poly = self.buildPowersCoefficients(polynomial2DName, polynomial2D)
		vignette_factor = numpy.ones((yDim, xDim), dtype=numpy.float32)
		for y in range(0, yDim):
			for x in range(0, xDim):
				vignette_factor[y, x] = self.vignetting(poly, float(x) / xDim, float(y) / yDim)
		return vignette_factor	
			
	# getSequoiaIrradiance
	def getSequoiaIrradiance(self,metadata, img):
		
		xDim = img.shape[1]
		yDim = img.shape[0]
		V = self.vignette_correction(metadata, xDim, yDim)
		img = img/V

		sensorModel = metadata['XMP:SensorModel'].split(',')
		A = float(sensorModel[0])
		B = float(sensorModel[1])
		C = float(sensorModel[2])

		fNumber = metadata['EXIF:FNumber']
		expTime = metadata['EXIF:ExposureTime']
		gain    = metadata['EXIF:ISO']

		return fNumber ** 2 * (img - B) / (A * expTime * gain + C)

	# getSunIrradiance
	def getSunIrradiance(self,metadata):
		
		encoded = metadata['XMP:IrradianceList']
		
		# decode the string
		data = base64.standard_b64decode(encoded)

		# ensure that there's enough data QHHHfff
		#print (len(data))
		assert len(data) % 28 == 0

		# determine how many datasets there are
		count = len(data) // 28

		# unpack the data as uint64, uint16, uint16, uint16, uint16, float, float, float
		result = []
		for i in range(count):
			index = 28 * i
			s = struct.unpack('<QHHHHfff', data[index:index + 28])
			result.append(s)
			
		#GetTimefromStart
		def GetTimefromStart(metadata):
			# Calculate sunshine sensor irradiance
			# The code is written by Yu-Hsuan Tu (https://github.com/dobedobedo/Parrot_Sequoia_Image_Handler/tree/master/Modules)
			# The code has been modified by Rasmus Fenger-Nielsen	
			Time = datetime.datetime.strptime(metadata['Composite:SubSecCreateDate'], "%Y:%m:%d %H:%M:%S.%f")
			Time_UTC = pytz.utc.localize(Time, is_dst=False)
			duration = datetime.timedelta(hours=Time_UTC.hour,minutes=Time_UTC.minute,seconds=Time_UTC.second,microseconds=Time_UTC.microsecond)
			return duration		

		CreateTime = GetTimefromStart(metadaa)
		timestamp = []
		for measurement in result:
			q, r = divmod(measurement[0], 1000000)
			timestamp.append(abs(datetime.timedelta(seconds=q, microseconds=r) - CreateTime))
		TargetIndex = timestamp.index(min(timestamp))
		count = result[TargetIndex][1]
		gain = result[TargetIndex][3]
		exposuretime = result[TargetIndex][4]
		
		return float(count) / (gain * exposuretime)
		
	# createUndistortLenMap
	def createUndistortLenMap(self,multi):

		# check all same size
		Assert(len(set([single.shape for single in multi]))==1)
		ImageWidth,ImageHeight=multi[0].shape[1],multi[0].shape[0]

		metadata=self.images[0].metadata

		if 'XMP:FisheyePolynomial' not in metadata or 'XMP:FisheyeAffineMatrix' not in metadata:
			return

		p0,p1,p2,p3 = numpy.array(metadata['XMP:FisheyePolynomial'].split(',')).astype(numpy.float)[0:4]
		C,D,E,F = numpy.array(metadata['XMP:FisheyeAffineMatrix'].split(',')).astype(numpy.float)[0:4]

		print("Sequoia finding lens distortions map for fisheye","XMP:FisheyePolynomial",p0,p1,p2,p3,"XMP:FisheyeAffineMatrix",C,D,E,F)
		
		cam_mat = numpy.zeros((3, 3))
		cam_mat[0, 0] = self.calibration.f; cam_mat[0, 2] = self.calibration.cx
		cam_mat[1, 1] = self.calibration.f; cam_mat[1, 2] = self.calibration.cy
		cam_mat[2, 2] = 1.0

		# create array with pixel coordinates
		x, y = numpy.meshgrid(range(ImageWidth), range(ImageHeight))
		P = numpy.array([x.flatten(order='F'), y.flatten(order='F'), numpy.ones(ImageWidth * ImageHeight)])
		p = numpy.linalg.solve(cam_mat, P) 
		X,Y = p[0],p[1]
		r = numpy.sqrt((X**2) + (Y**2))
		theta = (2/math.pi) * numpy.arctan(r)
		row = p0 + p1 * theta + p2 * theta**2 + p3 * theta**3
		tmp = row / r
		Xh = X * tmp
		Yh = Y * tmp
		Xd = C * Xh + D * Yh + self.calibration.cx
		Yd = E * Xh + F * Yh + self.calibration.cy
		distorted = [Xd, Yd, numpy.ones(len(Xd))]

		self.xmap = numpy.reshape(distorted[0], (ImageHeight, ImageWidth), order='F').astype(numpy.float32)
		self.ymap = numpy.reshape(distorted[1], (ImageHeight, ImageWidth), order='F').astype(numpy.float32)


	# findGroups
	# example: IMG_0000_1.tif  / IMG_0000_2.tif / IMG_0000_3.tif / IMG_0000_4.tif / IMG_0000_5.tif
	# note I can have same group number in different directories (example calib/.. msb/..)
	# so I need to separate them with dirname
	def getGroupId(self,filename):
		A=os.path.dirname(filename)
		if   A.endswith("calib"): Priority=0
		elif A.endswith("msp"):   Priority=1
		else: return ""
		filename=os.path.basename(filename)
		v=os.path.splitext(filename)[0].split("_")
		if len(v)<2 or not v[-2].isdigit(): return ""
		return (Priority,v[-2]) 
	
	# removePanels
	def findPanels(self):
		print("Finding panels...")
		self.panels=[]
		for img in self.images.copy():
			if "calib" in os.path.split(img.filenames	[0])[-2]:
				print(img.filenames,"is panel")
				self.panels.append(img)
				self.images.remove(img)
			else: 
				print( os.path.split(img.filenames	[0]),"does not seem a panel. Switching to image mode")
				break
		if not self.panels:
			print("Warning","I don't have any panel image'")

	# generateImage
	def generateImage(self,img):

		# read all images
		multi=[cv2.imread(filename,-1) for filename in img.filenames]
		
		# compute irradiance
		# metadata=self.images[index].metadata
		# broken right now since my sequence has not the 'XMP:SensorModel' metadata
		# multi=[self.getSequoiaIrradiance(metadata,single)/self.getSunIrradiance(metadata) for single in multi]
		
		# undistort (i'm loosing a big portion of the image here...)
		multi = self.undistortImage(multi)
		multi = [single.astype('float32') for single in multi]
		multi = self.mirrorY(multi)
		multi = self.swapRedAndBlue(multi)
		multi = self.undistortImage(multi)
		multi = self.alignImage(multi)
		return multi


# /////////////////////////////////////////////////////////////////////////////////////////////////////
def CreateImageProviderInstance(metadata):
	exif_make =str(metadata["EXIF:Make"]).lower()  if "EXIF:Make"  in metadata else ""
	exif_model=str(metadata["EXIF:Model"]).lower() if "EXIF:Model" in metadata else ""
	if "sequoia" in exif_make or "sequoia" in exif_model:
		return ImageProviderSequoia()
	else:
		return None
