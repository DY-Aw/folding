import pyrr
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
    transformed = pyrr.matrix44.apply_to_vector(
        pyrr.matrix44.multiply(
            pyrr.matrix44.multiply(
                model,
                view
            ),
            projection
        ),
        np.append(point,1.0)
    )
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

# Casts a ray from the cursor starting from the near clipping plane.
def mouseToRay(screenInfo, proj, view):
    sw, sh = screenInfo
    mouseX, mouseY = convertToOpenGLCoordinates(pygame.mouse.get_pos(), (sw, sh))
    near = pyrr.Vector4([mouseX, mouseY, -1.0, 1.0], dtype=np.float32)
    far = pyrr.Vector4([mouseX, mouseY, 1.0, 1.0], dtype=np.float32)

    iproj = pyrr.matrix44.inverse(proj)
    iview = pyrr.matrix44.inverse(view)

    view_near = pyrr.matrix44.apply_to_vector(iproj, near)
    view_near = view_near / view_near[3]
    view_far = pyrr.matrix44.apply_to_vector(iproj, far)
    view_far = view_far / view_far[3]
    view_vec = view_far - view_near

    rayOrigin = pyrr.matrix44.apply_to_vector(iview, view_near)
    rayOrigin = rayOrigin / rayOrigin[3]

    rayDirection = pyrr.matrix44.apply_to_vector(iview, pyrr.vector4.create(view_vec[0], view_vec[1], view_vec[2], 0.0))
    rayOrigin = pyrr.vector3.create(rayOrigin[0], rayOrigin[1], rayOrigin[2])
    rayDirection = pyrr.vector3.create(rayDirection[0], rayDirection[1], rayDirection[2])
    return rayOrigin, rayDirection

# Returns the distance from the ray origin at which the given triangle intersects the ray. Returns None if no intersection.
def triangleIntersect(rayOrigin, rayDirection, v0, v1, v2):
    edge1 = v1 - v0
    edge2 = v2 - v0

    pvec = pyrr.vector3.cross(rayDirection, edge2)
    det = pyrr.vector3.dot(edge1, pvec)
    inv_det = 1.0/det

    tvec = rayOrigin - v0
    u = pyrr.vector3.dot(tvec, pvec) * inv_det
    if u < 0.0 or u > 1.0:
        return None
    qvec = pyrr.vector3.cross(tvec, edge1)
    v = pyrr.vector3.dot(rayDirection, qvec) * inv_det
    if v < 0.0 or (u + v) > 1.0:
        return None
    
    t = np.dot(edge2, qvec) * inv_det
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