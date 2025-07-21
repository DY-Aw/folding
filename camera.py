import math
import pyrr

from OpenGL.GL import *

class Camera:
    def __init__(self, data):
        yaw, pitch, zoom = data
        self.yaw = math.radians(yaw)
        self.pitch = math.radians(pitch)
        self.zoom = zoom
    
    def calculateViewMatrix(self, modelViewLocation):
        # Facing unit vector
        yc = math.sin(self.pitch)
        xc = math.cos(self.yaw) * math.cos(self.pitch)
        zc = math.sin(self.yaw) * math.cos(self.pitch)

        # Scale facing vector
        x = self.zoom * xc
        y = self.zoom * yc
        z = self.zoom * zc

        eye = pyrr.vector3.create(x=x, y=y, z=z)
        target = pyrr.vector3.create(x=0.0, y=0.0, z=0.0)
        up = pyrr.vector3.create(x=0.0, y=1.0, z=0.0)

        view_transform = pyrr.matrix44.create_look_at(eye, target, up, dtype=None)
        glUniformMatrix4fv(modelViewLocation, 1, GL_FALSE, view_transform)