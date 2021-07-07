# please check if this works for you, otherwise we need to move this function outside
from OpenVisus.__main__ import MidxToIdx

# source file
midx="/Volumes/ViSUSAg/PeteSmallEnd/MAPIR/VisusSlamFiles/visus.midx"
midx="/Volumes/TenGViSUSAg/2021Season/MapIR/MAPIR\ 02 5.10.21/VisusSlamFiles/visus.midx"
midx="/Volumes/TenGViSUSAg/2021Season/MapIR/MAPIR\ 02 5.10.21/VisusSlamFiles/visus.midx"

# destination file
idx="/Volumes/ViSUSAg/PeteSmallEnd/MAPIR/VisusSlamFiles/TestIdx/test.idx"

# this is the default, works just fine
tile_size="4*1024"

# this is the python expression to extract and process the data
# NOTE you first have to convert OpenVisus array ->numpy and back
field="""
data=Array.toNumPy(voronoi())
data = data.astype(numpy.float32)
orange,cyan,NIR=data[:,:,0],data[:,:,1],data[:,:,2]
import matplotlib
import cv2, numpy
NDVI_u = (NIR - orange)
NDVI_d = (NIR + orange)+.001
NDVI = NDVI_u / NDVI_d
#map [-1,1] to [0,1]
NDVI = (NDVI+1.0)/2.0
gray = numpy.float32(NDVI)
cdictN = [ (0.56, 0.02 ,0.02), (0.74, 0.34 ,0.04), (0.94, 0.65 ,0.27), (0.2, 0.4 ,0.0), (0.2, 0.4 ,0.0),]
nodesN =[0.0,0.25,0.5,0.75,1.0,]
cmapN = matplotlib.colors.LinearSegmentedColormap.from_list("mycmap", list(zip(nodesN, cdictN)))
#out =  numpy.float32(cmapN(gray))
out =  numpy.uint8(cmapN(gray)*255)
#colomapping generates RGBA, only need RGB
out = out[...,:3]
output=Array.fromNumPy(out,TargetDim=2)

"""

MidxToIdx([
   "--midx", midx  ,
   "--tile-size",tile_size,
   "--idx", idx  ,
   "--field",field
])