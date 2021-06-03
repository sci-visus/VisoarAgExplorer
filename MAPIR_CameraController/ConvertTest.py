

import os

import numpy as np
import cv2
import struct
infile = r'E:\New Firmware 12bit TEST\2017_0101_002615_001.RAW'
with open(infile, "rb") as rawimage:
    rawimage.seek(0)
    data = struct.unpack("=" + str(int(os.stat(infile).st_size / 4)) + "I",
                         rawimage.read(os.stat(infile).st_size))
