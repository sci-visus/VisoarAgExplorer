import matplotlib
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import cv2, numpy

# Convert ViSUS array to numpy
# pdim = input.dims.getPointDim()
# img = Array.toNumPy(input, bShareMem=True)
DEBUG = False
CV_SHOW = False
FILE_INPUT = False
PIXEL = False
if FILE_INPUT:
    dirName= '/Volumes/ViSUSAg/MAPIR/rapini_11-1-2018/S3WOCN_examples/'
    saveDir ='VisusSlamFiles/ViSOARIDX/'
    filename = '2018_1101_100723_240.JPG'

    dirName= '/Volumes/ViSUSAg/MAPIR/BodyShopE/'
    filename ='BodyShopE_2021_0427_133550_114.JPG'

    dirName= '/Volumes/ViSUSAg/MawsHill/MAPIR MawMaws Hill 4.22.21/'
    filename ='2021_0422_111630_131.JPG'

    dirName= '/Volumes/ViSUSAg/MawsHill/smallTest/'
    filename ='2021_0422_111630_131.jpg'
    img = cv2.imread(dirName+filename)
else:
    img = input.astype(numpy.float32)


orange = img[:, :, 0]/255
cyan = img[:, :, 1]/255
NIR = img[:, :, 2]/255

NDVI_u = (NIR - orange)
NDVI_d = (NIR + orange)
#NDVI_d[NDVI_d == 0 ] = 0.01
NDVI = NDVI_u / (NDVI_d+.0001)
#NDVI = (NDVI+1.0)/2.0
NDVI = cv2.normalize(NDVI, None, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_32F)  # normalize data [0,1]

gray =  numpy.float32(NDVI)


cdictN = [ (0.56, 0.02 ,0.02), (0.74, 0.34 ,0.04), (0.94, 0.65 ,0.27), (0.2, 0.4 ,0.0), (0.2, 0.4 ,0.0),]
#cdictN = [ (0.56, 0.02 ,0.02), (0.74, 0.74 ,0.04), (0.0, 0.65 ,0.0), (0.0, 0.4 ,0.0), (0.0, 0.4 ,0.0),]
nodesN =[0.0,0.25,0.5,0.75,1.0,]

OLD = False

if OLD:
    out = cv2.cvtColor(numpy.float32(gray), cv2.COLOR_GRAY2RGB,cv2.CV_32F)
    if CV_SHOW:
        cv2.imshow('img {0}'.format('start'), out)
        k = cv2.waitKey(0)

    maskSave  = gray
    maskSave.fill(0)
    maskSave = cv2.cvtColor(numpy.float32(maskSave), cv2.COLOR_GRAY2RGB,cv2.CV_32F)
    if CV_SHOW:
        cv2.imshow('mask Save', maskSave)
        k = cv2.waitKey(0)
    outSave = maskSave

    for n in range(0, len(nodesN)-1):
        outTemp = out
        # Define lower and uppper limits of what we call "brown"
        start_C=numpy.array([nodesN[n],nodesN[n],nodesN[n]])
        end_C=numpy.array([nodesN[n+1],nodesN[n+1],nodesN[n+1]])
        #start_C= nodesN[n]
        #end_C= nodesN[n+1]
        print(nodesN[n])
        print(cdictN[n])

        # Mask image to only select browns
        mask=cv2.inRange(out,start_C,end_C-0.01)
        #maskSave = mask + maskSave
        if CV_SHOW:
            cv2.imshow('mask {0} {1} to {2}'.format(n,nodesN[n],nodesN[n+1] ), mask)
            k = cv2.waitKey(0)
        # cv2.imshow('maskSave {0}'.format(n), maskSave)
        # k = cv2.waitKey(0)
        #outkeep  = out
        # Change image to red where we found brown
        outTemp[mask>0]=cdictN[n]
        outTemp[mask<0]=(0,0,0)
        outSave = outTemp + outSave
        #out = outkeep + out
        if CV_SHOW:
            cv2.imshow('outTemp {1} to {2}'.format(n,nodesN[n],nodesN[n+1] ),outTemp)
            k = cv2.waitKey(0)
            cv2.imshow('outSave {1} to {2}'.format(n,nodesN[n],nodesN[n+1] ),outSave)
            k = cv2.waitKey(0)
        if FILE_INPUT:
            cv2.imwrite(dirName+'VisusSlamFiles/ViSOARIDX/Thresh{0}_{1}_{2}_{3}'.format(n,nodesN[n],nodesN[n+1],filename), outTemp*255)

    out  = outSave*255
    out = cv2.cvtColor( out, cv2.COLOR_BGR2RGB)
    # out = cv2.cvtColor(out, cv2.COLOR_RGB2BGR,cv2.CV_32F)

    if DEBUG:
        print(dirName+'VisusSlamFiles/ViSOARIDX/Thresh{0}_{1}_{2}_{3}'.format(n,nodesN[n],nodesN[n+1],filename))
    if FILE_INPUT:
        out = outSave * 255
        out = cv2.cvtColor(out, cv2.COLOR_BGR2RGB)
        if (CV_SHOW):
            cv2.imshow('out Final', out)
            k = cv2.waitKey(0)
            cv2.imwrite(dirName+'VisusSlamFiles/ViSOARIDX/Thresh_{0}'.format(filename), out)
    #out =gray
    else:
        #output = Array.fromNumPy(out, TargetDim=pdim)
        output = out.astype(numpy.float32)

