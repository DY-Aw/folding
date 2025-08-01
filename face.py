import numpy as np
from OpenGL.GL import *
import ctypes
from pyglm import glm

class Face:

    def __init__(self, face_data, points, faceColorUniformLocation, matrix=glm.mat4()):
        self.vertices = face_data['vertices']
        self.points = points

        self.sunlight = glm.normalize(glm.vec3(0.5, 0.7, -0.5))
        self.frontcolor = (1.0, 0.0, 0.0)
        self.backcolor = (1.0, 1.0, 1.0)

        self.model_transform = matrix

        self.triangles = self.triangulate()

        self.vertex_count = len(self.triangles) // 3
        self.trianglevertices = np.array(self.triangles, dtype=np.float32)

        self.tvao = glGenVertexArrays(1)
        glBindVertexArray(self.tvao)
        self.tvbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.tvbo)
        glBufferData(GL_ARRAY_BUFFER, self.trianglevertices.nbytes, self.trianglevertices, GL_STATIC_DRAW)
        
        # Position attribute
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 12, ctypes.c_void_p(0))

        self.faceColorUniformLocation = faceColorUniformLocation

    def colorcalculate(self, position):
        pointinquestion = glm.inverseTranspose(self.model_transform) * glm.vec4(*self.points[self.vertices[0]], 1.0)
        pointinquestion = glm.vec3(pointinquestion)

        facing = glm.normalize(pointinquestion - position)

        facenormal = self.model_transform * glm.vec4(0, 1, 0, 0)
        normal = glm.normalize(glm.vec3(facenormal))
        
        #color calculation
        dot_product = glm.dot(normal, facing)
        if dot_product < 0:
            basecolor = self.frontcolor
        else:
            basecolor = self.backcolor
            normal = -normal

        c1, c2, c3 = basecolor
        sun_dot = glm.dot(normal, self.sunlight)
        multiplier = (sun_dot / 2.5) + 0.7
        self.color = [
            multiplier * c1,
            multiplier * c2,
            multiplier * c3
        ]

    def triangulate(self):
        triangles = []
        for i in range(1, len(self.vertices) - 1):
            triangles.extend(self.points[self.vertices[0]])
            triangles.extend(self.points[self.vertices[i]])
            triangles.extend(self.points[self.vertices[i+1]])
        return tuple(triangles)
    
    def updateModelMatrix(self, matrix):
        self.model_transform = matrix * self.model_transform

    def destroy(self):
        glDeleteVertexArrays(1, (self.tvao,))
        glDeleteBuffers(1, (self.tvbo,))

