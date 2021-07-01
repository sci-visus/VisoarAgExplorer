# File: MAPIR_Converter.py
#
# Class: Converter
#
# Creator: Ethan Hall, in association with Peau Productions/MAPIR
#
# Purpose: To convert custom raw files
#########################################################################






import os

import numpy as np
import cv2
from  LensLookups import *
import struct

from fractions import Fraction

os.umask(0)




EXP_LOOKPUP = ["0", "1/32000", "1/16000", "1/8000",
                                 "1/6000", "1/4000",
                                 "1/2000", "1/1600",  "1/1250", "1/1000",
            					 "1/800", "1/640", "1/500", "1/400", "1/320",
            					 "1/250", "1/200", "1/160", "1/125", "1/100",
            					 "1/80", "1/60", "1/50", "1/40", "1/30",
            					 "1/25", "1/20", "1/15", "1/12", "1/10",
            					 "1/8", "1/6.4", "1/5", "1/4", "1/3.2",
            					 "1/2.5", "1/2", "1/1" ]
class Converter:
    rawimage = None
    STD_PAYLOAD = {  # Dictionary for storing the Standard information of a .mapir format image.
        "CAM_ID": 0x0001,
        "DUMMY": 0x0000,
        "CAM_SN": 0x000000,
        "LINK_ID": 0x00,
        "FW_VER": 0x0103,
        "FMT_VER": 0x103
    }

    SENS_PAYLOAD = {  # Dictionary for storing the Sensor information of a .mapir format image.
        "SENS_ID": 0x0000,
        "FW_VER": 0x0000,
        "SENS_SN": 0x123456,
        "COL_TYPE": 0x00,
        "COL_BITS": 0x0,
        "TOTAL_HORZ_RES": 0x0,
        "STRIPE": 0x0,
        "TOTAL_VERT_RES": 0x0,
        "ACTIVE_HORZ_RES": 0x0,
        "ACTIVE_VERT_RES": 0x0,
        "ACTIVE_HORZ_OFF": 0x0,
        "ACTIVE_VERT_OFF": 0x0,
        "FILLER": 0x00,
        "EXT_CHKS": 0x00
    }

    META_PAYLOAD = {  # Dictionary for storing the metadata tags of a .mapir format image.
        "EXP_TIME": [1, 0],
        "EXP_MODE": [2, 0],
        "LENS": [3, 0],
        "TIME_SECS": [4, 0],
        "TIME_NSECS": [5, 0],
        "TRIGGER_DELAY_NSECS": [6, 0],
        "ISO_SPEED": [7, 0],
        "FILTER_ID": [8, 0],
        "ARRAY_ID": [9, 0],
        "ARRAY_TYPE": [10, 0],
        "ATT_Q0": [256, 0.0],
        "ATT_Q1": [257, 0.0],
        "ATT_Q2": [258, 0.0],
        "ATT_Q3": [259, 0.0],
        "GNSS_TIME_SECS": [512, 0],
        "GNSS_TIME_NSECS": [513, 0],
        "GNSS_LON_HI": [514, 0.0],
        "GNSS_LON_LO": [515, 0.0],
        "GNSS_LAT_HI": [516, 0.0],
        "GNSS_LAT_LO": [517, 0.0],
        "GNSS_HEIGHT_ELIPSOID": [518, 0.0],
        "GNSS_HEIGHT_SEA_LEVEL": [519, 0.0],
        "GNSS_VELOCITY_N": [520, 0.0],
        "GNSS_VELOCITY_E": [521, 0.0],
        "GNSS_VELOCITY_DOWN": [522, 0.0],
        "GNSS_PDOP": [528, 0.0],
        "GNSS_TIME_FORMAT": [531, 0],
        "GNSS_LEAP_SECONDS": [532, 0],
        "GNSS_FIX_STATUS": [533, 0]

    }

    ######################## __init__ #################################
    # Entrance: Creation of Converter class                          #
    # Process: Initial setup of Variables in Converter class         #
    # Exit: All variables that need initialising will be initialised #
    ##################################################################
    def __init__(self):
        self.STD_PAYLOAD = {  # Dictionary for storing the Standard information of a .mapir format image.
        "CAM_ID": 0x0001,
        "DUMMY": 0x0000,
        "CAM_SN": 0x000000,
        "LINK_ID": 0x00,
        "FW_VER": 0x0103,
        "FMT_VER": 0x103
        }

        self.SENS_PAYLOAD = {  # Dictionary for storing the Sensor information of a .mapir format image.
        "SENS_ID": 0x0000,
        "FW_VER": 0x0000,
        "SENS_SN": 0x123456,
        "COL_TYPE": 0x00,
        "COL_BITS": 0x0,
        "TOTAL_HORZ_RES": 0x0,
        "STRIPE": 0x0,
        "TOTAL_VERT_RES": 0x0,
        "ACTIVE_HORZ_RES": 0x0,
        "ACTIVE_VERT_RES": 0x0,
        "ACTIVE_HORZ_OFF": 0x0,
        "ACTIVE_VERT_OFF": 0x0,
        "FILLER": 0x00,
        "EXT_CHKS": 0x00
        }

        self.META_PAYLOAD = {  # Dictionary for storing the metadata tags of a .mapir format image.
        "EXP_TIME": [1, 0],
        "EXP_MODE": [2, 0],
        "LENS": [3, 0],
        "TIME_SECS": [4, 0],
        "TIME_NSECS": [5, 0],
        "TRIGGER_DELAY_NSECS": [6, 0],
        "ISO_SPEED": [7, 0],
        "FILTER_ID": [8, 0],
        "ARRAY_ID": [9, 0],
        "ARRAY_TYPE": [10, 0],
        "ATT_Q0": [256, 0.0],
        "ATT_Q1": [257, 0.0],
        "ATT_Q2": [258, 0.0],
        "ATT_Q3": [259, 0.0],
        "GNSS_TIME_SECS": [512, 0],
        "GNSS_TIME_NSECS": [513, 0],
        "GNSS_LON_HI": [514, 0.0],
        "GNSS_LON_LO": [515, 0.0],
        "GNSS_LAT_HI": [516, 0.0],
        "GNSS_LAT_LO": [517, 0.0],
        "GNSS_HEIGHT_ELIPSOID": [518, 0.0],
        "GNSS_HEIGHT_SEA_LEVEL": [519, 0.0],
        "GNSS_VELOCITY_N": [520, 0.0],
        "GNSS_VELOCITY_E": [521, 0.0],
        "GNSS_VELOCITY_DOWN": [522, 0.0],
        "GNSS_PDOP": [528, 0.0],
        "GNSS_TIME_FORMAT": [531, 0],
        "GNSS_LEAP_SECONDS": [532, 0],
        "GNSS_FIX_STATUS": [533, 0]

        }
        """Constructor."""

    ######################## openRaw #################################
    # Entrance: The data will be in a .mapir raw format              #
    # Process: Read raw data into variables and arrange for writing  #
    # Exit: Data will be stored in variables in a write ready format #
    ##################################################################
    def openRaw(self, mapirin, mapirout, darkscale=False):
        with open(mapirin, "rb") as self.rawimage:

            self.rawimage.seek(0)
            data = struct.unpack("=" + str(int(os.stat(mapirin).st_size / 4)) + "I",
                                 self.rawimage.read(os.stat(mapirin).st_size))
            # print(len(data))
            # print(data[0:4])
            # print(data[4:8])
            roughimg = data[8:int(data[1] / 4)]
            k = []

            # TODO figure out a way to iterate over every 3 items in the list in order to rearrange them properly
            for i in range(0, len(roughimg), 3):
                j = struct.pack("=I", roughimg[i])
                p = struct.pack("=I", roughimg[i + 1])
                q = struct.pack("=I", roughimg[i + 2])
                # nibble0 = j[1] >> 4
                # nibble1 = j[1] & 15
                # nibble2 = j[0] >> 4
                # nibble3 = j[0] & 15
                # nibble4 = j[3] >> 4
                # nibble5 = j[3] & 15
                # nibble6 = j[2] >> 4
                # nibble7 = j[2] & 15
                # nibble8 = p[1] >> 4
                # nibble9 = p[1] & 15
                # nibble10 = p[0] >> 4
                # nibble11 = p[0] & 15
                # nibble12 = p[3] >> 4
                # nibble13 = p[3] & 15
                # nibble14 = p[2] >> 4
                # nibble15 = p[2] & 15
                # nibble16 = q[1] >> 4
                # nibble17 = q[1] & 15
                # nibble18 = q[0] >> 4
                # nibble19 = q[0] & 15
                # nibble20 = q[3] >> 4
                # nibble21 = q[3] & 15
                # nibble22 = q[2] >> 4
                # nibble23 = q[2] & 15

                if darkscale:
                    k.append(0 | (j[1] << 4) | (j[0] >> 4))

                    k.append(((j[0] & 0x0F) << 8) | (j[3]))

                    k.append(0 | (j[2] << 4) | (p[1] >> 4))

                    k.append(((p[1] & 0x0F) << 8) | (p[0]))

                    k.append(0 | (p[3] << 4) | (p[2] >> 4))

                    k.append(((p[2] & 0x0F) << 8) | (q[1]))

                    k.append(0 | (q[0] << 4) | (q[3] >> 4))

                    k.append(((q[3] & 0x0F) << 8) | (q[2]))
                else:
                    k.append((j[1] << 8) | (j[0] & 0xF0))

                    k.append((j[0] << 12) | (j[3] << 4))

                    k.append((j[2] << 8) | (p[1] & 0xF0))

                    k.append((p[1] << 12) | (p[0] << 4))

                    k.append((p[3] << 8) | (p[2] & 0xF0))

                    k.append((p[2] << 12) | (q[1] << 4))

                    k.append((q[0] << 8) | (q[3] & 0xF0))

                    k.append((q[3] << 12) | (q[2] << 4))

                    # k.append((nibble3 << 12) | (nibble4 << 8) | (nibble5 << 4) | 0)
                    #
                    # k.append((nibble6 << 12) | (nibble7 << 8) | (nibble8 << 4) | 0)
                    #
                    # k.append((nibble9 << 12) | (nibble10 << 8) | (nibble11 << 4) | 0)
                    #
                    # k.append((nibble12 << 12) | (nibble13 << 8) | (nibble14 << 4) | 0)
                    #
                    # k.append((nibble15 << 12) | (nibble16 << 8) | (nibble17 << 4) | 0)
                    #
                    # k.append((nibble18 << 12) | (nibble19 << 8) | (nibble20 << 4) | 0)
                    #
                    # k.append((nibble21 << 12) | (nibble22 << 8) | (nibble23 << 4) | 0)

            k = np.array(k)
            h = int(np.sqrt(k.shape[0] / (4 / 3)))
            w = int(h * (4 / 3))
            try:
                k = np.reshape(k, (h, w)).astype("uint16")
            except:
                h = int(np.sqrt(k.shape[0] / (4)))
                w = int(h * (4 / 3))
                k = np.reshape(k, (h, w), 3).astype("uint16")
            # if len(k.shape) > 2:
            #     rk = k[:, [2,1,0]]
            #     cv2.imwrite(mapirout, rk)
            # else:
            cv2.imwrite(mapirout, k)
            # print(data[int(data[1] / 4)])
            # print(data[int(data[1] / 4) + 1])
            std_vals = []
            for i in range(int(data[1] / 4) + 2, int(data[2] / 4), 1):
                std_vals.append(data[i])
            self._storeSTD_Payload(std_vals)
            # print(data[int(data[2] / 4)])
            sens_vals = []
            for i in range(int(data[2] / 4) + 2, int(data[3] / 4), 1):
                sens_vals.append(data[i])
            self._storeSENS_Payload(sens_vals)
            # print(data[int(data[3] / 4)])
            meta_vals = []
            meta_len = (data[int(data[3] / 4) + 2]) * 2
            meta_st = (int(data[3] / 4) + 8)
            for i in range(meta_st, meta_st + meta_len, 2):
                # print(data[i])
                # print(data[i + 1])
                meta_vals.append([data[i], data[i + 1]])
            meta_vals.sort()
            # self.META_PAYLOAD = sorted(self.META_PAYLOAD.iteritems())

            # self.META_PAYLOAD = collections.OrderedDict(self.META_PAYLOAD)
            lensval = self._storeMETA_Payload(meta_vals)
