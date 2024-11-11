import cv2
import numpy as np
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter

def detect_number(image, corners):
    # Unpack the four corners
    top_right, top_left, bottom_left, bottom_right = corners
    
    # Define the width and height of the new perspective rectangle
    width = max(np.linalg.norm(np.array(top_right) - np.array(top_left)),
                np.linalg.norm(np.array(bottom_right) - np.array(bottom_left)))
    height = max(np.linalg.norm(np.array(top_left) - np.array(bottom_left)),
                 np.linalg.norm(np.array(top_right) - np.array(bottom_right)))
    
    # Destination points for the perspective transformation
    dst_points = np.array([
        [0, 0],
        [width - 1, 0],
        [width - 1, height - 1],
        [0, height - 1]
    ], dtype="float32")
    
    # Source points from the corners
    src_points = np.array([top_left, top_right, bottom_right, bottom_left], dtype="float32")
    
    # Perform perspective transformation
    matrix = cv2.getPerspectiveTransform(src_points, dst_points)
    warped = cv2.warpPerspective(image, matrix, (int(width), int(height)))

    # OCR on the warped image
    image = Image.fromarray(warped)
    gray_image = image.convert('L')
    enhancer = ImageEnhance.Contrast(gray_image)
    enhanced_image = enhancer.enhance(2)
    threshold_image = enhanced_image.point(lambda p: p > 75 and 255)
    sharpened_image = threshold_image.filter(ImageFilter.SHARPEN)
    text = pytesseract.image_to_string(sharpened_image, config='--oem 3 --psm 6 outputbase digits')
    text = text.replace(" ", "").replace("\n", "")
    return text


def detect_room_label(image_path, resize_factor=5, area_threshold=100, approx_tolerance=0.05):
    # Load and resize the image
    image = cv2.imread(image_path)
    image = cv2.resize(image, (image.shape[1] // resize_factor, image.shape[0] // resize_factor))
    
    # Apply bilateral filter for noise reduction while keeping edges sharp
    filtered_image = cv2.bilateralFilter(image, 15, 80, 80)
    
    # Convert to grayscale
    gray = cv2.cvtColor(filtered_image, cv2.COLOR_BGR2GRAY)
    
    # Apply dilation followed by erosion to enhance the shapes
    kernel = np.ones((5, 5), np.float32) / 49
    dilated = cv2.dilate(gray, kernel, iterations=3)
    
    # Apply erosion to remove noise
    eroded = cv2.erode(dilated, kernel, iterations=1)
    
    # Detect edges using Canny Edge Detector
    thr1, thr2 = 50, 200
    edged = cv2.Canny(eroded, thr1, thr2)
    
    # Find contours
    contours, _ = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    rectangle_corners = []  # To store the four corners of each detected rectangle

    for cnt in contours:
        area = cv2.contourArea(cnt)
        
        # Only consider large enough areas to filter noise
        if area > area_threshold:
            # Approximate the contour to simplify it
            approx = cv2.approxPolyDP(cnt, approx_tolerance * cv2.arcLength(cnt, True), True)
            
            # Check if the contour has 4 vertices (rectangle-like shape)
            if len(approx) == 4:
                
                # Extract the corner points
                corners = [point[0] for point in approx]
                rectangle_corners.append(corners)

                OCR_result = detect_number(image, corners)
                if sum(char.isdigit() for char in OCR_result) >= 2:
                    print("Detected Number:", OCR_result)
                    cv2.drawContours(image, [approx], -1, (0, 255, 0), 3)
                    cv2.putText(image, OCR_result, tuple(corners[0]), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                    the_corners = corners
                    the_number = OCR_result
                    # break
    
    # Display the image with detected rectangles for visualization
    cv2.imshow('Rectangles Detected', image)
    cv2.waitKey(20000)
    cv2.destroyAllWindows()

    return the_corners, the_number

# Example usage
image_path = "/home/kevinbee/Desktop/apriltag_indoor_navigation/room_label_detector/images/office.JPG"
corners, number = detect_room_label(image_path, resize_factor=4, area_threshold=500, approx_tolerance=0.05)