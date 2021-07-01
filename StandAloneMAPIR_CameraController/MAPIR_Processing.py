# -*- coding: utf-8 -*-
"""
/***************************************************************************
 MAPIR_ProcessingDockWidget
                                 A QGIS plugin
 Widget for processing images captured by MAPIR cameras
                             -------------------
        begin                : 2016-09-26
        git sha              : $Format:%H$
        copyright            : (C) 2016 by Peau Productions
        email                : ethan@peauproductions.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os
from os import listdir
import warnings
warnings.filterwarnings("ignore")

from PIL import Image
from PIL.TiffTags import TAGS
import sys

os.umask(0)

from  LensLookups import *
from  MAPIR_Enums import *

from datetime import datetime

import shutil
import platform
import itertools
import ctypes
import string
#import win32api
import PIL
import bitstring
import collections
# import tifffile

# from PyQt5 import QtCore, QtGui, QtWidgets
#
# import PyQt5.uic as uic

import numpy as np
import subprocess
import cv2
import copy
import hid
import time
import json
import math
import webbrowser

import Calibration
import show_image
import Geometry
from bit_depth_conversion import normalize, normalize_rgb
from camera_specs import CameraSpecs

from MAPIR_Enums import *
##AAG: Taking out UI classes
#from Calculator import *
#from LUT_Dialog import *
#from Vignette import *
#from BandOrder import *
#from ViewerSave_Dialog import *
import xml.etree.ElementTree as ET
#import KernelConfig
from MAPIR_Converter import *
#from Exposure import *
from ArrayTypes import AdjustYPR, CurveAdjustment
from reg_value_conversion import *
from ExifUtils import *
#from Geotiff import *


modpath = os.path.dirname(os.path.realpath(__file__))

if not os.path.exists(modpath + os.sep + "instring.txt"):
    istr = open(modpath + os.sep + "instring.txt", "w")
    istr.close()

def dir_path(string):
    if os.path.isdir(string):
        return string
    else:
        raise NotADirectoryError(string)



# from osgeo import gdal
# gdal.UseExceptions()
# fp, pathname, description = imp.find_module('_gdal', [dirname(gdal.__file__)])
# dist_dir = "dist"
# shutil.copy(pathname, dist_dir)
# import gdal as gdal2
# import gdal

import glob

all_cameras = []
if sys.platform == "win32":
    si = subprocess.STARTUPINFO()
    si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
else:
    si = None

class tPoll:
    def __init__(self):
        request = 0
        code = 0
        len = 0 #Len can also store the value depending on the code given
        values = []

class tEventInfo:
    def __init__(self):
        mode = 0
        process = 0
        focusing = 0
        inversion = 0
        nr_faces = 0

class MAPIR_ProcessingCLI( ):
    BASE_COEFF_SURVEY1_NDVI_JPG = {"red":   {"slope": 331.759383023, "intercept": -6.33770486888},
                                   "green": {"slope": 1.00, "intercept": 0.00},
                                   "blue":  {"slope": 51.3264675118, "intercept": -0.6931339436}
                                  }

    BASE_COEFF_SURVEY2_RED_JPG = {"slope": 16.01240929, "intercept": -2.55421832}
    BASE_COEFF_SURVEY2_RED_TIF = {"slope": 0.24177528, "intercept": -5.09645820}

    BASE_COEFF_SURVEY2_GREEN_JPG = {"slope": 4.82869470, "intercept": -0.60437250}
    BASE_COEFF_SURVEY2_GREEN_TIF = {"slope": 0.07640011, "intercept": -1.39528479}

    BASE_COEFF_SURVEY2_BLUE_JPG = {"slope": 2.67916884, "intercept": -0.39268985}
    BASE_COEFF_SURVEY2_BLUE_TIF = {"slope": 0.03943339, "intercept": -0.67299134}


    BASE_COEFF_SURVEY2_NDVI_JPG = {"red":   {"slope": 6.51199915, "intercept": -0.29870245},
                                   "green": {"slope": 1.00, "intercept": 0.00},
                                   "blue":  {"slope": 10.30416005, "intercept": -0.65112026}
                                  }

    BASE_COEFF_SURVEY2_NDVI_TIF = {"red":   {"slope": 1.06087488594, "intercept": 3.21946584661},
                                   "green": {"slope": 1.00, "intercept": 0.00},
                                   "blue":  {"slope": 1.46482226805, "intercept": -43.6505776052}
                                  }

    BASE_COEFF_SURVEY2_NIR_JPG = {"slope": 7.13619139, "intercept": -0.46967653}
    BASE_COEFF_SURVEY2_NIR_TIF = {"slope":  0.12962333, "intercept": -2.24216724}

    BASE_COEFF_SURVEY3_NGB_TIF = {"red":   {"slope": 6.9623355781520475, "intercept": -0.0864835439375467},
                                  "green": {"slope": 1.8947426321347667, "intercept": -0.0494622920687357},
                                  "blue":  {"slope": 2.743963570586564, "intercept":  -0.03883688306243116}
                                 }

    BASE_COEFF_SURVEY3_NGB_JPG = {"red":   {"slope": 1.3572359350724152, "intercept": -0.23211423412281346},
                                  "green": {"slope": 1.1880427799275182, "intercept": -0.15262065349606874},
                                  "blue":  {"slope": 1.352860697992975, "intercept":  -0.19361810260132328}
                                 }

    BASE_COEFF_SURVEY3_RGN_JPG = {"red":   {"slope": 1.3289958195489457, "intercept": -0.17638075239399503},
                                  "green": {"slope": 1.2902528664499517, "intercept": -0.15262065349606874},
                                  "blue":  {"slope": 1.387381083964384, "intercept":  -0.2193633829181454}
                                 }

    BASE_COEFF_SURVEY3_RGN_TIF = {"red":   {"slope": 3.3823966319413326, "intercept": -0.025581742423831766},
                                  "green": {"slope": 2.0198257823722026, "intercept": -0.019624370783744682},
                                  "blue":  {"slope": 6.639688121967463, "intercept":  -0.025991734455270532}
                                 }

    BASE_COEFF_SURVEY3_OCN_JPG = {"red":   {"slope": 1.0228327654792326, "intercept": -0.1847085716228949},
                                  "green": {"slope":  1.0655229303683258, "intercept": -0.1921036590734388},
                                  "blue":  {"slope": 1.0562618906633048, "intercept":  -0.2037317328293336}
                                 }

    BASE_COEFF_SURVEY3_OCN_TIF = {"red":   {"slope": 1.557354345031938, "intercept": -0.0790237907829558},
                                  "green": {"slope": 1.3794503108318112, "intercept": -0.0743811687912796},
                                  "blue":  {"slope": 2.1141137232666183, "intercept": -0.0650818927718132}
                                 }

    BASE_COEFF_SURVEY3_NIR_TIF = {"slope":  13.2610911247, "intercept": 0.0}

    BASE_COEFF_SURVEY3_RE_JPG = {"slope":  0.12962333, "intercept": -2.24216724}
    BASE_COEFF_SURVEY3_RE_TIF = {"slope":  14.637430522690837, "intercept": -0.11816284659122683}

    BASE_COEFF_DJIX3_NDVI_JPG = {"red":   {"slope": 4.63184993, "intercept": -0.34430543},
                                 "green": {"slope": 1.00, "intercept": 0.00},
                                 "blue":  {"slope": 16.36429964, "intercept": -0.49413940}
                                }

    BASE_COEFF_DJIX3_NDVI_TIF = {"red":   {"slope": 0.01350319, "intercept": -0.74925346},
                                 "green": {"slope": 1.00, "intercept": 0.00},
                                 "blue":  {"slope": 0.03478272, "intercept": -0.77810008}
                                }

    BASE_COEFF_DJIPHANTOM4_NDVI_JPG = {"red":   {"slope": 0.03333209, "intercept": -1.17016961},
                                       "green": {"slope": 1.00, "intercept": 0.00},
                                       "blue":  {"slope": 0.05373502, "intercept": -0.99455214}
                                      }

    BASE_COEFF_DJIPHANTOM4_NDVI_TIF = {"red":   {"slope": 0.03333209, "intercept": -1.17016961},
                                       "green": {"slope": 1.00, "intercept": 0.00},
                                       "blue":  {"slope": 0.05373502, "intercept": -0.99455214}
                                      }

    BASE_COEFF_DJIPHANTOM3_NDVI_JPG = {"red":   {"slope": 3.44708472, "intercept": -1.54494979},
                                       "green": {"slope": 1.00, "intercept": 0.00},
                                       "blue":  {"slope": 6.35407929, "intercept": -1.40606832}
                                      }

    BASE_COEFF_DJIPHANTOM3_NDVI_TIF = {"red":   {"slope":  0.01752340, "intercept": -1.37495554},
                                       "green": {"slope": 1.00, "intercept": 0.00},
                                       "blue":  {"slope": 0.03700812, "intercept": -1.41073753}
                                      }

    BASE_COEFF_KERNEL_F644 = [0.0, 0.0]
    BASE_COEFF_KERNEL_F405 = [0.0, 0.0]
    BASE_COEFF_KERNEL_F450 = [0.0, 0.0]
    BASE_COEFF_KERNEL_F520 = [0.0, 0.0]
    BASE_COEFF_KERNEL_F550 = [0.0, 0.0]
    BASE_COEFF_KERNEL_F632 = [0.0, 0.0]
    BASE_COEFF_KERNEL_F650 = [0.0, 0.0]
    BASE_COEFF_KERNEL_F725 = [0.0, 0.0]
    BASE_COEFF_KERNEL_F808 = [0.0, 0.0]
    BASE_COEFF_KERNEL_F850 = [0.0, 0.0]
    BASE_COEFF_KERNEL_F395_870 = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    BASE_COEFF_KERNEL_F475_850 = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    BASE_COEFF_KERNEL_F550_850 = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    BASE_COEFF_KERNEL_F660_850 = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    BASE_COEFF_KERNEL_F475_550_850 = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    BASE_COEFF_KERNEL_F550_660_850 = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

    # eFilter = mousewheelFilter()
    camera = 0
    poll = []
    ei = tEventInfo()
    capturing = False
    SQ_TO_TARG = 2.1875
    SQ_TO_SQ = 5.0
    CORNER_TO_CORNER = 5.25
    CORNER_TO_TARG = 10.0
    TARGET_LENGTH = 2.0
    TARG_TO_TARG = 2.6
    dialog = None
    imcols = 4608
    imrows = 3456
    imsize = imcols * imrows
    #closingPlugin = QtCore.pyqtSignal()
    firstpass = True
    useqr = False
    qrcoeffs = []

    qrcoeffs2 = []
    qrcoeffs3 = []
    qrcoeffs4 = []
    qrcoeffs5 = []
    qrcoeffs6 = []
    coords = []
    # drivesfound = []
    ref = ""
    refindex = ["oldrefvalues", "newrefvalues"] #version 1 - old, version 2 - new
    refvalues = {
    "oldrefvalues":{
        "660/850": [[0.87032549, 0.52135779, 0.23664799], [0, 0, 0], [0.8463514, 0.51950608, 0.22795518]],
        "446/800": [[0.8419608509, 0.520440145, 0.230113958], [0, 0, 0], [0.8645652801, 0.5037779363, 0.2359041624]],
        "850": [[0.8463514, 0.51950608, 0.22795518], [0, 0, 0], [0, 0, 0]],

        "650": [[0.87032549, 0.52135779, 0.23664799], [0, 0, 0], [0, 0, 0]],
        "550": [[0, 0, 0], [0.87415089, 0.51734381, 0.24032515], [0, 0, 0]],
        "450": [[0, 0, 0], [0, 0, 0], [0.86469794, 0.50392915, 0.23565447]],
        "725": [0.8609978650653954, 0.5211329995745606, 0.23324225504400245],
        "490/615/808": [0.8472247816774043, 0.5200480372488874, 0.23065111839727553],
        "Mono450": [0.8634818638, 0.5024087105, 0.2351860396],
        "Mono550": [0.8740616379, 0.5173070235, 0.2402423818],
        "Mono650": [0.8705783136, 0.5212290524, 0.2366437854],
        "Mono725": [0.8606071247, 0.521474266, 0.2337744252],
        "Mono808": [0.8406184266, 0.5203405498, 0.2297701185],
        "Mono850": [0.8481919553, 0.519491643, 0.2278713071],
        "Mono405": [0.8556905469, 0.4921243183, 0.2309899254],
        "Mono518": [0.8729814889, 0.5151370187, 0.2404729692],
        "Mono632": [0.8724034645, 0.5209649915, 0.2374529161],

        "Mono590": [0.8747043911, 0.5195596573, 0.2392049856],
        "550/660/850": [[0.8474610999, 0.5196055607, 0.2279922965],[0.8699940018, 0.5212235151, 0.2364397706],[0.8740311726, 0.5172611881, 0.2402870156]]

    },
    "newrefvalues":{
        "660/850": [[0.8691644285714284, 0.2624914285714286, 0.20969199999999993, 0.019544714285714283], [0, 0, 0, 0], [0.8653063177, 0.2798126291, 0.2337498097, 0.0193295348]],
        "446/800": [[0.7882333002, 0.2501235178, 0.1848459584, 0.020036883], [0, 0, 0], [0.8645652801, 0.5037779363, 0.2359041624]],
        "725" : [0.8688518306024209, 0.26302553751154756, 0.2127410973890211, 0.019551020566927594],
        "850": [[0.8649280907, 0.2800907016, 0.2340131491, 0.0195446727], [0, 0, 0], [0, 0, 0]],

        "650": [[0.8773469949, 0.2663571183, 0.199919444, 0.0192325637], [0, 0, 0], [0, 0, 0]],
        "550": [[0, 0, 0], [0.8686559344, 0.2655697585, 0.1960837144, 0.0195629009], [0, 0, 0]],
        "450": [[0, 0, 0], [0, 0, 0], [0.7882333002, 0.2501235178, 0.1848459584, 0.020036883]],
        "Mono405": [0.6959473282,  0.2437485737, 0.1799017476, 0.0205591758],
        "Mono450": [0.7882333002, 0.2501235178, 0.1848459584, 0.020036883],
        "Mono490": [0.8348841674, 0.2580074987, 0.1890252099, 0.01975703],
        "Mono518": [0.8572181897, 0.2628629357, 0.192259471, 0.0196629792],
        "Mono550": [0.8686559344, 0.2655697585, 0.1960837144, 0.0195629009],
        "Mono590": [0.874586922, 0.2676592931, 0.1993779934, 0.0193745668],
        "Mono615": [0.8748454449, 0.2673426216, 0.1996415667, 0.0192891156],
        "Mono632": [0.8758224323, 0.2670055225, 0.2023045295, 0.0192596465],
        "Mono650": [0.8773469949, 0.2663571183, 0.199919444, 0.0192325637],
        "Mono685": [0.8775925081, 0.2648548355, 0.1945563456, 0.0192860556],
        "Mono725": [0.8756774317, 0.266883373, 0.21603525, 0.194527158],
        "Mono780": [0.8722125382, 0.2721842015, 0.2238493387, 0.0196295938],
        "Mono808": [0.8699458632, 0.2780141682, 0.2283300902, 0.0216592377],
        "Mono850": [0.8649280907, 0.2800907016, 0.2340131491, 0.0195446727],
        "Mono880": [0.8577996233, 0.2673899041, 0.2371926238, 0.0202034892],
        "550/660/850": [[0.8689592421, 0.2656248359, 0.1961875592, 0.0195576511], [0.8775934407, 0.2661207692, 0.1987265874, 0.0192249327],
                        [0.8653063177, 0.2798126291, 0.2337498097, 0.0193295348]],
        "490/615/808": [[0.8414604806, 0.2594283565, 0.1897271608, 0.0197180224],
                        [0.8751529643, 0.2673261446, 0.2007025375, 0.0192817427],
                        [0.868782908, 0.27845399, 0.2298671821, 0.0211305297]],
        "475/550/850": [[0.8348841674, 0.2580074987, 0.1890252099, 0.01975703], [0.8689592421, 0.2656248359, 0.1961875592, 0.0195576511],
                        [0.8653063177, 0.2798126291, 0.2337498097, 0.0193295348]]

    }}
    pixel_min_max = {"redmax": 0.0, "redmin": 65535.0,
                     "greenmax": 0.0, "greenmin": 65535.0,
                     "bluemax": 0.0, "bluemin": 65535.0}

    multiplication_values = {"red":   {"slope": 0.00, "intercept": 0.00},
                             "green": {"slope": 0.00, "intercept": 0.00},
                             "blue":  {"slope": 0.00, "intercept": 0.00},
                             "mono":  {"slope": 0.00, "intercept": 0.00}
                            }


    qr_coeffs = {}

    monominmax = {"min": 65535.0,"max": 0.0}
    imkeys_JPG = np.array(list(range(0, 255)))
    imkeys = np.array(list(range(0, 65536)))
    weeks = 0
    days = 0
    hours = 0
    minutes = 0
    seconds = 1
    conv = None
    kcr = None
    analyze_bands = []
    modalwindow = None
    calcwindow = None
    LUTwindow = None
    M_Shutter_Window = None
    A_Shutter_Window = None
    Bandwindow = None
    Advancedwindow = None
    rdr = []
    ManualExposurewindow = None
    AutoExposurewindow = None
    BandNames = {
        "RGB": [644, 0, 0],
        "405": [405, 0, 0],
        "450": [450, 0, 0],
        "490": [490, 0, 0],
        "518": [518, 0, 0],
        "550": [550, 0, 0],
        "590": [590, 0, 0],
        "615": [615, 0, 0],
        "632": [632, 0, 0],
        "650": [650, 0, 0],
        "685": [685, 0, 0],
        "725": [725, 0, 0],
        "780": [780, 0, 0],
        "808": [808, 0, 0],
        "850": [850, 0, 0],
        "880": [880, 0, 0],
        "940": [940, 0, 0],
        "945": [945, 0, 0],
        "UVR": [870, 0, 395],
        "NGB": [850, 550, 475],
        "RGN": [660, 550, 850],
        "OCN": [615, 490, 808],

    }
    VigWindow = None
    ndvipsuedo = None
    savewindow = None
    index_to_save = None
    LUT_to_save = None
    LUT_Min = -1.0
    LUT_Max = 1.0
    array_indicator = False
    seed_pass = False
    transferoutfolder = None
    yestransfer = False
    yesdelete = False
    selection_made = False
    POLL_TIME = 3000

    slow = 0
    regs = [0] * eRegister.RG_SIZE.value
    paths = []
    pathnames = []
    driveletters = []
    source = 0
    evt = 0
    info = 0
    VENDOR_ID = 0x525
    PRODUCT_ID = 0xa4ac
    BUFF_LEN = 512
    SET_EVENT_REPORT = 1
    SET_COMMAND_REPORT = 3
    SET_REGISTER_WRITE_REPORT = 5
    SET_REGISTER_BLOCK_WRITE_REPORT = 7
    SET_REGISTER_READ_REPORT = 9
    SET_REGISTER_BLOCK_READ_REPORT = 11
    SET_CAMERA = 13
    display_image = None
    display_image_original = None
    displaymax = None
    displaymin = None
    mapscene = None
    frame = None
    legend_frame = None
    legend_scene = None
    image_loaded = False

    COLOR_CORRECTION_VECTORS = [1.398822546, -0.09047482163, 0.1619316638, -0.01290435996, 0.8994362354, 0.1134681329, 0.007306902204, -0.05995989591, 1.577814579]#101018
    regs = []
    DJIS = ["DJI Phantom 4", "DJI Phantom 4 Pro", "DJI Phantom 3a", "DJI Phantom 3p", "DJI X3"]
    SURVEYS = ["Survey1", "Survey2", "Survey3"]
    KERNELS = ["Kernel 3.2", "Kernel 14.4"]

    ANGLE_SHIFT_QR = 7

    JPGS = ["jpg", "JPG", "jpeg", "JPEG"]
    TIFS = ["tiff", "TIFF", "tif", "TIF"]

    PIX4D_VALUES = {"3.37": {   "PRINCIPALPOINT":"3.84387, 1.53139",
                                "PERSPECTIVEFOCALLENGTH":"3.37",
                                "PERSPECTIVEDISTORTION":"0, 0, 0, 0, 0"},

                    "8.25": {   "PRINCIPALPOINT":"3.84387, 1.53139",
                                "PERSPECTIVEFOCALLENGTH":"8.444407",
                                "PERSPECTIVEDISTORTION":"-0.07569, 0.059957, -0.02031, -0.01246, 0.016932"},

                    "3.5": {    "PRINCIPALPOINT":"3.524, 2.6604",
                                "PERSPECTIVEFOCALLENGTH":"3.4097",
                                "PERSPECTIVEDISTORTION":"0.058, -0.222, 0.017, 0, 0"},

                    "5.5": {    "PRINCIPALPOINT":"3.412091, 2.745396",
                                "PERSPECTIVEFOCALLENGTH":"5.5",
                                "PERSPECTIVEDISTORTION":"0, 0, 0, 0, 0"},

                    "9.6": {    "PRINCIPALPOINT":"3.412091, 2.745396",
                                "PERSPECTIVEFOCALLENGTH":"9.6706605",
                                "PERSPECTIVEDISTORTION":"-0.107494, 0.0852713, 0.114084, 0.000263678, -0.000463052"},

                    "12.0": {   "PRINCIPALPOINT":"3.412091, 2.745396",
                                "PERSPECTIVEFOCALLENGTH":"12.0",
                                "PERSPECTIVEDISTORTION":"0, 0, 0, 0, 0"},

                    "16.0": {   "PRINCIPALPOINT":"3.412091, 2.745396",
                                "PERSPECTIVEFOCALLENGTH":"16.0",
                                "PERSPECTIVEDISTORTION":"0, 0, 0, 0, 0"},

                    "35.0": {   "PRINCIPALPOINT":"3.412091, 2.745396",
                                "PERSPECTIVEFOCALLENGTH":"35.0",
                                "PERSPECTIVEDISTORTION":"0, 0, 0, 0, 0"},

    }

    CHECKED = 2 # QT creator syntax for checkState(); 2 signifies the box is checked, 0 is unchecked
    UNCHECKED = 0

    SENSOR_LOOKUP = {6: "14.4 MP", 4: "3.2 MP"}
    SHUTTER_SPEED_LOOKUP = {1: "1/32000",
                            2: "1/16000",
                            3: "1/8000",
                            4: "1/6000",
                            5: "1/4000",
                            6: "1/2000",
                            7: "1/1600",
                            8: "1/1250",
                            9: "1/1000",
                            10: "1/800",
                            11: "1/640",
                            12: "1/500",
                            13: "1/400",
                            14: "1/320",
                            15: "1/250",
                            16: "1/200",
                            17: "1/160",
                            18: "1/125",
                            19: "1/100",
                            20: "1/80",
                            21: "1/60",
                            22: "1/50",
                            23: "1/40",
                            24: "1/30",
                            25: "1/25",
                            26: "1/20",
                            27: "1/15",
                            28: "1/12",
                            29: "1/10",
                            30: "1/8",
                            31: "1/6.4",
                            32: "1/5",
                            33: "1/4",
                            34: "1/3.2",
                            35: "1/2.5",
                            36: "1/2",
                            37: "1/1" }

    ISO_VALS = (1,2,4,8,16,32)
    lensvals = None

    def __init__(self, parent=None, args=None):
        """Constructor."""
        #super(MAPIR_ProcessingCLI, self).__init__(parent,args)
        self.CalibrationLog = []
        self.HCP_value = 5
        self.histogramClipBox =False
        self.IndexBox = True
        self.Tiff2JpgBox = True
        self.CalibrationTargetSelect = 0  #0 for version 2; 1 for Version 1
        self.args = args

        if args!='wait':
            import argparse

            parser = argparse.ArgumentParser(description='MAPIR camera Process target and folder of images.')

            parser.add_argument('--target', help= 'image containing target  ')
            parser.add_argument('--path', type=dir_path, help='directory of source images')
            parser.add_argument('--calibration_camera_model', help='Survey3')
            parser.add_argument('--calibration_QR_file',   help='same as target')
            parser.add_argument('--calibration_filter',   help='filter such as OCN')
            parser.add_argument('--calibration_lens',   help='3.37mm (Survey3W)')
            args = parser.parse_args()

            if args and os.path.exists(args.target):
                self.targetImage = args.target
            else:
                self.targetImage ='/Volumes/ViSUSAg/MAPIR/rapini_11-1-2018/target/2018_1101_100128_003.JPG'
                self.targetImage ='/Volumes/TenGViSUSAg/2021Season/MapIR/MAPIR Pea 07 6.17.21/target/2021_0617_045935_005.JPG'
                print('ERROR: need target Image, setting to default')
                #return

            if args and os.path.exists(args.path):
                self.CalibrationInFolder = args.path
            else:
                self.CalibrationInFolder ='/Volumes/ViSUSAg/MAPIR/rapini_11-1-2018/smallTestMapirOCN'
                self.CalibrationInFolder = '/Volumes/TenGViSUSAg/2021Season/MapIR/MAPIR Pea 07 6.17.21/uncalibrated'
                print('ERROR: need path to images, setting to default')
                #return

            self.calibration_QR_file =  self.targetImage
            self.calibration_filter =  'OCN'
            self.calibration_lens = '3.37mm (Survey3W)'
            self.calibration_camera_model = 'Survey3'

            try:
                self.generate_calibration()
                #print(self.CalibrationLog)
                self.on_CalibrateButton_released()
                #print(self.CalibrationLog)
            except:
                print('ERROR')

    def processArgs(self,args):
        self.calibration_filter = 'OCN'
        self.calibration_lens = '3.37mm (Survey3W)'
        self.calibration_camera_model = 'Survey3'
        self.targetImage = args['target']
        self.CalibrationInFolder = args['path']
        self.calibration_QR_file = self.targetImage
        self.CalibrationCameraModel = self.calibration_camera_model
        self.CalibrationQRFile = self.calibration_QR_file
        self.CalibrationFilter = self.calibration_filter
        self.CalibrationLens = self.calibration_lens


    def generate_calibration(self):
        self.qr_coeffs_index = 1
        self.findQR(self.calibration_QR_file , [self.calibration_camera_model, self.calibration_filter, self.calibration_lens])
        print(self.multiplication_values)

        self.qr_coeffs[self.qr_coeffs_index] = copy.deepcopy(self.multiplication_values["mono"])
        qrcoeffs = self.qr_coeffs
        self.useqr = True

        return self.qr_coeffs_index, self.qr_coeffs


    def CalibrationLog_append(self, str):
        print(str)  #Could change this to generate log file
        self.CalibrationLog.append(str)

    def append_select_a_camera_message_to_calibration_log(self):
        self.CalibrationLog_append("Attention! Please select a camera model.\n")

    def append_please_select_a_target_image_message_to_calibration_log(self):
        self.CalibrationLog_append("Attention! Please select a target image.\n")

    def any_calibration_camera_model_selected(self, calibration_camera_model):
        return True

    def any_calibration_target_image_selected(self, calibration_QR_file):
        return True

    def append_calibrating_image_message_to_calibration_log(self, image_index, files_to_calibrate):
        self.CalibrationLog_append("Calibrating image " + str(image_index + 1) + " of " + str(len(files_to_calibrate)))

    def output_mono_band_validation(self):
        camera_model = self.PreProcessCameraModel.currentText()
        filt = self.PreProcessFilter.currentText()

        if not ((camera_model in ["Survey2", "Survey3"]) and (filt in ["RE", "NIR", "Red", "Blue", "Green"])):
            self.PreProcessLog.append("WARNING: Outputting mono band for filter {} is not supported for Calibration Tab \n".format(filt))

    @staticmethod
    def get_mapir_files_in_dir(dir_name):
        return glob.glob(dir_name + os.sep + "*.[mM][aA][pP][iI][rR]")

    @staticmethod
    def get_raw_files_in_dir(dir_name):
        return glob.glob(dir_name + os.sep + "*.[rR][aA][wW]")

    @staticmethod
    def get_tiff_files_in_dir(dir_name):
        file_paths = []
        file_paths.extend(glob.glob(dir_name + os.sep + "*.[tT][iI][fF]"))
        file_paths.extend(glob.glob(dir_name + os.sep + "*.[tT][iI][fF][fF]"))
        return file_paths

    @staticmethod
    def get_jpg_files_in_dir(dir_name):
        file_paths = []
        file_paths.extend(glob.glob(dir_name + os.sep + "*.[jJ][pP][gG]"))
        file_paths.extend(glob.glob(dir_name + os.sep + "*.[jJ][pP][eE][gG]"))
        return file_paths

    @staticmethod
    def get_dng_files_in_dir(dir_name):
        return glob.glob(dir_name + os.sep + "*.DNG")

    def get_rgb_clipping_channel_max_mins(self, img, counter):
        is_first_image = counter == 0

        blue = img[:, :, 0]
        green = img[:, :, 1]
        red = img[: ,: , 2]

        if is_first_image:
            self.HC_max["redmax"] = self.get_clipping_value(red)
            self.HC_max["greenmax"] = self.get_clipping_value(green)
            self.HC_max["bluemax"] = self.get_clipping_value(blue)

            print('get_rgb_clipping_channel_max_mins')
            self.min = min(red.min(), green.min(), blue.min())
            self.print_rgb_mins(blue, green, red)
            print(self.min)
        else:
            self.HC_max["redmax"] = max([self.get_clipping_value(red), self.HC_max["redmax"]])
            self.HC_max["greenmax"] = max([self.get_clipping_value(green), self.HC_max["greenmax"]])
            self.HC_max["bluemax"] = max([self.get_clipping_value(blue), self.HC_max["bluemax"]])

            self.min = min(self.min, red.min(), green.min(), blue.min())
            self.print_rgb_mins(blue, green, red)
            print(self.min)

    def delete_all_exiftool_tmp_files_in_dir(self, dir_path):
        for file_name in listdir(dir_path):
            if file_name.endswith('_exiftool_tmp'):
                os.remove(os.path.join(dir_path,file_name))

    def get_LOBF_values(self, x, y):
        try:
            mean_x = np.mean(x)
            mean_y = np.mean(y)

            numer = sum((x - mean_x) * (y - mean_y))
            denom = sum(np.power(x - mean_x, 2))

            slope = numer / denom
            intercept = mean_y - (slope * mean_x)

            return slope, intercept
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print("Error: ", e)
            print("Line: " + str(exc_tb.tb_lineno))

    def get_filetype(self, image):
        if image.split(".")[1] in self.JPGS:
            return "JPG"

        elif image.split(".")[1] in self.TIFS:
            return "TIF"
    def is_calibration_target_version_2(self):
        return self.CalibrationTargetSelect  == 0

    def is_calibration_target_version_1(self):
        return self.CalibrationTargetSelect  == 1

    def get_version_2_target_corners(self, image_path):
        self.coords = Calibration.get_image_corners(image_path)
        self.ref = self.refindex[1]
        print('self.coords: ' + str(self.coords))

    def findQR(self, image_path, ind):
        try:
            self.ref = ""

            if self.is_calibration_target_version_2():
                version = "V2"

            elif self.is_calibration_target_version_1():
                version = "V1"

            camera_model = ind[0]
            fil = ind[1]
            lens = ind[2]

            image = cv2.imread(image_path, -1)

            if self.check_if_RGB(camera_model, fil, lens):
                if len(image.shape) < 3:
                    raise IndexError("RGB filter was selected but input folders contain MONO images")
            else:
                if len(image.shape) > 2:
                    raise IndexError("Mono filter was selected but input folders contain RGB images")

            #Fiducial Finder only needs to be run for Version 2, calib.txt will only be written for Version 2
            if version == "V2":
                self.get_version_2_target_corners(image_path)

            #Finding coordinates for Version 1
            else:
                self.CalibrationLog_append("Looking for QR target \n")
                self.ref = self.refindex[0]

                if self.check_if_RGB(camera_model, fil, lens): #if RGB Camera
                    im = cv2.imread(image_path)
                    grayscale = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)

                    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8)) #increasing contrast
                    cl1 = clahe.apply(grayscale)
                else: #if mono camera
                    #QtWidgets.QApplication.processEvents()
                    im = cv2.imread(image_path, 0)
                    clahe2 = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
                    cl1 = clahe2.apply(im)
                denoised = cv2.fastNlMeansDenoising(cl1, None, 14, 7, 21)
                threshcounter = 17

                while threshcounter <= 255:
                    ret, thresh = cv2.threshold(denoised, threshcounter, 255, 0)

                    major = cv2.__version__.split('.')[0]
                    if major == '3':
                    # if os.name == "nt":
                        _, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
                    else:
                        contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
                    self.coords = []
                    count = 0

                    if hierarchy is not None:
                        for i in hierarchy[0]:
                            self.traverseHierarchy(hierarchy, contours, count, im, 0)
                            count += 1

                    if len(self.coords) == 3:
                        break
                    else:
                        threshcounter += 17

                if len(self.coords) is not 3:
                    self.CalibrationLog_append("Could not find MAPIR ground target.")
                    #QtWidgets.QApplication.processEvents()
                    return

            line1 = Geometry.distance(self.coords[0], self.coords[1])
            line2 = Geometry.distance(self.coords[1], self.coords[2])
            line3 = Geometry.distance(self.coords[2], self.coords[0])
            hypotenuse = max([line1, line2, line3])

            #Finding Version 2 Target
            if version == "V2":
                center = self.coords[0]
                right = self.coords[1]
                bottom = self.coords[2]

                slope = Geometry.slope(right, bottom)
                dist = center[1] - (slope * center[0]) + ((slope * bottom[0]) - bottom[1])
                dist /= np.sqrt(np.power(slope, 2) + 1)
                # (center_y - slope * center_x + slope * bottom_x - bottom_y) / sqrt(slope^2 + 1)

                slope_right_to_center = Geometry.slope(right, center)
                angle = abs(math.degrees(math.atan(slope_right_to_center)))

            else:
                if hypotenuse == line1:
                    slope = Geometry.slope(self.coords[0], self.coords[1])
                    dist = self.coords[2][1] - (slope * self.coords[2][0]) + ((slope * self.coords[1][0]) - self.coords[1][1])
                    dist /= np.sqrt(np.power(slope, 2) + 1)
                    center = self.coords[2]

                    if (slope < 0 and dist < 0) or (slope >= 0 and dist >= 0):

                        bottom = self.coords[0]
                        right = self.coords[1]
                    else:

                        bottom = self.coords[1]
                        right = self.coords[0]
                elif hypotenuse == line2:
                    slope = Geometry.slope(self.coords[1], self.coords[2])
                    dist = self.coords[0][1] - (slope * self.coords[0][0]) + ((slope * self.coords[2][0]) - self.coords[2][1])
                    dist /= np.sqrt(np.power(slope, 2) + 1)
                    center = self.coords[0]

                    if (slope < 0 and dist < 0) or (slope >= 0 and dist >= 0):

                        bottom = self.coords[1]
                        right = self.coords[2]
                    else:

                        bottom = self.coords[2]
                        right = self.coords[1]
                else:
                    slope = Geometry.slope(self.coords[2], self.coords[0])
                    dist = self.coords[1][1] - (slope * self.coords[1][0]) + ((slope * self.coords[0][0]) - self.coords[0][1])
                    dist /= np.sqrt(np.power(slope, 2) + 1)
                    center = self.coords[1]
                    if (slope < 0 and dist < 0) or (slope >= 0 and dist >= 0):
                        # self.CalibrationLog_append()("slope and dist share sign")
                        bottom = self.coords[2]
                        right = self.coords[0]
                    else:

                        bottom = self.coords[0]
                        right = self.coords[2]

            if version == "V2":
                if len(self.coords) > 0:
                    guidelength = np.sqrt(np.power((center[0] - bottom[0]), 2) + np.power((center[1] - bottom[1]), 2))
                    pixelinch = guidelength / self.CORNER_TO_CORNER

                    rad = (pixelinch * self.CORNER_TO_TARG)
                    vx = center[1] - bottom[1]
                    vy = center[0] - bottom[0]

            else:
                guidelength = np.sqrt(np.power((center[0] - bottom[0]), 2) + np.power((center[1] - bottom[1]), 2))
                pixelinch = guidelength / self.SQ_TO_SQ
                rad = (pixelinch * self.SQ_TO_TARG)
                vx = center[0] - bottom[0]
                vy = center[1] - bottom[1]

            newlen = np.sqrt(vx * vx + vy * vy)

            if version == "V2":
                if len(self.coords) > 0:
                    targ1x = (rad * (vx / newlen)) + self.coords[0][0]
                    targ1y = (rad * (vy / newlen)) + self.coords[0][1]
                    targ2x = (rad * (vx / newlen)) + self.coords[1][0]
                    targ2y = (rad * (vy / newlen)) + self.coords[1][1]
                    targ3x = (rad * (vx / newlen)) + self.coords[2][0]
                    targ3y = (rad * (vy / newlen)) + self.coords[2][1]
                    targ4x = (rad * (vx / newlen)) + self.coords[3][0]
                    targ4y = (rad * (vy / newlen)) + self.coords[3][1]

                    if angle > self.ANGLE_SHIFT_QR:
                        corn_to_targ = self.CORNER_TO_TARG - 1
                        rad = (pixelinch * corn_to_targ)
                        targ1y = -(rad * (vy / newlen)) + self.coords[0][1]
                        targ2y = -(rad * (vy / newlen)) + self.coords[1][1]
                        targ3y = -(rad * (vy / newlen)) + self.coords[2][1]
                        targ4y = -(rad * (vy / newlen)) + self.coords[3][1]


                    target1 = (int(targ1x), int(targ1y))
                    target2 = (int(targ2x), int(targ2y))
                    target3 = (int(targ3x), int(targ3y))
                    target4 = (int(targ4x), int(targ4y))

            else:
                targ1x = (rad * (vx / newlen)) + center[0]
                targ1y = (rad * (vy / newlen)) + center[1]
                targ3x = (rad * (vx / newlen)) + right[0]
                targ3y = (rad * (vy / newlen)) + right[1]

                target1 = (int(targ1x), int(targ1y))
                target3 = (int(targ3x), int(targ3y))
                target2 = (int((np.abs(target1[0] + target3[0])) / 2), int(np.abs((target1[1] + target3[1])) / 2))

            im2 = cv2.imread(image_path, -1)

            # kernel = np.ones((2, 2), np.uint16)
            # im2 = cv2.erode(im2, kernel, iterations=1)
            # im2 = cv2.dilate(im2, kernel, iterations=1)
            if camera_model == "Survey2" and fil == "Red + NIR (NDVI)":
                blue = im2[:, :, 0]
                green = im2[:, :, 1]
                red = im2[:, :, 2] - (im2[:, :, 0] * 0.80)

                if "JPG" in os.path.splitext(image_path)[1]:
                    red[red > 255.0] = 255.0
                    red[red < 0.0] = 0.0
                    red = red.astype("uint8")

                else:
                    red[red > 65535.0] = 65535.0
                    red[red < 0.0] = 0.0
                    red = red.astype("uint16")

                im2 =  cv2.merge((blue, green, red))


            if self.check_if_RGB(camera_model, fil, lens):
                try:
                    targ1values = im2[(target1[1] - int((pixelinch * 0.75) / 2)):(target1[1] + int((pixelinch * 0.75) / 2)),
                                  (target1[0] - int((pixelinch * 0.75) / 2)):(target1[0] + int((pixelinch * 0.75) / 2))]


                    targ2values = im2[(target2[1] - int((pixelinch * 0.75) / 2)):(target2[1] + int((pixelinch * 0.75) / 2)),
                                  (target2[0] - int((pixelinch * 0.75) / 2)):(target2[0] + int((pixelinch * 0.75) / 2))]

                    targ3values = im2[(target3[1] - int((pixelinch * 0.75) / 2)):(target3[1] + int((pixelinch * 0.75) / 2)),
                                  (target3[0] - int((pixelinch * 0.75) / 2)):(target3[0] + int((pixelinch * 0.75) / 2))]
                except Exception as e:
                    exc_type, exc_obj,exc_tb = sys.exc_info()
                    print(e)
                    print("Line: " + str(exc_tb.tb_lineno))

                t1redmean = np.mean(targ1values[:, :, 2])
                t1greenmean = np.mean(targ1values[:, :, 1])
                t1bluemean = np.mean(targ1values[:, :, 0])

                t2redmean = np.mean(targ2values[:, :, 2])
                t2greenmean = np.mean(targ2values[:, :, 1])
                t2bluemean = np.mean(targ2values[:, :, 0])

                t3redmean = np.mean(targ3values[:, :, 2])
                t3greenmean = np.mean(targ3values[:, :, 1])
                t3bluemean = np.mean(targ3values[:, :, 0])

                yred = []
                yblue = []
                ygreen = []
                if version == "V2":
                    if len(self.coords) > 0:
                        targ4values = im2[(target4[1] - int((pixelinch * 0.75) / 2)):(target4[1] + int((pixelinch * 0.75) / 2)),
                                      (target4[0] - int((pixelinch * 0.75) / 2)):(target4[0] + int((pixelinch * 0.75) / 2))]
                        t4redmean = np.mean(targ4values[:, :, 2])
                        t4greenmean = np.mean(targ4values[:, :, 1])
                        t4bluemean = np.mean(targ4values[:, :, 0])
                        yred = [0.87, 0.51, 0.23, 0.0]
                        yblue = [0.87, 0.51, 0.23, 0.0]
                        ygreen = [0.87, 0.51, 0.23, 0.0]

                        xred = [t1redmean, t2redmean, t3redmean, t4redmean]
                        xgreen = [t1greenmean, t2greenmean, t3greenmean, t4greenmean]
                        xblue = [t1bluemean, t2bluemean, t3bluemean, t4bluemean]

                    #self.print_center_targs(image_path, targ1values, targ2values, targ3values, targ4values, target1, target2, target3, target4, angle)

                else:
                    yred = [0.87, 0.51, 0.23]
                    yblue = [0.87, 0.51, 0.23]
                    ygreen = [0.87, 0.51, 0.23]

                    xred = [t1redmean, t2redmean, t3redmean]
                    xgreen = [t1greenmean, t2greenmean, t3greenmean]
                    xblue = [t1bluemean, t2bluemean, t3bluemean]

                if ((camera_model == "Survey3" and fil == "RGN") or (camera_model == "DJI Phantom 4 Pro")
                        or (camera_model == "Kernel 14.4" and fil =="550/660/850")):
                    yred = self.refvalues[self.ref]["550/660/850"][0]
                    ygreen = self.refvalues[self.ref]["550/660/850"][1]
                    yblue = self.refvalues[self.ref]["550/660/850"][2]

                elif ((camera_model == "Survey3" and fil == "NGB")
                    or (camera_model == "Kernel 14.4" and fil == "475/550/850")):

                    yred = self.refvalues[self.ref]["475/550/850"][0]
                    ygreen = self.refvalues[self.ref]["475/550/850"][1]
                    yblue = self.refvalues[self.ref]["475/550/850"][2]

                elif (camera_model == "Survey3" and fil == "OCN") or (camera_model == "Kernel 14.4" and fil == "OCN"):

                    yred = self.refvalues[self.ref]["490/615/808"][0]
                    ygreen = self.refvalues[self.ref]["490/615/808"][1]
                    yblue = self.refvalues[self.ref]["490/615/808"][2]

                else: #Survey 2 - NDVI
                    yred = self.refvalues[self.ref]["660/850"][0]
                    ygreen = self.refvalues[self.ref]["660/850"][1]
                    yblue = self.refvalues[self.ref]["660/850"][2]

                if self.get_filetype(image_path) == "JPG":
                    xred = [x / 255 for x in xred]
                    xgreen = [x / 255 for x in xgreen]
                    xblue = [x / 255 for x in xblue]

                elif self.get_filetype(image_path) == "TIF":
                    xred = [x / 65535 for x in xred]
                    xgreen = [x / 65535 for x in xgreen]
                    xblue = [x / 65535 for x in xblue]

                xred, yred = self.check_exposure_quality(xred, yred)
                xgreen, ygreen = self.check_exposure_quality(xgreen, ygreen)
                xblue, yblue = self.check_exposure_quality(xblue, yblue)

                if any(item == 1 or item == 0 or np.isnan(item) for item in xred + xgreen + xblue):
                    raise Exception("Provided calibration target photo is not generating good calibration values. Please use another calibration target photo.")

                x_channels = [xred, xgreen, xblue]

                if self.bad_target_photo(x_channels):
                    self.CalibrationLog_append("WARNING: Provided calibration target photo is not generating good calibration values. For optimal calibration, please use another calibration target photo or check that white balance and exposure settings are set to default values. \n")

                red_slope, red_intercept = self.get_LOBF_values(xred, yred)
                green_slope, green_intercept = self.get_LOBF_values(xgreen, ygreen)
                blue_slope, blue_intercept = self.get_LOBF_values(xblue, yblue)

                #return cofr, cofg, cofb
                self.multiplication_values["red"]["slope"] = red_slope
                self.multiplication_values["red"]["intercept"] = red_intercept

                self.multiplication_values["green"]["slope"] = green_slope
                self.multiplication_values["green"]["intercept"] = green_intercept

                self.multiplication_values["blue"]["slope"] = blue_slope
                self.multiplication_values["blue"]["intercept"] = blue_intercept

                if (camera_model == "Survey2" and fil == "Red + NIR (NDVI)"):
                    self.multiplication_values["green"]["slope"] = 1
                    self.multiplication_values["green"]["intercept"] = 0


                if version == "V2":
                    if len(self.coords) > 0:
                        self.CalibrationLog_append("Found QR Target Model 2,  proceeding with calibration...")
                    else:
                        self.CalibrationLog_append("Could not find Calibration Target.")
                else:
                    self.CalibrationLog_append("Found QR Target Model 1,  proceeding with calibration...")

            else:
                if version == "V2":
                    if len(self.coords) > 0:
                        targ1values = im2[(target1[1] - int((pixelinch * 0.75) / 2)):(target1[1] + int((pixelinch * 0.75) / 2)),
                                      (target1[0] - int((pixelinch * 0.75) / 2)):(target1[0] + int((pixelinch * 0.75) / 2))]
                        targ2values = im2[(target2[1] - int((pixelinch * 0.75) / 2)):(target2[1] + int((pixelinch * 0.75) / 2)),
                                      (target2[0] - int((pixelinch * 0.75) / 2)):(target2[0] + int((pixelinch * 0.75) / 2))]
                        targ3values = im2[(target3[1] - int((pixelinch * 0.75) / 2)):(target3[1] + int((pixelinch * 0.75) / 2)),
                                      (target3[0] - int((pixelinch * 0.75) / 2)):(target3[0] + int((pixelinch * 0.75) / 2))]
                        targ4values = im2[(target4[1] - int((pixelinch * 0.75) / 2)):(target4[1] + int((pixelinch * 0.75) / 2)),
                                      (target4[0] - int((pixelinch * 0.75) / 2)):(target4[0] + int((pixelinch * 0.75) / 2))]

                        if (len(im2.shape) > 2) and fil in ["RE", "NIR", "Red"]:
                            t1mean = np.mean(targ1values[:,:,2])
                            t2mean = np.mean(targ2values[:,:,2])
                            t3mean = np.mean(targ3values[:,:,2])
                            t4mean = np.mean(targ4values[:,:,2])

                        elif (len(im2.shape) > 2) and fil in ["Green"]:
                            t1mean = np.mean(targ1values[:,:,1])
                            t2mean = np.mean(targ2values[:,:,1])
                            t3mean = np.mean(targ3values[:,:,1])
                            t4mean = np.mean(targ4values[:,:,1])

                        elif (len(im2.shape) > 2) and fil in ["Blue"]:
                            t1mean = np.mean(targ1values[:,:,0])
                            t2mean = np.mean(targ2values[:,:,0])
                            t3mean = np.mean(targ3values[:,:,0])
                            t4mean = np.mean(targ4values[:,:,0])

                        else:
                            t1mean = np.mean(targ1values)
                            t2mean = np.mean(targ2values)
                            t3mean = np.mean(targ3values)
                            t4mean = np.mean(targ4values)

                        y = [0.87, 0.51, 0.23, 0.0]
                        x = [t1mean, t2mean, t3mean, t4mean]
                else:
                    targ1values = im2[(target1[1] - int((pixelinch * 0.75) / 2)):(target1[1] + int((pixelinch * 0.75) / 2)),
                                  (target1[0] - int((pixelinch * 0.75) / 2)):(target1[0] + int((pixelinch * 0.75) / 2))]

                    targ2values = im2[(target2[1] - int((pixelinch * 0.75) / 2)):(target2[1] + int((pixelinch * 0.75) / 2)),
                                  (target2[0] - int((pixelinch * 0.75) / 2)):(target2[0] + int((pixelinch * 0.75) / 2))]

                    targ3values = im2[(target3[1] - int((pixelinch * 0.75) / 2)):(target3[1] + int((pixelinch * 0.75) / 2)),
                                  (target3[0] - int((pixelinch * 0.75) / 2)):(target3[0] + int((pixelinch * 0.75) / 2))]


                    if (len(im2.shape) > 2) and fil in ["RE", "NIR", "Red"]:
                        t1mean = np.mean(targ1values[:,:,2])
                        t2mean = np.mean(targ2values[:,:,2])
                        t3mean = np.mean(targ3values[:,:,2])

                    elif (len(im2.shape) > 2) and fil in ["Green"]:
                        t1mean = np.mean(targ1values[:,:,1])
                        t2mean = np.mean(targ2values[:,:,1])
                        t3mean = np.mean(targ3values[:,:,1])

                    elif (len(im2.shape) > 2) and fil in ["Blue"]:
                        t1mean = np.mean(targ1values[:,:,0])
                        t2mean = np.mean(targ2values[:,:,0])
                        t3mean = np.mean(targ3values[:,:,0])
                    else:
                        t1mean = np.mean(targ1values)
                        t2mean = np.mean(targ2values)
                        t3mean = np.mean(targ3values)
                    y = [0.87, 0.51, 0.23]
                    x = [t1mean, t2mean, t3mean]


                if (fil == "NIR" and (camera_model in ["Survey2", "Survey3"])):
                    y = self.refvalues[self.ref]["850"][0]

                elif camera_model == "Survey2" and fil == "Red":
                    y = self.refvalues[self.ref]["650"][0]

                elif camera_model == "Survey2" and fil == "Green":
                    y = self.refvalues[self.ref]["550"][1]

                elif camera_model == "Survey2" and fil == "Blue":
                    y = self.refvalues[self.ref]["450"][2]

                elif fil in ['405', '450', '490', '518', '550', '590', '615', '632', '650', '685', '725', '808', '850']:
                    mono_fil = 'Mono' + fil
                    y = self.refvalues[self.ref][mono_fil]

                elif fil == "RE":
                    y = self.refvalues[self.ref]["725"]


                if self.get_filetype(image_path) == "JPG":
                    x = [i / 255 for i in x]

                elif self.get_filetype(image_path) == "TIF":
                    x = [i / 65535 for i in x]

                if self.bad_target_photo([x]):
                    self.CalibrationLog_append("WARNING: Provided calibration target photo is not generating good calibration values. For optimal calibration, please use another calibration target photo or check that white balance and exposure settings are set to defualt values. \n")

                slope, intercept = self.get_LOBF_values(x, y)

                self.multiplication_values["mono"]["slope"] = slope
                self.multiplication_values["mono"]["intercept"] = intercept

                if version == "V2":
                    if len(self.coords) > 0:
                        self.CalibrationLog_append("Found QR Target Model 2, please proceed with calibration.")
                    else:
                        self.CalibrationLog_append("Could not find Calibration Target.")
                else:
                    self.CalibrationLog_append("Found QR Target Model 1, please proceed with calibration.")
                #QtWidgets.QApplication.processEvents()

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(str(e) + ' Line: ' + str(exc_tb.tb_lineno))
            self.CalibrationLog_append("Error: " + str(e))
            return
            # slope, intcpt, r_value, p_value, std_err = stats.linregress(x, y)
            # self.CalibrationLog_append()("Found QR Target, please proceed with calibration.")
            #
            # return [intcpt, slope]
        # Calibration Steps: End


    def check_if_RGB(self, camera, filt, lens): #Kernel 14.4, Survey 3 - RGBs, and Phantoms
        if camera in self.DJIS:
            return True
        elif (camera == "Survey3" and filt not in ["RE", "NIR"]):
            return True
        elif camera == "Kernel 14.4":
            return True
        elif camera == "Survey2" and filt == "Red + NIR (NDVI)":
            return True
        elif camera == "Survey2" and filt == "RGB":
            return True
        else:
            return False


    def traverseHierarchy(self, tier, cont, index, image, depth):

        if tier[0][index][2] != -1:
            self.traverseHierarchy(tier, cont, tier[0][index][2], image, depth + 1)
            return
        elif depth >= 2:
            c = cont[index]
            moment = cv2.moments(c)
            if int(moment['m00']) != 0:
                x = int(moment['m10'] / moment['m00'])
                y = int(moment['m01'] / moment['m00'])
                self.coords.append([x, y])
            return


    def bad_target_photo(self, channels):
        for channel in channels:
            if channel != sorted(channel, reverse=True):
                return True

            for targ in channel:
                if math.isnan(targ):
                    return True

        return False

    def check_exposure_quality(self, x, y):
        if (x[0] == 1 and x[-1] == 0):
            x = x[1:]
            y = y[1:]

        elif (x[0] == 1):
            x = x[1:]
            y = y[1:]

        elif (x[-1] == 0):
            x = x[:-1]
            y = y[:-1]

        return x, y


    #Function that calibrates global max and mins
    def calibrate(self, mult_values, value):
        slope = mult_values["slope"]
        intercept = mult_values["intercept"]

        return int((slope * value) + intercept)

    def get_HC_value(self, color):
        HCP = int(self.HCP_value) / 100
        unique, counts = np.unique(color, return_counts=True)
        freq_array = np.asarray((unique, counts)).T

        total_pixels = color.size

        sum_pixels = 0
        for pixel in freq_array[::-1]:
            sum_pixels += pixel[1]

            if (sum_pixels / total_pixels) >= HCP:
                return pixel[0]

    # def on_histogramClipBox_toggled(self):
    #     if self.histogramClipBox  == 2:
    #         self.Histogram_Clipping_Percentage.setEnabled(True)
    #         #self.HCP_value.setEnabled(True)
    #
    #     elif self.histogramClipBox  == 0:
    #         self.Histogram_Clipping_Percentage.setEnabled(False)
    #         #self.HCP_value.setEnabled(False)
    #         #self.HCP_value.clear()

    def check_HCP_value(self):
        # if "." in self.HCP_value :
        #     return True

        if self.histogramClipBox  and not self.HCP_value :
            return True

        elif (self.histogramClipBox  and (int(self.HCP_value ) < 1 or int(self.HCP_value ) > 100)):
            return True

        else:
            return False

    def failed_calibration(self):
        self.failed_calib = True
        self.CalibrationLog_append("No default calibration data for selected camera model. Please please supply a MAPIR Reflectance Target to proceed.\n")

    # def make_calibration_out_dir(self):
    def get_files_to_calibrate(self):
        files = []
        files.extend(MAPIR_ProcessingCLI.get_tiff_files_in_dir('.'))
        files.extend(MAPIR_ProcessingCLI.get_jpg_files_in_dir('.'))
        return files

    # def get_calibration_out_path(self, parent_dirname, folder_count):
    #     parent_dirname + os.sep + "Calibrated_" + str(folder_count)

    def make_calibration_out_dir(self, parent_dirname):
        foldercount = 1
        endloop = False
        while endloop is False:
            # outdir = self.get_calibration_out_path(parent_dirname, foldercount)
            outdir = parent_dirname + os.sep + "Calibrated_" + str(foldercount)

            if os.path.exists(outdir):
                foldercount += 1
            else:
                os.mkdir(outdir)
                endloop = True
        return outdir

    def on_CalibrateButton_released(self):
        self.failed_calib = False
        outdir = None
        if not self.calibration_QR_file and self.CalibrationInFolder :
            self.useqr = False
            self.CalibrationLog_append("Attempting to calibrate without MAPIR Reflectance Target...\n")

        try:

            if self.check_HCP_value():
                self.CalibrationLog_append("Attention! Please select a Histogram Clipping Percentage value between 1-100.")
                self.CalibrationLog_append("For example: for 20%, please enter 20\n")

            # elif len(self.CalibrationInFolder.text()) <= 0 \
            #         and len(self.CalibrationInFolder_2.text()) <= 0 \
            #         and len(self.CalibrationInFolder_3.text()) <= 0 \
            #         and len(self.CalibrationInFolder_4.text()) <= 0 \
            #         and len(self.CalibrationInFolder_5.text()) <= 0 \
            #         and len(self.CalibrationInFolder_6.text()) <= 0:
            #     self.CalibrationLog_append()("Attention! Please select a calibration folder.\n")
            #
            else:
                self.CalibrationLog_append("Analyzing Input Directory. Please wait... \n")
                self.firstpass = True
                # self.CalibrationLog_append()("CSV Input: \n" + str(self.refvalues))
                # self.CalibrationLog_append()("Calibration button pressed.\n")
                calfolder = self.CalibrationInFolder


                self.pixel_min_max = {"redmax": 0.0, "redmin": 65535.0,
                                      "greenmax": 0.0, "greenmin": 65535.0,
                                      "bluemax": 0.0, "bluemin": 65535.0}

                self.HC_max = {"redmax": 0.0,
                               "greenmax": 0.0,
                               "bluemax": 0.0, }

                self.HC_mono_max = 0
                self.multiple_inputs = False
                self.maxes = {}
                self.mins = {}
                self.HC_mult_max = {}

                # self.CalibrationLog_append()("Calibration target folder is: " + calfolder + "\n")
                files_to_calibrate = []


                indexes = [
                    [self.calibration_camera_model , self.calibration_filter,
                     self.calibration_lens],
                ]
                #AAG:
                self.multiple_inputs = False
                # if indexes[1][0] != "":
                #     self.multiple_inputs = True

                folderind = [calfolder ]

                for j, ind in enumerate(indexes):
                    CHECKED = 2
                    UNCHECKED = 0

                    camera_model = ind[0]
                    filt = ind[1]
                    lens = ind[2]

                    if camera_model == "":
                        pass

                    elif self.check_if_RGB(camera_model, filt, lens):

                        if os.path.exists(folderind[j]):
                            os.chdir(folderind[j])
                            files_to_calibrate = self.get_files_to_calibrate()

                            if "tif" or "TIF" or "jpg" or "JPG" in files_to_calibrate[0]:
                                outdir = self.make_calibration_out_dir(folderind[j])

                        for i, calpixel in enumerate(files_to_calibrate):
                            file_ext = calpixel.split('.')[-1]
                            # if file_ext == 'tif' or file_ext == 'TIF':
                            #     img = tifffile.imread(calpixel)
                            # else:
                            img = cv2.imread(calpixel, cv2.IMREAD_UNCHANGED)
                            if len(img.shape) < 3:
                                raise IndexError("RGB filter was selected but input folders contain MONO images")

                            blue = img[:, :, 0]
                            green = img[:, :, 1]
                            red = img[:, :, 2]

                            if camera_model == "Survey2" and filt == "Red + NIR (NDVI)":
                                red = img[:, :, 2] - (blue * 0.80)

                            # these are a little confusing, but the check to find the highest and lowest pixel value
                            # in each channel in each image and keep the highest/lowest value found.
                            if self.seed_pass == False:
                                self.pixel_min_max["redmax"] = red.max()
                                self.pixel_min_max["redmin"] = red.min()

                                self.pixel_min_max["greenmax"] = green.max()
                                self.pixel_min_max["greenmin"] = green.min()

                                self.pixel_min_max["bluemax"] = blue.max()
                                self.pixel_min_max["bluemin"] = blue.min()

                                if self.histogramClipBox  == self.CHECKED:
                                    self.HC_max["redmax"] = self.get_HC_value(red)
                                    self.HC_max["greenmax"] = self.get_HC_value(green)
                                    self.HC_max["bluemax"] = self.get_HC_value(blue)

                                self.seed_pass = True

                            else:

                                try:
                                    # compare current image min-max with global min-max (non-calibrated)
                                    self.pixel_min_max["redmax"] = max(red.max(), self.pixel_min_max["redmax"])
                                    self.pixel_min_max["redmin"] = min(red.min(), self.pixel_min_max["redmin"])

                                    self.pixel_min_max["greenmax"] = max(green.max(), self.pixel_min_max["greenmax"])
                                    self.pixel_min_max["greenmin"] = min(green.min(), self.pixel_min_max["greenmin"])

                                    self.pixel_min_max["bluemax"] = max(blue.max(), self.pixel_min_max["bluemax"])
                                    self.pixel_min_max["bluemin"] = min(blue.min(), self.pixel_min_max["bluemin"])

                                    if self.histogramClipBox  == self.CHECKED:
                                        self.HC_max["redmax"] = max(self.get_HC_value(red), self.HC_max["redmax"])
                                        self.HC_max["greenmax"] = max(self.get_HC_value(green), self.HC_max["greenmax"])
                                        self.HC_max["bluemax"] = max(self.get_HC_value(blue), self.HC_max["bluemax"])


                                except Exception as e:
                                    print("ERROR: ", e)
                                    exc_type, exc_obj, exc_tb = sys.exc_info()
                                    print(' Line: ' + str(exc_tb.tb_lineno))

                        min_max_list = ["redmax", "redmin", "greenmax", "greenmin", "bluemin", "bluemax"]
                        if not self.useqr:
                            filetype = calpixel.split(".")[-1]
                            min_max_wo_g_list = ["redmax", "redmin", "bluemin", "bluemax"]

                            if camera_model == "Survey1":  # Survey1_NDVI
                                min_max_list = min_max_wo_g_list
                                if filetype in self.JPGS:
                                    base_coef = self.BASE_COEFF_SURVEY1_NDVI_JPG

                                else:
                                    self.failed_calibration()
                                    break

                            elif camera_model == "Survey2" and filt == "Red + NIR (NDVI)":  # Survey 2 + Red + NIR
                                min_max_list = min_max_wo_g_list

                                if filetype in self.TIFS:
                                    base_coef = self.BASE_COEFF_SURVEY2_NDVI_TIF

                                elif filetype in self.JPGS:
                                    base_coef = self.BASE_COEFF_SURVEY2_NDVI_JPG

                                else:
                                    self.failed_calibration()
                                    break

                            elif camera_model == "DJI Phantom 3a":
                                min_max_list = min_max_wo_g_list
                                if filetype in self.TIFS:
                                    base_coef = self.BASE_COEFF_DJIX3_NDVI_TIF

                                elif filetype in self.JPGS:
                                    base_coef = self.BASE_COEFF_DJIX3_NDVI_JPG

                                else:
                                    self.failed_calibration()
                                    break

                            elif camera_model == "DJI Phantom 4":
                                min_max_list = min_max_wo_g_list
                                if filetype in self.TIFS:
                                    base_coef = self.BASE_COEFF_DJIPHANTOM4_NDVI_TIF

                                elif filetype in self.JPGS:
                                    base_coef = self.BASE_COEFF_DJIPHANTOM4_NDVI_JPG

                                else:
                                    self.failed_calibration()
                                    break

                            elif camera_model in ["DJI Phantom 4 Pro", "DJI Phantom 3a"]:
                                min_max_list = min_max_wo_g_list

                                if filetype in self.TIFS:
                                    base_coef = self.BASE_COEFF_DJIPHANTOM3_NDVI_TIF

                                elif filetype in self.JPGS:
                                    base_coef = self.BASE_COEFF_DJIPHANTOM3_NDVI_JPG
                                else:
                                    self.failed_calibration()
                                    break

                            elif camera_model == "Survey3":

                                if filt == "RGN":
                                    if filetype in self.JPGS:
                                        base_coef = self.BASE_COEFF_SURVEY3_RGN_JPG
                                    elif filetype in self.TIFS:
                                        base_coef = self.BASE_COEFF_SURVEY3_RGN_TIF

                                elif filt == "OCN":
                                    if filetype in self.JPGS:
                                        base_coef = self.BASE_COEFF_SURVEY3_OCN_JPG
                                    elif filetype in self.TIFS:
                                        base_coef = self.BASE_COEFF_SURVEY3_OCN_TIF

                                elif filt == "NGB":
                                    if filetype in self.JPGS:
                                        base_coef = self.BASE_COEFF_SURVEY3_NGB_JPG
                                    elif filetype in self.TIFS:
                                        base_coef = self.BASE_COEFF_SURVEY3_NGB_TIF

                                else:
                                    self.failed_calibration()
                                    break

                            else:
                                self.failed_calibration()
                                break

                            for min_max in min_max_list:
                                if len(min_max) == 6:
                                    color = min_max[:3]

                                elif len(min_max) == 7:
                                    color = min_max[:4]
                                else:
                                    color = min_max[:5]

                                self.pixel_min_max[min_max] = self.calibrate(base_coef[color], self.pixel_min_max[min_max])

                            if self.histogramClipBox  == self.CHECKED:
                                self.HC_max["redmax"] = self.calibrate(base_coef["red"], self.HC_max["redmax"])
                                self.HC_max["greenmax"] = self.calibrate(base_coef["green"], self.HC_max["greenmax"])
                                self.HC_max["bluemax"] = self.calibrate(base_coef["blue"], self.HC_max["bluemax"])

                        self.seed_pass = False

                        # Calibrate global max and mins
                        if self.useqr:

                            for min_max in min_max_list:
                                if len(min_max) == 6:
                                    color = min_max[:3]
                                elif len(min_max) == 7:
                                    color = min_max[:4]
                                else:
                                    color = min_max[:5]

                                self.pixel_min_max[min_max] = self.calibrate(self.multiplication_values[color],
                                                                             self.pixel_min_max[min_max])

                            if self.histogramClipBox  == self.CHECKED:
                                self.HC_max["redmax"] = self.calibrate(self.multiplication_values["red"],
                                                                       self.HC_max["redmax"])
                                self.HC_max["greenmax"] = self.calibrate(self.multiplication_values["green"],
                                                                         self.HC_max["greenmax"])
                                self.HC_max["bluemax"] = self.calibrate(self.multiplication_values["blue"],
                                                                        self.HC_max["bluemax"])

                        for i, calfile in enumerate(files_to_calibrate):

                            cameramodel = ind
                            self.append_calibrating_image_message_to_calibration_log(i, files_to_calibrate)
                            #QtWidgets.QApplication.processEvents()
                            if self.useqr:
                                try:
                                    self.CalibratePhotos(calfile, self.multiplication_values, self.pixel_min_max, outdir,
                                                         ind)
                                except Exception as e:
                                    exc_type, exc_obj, exc_tb = sys.exc_info()
                                    self.CalibrationLog_append(str(e))
                            else:
                                self.CalibratePhotos(calfile, base_coef, self.pixel_min_max, outdir, ind)

                    else:
                        if os.path.exists(folderind[j]):
                            os.chdir(folderind[j])
                            files_to_calibrate = self.get_files_to_calibrate()

                            if not self.multiple_inputs:
                                if "tif" or "TIF" or "jpg" or "JPG" in files_to_calibrate[0]:
                                    outdir = self.make_calibration_out_dir(folderind[j])

                        for i, calpixel in enumerate(files_to_calibrate):
                            file_ext = calpixel.split('.')[-1]
                            # if file_ext == 'tif' or file_ext == 'TIF':
                            #     img = tifffile.imread(calpixel)
                            # else:
                            # img = cv2.imread(calpixel, cv2.IMREAD_UNCHANGED)
                            img = cv2.imread(calpixel, cv2.IMREAD_UNCHANGED)
                            # img = cv2.imread(calpixel, -1)

                            if len(img.shape) > 2:
                                raise IndexError("Mono filter was selected but input folders contain RGB images")

                            if self.seed_pass == False:
                                self.monominmax["max"] = img.max()
                                self.monominmax["min"] = img.min()

                                if self.histogramClipBox  == self.CHECKED:
                                    self.HC_mono_max = self.get_HC_value(img)

                                self.seed_pass = True

                            else:

                                try:
                                    # compare current image min-max with global min-max (non-calibrated)
                                    self.monominmax["max"] = max(img.max(), self.monominmax["max"])
                                    self.monominmax["min"] = min(img.min(), self.monominmax["min"])

                                    if self.histogramClipBox  == self.CHECKED:
                                        self.HC_mono_max = max(self.get_HC_value(img), self.HC_mono_max)

                                except Exception as e:
                                    exc_type, exc_obj, exc_tb = sys.exc_info()

                        if not self.useqr:
                            filetype = calpixel.split(".")[-1]

                            if camera_model == "Survey2":
                                if filt == "Red":
                                    if filetype in self.JPGS:
                                        base_coef = self.BASE_COEFF_SURVEY2_RED_JPG

                                    elif filetype in self.TIFS:
                                        base_coef = self.BASE_COEFF_SURVEY2_RED_TIF

                                    else:
                                        self.failed_calibration()
                                        break

                                elif filt == "Green":
                                    if filetype in self.JPGS:
                                        base_coef = self.BASE_COEFF_SURVEY2_GREEN_JPG

                                    elif filetype in self.TIFS:
                                        base_coef = self.BASE_COEFF_SURVEY2_GREEN_TIF

                                    else:
                                        self.failed_calibration()
                                        break

                                elif filt == "Blue":
                                    if filetype in self.JPGS:
                                        base_coef = self.BASE_COEFF_SURVEY2_BLUE_JPG

                                    elif filetype in self.TIFS:
                                        base_coef = self.BASE_COEFF_SURVEY2_BLUE_TIF

                                    else:
                                        self.failed_calibration()
                                        break

                                elif filt == "NIR":
                                    if filetype in self.JPGS:
                                        base_coef = self.BASE_COEFF_SURVEY2_NIR_JPG

                                    elif filetype in self.TIFS:
                                        base_coef = self.BASE_COEFF_SURVEY2_NIR_TIF

                                    else:
                                        self.failed_calibration()
                                        break

                                else:
                                    self.failed_calibration()
                                    break

                            elif camera_model == "Survey3":
                                if filt == "RE":
                                    if filetype in self.JPGS:
                                        base_coef = self.BASE_COEFF_SURVEY3_RE_JPG

                                    elif filetype in self.TIFS:
                                        base_coef = self.BASE_COEFF_SURVEY3_RE_TIF

                                    else:
                                        self.failed_calibration()
                                        break

                                elif filt == "NIR":
                                    if filetype in self.TIFS:
                                        base_coef = self.BASE_COEFF_SURVEY3_NIR_TIF

                                    else:
                                        self.failed_calibration()
                                        break

                            elif camera_model == "Kernel 3.2":
                                raise UnboundLocalError(
                                    "Calibration without a calibration target is not supported for Kernel 3.2")

                            if self.multiple_inputs:
                                self.maxes[j + 1] = self.calibrate(base_coef, img.max())
                                self.mins[j + 1] = self.calibrate(base_coef, img.min())

                            else:
                                self.monominmax["max"] = self.calibrate(base_coef, self.monominmax["max"])
                                self.monominmax["min"] = self.calibrate(base_coef, self.monominmax["min"])

                        if self.useqr:
                            if self.multiple_inputs:
                                self.maxes[j + 1] = self.calibrate(self.qr_coeffs[j + 1], img.max())
                                self.mins[j + 1] = self.calibrate(self.qr_coeffs[j + 1], img.min())

                                if self.histogramClipBox  == self.CHECKED:
                                    self.HC_mult_max[j + 1] = self.calibrate(self.qr_coeffs[j + 1], self.get_HC_value(img))

                            else:
                                self.monominmax["max"] = self.calibrate(self.multiplication_values["mono"],
                                                                        self.monominmax["max"])
                                self.monominmax["min"] = self.calibrate(self.multiplication_values["mono"],
                                                                        self.monominmax["min"])

                                if self.histogramClipBox  == self.CHECKED:
                                    self.HC_mono_max = self.calibrate(self.multiplication_values["mono"], self.HC_mono_max)

                        if not self.multiple_inputs:
                            for i, calfile in enumerate(files_to_calibrate):
                                cameramodel = ind
                                if self.useqr:
                                    try:
                                        self.append_calibrating_image_message_to_calibration_log(i, files_to_calibrate)
                                        #QtWidgets.QApplication.processEvents()
                                        self.CalibrateMono(calfile, self.multiplication_values["mono"], outdir, ind)

                                    except Exception as e:
                                        print("ERROR: ", e)
                                        exc_type, exc_obj, exc_tb = sys.exc_info()
                                        exc_type, exc_obj, exc_tb = sys.exc_info()
                                        print(' Line: ' + str(exc_tb.tb_lineno))
                                        self.CalibrationLog_append(str(e))
                                else:
                                    self.append_calibrating_image_message_to_calibration_log(i, files_to_calibrate)
                                    #QtWidgets.QApplication.processEvents()

                                    self.CalibrateMono(calfile, base_coef, outdir, ind)

                if self.multiple_inputs and not self.check_if_RGB(camera_model, filt, lens):
                    self.monominmax["max"] = max(list(self.maxes.values()))
                    self.monominmax["min"] = min(list(self.mins.values()))

                    if self.histogramClipBox  == self.CHECKED:
                        self.HC_mono_max = max(list(self.HC_mult_max.values()))

                    for j, ind in enumerate(indexes):
                        camera_model = ind[0]
                        filt = ind[1]
                        lens = ind[2]

                        if camera_model == "":
                            continue

                        if os.path.exists(folderind[j]):
                            os.chdir(folderind[j])
                            files_to_calibrate = self.get_files_to_calibrate()

                            if "tif" or "TIF" or "jpg" or "JPG" in files_to_calibrate[0]:
                                outdir = self.make_calibration_out_dir(folderind[j])

                        for i, calfile in enumerate(files_to_calibrate):
                            if self.useqr:
                                try:
                                    self.append_calibrating_image_message_to_calibration_log(i, files_to_calibrate)
                                    #QtWidgets.QApplication.processEvents()
                                    self.CalibrateMono(calfile, self.qr_coeffs[j + 1], outdir, ind)

                                except Exception as e:
                                    print("ERROR: ", e)
                                    exc_type, exc_obj, exc_tb = sys.exc_info()
                                    exc_type, exc_obj, exc_tb = sys.exc_info()
                                    print(' Line: ' + str(exc_tb.tb_lineno))
                                    self.CalibrationLog_append(str(e))
                            else:
                                raise Exception(
                                    "Calibrating multiple inputs without calibration target not supported for mono images")

                if not self.failed_calib:
                    self.CalibrationLog_append("Finished Calibrating " + str(
                        len(files_to_calibrate) ) + " images\n")
                #self.CalibrateButton.setEnabled(True)
                self.seed_pass = False


        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(e)
            print("Line: " + str(exc_tb.tb_lineno))

        return outdir



    def save_calibrated_image_without_conversion(self, in_image_path, calibrated_image, out_dir):
        out_image_path = out_dir + in_image_path.split('.')[1] + "_CALIBRATED." + in_image_path.split('.')[2]
        if 'tif' in in_image_path.split('.')[2].lower():
            cv2.imencode(".tif", calibrated_image)
            cv2.imwrite(out_image_path, calibrated_image)

            # tiff = gdal.Open(in_image_path, gdal.GA_ReadOnly)
            # tiff_has_no_projection_data = tiff.GetProjection() == ''
            # tiff = None

            # # if tiff_has_no_projection_data:
            #     cv2.imencode(".tif", calibrated_image)
            #     cv2.imwrite(out_image_path, calibrated_image)
            #     self.copyExif(in_image_path, out_image_path)
            # # else:
            # #     # cv2.imencode(".tif", calibrated_image)
            # #     # cv2.imwrite(out_image_path, calibrated_image)
            # #     self.geotiff_with_metadata_from_rgba(in_image_path, calibrated_image, out_image_path)

        else:
            cv2.imwrite(out_image_path, calibrated_image, [int(cv2.IMWRITE_JPEG_QUALITY), 100])

        self.copyExif(in_image_path, out_image_path)

        # self.copyExif(in_image_path, out_image_path)


    def calculate_mode(self, freq_array):
        pixel_freq = 0
        mode = 0
        for pixel in freq_array:
            if pixel[1] > pixel_freq:
                pixel_freq = pixel[1]
                mode = pixel[0]
        return mode

    def get_global_max_and_min_calibrated_pixel_values(self, camera_model, filt, minmaxes):
        ### find the global maximum (maxpixel) and minimum (minpixel) calibrated pixel values over the entire directory.
        red_min = minmaxes["redmin"]
        red_max = minmaxes["redmax"]
        blue_min = minmaxes["bluemin"]
        blue_max = minmaxes["bluemax"]
        green_min = minmaxes["greenmin"]
        green_max = minmaxes["greenmax"]

        if camera_model == "Survey1":  ###Survey1 NDVI
            maxpixel = max([blue_max, red_max])
            minpixel = min([blue_min, red_min])
            # blue = refimg[:, :, 0] - (refimg[:, :, 2] * 0.80)  # Subtract the NIR bleed over from the blue channel

        elif camera_model in ["Survey2", "Survey3"] and filt in ["NIR", "Red", "RE"]:
            maxpixel = red_max
            minpixel = red_min

        elif camera_model == 'Survey2':
            if filt == 'Green':
                maxpixel = green_max
                minpixel = green_min
            elif filt == 'Blue':
                maxpixel = blue_max
                minpixel = blue_min

        elif camera_model in ["Survey3", "DJI Phantom 4 Pro"]:
            maxpixel = max([blue_max, red_max, green_max])
            minpixel = min([blue_min, red_min, green_min])

        else:  ###Survey2 NDVI
            maxpixel = max([blue_max, red_max])
            minpixel = min([blue_min, red_min])
            # if ind[0] == 4:
            #     red = refimg[:, :, 2] - (refimg[:, :, 0] * 0.80)  # Subtract the NIR bleed over from the red channel
        return maxpixel, minpixel

    def calibrate_channel(self, channel, slope, intercept):
        return channel * slope + intercept

    def histogram_clip_channel(self, channel, global_clip_max):
        channel[channel > global_clip_max] = global_clip_max

    def histogram_clip_image(self, red, green, blue, global_HC_max):
        self.histogram_clip_channel(red, global_HC_max)
        self.histogram_clip_channel(green, global_HC_max)
        self.histogram_clip_channel(blue, global_HC_max)

    @staticmethod
    def convert_normalized_layer_to_bit_depth(layer, bit_depth):
        layer *= 2**bit_depth-1
        layer = layer.astype(int)
        dtype = 'uint' + str(bit_depth)
        layer = layer.astype(dtype)
        return layer

    def convert_normalized_image_to_bit_depth(self, bit_depth, red, green, blue, alpha=None):
        red = MAPIR_ProcessingDockWidget.convert_normalized_layer_to_bit_depth(red, bit_depth)
        green = MAPIR_ProcessingDockWidget.convert_normalized_layer_to_bit_depth(green, bit_depth)
        blue = MAPIR_ProcessingDockWidget.convert_normalized_layer_to_bit_depth(blue, bit_depth)

        if alpha is None:
            alpha = []
        if not alpha == []:
            alpha = MAPIR_ProcessingDockWidget.convert_normalized_layer_to_bit_depth(alpha, bit_depth)
            # MAPIR_ProcessingDockWidget.print_2d_list_frequencies(13228, alpha)

        return red, green, blue, alpha


    def geotiff_with_metadata_from_rgba(self, in_geotiff_path, image_data, out_geotiff_path):
        out_geotiff = Geotiff.create_geotiff(image_data, out_geotiff_path)
        out_geotiff.FlushCache()

        self.copyExif(in_geotiff_path, out_geotiff_path)

        projection, geo_transform, gcps, gcp_projection = Geotiff.get_geo_data(in_geotiff_path)
        Geotiff.set_geo_data(out_geotiff, projection, geo_transform, gcps, gcp_projection)

        bands = Geotiff.get_bands_from_image_data(image_data)
        nodata = -10000
        Geotiff.write_bands_to_geotiff(out_geotiff, bands, nodata)

        out_geotiff.FlushCache()
        out_geotiff = None

    # def save_geo_data_to_tiff(self, in_geotiff_path, calibrated_image_path):

    #     in_geotiff = gdal.Open(in_geotiff_path)
    #     projection = in_geotiff.GetProjection()
    #     geo_transform = in_geotiff.GetGeoTransform()
    #     GCPs = in_geotiff.GetGCPs()
    #     GCP_projection = in_geotiff.GetGCPProjection()

    #     calibrated_image = gdal.Open(calibrated_image_path, gdal.GA_Update)
    #     calibrated_image.SetGeoTransform(geo_transform)
    #     calibrated_image.SetProjection(projection)
    #     calibrated_image.SetGCPs(GCPs, GCP_projection)

    #     calibrated_image.FlushCache()

    #     in_geotiff = None
    #     calibrated_image = None

    def CalibrateMono(self, photo, coeff, output_directory, ind):
        try:
            refimg = cv2.imread(photo, -1)

            maxpixel = self.monominmax["max"]
            minpixel = self.monominmax["min"]

            refimg = ((refimg * coeff["slope"]) + coeff["intercept"])

            if self.histogramClipBox  == self.CHECKED:
                global_HC_max = self.HC_mono_max
                refimg[refimg > global_HC_max] = global_HC_max
                maxpixel = global_HC_max

            refimg = ((refimg - minpixel) / (maxpixel - minpixel))

            if self.IndexBox  == self.UNCHECKED:
            #Float to JPG
                if photo.split('.')[2].upper() == "JPG" or photo.split('.')[2].upper() == "JPEG" or self.Tiff2JpgBox  > 0:
                    refimg *= 255
                    refimg = refimg.astype(int)
                    refimg = refimg.astype("uint8")

                else: #Float to Tiff
                    refimg *= 65535
                    refimg = refimg.astype(int)
                    refimg = refimg.astype("uint16")

            else: #Float to Index
                refimg[refimg > 1.0] = 1.0
                refimg[refimg < 0.0] = 0.0
                refimg = refimg.astype("float")
                refimg = cv2.normalize(refimg.astype("float"), None, 0.0, 1.0, cv2.NORM_MINMAX)

            if self.Tiff2JpgBox > 0:
                self.CalibrationLog_append("Making JPG")
                #QtWidgets.QApplication.processEvents()
                cv2.imencode(".jpg", refimg)
                outpath = output_directory + photo.split('.')[1] + "_CALIBRATED.JPG"
                cv2.imwrite(outpath, refimg,
                            [int(cv2.IMWRITE_JPEG_QUALITY), 100])

                self.copyExif(photo, outpath)

            else:
                self.save_calibrated_image_without_conversion(photo, refimg, output_directory)

        except Exception as e:
            exc_type, exc_obj,exc_tb = sys.exc_info()
            print(e)
            print("Line: " + str(exc_tb.tb_lineno))


    @staticmethod
    def print_2d_list_frequencies(size, list):
        frequencies = collections.Counter([])
        for i in range(size):
            row = list[i]
            row_freqs = collections.Counter(row)
            frequencies += row_freqs
            # print('Row ' + str(i) + ': ' + str(row_freqs))
        print(frequencies)

    def CalibratePhotos(self, photo, coeffs, minmaxes, output_directory, ind):
        refimg = cv2.imread(photo, -1)

        camera_model = ind[0]
        filt = ind[1]
        lens = ind[2]

        ### split channels (using cv2.split caused too much overhead and made the host program crash)
        alpha = []
        has_alpha_layer = False
        blue = refimg[:, :, 0]
        green = refimg[:, :, 1]
        red = refimg[:, :, 2]

        if camera_model == "Survey2" and filt == "Red + NIR (NDVI)":
            red = refimg[:, :, 2] - (refimg[:, :, 0] * 0.80)

        if refimg.shape[2] == 4:
            alpha = refimg[:, :, 3]
            has_alpha_layer = True
            refimg = copy.deepcopy(refimg[:, :, :3])

        red = self.calibrate_channel(red, coeffs["red"]["slope"], coeffs["red"]["intercept"])
        green = self.calibrate_channel(green, coeffs["green"]["slope"], coeffs["green"]["intercept"])
        blue = self.calibrate_channel(blue, coeffs["blue"]["slope"], coeffs["blue"]["intercept"])

        maxpixel, minpixel = self.get_global_max_and_min_calibrated_pixel_values(camera_model, filt, minmaxes)


        ### Scale calibrated values back down to a useable range (Adding 1 to avoid 0 value pixels, as they will cause a
        #### divide by zero case when creating an index image

        if self.histogramClipBox  == self.CHECKED:
            global_HC_max = max([self.HC_max["bluemax"], self.HC_max["redmax"], self.HC_max["greenmax"]])
            self.histogram_clip_image(red, green, blue, global_HC_max)
            maxpixel = global_HC_max

        red, green, blue = normalize_rgb(red, green, blue, maxpixel, minpixel)

        if has_alpha_layer:
            original_alpha_depth = alpha.max() - alpha.min()
            alpha = alpha / original_alpha_depth

        # MAPIR_ProcessingDockWidget.print_2d_list_frequencies(13228, alpha)

        if self.IndexBox  == self.UNCHECKED:
            if refimg.dtype == 'uint8':
                # if 'tif' in photo.split('.')[-1].lower():
                #     # tiff = gdal.Open(photo, gdal.GA_ReadOnly)
                #     # tiff_has_projection_data = not tiff.GetProjection() == ''
                #     # self.CalibrationLog_append()('tiff: ' + str(tiff))
                #     # self.CalibrationLog_append()(str(gdal))
                #     # self.CalibrationLog_append()(gdal.__version__)
                #     # self.CalibrationLog_append()(gdal.VersionInfo())
                #     # self.CalibrationLog_append()('Projection: ' + str(tiff.GetProjection()))
                #     # self.CalibrationLog_append()('has_projection_data: ' + str(tiff_has_projection_data))
                #     # if tiff_has_projection_data:
                #     #     bit_depth = 16
                #     #     self.CalibrationLog_append()('tiff with projection data bd=16')
                #     else:
                #         bit_depth = 8
                #         self.CalibrationLog_append()('tiff without projection data bd=8')
                # else:
                    # bit_depth = 8
                bit_depth = 8
            elif refimg.dtype == 'uint16':
                bit_depth = 16
            else:
                raise Exception('Calibration input image should be 8-bit or 16-bit')

            red, green, blue, alpha = self.convert_normalized_image_to_bit_depth(bit_depth, red, green, blue, alpha)
            layers = (blue, green, red, alpha) if has_alpha_layer else (blue, green, red)
            refimg = cv2.merge(layers)

        else: #Float to Index
            red = red.astype("float32")
            green = green.astype("float32")
            blue = blue.astype("float32")

            #refimg = cv2.merge((blue, green, red))
            #refimg = cv2.normalize(refimg.astype("float32"), None, 0.0, 1.0, cv2.NORM_MINMAX)

        if self.Tiff2JpgBox  > 0:
            self.CalibrationLog_append("Making JPG")
            #QtWidgets.QApplication.processEvents()

            cv2.imencode(".jpg", refimg)
            cv2.imwrite(output_directory + photo.split('.')[1] + "_CALIBRATED.JPG", refimg,
                        [int(cv2.IMWRITE_JPEG_QUALITY), 100])

            self.copyExif(photo, output_directory + photo.split('.')[1] + "_CALIBRATED.JPG")

        else:
            if self.IndexBox :
                newimg_r = output_directory + photo.split('.')[1] + "_CALIBRATED_red." + photo.split('.')[2]
                newimg_b = output_directory + photo.split('.')[1] + "_CALIBRATED_blue." + photo.split('.')[2]
                newimg_g = output_directory + photo.split('.')[1] + "_CALIBRATED_green." + photo.split('.')[2]

                cv2.imencode(".tif", red)
                cv2.imencode(".tif", green)
                cv2.imencode(".tif", blue)

                cv2.imwrite(newimg_r, red)
                cv2.imwrite(newimg_b, blue)
                cv2.imwrite(newimg_g, green)

                # srin = gdal.Open(photo)
                # inproj = srin.GetProjection()
                # transform = srin.GetGeoTransform()
                # gcpcount = srin.GetGCPs()

                # srout = gdal.Open(newimg_r, gdal.GA_Update)
                # srout = gdal.Open(newimg_g, gdal.GA_Update)
                # srout = gdal.Open(newimg_b, gdal.GA_Update)

                # srout.SetProjection(inproj)
                # srout.SetGeoTransform(transform)
                # srout.SetGCPs(gcpcount, srin.GetGCPProjection())
                # srout = None
                # srin = None

                self.copyExif(photo, newimg_r)
                self.copyExif(photo, newimg_g)
                self.copyExif(photo, newimg_b)

            else:
                self.save_calibrated_image_without_conversion(photo, refimg, output_directory)


    def copyExif(self, inphoto, outphoto):
        subprocess._cleanup()
        if sys.platform == "win32":
            print('Using: {0}'.format(modpath + os.sep +r'exiftool.exe'))
            exiftool_exe = modpath + os.sep +r'exiftool.exe'
        else:
            exiftool_exe = r'exiftool'
        try:
            data = subprocess.run(
                args=[exiftool_exe, '-m', r'-UserComment', r'-ifd0:imagewidth', r'-ifd0:imageheight',
                      os.path.abspath(inphoto)],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                stdin=subprocess.PIPE, startupinfo=si).stdout.decode("utf-8")

            data = [line.strip().split(':') for line in data.split('\r\n') if line.strip()]

            # parse yaw pitch roll from metadata
            ypr = data[0][1].split()
            # ypr = [0.0] * 3

            # ypr[0] = abs(float(ypr[0]) % 360.0) #Yaw
            # ypr[1] = abs((float(ypr[1]) + 180.0) % 360.0) #Pitch
            # ypr[2] = abs((float(-ypr[2])) % 360.0) #Roll


            w = int(data[1][1])
            h = int(data[2][1])
            model = self.findCameraModel(w * h)
            centralwavelength = self.lensvals[3:6][1]
            bandname = self.lensvals[3:6][0]

            fnumber = self.lensvals[0][1]
            focallength = self.lensvals[0][0]
            lensmodel = self.lensvals[0][0] + "mm"

            # centralwavelength = inphoto.split(os.sep)[-1][1:4]
            if '' not in bandname:

                if sys.platform == "win32":
                    print('Using: {0}'.format(modpath + os.sep + r'exiftool.exe'))
                    exiftool_exe = modpath + os.sep + r'exiftool.exe'
                else:
                    exiftool_exe = r'exiftool'

                exifout = subprocess.run(
                    [ exiftool_exe, r'-config', modpath + os.sep + r'mapir.config', '-m',
                     r'-overwrite_original', r'-tagsFromFile',
                     os.path.abspath(inphoto),
                     r'-all:all<all:all',
                     r'-ifd0:make=MAPIR',
                     r'-Model=' + model,
                     #r'-ifd0:blacklevelrepeatdim=' + str(1) + " " + str(1),
                     #r'-ifd0:blacklevel=0',
                     r'-bandname=' + str(bandname[0] + ', ' + bandname[1] + ', ' + bandname[2]),
                     # r'-bandname2=' + str( r'F' + str(self.BandNames.get(bandname, [0, 0, 0])[1])),
                     # r'-bandname3=' + str( r'F' + str(self.BandNames.get(bandname, [0, 0, 0])[2])),
                     r'-WavelengthFWHM=' + str( self.lensvals[3:6][0][2] + ', ' + self.lensvals[3:6][1][2] + ', ' + self.lensvals[3:6][2][2]) ,
                     r'-ModelType=perspective',
                     r'-Yaw=' + str(ypr[0]),
                     r'-Pitch=' + str(ypr[1]),
                     r'-Roll=' + str(ypr[2]),
                     r'-CentralWavelength=' + str(float(centralwavelength[0])) + ', ' + str(float(centralwavelength[1])) + ', ' + str(float(centralwavelength[2])),
                     r'-Lens=' + lensmodel,
                     r'-FocalLength=' + focallength,
                     r'-fnumber=' + fnumber,
                     r'-FocalPlaneXResolution=' + str(6.14),
                     r'-FocalPlaneYResolution=' + str(4.60),
                     os.path.abspath(outphoto)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE,
                    startupinfo=si).stderr.decode("utf-8")
            else:
                if bandname[0].isdigit():
                    bandname[0] = r'F' + bandname[0]
                if bandname[1].isdigit():
                    bandname[1] = r'F' + bandname[1]
                if bandname[2].isdigit():
                    bandname[2] = r'F' + bandname[2]
                if sys.platform == "win32":
                    print('Using: {0}'.format(modpath + os.sep + r'exiftool.exe'))
                    exiftool_exe = modpath + os.sep + r'exiftool.exe'
                else:
                    exiftool_exe = r'exiftool'
                exifout = subprocess.run(
                    [ exiftool_exe, r'-config', modpath + os.sep + r'mapir.config', '-m',
                     r'-overwrite_original', r'-tagsFromFile',
                     os.path.abspath(inphoto),
                     r'-all:all<all:all',
                     r'-ifd0:make=MAPIR',
                     r'-Model=' + model,
                     #r'-ifd0:blacklevelrepeatdim=' + str(1) + " " + str(1),
                     #r'-ifd0:blacklevel=0',
                     r'-bandname=' + str( bandname[0]),
                     r'-ModelType=perspective',
                     r'-WavelengthFWHM=' + str(self.lensvals[3:6][0][2]),
                     r'-Yaw=' + str(ypr[0]),
                     r'-Pitch=' + str(ypr[1]),
                     r'-Roll=' + str(ypr[2]),
                     r'-CentralWavelength=' + str(float(centralwavelength[0])),
                     r'-Lens=' + lensmodel,
                     r'-FocalLength=' + focallength,
                     r'-fnumber=' + fnumber,
                     r'-FocalPlaneXResolution=' + str(6.14),
                     r'-FocalPlaneYResolution=' + str(4.60),
                     os.path.abspath(outphoto)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE,
                    startupinfo=si).stderr.decode("utf-8")
        except Exception as e:
            if sys.platform == "win32":
                print('Using: {0}'.format(modpath + os.sep + r'exiftool.exe'))
                exiftool_exe = modpath + os.sep + r'exiftool.exe'
            else:
                exiftool_exe = r'exiftool'
            exifout = subprocess.run(
                [ exiftool_exe, #r'-config', modpath + os.sep + r'mapir.config',
                 r'-overwrite_original_in_place', r'-tagsFromFile',
                 os.path.abspath(inphoto),
                 r'-all:all<all:all',
                 os.path.abspath(outphoto)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE,
                startupinfo=si).stderr.decode("utf-8")
            print(exifout)

    def copySimple(self, inphoto, outphoto):
        ExifUtils.copy_simple(inphoto, outphoto, si)

    def copyMAPIR(self, inphoto, outphoto):
        if sys.platform == "win32":
            # with exiftool.ExifTool() as et:
            #     et.execute(r' -overwrite_original -tagsFromFile ' + os.path.abspath(inphoto) + ' ' + os.path.abspath(outphoto))

            try:
                # self.PreProcessLog.append(str(modpath + os.sep + r'exiftool.exe') + ' ' + inphoto + ' ' + outphoto)
                subprocess._cleanup()
                if sys.platform == "win32":
                    print('Using: {0}'.format(modpath + os.sep + r'exiftool.exe'))
                    exiftool_exe = modpath + os.sep + r'exiftool.exe'
                else:
                    exiftool_exe = r'exiftool'

                data = subprocess.run(
                    args=[ exiftool_exe, '-m', r'-ifd0:imagewidth', r'-ifd0:imageheight', os.path.abspath(inphoto)],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                    stdin=subprocess.PIPE, startupinfo=si).stdout.decode("utf-8")

                data = [line.strip().split(':') for line in data.split('\r\n') if line.strip()]
                #ypr = data[0][1].split()
                #
                ypr = [0.0] * 3

                ypr[0] = float(self.conv.META_PAYLOAD["ATT_Q0"][1])
                ypr[1] = float(self.conv.META_PAYLOAD["ATT_Q1"][1])
                ypr[2] = float(self.conv.META_PAYLOAD["ATT_Q2"][1])

                self.conv.META_PAYLOAD["ARRAY_ID"][1] = self.conv.STD_PAYLOAD["LINK_ID"]
                #ypr = {"yaw": 0, "pitch": 0, "roll": 0}

                if self.conv.META_PAYLOAD["ARRAY_TYPE"][1] != 0:
                    ypr = AdjustYPR(int(self.conv.META_PAYLOAD["ARRAY_TYPE"][1]), int(self.conv.META_PAYLOAD["ARRAY_ID"][1]),ypr)
                    ypr = CurveAdjustment(int(self.conv.META_PAYLOAD["ARRAY_TYPE"][1]), int(self.conv.META_PAYLOAD["ARRAY_ID"][1]),ypr)

                w = int(data[0][1])
                h = int(data[1][1])
                model = self.findCameraModel(w * h)
                centralwavelength = [self.lensvals[3:6][0][1], self.lensvals[3:6][1][1], self.lensvals[3:6][2][1]]
                bandname = [self.lensvals[3:6][0][0], self.lensvals[3:6][1][0], self.lensvals[3:6][2][0]]

                fnumber = self.lensvals[0][1]
                focallength = self.lensvals[0][0]

                lensmodel = self.lensvals[0][0] + "mm"
                pixels_per_unit = "289855/1000" if model == "Kernel 3.2MP" else "714286/1000"

                principal_point = self.PIX4D_VALUES[focallength]["PRINCIPALPOINT"]
                perspective_focal_length = self.PIX4D_VALUES[focallength]["PERSPECTIVEFOCALLENGTH"]
                perspective_distortion = self.PIX4D_VALUES[focallength]["PERSPECTIVEDISTORTION"]

            except Exception as e:
                exc_type, exc_obj,exc_tb = sys.exc_info()
                ypr = None
                print(e)
                print("Line: " + str(exc_tb.tb_lineno))
                print("Warning: No userdefined tags detected")

                # subprocess.call(
                #     [modpath + os.sep + r'exiftool.exe', '-m', r'-overwrite_original', r'-tagsFromFile',
                #      os.path.abspath(inphoto),
                #      # r'-all:all<all:all',
                #      os.path.abspath(outphoto)], startupinfo=si)
            finally:
                if ypr is not None:
                    try:
                        dto = datetime.fromtimestamp(self.conv.META_PAYLOAD["TIME_SECS"][1])
                        m, s = divmod(self.conv.META_PAYLOAD["GNSS_TIME_SECS"][1], 60)
                        h, m = divmod(m, 60)

                        # dd, h = divmod(h, 24)

                        if self.PreProcessVignette.isChecked():
                            fil_str = self.PreProcessFilter.currentText()
                            # if "/" in self.PreProcessFilter.currentText():
                            #     fil_names = self.PreProcessFilter.currentText().split("/")
                            #     fil_str = fil_names[0] + "-" + fil_names[1] + "-" + fil_names[2]
                            DFV = self.get_dark_frame_value(fil_str)
                        else:
                            DFV = None

                        altref = 0 if self.conv.META_PAYLOAD["GNSS_HEIGHT_SEA_LEVEL"][1] >= 0 else 1
                        if '' not in bandname:
                            if sys.platform == "win32":
                                exiftool_exe = modpath + os.sep +  r'exiftool.exe'
                            else:
                                exiftool_exe = r'exiftool'
                            exifout = subprocess.run(
                                [exiftool_exe,  r'-config', modpath + os.sep + r'mapir.config', '-m', r'-overwrite_original', r'-tagsFromFile',
                                 os.path.abspath(inphoto),
                                 r'-all:all<all:all',
                                 r'-ifd0:make=MAPIR',
                                 r'-Model=' + model,
                                 #r'-ifd0:blacklevelrepeatdim=' + str(1) + " " + str(1),
                                 #r'-ifd0:blacklevel=0',
                                 r'-ModelType=perspective',
                                 r'-BlackCurrent=' + str(DFV),
                                 r'-BlackCurrent=' + str(DFV),
                                 r'-BlackCurrent=' + str(DFV),
                                 r'-Yaw=' + str(ypr[0]),
                                 r'-Pitch=' + str(ypr[1]),
                                 r'-Roll=' + str(ypr[2]),
                                 r'-CentralWavelength=' + str(float(centralwavelength[0])),
                                 r'-CentralWavelength=' + str(float(centralwavelength[1])),
                                 r'-CentralWavelength=' + str(float(centralwavelength[2])),
                                 r'-bandname=' + bandname[0],
                                 r'-bandname=' + bandname[1],
                                 r'-bandname=' + bandname[2],
                                 r'-PrincipalPoint=' + principal_point,
                                 r'-PerspectiveFocalLength=' + perspective_focal_length,
                                 r'-PerspectiveDistortion=' + perspective_distortion,
                                 r'-WavelengthFWHM=' + self.lensvals[3:6][0][2],
                                 r'-WavelengthFWHM=' + self.lensvals[3:6][1][2],
                                 r'-WavelengthFWHM=' + self.lensvals[3:6][2][2],

                                 r'-GPSLatitude="' + str(self.conv.META_PAYLOAD["GNSS_LAT_HI"][1]) + r'"',

                                 r'-GPSLongitude="' + str(self.conv.META_PAYLOAD["GNSS_LON_HI"][1]) + r'"',
                                 r'-GPSTimeStamp="{hour=' + str(h) + r',minute=' + str(m) + r',second=' + str(s) + r'}"',
                                 r'-GPSAltitude=' + str(self.conv.META_PAYLOAD["GNSS_HEIGHT_SEA_LEVEL"][1]),
                                 # r'-GPSAltitudeE=' + str(self.conv.META_PAYLOAD["GNSS_HEIGHT_ELIPSOID"][1]),
                                 r'-GPSAltitudeRef#=' + str(altref),
                                 r'-GPSTimeStampS=' + str(self.conv.META_PAYLOAD["GNSS_TIME_NSECS"][1]),
                                 r'-GPSLatitudeRef=' + self.conv.META_PAYLOAD["GNSS_VELOCITY_N"][1],
                                 r'-GPSLongitudeRef=' + self.conv.META_PAYLOAD["GNSS_VELOCITY_E"][1],
                                 r'-GPSLeapSeconds=' + str(self.conv.META_PAYLOAD["GNSS_LEAP_SECONDS"][1]),
                                 r'-GPSTimeFormat=' + str(self.conv.META_PAYLOAD["GNSS_TIME_FORMAT"][1]),
                                 r'-GPSFixStatus=' + str(self.conv.META_PAYLOAD["GNSS_FIX_STATUS"][1]),
                                 r'-DateTimeOriginal=' + dto.strftime("%Y:%m:%d %H:%M:%S"),
                                 r'-SubSecTimeOriginal=' + str(self.conv.META_PAYLOAD["TIME_NSECS"][1]),
                                 r'-ExposureTime=' + str(self.conv.META_PAYLOAD["EXP_TIME"][1]),
                                 r'-ExposureMode#=' + str(self.conv.META_PAYLOAD["EXP_MODE"][1]),
                                 r'-ISO=' + str(self.conv.META_PAYLOAD["ISO_SPEED"][1]),
                                 r'-Lens=' + lensmodel,
                                 r'-FocalLength=' + focallength,
                                 r'-fnumber=' + fnumber,
                                 r'-ArrayID=' + str(self.conv.META_PAYLOAD["ARRAY_ID"][1]),
                                 r'-ArrayType=' + str(self.conv.META_PAYLOAD["ARRAY_TYPE"][1]), #add rig name and rig index
                                 r'-FocalPlaneXResolution#=' + pixels_per_unit,
                                 r'-FocalPlaneYResolution#=' + pixels_per_unit,
                                 r'-FocalPlaneResolutionUnit#=' + '4',
                                 os.path.abspath(outphoto)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, startupinfo=si).stderr.decode("utf-8")
                        else:

                            bandname = [band for band in bandname if band]
                            CWL = [cwl for cwl in centralwavelength if cwl]

                            if sys.platform == "win32":
                                exiftool_exe = modpath + os.sep + r'exiftool.exe'
                            else:
                                exiftool_exe = r'exiftool'

                            exifout = subprocess.run(
                                [ exiftool_exe , r'-config', modpath + os.sep + r'mapir.config',
                                 '-m', r'-overwrite_original', r'-tagsFromFile',
                                 os.path.abspath(inphoto),
                                 r'-all:all<all:all',
                                 r'-ifd0:make=MAPIR',
                                 r'-Model=' + model,
                                 r'-ModelType=perspective',
                                 r'-BlackCurrent=' + str(DFV),
                                 r'-Yaw=' + str(ypr[0]),
                                 r'-Pitch=' + str(ypr[1]),
                                 r'-Roll=' + str(ypr[2]),
                                 r'-CentralWavelength=' + str(CWL[0] if CWL[0] == "" else float(CWL[0])),
                                 #r'-ifd0:blacklevelrepeatdim=' + str(1) + " " +  str(1),
                                 #r'-ifd0:blacklevel=0',
                                 # r'-BandName="{band1=' + str(self.BandNames[bandname][0]) + r'band2=' + str(self.BandNames[bandname][1]) + r'band3=' + str(self.BandNames[bandname][2]) + r'}"',
                                 r'-bandname=' + bandname[0],
                                 r'-PrincipalPoint=' + principal_point,
                                 r'-PerspectiveFocalLength=' + perspective_focal_length,
                                 r'-PerspectiveDistortion=' + perspective_distortion,
                                 r'-WavelengthFWHM=' + str(self.lensvals[3:6][0][2]),
                                 r'-GPSLatitude="' + str(self.conv.META_PAYLOAD["GNSS_LAT_HI"][1]) + r'"',

                                 r'-GPSLongitude="' + str(self.conv.META_PAYLOAD["GNSS_LON_HI"][1]) + r'"',
                                 r'-GPSTimeStamp="{hour=' + str(h) + r',minute=' + str(m) + r',second=' + str(
                                     s) + r'}"',
                                 r'-GPSAltitude=' + str(self.conv.META_PAYLOAD["GNSS_HEIGHT_SEA_LEVEL"][1]),
                                 # r'-GPSAltitudeE=' + str(self.conv.META_PAYLOAD["GNSS_HEIGHT_ELIPSOID"][1]),
                                 r'-GPSAltitudeRef#=' + str(altref),
                                 r'-GPSTimeStampS=' + str(self.conv.META_PAYLOAD["GNSS_TIME_NSECS"][1]),
                                 r'-GPSLatitudeRef=' + self.conv.META_PAYLOAD["GNSS_VELOCITY_N"][1],
                                 r'-GPSLongitudeRef=' + self.conv.META_PAYLOAD["GNSS_VELOCITY_E"][1],
                                 r'-GPSLeapSeconds=' + str(self.conv.META_PAYLOAD["GNSS_LEAP_SECONDS"][1]),
                                 r'-GPSTimeFormat=' + str(self.conv.META_PAYLOAD["GNSS_TIME_FORMAT"][1]),
                                 r'-GPSFixStatus=' + str(self.conv.META_PAYLOAD["GNSS_FIX_STATUS"][1]),
                                 r'-DateTimeOriginal=' + dto.strftime("%Y:%m:%d %H:%M:%S"),
                                 r'-SubSecTimeOriginal=' + str(self.conv.META_PAYLOAD["TIME_NSECS"][1]),
                                 r'-ExposureTime=' + str(self.conv.META_PAYLOAD["EXP_TIME"][1]),
                                 r'-ExposureMode#=' + str(self.conv.META_PAYLOAD["EXP_MODE"][1]),
                                 r'-ISO=' + str(self.conv.META_PAYLOAD["ISO_SPEED"][1]),
                                 r'-Lens=' + lensmodel,
                                 r'-FocalLength=' + focallength,
                                 r'-fnumber=' + fnumber,
                                 r'-ArrayID=' + str(self.conv.META_PAYLOAD["ARRAY_ID"][1]),
                                 r'-ArrayType=' + str(self.conv.META_PAYLOAD["ARRAY_TYPE"][1]),
                                 r'-FocalPlaneXResolution=' + pixels_per_unit,
                                 r'-FocalPlaneYResolution=' + pixels_per_unit,
                                 r'-FocalPlaneResolutionUnit#=' + '4',
                                 os.path.abspath(outphoto)], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                stdin=subprocess.PIPE, startupinfo=si).stderr.decode("utf-8")
                        print(exifout)

                    except Exception as e:
                        exc_type, exc_obj,exc_tb = sys.exc_info()
                        if self.MapirTab.currentIndex() == 0:
                            self.PreProcessLog.append("Error: " + str(e) + ' Line: ' + str(exc_tb.tb_lineno))
                        elif self.MapirTab.currentIndex() == 1:
                            self.CalibrationLog_append("Error: " + str(e))
                else:
                    if sys.platform == "win32":
                        exiftool_exe = modpath + os.sep + r'exiftool.exe'
                    else:
                        exiftool_exe = r'exiftool'
                    # self.PreProcessLog.append("No IMU data detected.")
                    subprocess.call(
                        [exiftool_exe, '-m', r'-overwrite_original', r'-tagsFromFile',
                         os.path.abspath(inphoto),
                         # r'-all:all<all:all',
                         os.path.abspath(outphoto)], startupinfo=si)
        else:
            if sys.platform == "win32":
                exiftool_exe = r'exiftool.exe'
            else:
                exiftool_exe = r'exiftool'
            subprocess.call(
                [exiftool_exe, r'-overwrite_original', r'-addTagsFromFile', os.path.abspath(inphoto),
                 # r'-all:all<all:all',
                 os.path.abspath(outphoto)])

