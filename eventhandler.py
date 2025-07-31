import pygame
from randomoperations import *

class EventHandler:
    def __init__(self, screeninfo, renderer, foldengine, projection_transform):
        self.sw, self.sh = screeninfo
        self.renderer = renderer
        self.foldengine = foldengine
        self.projection_transform = projection_transform
        self.camera = self.renderer.camera
        self.points = self.renderer.points
        self.faces = self.renderer.faces

        self.RIGHTDOWN = False
        self.SHIFTDOWN = False
        self.grab = False
        self.orbit = False
        self.selecteditems = {'faces': [], 'lines': {}, 'points': {}}
        self.orbitsens = 0.01
        self.hoveredLine = None
        self.hoveredPoint = None
        self.hoveredFace = None
        self.newvertices = []
        
        self.modes = {
            "vertexEdit": False,
            "lineSelect": False,
            "folding": False,
            "faceSelect": False
        }
        self.previousMode = None

    def initializeEvents(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if self.hoveredLine != None:
                    if self.hoveredLine[0] not in self.selecteditems['lines'].keys():
                        if not self.SHIFTDOWN:
                            self.selecteditems['lines'] = {}
                        self.selecteditems['lines'].update({self.hoveredLine[0]: self.hoveredLine[1]})
                    else:
                        del self.selecteditems['lines'][self.hoveredLine[0]]
                    self.hoveredLine = None
                elif self.modes['lineSelect']:
                    self.selecteditems['lines'] = {}
                if self.hoveredPoint != None:
                    self.selecteditems['points'].update({self.hoveredPoint[0]: self.hoveredPoint[1]})
                    self.selecteditems['lines'] = {}
                    self.newvertices.append(self.hoveredPoint)
                    self.hoveredPoint = None
                if self.hoveredFace != None:                  
                    if self.hoveredFace not in self.selecteditems['faces']:
                        if not self.SHIFTDOWN:
                            self.selecteditems['faces'] = []
                        self.selecteditems['faces'].append(self.hoveredFace)
                    else:
                        self.selecteditems['faces'] = []
                    self.hoveredFace = None
                elif self.modes['faceSelect']:
                    self.selecteditems['faces'] = []

            if event.button == 2:
                self.orbit = True
            if event.button == 3:
                self.RIGHTDOWN = True
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.grab = False
            if event.button == 2:
                self.orbit = False
            if event.button == 3:
                self.RIGHTDOWN = False
        elif event.type == pygame.MOUSEMOTION:
            if self.orbit:
                self.camera.orbit(event.rel[0] * self.orbitsens, -event.rel[1] * self.orbitsens)
            elif self.grab and self.RIGHTDOWN:
                p1, p2, grabbedfaces = self.grabbed
                for grabbedface in grabbedfaces:
                    self.foldengine.foldGrab(p1, p2, grabbedface, (pygame.mouse.get_pos(), event.rel, (self.sw, self.sh)), (self.camera.view_transform))
    
        # Scroll zoom
        elif event.type == pygame.MOUSEWHEEL:
            scrollsens = 0.1
            self.camera._zoom(-event.y * scrollsens)

        # Letter keys
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                for mode in self.modes.keys():
                    self.modes[mode] = False
                if self.previousMode != None:
                    self.modes[self.previousMode] = True
            if event.key == pygame.K_v:
                self.swapMode("vertexEdit")
                print("s", self.modes)
            if event.key == pygame.K_q:
                self.swapMode("lineSelect", True)
                print("q", self.modes)
            if event.key == pygame.K_x:
                self.splitVertices()
                self.splitLines()
            if event.key == pygame.K_f:
                self.swapMode("folding")
            if event.key == pygame.K_w:
                self.swapMode("faceSelect", True)

            if event.key == pygame.K_LSHIFT:
                self.SHIFTDOWN = True
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_LSHIFT:
                self.SHIFTDOWN = False
    
    def swapMode(self, mode, saveprevious = False):
        # Exits every mode and swaps to/from the desired mode
        enabled = self.modes[mode]
        for _mode in self.modes.keys():
            if self.modes[_mode] == True:
                self.previousMode = _mode
            self.modes[_mode] = False
        if not enabled:
            self.modes[mode] = True
        if not saveprevious:
            self.previousMode = None

    def lineSelect(self):
        self.hoveredLine = None
        if self.modes["lineSelect"]:
            points = {}
            lines = {}
            closestLine = None
            for faceID, face in self.faces.items():
                face = self.faces[faceID]
                model_transform = face.model_transform
                for vertex in face.vertices:
                    if vertex not in points.keys():
                        transformedpoint = getScreenCoordinates(
                            self.points[vertex],
                            model_transform,
                            self.camera.view_transform,
                            self.projection_transform
                        )
                        points.update({vertex: convertToPygameCoordinates(
                            (transformedpoint[0], transformedpoint[1]),
                            (self.sw, self.sh)
                        )})
                for vID in range(len(face.vertices)):
                    lineID = tuple(set({face.vertices[vID-1], face.vertices[vID]}))
                    if lineID not in lines.keys():
                        lines.update({lineID: faceID})
            for line, face in lines.items():
                try:
                    a, b = line
                except:
                    print(lines)
                    raise("something went wrong")
                rightbound, m_x, m_y = mouseToLine(points[a], points[b], pygame.mouse.get_pos())
                if m_x < 0 or m_x > rightbound:
                    continue
                if abs(m_y) > 10:
                    continue
                if closestLine == None:
                    closestLine = (line, face, m_y)
                elif m_y < closestLine[2]:
                    closestLine = (line, face, m_y)

            if closestLine != None:
                self.renderer.drawLine(tuple(closestLine[0]), (0, 1, 0), closestLine[1], 3.0)
                self.hoveredLine = (closestLine[0], closestLine[1])

    def vertexEdit(self):
        if self.modes['vertexEdit']:
            if self.selecteditems['lines'] != {}:
                for asd in self.selecteditems['lines'].keys():
                    line = asd
                face = self.selecteditems['lines'][line]
                model = self.faces[face].model_transform
                view = self.camera.view_transform
                projection = self.projection_transform
                p1, p2 = self.points[line[0]], self.points[line[1]]
                point1 = convertToPygameCoordinates(
                    getScreenCoordinates(p1, model, view, projection),
                    (self.sw, self.sh)
                )
                point2 = convertToPygameCoordinates(
                    getScreenCoordinates(p2, model, view, projection),
                    (self.sw, self.sh)
                )
                b, m_x, m_y = mouseToLine(point1, point2, pygame.mouse.get_pos())
                if m_x > 0 and m_x < b:
                    ratio = m_x/b
                elif m_x <= 0:
                    ratio = 0
                elif m_x >= b:
                    ratio = 1
                tempPoint = []
                for i in range(3):
                    tempPoint.append(p1[i] + ratio * (p2[i] - p1[i]))
                tempPoint = tuple(tempPoint)
                self.renderer.drawPoint(tempPoint, (0, 0, 0), face, 10.0)
                self.hoveredPoint = (tempPoint, face, list(line))
        else:
            self.hoveredPoint = None
    
    def splitVertices(self):
        if len(self.newvertices) == 2 and len(self.selecteditems['faces']) > 0:
            if set(self.newvertices[0][2]) != set(self.newvertices[1][2]):
                for face in self.selecteditems['faces']:
                    self.foldengine.splitBetweenPoints(
                        self.newvertices[0][0],
                        self.newvertices[1][0],
                        self.newvertices[0][2],
                        self.newvertices[1][2],
                        face
                    )
        self.newvertices = []
        self.selecteditems['points'] = {}

    def splitLines(self):
        lines = list(self.selecteditems['lines'])
        if len(lines) == 2 and len(self.selecteditems['faces']) > 0:
            line1 = lines[0]
            line2 = lines[1]
            for face in self.selecteditems['faces']:
                self.foldengine.splitBetweenEdges(line1, line2, face)
    
    def faceSelect(self):
        self.hoveredFace = None
        if self.modes["faceSelect"]:
            rayOrigin, rayDirection = mouseToRay((self.sw, self.sh), self.projection_transform, self.camera.view_transform)
            min_t = None
            for id, face in self.faces.items():
                face_t = None
                model = face.model_transform
                for i in range(len(list(face.triangles))//9):
                    j = 9 * i
                    vert1 = pyrr.vector4.create(face.triangles[j], face.triangles[j+1], face.triangles[j+2], 1.0)
                    vert2 = pyrr.vector4.create(face.triangles[j+3], face.triangles[j+4], face.triangles[j+5], 1.0)
                    vert3 = pyrr.vector4.create(face.triangles[j+6], face.triangles[j+7], face.triangles[j+8], 1.0)

                    v1 = pyrr.matrix44.apply_to_vector(model, vert1)
                    v2 = pyrr.matrix44.apply_to_vector(model, vert2)
                    v3 = pyrr.matrix44.apply_to_vector(model, vert3)
                    v1 = v1 / v1[3]
                    v2 = v2 / v2[3]
                    v3 = v3 / v3[3]

                    intersect = triangleIntersect(
                        rayOrigin, rayDirection,
                        pyrr.vector3.create(v1[0], v1[1], v1[2]),
                        pyrr.vector3.create(v2[0], v2[1], v2[2]),
                        pyrr.vector3.create(v3[0], v3[1], v3[2])
                    )
                    if intersect is not None:
                        face_t = intersect[0] if intersect[0] > 0 else None
                if face_t is not None:
                    if min_t is None:
                        min_t = (face_t, id)
                    elif face_t < min_t[0]:
                        min_t = (face_t, id)
            if min_t is not None:
                self.renderer.drawOutline(min_t[1], (0, 1, 0), width=3.0)
                self.hoveredFace = min_t[1]
        else:
            self.hoveredFace = None

    
    def folding(self):
        if self.modes['folding']:
            if self.selecteditems['faces']:
                lineslist = list(self.selecteditems['lines'].keys())
                if len(lineslist) == 1:
                    p1, p2 = lineslist[0]
                    grabbedface = self.selecteditems['faces']
                    self.grabbed = (p1, p2, grabbedface)
                    self.grab = True
                else:
                    self.grab = False
            else:
                self.grab = False
        else:
            self.grab = False

    def drawSelected(self):
        for face in self.selecteditems['faces']:
            self.renderer.drawOutline(face, (1, 1, 0), 3.0)
        for line, face in self.selecteditems['lines'].items():
            self.renderer.drawLine(line, (1, 1, 0), face, 3.0)
        for point, face in self.selecteditems['points'].items():
            self.renderer.drawPoint(point, (1, 1.0, 0), face, 10.0)
