import json
import os
import sys

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
    