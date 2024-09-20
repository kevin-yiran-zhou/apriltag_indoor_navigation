from src import apriltag_detection, calculate_pose


# parameters
image_path = "test_images/3.jpg"
json_path = "apriltags.json"
camera_focal_length = 304
image_width = 404
image_height = 302
real_tag_size = 0.1


# main function
def main():
    # tag detection
    detected_info = apriltag_detection.detect_and_mark_apriltags(image_path, json_path)
    if detected_info is None:
        print("No AprilTag detected.")
        return None

    # distance and angle calculation
    tag_id, distance, angle = apriltag_detection.calculate_distance_and_angle(detected_info[0], camera_focal_length, image_width, image_height, real_tag_size)
    print("Detected AprilTags:")
    print(f"AprilTag ID: {tag_id}")
    print(f"  Distance: {distance:.2f} meters")
    print(f"  Angle: {angle:.2f} degrees")

    # pose calculation
    # pose = calculate_pose.calculate_pose(tag_id, distance, angle, json_path)
    # print("Calculated Pose:")
    # print(f"  X: {pose[0]:.2f} meters")
    # print(f"  Y: {pose[1]:.2f} meters")
    # print(f"  Angle: {pose[2]:.2f} degrees")

if __name__ == "__main__":
    main()