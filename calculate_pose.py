import numpy as np
import json

def calculate_pose(tag_id, distance, angle):
    with open('tags.json', 'r') as f:
        apriltag_data = json.load(f)
    apriltag_poses = {tag['id']: (tag['name'], np.array(tag['position'])) for tag in apriltag_data['apriltags']}
    tag_pose = apriltag_poses[tag_id][1]
    x = tag_pose[0] + distance * np.cos(np.radians(angle))
    y = tag_pose[1] + distance * np.sin(np.radians(angle))
    angle = (tag_pose[2] + angle) % 360
    return [x, y, angle]