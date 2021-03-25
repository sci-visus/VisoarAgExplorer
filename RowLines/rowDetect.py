
import os
import os.path
import time

import cv2
import numpy as np
import math

import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.image as mpimg


DEBUG = True
VISOAR = False

HOUGH_RHO = 100                      # Distance resolution of the accumulator in pixels
HOUGH_ANGLE = math.pi*45.0/180     # Angle resolution of the accumulator in radians
HOUGH_THRESH_MAX = 100             # Accumulator threshold parameter. Only those lines are returned that get enough votes
HOUGH_THRESH_MIN = 10
HOUGH_THRESH_INCR = 1

NUMBER_OF_ROWS = 10  # how many crop rows to detect

THETA_SIM_THRESH = math.pi*(6.0/180)   # How similar two rows can be
RHO_SIM_THRESH = 8   # How similar two rows can be
ANGLE_THRESH = math.pi*(20.0/180) # How steep angles the crop rows can be in radians

 

def getRowLines(TGIcolor, TGIbinary):
    '''Inputs an image and outputs the lines'''
    image_in = TGIbinary

    save_image('_image_in', image_in)
    

    ### Grayscale Transform ###
    #image_edit = grayscale_transform(image_in)
   
    gray = cv2.cvtColor(image_in,cv2.COLOR_BGR2GRAY)
    save_image('_image_gray', gray)
   
    USE_SKELETON = True
    USE_SIMPLE_HOUGH = True

    if USE_SKELETON:
        skeleton = skeletonize(gray)
        save_image('_image_skeleton', skeleton)
    else: 
        skeleton = gray

    # Apply edge detection method on the image 
    #apertureSize = 3
    #skeleton = cv2.Canny(skeleton,50,150,apertureSize = 3) 
    #save_image('2_image_canny'+ str(apertureSize), skeleton)

    if USE_SIMPLE_HOUGH:
        return getHough(TGIcolor, skeleton)

    else :

        ### Hough Transform ###
        (crop_lines, crop_lines_hough) = crop_point_hough(skeleton)

        save_image('3_image_hough',   crop_lines_hough )
        save_image('4_image_lines',  crop_lines)

        #save_image('3_image_hough', cv2.addWeighted(image_in, 1, crop_lines_hough, 1, 0.0))
        #save_image('4_image_lines', cv2.addWeighted(image_in, 1, crop_lines, 1, 0.0))

        return crop_lines

def getHough(img, edges):
    # This returns an array of r and theta values 
    #lines = cv2.HoughLines(edges,1,np.pi/180, 200) 
    lines = cv2.HoughLines(edges,1,HOUGH_ANGLE, 200) 
    #lines =cv2.HoughLines(edges,1,np.pi/180,150,200)
    print('Lines from HoughLines')
    print (lines)
      
    # The below for loop runs till r and theta values  
    # are in the range of the 2d array 
       # for line in lines:
       #  for rho, theta in line:
       #      a = np.cos(theta)
       #      b = np.sin(theta)
       #      x0 = a * rho
       #      y0 = b * rho
       #      x1 = int(x0 + 1000 * (-b))
       #      y1 = int(y0 + 1000 * (a))
       #      x2 = int(x0 - 1000 * (-b))
       #      y2 = int(y0 - 1000 * (a))
       #      if theta > np.pi / 3 and theta < np.pi * 2 / 3:
       #          thetas.append(theta)
       #          new = cv2.line(new, (x1, y1), (x2, y2), (255, 255, 255), 1)

    thetas = []

    try:
        for line in lines:
            for r,theta in line: 
                  
                # Stores the value of cos(theta) in a 
                a = np.cos(theta) 
              
                # Stores the value of sin(theta) in b 
                b = np.sin(theta) 
                  
                # x0 stores the value rcos(theta) 
                x0 = a*r 
                  
                # y0 stores the value rsin(theta) 
                y0 = b*r 
                  
                # x1 stores the rounded off value of (rcos(theta)-1000sin(theta)) 
                x1 = int(x0 + 1000*(-b)) 
                  
                # y1 stores the rounded off value of (rsin(theta)+1000cos(theta)) 
                y1 = int(y0 + 1000*(a)) 
              
                # x2 stores the rounded off value of (rcos(theta)+1000sin(theta)) 
                x2 = int(x0 - 1000*(-b)) 
                  
                # y2 stores the rounded off value of (rsin(theta)-1000cos(theta)) 
                y2 = int(y0 - 1000*(a)) 
                  
                # cv2.line draws a line in img from the point(x1,y1) to (x2,y2). 
               
                #if theta > np.pi / 3 and theta < np.pi * 2 / 3:
                #     thetas.append(theta)
                #    img = cv2.line(img,(x1,y1), (x2,y2), (100,255,100),2) 


                img = cv2.line(img,(x1,y1), (x2,y2), (100,255,100),2) 
    except:
        print('ERROR: Hough did not work!')
        pass
  
          
        
    save_image('_withLines', img)
    return img


