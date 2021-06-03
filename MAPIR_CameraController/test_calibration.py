import Calibration

def test_filter_detected_targets_by_id():
    corners = [
        [[1, 2], [2, 2], [2, 1], [1, 1]],
        [[3, 4], [4, 4], [4, 3], [3, 3]],
        [[5, 6], [6, 6], [6, 5], [5, 5]],
        [[7, 8], [8, 8], [8, 7], [7, 7]],
    ]
    ids = [1, 2, 3, 4]
    third_target_corners = Calibration.filter_detected_targets_by_id(corners, ids, 3)
    assert third_target_corners == [[[5, 6], [6, 6], [6, 5], [5, 5]]]
