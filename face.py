import numpy as np
from OpenGL.GL import *
import ctypes
import pyrr

class Face:

    def __init__(self, face_data, points, face_color_uniform_location):
        self.vertices = face_data['vertices']
        self.points = points

        self.sunlight = pyrr.vector.normalize(pyrr.vector3.create(0.5, -0.7, -0.5))
        self.basecolor = (1.0, 0.0, 0.0)

        self.triangles = self.triangulate()

        self.vertex_count = len(self.triangles) // 3
        self.trianglevertices = np.array(self.triangles, dtype=np.float32)

        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.trianglevertices.nbytes, self.trianglevertices, GL_STATIC_DRAW)
        
        # Position attribute
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 12, ctypes.c_void_p(0))

        self.face_color_uniform_location = face_color_uniform_location

    def colorcalculate(self, model_transform, facing):
        vectorre = pyrr.matrix44.multiply(model_transform, pyrr.vector4.create(0, 1, 0, 0))
        c1, c2, c3 = self.basecolor
        normal = pyrr.vector.normalize(pyrr.vector3.create(vectorre[0], vectorre[1], vectorre[2]))

        #color calculation

        normal *= np.sign(normal.dot(self.sunlight))
        sun_dot = normal.dot(self.sunlight)
        normalfacing = np.sign(pyrr.Vector3(facing).dot(normal))
        sun_dot *= normalfacing
        multiplier = (-sun_dot / 2.5) + 0.7
        self.color = [
            multiplier * c1,
            multiplier * c2,
            multiplier * c3
        ]

    def triangulate(self):
        triangles = []
        for i in range(1, len(self.vertices) - 1):
            triangles += self.points[self.vertices[0]]
            triangles += self.points[self.vertices[i]]
            triangles += self.points[self.vertices[i+1]]
        return tuple(triangles)
    

    def draw(self, modelMatrixLocation, model_transform, facing):
        self.colorcalculate(model_transform, facing)
        glUniform3fv(self.face_color_uniform_location, 1, self.color)

        # Define model matrix
        glUniformMatrix4fv(modelMatrixLocation, 1, GL_FALSE, model_transform)

        glBindVertexArray(self.vao)
        glDrawArrays(GL_TRIANGLES, 0, self.vertex_count)

    def destroy(self):
        glDeleteVertexArrays(1, (self.vao,))
        glDeleteBuffers(1, (self.vbo,))

