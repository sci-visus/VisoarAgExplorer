import cv2
import numpy
import random

import matplotlib as mpl


############## TGI Filter #################



def get_TGI(img):
    VISOAR = True
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
    #save_image('_tgi_gray', getIntImg(gray))

    # Green, green , yellow
    # cdict=[(.2, .4,0), (.2, .4,0), (.94, .83, 0), (.286,.14,.008), (.56,.019,.019)]
    cdict = [(.56, .019, .019), (.286, .14, .008), (.94, .83, 0), (.2, .4, 0), (.2, .4, 0)]
    cmap = mpl.colors.LinearSegmentedColormap.from_list(name='my_colormap', colors=cdict, N=1000)
    color = cmap(gray)
    #save_image('_tgi_color', getIntImg(color))

    # binary
    cdict = [(0, 0, 0), (0, 0, 0), (0, 0, 0), (1, 1, 1), (1, 1, 1)]
    cmap = mpl.colors.LinearSegmentedColormap.from_list(name='my_colormap', colors=cdict, N=1000)
    binary = cmap(gray)
    #save_image('_tgi_binary', getIntImg(binary))

    return color, binary

############## Resize image, keep aspect, fit to Width #################
#
# def resizeImg(imgIn, width):
#     # print('Original Dimensions : ',imgIn.shape)
#     height = imgIn.shape[0]  # keep original height
#     dim = (width, height)
#     # resize image
#     resized = cv2.resize(imgIn, dim, interpolation=cv2.INTER_AREA)
#     return resized

############## Print Image Info for Debugging #################

# def printImgInfo(im):
#     DEBUG = False
#     if (DEBUG):
#         height, width = im.shape[:2]
#         type = im.dtype
#         print(width)
#         print(height)
#         print(type)
#         if len(im.shape) == 2:  # gives you two, it has a single channel.
#             print('img has 1 channel')
#         else:
#             if len(im.shape) == 3:
#                 print("img has 3 channels")

############## Convert Image to Int #################

# def getIntImg(im):
#     DEBUG = False
#     if im is None:
#         return []
#
#     if (im.dtype == numpy.float32) or (im.dtype == numpy.float64):
#         if len(im.shape) == 3:
#             # im = cv2.cvtColor(numpy.float32(im), cv2.COLOR_GRAY2RGB)  # data comes in 64 bit, but cvt only handles 32
#             im = numpy.uint8(im * 255)  # color map requires 8bit.. ugh, convert again
#         elif len(im.shape) == 2:
#             im = cv2.cvtColor(numpy.float32(im), cv2.COLOR_GRAY2RGB)  # data comes in 64 bit, but cvt only handles 32
#             im = numpy.uint8(im * 255)  # color map requires 8bit.. ugh, convert again
#
#     if len(im.shape) == 2:  # gives you two, it has a single channel.
#         if (DEBUG):
#             print('single channel image, converting to three')
#         im = cv2.cvtColor(numpy.float32(im), cv2.COLOR_GRAY2RGB)
#     else:
#         if len(im.shape) == 3:
#             if (DEBUG):
#                 print("img has 3 channels")
#     if (len(im.shape) == 1):
#         im = numpy.uint8(im)
#     #	return cv2.merge((im,im,im))
#
#     return im

############## Save Image Function #################

# def save_image(image_name, image_data):
#     '''Saves image if user requests before runtime'''
#     # if curr_image in images_to_save:
#     image_name_new = os.path.join(image_out_path,
#                                   "{0}{1}.jpg".format(str(save_image.IMAGE_INC), image_name))
#     save_image.IMAGE_INC += 1
#     print('saving img: ' + image_name_new)
#     cv2.imwrite(image_name_new, image_data)


############## MAIN #################

###          Read in Image        ###

#save_image.IMAGE_INC = 0
#image_out_path = os.path.abspath('/Users/amygooch/GIT/VisoarAgExplorerMay/RowLines/')

#if VISOAR:
    #pdim = input.dims.getPointDim()
    #img = Array.toNumPy(input, bShareMem=True)
#img = input.astype(numpy.float32)
# elif options.file:
#     img = cv2.imread(os.path.abspath(options.file))
# else:
VISOAR = True
if not VISOAR:
    input = cv2.imread('/Users/amygooch/GIT/VisoarAgExplorerMay/idx_example/WeedsNoMark_sm.png')

img = input.astype(numpy.float32)
print('00_input')

#img = cv2.cvtColor(input, cv2.COLOR_BGR2RGB, cv2.CV_32F )


#printImgInfo(img)

###        Apply TGI Filter      ###

TGIcolor, TGIbinary = get_TGI(img)
print('01_TGI')
# array =numpy.uint8(binaryTGI * 255)
print('colorTGI')
TGIcolor = (TGIcolor*255).astype(numpy.uint8) # getIntImg(TGIcolor)
TGIbinary = (TGIbinary*255).astype(numpy.uint8) # getIntImg(TGIbinary)
TGIbinary = cv2.cvtColor(TGIbinary, cv2.COLOR_RGB2GRAY)
print('02_TGI')
###        More to get contours      ###
height, width = TGIbinary.shape[:2]
contours, hierarchy = cv2.findContours(TGIbinary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
print('03_contours')
filteredImg = TGIcolor.astype(numpy.uint8)

for cnt in contours:
    rand_color = (random.randint(127, 255), random.randint(127, 255), random.randint(127, 255))

    area = cv2.contourArea(cnt)
    if (area > 100) and area < (height * width * .5):
        #filteredImg = cv2.drawContours(filteredImg, cnt, -1, rand_color, 3)

        rect = cv2.minAreaRect(cnt)
        box = cv2.boxPoints(rect)
        box = numpy.int0(box)
        filteredImg = cv2.drawContours(filteredImg, [box], 0, rand_color, 2)

        # hull = cv2.convexHull(cnt)
        #rows, cols = filteredImg.shape[:2]
        #[vx, vy, x, y] = cv2.fitLine(cnt, cv2.DIST_L2, 0, 0.01, 0.01)
        #lefty = int((-x * vy / vx) + y)
        #righty = int(((cols - x) * vy / vx) + y)
        #filteredImg = cv2.line(filteredImg, (cols - 1, righty), (0, lefty), rand_color, 2)
print('04_contours')
#out = cv2.cvtColor(filteredImg, cv2.COLOR_BGR2RGB)
out = filteredImg

############## OUTPUT FILE BACK TO VISUS ##############
#output = Array.fromNumPy(out, TargetDim=pdim)
output =  out
