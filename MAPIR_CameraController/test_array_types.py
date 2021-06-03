from ArrayTypes import AdjustYPR, CurveAdjustment

# def test_adjust_ypr(array_type, array_id, expected_output):
#     imu = [1.0, 2.0, 3.0]
#     adjusted_imu = AdjustYPR(array_type, array_id, imu)
#     assert adjusted_imu == expected_output

def test_adjust_ypr_array_type_0():
    imu = [1.0, 2.0, 3.0]
    array_type = 0
    array_id = 0
    adjusted_imu = AdjustYPR(array_type, array_id, imu)
    assert adjusted_imu == [1.0, 2.0, 3.0]

def test_adjust_ypr_array_type_1():
    imu = [1.0, 2.0, 3.0]
    array_type = 1
    array_id = 0
    adjusted_imu = AdjustYPR(array_type, array_id, imu)
    assert adjusted_imu == [91.0, -3.0, 2.0]

def test_adjust_ypr_array_type_2():
    imu = [1.0, 2.0, 3.0]
    array_type = 2
    array_id = 0
    adjusted_imu = AdjustYPR(array_type, array_id, imu)
    assert adjusted_imu == [181.0, -2.0, -3.0]

def test_adjust_ypr_array_type_3():
    imu = [1.0, 2.0, 3.0]
    array_type = 3
    array_id = 0
    adjusted_imu = AdjustYPR(array_type, array_id, imu)
    assert adjusted_imu == [271.0, 3.0, -2.0]

def test_adjust_ypr_array_type_4():
    imu = [1.0, 2.0, 3.0]
    # test_adjust_ypr(4,0, [271.0, 3.0, -2.0])
    array_type = 4
    array_id = 0
    adjusted_imu = AdjustYPR(array_type, array_id, imu)
    assert adjusted_imu == [1.0, 2.0, 3.0]

    imu = [1.0, 2.0, 3.0]
    array_id = 1
    adjusted_imu = AdjustYPR(array_type, array_id, imu)
    assert adjusted_imu == [181.0, -2.0, -3.0]


def test_adjust_ypr_array_type_5():
    imu = [1.0, 2.0, 3.0]
    array_type = 5
    array_id = 0
    adjusted_imu = AdjustYPR(array_type, array_id, imu)
    assert adjusted_imu == [91.0, -3.0, 2.0]

    imu = [1.0, 2.0, 3.0]
    array_id = 1
    adjusted_imu = AdjustYPR(array_type, array_id, imu)
    assert adjusted_imu == [271.0, 3.0, -2.0]

def test_adjust_ypr_array_type_6():
    imu = [1.0, 2.0, 3.0]
    array_type = 6
    array_id = 0
    adjusted_imu = AdjustYPR(array_type, array_id, imu)
    assert adjusted_imu == [181.0, -2.0, -3.0]

    imu = [1.0, 2.0, 3.0]
    array_id = 1
    adjusted_imu = AdjustYPR(array_type, array_id, imu)
    assert adjusted_imu == [1.0, 2.0, 3.0]

def test_adjust_ypr_array_type_7():
    imu = [1.0, 2.0, 3.0]
    array_type = 7
    array_id = 0
    adjusted_imu = AdjustYPR(array_type, array_id, imu)
    assert adjusted_imu == [271.0, 3.0, -2.0]

    imu = [1.0, 2.0, 3.0]
    array_id = 1
    adjusted_imu = AdjustYPR(array_type, array_id, imu)
    assert adjusted_imu == [91.0, -3.0, 2.0]

