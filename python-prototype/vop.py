import math
import numpy as np

class Vector:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __repr__(self):
        return f"(x: [{self.x:.3f}], y: [{self.y:.3f}], z: [{self.z:.3f}])"

    def to_list(self):
        return [self.x, self.y, self.z]
    
    def magnitude(self):
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)
    
    def normalize(self):
        mag = self.magnitude()
        return Vector(self.x/mag, self.y/mag, self.z/mag)
    
    def vCoord(self):
        return (self.x, self.y, self.z)

    # Not implemented
    def proj(self, other):
        return Vector()
    
    def __add__(self, other):
        return Vector(
            self.x + other.x,
            self.y + other.y,
            self.z + other.z
        )
    
    def __sub__(self, other):
        return Vector(
            self.x - other.x,
            self.y - other.y,
            self.z - other.z
        )

    def dot(self, other):
        return(self.x*other.x + self.y*other.y + self.z*other.z)
    
    def cross(self, other):
        return Vector(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x
        )
    
    def __mul__(self, scalar):
        if not isinstance(scalar, (int, float)):
            raise TypeError("Can only multiply a Vector by a scalar (int or float)")
        return Vector(self.x * scalar, self.y * scalar, self.z * scalar)

    def __rmul__(self, scalar):
        return self.__mul__(scalar)
    
    def normals(self):
        v = self.normalize()
        v2x = 0 - (v.y + v.z)
        v2 = Vector.cross(v, Vector(0, 0, 1)).normalize()
        v3 = Vector.cross(v, v2)
        return v2, v3
    
    def matrix(vectors):
        x, y, z = [], [], []
        for vector in vectors:
            x.append(vector.x)
            y.append(vector.y)
            z.append(vector.z)
        return np.array([x, y, z])
    
    def basis(vectors, point):
        matrix = Vector.matrix(vectors)
        imatrix = np.linalg.inv(matrix)
        x, y, z = point
        converted_point = imatrix @ np.array([[x], [y], [z]])
        return tuple(converted_point.flatten())

