import matplotlib
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import cv2, numpy

# Convert ViSUS array to numpy
# pdim = input.dims.getPointDim()
# img = Array.toNumPy(input, bShareMem=True)
img = input.astype(numpy.float32)

orange = img[:, :, 0]
cyan = img[:, :, 1]
NIR = img[:, :, 2]

NDVI_u = (NIR - orange)
NDVI_d = (NIR + orange)
NDVI_d[NDVI_d == 0] = 0.01
NDVI = NDVI_u / NDVI_d
#NDVI = cv2.normalize(NDVI, None, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_32F)  # normalize data [0,1]

gray = numpy.float32(NDVI)

colors = ["darkred", "darkred", "gold", "yellowgreen", "darkgreen", "darkgreen"]
nodes = [0.0, 0.3, 0.6, 0.7, 0.79, 1.0]
cmap = matplotlib.colors.LinearSegmentedColormap.from_list("mycmap", list(zip(nodes, colors)))
out = cmap(gray)

out = cv2.cvtColor(numpy.float32(out), cv2.COLOR_BGR2RGB)
out = cv2.cvtColor(numpy.float32(out), cv2.COLOR_RGB2BGR)

# output = Array.fromNumPy(out, TargetDim=pdim)
output = out.astype(numpy.float32)
