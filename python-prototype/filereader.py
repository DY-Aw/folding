import json
import os

from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader

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
    yaw = loaded_data['yaw']
    pitch = loaded_data['pitch']
    zoom = loaded_data['zoom']
    return yaw, pitch, zoom

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
