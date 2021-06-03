'''This function adjusts the IMU data of the camera to match the image captured by the sensor.'''
import sys

def AdjustYPR(atype=0, arid=0, imu=[0.0, 0.0, 0.0]):
    if atype == 101:
        orientation = arid % 2
        #imu[1] = -imu[1]
        if orientation: # Links 1 and 3
            #print("1 or 3: ", arid)
            imu[0] = -imu[0]
            imu[2] = -imu[2]
            #imu[0] += 180
            #imu[0] = imu[0] % 360
            #imu[2] = -imu[2]
        else:
            imu[1] = -imu[1]

    if atype != 100:
        index = atype % 4
        orientation = arid % 2
        imu[0] += (index * 90.0)
        if orientation: # Links 1 and 3
            imu[0] += 180.0
        imu[0] = imu[0] % 360
        if orientation:
            if index == 2:
                pass
            elif index == 3:
                imu[1], imu[2] = -imu[2], imu[1]
            elif index == 0:
                imu[1], imu[2] = -imu[1], -imu[2]
            else:
                imu[1], imu[2] = imu[2], -imu[1]
        else:
            if index == 0:
                pass
            elif index == 1:
                imu[1], imu[2] = -imu[2], imu[1]
            elif index == 2:
                imu[1], imu[2] = -imu[1], -imu[2]
            else:
                imu[1], imu[2] = imu[2], -imu[1]

    return imu


# These numbers (CURVE_NUMBERS_MASTER) represent the rotations of the 100 series of kernel arrays.
# They are negative because they use the master camera as their reference point.

CURVE_NUMBERS_MASTER = {
    "YAW": -2.5,
    "PITCH": -13.5,
    "ROLL": -17.3
}

# This function adds the numbers above to adjust imu for curved arrays.
def CurveAdjustment(array_type=100, array_id=0, imu=[0.0, 0.0, 0.0]):
    try:

        if array_type == 100:
            if array_id in [0, 2]:
                imu[0] += CURVE_NUMBERS_MASTER["YAW"]
                imu[1] += CURVE_NUMBERS_MASTER["PITCH"]
                imu[2] += CURVE_NUMBERS_MASTER["ROLL"]
            else:
                imu[0] -= CURVE_NUMBERS_MASTER["YAW"]
                imu[1] += CURVE_NUMBERS_MASTER["PITCH"]
                imu[2] -= CURVE_NUMBERS_MASTER["ROLL"]

        elif array_type == 101:
            if array_id == 0:
                imu[0] += CURVE_NUMBERS_MASTER["YAW"]
                imu[1] += CURVE_NUMBERS_MASTER["PITCH"]
                imu[2] += CURVE_NUMBERS_MASTER["ROLL"]

            elif array_id == 1:
                imu[0] -= CURVE_NUMBERS_MASTER["YAW"]
                imu[1] += CURVE_NUMBERS_MASTER["PITCH"]
                imu[2] -= CURVE_NUMBERS_MASTER["ROLL"]

            elif array_id == 2:
                imu[0] -= CURVE_NUMBERS_MASTER["YAW"]
                imu[1] += CURVE_NUMBERS_MASTER["PITCH"]
                imu[2] -= CURVE_NUMBERS_MASTER["ROLL"]

            else:
                imu[0] += CURVE_NUMBERS_MASTER["YAW"]
                imu[1] += CURVE_NUMBERS_MASTER["PITCH"]
                imu[2] += CURVE_NUMBERS_MASTER["ROLL"]

        return imu

    except Exception as e:
        print(e)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print("Line: " + str(exc_tb.tb_lineno))
