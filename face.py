'''import numpy as np
from OpenGL.GL import *
import ctypes

class Face:

    def __init__(self, face_data, points):
        self.vertices = face_data['vertices']
        self.points = points
        self.color = [c / 255.0 for c in face_data['color']] if 'color' in face_data else [1.0, 0.0, 0.0]

        self.triangles = self.triangulate()

        self.vao = None
        self.vbo = None

        self.vertex_count = 0
        self.gpu_data()

    def triangulate(self):
        triangles = []
        for i in range(1, len(self.vertices) - 1):
            triangles.append((self.vertices[0], self.vertices[i], self.vertices[i+1]))
        return triangles
    
    def gpu_data(self):

        vertex_data = []
        
        for tri_vertex_keys in self.triangles:
            for vertex_key in tri_vertex_keys:
                point = self.points[vertex_key]
                
                vertex_data.extend(point)
                vertex_data.extend(self.color)

                self.vertices_np_array = np.array(vertex_data, dtype=np.float32)
                self.vertex_count = len(vertex_data) // 6

                if self.vao is None:
                    self.vao = glGenVertexArrays(1)
                    glBindVertexArray(self.vao)

                if self.vbo is None:
                    self.vbo = glGenBuffers(1)
                    glBindBuffer(GL_ARRAY_BUFFER, self.vbo)

                glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)
                glEnableVertexAttribArray(0)
                glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(0))
                glEnableVertexAttribArray(1)
                glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(12))
                glBindBuffer(GL_ARRAY_BUFFER, 0)
                glBindVertexArray(0)

    def draw(self):
        glBindVertexArray(self.vao)
        glDrawArrays(GL_TRIANGLES, 0, self.vertex_count)
        glBindVertexArray(0)

    def destroy(self):
        if self.vao is not None:
            glDeleteVertexArrays(1, (self.vao,))
            self.vao = None
        if self.vbo is not None:
            glDeleteBuffers(1, (self.vbo,))
            self.vbo = None'''

# In data/models.py (or paper.py, where your Face class is defined)

import numpy as np
from OpenGL.GL import *
import ctypes # Needed for glVertexAttribPointer offset

