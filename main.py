import pygame
from OpenGL.GL import *
import numpy as np
import pyrr

from filereader import *
from facehandler import FaceHandler
from foldingengine import Fold

from camera import Camera


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

        self.orbitsens = 0.01
        #-----------------------------


        
        glEnable(GL_DEPTH_TEST)
        glClearColor(0.1, 0.1, 0.1, 1.0)
        
        self.shader = shader_create("vertex.txt", "fragment.txt") 
        glUseProgram(self.shader)

        self.camera = Camera(camera_create("camera.json"))

        self.points = pl_create("points.json")
        self.faces = faces_create("faces.json")

        self.face_color_uniform_location = glGetUniformLocation(self.shader, "faceColor")
        self.facehandler = FaceHandler(self.points, self.face_color_uniform_location, self.camera)

        for face in self.faces.keys():
            self.facehandler.update(face, self.faces[face])

        self.foldengine = Fold(self.facehandler, self.points)

        # Use actual window aspect ratio
        aspect_ratio = (self.sw - 50) / (self.sh - 50)
        self.projection_transform = pyrr.matrix44.create_perspective_projection(
            fovy = 45, aspect = aspect_ratio,
            near = 0.1, far = 10, dtype=np.float32
        )

        # Define projection matrix
        glUniformMatrix4fv(
            glGetUniformLocation(self.shader, "projection"),
            1, GL_FALSE, self.projection_transform
        )

        self.modelMatrixLocation = glGetUniformLocation(self.shader, "model")
        self.modelViewLocation = glGetUniformLocation(self.shader, "view")

        self.mainloop()
    
    def mainloop(self):
        running = True
        while(running):
            for event in pygame.event.get():
                if (event.type == pygame.QUIT):
                    running = False
                elif (event.type == pygame.VIDEORESIZE):
                    # Handle window resize
                    glViewport(0, 0, event.w, event.h)

                # Mouse
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.grab = True
                    if event.button == 2:
                        self.orbit = True
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.grab = False
                    if event.button == 2:
                        self.orbit = False
                elif event.type == pygame.MOUSEMOTION:
                    if self.grab:
                        #self.foldengine.fold("E", "F", "F0", event.rel[0] * self.grabsens)
                        self.foldengine.foldGrab("E", "F", "F0", (pygame.mouse.get_pos(), event.rel, (self.sw, self.sh)), (self.camera.view_transform))
                    if self.orbit:
                        self.camera.orbit(event.rel[0] * self.orbitsens, -event.rel[1] * self.orbitsens)
                
                # Scroll zoom
                elif event.type == pygame.MOUSEWHEEL:
                    scrollsens = 0.1
                    self.camera._zoom(-event.y * scrollsens)

            self.camera.calculateViewMatrix(self.modelViewLocation)

            # Clear both color and depth buffers
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

            glUseProgram(self.shader)
            self.facehandler.drawfaces(self.modelMatrixLocation)
            
            pygame.display.flip()
            self.clock.tick(60)
        
        self.quit()

    def quit(self):
        self.facehandler.destroy()
        glDeleteProgram(self.shader)
        pygame.quit()



if __name__ == "__main__":
    myApp = App()