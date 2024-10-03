from src import apriltag_detection_pnp, calculate_pose_pnp, navigate, plot_room
import numpy as np
import json

# parameters
image_number = "0_right"
image_path = f"test_images/{image_number}.jpg"
json_path = "apriltags.json"
camera_focal_length = 304
real_tag_size = 0.1
target_tag_id = 3

# Calculate the center points
image_width = 4031
image_height = 3023
c_x = 1330
c_y = 997
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
    pose = calculate_pose_pnp.calculate_pose(apriltag_data, tag_id, detected_info, camera_matrix, dist_coeffs, real_tag_size)
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


            # roll, pitch, yaw = rvec_to_euler_angles(rvec)
            # roll, pitch, yaw = np.degrees(roll)%360, np.degrees(pitch)%360, np.degrees(yaw)%360
            # print(f"  Roll: {roll:.2f}, Pitch: {pitch:.2f}, Yaw: {yaw:.2f}")