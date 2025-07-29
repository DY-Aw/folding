import pyrr
import numpy as np
import math

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

def nextFaceInSequence(faceID):
    return 'F'+str(int(faceID[1:])+1)

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

            
