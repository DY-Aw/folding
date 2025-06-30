from face import Face
import numpy as np
import pyrr

class FaceHandler:
    def __init__(self, points):
        self.points = points
        self.faces = {}

    def update(self, face, faceinfo):
        faceclass = Face(faceinfo, self.points)
        self.faces.update({face: faceclass})

    def drawfaces(self, modelMatrixLocation):
        face_matrices = self.modeltransform()
        for face in self.faces.keys():
            model_transform = face_matrices[face]
            self.faces[face].draw(modelMatrixLocation, model_transform)

    def modeltransform(self):
        face_matrices = {}
        for face in self.faces.keys():

            # Create model transformation matrix
            model_transform = pyrr.matrix44.create_identity(dtype=np.float32)
            
            # Apply rotation
            model_transform = pyrr.matrix44.multiply(
                m1 = model_transform,
                m2 = pyrr.matrix44.create_from_eulers(
                    eulers = np.radians(self.faces[face].eulers),
                    dtype = np.float32
                )
            )
            
            # Apply translation
            model_transform = pyrr.matrix44.multiply(
                m1 = model_transform,
                m2 = pyrr.matrix44.create_from_translation(
                    vec = self.faces[face].position,
                    dtype = np.float32
                )
            )
            face_matrices.update({face: model_transform})
        return face_matrices

    def destroy(self):
        for face in self.faces.values():
            face.destroy()
