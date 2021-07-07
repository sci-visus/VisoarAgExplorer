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
#map [-1,1] to [0,1]
NDVI = (NDVI+1.0)/2.0
#NDVI = cv2.normalize(NDVI, None, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_32F)  # normalize data [0,1]

gray = numpy.float32(NDVI)

sandpt =   (255/255.0, 238/255.0, 204/255.0)
lawngreenpt = (51/255.0, 153/255.0, 51/255.0)
greenpt =  (0/255.0, 102/255.0, 0/255.0)
darkgreenpt=(0, 51/255.0, 0)
redPt =  (153/255.0, 0, 0)
orangept = (255/255.0, 204/255.0, 128/255.0)

cdictN = [ redPt, orangept,sandpt,greenpt, darkgreenpt ]

#cdictN = [ (0.56, 0.02 ,0.02), (0.74, 0.34 ,0.04), (0.94, 0.65 ,0.27), (0.2, 0.4 ,0.0), (0.2, 0.4 ,0.0),]
nodesN =[0.0,0.25,0.5,0.75,1.0,]
cmapN = matplotlib.colors.LinearSegmentedColormap.from_list("mycmap", list(zip(nodesN, cdictN)))

colors = ["darkred", "darkred", "gold", "yellowgreen", "darkgreen", "darkgreen"]
nodes = [0.0, 0.3, 0.6, 0.7, 0.79, 1.0]
cmap = matplotlib.colors.LinearSegmentedColormap.from_list("mycmap", list(zip(nodes, colors)))
#out = cmapN(gray)
out =  numpy.uint8(cmapN(gray)*255)
#colomapping generates RGBA, only need RGB
out = out[...,:3]
#
# out = cv2.cvtColor(numpy.float32(out), cv2.COLOR_BGR2RGB)
# out = cv2.cvtColor(numpy.float32(out), cv2.COLOR_RGB2BGR)

# output = Array.fromNumPy(out, TargetDim=pdim)
output = out.astype(numpy.uint8)
