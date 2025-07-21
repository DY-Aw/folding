from face import Face
import numpy as np
import pyrr

class FaceHandler:
    def __init__(self, points, face_color_uniform_location, camera):
        self.points = points
        self.face_color_uniform_location = face_color_uniform_location
        self.camera = camera
        self.faces = {}
        self.transformations = {}

    def update(self, face, faceinfo):
        faceclass = Face(faceinfo, self.points, self.face_color_uniform_location)
        self.faces.update({face: faceclass})

    def drawfaces(self, modelMatrixLocation):
        for face in self.faces.keys():
            model_transform = pyrr.matrix44.create_identity(dtype=np.float32)
            if face in self.transformations.keys():
                model_transform = self.transformations[face]
            self.faces[face].draw(modelMatrixLocation, model_transform, self.camera.facing)
    
    def updateModelMatrix(self, face, matrix):
        if face not in self.transformations.keys():
            self.transformations.update({face: matrix})
        else:
            self.transformations[face] = pyrr.matrix44.multiply(matrix, self.transformations[face])

    def destroy(self):
        for face in self.faces.values():
            face.destroy()
