import numpy as np
import math

def create_view_matrix(yaw, pitch, zoom):
    """
    Create a view matrix from spherical coordinates.
    Camera is at distance 'zoom' from origin, facing the origin.
    """
    # Convert spherical coordinates to cartesian position
    x = zoom * math.cos(pitch) * math.cos(yaw)
    y = zoom * math.sin(pitch)
    z = zoom * math.cos(pitch) * math.sin(yaw)
    
    camera_pos = np.array([x, y, z])
    target = np.array([0.0, 0.0, 0.0])  # Looking at origin
    up = np.array([0.0, 1.0, 0.0])      # World up vector
    
    # Calculate camera basis vectors (OpenGL convention: camera looks down -Z)
    forward = target - camera_pos
    forward = forward / np.linalg.norm(forward)
    
    right = np.cross(forward, up)
    right = right / np.linalg.norm(right)
    
    up = np.cross(right, forward)
    
    # For OpenGL, we need to flip the forward direction (camera looks down -Z)
    forward = -forward
    
    # Create view matrix (OpenGL convention)
    view_matrix = np.array([
        [right[0], up[0], forward[0], 0],
        [right[1], up[1], forward[1], 0],
        [right[2], up[2], forward[2], 0],
        [-np.dot(right, camera_pos), -np.dot(up, camera_pos), -np.dot(forward, camera_pos), 1]
    ])
    
    return view_matrix

def create_projection_matrix(fovy_degrees, aspect_ratio, near=0.1, far=100.0):
    """
    Create a perspective projection matrix.
    """
    fovy_rad = math.radians(fovy_degrees)
    f = 1.0 / math.tan(fovy_rad / 2.0)
    
    projection_matrix = np.array([
        [f / aspect_ratio, 0, 0, 0],
        [0, f, 0, 0],
        [0, 0, (far + near) / (near - far), (2 * far * near) / (near - far)],
        [0, 0, -1, 0]
    ])
    
    return projection_matrix

def world_to_clip_space(world_pos, view_matrix, projection_matrix):
    """
    Convert world coordinates to clip space coordinates.
    """
    # Convert to homogeneous coordinates
    world_pos_homo = np.array([world_pos[0], world_pos[1], world_pos[2], 1.0])
    
    # Transform to view space
    view_pos = view_matrix @ world_pos_homo
    
    # Transform to clip space
    clip_pos = projection_matrix @ view_pos
    
    return clip_pos, view_pos

def clip_to_ndc(clip_pos):
    """
    Convert clip space to normalized device coordinates (NDC).
    """
    if clip_pos[3] != 0:
        ndc = clip_pos[:3] / clip_pos[3]
    else:
        ndc = clip_pos[:3]
    return ndc

def ndc_to_screen(ndc, screen_width, screen_height):
    """
    Convert NDC to screen coordinates.
    """
    screen_x = (ndc[0] + 1.0) * 0.5 * screen_width
    screen_y = (1.0 - ndc[1]) * 0.5 * screen_height  # Flip Y for screen coordinates
    return screen_x, screen_y

