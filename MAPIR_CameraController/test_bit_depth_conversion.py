import bit_depth_conversion
import numpy as np

def test_normalize():
    layer_arr = []

    max_pixel = 20
    min_pixel = 0

    for i in range(min_pixel, max_pixel + 1):
        arr = i*np.ones((1, 100))
        layer_arr.extend(arr)
    layer = np.array(layer_arr)

    expected_normalized_layer_arr = []
    normalized_values = [
        0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5,
        0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0
    ]

    for i in normalized_values:
        arr = i*np.ones((1, 100))
        expected_normalized_layer_arr.extend(arr)
    expected_normalized_layer = np.array(expected_normalized_layer_arr)

    normalized_layer = bit_depth_conversion.normalize(layer, max_pixel, min_pixel)
    assert np.array_equal(normalized_layer, expected_normalized_layer)
