import numpy as np
import cv2

# Function to extract the pose of the tag using solvePnP
def calculate_pose_with_pnp(tag_corners, camera_matrix, dist_coeffs, tag_size):
    """
    Calculates translation and rotation using cv2.solvePnP.
    
    Args:
        tag_corners (list): List of corner points from the detected tag [(ptA), (ptB), (ptC), (ptD)].
        camera_matrix (numpy array): The camera intrinsic matrix.
        dist_coeffs (numpy array): The distortion coefficients for the camera.
        tag_size (float): The real-world size of the AprilTag (e.g., width of the tag in meters).

    Returns:
        tuple: Rotation vector, translation vector, success flag (True if solvePnP succeeds).
    """
    # Define the 3D object points for the AprilTag in the tag's coordinate frame
    object_points = np.array([
        [-tag_size / 2, -tag_size / 2, 0],  # Bottom-left corner
        [ tag_size / 2, -tag_size / 2, 0],  # Bottom-right corner
        [ tag_size / 2,  tag_size / 2, 0],  # Top-right corner
        [-tag_size / 2,  tag_size / 2, 0]   # Top-left corner
    ], dtype=np.float32)
    
    # Convert pixel corner points to numpy array for solvePnP
    image_points = np.array(tag_corners, dtype=np.float32)
    
    # Use cv2.solvePnP to calculate rotation and translation vectors
    success, rvec, tvec = cv2.solvePnP(object_points, image_points, camera_matrix, dist_coeffs)
    
    if not success:
        return None, None, False
    
    return rvec, tvec, True


# Function to invert the translation (user's position based on the tag)
def invert_translation(translation):
    tx, ty, tz = translation
    return [-tx, -ty, -tz]  # Inverted translation


# Function to convert the rotation vector (rvec) to Euler angles
def rvec_to_euler_angles(rvec):
    """
    Convert a rotation vector to Euler angles (yaw, pitch, roll).
    """
    rotation_matrix, _ = cv2.Rodrigues(rvec)
    return rotation_matrix_to_euler_angles(rotation_matrix)


# Function to convert a rotation matrix to Euler angles
def rotation_matrix_to_euler_angles(R):
    """
    Convert a rotation matrix to Euler angles (yaw, pitch, roll) in degrees.
    Assumes the rotation matrix follows the ZYX convention.
    """
    sy = np.sqrt(R[0, 0] ** 2 + R[1, 0] ** 2)
    singular = sy < 1e-6

    if not singular:
        roll = np.arctan2(R[2, 1], R[2, 2])
        pitch = np.arctan2(-R[2, 0], sy)
        yaw = np.arctan2(R[1, 0], R[0, 0])
    else:
        roll = np.arctan2(-R[1, 2], R[1, 1])
        pitch = np.arctan2(-R[2, 0], sy)
        yaw = 0

    return np.degrees(roll), np.degrees(pitch), np.degrees(yaw)


# Function to apply a 2D rotation to account for the tag's yaw in the world frame
def apply_rotation(yaw, relative_position):
    """
    Rotate the relative position by the tag's yaw angle (in degrees).
    Args:
        yaw (float): The yaw of the tag in degrees (from apriltag_data).
        relative_position (list or array): The user's relative (x, z) position.
    
    Returns:
        list: The rotated position in world coordinates.
    """
    # Convert yaw from degrees to radians
    yaw_rad = np.radians(yaw)
    
    # 2D rotation matrix to rotate around the vertical axis (y-axis)
    rotation_matrix = np.array([
        [np.cos(yaw_rad), -np.sin(yaw_rad)],
        [np.sin(yaw_rad),  np.cos(yaw_rad)]
    ])
    
    # Apply the 2D rotation to the (x, z) relative position
    rotated_position = rotation_matrix.dot(relative_position[:2])  # Apply only on x, z
    return [rotated_position[0], relative_position[1], rotated_position[1]]  # Return x, y, z


# Main function to calculate the pose (translation, yaw, pitch, roll) using solvePnP
def calculate_pose(apriltag_data, tag_id, detected_tag_info, camera_matrix, dist_coeffs, tag_size):
    # Extract the corners of the detected AprilTag
    for tag in detected_tag_info:
        if tag["id"] == tag_id:
            tag_corners = tag["corners"]  # These are pixel coordinates (ptA, ptB, ptC, ptD)
            
            # Calculate translation and rotation using solvePnP
            rvec, tvec, success = calculate_pose_with_pnp(tag_corners, camera_matrix, dist_coeffs, tag_size)
            if not success:
                print(f"Failed to calculate pose for tag ID {tag_id}")
                return None
            
            # Convert rotation vector to Euler angles (yaw, pitch, roll)
            roll, pitch, yaw = rvec_to_euler_angles(rvec)
            roll, pitch, yaw = np.degrees(roll)%360, np.degrees(pitch)%360, np.degrees(yaw)%360
            print(f"  Roll: {roll:.2f}, Pitch: {pitch:.2f}, Yaw: {yaw:.2f}")
            
            # Invert the translation to get the user's relative position
            user_relative_position = invert_translation(tvec.flatten())  # Relative to the tag

            # Get the tag's real-world position and yaw (from apriltag_data)
            tag_real_position = apriltag_data["apriltags"][tag_id]["position"]
            tag_real_x, tag_real_y, tag_real_z, tag_real_yaw = tag_real_position

            # Rotate the user's relative position by the tag's yaw (facing direction)
            user_rotated_position = apply_rotation(tag_real_yaw, user_relative_position)
            print("======================================")
            print(f"Relative location of Apriltag from camera:")
            print(f"  Distance: {np.linalg.norm(user_relative_position):.2f} meters")
            print(f"  Yaw: {np.degrees(np.arctan2(user_relative_position[0], user_relative_position[2])):.2f} degrees")

            # Calculate the absolute position of the user by adding the tag's real position
            user_absolute_x = tag_real_x + user_rotated_position[0]
            user_absolute_y = tag_real_y + user_rotated_position[2]
            user_absolute_z = tag_real_z + user_rotated_position[1]

            # Calculate the relative yaw and absolute yaw of the user
            relative_yaw = np.degrees(np.arctan2(user_relative_position[0], user_relative_position[2]))
            user_yaw = (-relative_yaw + tag_real_yaw) % 360  # Modulo 360 to keep it within [0, 360] degrees

            # Return the user's absolute position (x, z, y) and the facing direction (yaw)
            user_pose = {
                "x": user_absolute_x,
                "y": user_absolute_y,
                "z": user_absolute_z,
                "yaw": user_yaw  # Facing direction (yaw in camera frame)
            }
            print("======================================")
            print(f"User's pose: X: {user_pose['x']:.2f}, Y: {user_pose['y']:.2f}, Z: {user_pose['z']:.2f}, Yaw: {user_pose['yaw']:.2f}")
            return user_pose
        
    return None  # If no matching tag is found