#             # print(data[2])
            return self.STD_PAYLOAD, self.SENS_PAYLOAD, self.META_PAYLOAD, lensval

    ######################## unpackSTD_Payload ############################
    # Entrance: STD_PAYLOAD will be read by openMapir function            #
    # Process: Store data in the STD_Payload Dictionary                   #
    # Exit: Data will be stored in STD_Payload Dictionary                 #
    #######################################################################
    def _storeSTD_Payload(self, payload):

        self.STD_PAYLOAD["CAM_ID"] = payload[0]
        self.STD_PAYLOAD["DUMMY"] = payload[1]
        self.STD_PAYLOAD["CAM_SN"] = payload[2]
        self.STD_PAYLOAD["LINK_ID"] = payload[3]
        self.STD_PAYLOAD["FW_VER"] = payload[4]
        self.STD_PAYLOAD["FMT_VER"] = payload[5]

    # TODO: finish setup of unpacking all payloads
    ######################## unpackSTD_Payload ############################
    # Entrance: SENS_PAYLOAD will be read by openMapir function           #
    # Process: Store data in the SENS_Payload Dictionary                  #
    # Exit: Data will be stored in SENS_Payload Dictionary                #
    #######################################################################
    def _storeSENS_Payload(self, payload):
        self.SENS_PAYLOAD["SENS_ID"] = payload[0]
        self.SENS_PAYLOAD["FW_VER"] = payload[1]
        self.SENS_PAYLOAD["SENS_SN"] = payload[2]
        self.SENS_PAYLOAD["COL_TYPE"] = payload[3]
        self.SENS_PAYLOAD["COL_BITS"] = payload[4]
        self.SENS_PAYLOAD["TOTAL_HORZ_RES"] = payload[5]
        self.SENS_PAYLOAD["STRIPE"] = payload[6]
        self.SENS_PAYLOAD["TOTAL_VERT_RES"] = payload[7]
        self.SENS_PAYLOAD["ACTIVE_HORZ_RES"] = payload[8]
        self.SENS_PAYLOAD["ACTIVE_VERT_RES"] = payload[9]
        self.SENS_PAYLOAD["ACTIVE_HORZ_OFF"] = payload[10]
        self.SENS_PAYLOAD["ACTIVE_VERT_OFF"] = payload[11]
        self.SENS_PAYLOAD["FILLER"] = payload[12]
        self.SENS_PAYLOAD["EXT_CHKS"] = payload[13]

    ######################## unpackSTD_Payload ############################
    # Entrance: META_PAYLOAD will be read by openMapir function           #
    # Process: Store data in the META_Payload Dictionary                  #
    # Exit: Data will be stored in META_Payload Dictionary                #
    #######################################################################
    def _storeMETA_Payload(self, payload):
        for item in payload:
            for key in self.META_PAYLOAD.keys():
                if item[0] == self.META_PAYLOAD[key][0]:
                    if ("ATT_" in key) or ("_V_" in key) or ("PDOP" in key) or ("GNSS_H" in key):
                        item[1] = struct.unpack("=f", struct.pack("=I", item[1]))[0]
                    self.META_PAYLOAD[key] = item
                    break
        lensval = LENS_LOOKUP[self.META_PAYLOAD["LENS"][1]]
        self.META_PAYLOAD["GNSS_LAT_HI"][1] = (self.META_PAYLOAD["GNSS_LAT_HI"][1] << 32) | self.META_PAYLOAD["GNSS_LAT_LO"][1]
        self.META_PAYLOAD["GNSS_LON_HI"][1] = (self.META_PAYLOAD["GNSS_LON_HI"][1] << 32) | self.META_PAYLOAD["GNSS_LON_LO"][1]
        self.META_PAYLOAD["GNSS_LAT_HI"][1] = struct.unpack("=d", struct.pack("=Q", self.META_PAYLOAD["GNSS_LAT_HI"][1]))[0]
        self.META_PAYLOAD["GNSS_LON_HI"][1] = struct.unpack("=d", struct.pack("=Q", self.META_PAYLOAD["GNSS_LON_HI"][1]))[0]
        self.META_PAYLOAD["GNSS_VELOCITY_N"][1] = "N" if self.META_PAYLOAD["GNSS_LAT_HI"][1] > 0 else "S"
        self.META_PAYLOAD["GNSS_VELOCITY_E"][1] = "E" if self.META_PAYLOAD["GNSS_LON_HI"][1] > 0 else "W"
        self.META_PAYLOAD["GNSS_LAT_HI"][1] = self._formatLATLON(self.META_PAYLOAD["GNSS_LAT_HI"][1])
        self.META_PAYLOAD["GNSS_LON_HI"][1] = self._formatLATLON(self.META_PAYLOAD["GNSS_LON_HI"][1])
        self.META_PAYLOAD["LENS"][1] = LENS_LOOKUP[self.META_PAYLOAD["LENS"][1]][0][0]
        try:
            if self.META_PAYLOAD["EXP_TIME"][1] in range(len(EXP_LOOKPUP)):
                self.META_PAYLOAD["EXP_TIME"][1] = EXP_LOOKPUP[self.META_PAYLOAD["EXP_TIME"][1]]
            else:
                self.META_PAYLOAD["EXP_TIME"][1] = str(min(EXP_LOOKPUP[1:30], key=lambda x:abs(int(x.split('/')[1])-int(1000000.0 / self.META_PAYLOAD["EXP_TIME"][1]))))
        except Exception as e:
            print(e)
        return lensval
    def _formatLATLON(self, data):
        abso = abs(data)

        degr = int(np.floor(abso))
        minutes = (abso - degr)*60
        int_minutes = int(np.floor(minutes))
        seconds = (minutes - int_minutes)*60
        retval = str(degr) + " " + str(int_minutes) + " " + str((seconds))
        return retval
