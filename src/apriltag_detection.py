import cv2
import apriltag
import json
import numpy as np
import os

def detect_and_mark_apriltags(image_path, json_path, camera_matrix, dist_coeffs, tag_size):
    # Load the image
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Load the apriltags.json file
    with open(json_path, 'r') as f:
        apriltag_data = json.load(f)

    # Create a dictionary for quick lookup by tag ID
    apriltag_dict = {tag['id']: tag for tag in apriltag_data['apriltags']}

    # Initialize the AprilTag detector
    detector = apriltag.Detector()

    # Detect AprilTags in the image
    results = detector.detect(gray)

    # List to store corners, center, and orientation of detected AprilTags
    detected_tag_info = []

    # Loop over the detected results
    for r in results:
        tag_id = r.tag_id  # Get the detected tag ID

        # Check if the detected tag ID is in the apriltag_dict
        if tag_id in apriltag_dict:
            tag_info = apriltag_dict[tag_id]  # Fetch metadata
            name = tag_info["name"]  # Use only the name

            # Extract the bounding box (four corners) of the tag
            (ptA, ptB, ptC, ptD) = r.corners
            ptA = (int(ptA[0]), int(ptA[1]))
            ptB = (int(ptB[0]), int(ptB[1]))
            ptC = (int(ptC[0]), int(ptC[1]))
            ptD = (int(ptD[0]), int(ptD[1]))

            # Draw the bounding box of the AprilTag
            cv2.line(image, ptA, ptB, (0, 255, 0), 2)
            cv2.line(image, ptB, ptC, (0, 255, 0), 2)
            cv2.line(image, ptC, ptD, (0, 255, 0), 2)
            cv2.line(image, ptD, ptA, (0, 255, 0), 2)

            # Draw the center (x, y) of the tag
            (cX, cY) = (int(r.center[0]), int(r.center[1]))
            cv2.circle(image, (cX, cY), 5, (0, 0, 255), -1)

            # Use PnP to get the tag's pose (translation and rotation)
            object_points = np.array([
                [-tag_size/2, -tag_size/2, 0],
                [ tag_size/2, -tag_size/2, 0],
                [ tag_size/2,  tag_size/2, 0],
                [-tag_size/2,  tag_size/2, 0]
            ], dtype=np.float32)

            image_points = np.array([ptA, ptB, ptC, ptD], dtype=np.float32)
            success, rvec, tvec = cv2.solvePnP(object_points, image_points, camera_matrix, dist_coeffs)

            # Rotation and translation vectors
            if success:
                rotation_matrix, _ = cv2.Rodrigues(rvec)
                translation = tvec

                # Convert rotation matrix to Euler angles (yaw, pitch, roll)
                roll, pitch, yaw = rotation_matrix_to_euler_angles(rotation_matrix)

                # Append the tag's info
                detected_tag_info.append({
                    "id": tag_id,
                    "corners": {
                        "ptA": ptA,
                        "ptB": ptB,
                        "ptC": ptC,
                        "ptD": ptD
                    },
                    "center": (cX, cY),
                    "translation": translation.flatten(),
                    "rotation": (yaw, pitch, roll)  # Yaw, pitch, and roll
                })

    # Save the image with marked AprilTags in the same folder as the input image
    base_name = os.path.splitext(os.path.basename(image_path))[0]
    output_path = os.path.join(os.path.dirname(image_path), f"{base_name}_marked.jpg")
    cv2.imwrite(output_path, image)

    # Return the list of detected tags with their corners, center, and pose (translation and rotation)
    return detected_tag_info

def rotation_matrix_to_euler_angles(R):
    """
    Convert a rotation matrix to Euler angles (yaw, pitch, roll).
    Assumes that the rotation matrix follows the ZYX convention.
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

    return roll, pitch, yaw
