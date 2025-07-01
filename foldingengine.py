import numpy as np
import math
import pyrr

class Fold:
    def __init__(self, facehandler, points):
        self.facehandler = facehandler
        self.points = points

    def fold(self, point1, point2, face, angle):
        angle = np.radians(angle)

        p1x, p1y, p1z = self.points[point1]
        p2x, p2y, p2z = self.points[point2]

        # Translation matrices
        toOrigin = pyrr.matrix44.create_from_translation((-p1x, -p1y, -p1z))
        fromOrigin = pyrr.matrix44.inverse(toOrigin)

        # Rotation matrix
        rotationMatrix = pyrr.matrix44.create_from_axis_rotation(
            axis=pyrr.vector.normalize(pyrr.vector3.create(
                x=(p2x - p1x),
                y=(p2y - p1y),
                z=(p2z - p1z),
                dtype=np.float32
            )),
            theta=angle,
            dtype=np.float32
        )


        self.facehandler.updatemodelmatrix(face, pyrr.matrix44.multiply(fromOrigin, pyrr.matrix44.multiply(rotationMatrix, toOrigin)))

    def split(point1, point2, face):
        pass