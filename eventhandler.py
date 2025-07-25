import pygame
import pyrr
import math
import numpy as np

class EventHandler:
    def __init__(self, screeninfo, renderer, foldengine, projection_transform):
        self.sw, self.sh = screeninfo
        self.renderer = renderer
        self.foldengine = foldengine
        self.projection_transform = projection_transform
        self.camera = self.renderer.camera
        self.points = self.renderer.points
        self.faces = self.renderer.faces

        self.grab = False
        self.orbit = False
        self.selected = None
        self.orbitsens = 0.01
        
        self.modes = {
            "vertexEdit": False
        }

    def initializeEvents(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                selected = "F1"
                if selected != None:
                    self.grab = True
            if event.button == 2:
                self.orbit = True
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.grab = False
            if event.button == 2:
                self.orbit = False
        elif event.type == pygame.MOUSEMOTION:
            if self.orbit:
                self.camera.orbit(event.rel[0] * self.orbitsens, -event.rel[1] * self.orbitsens)
            elif self.grab:
                self.selected = "F0"
                self.foldengine.foldGrab("E", "F", self.selected, (pygame.mouse.get_pos(), event.rel, (self.sw, self.sh)), (self.camera.view_transform))
    
        # Scroll zoom
        elif event.type == pygame.MOUSEWHEEL:
            scrollsens = 0.1
            self.camera._zoom(-event.y * scrollsens)

        # Letter keys
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_ESCAPE:
                for mode in self.modes.keys():
                    self.modes[mode] = False
            if event.key == pygame.K_v:
                self.swapMode("vertexEdit")
    
    def swapMode(self, mode):
        # Exits every mode and swaps to/from the desired mode
        enabled = self.modes[mode]
        for mode in self.modes.keys():
            self.modes[mode] = False
        if not enabled:
            self.modes[mode] = True

    def vertexEdit(self):
        if self.modes["vertexEdit"]:
            mouseX, mouseY = pygame.mouse.get_pos()
            closestLine = None
            points = {}
            lines = {}
            for faceID, face in self.faces.items():
                face = self.faces[faceID]
                model_transform = face.model_transform
                screenCoordinateTransformer = pyrr.matrix44.multiply(
                    self.projection_transform,
                    pyrr.matrix44.multiply(
                        self.camera.view_transform,
                        model_transform
                    )
                )
                for vertex in face.vertices:
                    if vertex not in points.keys():
                        transformedpoint = pyrr.matrix44.multiply(
                            screenCoordinateTransformer,
                            pyrr.Vector4(self.points[vertex]+(1,))
                        )
                        #transformedpoint = transformedpoint / transformedpoint[3]
                        points.update({vertex: self.convertToPygameCoordinates(
                            transformedpoint[0],
                            transformedpoint[1]
                        )})
                for vID in range(len(face.vertices)):
                    lineID = tuple(set({face.vertices[vID-1], face.vertices[vID]}))
                    if lineID not in lines.keys():
                        lines.update({lineID: faceID})
            for line, face in lines.items():
                a, b = line
                ax, ay = points[a]
                bx, by = points[b]

                bx -= ax
                by -= ay
                mx = mouseX - ax
                my = mouseY - ay
                
                theta = -math.atan2(by, bx)
                upperbound = bx * math.cos(theta) - by * math.sin(theta)

                m_x = mx * math.cos(theta) - my * math.sin(theta)
                m_y = mx * math.sin(theta) + my * math.cos(theta)

                if m_x < 0 or m_x > upperbound:
                    continue
                if abs(m_y) > 5:
                    continue
                if closestLine == None:
                    closestLine = (line, face, m_y)
                elif m_y < closestLine[2]:
                    closestLine = (line, face, m_y)
            if closestLine != None:
                self.renderer.drawLine(tuple(closestLine[0]), (1, 1, 0), closestLine[1], 3.0)
            #print(points["A"], points["B"], mouseX, mouseY)
            print(self.convertToOpenGLCoordinates(mouseX, mouseY))
            print(self.sw, self.sh)




    def convertToOpenGLCoordinates(self, x, y):
        fx = 2*x / self.sw - 1
        fy = 2*y / self.sh - 1
        return fx, -fy
    
    def convertToPygameCoordinates(self, x, y):
        fx = (x+1) * self.sw / 2
        fy = (-y+1) * self.sh / 2
        return fx, fy
    
