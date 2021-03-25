import cv2,numpy

#Convert ViSUS array to numpy
#pdim=input.dims.getPointDim()
#img=Array.toNumPy(input,bShareMem=True)

img = input.astype(numpy.float32)

gray = cv2.cvtColor(img,cv2.COLOR_RGB2GRAY)
grayi = numpy.uint8(gray * 255)
valid,thresh = cv2.threshold(grayi,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
thresh = cv2.cvtColor(thresh,cv2.COLOR_GRAY2RGB)  #for some reason, the grayscale image was not correctly converting to Qimage

#output=Array.fromNumPy(thresh,TargetDim=pdim)
output= thresh