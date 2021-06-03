###############################################
###     Example Python Script               ###
###############################################
##                                          ###
##       COMPUTE TGI for every pixel        ###
# TGI is sensitive to leaf chlorophyll content at the canopy scale and not sensitive to leaf area index
# TGI may be the best spectral index to detect crop nitrogen requirements with low-cost digital cameras mounted on low-altitude airborne platforms.
# https://digitalcommons.unl.edu/cgi/viewcontent.cgi?article=2161&context=usdaarsfacpub

###############################################
###     Import your libraries as needed     ###
###############################################


import cv2, numpy
import matplotlib

# import matplotlib.pyplot as plt
# import matplotlib.image as mpimg

###############################################
###     Convert ViSUS array to numpy        ###
###############################################

# pdim = input.dims.getPointDim()
# img = Array.toNumPy(input, bShareMem=True)
img = input.astype(numpy.float32)

###############################################
###     Get each channel of image           ###
###############################################

red = img[:, :, 0]
green = img[:, :, 1]
blue = img[:, :, 2]

###############################################
###    Do Some Math                         ###
###############################################

# #TGI – Triangular Greenness Index - RGB index for chlorophyll sensitivity. TGI index relies on reflectance values at visible wavelengths. It #is a fairly good proxy for chlorophyll content in areas of high leaf cover.
# #TGI = −0.5 * ((190 * (redData − greeData)) − (120*(redData − blueData)))
scaleRed = (0.39 * red)
scaleBlue = (.61 * blue)
TGI = green - scaleRed - scaleBlue
TGI = (TGI + 1.0) / 2.0
#TGI = cv2.normalize(TGI, None, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_32F)  # normalize data [0,1]

#gray = cv2.cvtColor(numpy.float32(TGI), cv2.COLOR_GRAY2RGB)
gray = numpy.float32(TGI)

colors = [(1.0, 0.97, 0.66), (0.94,0.30,0.34), (0.59, 0.98, 0.59), (0.59, 0.98, 0.79),(0.29, 0.58, 0.29)]
nodes1 =[0.0,0.4,0.6,0.7,1.0,]
cmap = matplotlib.colors.LinearSegmentedColormap.from_list("mycmap", list(zip(nodes1, colors )))

out = cmap(gray)
#colomapping generates RGBA, only need RGB
out = out[...,:3]
###############################################
###   To return our your output image (out) ###
###    convert from NumPy                   ###
###############################################
#out = cv2.cvtColor(numpy.float32(out), cv2.COLOR_RGB2BGR)
#
#out = cv2.cvtColor(numpy.float32(out), cv2.COLOR_RGB2BGR)
# out = cv2.cvtColor(numpy.float32(out), cv2.COLOR_BGR2RGB)
# out = cv2.cvtColor(numpy.float32(out), cv2.COLOR_RGB2BGR)

###############################################
###   To return our your output image (out) ###
###    convert from NumPy                   ###
###############################################
#output = out
output = out.astype(numpy.float32)