elif PIXEL:
    outTemp = img
    out = 1.0 - gray
    h, w, c = outTemp.shape
    if DEBUG:
        print('image: {0}x{1}x{2}'.format(w,h,c))
        print('Color1: {0} {1} {2}'.format(int(cdictN[0][0]*255),int(cdictN[0][1]*255),int(cdictN[0][2]*255)))
        print('Color2: {0} {1} {2}'.format(int(cdictN[1][0]*255),int(cdictN[1][1]*255),int(cdictN[1][2]*255)))
        print('Color3: {0} {1} {2}'.format(int(cdictN[2][0]*255),int(cdictN[2][1]*255),int(cdictN[2][2]*255)))
        print('Color4: {0} {1} {2}'.format(int(cdictN[3][0]*255),int(cdictN[3][1]*255),int(cdictN[3][2]*255)))
        if CV_SHOW:
            cv2.imshow('img {0}'.format('img'), img)
            k = cv2.waitKey(0)
            plt.hist(img.ravel(), 256, [0, 1.0]);
            plt.show()
            k = cv2.waitKey(0)

    for y in range(h):
        for x in range(w):
            s = 1
            #for z in range(c):
            if out[y][x]  >= 0 and out[y][x]  < nodesN[1]:
                outTemp[y][x][0] = int(cdictN[s][0]*255)
                outTemp[y][x][1] = int(cdictN[s][1]*255)
                outTemp[y][x][2] = int(cdictN[s][2]*255)
            elif out[y][x]  >= nodesN[1] and out[y][x] < nodesN[2]:
                outTemp[y][x][0] = int(cdictN[s+1][0]*255)
                outTemp[y][x][1] = int(cdictN[s+1][1]*255)
                outTemp[y][x][2] = int(cdictN[s+1][2]*255)
            elif out[y][x] >= nodesN[2] and out[y][x] < nodesN[3]:
                outTemp[y][x][0] = int(cdictN[s+2][0]*255)
                outTemp[y][x][1] = int(cdictN[s+2][1]*255)
                outTemp[y][x][2] = int(cdictN[s+2][2]*255)
            elif out[y][x] >= nodesN[3] and out[y][x] < nodesN[4]:
                outTemp[y][x][0] = int(cdictN[s+3][0]*255)
                outTemp[y][x][1] = int(cdictN[s+3][1]*255)
                outTemp[y][x][2] = int(cdictN[s+3][2]*255)
            else:
                outTemp[y][x][0] = int(0* 255)
                outTemp[y][x][1] = int(0* 255)
                outTemp[y][x][2] = int(0 * 255)
        if DEBUG:
            print('out/gray: {0}'.format(out[y][x]) + '   input: {0}'.format(outTemp[y][x])+'outTemp: {0}'.format(outTemp[y][x]))
    if FILE_INPUT:
        outTemp = cv2.cvtColor(outTemp, cv2.COLOR_BGR2RGB)
        if CV_SHOW:
            cv2.imshow('out Final', outTemp)
            k = cv2.waitKey(0)
        plt.hist(out.ravel(), 256, [0, 1.0])
        plt.show()
        k = cv2.waitKey(0)
        plt.hist(outTemp.ravel(), 256, [0, 256])
        plt.show()
        k = cv2.waitKey(0)

    else:
        #plt.hist(outTemp.ravel(), 256, [0, 256])
        #plt.show()
        #outTemp = cv2.cvtColor(outTemp, cv2.COLOR_BGR2RGB)
        # output = Array.fromNumPy(out, TargetDim=pdim)
        output = outTemp.astype(numpy.uint8)

