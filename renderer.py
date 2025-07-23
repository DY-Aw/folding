import numpy as np
from OpenGL.GL import *

class Renderer:
    def __init__(self, points, facehandler, camera, faceColorUniformLocation, modelMatrixLocation):
        self.points = points
        self.facehandler = facehandler
        self.camera = camera
        self.faceColorUniformLocation = faceColorUniformLocation
        self.modelMatrixLocation = modelMatrixLocation

    def drawLine(self, vertexIDs, color, face, width=1.0):
        glLineWidth(width)
        vertices = []
        for vertex in vertexIDs:
            vertices.extend(self.points[vertex])
        self.gpuData(vertices)

        glUniform3fv(self.faceColorUniformLocation, 1, color)

        glUniformMatrix4fv(self.modelMatrixLocation, 1, GL_FALSE, self.facehandler.faces[face].model_transform)

        glDrawArrays(GL_LINES, 0, len(vertexIDs))
    
    def drawOutline(self, face, color, width=1.0):
        glLineWidth(width)
        vertexIDs = self.facehandler.faces[face].vertices
        vertices = []
        for vertex in vertexIDs:
            vertices.extend(self.points[vertex])
        self.gpuData(vertices)

        glUniform3fv(self.faceColorUniformLocation, 1, color)

        glUniformMatrix4fv(self.modelMatrixLocation, 1, GL_FALSE, self.facehandler.faces[face].model_transform)

        glDrawArrays(GL_LINE_LOOP, 0, len(vertexIDs))

    def drawFace(self, faceID):
        face = self.facehandler.faces[faceID]
        vertices = face.triangles
        self.gpuData(vertices)

        face.colorcalculate(self.camera.position)
        glUniform3fv(self.faceColorUniformLocation, 1, face.color)

        glUniformMatrix4fv(self.modelMatrixLocation, 1, GL_FALSE, face.model_transform)

        glDrawArrays(GL_TRIANGLES, 0, len(vertices))

    def gpuData(self, vertices):
        vertexArray = np.array(vertices, dtype=np.float32)
        vao = glGenVertexArrays(1)
        glBindVertexArray(vao)
        vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, vbo)
        glBufferData(GL_ARRAY_BUFFER, vertexArray.nbytes, vertexArray, GL_STATIC_DRAW)

        # Position attribute
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 12, ctypes.c_void_p(0))

    def gpuData2(self, vertices):
        vertexCoords = []
        for vertex in vertices:
            vertexCoords.extend(self.points[vertex])
        self.gpuData(vertexCoords)

