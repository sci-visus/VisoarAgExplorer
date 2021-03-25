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
#TGI = (TGI + 1.0) / 2.0
#TGI = cv2.normalize(TGI, None, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_32F)  # normalize data [0,1]

#gray = cv2.cvtColor(numpy.float32(TGI), cv2.COLOR_GRAY2RGB)
gray = numpy.float32(TGI)

#cdict=[(.2, .4,0), (.2, .4,0), (.94, .83, 0), (.286,.14,.008), (.56,.019,.019)]
#cdict = [(.56, .019, .019), (.286, .14, .008), (.94, .83, 0), (.2, .4, 0), (.2, .4, 0)]
cdict = [ (0.56, 0.02 ,0.02), (0.74, 0.34 ,0.04), (0.94, 0.65 ,0.27), (0.2, 0.4 ,0.0), (0.2, 0.4 ,0.0),]


cmap = matplotlib.colors.LinearSegmentedColormap.from_list(name='my_colormap', colors=cdict, N=1000)
#
# mapN = matplotlib.colors.LinearSegmentedColormap.from_list(name="", colors=["red","violet","blue", "yellow", "green"], N=1000)


colors = ["red","darkorange", "gold", "lawngreen", "green","green"]
cmap1 = matplotlib.colors.LinearSegmentedColormap.from_list("mycmap", cdict)
nodes = [0.0, 0.2, 0.5, 0.8,0.9, 1.0]
cmap2 = matplotlib.colors.LinearSegmentedColormap.from_list("mycmap", list(zip(nodes, colors)))
out =  cmap(gray)

###############################################
###   To return our your output image (out) ###
###    convert from NumPy                   ###
###############################################
#out = cv2.cvtColor(numpy.float32(out), cv2.COLOR_RGB2BGR)
#
#out = cv2.cvtColor(numpy.float32(out), cv2.COLOR_RGB2BGR)
out = cv2.cvtColor(numpy.float32(out), cv2.COLOR_BGR2RGB)
out = cv2.cvtColor(numpy.float32(out), cv2.COLOR_RGB2BGR)

###############################################
###   To return our your output image (out) ###
###    convert from NumPy                   ###
###############################################
#output = out
output = out.astype(numpy.float32)
