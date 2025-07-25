def convertToOpenGLCoordinates(x, y, sw, sh):
    fx = 2*x / sw - 1
    fy = 2*y / sh - 1
    return fx, -fy

def convertToPygameCoordinates(x, y, sw, sh):
    fx = (x+1) * sw / 2
    fy = (-y+1) * sh / 2
    return fx, fy