else:

    # functions for blending operations
    # takes a pixel from image 1 (pix_1) and blends it with a pixel from image 2 (pix_2)
    # depending on the value given in perc (percentage);
    # if perc = 0 or 255 (or 0,0,0 or 255,255,255) it will perform no blending at all
    # and return the value of image 1 or image 2;
    # by contrast, all values in between (e.g., 140) will give a weighted blend of the two images
    # function can be used with scalars or numpy arrays (perc will be greyscale numpy array then)
    def mix_pixel(pix_1, pix_2, perc):
        return (perc / 255 * pix_2) + ((255 - perc) / 255 * pix_1)


    # function for blending images depending on values given in mask
    def blend_images_using_mask(img_orig, img_for_overlay, img_mask):
        # turn mask into 24 bit greyscale image if necessary
        # because mix_pixel() requires numpy arrays having the same dimension
        # if image is 24-bit BGR, the image has 3 dimensions, if 8 bit greyscale 2 dimensions
        if len(img_mask.shape) != 3:
            img_mask = cv2.cvtColor(img_mask, cv2.COLOR_GRAY2BGR, cv2.CV_8U)

        # interpolate between two images (img_orig and img_to_insert)
        # using the values in img_mask (each pixel serves as individual weight)
        # as weighting factors (ranging from [0,0,0] to [255,255,255] or 0 to 100 percent);
        # because all three images are numpy arrays standard operators
        # for multiplication etc. will be applied to all values in arrays
        img_res = mix_pixel(img_orig, img_for_overlay, img_mask)

        return img_res.astype(numpy.uint8)



    cdictN = [ (int(0.56*255), int(0.02*255) ,int(0.02*255)),
               (int(0.74*255), int(0.34*255) ,int(0.04*255)),
               (int(0.94*255), int(0.65*255) ,int(0.27*255)),
               (int(0.2*255), int(0.4*255) ,int(0.0*255)),
               (int(0.2*255), int(0.4*255) ,int(0.0*255)),]
    #Red to Green
    cdictN = [ (0.56, 0.02 ,0.02), (0.74, 0.34 ,0.04), (0.94, 0.65 ,0.270), (0.20, 0.4 ,0.0), (0.20, 0.4 ,0.0),]
    #Green to Red
    cdictN = [  (0.20, 0.4 ,0.0), (68/255, 102/255, 85/255),(41/255, 77/255, 66/255),(217/255, 207/255, 176/255), (0.56, 0.02 ,0.02), ]
    nodesN =[0.0,0.5,0.75,0.9,1.0,]

    f0 = cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB, cv2.CV_8U)
    f0[:, :] = (0, 0, 0)
    img_blended = f0
    for n in range(0, len(nodesN) - 1):
        mn = cv2.inRange(gray, nodesN[n], nodesN[n+1])

        fn = f0
        fn[:, :] = (cdictN[n+1])
        fn = (fn * 255).astype(numpy.uint8)
        # f1 = cv2.cvtColor(f1, cv2.COLOR_RGB2BGR, cv2.CV_8U)
        if CV_SHOW:
            cv2.imshow('img {0} {1}'.format('img f1 should be  ', cdictN[n+1]), fn)
            k = cv2.waitKey(0)
        f0[:, :] = (0, 0, 0)
        img_blended = blend_images_using_mask(img_blended, fn, mn)
        if CV_SHOW:
            cv2.imshow('img {0}'.format(n), img_blended)
            k = cv2.waitKey(0)


    output = cv2.cvtColor(img_blended, cv2.COLOR_BGR2RGB)
    if CV_SHOW:
        cv2.imshow('img {0}'.format('FINAL'), output)
        k = cv2.waitKey(0)

    output = output.astype(numpy.uint8)