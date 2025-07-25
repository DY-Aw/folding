import numpy as np
import math
import pyrr
from randomoperations import *

class Fold:
    def __init__(self, faces, points, projection_transform):
        self.faces = faces
        self.points = points
        self.projection_transform = projection_transform

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

        self.faces[face].updateModelMatrix(pyrr.matrix44.multiply(pyrr.matrix44.multiply(toOrigin, rotationMatrix), fromOrigin))

    def foldGrab(self, point1, point2, face, mouseinfo, view_transform):
        # Transform mouse data from pygame screen coordinates to OpenGl screen coordinates
        finalMousePos, mouseDisplacement, screenInfo = mouseinfo
        initialMousePos = (
            finalMousePos[0] - mouseDisplacement[0],
            finalMousePos[1] - mouseDisplacement[1]
        )
        finalMousePos = convertToOpenGLCoordinates(finalMousePos[0], finalMousePos[1], screenInfo[0], screenInfo[1])
        initialMousePos = convertToOpenGLCoordinates(initialMousePos[0], initialMousePos[1], screenInfo[0], screenInfo[1])
        # Create transformation matrix using model and view matrices
        model_transform = self.faces[face].model_transform
        transformMatrix = pyrr.matrix44.multiply(
            pyrr.matrix44.multiply(
                model_transform,
                view_transform
            ),
            self.projection_transform
        )

        # Transform crease points to screen coordinates
        point1Transformed = pyrr.matrix44.multiply(
            pyrr.Vector4(np.append(self.points[point1], 1.0)),
            transformMatrix
        )
        point2Transformed = pyrr.matrix44.multiply(
            pyrr.Vector4(np.append(self.points[point2], 1.0)),
            transformMatrix
        )

        ndcP1 = point1Transformed / point1Transformed[3]
        ndcP2 = point2Transformed / point2Transformed[3]

        # Define point for cursor to rotate around
        pivot = (
            (ndcP1[0]+ndcP2[0])/2,
            (ndcP1[1]+ndcP2[1])/2
        )
        
        initialCoordinate = (
            initialMousePos[0] - pivot[0],
            initialMousePos[1] - pivot[1]
        )
        finalCoordinate = (
            finalMousePos[0] - pivot[0],
            finalMousePos[1] - pivot[1]
        )

        # Calculate change in angle
        theta0 = math.atan2(initialCoordinate[1], initialCoordinate[0])
        theta1 = math.atan2(finalCoordinate[1], finalCoordinate[0])

        theta = theta1 - theta0
        if point1Transformed[2] < point2Transformed[2]:
            theta = 0-theta

        self.fold(point1, point2, face, theta)

        
    def split(point1, point2, face):
        pass