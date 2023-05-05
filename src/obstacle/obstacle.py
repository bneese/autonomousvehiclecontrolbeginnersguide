"""
obstacle.py

Author: Shisato Yano
"""

import numpy as np
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).absolute().parent) + "/../array")
from xy_array import XYArray


class Obstacle:
    def __init__(self, state, accel_mps2=0.0, yaw_rate_rps=0.0,
                 length_m=2.0, width_m=2.0):
        self.state = state
        self.accel_mps2 = accel_mps2
        self.yaw_rate_rps = yaw_rate_rps

        contour = np.array([[length_m, -length_m, -length_m, length_m, length_m],
                            [width_m, width_m, -width_m, -width_m, width_m]])
        self.array = XYArray(contour)
    
    def update(self, time_s):
        updated_state = self.state.update(self.accel_mps2, self.yaw_rate_rps, time_s)
        self.state = updated_state
    
    def draw(self, axes, elems):
        x_m = self.state.get_x_m()
        y_m = self.state.get_y_m()
        yaw_rad = self.state.get_yaw_rad()

        transformed_array = self.array.homogeneous_transformation(x_m, y_m, yaw_rad)
        data = transformed_array.get_data()
        obstacle_plot, = axes.plot(data[0, :], data[1, :], lw=1.0, color='k', ls='-')
        elems.append(obstacle_plot)
