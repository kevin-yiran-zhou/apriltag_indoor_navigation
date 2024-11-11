from PIL import Image, ImageEnhance, ImageFilter
import pytesseract

# Load the image
image_path = '/home/kevinbee/Desktop/apriltag_indoor_navigation/room_label_detector/images/office_num.png'
image = Image.open(image_path)

gray_image = image.convert('L')
enhancer = ImageEnhance.Contrast(gray_image)
enhanced_image = enhancer.enhance(2)

threshold_image = enhanced_image.point(lambda p: p > 75 and 255)
sharpened_image = threshold_image.filter(ImageFilter.SHARPEN)
sharpened_image.save('/home/kevinbee/Desktop/apriltag_indoor_navigation/room_label_detector/images/office_num_sharpened.png')

# Use OCR with different PSM
extracted_text = pytesseract.image_to_string(sharpened_image, config='--oem 3 --psm 6 outputbase digits')

# Print the extracted text
print("Extracted Text:", extracted_text)
