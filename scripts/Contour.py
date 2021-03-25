import cv2
import numpy
import random

import matplotlib

############## MAIN #################
img = input.astype(numpy.float32)
print('00_input')

###        Apply TGI Filter      ###

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
red = img[:, :, 0]
green = img[:, :, 1]
blue = img[:, :, 2]
scaleRed = (0.39 * red)
scaleBlue = (.61 * blue)
TGI_gray = green - scaleRed - scaleBlue
TGI_gray = cv2.normalize(TGI_gray, None, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_32F)  # normalize data [0,1]
cdict = [(.56, .019, .019), (.286, .14, .008), (.94, .83, 0), (.2, .4, 0), (.2, .4, 0)]
cmap = matplotlib.colors.LinearSegmentedColormap.from_list(name='my_colormap', colors=cdict, N=1000)
TGIcolor = cmap(TGI_gray)
cdict = [(0, 0, 0), (0, 0, 0), (0, 0, 0), (1, 1, 1), (1, 1, 1)]
cmap = matplotlib.colors.LinearSegmentedColormap.from_list(name='my_colormap', colors=cdict, N=1000)
TGIbinary = cmap(TGI_gray)
print('01_TGI')
print('colorTGI')
TGIcolor = (TGIcolor * 255).astype(numpy.uint8)
TGIbinary = (TGIbinary * 255).astype(numpy.uint8)
TGIbinary = cv2.cvtColor(TGIbinary, cv2.COLOR_RGB2GRAY)
print('02_TGI')
height, width = TGIbinary.shape[:2]
contours, hierarchy = cv2.findContours(TGIbinary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
print('03_contours')
filteredImg = TGIcolor.astype(numpy.uint8)
for cnt in contours:
    rand_color = (random.randint(127, 255), random.randint(127, 255), random.randint(127, 255))
    area = cv2.contourArea(cnt)
    if (area > 100) and area < (height * width * .5):
        rect = cv2.minAreaRect(cnt)
        box = cv2.boxPoints(rect)
        box = numpy.int0(box)
        filteredImg = cv2.drawContours(filteredImg, [box], 0, rand_color, 2)
output =filteredImg
