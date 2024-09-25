import numpy as np
import json

def calculate_pose(tag_id, distance, angle, tag_rotation_angle, json_path):
    with open(json_path, 'r') as f:
        apriltag_data = json.load(f)

    apriltag_poses = {tag['id']: (tag['name'], np.array(tag['position'])) for tag in apriltag_data['apriltags']}
    tag_pose = apriltag_poses[tag_id][1]

    # Tag's position in the room (x, y) and its facing angle in the world
    tag_x, tag_y, _, tag_facing_angle = tag_pose

    # The user's relative angle to the tag in the world frame
    # We need to adjust the angle using the tag's facing direction
    adjusted_angle = (tag_facing_angle - angle) % 360

    # Calculate the user's position relative to the tag
    x = tag_x + distance * np.cos(np.radians(adjusted_angle))
    y = tag_y + distance * np.sin(np.radians(adjusted_angle))

    # Calculate the user’s global facing angle by adjusting for the tag's rotation
    user_facing_angle = (180 - angle + tag_rotation_angle + tag_facing_angle) % 360

    return [x, y, user_facing_angle]
