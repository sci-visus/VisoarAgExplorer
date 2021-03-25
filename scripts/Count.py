import matplotlib
import cv2
import numpy
import imutils
import random

def find_if_close(cent1, cent2):
    import cv2
    # https://www.w3resource.com/python-exercises/basic/python-basic-1-exercise-45.php
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
        # print("Input x1, y1, r1, x2, y2, r2:")
        # x1,y1,r1,x2,y2,r2 = [float(i) for i in input().split()]
        d = math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
        if d < r1 - r2:
            # print("C2  is in C1")
            return True
        elif d < r2 - r1:
            # print("C1  is in C2")
            return True
        elif d > r1 + r2:
            # print("Circumference of C1  and C2  intersect")
            return True
        else:
            # print("C1 and C2  do not overlap")
            return False

def unifyContours(cnts, draw, target):
    import cv2
    import random
    #rand_color = (255,255,128)
    rand_color = (random.randint(127, 255), random.randint(127, 255), random.randint(127, 255))
    # https://dsp.stackexchange.com/questions/2564/opencv-c-connect-nearby-contours-based-on-distance-between-them
    UNIFY = True
    if UNIFY:
        LENGTH = len(cnts)
        status = numpy.zeros((LENGTH, 1))
        for i, cnt1 in enumerate(cnts):
            x = i
            if i != LENGTH - 1:
                for j, cnt2 in enumerate(cnts[i + 1:]):
                    x = x + 1
                    dist = find_if_close(cnt1, cnt2)
                    if dist:
                        val = min(status[i], status[x])
                        status[x] = status[i] = val
                    else:
                        if status[x] == status[i]:
                            status[x] = i + 1
        unified = []
        maximum = int(status.max()) + 1
        for i in range(maximum):
            pos = numpy.where(status == i)[0]
            if pos.size != 0:
                cont = numpy.vstack(cnts[i] for i in pos)
                if cont.any():
                    hull = cv2.convexHull(cont)
                    unified.append(hull)
        if draw:  # DRAW_OPTIMIZED_CONTOURS
            cv2.drawContours(target, unified, -1, rand_color, 4)
        return unified



mymedian = 0
mymean = 0
mymax = 0
mymin = 0
img = input.astype(numpy.float32)

red = img[:, :, 0]
green = img[:, :, 1]
blue = img[:, :, 2]
scaleRed = (0.39 * red)
scaleBlue = (.61 * blue)
TGI = green - scaleRed - scaleBlue
TGI = cv2.normalize(TGI, None, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_32F)  # normalize data [0,1]
gray = TGI
cdict = [(.56, .019, .019), (.286, .14, .008), (.94, .83, 0), (.2, .4, 0), (.2, .4, 0)]
cmap = matplotlib.colors.LinearSegmentedColormap.from_list(name='my_colormap', colors=cdict, N=1000)
out = cmap(gray)

circlesArray = []
out = cv2.cvtColor(numpy.float32(out), cv2.COLOR_RGB2BGR)
#valid, imgfile, circles_array = get_filter_img(out, circles_array)

DEBUG = False
VISOAR = False
USE_OPENING = False
target = (out * 255).astype(numpy.uint8)
gray = cv2.cvtColor(target, cv2.COLOR_RGB2GRAY)
validThresh, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
if USE_OPENING:
    # noise removal
    kernel = numpy.ones((3, 3), numpy.uint8)
    opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=2)
    if DEBUG:
        cv2.imwrite('061019_01morph.png', opening)
    # sure background area
    sure_bg = cv2.dilate(opening, kernel, iterations=3)
    if DEBUG:
        cv2.imwrite('061019_02sure_bg.png', sure_bg)
else:
    opening = thresh
    sure_bg = thresh
# Finding sure foreground area
# opening = getIntImg(opening)
dist_transform = cv2.distanceTransform(opening, cv2.DIST_L2, 5)
ret, sure_fg = cv2.threshold(dist_transform, 0.1 * dist_transform.max(), 255, 0)
# Finding unknown region
sure_fg = numpy.uint8(sure_fg)
unknown = cv2.subtract(sure_bg, sure_fg)
# Marker labelling
ret, markers = cv2.connectedComponents(sure_fg)
# Add one to all labels so that sure background is not 0, but 1
markers = markers + 1
# Now, mark the region of unknown with zero
markers[unknown == 255] = 0
markers = markers.astype('int32')
markers = cv2.watershed(target, markers)
target[markers == -1] = [255, 0, 0]
print("[INFO] {} unique segments found".format(len(numpy.unique(markers)) - 1))
# https://www.pyimagesearch.com/2015/11/02/watershed-opencv/
labels = markers
height, width = gray.shape[:2]
min_width = min(width, height)
margin = min_width - (min_width * .2)
print('Will be removing item of radius ' + str(margin))
circlesOnlyMask = numpy.zeros((height, width, 3), numpy.uint8)
# print(labels)
DRAW_ALL_CONTOURS = False
DRAW_ENCLOSING_CIRCLE = True
DRAW_MOMENTS = False
DRAW_OPTIMIZED_CONTOURS = True
all_unified = []
for label in numpy.unique(labels):
    if label == 0:
        continue
    mask = numpy.zeros(gray.shape, dtype="uint8")
    mask[labels == label] = 255
    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
                            cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    c = max(cnts, key=cv2.contourArea)
    FONT_SCALE = 5
    FONT_THICKNESS = 2
    text_to_write = '*'
    USE_CIRCLE = False
    rand_color = (random.randint(127, 255), random.randint(127, 255), random.randint(127, 255))
    ((x, y), r) = cv2.minEnclosingCircle(c)
    if r < margin:
        circlesArray.append(r)
        if DRAW_ENCLOSING_CIRCLE:
            print('Drawing Enclosing circle')
            cv2.circle(target, (int(x), int(y)), int(r), rand_color, 2)
            cv2.putText(target, text_to_write,
                        (int(x) - 10, int(y)),
                        cv2.FONT_HERSHEY_SIMPLEX, FONT_SCALE, rand_color, FONT_THICKNESS)
        centroids = []
        if DRAW_MOMENTS:
            print('Drawing Moments')
            ceach = c
            M = cv2.moments(ceach)
            if M["m00"] is not None:
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
                centroids.append((cX, cY, x, y, r))
                cv2.drawContours(target, [ceach], -1, rand_color, 2)
                cv2.circle(target, (cX, cY), 7, rand_color, -1)
        unifyContours(cnts, draw=True, target=target)
    else:
        print('removing item of radius ' + str(r))

if circlesArray:
    mymedian = numpy.median(circlesArray)
    mymean = numpy.mean(circlesArray)
    mymax = numpy.max(circlesArray)
    mymin = numpy.min(circlesArray)
    print('Median: {0} Mean: {1} [{2}, {3}]'.format(mymedian, mymean, mymax, mymin))

output = target
