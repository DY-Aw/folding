import numpy as np
from OpenGL.GL import *
import ctypes
import pyrr

class Face:

    def __init__(self, face_data, points, face_color_uniform_location):
        self.vertices = face_data['vertices']
        self.points = points
        self.center = (0,0,0)

        self.sunlight = pyrr.vector.normalize(pyrr.vector3.create(0.5, 0.7, -0.5))
        self.frontcolor = (1.0, 0.0, 0.0)
        self.backcolor = (1.0, 1.0, 1.0)
        self.epsilon = 1e-2

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

    def colorcalculate(self, model_transform, position):
        pointinquestion = pyrr.matrix44.multiply(
            pyrr.matrix44.inverse(model_transform).T,
            pyrr.Vector4(self.center+(1,))
        )
        pointinquestion = pyrr.vector3.create(
            pointinquestion[0],
            pointinquestion[1],
            pointinquestion[2]
        )

        facing = pyrr.vector.normalize(pyrr.Vector3(pointinquestion - position))
        facing = pyrr.vector3.create(-facing[0], facing[1], -facing[2])

        facenormal = pyrr.matrix44.multiply(model_transform, pyrr.vector4.create(0, 1, 0, 0))
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


        #self.color = basecolor


        '''normal *= np.sign(normal.dot(self.sunlight))
        sun_dot = normal.dot(self.sunlight)
        normalfacing = np.sign(pyrr.Vector3(facing).dot(normal))
        sun_dot *= normalfacing
        multiplier = (sun_dot / 2.5) + 0.7
        self.color = [
            multiplier * c1,
            multiplier * c2,
            multiplier * c3
        ]'''

    def triangulate(self):
        triangles = []
        for i in range(1, len(self.vertices) - 1):
            triangles += self.points[self.vertices[0]]
            triangles += self.points[self.vertices[i]]
            triangles += self.points[self.vertices[i+1]]
        return tuple(triangles)
    

    def draw(self, modelMatrixLocation, model_transform, position):
        self.colorcalculate(model_transform, position)
        glUniform3fv(self.face_color_uniform_location, 1, self.color)

        # Define model matrix
        glUniformMatrix4fv(modelMatrixLocation, 1, GL_FALSE, model_transform)

        glBindVertexArray(self.vao)
        glDrawArrays(GL_TRIANGLES, 0, self.vertex_count)

    def centercalc(self):
        x, y, z = 0, 0, 0
        for vertex in self.vertices:
            cx, cy, cz = self.points[vertex]
            x += cx
            y += cy
            z += cz
        
        return (x, y, z)

    def destroy(self):
        glDeleteVertexArrays(1, (self.vao,))
        glDeleteBuffers(1, (self.vbo,))

