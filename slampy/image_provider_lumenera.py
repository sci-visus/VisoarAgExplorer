

import tifffile
import cv2

from slampy.image_provider import *
from slampy.image_utils    import *

# ///////////////////////////////////////////////////////////////////////////////////////////////
class ImageProviderLumenera(ImageProvider):
	
	#  constructor
	def __init__(self):
		super().__init__()
		
	# example: NIR_608.TIF  / RGB_608.TIF / Thermal_608.TIF returns 608
	# they are in different directories
	def getGroupId(self,filename):
		if not "RGB_" in filename: return ""  # only RGB right now
		filename=os.path.basename(filename)
		v=os.path.splitext(filename)[0].split("_")
		if len(v)<1 or not v[-1].isdigit(): return ""
		return v[-1]

	# generateImage
	def generateImage(self,img):
                if img.filenames[0].lower().endswith("jpg"):
                        multi=[cv2.imread(filename,-1) for filename in img.filenames]
                else:
	                multi = [numpy.array(tifffile.imread(filename)) for filename in img.filenames]

                multi = [ConvertImageToUint8(single) for single in multi] # TODO
                multi = self.mirrorY(multi)
                multi = self.swapRedAndBlue(multi)
                multi = self.undistortImage(multi)
                multi = self.alignImage(multi)
                return multi


# /////////////////////////////////////////////////////////////////////////////////////////////////////
def CreateImageProviderInstance(metadata):
	exif_make =str(metadata["EXIF:Make"]).lower()  if "EXIF:Make"  in metadata else ""
	exif_model=str(metadata["EXIF:Model"]).lower() if "EXIF:Model" in metadata else ""

	if "lumenera" in exif_model or "lumenera" in exif_make:
		return ImageProviderLumenera()
	else:
		return None
