import numpy as np
from OpenGL.GL import *
import ctypes

class Face:

    def __init__(self, face_data, points):
        self.vertices = face_data['vertices']
        self.points = points
        self.color = [c / 255.0 for c in face_data['color']] if 'color' in face_data else [1.0, 0.0, 0.0]

        self.triangles = self.triangulate()

        self.vao = None
        self.vbo = None

        self.vertex_count = 0

    def triangulate(self):
        triangles = []
        for i in range(1, len(self.vertices) - 1):
            triangles.append((self.vertices[0], self.vertices[i], self.vertices[i+1]))
        return triangles
    
    def gpu_data(self):

        vertex_data = []
        
        for tri_vertex_keys in self.triangles:
            for vertex_key in tri_vertex_keys:
                point = self.points[vertex_key]
                
                vertex_data.extend(point)
                vertex_data.extend(self.color)

                self.vertices_np_array = np.array(vertex_data, dtype=np.float32)
                self.vertex_count = len(vertex_data) // 6

                if self.vao is None:
                    self.vao = glGenVertexArrays(1)
                    glBindVertexArray(self.vao)

                if self.vbo is None:
                    self.vbo = glGenBuffers(1)
                    glBindBuffer(GL_ARRAY_BUFFER, self.vbo)

                glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)
                glEnableVertexAttribArray(0)
                glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(0))
                glEnableVertexAttribArray(1)
                glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(12))
                glBindBuffer(GL_ARRAY_BUFFER, 0)
                glBindVertexArray(0)

    def draw(self):
        glBindVertexArray(self.vao)
        glDrawArrays(GL_TRIANGLES, 0, self.vertex_count)
        glBindVertexArray(0)

    def destroy(self):
        if self.vao is not None:
            glDeleteVertexArrays(1, (self.vao,))
            self.vao = None
        if self.vbo is not None:
            glDeleteBuffers(1, (self.vbo,))
            self.vbo = None