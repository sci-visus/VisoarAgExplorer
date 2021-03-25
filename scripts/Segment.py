
import cv2, numpy
import numpy as np
import imutils
import random
import matplotlib as mpl
#import matplotlib.pyplot as plt
#import matplotlib.image as mpimg
#DEBUG = True
#VISOAR = True


def getIntImg(im):
    DEBUG = False
    if im is None:
        return []

    if (im.dtype == np.float32) or (im.dtype == np.float64):
        if len(im.shape) == 3:
            # im = cv2.cvtColor(np.float32(im), cv2.COLOR_GRAY2RGB)  # data comes in 64 bit, but cvt only handles 32
            im = np.uint8(im * 255)  # color map requires 8bit.. ugh, convert again
        elif len(im.shape) == 2:
            im = cv2.cvtColor(np.float32(im), cv2.COLOR_GRAY2RGB)  # data comes in 64 bit, but cvt only handles 32
            im = np.uint8(im * 255)  # color map requires 8bit.. ugh, convert again

    if len(im.shape) == 2:  # gives you two, it has a single channel.
        if (DEBUG):
            print('single channel image, converting to three')
        im = cv2.cvtColor(np.float32(im), cv2.COLOR_GRAY2RGB)
    else:
        if len(im.shape) == 3:
            if (DEBUG):
                print("img has 3 channels")
    if (len(im.shape) == 1):
        im = np.uint8(im)
    #	return cv2.merge((im,im,im))

    return im


def printImgInfo(im):
    DEBUG = False
    if (DEBUG):
        height, width = im.shape[:2]
        type = im.dtype
        print(width)
        print(height)
        print(type)
        if len(im.shape) == 2:  # gives you two, it has a single channel.
            print('img has 1 channel')
        else:
            if len(im.shape) == 3:
                print("img has 3 channels")


def get_TGI(img):
    VISOAR = True
    if VISOAR:
        red = img[:, :, 0]
        green = img[:, :, 1]
        blue = img[:, :, 2]
    else:
        blue, green, red = cv2.split(img)

    # #TGI – Triangular Greenness Index - RGB index for chlorophyll sensitivity. TGI index relies on reflectance values at visible wavelengths. It #is a fairly good proxy for chlorophyll content in areas of high leaf cover.
    # #TGI = −0.5 * ((190 * (redData − greeData)) − (120*(redData − blueData)))
    scaleRed = (0.39 * red)
    scaleBlue = (.61 * blue)
    TGI = green - scaleRed - scaleBlue
    TGI = cv2.normalize(TGI, None, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_32F)  # normalize data [0,1]

    gray = TGI
    #save_image('_tgi_gray', gray)

    # Green, green , yellow
    # cdict=[(.2, .4,0), (.2, .4,0), (.94, .83, 0), (.286,.14,.008), (.56,.019,.019)]
    cdict = [(.56, .019, .019), (.286, .14, .008), (.94, .83, 0), (.2, .4, 0), (.2, .4, 0)]
    cmap = mpl.colors.LinearSegmentedColormap.from_list(name='my_colormap', colors=cdict, N=1000)
    color = cmap(gray)
    #save_image('_tgi_color', color)

    # binary
    cdict = [(0, 0, 0), (0, 0, 0), (0, 0, 0), (1, 1, 1), (1, 1, 1)]
    cmap = mpl.colors.LinearSegmentedColormap.from_list(name='my_colormap', colors=cdict, N=1000)
    binary = cmap(gray)
    #save_image('_tgi_binary', binary)

    return color, binary


def get_kmeans_img(array, K=8):
    kmeans = K

    printImgInfo(array)
    if len(array.shape) == 2:
        array = cv2.cvtColor(np.float32(array), cv2.COLOR_GRAY2RGB)

    else:
        Z = array

    Z = array.reshape((-1, 3))

    # convert to np.float32
    Z = np.float32(Z)
    # Z = np.float32(array)
    print('Z')
    printImgInfo(Z)

    # define criteria, number of clusters(K) and apply kmeans()
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)

    ret, label, center = cv2.kmeans(Z, kmeans, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)

    # Now convert back into uint8, and make original image
    center = np.uint8(center)
    res = center[label.flatten()]
    res2 = res.reshape((array.shape))
    #save_image('_kmeans_', res2)
    return res2


##################################
#  Convert ViSUS array to numpy
##################################

# pdim = input.dims.getPointDim()
# img = Array.toNumPy(input, bShareMem=True)
img = input.astype(numpy.float32)

colorTGI, binaryTGI = get_TGI(img)
array = getIntImg(colorTGI)

imgfile = get_kmeans_img(array)

#output = Array.fromNumPy(imgfile, TargetDim=pdim)
output = imgfile

