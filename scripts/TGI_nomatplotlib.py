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

def getPaintColors():
    if False:
        greenpaint = numpy.uint8(numpy.array([.2, .4, 0]) * 255)
        yellowpaint = numpy.uint8(numpy.array([.94, .83, 0]) * 255)
        bluepaint = numpy.uint8(numpy.array([.286, .14, .008]) * 255)
        redpaint = numpy.uint8(numpy.array([.56, .019, .019]) * 255)
    else:
        greenpaint = numpy.uint8(numpy.array([0, .4, .2]) * 255)
        yellowpaint = numpy.uint8(numpy.array([0, .83, .94]) * 255)
        bluepaint = numpy.uint8(numpy.array([.008, .14, .286]) * 255)
        redpaint = numpy.uint8(numpy.array([.019, .019, .56]) * 255)
    return greenpaint, yellowpaint, bluepaint, redpaint


img = input.astype(numpy.float32)
#img = cv2.cvtColor(input, cv2.COLOR_BGR2RGB)

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

#TGI RANGES  -1 to 1
# As NDVI values close to zero represent bare soil,
# thus I prefer grey-yellow-beige colors,
# NDVI close to 1 represents living vegetation,
# thus, I prefer green colors.
# Negative values are often displayed "blue" for water.


TGI = (TGI + 1.0 )/ 2.0   #TGI RANGES  -1 to 1, fix it [0,1]
#TGI = cv2.normalize(TGI, None, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_32F)  # normalize data [0,1]



# cdict=[(.2, .4,0), (.2, .4,0), (.94, .83, 0), (.286,.14,.008), (.56,.019,.019)]
#cdict = [(.56, .019, .019), (.286, .14, .008), (.94, .83, 0), (.2, .4, 0), (.2, .4, 0)]
#cmap = mpl.colors.LinearSegmentedColormap.from_list(name='my_colormap', colors=cdict, N=1000)


#TGI RANGES  0 to 1
# beige = As NDVI values close to .5 represent bare soil,

# green = NDVI .8 to 1 represents living vegetation,

# 0 to .4 are often displayed "blue" for water.


#lut_8u_1 = np.interp(np.arange(0, 100), red, blue).astype(np.uint8)
#lut_8u_2 = np.interp(np.arange(100,130), blue, yellow).astype(np.uint8)
#lut_8u_3 = np.interp(np.arange(130, 256), yellow, green).astype(np.uint8)
#image_contrasted = cv2.LUT(image, lut_8u)

#lut = numpy.zeros((256, 1, 3), dtype=numpy.uint8)
#lut[]
gray = cv2.cvtColor(TGI,cv2.COLOR_GRAY2RGB)
grayi = 255 - numpy.uint8(gray * 255)

greenpaint, yellowpaint, bluepaint, redpaint = getPaintColors()

redChannel, greenChannel, blueChannel = cv2.split(grayi)

#out = cmap(gray)

# get min and max on image and map original values to those in percentage steps
# instead of using 0 to 255 over images (we need to find the dynamic range of the image and use its range for the mapping)
# may need to do this for TGI



if False:
    greenpt = 0 + 255 * .4
    yellowpt = greenpt + 255 * .1
    bluept = yellowpt + 255 * .3
    redpt = bluept + 255 * .2

    originalValues = numpy.array([0, greenpt, yellowpt, bluept, redpt, 255])

    redValues =      numpy.array([greenpaint[0],greenpaint[0],  yellowpaint[0], bluepaint[0], redpaint[0], redpaint[0] ])

    blueValues =     numpy.array([greenpaint[1],greenpaint[1],  yellowpaint[1], bluepaint[1], redpaint[1], redpaint[1]  ])
    greenValues =    numpy.array([greenpaint[2],greenpaint[2],  yellowpaint[2], bluepaint[2], redpaint[2], redpaint[2]  ])
else:
    greenpt = 255 - (255 * .4)
    yellowpt = greenpt - (255 * .1)
    bluept = yellowpt - (255 * .3)
    redpt = bluept - (255 * .2)

    originalValues = numpy.array([0, redpt, bluept, yellowpt, greenpt, 255])

    redValues = numpy.array([redpaint[0], redpaint[0], bluepaint[0], yellowpaint[0], greenpaint[0], greenpaint[0]])

    blueValues = numpy.array([redpaint[1], redpaint[1], bluepaint[1], yellowpaint[1], greenpaint[1], greenpaint[1]])
    greenValues = numpy.array(
        [redpaint[2], redpaint[2], bluepaint[2], yellowpaint[2], greenpaint[2], greenpaint[2]])

#Creating the lookuptables
fullRange = numpy.uint8(numpy.arange(0,256  ))

#Creating the lookuptable for blue channel
blueLookupTable = numpy.uint8(numpy.interp(fullRange, originalValues, blueValues ))
#Creating the lookuptables for green channel
greenLookupTable = numpy.uint8(numpy.interp(fullRange, originalValues, greenValues ))
#Creating the lookuptables for red channel
redLookupTable = numpy.uint8(numpy.interp(fullRange, originalValues, redValues ))


#cmap = cv2.merge([blueLookupTable, greenLookupTable, redLookupTable])
cmap = cv2.merge([redLookupTable, greenLookupTable, blueLookupTable])



out = cv2.applyColorMap(grayi, cmap)
out = cv2.cvtColor(out, cv2.COLOR_BGR2RGB)

###############################################
###   To return our your output image (out) ###
###    convert from NumPy                   ###
###############################################

output = (out/255.0).astype(numpy.float32)
#output = (grayi/255.0).astype(numpy.float32)
