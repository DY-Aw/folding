from pyglm import glm
import numpy as np
import math
import pygame

# Converts pygame coordinates to opengl coordinates
def convertToOpenGLCoordinates(xy, s):
    x, y = xy
    sw, sh = s
    fx = 2*x / sw - 1
    fy = 2*y / sh - 1
    return fx, -fy

# Converts opengl coordinates to pygame coordinates
def convertToPygameCoordinates(xy, s):
    x, y = xy
    sw, sh = s
    fx = (x+1) * sw / 2
    fy = (-y+1) * sh / 2
    return fx, fy

# Converts local space coordinates to ndc
def getScreenCoordinates(point, model, view, projection):
    transformed = projection * view * model * glm.vec4(*point, 1.0)
    return (transformed[0]/transformed[3], transformed[1]/transformed[3])

# Takes mouse position relative to a given line
# Returns linelength, distance from line, distance along line
def mouseToLine(p1, p2, m):
    mouseX, mouseY = m
    ax, ay = p1
    bx, by = p2
    bx -= ax
    by -= ay
    mx = mouseX - ax
    my = mouseY - ay
    theta = -math.atan2(by, bx)
    b = bx * math.cos(theta) - by * math.sin(theta)
    m_x = mx * math.cos(theta) - my * math.sin(theta)
    m_y = mx * math.sin(theta) + my * math.cos(theta)

    return b, m_x, m_y

# Returns the next letter alphabetically. If character is z, will increment to aa
def nextLetterInSequence(letter, uppercase=False):
    # Convert letter to digits
    digits=[]
    for char in letter.lower():
        # Convert letters to numbers, with 'a' = 1 to 'z' = 26
        digits.append(ord(char))
    digits.reverse()
    digits[0] += 1
    x = len(digits)
    for i in range(x):
        # If ASCII above 'z'
        if digits[i] > 122:
            # Change digit to 'a'
            digits[i] -= 26
            # Carry over
            if i+1 > x-1:
                digits.append(97)
            else:
                digits[i+1] += 1
    digits.reverse()
    result = ''
    for i in range(len(digits)):
        result += chr(digits[i])
    if uppercase:
        result = result.upper()
    return result

# Returns the next faceID. Stored as 'F[x]' where [x] is an integer.
def nextFaceInSequence(faceID):
    return 'F'+str(int(faceID[1:])+1)

# Creates a point at specified local coordinates 
def createPoint(pointsdict, coordinates):
    sortedIDs = list(pointsdict.keys())
    sortedIDs.sort(key=AlphaID)
    pointID = nextLetterInSequence(sortedIDs[-1])
    pointsdict.update({pointID: coordinates})
    return pointID

# Find the intersection of lines defined by (p1, p2) and (p3, p4)
def findIntersection(p1, p2, p3, p4):
    x1, y1 = p1
    x2, y2 = p2
    x3, y3 = p3
    x4, y4 = p4

    A1 = y2 - y1
    B1 = x1 - x2
    C1 = A1 * x1 + B1 * y1

    A2 = y4 - y3
    B2 = x3 - x4
    C2 = A2 * x3 + B2 * y3

    determinant = A1 * B2 - A2 * B1

    EPSILON = 1e-9 

    if abs(determinant) < EPSILON:
        return None
    else:
        x = (C1 * B2 - C2 * B1) / determinant
        y = (A1 * C2 - A2 * C1) / determinant
        return (x, y)
    
def create2dTranslationMatrix(dx, dy):
    matrix = glm.mat3(
        1.0, 0.0, 0.0,
        0.0, 1.0, 0.0,
        dx, dy, 1.0
    )
    return matrix

def create2dRotationMatrix(theta):
    matrix = glm.mat3(
        glm.cos(theta), glm.sin(theta), 0,
        -glm.sin(theta), glm.cos(theta), 0,
        0, 0, 1
    )
    return matrix

# Casts a ray from the cursor starting from the near clipping plane.
def mouseToRay(screenInfo, proj, view):
    sw, sh = screenInfo
    mouseX, mouseY = convertToOpenGLCoordinates(pygame.mouse.get_pos(), (sw, sh))
    near = glm.vec4(mouseX, mouseY, -1.0, 1.0)
    far = glm.vec4(mouseX, mouseY, 1.0, 1.0)

    iproj = glm.inverse(proj)
    iview = glm.inverse(view)

    view_near = iproj * near
    view_near = view_near / view_near[3]
    view_far = iproj * far
    view_far = view_far / view_far[3]
    view_vec = view_far - view_near

    rayOrigin = iview * view_near
    rayOrigin = rayOrigin / rayOrigin[3]

    rayDirection = iview * glm.vec4(view_vec[0], view_vec[1], view_vec[2], 0.0)
    rayOrigin = glm.vec3(rayOrigin[0], rayOrigin[1], rayOrigin[2])
    rayDirection = glm.vec3(rayDirection[0], rayDirection[1], rayDirection[2])
    return rayOrigin, rayDirection

# Returns the distance from the ray origin at which the given triangle intersects the ray. Returns None if no intersection.
def triangleIntersect(rayOrigin, rayDirection, v0, v1, v2):
    edge1 = v1 - v0
    edge2 = v2 - v0

    pvec = glm.cross(rayDirection, edge2)
    det = glm.dot(edge1, pvec)
    inv_det = 1.0/det

    tvec = rayOrigin - v0
    u = glm.dot(tvec, pvec) * inv_det
    if u < 0.0 or u > 1.0:
        return None
    qvec = glm.cross(tvec, edge1)
    v = glm.dot(rayDirection, qvec) * inv_det
    if v < 0.0 or (u + v) > 1.0:
        return None
    
    t = glm.dot(edge2, qvec) * inv_det
    if t < 0:
        return None
    
    return t, u, v

# Sorting list by alphabet ID. Usage: my_list.sort(key=AlphaID)
def AlphaID(s: str) -> int:
    valueAsString = ''
    for char in s.lower():
        valueAsString += str(ord(char)-87)
    return int(valueAsString)

# Sorting list by face ID ('F[x]' where x is an integer). Usage: my_list.sort(key=FaceID)
def FaceID(s: str) -> int:
    faceID = s[1:]
    return int(faceID)