def main():
    # Parameters
    camera = {
        "yaw": -1.05,
        "pitch": -0.53,
        "zoom": 3
    }
    
    point_A = np.array([-0.5, 0, -0.5])
    screen_width = 1536
    screen_height = 864
    fovy = 45
    
    # Calculate aspect ratio
    aspect_ratio = screen_width / screen_height
    
    # Create transformation matrices
    view_matrix = create_view_matrix(camera["yaw"], camera["pitch"], camera["zoom"])
    projection_matrix = create_projection_matrix(fovy, aspect_ratio)
    
    # Debug: Show camera position
    x = camera["zoom"] * math.cos(camera["pitch"]) * math.cos(camera["yaw"])
    y = camera["zoom"] * math.sin(camera["pitch"])
    z = camera["zoom"] * math.cos(camera["pitch"]) * math.sin(camera["yaw"])
    camera_pos = np.array([x, y, z])
    
    print(f"Camera world position: [{camera_pos[0]:.4f}, {camera_pos[1]:.4f}, {camera_pos[2]:.4f}]")
    print(f"Camera looking at: [0.0000, 0.0000, 0.0000] (origin)")
    print(f"Up vector: [0, 1, 0] (positive Y)")
    print()
    
    # Transform point A to clip space
    clip_pos, view_pos = world_to_clip_space(point_A, view_matrix, projection_matrix)
    
    # Convert to NDC
    ndc = clip_to_ndc(clip_pos)
    
    # Convert to screen coordinates
    screen_x, screen_y = ndc_to_screen(ndc, screen_width, screen_height)
    
    # Print results
    print("=== 3D to Clip Space Conversion ===")
    print(f"Input point (world space): {point_A}")
    print(f"Camera position: yaw={camera['yaw']:.2f}, pitch={camera['pitch']:.2f}, zoom={camera['zoom']}")
    print(f"Screen dimensions: {screen_width}x{screen_height}")
    print(f"Field of view: {fovy}°")
    print()
    
    print("=== Transformation Matrices ===")
    print("View Matrix:")
    print(view_matrix)
    print()
    print("Projection Matrix:")
    print(projection_matrix)
    print()
    
    print("=== Results ===")
    print(f"View space coordinates: [{view_pos[0]:.4f}, {view_pos[1]:.4f}, {view_pos[2]:.4f}, {view_pos[3]:.4f}]")
    print(f"Clip space coordinates: [{clip_pos[0]:.4f}, {clip_pos[1]:.4f}, {clip_pos[2]:.4f}, {clip_pos[3]:.4f}]")
    print(f"NDC coordinates: [{ndc[0]:.4f}, {ndc[1]:.4f}, {ndc[2]:.4f}]")
    print(f"Screen coordinates: ({screen_x:.1f}, {screen_y:.1f})")
    print(f"Camera distance from point: {np.linalg.norm(point_A):.4f}")
    print(f"View space Z (camera space depth): {view_pos[2]:.4f}")
    print()
    
    # Check if point is visible (including depth test and behind camera check)
    is_behind_camera = clip_pos[3] <= 0
    is_in_frustum = (-abs(clip_pos[3]) <= clip_pos[0] <= abs(clip_pos[3]) and 
                     -abs(clip_pos[3]) <= clip_pos[1] <= abs(clip_pos[3]) and 
                     0 <= clip_pos[2] <= abs(clip_pos[3]))  # OpenGL depth range [0,1] after perspective divide
    is_visible = not is_behind_camera and is_in_frustum
    
    print(f"Point is {'visible' if is_visible else 'not visible'} on screen")
    if is_behind_camera:
        print("  - Point is behind the camera (w <= 0)")
    elif not is_in_frustum:
        print("  - Point is outside the viewing frustum")
    
    # Additional utility function to test multiple points
    def test_point(world_pos, label="Point"):
        clip_pos, view_pos = world_to_clip_space(world_pos, view_matrix, projection_matrix)
        ndc = clip_to_ndc(clip_pos)
        screen_x, screen_y = ndc_to_screen(ndc, screen_width, screen_height)
        
        is_behind_camera = clip_pos[3] <= 0
        is_in_frustum = (-abs(clip_pos[3]) <= clip_pos[0] <= abs(clip_pos[3]) and 
                         -abs(clip_pos[3]) <= clip_pos[1] <= abs(clip_pos[3]) and 
                         0 <= clip_pos[2] <= abs(clip_pos[3]))
        is_visible = not is_behind_camera and is_in_frustum
        
        status = "✓" if is_visible else ("behind" if is_behind_camera else "outside")
        print(f"{label}: {world_pos} -> Clip: [{clip_pos[0]:.4f}, {clip_pos[1]:.4f}, {clip_pos[2]:.4f}, {clip_pos[3]:.4f}] -> Screen: ({screen_x:.1f}, {screen_y:.1f}) {status}")
    
    print("\n=== Additional Test Points ===")
    test_point(np.array([0, 0, 0]), "Origin")
    test_point(np.array([1, 0, 0]), "X-axis")
    test_point(np.array([0, 1, 0]), "Y-axis")
    test_point(np.array([0, 0, 1]), "Z-axis")
    
    print("\n=== Coordinate System Test ===")
    print("Testing yaw=0, pitch=0, zoom=3:")
    test_camera = {"yaw": 0, "pitch": 0, "zoom": 3}
    x_test = test_camera["zoom"] * math.cos(test_camera["pitch"]) * math.cos(test_camera["yaw"])
    y_test = test_camera["zoom"] * math.sin(test_camera["pitch"])
    z_test = test_camera["zoom"] * math.cos(test_camera["pitch"]) * math.sin(test_camera["yaw"])
    print(f"Camera would be at: [{x_test:.4f}, {y_test:.4f}, {z_test:.4f}]")
    print("This confirms: yaw=0 -> camera faces along positive X-axis")
    print("              pitch=0 -> camera at Y=0 (XZ plane)")
    print("              up vector is positive Y-axis")

if __name__ == "__main__":
    main()