class Face:
    def __init__(self, face_data, points_data):
        # ... (previous __init__ code) ...
        self.original_vertex_keys = face_data['vertices']
        self.points = points_data
        self.color = [c / 255.0 for c in face_data['color']] if 'color' in face_data else [1.0, 1.0, 1.0]

        self.triangles = self._triangulate_convex_polygon()

        self.vao = None
        self.vbo = None
        self.vertex_count = 0 

        # Call the corrected GPU data setup method
        self._setup_gpu_data() 

    def _triangulate_convex_polygon(self):
        triangles = []
        for i in range(1, len(self.original_vertex_keys) - 1):
            triangles.append((self.original_vertex_keys[0], self.original_vertex_keys[i], self.original_vertex_keys[i+1]))
        return triangles

    def _setup_gpu_data(self): # Renamed for clarity, as it sets up data, not just general GPU ops
        """
        Prepares and uploads vertex data (position and color) to the GPU
        using VBOs and VAOs for this face's triangles.
        This method should be called ONCE when the face is created or its geometry changes.
        """
        vertex_data = [] # List to collect all floats for all vertices

        # --- STEP 1: Collect ALL vertex data into a single Python list ---
        for tri_vertex_keys in self.triangles:
            for vertex_key in tri_vertex_keys:
                point = self.points[vertex_key] # Get 3D world coordinates (x, y, z)
                
                # Append position (3 floats)
                vertex_data.extend(point)
                # Append color (3 floats) - using face's uniform color for now
                vertex_data.extend(self.color)
        
        # --- STEP 2: Convert to a single NumPy array after all data is collected ---
        self.vertices_np_array = np.array(vertex_data, dtype=np.float32)
        # --- STEP 3: Calculate the total number of *OpenGL vertices* ---
        self.vertex_count = len(vertex_data) // 6 # Each vertex has 6 floats (3 pos + 3 color)

        # --- STEP 4: OpenGL Buffer Setup (Perform ONCE per Face) ---

        # 4a. Generate and Bind VAO (Vertex Array Object)
        # VAO stores the state of how vertex attributes are configured (which VBO, how data is laid out).
        # Generate VAO only if it hasn't been generated before (e.g., first call)
        if self.vao is None: 
            self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao) # Bind this VAO; all subsequent configurations will be stored in it

        # 4b. Generate and Bind VBO (Vertex Buffer Object)
        # VBO stores the actual vertex data (positions, colors, etc.).
        # Generate VBO only if it hasn't been generated before
        if self.vbo is None:
            self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo) # Bind this VBO as the active array buffer

        # 4c. Upload data to VBO
        # glBufferData uploads the *entire* NumPy array to the bound VBO.
        # GL_STATIC_DRAW: Data is uploaded once and drawn many times (suitable for fixed geometry like this).
        glBufferData(GL_ARRAY_BUFFER, self.vertices_np_array.nbytes, self.vertices_np_array, GL_STATIC_DRAW)

        # 4d. Configure Vertex Attributes (tell OpenGL how to interpret data in VBO)
        # These locations (0 and 1) must match 'layout (location = X) in ...' in your GLSL shaders!

        # Attribute 0: 'vertexPos' (layout (location = 0) in vec3 vertexPos;)
        glVertexAttribPointer(
            0,                     # Attribute location in shader
            3,                     # Number of components per vertex (vec3 = x, y, z)
            GL_FLOAT,              # Data type of each component
            GL_FALSE,              # Normalized? (GL_FALSE for positions/colors)
            6 * ctypes.sizeof(GLfloat), # Stride: Bytes between the start of one vertex and the next (6 floats * 4 bytes/float)
            ctypes.c_void_p(0)     # Offset of the first component of this attribute (0 for position)
        )
        glEnableVertexAttribArray(0) # Enable the attribute

        # Attribute 1: 'vertexColor' (layout (location = 1) in vec3 vertexColor;)
        glVertexAttribPointer(
            1,                     # Attribute location in shader
            3,                     # Number of components per vertex (vec3 = r, g, b)
            GL_FLOAT,              # Data type of each component
            GL_FALSE,              # Normalized?
            6 * ctypes.sizeof(GLfloat), # Stride: Same as position (6 floats)
            ctypes.c_void_p(3 * ctypes.sizeof(GLfloat)) # Offset: 3 floats (pos) * 4 bytes/float = 12 bytes
        )
        glEnableVertexAttribArray(1) # Enable the attribute

        # --- STEP 5: Unbind VAO and VBO (after all configuration is complete) ---
        # It's good practice to unbind to prevent accidental modification by other code.
        glBindBuffer(GL_ARRAY_BUFFER, 0) # Unbind the VBO
        glBindVertexArray(0)             # Unbind the VAO (do this last for VAO to store VBO binding)

    def draw(self):
        """
        Draws the face using Modern OpenGL (VBO, VAO, Shaders).
        Assumes the correct shader program is already active.
        """
        # --- Drawing: Bind and Draw (Perform for EACH frame) ---
        glBindVertexArray(self.vao)      # Bind this face's VAO to prepare for drawing
        glDrawArrays(GL_TRIANGLES, 0, self.vertex_count) # Issue the draw call
        glBindVertexArray(0)             # Unbind VAO after drawing (good practice)

    def destroy(self):
        """
        Cleans up OpenGL resources (VAO and VBO) for this face.
        This should be called when the Face object is no longer needed.
        """
        if self.vao is not None:
            glDeleteVertexArrays(1, (self.vao,))
            self.vao = None
        if self.vbo is not None:
            glDeleteBuffers(1, (self.vbo,))
            self.vbo = None
