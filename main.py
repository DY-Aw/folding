import pygame
from OpenGL.GL import *
import numpy as np
import pyrr

from filereader import *
from facehandler import FaceHandler
from foldingengine import Fold


class App:
    def __init__(self):
        pygame.init()
        infoObject = pygame.display.Info()
        window_width = infoObject.current_w
        window_height = infoObject.current_h
        self.screen = pygame.display.set_mode((window_width - 50, window_height - 50), pygame.DOUBLEBUF | pygame.OPENGL | pygame.RESIZABLE)
        self.clock = pygame.time.Clock()
        
        glEnable(GL_DEPTH_TEST)
        glClearColor(0.1, 0.1, 0.1, 1.0)
        
        self.shader = shader_create("vertex.txt", "fragment.txt") 
        glUseProgram(self.shader)

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

        glUniformMatrix4fv(
            glGetUniformLocation(self.shader, "projection"),
            1, GL_FALSE, projection_transform
        )

        self.modelMatrixLocation = glGetUniformLocation(self.shader, "model")

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
            for face in self.facehandler.faces.values():
                face.eulers[0] +=0.2
                face.eulers[1] +=0.1
                face.eulers[2] += 0.1
            
            self.foldengine.fold("E", "F", "F0", 1)

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