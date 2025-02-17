"""
pure_pursuit_controller.py

Author: Shisato Yano
"""

from math import sin, tan, atan2


class PurePursuitController:
    """
    Controller class by Pure Pursuit algorithm
    """
    
    def __init__(self, spec, course=None, color='g'):
        """
        Constructor
        spec: Vehicle specification object
        course: Course data and logic object
        color: Color of drawing target point
        """
        
        self.MIN_LOOK_AHEAD_DISTANCE_M = 2.0
        self.LOOK_FORWARD_GAIN = 0.3
        self.SPEED_PROPORTIONAL_GAIN = 1.0
        self.WHEEL_BASE_M = spec.wheel_base_m
        self.MAX_ACCEL_MPS2 = spec.max_accel_mps2
        self.DRAW_COLOR = color

        self.course = course
        self.look_ahead_distance_m = self.MIN_LOOK_AHEAD_DISTANCE_M
        self.target_course_index = 0
        self.target_accel_mps2 = 0.0
        self.target_speed_mps = 0.0
        self.target_steer_rad = 0.0
        self.target_yaw_rate_rps = 0.0
        self.elapsed_time_sec = 0.0

        if self.course:    
            self.max_spd_mps = self.course.max_speed_mps()
            self.course_distance_m = self.course.distance_m()
        else:
            self.max_spd_mps = 5.0
            self.course_distance_m = 10.0
        self.accel_time_s = self.max_spd_mps / self.MAX_ACCEL_MPS2
        self.decel_time_s = self.accel_time_s
        accel_dist_m = self.max_spd_mps * self.accel_time_s / 2
        decel_dist_m = self.max_spd_mps * self.decel_time_s / 2
        self.const_time_s = (self.course_distance_m - accel_dist_m - decel_dist_m) / self.max_spd_mps
    
    def _calculate_look_ahead_distance(self, state):
        """
        Private function to calculate look ahead distance to target point
        state: Vehicle's state object
        """
        
        self.look_ahead_distance_m = self.LOOK_FORWARD_GAIN * state.get_speed_mps() + self.MIN_LOOK_AHEAD_DISTANCE_M

    def _calculate_target_course_index(self, state):
        """
        Private function to calculate target point's index on course
        state: Vehicle's state object
        """
        
        nearest_index = self.course.search_nearest_point_index(state)
        while self.look_ahead_distance_m > self.course.calculate_distance_from_point(state, nearest_index):
            if nearest_index + 1 >= self.course.length(): break
            nearest_index += 1
        self.target_course_index = nearest_index

    def _decide_target_speed_mps(self, time_s):
        """
        Private function to decide target speed[m/s]
        time_s: interval time[sec]
        """
        
        if self.elapsed_time_sec <= self.accel_time_s:
            self.target_speed_mps += self.MAX_ACCEL_MPS2 * time_s
            if self.target_speed_mps >= self.max_spd_mps:
                self.target_speed_mps = self.max_spd_mps
        elif self.accel_time_s < self.elapsed_time_sec <= (self.accel_time_s + self.const_time_s):
            self.target_speed_mps = self.max_spd_mps
        else:
            self.target_speed_mps -= self.MAX_ACCEL_MPS2 * time_s
            if self.target_speed_mps <= 0.0:
                self.target_speed_mps = 0.0

    def _calculate_target_acceleration_mps2(self, state):
        """
        Private function to calculate acceleration input
        state: Vehicle's state object
        """

        diff_speed_mps = self.target_speed_mps - state.get_speed_mps()
        self.target_accel_mps2 = self.SPEED_PROPORTIONAL_GAIN * diff_speed_mps

    def _calculate_target_steer_angle_rad(self, state):
        """
        Private function to calculate steering angle input
        state: Vehicle's state object
        """
        
        diff_angle_rad = self.course.calculate_angle_difference_rad(state, self.target_course_index)
        self.target_steer_rad = atan2((2 * self.WHEEL_BASE_M * sin(diff_angle_rad)), self.look_ahead_distance_m)

    def _calculate_target_yaw_rate_rps(self, state):
        """
        Private function to calculate yaw rate input
        state: Vehicle's state object
        """

        self.target_yaw_rate_rps = state.get_speed_mps() * tan(self.target_steer_rad) / self.WHEEL_BASE_M

    def update(self, state, time_s):
        """
        Function to update data for path tracking
        state: Vehicle's state object
        time_s: Simulation interval time[sec]
        """
        
        if not self.course: return

        self._calculate_look_ahead_distance(state)
        
        self._calculate_target_course_index(state)

        self._decide_target_speed_mps(time_s)

        self._calculate_target_acceleration_mps2(state)

        self._calculate_target_steer_angle_rad(state)

        self._calculate_target_yaw_rate_rps(state)

        self.elapsed_time_sec += time_s
    
    def get_target_accel_mps2(self):
        """
        Function to get acceleration input[m/s2]
        """
        
        return self.target_accel_mps2
    
    def get_target_steer_rad(self):
        """
        Function to get steering angle input[rad]
        """
        
        return self.target_steer_rad

    def get_target_yaw_rate_rps(self):
        """
        Function to get yaw rate input[rad/s]
        """

        return self.target_yaw_rate_rps
    
    def draw(self, axes, elems):
        """
        Function to draw target point on course
        axes: Axes object of figure
        elems: plot object's list
        """

        target_point_plot, = axes.plot(self.course.point_x_m(self.target_course_index), 
                                       self.course.point_y_m(self.target_course_index), 
                                       marker='o', 
                                       color=self.DRAW_COLOR,
                                       linewidth=0, 
                                       label="Target Point")
        elems.append(target_point_plot)
