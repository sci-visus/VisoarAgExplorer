import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import cv2, numpy

# COnvert ViSUS array to numpy
# pdim = input.dims.getPointDim()
# img = Array.toNumPy(input, bShareMem=True)
img = input.astype(numpy.float32)

red = img[:, :, 0]
green = img[:, :, 1]
blue = img[:, :, 2]

# #TGI – Triangular Greenness Index - RGB index for chlorophyll sensitivity. TGI index relies on reflectance values at visible wavelengths. It #is a fairly good proxy for chlorophyll content in areas of high leaf cover.
# #TGI = −0.5 * ((190 * (redData − greeData)) − (120*(redData − blueData)))
scaleRed = (0.39 * red)
scaleBlue = (.61 * blue)
TGI = green - scaleRed - scaleBlue
TGI = cv2.normalize(TGI, None, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_32F)  # normalize data [0,1]

gray = TGI

cdict = [(.2, .4, 0), (.2, .4, 0), (.94, .83, 0), (.286, .14, .008), (.56, .019, .019)]
cmap = mpl.colors.LinearSegmentedColormap.from_list(name='my_colormap', colors=cdict, N=1000)
out = cmap(gray)
# output1=Array.fromNumPy(out,TargetDim=pdim)
# pdim=output1.dims.getPointDim()
# img=Array.toNumPy(output1,bShareMem=True)

gray = cv2.cvtColor(numpy.float32(out), cv2.COLOR_RGB2GRAY)
grayi = numpy.uint8(gray * 255)
valid, thresh = cv2.threshold(grayi, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
thresh = cv2.cvtColor(thresh,
                      cv2.COLOR_GRAY2RGB)  # for some reason, the grayscale image was not correctly converting to Qimage

#output = Array.fromNumPy(thresh, TargetDim=pdim)
output = thresh

