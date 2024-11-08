import cv2
import numpy as np

def detect_labels(image_path, resize_width=800):
    # Load the image
    image = cv2.imread(image_path)
    
    # Calculate the resize ratio
    height, width = image.shape[:2]
    resize_ratio = resize_width / width
    
    # Resize the image
    resized_image = cv2.resize(image, (resize_width, int(height * resize_ratio)))
    gray = cv2.cvtColor(resized_image, cv2.COLOR_BGR2GRAY)

    # Improve contrast using histogram equalization
    gray = cv2.equalizeHist(gray)

    # Apply Gaussian blur to reduce noise and improve edge detection
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Detect edges with adjusted thresholds
    edged = cv2.Canny(blurred, 30, 100)

    # Find contours in the edged image
    contours, _ = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Loop through the contours and filter for rectangles
    labels = []
    for contour in contours:
        # Approximate the contour to reduce the number of points
        epsilon = 0.02 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)

        # Check if the approximated contour has 4 points, indicating a rectangle
        if len(approx) == 4:
            # Draw the rectangle on the resized image
            cv2.drawContours(resized_image, [approx], -1, (0, 255, 0), 2)
            labels.append(approx)

    # Display the output image with rectangles around detected labels
    cv2.imshow("Detected Labels", resized_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    return labels

# Provide the path to your image here
image_path = "/home/kevinbee/Desktop/apriltag_indoor_navigation/room_label_detector/images/1.JPG"
detected_labels = detect_labels(image_path, 1600)
print(f"Detected {len(detected_labels)} labels.")
