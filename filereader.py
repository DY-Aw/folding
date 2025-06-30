import json
import os
import sys

from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader

from face import Face

def get_resource_path(file):
    return os.path.join(os.path.dirname(__file__), "data/"+file)

def pl_create(file_name):
    file_path = get_resource_path(file_name)
    with open(file_path, 'r') as f:
        loaded_data = json.load(f)
    points = loaded_data['points']
    for key in points.keys():
        points[key] = tuple(points[key])
    return points

def camera_create(file_name):
    file_path = get_resource_path(file_name)
    with open(file_path, 'r') as f:
        loaded_data = json.load(f)
    x = loaded_data['x']
    y = loaded_data['y']
    z = loaded_data['z']
    yaw = loaded_data['yaw']
    pitch = loaded_data['pitch']
    hfov = loaded_data['hfov']
    return x, y, z, yaw, pitch, hfov

def faces_create(file_name):
    file_path = get_resource_path(file_name)
    with open(file_path, 'r') as f:
        loaded_data = json.load(f)
    faces = loaded_data['faces']
    return faces
    
def shader_create(vertexfile, fragmentfile):
    vertex_path = os.path.join(os.path.dirname(__file__), "shaders/"+vertexfile)
    fragment_path = os.path.join(os.path.dirname(__file__), "shaders/"+fragmentfile)
    with open(vertex_path, 'r') as f:
        vertex_source = f.read()
    
    with open(fragment_path, 'r') as f:
        fragment_source = f.read()

    shader = compileProgram(
        compileShader(vertex_source, GL_VERTEX_SHADER),
        compileShader(fragment_source, GL_FRAGMENT_SHADER)
    )
    return shader
