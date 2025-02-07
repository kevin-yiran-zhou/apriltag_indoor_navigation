# from src import apriltag_detection_pnp, calculate_pose_pnp, navigate, plot_room
from apriltag_indoor_navigation.pose_estimation.src import apriltag_detection_pnp, calculate_pose_pnp, navigate, plot_room
import numpy as np
import json
import os
import cv2


# # main function
# def run(image):
#     # parameters
#     print("======================================")
#     script_dir = os.path.dirname(os.path.abspath(__file__))
#     print(f"image: {image}")
#     image_path = os.path.join(script_dir, f"images/{image}.jpg")
#     image = cv2.imread(image_path)
#     # output_path4marked = os.path.join(script_dir, f"images_marked/{image}_marked.jpg")
#     # output_path4plot = os.path.join(script_dir, f"images_plot/{image}_plot.jpg")
#     json_path = os.path.join(script_dir, "apriltags.json")
#     real_tag_size = 0.1
#     # target_tag_id = 3

#     # Calculate the center points
#     org_image_width = 4031
#     org_image_height = 3023
#     resize = 0.33
#     image_width = int(org_image_width * resize)
#     image_height = int(org_image_height * resize)
#     print(f"  image_width: {image_width}, image_height: {image_height}")
#     camera_focal_length = 26 * image_width / 7.03
#     c_x = round(image_width / 2)
#     c_y = round(image_height / 2)
#     camera_matrix = np.array([[camera_focal_length, 0, c_x],
#                             [0, camera_focal_length, c_y],
#                             [0, 0, 1]])
#     dist_coeffs = np.zeros((1, 5))

#     # Load the apriltags.json file
#     with open(json_path, 'r') as f:
#         apriltag_data = json.load(f)
#     # Tag detection
#     detected_info, image = apriltag_detection_pnp.detect_and_mark_apriltags(image, apriltag_data) # , output_path4marked)
#     if len(detected_info) == 0:
#         print("No AprilTag detected.")
#         return None

#     # Extract the first detected tag's pose (translation and rotation)
#     tag_id = detected_info[0]["id"]
#     pose = calculate_pose_pnp.calculate_pose(apriltag_data, tag_id, detected_info, camera_matrix, dist_coeffs, real_tag_size, resize)
#     if pose is None:
#         print(f"No pose found for tag ID {tag_id}")
#         return None

#     # # Navigation
#     # twoD_pose = [pose["x"], pose["y"], pose["yaw"]]
#     # relative_angle, distance_to_tag = navigate.calculate_navigation(
#     #     twoD_pose, target_tag_id, json_path
#     # )
#     # clock = navigate.angle_to_clock_direction(relative_angle)
#     # print("======================================")
#     # print(navigate.message(clock, distance_to_tag))
#     # print("======================================")

#     # # Plot
#     # output_path4plot = os.path.join(script_dir, f"images_plot/{image}_plot.jpg")
#     # plot_room.plot_room(twoD_pose, target_tag_id, json_path, output_path4plot)

#     return 0


# main function
def run(image):
    # parameters
    print("======================================")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # print(f"image: {image}")
    # image_path = os.path.join(script_dir, f"images/{image}.jpg")
    print(f"image input type: {type(image)}")
    # convert
    python_bytes = bytes(image)
    np_array = np.frombuffer(python_bytes, dtype=np.uint8)
    # print(np_array.flatten()[0:10])
    # Reshape to YUV420 format
    yuv_frame = np_array.reshape((360, 320))  # OpenCV expects interleaved format
    # Convert YUV to BGR
    bgr_image = cv2.cvtColor(yuv_frame, cv2.COLOR_YUV2BGR_I420)
    print(f"image input type after conversion: {type(bgr_image)}")
    print("conversion done")

    # image = cv2.imread(image)
    # output_path4marked = os.path.join(script_dir, f"images_marked/{image}_marked.jpg")
    # output_path4plot = os.path.join(script_dir, f"images_plot/{image}_plot.jpg")
    json_path = os.path.join(script_dir, "apriltags.json")
    real_tag_size = 0.1
    # target_tag_id = 3

    # Calculate the center points
    org_image_width = 320
    org_image_height = 240
    resize = 1
    image_width = int(org_image_width * resize)
    image_height = int(org_image_height * resize)
    print(f"image_width: {image_width}, image_height: {image_height}")
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
    # Tag detection
    detected_info, image = apriltag_detection_pnp.detect_and_mark_apriltags(image, apriltag_data) # , output_path4marked)
    print(3)
    if len(detected_info) == 0:
        print("No AprilTag detected.")
        return None

    # Extract the first detected tag's pose (translation and rotation)
    tag_id = detected_info[0]["id"]
    pose = calculate_pose_pnp.calculate_pose(apriltag_data, tag_id, detected_info, camera_matrix, dist_coeffs, real_tag_size, resize)
    if pose is None:
        print(f"No pose found for tag ID {tag_id}")
        return None

    # # # Navigation
    # # twoD_pose = [pose["x"], pose["y"], pose["yaw"]]
    # # relative_angle, distance_to_tag = navigate.calculate_navigation(
    # #     twoD_pose, target_tag_id, json_path
    # # )
    # # clock = navigate.angle_to_clock_direction(relative_angle)
    # # print("======================================")
    # # print(navigate.message(clock, distance_to_tag))
    # # print("======================================")

    # # # Plot
    # # output_path4plot = os.path.join(script_dir, f"images_plot/{image}_plot.jpg")
    # # plot_room.plot_room(twoD_pose, target_tag_id, json_path, output_path4plot)

    return 0

def main():
    images = ["0_left"] # , "0_middle", "0_right", "1_left", "1_middle", "1_right", "2_left", "2_middle", "2_right", "3_left", "3_middle", "3_right"]
    for image in images:
        run(image)
        print(" ")

if __name__ == "__main__":
    main()