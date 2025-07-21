import numpy as np
from OpenGL.GL import *
import ctypes
import pyrr

class Face:

    def __init__(self, face_data, points):
        #-------TEMP--------
        self.position = [0, 0, 0]
        self.eulers = [0, 0, 0]
        #---------------

        self.vertices = face_data['vertices']
        self.points = points

        self.sunlight = pyrr.Vector3([0.5, -0.7, -0.5])
        self.color = self.colorcalculate((1.0, 0.0, 0.0))

        self.triangles = self.triangulate()

        self.vertex_count = len(self.triangles) // 6
        self.trianglevertices = np.array(self.triangles, dtype=np.float32)

        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.trianglevertices.nbytes, self.trianglevertices, GL_STATIC_DRAW)
        
        # Position attribute
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(0))
        # Color attribute
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(12))

    def colorcalculate(self, basecolor):
        c1, c2, c3 = basecolor
        #normal calculation
        p1 = self.points[self.vertices[0]]
        p2 = self.points[self.vertices[1]]
        p3 = self.points[self.vertices[2]]
        v1 = pyrr.Vector3([
            p2[0] - p1[0],
            p2[1] - p1[1],
            p2[2] - p1[2]
            ])
        v2 = pyrr.Vector3([
            p3[0] - p2[0],
            p3[1] - p2[1],
            p3[2] - p2[2]
        ])
        normal = v1.cross(v2)

        #color calculation
        sun_dot = normal.dot(self.sunlight)
        multiplier = (sun_dot / 2) + 0.5
        return [
            multiplier * c1,
            multiplier * c2,
            multiplier * c3
        ]

    def triangulate(self):
        triangles = []
        for i in range(1, len(self.vertices) - 1):
            x0, y0, z0 = self.points[self.vertices[0]]
            x1, y1, z1 = self.points[self.vertices[i]]
            x2, y2, z2 = self.points[self.vertices[i+1]]
            c1, c2, c3 = tuple(self.color)
            triangles += (
                x0, y0, z0, c1, c2, c3,
                x1, y1, z1, c1, c2, c3,
                x2, y2, z2, c1, c2, c3
            )
        return tuple(triangles)
    

    def draw(self, modelMatrixLocation, model_transform):
        # Define model matrix
        glUniformMatrix4fv(modelMatrixLocation, 1, GL_FALSE, model_transform)

        glBindVertexArray(self.vao)
        glDrawArrays(GL_TRIANGLES, 0, self.vertex_count)

    def data(self):
        self.vertex_count = len(self.vertices) // 6
        self.vertices = np.array(self.vertices, dtype=np.float32)

        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)
        
        # Position attribute
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(0))
        # Color attribute
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(12))

    def destroy(self):
        glDeleteVertexArrays(1, (self.vao,))
        glDeleteBuffers(1, (self.vbo,))

