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
import matplotlib as mpl
#import matplotlib.pyplot as plt
#import matplotlib.image as mpimg

###############################################
###     Convert ViSUS array to numpy        ###
###############################################

# pdim = input.dims.getPointDim()
# img = Array.toNumPy(input, bShareMem=True)
img = input.astype(numpy.float32)

###############################################
###     Get each channel of image           ###
###############################################

blue = img[:, :, 2]
output = cv2.cvtColor( blue, cv2.COLOR_GRAY2RGB)
