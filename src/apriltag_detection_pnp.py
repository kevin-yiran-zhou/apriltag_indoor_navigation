import cv2
import apriltag
import json
import os

def detect_and_mark_apriltags(image_path, apriltag_data):
    # Load the image
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

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

            # Append the tag's info
            detected_tag_info.append({
                "id": tag_id,
                "name": name,
                "center": (cX, cY),
                "corners": [ptD, ptC, ptB, ptA]
            })
            print("======================================")
            print(f"AprilTag {detected_tag_info[0]['id']} ({detected_tag_info[0]['name']})")
            print(f"  Center: {detected_tag_info[0]['center']}")
            print(f"  Corners: {detected_tag_info[0]['corners']}")

    # Save the image with marked AprilTags in the same folder as the input image
    base_name = os.path.splitext(os.path.basename(image_path))[0]
    output_path = os.path.join(os.path.dirname(image_path), f"{base_name}_marked.jpg")
    cv2.imwrite(output_path, image)

    # Return the list of detected tags with their corners, center, and pose (translation and rotation)
    return detected_tag_info