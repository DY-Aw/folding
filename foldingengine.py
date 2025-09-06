import numpy as np
import math
from pyglm import glm
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
        p1Transformed = model * glm.vec4(p1x, p1y, p1z, 1.0)
        p2Transformed = model * glm.vec4(p2x, p2y, p2z, 1.0)
        p1x, p1y, p1z = p1Transformed[0], p1Transformed[1], p1Transformed[2]
        p2x, p2y, p2z = p2Transformed[0], p2Transformed[1], p2Transformed[2]

        # Translation matrices
        toOrigin = glm.translate(glm.mat4(1.0), glm.vec3(-p1x, -p1y, -p1z))
        fromOrigin = glm.inverse(toOrigin)

        # Rotation matrix
        rotationMatrix = glm.rotate(glm.mat4(1.0), angle, glm.normalize(glm.vec3(p2x-p1x, p2y-p1y, p2z-p1z)))

        self.faces[face].updateModelMatrix(fromOrigin * rotationMatrix * toOrigin)

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
        transformMatrix = self.projection_transform * view_transform * model_transform

        # Transform crease points to screen coordinates
        point1Transformed = transformMatrix * glm.vec4(*self.points[point1], 1.0)
        point2Transformed = transformMatrix * glm.vec4(*self.points[point2], 1.0)

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
        for faceID, edge in self.faces[face].connections.items():
                self.grabEdge(faceID, tuple(edge), self.faces[face].model_transform)

        
    def splitBetweenPoints(self, point1, point2, face):
        translationmatrix = create2dTranslationMatrix(-point1[0], -point1[2])
        rotationmatrix = create2dRotationMatrix(-math.atan2(point2[2]-point1[2],point2[0]-point1[0]))
        transformation = rotationmatrix @ translationmatrix
        pointsTransformed = {}
        for vertex in self.faces[face].vertices:
            pointsTransformed.update({
                vertex: (transformation @ (self.points[vertex][0], self.points[vertex][2], 1.0))
            })
        face1Vertices = []
        face2Vertices = []
        for i, vertex in enumerate(self.faces[face].vertices):
            previousvertex = self.faces[face].vertices[i-1]
            currentvertex = self.faces[face].vertices[i]
            if np.sign(pointsTransformed[currentvertex][1]) != np.sign(pointsTransformed[previousvertex][1]):
                if pointsTransformed[currentvertex][1] != 0 and pointsTransformed[previousvertex][1] != 0:
                    p1 = pointsTransformed[previousvertex]
                    p2 = pointsTransformed[currentvertex]
                    try:
                        xint = (p2[1]*p1[0]-p1[1]*p2[0])/(p2[1]-p1[1])
                    except:
                        print(f'p1: {p1}, p2: {p2}. Division by zero')
                    newpoint = glm.inverse(transformation) * glm.vec3(xint, 0.0, 1.0)
                    newpointID = createPoint(self.points, (newpoint[0], 0, newpoint[1]))
                    face1Vertices.append(newpointID)
                    face2Vertices.append(newpointID)
            if pointsTransformed[currentvertex][1] > 0:
                face1Vertices.append(currentvertex)
            elif pointsTransformed[currentvertex][1] < 0:
                face2Vertices.append(currentvertex)
            elif pointsTransformed[currentvertex][1] == 0:
                face1Vertices.append(currentvertex)
                face2Vertices.append(currentvertex)
        face_data1 = {
            'vertices': face1Vertices
        }
        face_data2 = {
            'vertices': face2Vertices
        }
        model_transform = self.faces[face].model_transform
        faceColorUniformLocation = self.faces[face].faceColorUniformLocation
        self.faces[face] = Face(face_data1, self.points, faceColorUniformLocation, model_transform)
        faceIDs = list(self.faces.keys())
        faceIDs.sort(key=FaceID)
        self.faces.update({nextFaceInSequence(faceIDs[-1]): Face(face_data2, self.points, faceColorUniformLocation, model_transform)})


    def splitBetweenEdges(self, line1, line2, face):
        p11, p12 = self.points[line1[0]], self.points[line1[1]]
        p21, p22 = self.points[line2[0]], self.points[line2[1]]

        _int = findIntersection(
            (p11[0], p11[2]),
            (p12[0], p12[2]),
            (p21[0], p21[2]),
            (p22[0], p22[2])
        )
        if _int is not None:
            xint, yint = _int
            translationmatrix = create2dTranslationMatrix(-xint, -yint)
            l1translated = translationmatrix * glm.vec3((p11[0]+p12[0])/2, (p11[2]+p12[2])/2, 1.0)
            l2translated = translationmatrix * glm.vec3((p21[0]+p22[0])/2, (p21[2]+p22[2])/2, 1.0)
            a1 = math.atan2(l1translated[1], l1translated[0])
            a2 = math.atan2(l2translated[1], l2translated[0])
            v1 = glm.vec2(math.cos(a1), math.sin(a1))
            v2 = glm.vec2(math.cos(a2), math.sin(a2))
            vsum = glm.normalize(v1 + v2)
            theta = math.atan2(vsum[1], vsum[0])
            rotationmatrix = create2dRotationMatrix(0-theta)
        
        else:
            # Parallel
            if p11[0] != p12[0]:
                int1 = findIntersection(
                    (p11[0], p11[2]),
                    (p12[0], p12[2]),
                    (0, 0),
                    (0, 1)
                )
                int2 = findIntersection(
                    (p21[0], p21[2]),
                    (p22[0], p22[2]),
                    (0, 0),
                    (0, 1)
                )
                translationmatrix = create2dTranslationMatrix(0, -(int1[1]+int2[1])/2)
            else:
                int1 = findIntersection(
                    (p11[0], p11[2]),
                    (p12[0], p12[2]),
                    (0, 0),
                    (1, 0)
                )
                int2 = findIntersection(
                    (p21[0], p21[2]),
                    (p22[0], p22[2]),
                    (0, 0),
                    (1, 0)
                )
                translationmatrix = create2dTranslationMatrix(-(int1[0]+int2[0])/2, 0)
            rotationmatrix = create2dRotationMatrix(-math.atan2(p12[2]-p11[2], p12[0]-p11[0]))

        transformation = rotationmatrix * translationmatrix

        pointsTransformed = {}
        for vertex in self.faces[face].vertices:
            pointsTransformed.update({
                vertex: (transformation * glm.vec3(self.points[vertex][0], self.points[vertex][2], 1.0))
            })
        face1Vertices = []
        face2Vertices = []
        for i, vertex in enumerate(self.faces[face].vertices):
            previousvertex = self.faces[face].vertices[i-1]
            currentvertex = self.faces[face].vertices[i]
            if np.sign(pointsTransformed[currentvertex][1]) != np.sign(pointsTransformed[previousvertex][1]):
                if pointsTransformed[currentvertex][1] != 0 and pointsTransformed[previousvertex][1] != 0:
                    p1 = pointsTransformed[previousvertex]
                    p2 = pointsTransformed[currentvertex]
                    try:
                        xint = (p2[1]*p1[0]-p1[1]*p2[0])/(p2[1]-p1[1])
                    except:
                        print(f'p1: {p1}, p2: {p2}. Division by zero')
                    newpoint =  glm.inverse(transformation) * glm.vec3(xint, 0.0, 1.0)
                    newpointID = createPoint(self.points, (newpoint[0], 0, newpoint[1]))
                    face1Vertices.append(newpointID)
                    face2Vertices.append(newpointID)
            if pointsTransformed[currentvertex][1] > 0:
                face1Vertices.append(currentvertex)
            elif pointsTransformed[currentvertex][1] < 0:
                face2Vertices.append(currentvertex)
            elif pointsTransformed[currentvertex][1] == 0:
                face1Vertices.append(currentvertex)
                face2Vertices.append(currentvertex)
        faceIDs = list(self.faces.keys())
        faceIDs.sort(key=FaceID)
        newfaceID = nextFaceInSequence(faceIDs[-1])
        sharedVertices = self.findConnections(face1Vertices, face2Vertices)
        face1Connections = {newfaceID: sharedVertices}
        face2Connections = {face: sharedVertices}
        for connection, sharededge in self.faces[face].connections.items():
            a, b = sharededge
            if a in face1Vertices and b in face1Vertices:
                face1Connections[connection] = sharededge
            if a in face2Vertices and b in face2Vertices:
                face2Connections[connection] = sharededge
        face_data1 = {
            'vertices': face1Vertices,
            'connections': face1Connections
        }
        face_data2 = {
            'vertices': face2Vertices,
            'connections': face2Connections
        }
        model_transform = self.faces[face].model_transform
        faceColorUniformLocation = self.faces[face].faceColorUniformLocation
        self.faces[face] = Face(face_data1, self.points, faceColorUniformLocation, model_transform)
        self.faces.update({newfaceID: Face(face_data2, self.points, faceColorUniformLocation, model_transform)})
    
    def findConnections(self, face1Vertices, face2Vertices):
        sharedVertices = []
        for vertex in face1Vertices:
            if vertex in face2Vertices:
                sharedVertices.append(vertex)
        if len(sharedVertices) == 2:
            return tuple(sharedVertices)
        return None
            


    def grabEdge(self, face, edge, final_model_transform):
        point1, point2 = edge
        point1Local = self.points[point1]
        point2Local = self.points[point2]
        point1WorldFinal = final_model_transform * glm.vec4(*point1Local, 1.0)
        point2WorldFinal = final_model_transform * glm.vec4(*point2Local, 1.0)
        point1WorldInitial = self.faces[face].model_transform * glm.vec4(*point1Local, 1.0)
        point2WorldInitial = self.faces[face].model_transform * glm.vec4(*point2Local, 1.0)

        if glm.length(point2WorldFinal - point2WorldInitial) < glm.length(point1WorldFinal - point1WorldInitial):
            point1WorldInitial, point2WorldInitial = point2WorldInitial, point1WorldInitial
            point1WorldFinal, point2WorldFinal = point2WorldFinal, point1WorldFinal
        
        # Translation matrix
        translateTo = glm.translate(glm.mat4(1.0), glm.vec3(-point1WorldInitial))
        translateFrom = glm.inverse(translateTo)

        # Rotation matrix
        p1WFatOrigin = glm.normalize(glm.vec3(point2WorldInitial - point1WorldInitial))
        p2WFatOrigin = glm.normalize(glm.vec3(point2WorldFinal - point1WorldFinal))

        dotproduct = glm.dot(p1WFatOrigin, p2WFatOrigin)
        if dotproduct > 1:
            dotproduct = 1
        if dotproduct < -1:
            dotproduct = -1

        theta = math.acos(dotproduct)
        k = glm.cross(p1WFatOrigin, p2WFatOrigin)
        if np.all(np.isclose(k, 0.0)):
            rotationMatrix = glm.mat4(1.0)
        else:
            k = glm.normalize(k)
            matk = glm.mat3(
                0, k[2], -k[1],
                -k[2], 0, k[0],
                k[1], -k[0], 0
            )
            rotationMatrix = glm.mat3(1.0) + math.sin(theta) * matk + (1 - math.cos(theta)) * matk * matk
            rotationMatrix = glm.mat4(rotationMatrix)
        transformation = translateFrom * rotationMatrix * translateTo
        self.faces[face].model_transform = transformation * self.faces[face].model_transform