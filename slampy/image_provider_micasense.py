

import sys,os,platform,math

# this is needed to find micasense module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import micasense
import micasense.utils 
import micasense.metadata
import micasense.plotutils
import micasense.image 
import micasense.imageutils
import micasense.panel 
import micasense.capture 

from slampy.image_provider import *

# /////////////////////////////////////////////////////////////////////////////////////////////////////
# see https://github.com/micasense/imageprocessing/blob/master/Alignment.ipynb
class ImageProviderRedEdge(ImageProvider):
	
	#  constructor (TODO: panel_calibration)
	def __init__(self,panel_calibration=[0.67, 0.69, 0.68, 0.61, 0.67]):
		super().__init__()
		self.panel_calibration=panel_calibration
		self.panel_irradiance=None
		self.yaw_offset=math.pi # in the sequence I have the yaw is respect to the south
	
	# example: NIR_608.TIF  / RGB_608.TIF / Thermal_608.TIF returns 608
	def getGroupId(self,filename):
		filename=os.path.basename(filename)
		v=os.path.splitext(filename)[0].split("_")
		
		if len(v)<2 or not v[-2].isdigit(): 
			return ""

		# todo _6.tif  LWIR _6 which has a different resolution 
		if (v[-1])=="6":
			return ""

		return v[-2]
	
	# isPanel
	def isPanel(self,img):
		panel = micasense.panel.Panel(micasense.image.Image(img.filenames[0]))
		return panel.panel_detected()

	# findPanels
	def findPanels(self):

		print("Finding panels...")
		self.panels=[]

		# find the first panel
		while self.images and not self.isPanel(self.images[0]):
			print("Dropping",self.images[0].filenames,"because I need a panel")
			self.images=self.images[1:]

		if not self.images:
			raise Exception("cannot find the panel")

		# skip all panels
		while self.images and self.isPanel(self.images[0]):
			print(self.images[0].filenames,"is panel")
			self.panels.append(self.images[0])
			self.images=self.images[1:]

		if not self.images:
			raise Exception("cannot find flight images")

		print(self.images[0].filenames,"is not panel, starting the flight")

		# not I need to find a detected panel (it must be in self.panels)
		for it in self.panels:
			try:
				panel = micasense.capture.Capture.from_filelist(it.filenames) 
				self.panel_irradiance = panel.panel_irradiance(self.panel_calibration)	
				print("panel_irradiance",self.panel_irradiance)
				break
			except:
				pass


	# generateImage
	def generateImage(self,img):
		capture = micasense.capture.Capture.from_filelist(img.filenames)
		# note I'm ignoring distotions here
		# capture.images[I].undistorted(capture.images[I].reflectance())
		multi = capture.reflectance(self.panel_irradiance)
		multi = [single.astype('float32') for single in multi]
		multi = self.mirrorY(multi)
		multi = self.swapRedAndBlue(multi)
		multi = self.undistortImage(multi)
		multi = self.alignImage(multi)
		multi=[single for single in multi if single.shape==multi[0].shape]
		return multi

# /////////////////////////////////////////////////////////////////////////////////////////////////////
def CreateImageProviderInstance(metadata):

	acc=[]
	for key,value in metadata.items():
		acc.append(str(value).lower())

	acc=" ".join(acc)
	if "rededge" in acc or "micasense" in acc:
		return ImageProviderRedEdge()
	else:
		return None
