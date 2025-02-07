import numpy as np
import cv2

# Function to extract the pose of the tag using solvePnP
def pnp(tag_corners, camera_matrix, dist_coeffs, tag_size):
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
    tag_corners = [tag_corners[i] for i in [3, 2, 1, 0]]  # Reorder to match object_points
    image_points = np.array(tag_corners, dtype=np.float32)
    
    # Use cv2.solvePnP to calculate rotation and translation vectors
    success, rvec, tvec = cv2.solvePnP(object_points, image_points, camera_matrix, dist_coeffs)
    
    if not success:
        return None, None, False
    
    return rvec, tvec, True


# Function to convert the rotation vector (rvec) to Euler angles
def rvec_to_euler_angles(rvec):
    # Convert the rotation vector to a rotation matrix
    rotation_matrix, _ = cv2.Rodrigues(rvec)
    
    # Extract roll, pitch, and yaw from the rotation matrix
    sy = np.sqrt(rotation_matrix[0, 0]**2 + rotation_matrix[1, 0]**2)
    singular = sy < 1e-6

    if not singular:
        roll = np.arctan2(rotation_matrix[2, 1], rotation_matrix[2, 2])
        pitch = np.arctan2(-rotation_matrix[2, 0], sy)
        yaw = np.arctan2(rotation_matrix[1, 0], rotation_matrix[0, 0])
    else:
        roll = np.arctan2(-rotation_matrix[1, 2], rotation_matrix[1, 1])
        pitch = np.arctan2(-rotation_matrix[2, 0], sy)
        yaw = 0

    return np.degrees(roll), np.degrees(pitch), np.degrees(yaw)


# Main function to calculate the pose (translation, yaw, pitch, roll) using solvePnP
def calculate_pose(apriltag_data, tag_id, detected_tag_info, camera_matrix, dist_coeffs, tag_size, resize):
    # Extract the corners of the detected AprilTag
    for tag in detected_tag_info:
        if tag["id"] == tag_id:
            tag_corners = tag["corners"]  # These are pixel coordinates (ptA, ptB, ptC, ptD)
            
            # Calculate translation and rotation using solvePnP
            rvec, tvec, success = pnp(tag_corners, camera_matrix, dist_coeffs, tag_size)
            if not success:
                # print(f"Failed to calculate pose for tag ID {tag_id}")
                return None
            
            # Convert rotation vector to Euler angles (yaw, pitch, roll)
            roll, pitch, yaw = rvec_to_euler_angles(rvec)
            # print(f"  Roll: {roll:.2f} degrees, Pitch: {pitch:.2f} degrees, Yaw: {yaw:.2f} degrees")

            # Calculate the distance to the tag
            print("======================================")
            tvec_resized = tvec * resize
            # print(f"resized tvec: {tvec_resized}")
            t_x = tvec_resized[0][0]
            t_y = tvec_resized[1][0]
            t_z = tvec_resized[2][0]
            distance = t_z
            print(f"Distance: {distance:.2f} meters")

            # Calculate the angle of the tag from the camera
            horizontal_angle_rad = np.arctan2(t_x, t_z)
            horizontal_angle_deg = np.degrees(horizontal_angle_rad)
            print(f"Horizontal Angle: {horizontal_angle_deg:.2f} degrees")

            # Get the tag's real-world position and yaw (from apriltag_data)
            tag_real_position = apriltag_data["apriltags"][tag_id]["position"]
            tag_real_x, tag_real_y, tag_real_z, tag_real_facing_angle = tag_real_position

            # Calculate the camera's position and yaw
            camera_yaw = tag_real_facing_angle - 180 - pitch - horizontal_angle_deg
            camera_x = tag_real_x + distance * (np.sin(np.deg2rad(tag_real_facing_angle)) * np.sin(np.deg2rad(pitch)) + np.cos(np.deg2rad(tag_real_facing_angle)) * np.cos(np.deg2rad(pitch)))
            camera_y = tag_real_y + distance * (np.sin(np.deg2rad(tag_real_facing_angle)) * np.cos(np.deg2rad(pitch)) - np.cos(np.deg2rad(tag_real_facing_angle)) * np.sin(np.deg2rad(pitch)))

            # print("======================================")
            # print(f"Camera Position: ({camera_x:.2f}, {camera_y:.2f})")
            # print(f"Camera Angle: {camera_yaw:.2f} degrees")

            # Return the pose information
            return {
                "x": camera_x,
                "y": camera_y,
                "yaw": camera_yaw
            }

        
    return None  # If no matching tag is found