def test_adjust_ypr_array_type_8():
    imu = [1.0, 2.0, 3.0]
    array_type = 8
    array_id = 0
    adjusted_imu = AdjustYPR(array_type, array_id, imu)
    assert adjusted_imu == [1.0, 2.0, 3.0]

    imu = [1.0, 2.0, 3.0]
    array_id = 1
    adjusted_imu = AdjustYPR(array_type, array_id, imu)
    assert adjusted_imu == [181.0, -2.0, -3.0]

    imu = [1.0, 2.0, 3.0]
    array_id = 2
    adjusted_imu = AdjustYPR(array_type, array_id, imu)
    assert adjusted_imu == [1.0, 2.0, 3.0]

    imu = [1.0, 2.0, 3.0]
    array_id = 3
    adjusted_imu = AdjustYPR(array_type, array_id, imu)
    assert adjusted_imu == [181.0, -2.0, -3.0]

def test_adjust_ypr_array_type_9():
    imu = [1.0, 2.0, 3.0]
    array_type = 9
    array_id = 0
    adjusted_imu = AdjustYPR(array_type, array_id, imu)
    assert adjusted_imu == [91.0, -3.0, 2.0]

    imu = [1.0, 2.0, 3.0]
    array_id = 1
    adjusted_imu = AdjustYPR(array_type, array_id, imu)
    assert adjusted_imu == [271.0, 3.0, -2.0]

    imu = [1.0, 2.0, 3.0]
    array_id = 2
    adjusted_imu = AdjustYPR(array_type, array_id, imu)
    assert adjusted_imu == [91.0, -3.0, 2.0]

    imu = [1.0, 2.0, 3.0]
    array_id = 3
    adjusted_imu = AdjustYPR(array_type, array_id, imu)
    assert adjusted_imu == [271.0, 3.0, -2.0]

def test_adjust_ypr_array_type_10():
    imu = [1.0, 2.0, 3.0]
    array_type = 10
    array_id = 0
    adjusted_imu = AdjustYPR(array_type, array_id, imu)
    assert adjusted_imu == [181.0, -2.0, -3.0]

    imu = [1.0, 2.0, 3.0]
    array_id = 1
    adjusted_imu = AdjustYPR(array_type, array_id, imu)
    assert adjusted_imu == [1.0, 2.0, 3.0]

    imu = [1.0, 2.0, 3.0]
    array_id = 2
    adjusted_imu = AdjustYPR(array_type, array_id, imu)
    assert adjusted_imu == [181.0, -2.0, -3.0]

    imu = [1.0, 2.0, 3.0]
    array_id = 3
    adjusted_imu = AdjustYPR(array_type, array_id, imu)
    assert adjusted_imu == [1.0, 2.0, 3.0]

def test_adjust_ypr_array_type_11():
    imu = [1.0, 2.0, 3.0]
    array_type = 11
    array_id = 0
    adjusted_imu = AdjustYPR(array_type, array_id, imu)
    assert adjusted_imu == [271.0, 3.0, -2.0]

    imu = [1.0, 2.0, 3.0]
    array_id = 1
    adjusted_imu = AdjustYPR(array_type, array_id, imu)
    assert adjusted_imu == [91.0, -3.0, 2.0]

    imu = [1.0, 2.0, 3.0]
    array_id = 2
    adjusted_imu = AdjustYPR(array_type, array_id, imu)
    assert adjusted_imu == [271.0, 3.0, -2.0]

    imu = [1.0, 2.0, 3.0]
    array_id = 3
    adjusted_imu = AdjustYPR(array_type, array_id, imu)
    assert adjusted_imu == [91.0, -3.0, 2.0]

def test_adjust_ypr_array_type_12():
    imu = [1.0, 2.0, 3.0]
    array_type = 12
    array_id = 0
    adjusted_imu = AdjustYPR(array_type, array_id, imu)
    assert adjusted_imu == [1.0, 2.0, 3.0]

    imu = [1.0, 2.0, 3.0]
    array_id = 1
    adjusted_imu = AdjustYPR(array_type, array_id, imu)
    assert adjusted_imu == [181.0, -2.0, -3.0]

    imu = [1.0, 2.0, 3.0]
    array_id = 2
    adjusted_imu = AdjustYPR(array_type, array_id, imu)
    assert adjusted_imu == [1.0, 2.0, 3.0]

    imu = [1.0, 2.0, 3.0]
    array_id = 3
    adjusted_imu = AdjustYPR(array_type, array_id, imu)
    assert adjusted_imu == [181.0, -2.0, -3.0]

