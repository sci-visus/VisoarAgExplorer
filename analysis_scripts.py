import sys, os



NDVI_SCRIPT = """

""".strip()




TGI_OLD = """
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import cv2,numpy

#COnvert ViSUS array to numpy
pdim=input.dims.getPointDim()
img=Array.toNumPy(input,bShareMem=True)

red = img[:,:,0]   
green = img[:,:,1]
blue = img[:,:,2]

print('RED CHANNEL')
print(red.shape)
print(red)
print('Image size {}'.format(red.size))
print('Maximum RGB value in this image {}'.format(red.max()))
print('Minimum RGB value in this image {}'.format(red.min()))

# #TGI – Triangular Greenness Index - RGB index for chlorophyll sensitivity. TGI index relies on reflectance values at visible wavelengths. It #is a fairly good proxy for chlorophyll content in areas of high leaf cover.
# #TGI = −0.5 * ((190 * (redData − greeData)) − (120*(redData − blueData)))
scaleRed  = (0.39 * red)
scaleBlue = (.61 * blue)
TGI =  green - scaleRed - scaleBlue
TGI = cv2.normalize(TGI, None, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_32F) #  normalize data [0,1]
		
print("TGI")
print(TGI.shape)
print(TGI)
print('Image size {}'.format(TGI.size))
print('Maximum RGB value in this image {}'.format(TGI.max()))
print('Minimum RGB value in this image {}'.format(TGI.min()))

#NDVI = cv2.cvtColor(numpy.float32(TGI), cv2.COLOR_GRAY2RGB)  # data comes in 64 bit, but cvt only handles 32
NDVI =numpy.uint8(TGI * 255)  #color map requires 8bit.. ugh, convert again
#print(NDVI.shape)

gray = NDVI

print("gray")
print(gray.shape)
print(gray)
print('Image size {}'.format(gray.size))
print('Maximum RGB value in this image {}'.format(gray.max()))
print('Minimum RGB value in this image {}'.format(gray.min()))

#https://www.programcreek.com/python/example/89433/cv2.applyColorMap
mx = 256  # if gray.dtype==numpy.uint8 else 65535
lut = numpy.empty(shape=(256, 3))
# cmap = (
# 	(0, (6,6,127)),
# 	(0.2, (6,6,127)),
# 	(0.5, (34, 169,169)),
# 	(0.8, (51,102,0)),
# 	(1.0, (51,102,0) )
# )
#New one.. brow to red, yellow, green at top
cmap = (
	(0, (73,36,2)),
	(0.2, (142,5,5)),
	(0.3, (239, 211, 0)),
	(0.8, (51,102,0)),
	(1.0, (51,102,0) )
)

# cmap = (
# 	# taken from pyqtgraph GradientEditorItem
# 	(0, (127, 6,6)),
# 	(0.2, (127, 6,6,127)),
# 	(0.5, (169,169,34)),
# 	(0.8, (0,102,51)),
# 	(1.0, (0,102,51) )
# )

print(cmap[0])
lastval = cmap[0][0]
lastcol = cmap[0][1]

# build lookup table:
lastval, lastcol = cmap[0]
for step, col in cmap[1:]:
	val = int(step * mx)
	for i in range(3):
		lut[lastval:val, i] = numpy.linspace(
			lastcol[i], col[i], val - lastval)

	lastcol = col
	lastval = val

s0, s1 = gray.shape
out = numpy.empty(shape=(s0, s1, 3), dtype=numpy.uint8)

for i in range(3):
	out[..., i] = cv2.LUT(gray, lut[:, i])


print("out")
print(out.shape)
print(out)
print('Image size {}'.format(out.size))
print('Maximum RGB value in this image {}'.format(out.max()))
print('Minimum RGB value in this image {}'.format(out.min()))

out =  numpy.float32(out) 

output=Array.fromNumPy(out,TargetDim=pdim) 

""".strip()



TGI_THRESHOLD_SCRIPT = """


""".strip()


NDVI_THRESHOLD_SCRIPT = """


""".strip()



THRESHOLD_SCRIPT = """


""".strip()

COUNT_SCRIPT = """


""".strip()

