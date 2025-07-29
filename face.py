import numpy as np
from OpenGL.GL import *
import ctypes
import pyrr

class Face:

    def __init__(self, face_data, points, faceColorUniformLocation, matrix=pyrr.matrix44.create_identity()):
        self.vertices = face_data['vertices']
        self.points = points

        self.sunlight = pyrr.vector.normalize(pyrr.vector3.create(0.5, 0.7, -0.5))
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
        pointinquestion = pyrr.matrix44.multiply(
            pyrr.Vector4(np.append(self.points[self.vertices[0]], 1.0)),
            pyrr.matrix44.inverse(self.model_transform).T

        )
        pointinquestion = pyrr.vector3.create(
            pointinquestion[0],
            pointinquestion[1],
            pointinquestion[2]
        )

        facing = pyrr.vector.normalize(pyrr.Vector3(pointinquestion - position))
        facing = pyrr.vector3.create(facing[0], facing[1], facing[2])

        facenormal = pyrr.matrix44.multiply(pyrr.vector4.create(0, 1, 0, 0), self.model_transform)
        normal = pyrr.vector.normalize(pyrr.vector3.create(facenormal[0], facenormal[1], facenormal[2]))
        
        #color calculation
        dot_product = pyrr.vector.dot(normal, facing)
        if dot_product < 0:
            basecolor = self.frontcolor
        else:
            basecolor = self.backcolor
            normal = -normal

        c1, c2, c3 = basecolor
        sun_dot = pyrr.vector.dot(normal, self.sunlight)
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
        self.model_transform = pyrr.matrix44.multiply(self.model_transform, matrix)

    def destroy(self):
        glDeleteVertexArrays(1, (self.tvao,))
        glDeleteBuffers(1, (self.tvbo,))

