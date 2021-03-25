import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import cv2, numpy

# Convert ViSUS array to numpy
# pdim = input.dims.getPointDim()
# img = Array.toNumPy(input, bShareMem=True)
img = input.astype(numpy.float32)

NIR = img[:, :, 0]
Green = img[:, :, 1]
blue = img[:, :, 2]
Red = ??
#https://www.agrocam.eu/products
NG= Green / (NIR + Red + Green)


NDVI = cv2.normalize(NG, None, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_32F)  # normalize data [0,1]

NDVI = numpy.uint8(NDVI * 255)  # color map requires 8bit.. ugh, convert again

gray = NDVI

cdict = [(.2, .4, 0), (.2, .4, 0), (.94, .83, 0), (.286, .14, .008), (.56, .019, .019)]
cmap = mpl.colors.LinearSegmentedColormap.from_list(name='my_colormap', colors=cdict, N=1000)

out = cmap(gray)

#output = Array.fromNumPy(out, TargetDim=pdim)
output = out
