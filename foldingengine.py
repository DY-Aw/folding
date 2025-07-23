import numpy as np
import math
import pyrr

class Fold:
    def __init__(self, faces, points):
        self.faces = faces
        self.points = points

    def fold(self, point1, point2, face, angle):
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

        self.faces[face].updateModelMatrix(face, pyrr.matrix44.multiply(fromOrigin, pyrr.matrix44.multiply(rotationMatrix, toOrigin)))

    def foldGrab(self, point1, point2, face, mouseinfo, view_transform):
        # Transform mouse data from pygame screen coordinates to OpenGl screen coordinates
        finalMousePos, mouseDisplacement, screenInfo = mouseinfo
        finalMousePos = (
            2*(finalMousePos[0] / screenInfo[0]) - 1,
            2*(finalMousePos[1] / screenInfo[1]) - 1
        )
        mouseDisplacement = (
            2*mouseDisplacement[0] / screenInfo[0],
            2*mouseDisplacement[1] / screenInfo[1]
        )

        # Create transformation matrix using model and view matrices
        model_transform = self.faces[face].model_transform
        transformMatrix = pyrr.matrix44.multiply(
            view_transform,
            model_transform
        )

        # Transform crease points to screen coordinates
        point1Transformed = pyrr.matrix44.multiply(
            transformMatrix,
            pyrr.Vector4(self.points[point1] + (1,))
        )
        point2Transformed = pyrr.matrix44.multiply(
            transformMatrix,
            pyrr.Vector4(self.points[point2] + (1,))
        )

        # Define point for cursor to rotate around
        pivot = (
            (point1Transformed[0]+point2Transformed[0])/2,
            (point1Transformed[1]+point2Transformed[1])/2
            )
        
        # Change mouse coordinates from pygame to OpenGL
        initialCoordinate = (
            finalMousePos[0] - mouseDisplacement[0] - pivot[0],
            -(finalMousePos[1] - mouseDisplacement[1] - pivot[1])
        )
        finalCoordinate = (
            finalMousePos[0] - pivot[0],
            -(finalMousePos[1] - pivot[1])
        )

        # Calculate change in angle
        if initialCoordinate[0] == 0:
            if initialCoordinate[1] > 0:
                theta0 = math.pi/2
            else:
                theta0 = -math.pi/2
        else:
            theta0 = math.atan(initialCoordinate[1]/initialCoordinate[0])
        if initialCoordinate[0] < 0:
            theta0 += math.pi
        if finalCoordinate[0] == 0:
            if finalCoordinate[1] > 0:
                theta1 = math.pi/2
            else:
                theta1 = -math.pi/2
        else:
            theta1 = math.atan(finalCoordinate[1]/finalCoordinate[0])
        if finalCoordinate[0] < 0:
            theta1 += math.pi

        theta = theta1 - theta0
        if point1Transformed[2] > point2Transformed[2]:
            theta = 0-theta

        self.fold(point1, point2, face, theta)

        
    def split(point1, point2, face):
        pass