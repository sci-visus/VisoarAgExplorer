import numpy as np

# class Geometry:
#     @staticmethod
#     def get_distance_between_two_points(a, b):
#         return np.sqrt(np.power((a[0] - b[0]), 2) + np.power((a[1] - b[1]), 2))

def distance(a, b):
    return np.sqrt(np.power((a[0] - b[0]), 2) + np.power((a[1] - b[1]), 2))

def slope(a, b):
    return (b[1] - a[1]) / (b[0] - a[0])