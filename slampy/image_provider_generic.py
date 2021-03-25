

import cv2
import pytz
import base64
import struct

from slampy.image_provider import *

# /////////////////////////////////////////////////////////////////////////////////////////////////////
class ImageProviderGeneric(ImageProvider):

	#  constructor (TODO: panel_calibration)
	def __init__(self):
		super().__init__()
	
	# findGroups
	def findGroups(self,all_images):
		all_images=sorted(all_images)
		return [[filename] for filename in all_images]

	# generateImage
	def generateImage(self,img):
		multi = [cv2.imread(filename,-1) for filename in img.filenames]
		multi = self.mirrorY(multi)
		multi = self.swapRedAndBlue(multi)
		multi = self.undistortImage(multi)
		multi = self.alignImage(multi)
		return multi


# ///////////////////////////////////////////////////////////////////////////////////////////////
def CreateImageProviderInstance(metadata):
	return ImageProviderGeneric()