def test_adjust_ypr_array_type_13():
    imu = [1.0, 2.0, 3.0]
    array_type = 13
    array_id = 0
    adjusted_imu = AdjustYPR(array_type, array_id, imu)
    assert adjusted_imu == [91.0, -3.0, 2.0]

    imu = [1.0, 2.0, 3.0]
    array_id = 1
    adjusted_imu = AdjustYPR(array_type, array_id, imu)
    assert adjusted_imu == [271.0, 3.0, -2.0]

    imu = [1.0, 2.0, 3.0]
    array_id = 2
    adjusted_imu = AdjustYPR(array_type, array_id, imu)
    assert adjusted_imu == [91.0, -3.0, 2.0]

    imu = [1.0, 2.0, 3.0]
    array_id = 3
    adjusted_imu = AdjustYPR(array_type, array_id, imu)
    assert adjusted_imu == [271.0, 3.0, -2.0]

def test_adjust_ypr_array_type_14():
    imu = [1.0, 2.0, 3.0]
    array_type = 14
    array_id = 0
    adjusted_imu = AdjustYPR(array_type, array_id, imu)
    assert adjusted_imu == [181.0, -2.0, -3.0]

    imu = [1.0, 2.0, 3.0]
    array_id = 1
    adjusted_imu = AdjustYPR(array_type, array_id, imu)
    assert adjusted_imu == [1.0, 2.0, 3.0]

    imu = [1.0, 2.0, 3.0]
    array_id = 2
    adjusted_imu = AdjustYPR(array_type, array_id, imu)
    assert adjusted_imu == [181.0, -2.0, -3.0]

    imu = [1.0, 2.0, 3.0]
    array_id = 3
    adjusted_imu = AdjustYPR(array_type, array_id, imu)
    assert adjusted_imu == [1.0, 2.0, 3.0]


def test_adjust_ypr_array_type_15():
    imu = [1.0, 2.0, 3.0]
    array_type = 15
    array_id = 0
    adjusted_imu = AdjustYPR(array_type, array_id, imu)
    assert adjusted_imu == [271.0, 3.0, -2.0]

    imu = [1.0, 2.0, 3.0]
    array_id = 1
    adjusted_imu = AdjustYPR(array_type, array_id, imu)
    assert adjusted_imu == [91.0, -3.0, 2.0]

    imu = [1.0, 2.0, 3.0]
    array_id = 2
    adjusted_imu = AdjustYPR(array_type, array_id, imu)
    assert adjusted_imu == [271.0, 3.0, -2.0]

    imu = [1.0, 2.0, 3.0]
    array_id = 3
    adjusted_imu = AdjustYPR(array_type, array_id, imu)
    assert adjusted_imu == [91.0, -3.0, 2.0]

def test_curve_adjustment():
    array_type = 100

    imu = [0.0, 0.0, 0.0]
    array_id = 0
    adjusted_imu = CurveAdjustment(array_type, array_id, imu)
    assert adjusted_imu == [-2.5, -13.5, -17.3]

    imu = [0.0, 0.0, 0.0]
    array_id = 1
    adjusted_imu = CurveAdjustment(array_type, array_id, imu)
    assert adjusted_imu == [2.5, -13.5, 17.3]

    imu = [0.0, 0.0, 0.0]
    array_id = 2
    adjusted_imu = CurveAdjustment(array_type, array_id, imu)
    assert adjusted_imu == [-2.5, -13.5, -17.3]

    imu = [0.0, 0.0, 0.0]
    array_id = 3
    adjusted_imu = CurveAdjustment(array_type, array_id, imu)
    assert adjusted_imu == [2.5, -13.5, 17.3]