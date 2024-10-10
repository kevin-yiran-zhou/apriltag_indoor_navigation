from src import apriltag_detection_old, calculate_pose_old, navigate, plot_room

# parameters
image_number = 1
image_path = f"test_images/{image_number}.jpg"
json_path = "apriltags.json"
camera_focal_length = 304
# image_width = 4031
# image_height = 3022
image_width = 1330
image_height = 997
real_tag_size = 0.1
target_tag_id = 3

# main function
def main():
    # Tag detection
    detected_info = apriltag_detection_old.detect_and_mark_apriltags(image_path, json_path)
    if detected_info is None:
        print("No AprilTag detected.")
        return None

    # Distance, angle, and extra angle calculation
    tag_id, distance, angle, tag_rotation_angle = apriltag_detection_old.calculate_distance_and_angle(
        detected_info[0], camera_focal_length, image_width, image_height, real_tag_size
    )
    print("======================================")
    print("Detected AprilTags:")
    print(f"AprilTag ID: {tag_id}")
    print(f"  Distance: {distance:.2f} meters")
    print(f"  Angle: {angle:.2f} degrees")
    print(f"  Tag Rotation Angle: {tag_rotation_angle:.2f} degrees")  # Display the extra angle

    # Pose calculation
    pose = calculate_pose_old.calculate_pose(tag_id, distance, angle, tag_rotation_angle, json_path)
    print("======================================")
    print("Calculated Pose:")
    print(f"  X: {pose[0]:.2f} meters")
    print(f"  Y: {pose[1]:.2f} meters")
    print(f"  User Facing Angle: {pose[2]:.2f} degrees")


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