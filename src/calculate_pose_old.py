import numpy as np
import json

def calculate_pose(tag_id, distance, angle, tag_rotation_angle, json_path):
    """
    Calculate the user's position and orientation based on the detected AprilTag.
    """
    with open(json_path, 'r') as f:
        apriltag_data = json.load(f)

    apriltag_poses = {tag['id']: (tag['name'], np.array(tag['position'])) for tag in apriltag_data['apriltags']}
    tag_pose = apriltag_poses[tag_id][1]

    # Tag's position in the room (x, y) and its facing angle in world coordinates
    tag_x, tag_y, tag_z, tag_facing_angle = tag_pose

    # Adjust the relative angle correctly (user's perspective, left-negative, right-positive)
    adjusted_angle = (tag_facing_angle - angle + tag_rotation_angle) % 360

    # Calculate the user's position relative to the tag
    x = tag_x + distance * np.cos(np.radians(adjusted_angle))
    y = tag_y + distance * np.sin(np.radians(adjusted_angle))

    # User's facing angle relative to the room
    user_facing_angle = (adjusted_angle + 180) % 360  # Adding 180 to flip the user's facing direction

    # If the user_facing_angle is incorrect, you can toggle between +180 or -180 depending on the setup.
    # Uncomment the next line if you find that subtracting 180 degrees works better in your scenario:
    # user_facing_angle = (adjusted_angle - 180) % 360

    return [x, y, user_facing_angle]

