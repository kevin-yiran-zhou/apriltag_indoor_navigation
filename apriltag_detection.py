import cv2
import apriltag
import json
import os
from pdf2image import convert_from_path  # Library to convert PDF to image
import numpy as np  # Import NumPy to handle array conversion

def detect_and_mark_apriltags_with_metadata(image_path, json_path, pdf_dir):
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

    # List to store centers and additional metadata of detected AprilTags
    detected_tag_info = []

    # Loop over the detected results
    for r in results:
        tag_id = r.tag_id  # Get the detected tag ID

        # Check if the detected tag ID is in the apriltag_dict
        if tag_id in apriltag_dict:
            tag_info = apriltag_dict[tag_id]  # Fetch metadata
            name = tag_info["name"]  # Use only the name
            position = tag_info["position"]
            pdf_file = tag_info.get("pdf", None)

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

            # Append the tag's metadata and center to the list
            detected_tag_info.append({
                "id": tag_id,
                "name": name,
                "position": position,
                "center": (cX, cY),
                "pdf": pdf_file
            })

    # Save the image with marked AprilTags in the same folder as the input image
    base_name = os.path.splitext(os.path.basename(image_path))[0]
    output_path = os.path.join(os.path.dirname(image_path), f"{base_name}_marked.png")
    cv2.imwrite(output_path, image)

    # Return the list of detected tags with their metadata
    return detected_tag_info

# Example usage
if __name__ == "__main__":
    detected_info = detect_and_mark_apriltags_with_metadata("test_images/0.png", "apriltags.json", "apriltag_images/")
    print("Detected AprilTags with metadata:", detected_info)
