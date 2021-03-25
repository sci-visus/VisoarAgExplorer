import cv2, numpy
import matplotlib as mpl

# Convert ViSUS array to numpy
# pdim = input.dims.getPointDim()
# img = Array.toNumPy(input, bShareMem=True)
img = input.astype(numpy.float32)

RED = img[:, :, 0]
NIR = img[:, :, 1]


#Get rid of bad pixels:
#badPixels = np.array([255,255,255], dtype = "float32")
badPixels = numpy.zeros(NIR.shape, dtype = "float32")
badPixels[numpy.where(NIR == [255])] = [255]
NIR[numpy.where(NIR == [255])] = [0]

NDVI_u = (NIR - RED)
NDVI_d = (NIR + RED)
NDVI_d[numpy.where(NDVI_d == [0])] = [1]
NDVI = NDVI_u / NDVI_d

NDVI = cv2.normalize(NDVI, None, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_32F)  # normalize data [0,1]

NDVI = numpy.uint8(NDVI * 255)  # color map requires 8bit.. ugh, convert again

gray = NDVI

cdict = [(.2, .4, 0), (.2, .4, 0), (.94, .83, 0), (.286, .14, .008), (.56, .019, .019)]
cmap = mpl.colors.LinearSegmentedColormap.from_list(name='my_colormap', colors=cdict, N=1000)

out = cmap(gray)

#output = Array.fromNumPy(out, TargetDim=pdim)
output = out