ROW_SCRIPT1 = """


import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import cv2, numpy
import numpy as np
import imutils
import random

DEBUG = True


def getIntImg(im):
	if im is None:
		return []

	if (im.dtype ==np.float32) or (im.dtype ==np.float64) :
		if len(im.shape) == 3:
			#im = cv2.cvtColor(np.float32(im), cv2.COLOR_GRAY2RGB)  # data comes in 64 bit, but cvt only handles 32
			im =np.uint8(im * 255)  #color map requires 8bit.. ugh, convert again
		elif len(im.shape) == 2:
			im = cv2.cvtColor(np.float32(im), cv2.COLOR_GRAY2RGB)  # data comes in 64 bit, but cvt only handles 32
			im =np.uint8(im * 255)  #color map requires 8bit.. ugh, convert again

	if len(im.shape)==2: # gives you two, it has a single channel.
		if (DEBUG) :
			print('single channel image, converting to three')
		im = cv2.cvtColor(np.float32(im), cv2.COLOR_GRAY2RGB) 
	else: 
		if len(im.shape) == 3:
			if (DEBUG):
				print("img has 3 channels")
	if (len(im.shape) == 1):
	    im =np.uint8(im)
	#	return cv2.merge((im,im,im))

	return im

def printImgInfo( im):
	if (DEBUG):
		height, width = im.shape[:2]
		type = im.dtype
		print(width)
		print(height)
		print(type)
		if len(im.shape)==2: # gives you two, it has a single channel.
			print('img has 1 channel')
		else: 
			if len(im.shape) == 3:
				print("img has 3 channels")


    # self.plotWidget = qtmpl.MplWidget(self.central_widget)
    # # *****
    # self.plotWidget.setGeometry(QRect(20, 250, 821, 591))
    # self.plotWidget.setObjectName("plotWidget")

def find_if_close( cent1, cent2):
    #https://www.w3resource.com/python-exercises/basic/python-basic-1-exercise-45.php

    ((x1, y1), r1) = cv2.minEnclosingCircle(cent1)
    ((x2, y2), r2) = cv2.minEnclosingCircle(cent2)

    M1 = cv2.moments(cent1)
    if M1["m00"] is not None:
        cX1 = int(M1["m10"] / M1["m00"])
        cY1 = int(M1["m01"] / M1["m00"])
        M1 = cv2.moments(cent1)
        cX1 = int(M1["m10"] / M1["m00"])
        cY1 = int(M1["m01"] / M1["m00"])

        import math
        #print("Input x1, y1, r1, x2, y2, r2:")
        #x1,y1,r1,x2,y2,r2 = [float(i) for i in input().split()]
        d = math.sqrt((x1-x2)**2 + (y1-y2)**2)
        if d < r1-r2:
            #print("C2  is in C1")
            return True
        elif d < r2-r1:
            #print("C1  is in C2")
            return True
        elif d > r1+r2:
            #print("Circumference of C1  and C2  intersect")
            return True
        else:
            #print("C1 and C2  do not overlap")
            return False

def unifyContours( cnts, draw, target ):
    rand_color =  (random.randint(127, 255), random.randint(127, 255), random.randint(127, 255))
    #https://dsp.stackexchange.com/questions/2564/opencv-c-connect-nearby-contours-based-on-distance-between-them
    UNIFY = True
    if UNIFY:
        LENGTH = len(cnts)
        status = np.zeros((LENGTH,1))

        for i,cnt1 in enumerate(cnts):
            x = i    
            if i != LENGTH-1:
                for j,cnt2 in enumerate(cnts[i+1:]):
                    x = x+1
                    dist = find_if_close(cnt1,cnt2)
                    if dist == True:
                        val = min(status[i],status[x])
                        status[x] = status[i] = val
                    else:
                        if status[x]==status[i]:
                            status[x] = i+1

        unified = []
        maximum = int(status.max())+1
        for i in range(maximum):
            pos = np.where(status==i)[0]
            if pos.size != 0:
                cont = np.vstack(cnts[i] for i in pos)
                hull = cv2.convexHull(cont)
                unified.append(hull)

        if (draw): #DRAW_OPTIMIZED_CONTOURS
            cv2.drawContours(target,unified,-1,rand_color,4)
        return unified

def get_filter_img( target, circles_array):
    mymedian = 0
    mymean =0
    mymax = 0
    mymin = 0
    circles_array = []

    USE_OPENING = False
    #print('count filter input')
    #printImgInfo
    #print('count filter input target')
    valid = 1

    target = getIntImg(target)

    output = target.copy()
    gray = cv2.cvtColor(target,cv2.COLOR_RGB2GRAY)
    #return valid,gray

    valid, thresh = cv2.threshold(gray,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)

    printImgInfo(thresh)
    if DEBUG: 
        cv2.imwrite('061019_00thresh.png',thresh)
    #return valid,thresh

    if (USE_OPENING) :
        # noise removal
        kernel = np.ones((3,3),np.uint8)
        opening = cv2.morphologyEx(thresh,cv2.MORPH_OPEN,kernel, iterations = 2)
        if DEBUG: 
            cv2.imwrite('061019_01morph.png',opening)
        #return valid,opening
        # sure background area
        sure_bg = cv2.dilate(opening,kernel,iterations=3)
        if DEBUG: 
            cv2.imwrite('061019_02sure_bg.png',sure_bg)
    else: 
        opening = thresh
        #opening = np.uint8(opening)
        sure_bg = thresh
        #sure_bg = np.uint8(sure_bg)

    #return valid,sure_bg

    # Finding sure foreground area
    #opening = getIntImg(opening)
    dist_transform = cv2.distanceTransform(opening,cv2.DIST_L2,5)
    ret, sure_fg = cv2.threshold(dist_transform,0.1*dist_transform.max(),255,0)

    # Finding unknown region
    sure_fg = np.uint8(sure_fg)
    if DEBUG: 
        cv2.imwrite('061019_03sure_fg.png',sure_fg)

    unknown = cv2.subtract(sure_bg,sure_fg)
    if DEBUG: 
        cv2.imwrite('061019_04unknown.png',unknown)

    # Marker labelling
    ret, markers = cv2.connectedComponents(sure_fg)

    # Add one to all labels so that sure background is not 0, but 1
    markers = markers+1

    # Now, mark the region of unknown with zero
    markers[unknown==255] = 0
    markers = markers.astype('int32') 
    markers = cv2.watershed(target,markers)
    target[markers == -1] = [255,0,0]
    #return valid, target

    if DEBUG: 
        cv2.imwrite('061019_05countimg.png',target)

    print("[INFO] {} unique segments found".format(len(np.unique(markers)) - 1))
    #https://www.pyimagesearch.com/2015/11/02/watershed-opencv/
    labels = markers

    minLineLength = 100
    maxLineGap = 10
    lines = cv2.HoughLinesP(target,1,np.pi/180,100,minLineLength,maxLineGap)
    for x1,y1,x2,y2 in lines[0]:
        cv2.line(target,(x1,y1),(x2,y2),(0,255,0),2)

   

    return valid, lines
    #return valid, circlesOnlyMask
    #return valid, circlesGray
    #return valid, gray

def get_TGI(img):
	red = img[:,:,0]   
	green = img[:,:,1]
	blue = img[:,:,2]

	# #TGI – Triangular Greenness Index - RGB index for chlorophyll sensitivity. TGI index relies on reflectance values at visible wavelengths. It #is a fairly good proxy for chlorophyll content in areas of high leaf cover.
	# #TGI = −0.5 * ((190 * (redData − greeData)) − (120*(redData − blueData)))
	scaleRed  = (0.39 * red)
	scaleBlue = (.61 * blue)
	TGI =  green - scaleRed - scaleBlue
	TGI = cv2.normalize(TGI, None, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_32F) #  normalize data [0,1]

	gray = TGI

	cdict=[(.2, .4,0), (.2, .4,0), (.94, .83, 0), (.286,.14,.008), (.56,.019,.019)]
	cmap = mpl.colors.LinearSegmentedColormap.from_list(name='my_colormap',colors=cdict,N=1000)
	out = cmap(gray)
	return out
	
def RowLines(img):
    img = getIntImg(img)
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray,50,150,apertureSize = 3)
    
    lines = cv2.HoughLines(edges,1,np.pi/180,200)
    for rho,theta in lines[0]:
        a = np.cos(theta)
        b = np.sin(theta)
        x0 = a*rho
        y0 = b*rho
        x1 = int(x0 + 1000*(-b))
        y1 = int(y0 + 1000*(a))
        x2 = int(x0 - 1000*(-b))
        y2 = int(y0 - 1000*(a))
    
        cv2.line(img,(x1,y1),(x2,y2),(0,0,255),2)
    
    return(img)

#COnvert ViSUS array to numpy
pdim=input.dims.getPointDim()
img=Array.toNumPy(input,bShareMem=True)

out = get_TGI(img)

#thresh = get_threshold(out)

circles_array = []

#This is the most important line.. getting input converted so CV can use it!
out =  cv2.cvtColor(np.float32(out), cv2.COLOR_RGB2BGR)  

#OpenCV processing to filter and count
#valid, imgfile = get_filter_img(out, circles_array)

imgfile = RowLines(out)

output=Array.fromNumPy(imgfile,TargetDim=pdim)
""".strip()

SEGMENT_SCRIPT = """


""".strip()


ROW_SCRIPT = """

""".strip()

