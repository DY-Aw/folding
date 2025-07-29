import numpy as np
import math
import pyrr
from randomoperations import *
from face import Face

class Fold:
    def __init__(self, faces, points, projection_transform):
        self.faces = faces
        self.points = points
        self.projection_transform = projection_transform

    def fold(self, point1, point2, face, angle):
        p1x, p1y, p1z = self.points[point1]
        p2x, p2y, p2z = self.points[point2]

        model = self.faces[face].model_transform
        p1Transformed = pyrr.matrix44.apply_to_vector(
            model,
            pyrr.vector4.create(p1x, p1y, p1z, 1.0)
        )
        p2Transformed = pyrr.matrix44.apply_to_vector(
            model,
            pyrr.vector4.create(p2x, p2y, p2z, 1.0)
        )
        p1x, p1y, p1z = p1Transformed[0], p1Transformed[1], p1Transformed[2]
        p2x, p2y, p2z = p2Transformed[0], p2Transformed[1], p2Transformed[2]

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
        finalMousePos = convertToOpenGLCoordinates(finalMousePos, screenInfo)
        initialMousePos = convertToOpenGLCoordinates(initialMousePos, screenInfo)
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
        point1Transformed = pyrr.matrix44.apply_to_vector(
            transformMatrix,
            pyrr.Vector4(np.append(self.points[point1], 1.0))
        )
        point2Transformed = pyrr.matrix44.apply_to_vector(
            transformMatrix,
            pyrr.Vector4(np.append(self.points[point2], 1.0))
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

        
    def split(self, point1, point2, line1, line2, face):
        oldface = self.faces[face]
        pointIDs = list(self.points.keys())
        pointIDs.sort(key=AlphaID)
        p1ID = nextLetterInSequence(pointIDs[-1], True)
        p2ID = nextLetterInSequence(p1ID, True)
        self.points.update({p1ID: point1})
        self.points.update({p2ID: point2})

        # Set up vertex data for old and new faces
        vertex = line1[0]
        startIndex = oldface.vertices.index(vertex)
        list_length = len(oldface.vertices)
        if oldface.vertices[(startIndex+1)%list_length] == line1[1]:
            vertex = line1[1]
            startIndex = (startIndex+1)%list_length
        firstFaceVertices = [p2ID, p1ID, vertex]
        secondFaceVertices = [p1ID, p2ID]
        index = startIndex
        while oldface.vertices[index] not in line2:
            index = (index+1)%list_length
            firstFaceVertices.append(oldface.vertices[index])
        index = (index+1)%list_length
        while index != startIndex:
            secondFaceVertices.append(oldface.vertices[index])
            index = (index+1)%list_length
        
        face_data1 = {
            'vertices': firstFaceVertices
        }
        face_data2 = {
            'vertices': secondFaceVertices
        }
        model_transform = oldface.model_transform
        faceColorUniformLocation = oldface.faceColorUniformLocation

        self.faces[face] = Face(face_data1, self.points, faceColorUniformLocation, model_transform)

        faceIDs = list(self.faces.keys())
        faceIDs.sort(key=FaceID)
        self.faces.update({nextFaceInSequence(faceIDs[-1]): Face(face_data2, self.points, faceColorUniformLocation, model_transform)})

        
        