def skeletonize(image_in):
    '''Inputs and grayscale image and outputs a binary skeleton image'''
    size = np.size(image_in)
    skel = np.zeros(image_in.shape, np.uint8)

    ret, image_edit = cv2.threshold(image_in, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    element = cv2.getStructuringElement(cv2.MORPH_CROSS, (3,3))
    done = False

    while not done:
        eroded = cv2.erode(image_edit, element)
        temp = cv2.dilate(eroded, element)
        temp = cv2.subtract(image_edit, temp)
        skel = cv2.bitwise_or(skel, temp)
        image_edit = eroded.copy()

        zeros = size - cv2.countNonZero(image_edit)
        if zeros == size:
            done = True

    return skel


def tuple_list_round(tuple_list, ndigits_1=0, ndigits_2=0):
    '''Rounds each value in a list of tuples to the number of digits
       specified
    '''
    new_list = []
    for (value_1, value_2) in tuple_list:
        new_list.append( (round(value_1, ndigits_1), round(value_2, ndigits_2)) )

    return new_list

def crop_point_hough(crop_points):
    '''Iterates though Hough thresholds until optimal value found for
       the desired number of crop rows. Also does filtering.
    '''

    height = len(crop_points)
    width = len(crop_points[0])

    hough_thresh = HOUGH_THRESH_MAX
    rows_found = False

    while hough_thresh > HOUGH_THRESH_MIN and not rows_found:
        crop_line_data = cv2.HoughLines(crop_points, HOUGH_RHO, HOUGH_ANGLE, hough_thresh)

        crop_lines = np.zeros((height, width, 3), dtype=np.uint8)
        crop_lines_hough = np.zeros((height, width, 3), dtype=np.uint8)
        #print('CropLineData type = '+    type(crop_line_data))

        
        if  crop_line_data.any(): 
        # != None:

            # get rid of duplicate lines. May become redundant if a similarity threshold is done
            crop_line_data_1 = tuple_list_round(crop_line_data[0], -1, 4)
            crop_line_data_2 = []

            crop_lines_hough = np.zeros((height, width, 3), dtype=np.uint8)
            for (rho, theta) in crop_line_data_1:

                a = math.cos(theta)
                b = math.sin(theta)
                x0 = a*rho
                y0 = b*rho
                point1 = (int(round(x0+1000*(-b))), int(round(y0+1000*(a))))
                point2 = (int(round(x0-1000*(-b))), int(round(y0-1000*(a))))
                cv2.line(crop_lines_hough, point1, point2, (0, 0, 255), 2)


            for curr_index in range(len(crop_line_data_1)):
                (rho, theta) = crop_line_data_1[curr_index]

                is_faulty = False
                if ((theta >= ANGLE_THRESH) and (theta <= math.pi-ANGLE_THRESH)) or (theta <= 0.0001):
                    is_faulty = True

                else:
                    for (other_rho, other_theta) in crop_line_data_1[curr_index+1:]:
                        if abs(theta - other_theta) < THETA_SIM_THRESH:
                            is_faulty = True
                        elif abs(rho - other_rho) < RHO_SIM_THRESH:
                            is_faulty = True

                if not is_faulty:
                    crop_line_data_2.append( (rho, theta) )



            for (rho, theta) in crop_line_data_2:

                a = math.cos(theta)
                b = math.sin(theta)
                x0 = a*rho
                y0 = b*rho
                point1 = (int(round(x0+1000*(-b))), int(round(y0+1000*(a))))
                point2 = (int(round(x0-1000*(-b))), int(round(y0-1000*(a))))
                cv2.line(crop_lines, point1, point2, (0, 0, 255), 2)


            if len(crop_line_data_2) >= NUMBER_OF_ROWS:
                rows_found = True


        hough_thresh -= HOUGH_THRESH_INCR

    if rows_found == False:
        print(NUMBER_OF_ROWS, "rows_not_found")


    return (crop_lines, crop_lines_hough)

def get_TGI(img):
    if VISOAR:
        red = img[:,:,0]
        green = img[:,:,1]
        blue = img[:,:,2]
    else:
        blue, green, red = cv2.split(img)

    # #TGI – Triangular Greenness Index - RGB index for chlorophyll sensitivity. TGI index relies on reflectance values at visible wavelengths. It #is a fairly good proxy for chlorophyll content in areas of high leaf cover.
    # #TGI = −0.5 * ((190 * (redData − greeData)) − (120*(redData − blueData)))
    scaleRed  = (0.39 * red)
    scaleBlue = (.61 * blue)
    TGI =  green - scaleRed - scaleBlue
    TGI = cv2.normalize(TGI, None, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_32F) #  normalize data [0,1]

    gray = TGI
    save_image('_tgi_gray', getIntImg (gray))

    # Green, green , yellow
    #cdict=[(.2, .4,0), (.2, .4,0), (.94, .83, 0), (.286,.14,.008), (.56,.019,.019)]
    cdict=[(.56,.019,.019),(.286,.14,.008),(.94, .83, 0),(.2, .4,0), (.2, .4,0)  ]
    cmap = mpl.colors.LinearSegmentedColormap.from_list(name='my_colormap',colors=cdict,N=1000)
    color = cmap(gray)
    save_image('_tgi_color',  getIntImg (color))
   
    #binary
    cdict=[(0,0,0), (0,0,0), (0,0,0), (1,1,1), (1,1,1)]
    cmap = mpl.colors.LinearSegmentedColormap.from_list(name='my_colormap',colors=cdict,N=1000)
    binary = cmap(gray)
    save_image('_tgi_binary',  getIntImg (binary))

    return color, binary

def resizeImg(imgIn, width):
    #print('Original Dimensions : ',imgIn.shape)
    height = imgIn.shape[0] # keep original height
    dim = (width, height)
    # resize image
    resized = cv2.resize(imgIn, dim, interpolation = cv2.INTER_AREA)
    return resized

def get_kmeans_img(array,  K=8):
    kmeans = K

    printImgInfo(array)
    if len(array.shape) == 2:
        array = cv2.cvtColor(np.float32(array), cv2.COLOR_GRAY2RGB)
        
    else:
        Z = array

    Z = resizeImg(Z, 600)
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
    #res2 = cv2.cvtColor(res2, cv2.COLOR_BGR2RGB)
    save_image('_kmeans_'+str(K)+'_scaled_',res2)
    return res2

def get_kmeans_img2(img):
    import numpy as np
    import cv2

    Z = resizeImg(Z, 600)
    Z = img.reshape((-1,3))

    # convert to np.float32
    Z = np.float32(Z)

    # define criteria, number of clusters(K) and apply kmeans()
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    K = 8
    ret,label,center=cv2.kmeans(Z,K,None,criteria,10,cv2.KMEANS_RANDOM_CENTERS)

    # Now convert back into uint8, and make original image
    center = np.uint8(center)
    res = center[label.flatten()]
    res2 = res.reshape((img.shape))

    cv2.imshow('res2',res2)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


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

curr_image = 0 # global counter
images_to_save = [] # which test images to save
image_out_path = os.path.abspath('/Users/amygooch/GIT/VisoarAgExplorerMay/RowLines/')

#@static_vars(IMAGE_INC=0)
def save_image(image_name, image_data):

    '''Saves image if user requests before runtime'''
    #if curr_image in images_to_save:
    image_name_new = os.path.join(image_out_path, "{0}{1}_{2}.jpg".format(str(save_image.IMAGE_INC),image_name, str(curr_image) ))
    save_image.IMAGE_INC += 1
    print('saving img: '+image_name_new)
    cv2.imwrite(image_name_new, image_data)


if __name__ == '__main__':
#COnvert ViSUS array to numpy

    import optparse

    parser = optparse.OptionParser()

    
    parser.add_option('-f', '--file',
    action="store", dest="file",
    help="file string", default="spam")

    options, args = parser.parse_args()

    print ('Query string:'+ options.file)
   

    save_image.IMAGE_INC = 0
    if VISOAR:
        pdim=input.dims.getPointDim()
        img=Array.toNumPy(input,bShareMem=True)
    elif options.file:
         img = cv2.imread(os.path.abspath(options.file))
    else:
        img = cv2.imread('/Users/amygooch/GIT/ViSUS/SLAM/SLAM_AMY/VisusSlam/Filter_GUI/WeedsNoMark.png')

    printImgInfo(img)

    #get_kmeans_img2(img)

    TGIcolor, TGIbinary = get_TGI(img)
    #array =np.uint8(binaryTGI * 255) 
    print('colorTGI')
    TGIcolor = getIntImg(TGIcolor)
    TGIbinary = getIntImg(TGIbinary)


    color_clustered  = get_kmeans_img(TGIcolor, 8)
    binary_clustered  = get_kmeans_img(TGIbinary, 8)
    
    color_clustered  = get_kmeans_img(TGIcolor, 4)
    binary_clustered  = get_kmeans_img(TGIbinary, 4)
    
    color_clustered  = get_kmeans_img(TGIcolor, 2)
    binary_clustered  = get_kmeans_img(TGIbinary, 2)
    
   
    #This is the most important line.. getting input converted so CV can use it!
    #out =  cv2.cvtColor(np.float32(out), cv2.COLOR_RGB2BGR)
   
    #OpenCV processing to filter and count
    #valid, imgfile = get_filter_img(out, circles_array)

   
    if True:
        imgfile = getRowLines(color_clustered, binary_clustered)

        if VISOAR:
            output=Array.fromNumPy(imgfile,TargetDim=pdim)
        else:
            save_image('_Final_',imgfile)
