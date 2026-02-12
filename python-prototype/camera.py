import numpy as np
import math
from pyglm import glm

from OpenGL.GL import *

class Camera:
    def __init__(self, data):
        yaw, pitch, zoom = data
        self.yaw = yaw
        self.pitch = pitch
        self.zoom = zoom

    def getFacing(self):
        y = math.sin(self.pitch)
        x = math.cos(self.yaw) * math.cos(self.pitch)
        z = math.sin(self.yaw) * math.cos(self.pitch)
        self.facing = (x, y, z)        

    def orbit(self, yaw, pitch):
        self.yaw += yaw
        self.pitch += pitch

        if self.pitch > math.radians(90):
            self.pitch = math.radians(90)
        if self.pitch < math.radians(-90):
            self.pitch = math.radians(-90)
    
    def _zoom(self, zoom):
        self.zoom += zoom
        if self.zoom <= 0:
            self.zoom = 0
    
    def calculateViewMatrix(self, modelViewLocation):
        # Facing unit vector
        self.getFacing()
        xc, yc, zc = self.facing

        # Scale facing vector
        x = -self.zoom * xc
        y = -self.zoom * yc
        z = -self.zoom * zc

        self.position = glm.vec3(x, y, z)
        eye = self.position
        target = glm.vec3(0.0, 0.0, 0.0)
        up = glm.vec3(0.0, 1.0, 0.0)
        self.view_transform = glm.lookAt(eye, target, up)
        glUniformMatrix4fv(modelViewLocation, 1, GL_TRUE, np.array(self.view_transform))