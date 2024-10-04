from src import apriltag_detection_pnp, calculate_pose_pnp, navigate, plot_room
import numpy as np
import json

# parameters
image_number = "0_right"
image_path = f"test_images/{image_number}.jpg"
print("======================================")
print(f"image_path: {image_path}")
json_path = "apriltags.json"
real_tag_size = 0.1
target_tag_id = 3

# Calculate the center points
org_image_width = 4031
org_image_height = 3023
resize = 0.33
image_width = int(org_image_width * resize)
image_height = int(org_image_height * resize)
print(f"  image_width: {image_width}, image_height: {image_height}")
camera_focal_length = 26 * image_width / 7.03
c_x = round(image_width / 2)
c_y = round(image_height / 2)
camera_matrix = np.array([[camera_focal_length, 0, c_x],
                          [0, camera_focal_length, c_y],
                          [0, 0, 1]])
dist_coeffs = np.zeros((1, 5))

# Load the apriltags.json file
with open(json_path, 'r') as f:
    apriltag_data = json.load(f)


# main function
def main():
    # Tag detection
    detected_info = apriltag_detection_pnp.detect_and_mark_apriltags(image_path, apriltag_data)
    if detected_info is None:
        print("No AprilTag detected.")
        return None

    # Extract the first detected tag's pose (translation and rotation)
    tag_id = detected_info[0]["id"]
    pose = calculate_pose_pnp.calculate_pose(apriltag_data, tag_id, detected_info, camera_matrix, dist_coeffs, real_tag_size, resize)
    if pose is None:
        print(f"No pose found for tag ID {tag_id}")
        return None

    # Navigation
    twoD_pose = [pose["x"], pose["y"], pose["yaw"]]
    relative_angle, distance_to_tag = navigate.calculate_navigation(
        twoD_pose, target_tag_id, json_path
    )
    clock = navigate.angle_to_clock_direction(relative_angle)
    print("======================================")
    print(navigate.message(clock, distance_to_tag))
    print("======================================")

    # Plot
    output_path = f"test_images/{image_number}_plot.jpg"
    plot_room.plot_room(twoD_pose, target_tag_id, json_path, output_path)

    return 0

if __name__ == "__main__":
    main()