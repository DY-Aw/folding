from face import Face
import numpy as np
import pyrr

class FaceHandler:
    def __init__(self, points, faceColorUniformLocation):
        self.points = points
        self.faceColorUniformLocation = faceColorUniformLocation
        self.faces = {}

    def update(self, face, faceinfo, matrix=pyrr.matrix44.create_identity(dtype=np.float32)):
        faceclass = Face(faceinfo, self.points, self.faceColorUniformLocation, matrix)
        self.faces.update({face: faceclass})

    def proximity(self, mousepos):
        return "F1"

    def destroy(self):
        for face in self.faces.values():
            face.destroy()
