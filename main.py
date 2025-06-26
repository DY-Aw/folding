import pygame
from OpenGL.GL import *
import numpy as np
import ctypes
import pyrr

from filereader import *


class Cube:
    def __init__(self, position, eulers):
        self.position = np.array(position, dtype=np.float32)
        self.eulers = np.array(eulers, dtype=np.float32)


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
        
        self.cube = Cube(
            position = [0, 0, -3],
            eulers = [0, 0, 0]
        )

        self.cube_mesh = CubeMesh()

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

            # Update cube - rotate on multiple axes for better visibility
            self.cube.eulers[0] += 0.5  # X rotation
            self.cube.eulers[1] += 0.3  # Y rotation
            self.cube.eulers[2] += 0.2  # Z rotation
            
            # Keep angles in reasonable range
            for i in range(3):
                if self.cube.eulers[i] > 360:
                    self.cube.eulers[i] -= 360
            
            # Clear both color and depth buffers
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

            glUseProgram(self.shader)

            # Create model transformation matrix
            model_transform = pyrr.matrix44.create_identity(dtype=np.float32)
            
            # Apply rotation
            model_transform = pyrr.matrix44.multiply(
                m1 = model_transform,
                m2 = pyrr.matrix44.create_from_eulers(
                    eulers = np.radians(self.cube.eulers),
                    dtype = np.float32
                )
            )
            
            # Apply translation
            model_transform = pyrr.matrix44.multiply(
                m1 = model_transform,
                m2 = pyrr.matrix44.create_from_translation(
                    vec = self.cube.position,
                    dtype = np.float32
                )
            )

            glUniformMatrix4fv(self.modelMatrixLocation, 1, GL_FALSE, model_transform)
            glBindVertexArray(self.cube_mesh.vao)
            glDrawArrays(GL_TRIANGLES, 0, self.cube_mesh.vertex_count)
            
            pygame.display.flip()
            self.clock.tick(60)
        
        self.quit()

    def quit(self):
        self.cube_mesh.destroy()
        glDeleteProgram(self.shader)
        pygame.quit()


class CubeMesh:
    def __init__(self):
        self.vertices = (
            # Front face - Red
            -0.5, -0.5,  0.5,  1.0, 0.0, 0.0,
             0.5, -0.5,  0.5,  1.0, 0.0, 0.0,
             0.5,  0.5,  0.5,  1.0, 0.0, 0.0,
             0.5,  0.5,  0.5,  1.0, 0.0, 0.0,
            -0.5,  0.5,  0.5,  1.0, 0.0, 0.0,
            -0.5, -0.5,  0.5,  1.0, 0.0, 0.0,

            # Back face - Green
            -0.5, -0.5, -0.5,  0.0, 1.0, 0.0,
             0.5, -0.5, -0.5,  0.0, 1.0, 0.0,
             0.5,  0.5, -0.5,  0.0, 1.0, 0.0,
             0.5,  0.5, -0.5,  0.0, 1.0, 0.0,
            -0.5,  0.5, -0.5,  0.0, 1.0, 0.0,
            -0.5, -0.5, -0.5,  0.0, 1.0, 0.0,

            # Left face - Blue
            -0.5,  0.5,  0.5,  0.0, 0.0, 1.0,
            -0.5,  0.5, -0.5,  0.0, 0.0, 1.0,
            -0.5, -0.5, -0.5,  0.0, 0.0, 1.0,
            -0.5, -0.5, -0.5,  0.0, 0.0, 1.0,
            -0.5, -0.5,  0.5,  0.0, 0.0, 1.0,
            -0.5,  0.5,  0.5,  0.0, 0.0, 1.0,

            # Right face - Yellow
             0.5,  0.5,  0.5,  1.0, 1.0, 0.0,
             0.5,  0.5, -0.5,  1.0, 1.0, 0.0,
             0.5, -0.5, -0.5,  1.0, 1.0, 0.0,
             0.5, -0.5, -0.5,  1.0, 1.0, 0.0,
             0.5, -0.5,  0.5,  1.0, 1.0, 0.0,
             0.5,  0.5,  0.5,  1.0, 1.0, 0.0,

            # Bottom face - Magenta
            -0.5, -0.5, -0.5,  1.0, 0.0, 1.0,
             0.5, -0.5, -0.5,  1.0, 0.0, 1.0,
             0.5, -0.5,  0.5,  1.0, 0.0, 1.0,
             0.5, -0.5,  0.5,  1.0, 0.0, 1.0,
            -0.5, -0.5,  0.5,  1.0, 0.0, 1.0,
            -0.5, -0.5, -0.5,  1.0, 0.0, 1.0,

            # Top face - Cyan
            -0.5,  0.5, -0.5,  0.0, 1.0, 1.0,
             0.5,  0.5, -0.5,  0.0, 1.0, 1.0,
             0.5,  0.5,  0.5,  0.0, 1.0, 1.0,
             0.5,  0.5,  0.5,  0.0, 1.0, 1.0,
            -0.5,  0.5,  0.5,  0.0, 1.0, 1.0,
            -0.5,  0.5, -0.5,  0.0, 1.0, 1.0
        )
        
        self.vertex_count = len(self.vertices) // 6
        self.vertices = np.array(self.vertices, dtype=np.float32)

        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)
        
        # Position attribute
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(0))
        # Color attribute
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(12))
    
    def destroy(self):
        glDeleteVertexArrays(1, (self.vao,))
        glDeleteBuffers(1, (self.vbo,))


if __name__ == "__main__":
    myApp = App()