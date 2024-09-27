from src import apriltag_detection, calculate_pose, navigate, plot_room
import numpy as np

# parameters
image_number = 3
image_path = f"test_images/{image_number}.jpg"
json_path = "apriltags.json"
camera_focal_length = 304
real_tag_size = 0.1
target_tag_id = 3

# Calculate the center points
image_width = round(4031*0.3)
image_height = round(3023*0.3)
c_x = image_width / 2
c_y = image_height / 2
camera_matrix = np.array([[camera_focal_length, 0, c_x],
                          [0, camera_focal_length, c_y],
                          [0, 0, 1]])
dist_coeffs = np.zeros((1, 5))


# main function
def main():
    # Tag detection
    detected_info = apriltag_detection.detect_and_mark_apriltags(image_path, json_path, camera_matrix, dist_coeffs, real_tag_size)
    if detected_info is None:
        print("No AprilTag detected.")
        return None
    print("======================================")
    print(f"AprilTag {detected_info[0]['id']}")
    print(f"  Center: {detected_info[0]['center']}")
    print(f"  Rotation: {[angle * 180 / np.pi for angle in detected_info[0]['rotation']]} degrees")

    # Extract the first detected tag's pose (translation and rotation)
    tag_id = detected_info[0]["id"]
    pose = calculate_pose.calculate_pose(tag_id, detected_info)

    if pose is None:
        print(f"No pose found for tag ID {tag_id}")
        return None
    print("======================================")
    print(f"Pose:")
    print(f"  X: {pose[0]:.2f} meters")
    print(f"  Y: {pose[1]:.2f} meters")
    print(f"  User Facing Angle (Yaw): {pose[2]:.2f} degrees")

    # Navigation
    relative_angle, distance_to_tag = navigate.calculate_navigation(
        pose, target_tag_id, json_path
    )
    clock = navigate.angle_to_clock_direction(relative_angle)
    print("======================================")
    print(navigate.message(clock, distance_to_tag))
    print("======================================")

    # Plot
    output_path = f"test_images/{image_number}_plot.jpg"
    plot_room.plot_room(pose, target_tag_id, json_path, output_path)

    return 0

if __name__ == "__main__":
    main()
