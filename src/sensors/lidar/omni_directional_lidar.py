"""
omni_directional_lidar.py

Author: Shisato Yano
"""

import numpy as np
from math import atan2, sin, cos
from scipy.stats import norm

from scan_point import ScanPoint

class OmniDirectionalLidar:
    def __init__(self, obst_list, params):
        self.obst_list = obst_list
        self.params = params
        self.DIST_DB_SIZE = int(np.floor((np.pi * 2.0) / self.params.RESO_RAD)) + 1
        self.MAX_DB_VALUE = float("inf")
        self.DELTA_LIST = np.arange(0.0, 1.0, 0.008)
        self.latest_point_cloud = []
    
    def install(self, state):
        self.params.calculate_global_pos(state)

    def _visible(self, distance_m):
        return (self.params.MIN_RANGE_M <= distance_m <= self.params.MAX_RANGE_M)
    
    def _normalize_angle_until_2pi(self, angle_rad):
        if 0.0 > angle_rad: return (angle_rad + np.pi * 2.0)
        else: return angle_rad
    
    def _normalize_angle_pi_2_pi(self, angle_rad):
        if angle_rad > np.pi: return (angle_rad - np.pi * 2.0)
        else: return angle_rad
    
    def _ray_casting_filter(self, distance_list, angle_list):
        point_cloud = []
        dist_db = [self.MAX_DB_VALUE for _ in range(self.DIST_DB_SIZE)]

        for i in range(len(angle_list)):
            normalized_angle_2pi = self._normalize_angle_until_2pi(angle_list[i])
            angle_id = int(round(normalized_angle_2pi / self.params.RESO_RAD)) % self.DIST_DB_SIZE
            if dist_db[angle_id] > distance_list[i]:
                dist_db[angle_id] = distance_list[i]
        
        for i in range(len(dist_db)):
            angle_rad = i * self.params.RESO_RAD
            angle_pi_2_pi = self._normalize_angle_pi_2_pi(angle_rad)
            distance_m = dist_db[i]
            if (distance_m != self.MAX_DB_VALUE) and self._visible(distance_m):
                angle_with_noise = norm.rvs(loc=angle_pi_2_pi, scale=self.params.ANGLE_STD_SCALE)
                dist_with_noise = norm.rvs(loc=distance_m, scale=self.params.DIST_STD_RATE*distance_m)
                x_m = dist_with_noise * cos(angle_with_noise)
                y_m = dist_with_noise * sin(angle_with_noise)
                point_cloud.append(ScanPoint(dist_with_noise, angle_with_noise, x_m, y_m))
        
        self.latest_point_cloud = point_cloud
    
    def _interpolate(self, x_1, x_2, delta):
        return ((1.0 - delta) * x_1 + delta * x_2)

    def _calculate_contour_xy(self, vertex_x, vertex_y):
        contour_x, contour_y = [], []
        len_vertex = len(vertex_x)

        for i in range(len_vertex - 1):
            contour_x.extend([self._interpolate(vertex_x[i], vertex_x[i+1], delta) for delta in self.DELTA_LIST])
            contour_y.extend([self._interpolate(vertex_y[i], vertex_y[i+1], delta) for delta in self.DELTA_LIST])
        
        contour_x.extend([self._interpolate(vertex_x[len_vertex-1], vertex_x[1], delta) for delta in self.DELTA_LIST])
        contour_y.extend([self._interpolate(vertex_y[len_vertex-1], vertex_y[1], delta) for delta in self.DELTA_LIST])

        return contour_x, contour_y

    def update(self, state):
        self.params.calculate_global_pos(state)

        distance_list, angle_list = [], []
        for obst in self.obst_list.get_list():
            vertex_x, vertex_y = obst.vertex_xy()
            contour_x, contour_y = self._calculate_contour_xy(vertex_x, vertex_y)
            for x, y in zip(contour_x, contour_y):
                diff_x = x - self.params.get_global_x_m()
                diff_y = y - self.params.get_global_y_m()
                distance_m = np.hypot(diff_x, diff_y)
                angle_rad = atan2(diff_y, diff_x) - state.get_yaw_rad()
                distance_list.append(distance_m)
                angle_list.append(angle_rad)
        
        self._ray_casting_filter(distance_list, angle_list)
    
    def draw(self, axes, elems, state):
        self.params.draw_pos(axes, elems)

        for point in self.latest_point_cloud:
            point.draw(axes, 
                       self.params.get_global_x_m(), 
                       self.params.get_global_y_m(), 
                       state.get_yaw_rad(), 
                       elems)
