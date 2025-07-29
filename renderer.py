import numpy as np
from OpenGL.GL import *

class Renderer:
    def __init__(self, points, faces, camera, faceColorUniformLocation, modelMatrixLocation):
        self.points = points
        self.faces = faces
        self.camera = camera
        self.faceColorUniformLocation = faceColorUniformLocation
        self.modelMatrixLocation = modelMatrixLocation

        # Set up vao and vbo
        vao = glGenVertexArrays(1)
        glBindVertexArray(vao)
        vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, vbo)

        # Position attribute
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 12, ctypes.c_void_p(0))

    def drawPoint(self, vertex, color, face, size=1.0):
        glEnable(GL_POLYGON_OFFSET_POINT)
        glPolygonOffset(-100.0, -100.0)
        glEnable(GL_POINT_SMOOTH)
        glPointSize(size)
        if type(vertex) == tuple:
            self.gpuData(vertex)
        else:
            self.gpuData(self.points[vertex])

        glUniform3fv(self.faceColorUniformLocation, 1, color)

        glUniformMatrix4fv(self.modelMatrixLocation, 1, GL_FALSE, self.faces[face].model_transform)

        glDrawArrays(GL_POINTS, 0, 1)
        glDisable(GL_POLYGON_OFFSET_POINT)

    def drawLine(self, vertexIDs, color, face, width=1.0):
        glLineWidth(width)
        vertices = []
        for vertex in vertexIDs:
            vertices.extend(self.points[vertex])
        self.gpuData(vertices)

        glUniform3fv(self.faceColorUniformLocation, 1, color)

        glUniformMatrix4fv(self.modelMatrixLocation, 1, GL_FALSE, self.faces[face].model_transform)

        glDrawArrays(GL_LINES, 0, len(vertexIDs))
    
    def drawOutline(self, face, color, width=1.0):
        glLineWidth(width)
        vertexIDs = self.faces[face].vertices
        vertices = []
        for vertex in vertexIDs:
            vertices.extend(self.points[vertex])
        self.gpuData(vertices)

        glUniform3fv(self.faceColorUniformLocation, 1, color)

        glUniformMatrix4fv(self.modelMatrixLocation, 1, GL_FALSE, self.faces[face].model_transform)

        glDrawArrays(GL_LINE_LOOP, 0, len(vertexIDs))

    def drawFace(self, faceID):
        glEnable(GL_POLYGON_OFFSET_FILL)
        glPolygonOffset(1.0, 1.0)
        face = self.faces[faceID]
        vertices = face.triangles
        self.gpuData(vertices)

        face.colorcalculate(self.camera.position)
        glUniform3fv(self.faceColorUniformLocation, 1, face.color)

        glUniformMatrix4fv(self.modelMatrixLocation, 1, GL_FALSE, face.model_transform)
        glDrawArrays(GL_TRIANGLES, 0, len(vertices))
        glDisable(GL_POLYGON_OFFSET_FILL)

    def gpuData(self, vertices):
        vertexArray = np.array(vertices, dtype=np.float32)
        glBufferData(GL_ARRAY_BUFFER, vertexArray.nbytes, vertexArray, GL_STATIC_DRAW)

