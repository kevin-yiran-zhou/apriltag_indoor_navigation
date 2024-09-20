import cv2
import apriltag
import json
import numpy as np
import os

def detect_and_mark_apriltags(image_path, json_path, pdf_dir):
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

    # List to store corners and center of detected AprilTags
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

            # Draw only the name of the tag on the image
            cv2.putText(image, name, (ptA[0], ptA[1] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            # Append the tag's ID, four corners, and center to the list
            detected_tag_info.append({
                "id": tag_id,
                "corners": {
                    "ptA": ptA,
                    "ptB": ptB,
                    "ptC": ptC,
                    "ptD": ptD
                },
                "center": (cX, cY)
            })

    # Save the image with marked AprilTags in the same folder as the input image
    base_name = os.path.splitext(os.path.basename(image_path))[0]
    output_path = os.path.join(os.path.dirname(image_path), f"{base_name}_marked.png")
    cv2.imwrite(output_path, image)

    # Return the list of detected tags with their corners and center locations
    return detected_tag_info



def calculate_distance_and_angle(tag_info, camera_focal_length, image_width, image_height, real_tag_size=0.2):
    """
    Calculate real-world distance and angle from camera to AprilTag.
    
    Parameters:
    - tag_info (dict): The dictionary containing ID, corners, and center from previous function.
    - camera_focal_length (float): The focal length of the camera in pixels.
    - image_width (int): Width of the camera image in pixels.
    - image_height (int): Height of the camera image in pixels.
    - real_tag_size (float): Real-world size of the AprilTag (default is 0.2 meters = 200 mm).
    
    Returns:
    - distance (float): Distance from the camera to the AprilTag in meters.
    - angle (float): Angle between the camera and the AprilTag in degrees.
    """
    
    # Extract the corners of the tag from the input
    corners = tag_info["corners"]
    ptA = np.array(corners["ptA"])
    ptB = np.array(corners["ptB"])
    ptC = np.array(corners["ptC"])
    ptD = np.array(corners["ptD"])

    # Calculate the pixel width of the tag in the image (distance between ptA and ptB)
    pixel_tag_width = np.linalg.norm(ptA - ptB)

    # Calculate the distance using the pinhole camera model
    distance = (real_tag_size * camera_focal_length) / pixel_tag_width

    # Extract the center of the tag from the input
    tag_center = np.array(tag_info["center"])

    # Compute the camera image center
    image_center = np.array([image_width / 2, image_height / 2])

    # Calculate the displacement between the image center and the tag center
    displacement_x = tag_center[0] - image_center[0]

    # Calculate the horizontal angle using the displacement in pixels and the focal length
    angle = np.degrees(np.arctan(displacement_x / camera_focal_length))

    return distance, angle



# Example usage
if __name__ == "__main__":
    detected_info = detect_and_mark_apriltags("test_images/0.png", "apriltags.json", "apriltag_images/")
    print("Detected AprilTags with metadata (ID, corners, and center):")
    for tag in detected_info:
        print(f"Tag ID: {tag['id']}")
        print(f"  Corners: {tag['corners']}")
        print(f"  Center: {tag['center']}")
        distance, angle = calculate_distance_and_angle(tag, 1000, 640, 480)
        print(f"  Distance: {distance:.2f} meters")
        print(f"  Angle: {angle:.2f} degrees")