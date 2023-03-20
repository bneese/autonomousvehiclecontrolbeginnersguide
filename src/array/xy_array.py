"""
xy_array.py

Author: Shisato Yano
"""

from math import sin, cos
import numpy as np


class XYArray:
    """
    X-Y 2D array data and logic class
    """

    def __init__(self, array):
        """
        Constructor
        array: np.array([[x1, x2,..., xn], [y1, y2,..., yn]])
        """

        self.array = array
    
    def homogeneous_transformation(self, x, y, angle_rad):
        angle_cos = cos(angle_rad)
        angle_sin = sin(angle_rad)

        rotation_matrix = np.array([[angle_cos, -angle_sin],
                                    [angle_sin, angle_cos]])
        
        rotated_array = rotation_matrix.dot(self.array)

        return rotated_array + np.ones(rotated_array.shape) * np.array([[x], [y]])
    
    def draw(self, axes, color, line_width, line_type):
        return axes.plot(self.array[0, :], self.array[1, :],
                         color=color, lw=line_width, ls=line_type)
