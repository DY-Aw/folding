import math
import numpy as np
from vop import Vector

class Camera:
    def __init__(self, x, y, z, yaw, pitch, hfov, sw, sh):
        self.x, self.y, self.z = x, y, z
        self.yaw, self.pitch = math.radians(yaw), math.radians(pitch)
        self.sw, self.sh = sw, sh
        self.ar = self.sw / self.sh
        self.hfov = math.radians(hfov)
        self.vfov = 2 * math.atan(math.tan(self.hfov/2)/(self.sw / self.sh))
        self.near_clip = 0.1
        self.far_clip = 100.0

    def getposition(self):
        return Vector(self.x, self.y, self.z)

    def getfacing(self):
        fx = -math.cos(self.yaw) * math.cos(self.pitch)
        fy = math.sin(self.pitch)
        fz = -math.sin(self.yaw) * math.cos(self.pitch)
        return Vector(fx, fy, fz).normalize()
    
    def getupvector(self):
        return Vector(0, 1, 0)
    
    def getrightvector(self):
        return Vector(0, 1, 0).cross(self.getfacing()).normalize()
    
    def viewmatrix(self):
        right = self.getrightvector()
        up = self.getupvector()
        forward = self.getfacing()
        eye = self.getposition()
        view_matrix = np.array([
            [right.x, right.y, right.z, -right.dot(eye)],
            [up.x, up.y, up.z, -up.dot(eye)],
            [-forward.x, -forward.y, -forward.z, forward.dot(eye)],
            [0, 0, 0, 1]
        ])
        return view_matrix.T
    
    def perspectivematrix(self):
        f = 1 / math.tan(self.vfov / 2)
        z_norm_factor = (self.far_clip + self.near_clip) / (self.near_clip - self.far_clip)
        z_translation = (2 * self.far_clip * self.near_clip) / (self.near_clip - self.far_clip)
        perspective_matrix = np.array([
            [f/self.ar, 0, 0, 0],
            [0, f, 0, 0],
            [0, 0, z_norm_factor, z_translation],
            [0, 0, -1, 0]
        ])
        return perspective_matrix.T