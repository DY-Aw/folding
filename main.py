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
        window_width = infoObject.current_w
        window_height = infoObject.current_h
        self.screen = pygame.display.set_mode((window_width - 50, window_height - 50), pygame.DOUBLEBUF | pygame.OPENGL | pygame.RESIZABLE)
        self.clock = pygame.time.Clock()
        self.buttondown = False
        
        glEnable(GL_DEPTH_TEST)
        glClearColor(0.1, 0.1, 0.1, 1.0)
        
        self.shader = shader_create("vertex.txt", "fragment.txt") 
        glUseProgram(self.shader)

        self.camera = Camera(camera_create("camera.json"))

        self.points = pl_create("points.json")
        self.faces = faces_create("faces.json")
        self.facehandler = FaceHandler(self.points)

        for face in self.faces.keys():
            self.facehandler.update(face, self.faces[face])

        self.foldengine = Fold(self.facehandler, self.points)

        # Use actual window aspect ratio
        aspect_ratio = (window_width - 50) / (window_height - 50)
        projection_transform = pyrr.matrix44.create_perspective_projection(
            fovy = 45, aspect = aspect_ratio,
            near = 0.1, far = 10, dtype=np.float32
        )

        # Define projection matrix
        glUniformMatrix4fv(
            glGetUniformLocation(self.shader, "projection"),
            1, GL_FALSE, projection_transform
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

                # Mouse orbit
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 2:
                        self.buttondown = True
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 2:
                        self.buttondown = False
                elif event.type == pygame.MOUSEMOTION:
                    if self.buttondown:
                        sensitivity = 0.01
                        self.camera.orbit(event.rel[0] * sensitivity, event.rel[1] * sensitivity)
                
                # Scroll zoom
                elif event.type == pygame.MOUSEWHEEL:
                    scrollsens = 0.1
                    self.camera._zoom(-event.y * scrollsens)
            
            self.foldengine.fold("E", "F", "F0", 1)

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