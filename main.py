import pygame
from OpenGL.GL import *
import numpy as np
import pyrr

from filereader import *
from foldingengine import Fold
from renderer import Renderer
from face import Face

from camera import Camera
from eventhandler import EventHandler


class App:
    def __init__(self):
        pygame.init()
        infoObject = pygame.display.Info()
        self.sw = infoObject.current_w
        self.sh = infoObject.current_h
        self.screen = pygame.display.set_mode((self.sw - 50, self.sh - 50), pygame.DOUBLEBUF | pygame.OPENGL | pygame.RESIZABLE)
        self.clock = pygame.time.Clock()

        #Constants ----------------
        self.orbit = False
        self.grab = False
        #-----------------------------
        
        glEnable(GL_DEPTH_TEST)
        glClearColor(0.1, 0.1, 0.1, 1.0)
        
        # Initialize file data
        self.shader = shader_create("vertex.txt", "fragment.txt") 
        glUseProgram(self.shader)
        # Define matrix locations
        self.modelMatrixLocation = glGetUniformLocation(self.shader, "model")
        self.modelViewLocation = glGetUniformLocation(self.shader, "view")
        self.modelProjectionLocation = glGetUniformLocation(self.shader, "projection")
        self.faceColorUniformLocation = glGetUniformLocation(self.shader, "faceColor")
        
        # Use actual window aspect ratio
        aspect_ratio = (self.sw - 50) / (self.sh - 50)
        self.projection_transform = pyrr.matrix44.create_perspective_projection(
            fovy = 45, aspect = aspect_ratio,
            near = 0.1, far = 10, dtype=np.float32
        )

        # Define projection matrix
        glUniformMatrix4fv(
            self.modelProjectionLocation,
            1, GL_FALSE, self.projection_transform
        )

        self.camera = Camera(camera_create("camera.json"))
        self.points = pl_create("points.json")
        self.facesFromFile = faces_create("faces.json")
        self.faces = {}
        for face in self.facesFromFile.keys():
            faceclass = Face(self.facesFromFile[face], self.points, self.faceColorUniformLocation)
            self.faces.update({face: faceclass})

        self.renderer = Renderer(self.points, self.faces, self.camera, self.faceColorUniformLocation, self.modelMatrixLocation)
        self.foldengine = Fold(self.faces, self.points, self.projection_transform)
        self.eventhandler = EventHandler((self.sw, self.sh), self.renderer, self.foldengine, self.projection_transform)

        self.mainloop()
    
    def mainloop(self):
        running = True
        while(running):
            for event in pygame.event.get():
                if (event.type == pygame.QUIT):
                    running = False
                elif (event.type == pygame.VIDEORESIZE):
                    # Handle window resize
                    self.sw = event.w
                    self.sh = event.h
                    glViewport(0, 0, event.w, event.h)
                    aspect_ratio = (self.sw - 50) / (self.sh - 50)
                    self.projection_transform = pyrr.matrix44.create_perspective_projection(
                        fovy = 45, aspect = aspect_ratio,
                        near = 0.1, far = 10, dtype=np.float32
                    )
                    glUniformMatrix4fv(
                        self.modelProjectionLocation,
                        1, GL_FALSE, self.projection_transform
                    )

                # Interactions
                else:
                    self.eventhandler.initializeEvents(event)

            self.camera.calculateViewMatrix(self.modelViewLocation)

            # Clear both color and depth buffers
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

            glUseProgram(self.shader)
            glEnable(GL_POLYGON_OFFSET_FILL)
            glPolygonOffset(1.0, 1.0)
            for face in self.faces.keys():
                self.renderer.drawFace(face)
            glDisable(GL_POLYGON_OFFSET_FILL)
            if self.eventhandler.grab:
                if self.eventhandler.selected is not None:
                    self.renderer.drawOutline(self.eventhandler.selected, (1, 1, 0), 3.0)
            if self.eventhandler.modes["vertexEdit"]:
                self.renderer.drawPoint("A", (0, 1, 0), "F0", 10.0)
            self.eventhandler.vertexEdit()

            pygame.display.flip()
            self.clock.tick(60)
        
        self.quit()

    def quit(self):
        for face in self.faces.values():
            face.destroy()
        glDeleteProgram(self.shader)
        pygame.quit()



if __name__ == "__main__":
    myApp = App()