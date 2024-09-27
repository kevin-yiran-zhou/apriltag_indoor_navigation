import json
import numpy as np

def angle_to_clock_direction(angle):
    """
    Converts an angle into a clock direction (12, 1, 2, ..., 12).
    """
    result = round(((angle + 15) % 360) / 30)
    if result == 0:
        result = 12
    return result

def message(clock, distance):
    """
    Generates a directional message based on the clock direction and distance.
    """
    distance = round(distance, 1)
    if clock == 12:
        return f"Go straight and walk {distance} meters."
    elif clock in [1, 11]:
        return f"Go straight and walk {distance} meters along {clock} o'clock."
    elif clock in [2, 4]:
        return f"Turn right to {clock} o'clock and walk {distance} meters."
    elif clock == 3:
        return f"Turn right and walk {distance} meters."
    elif clock in [5, 7]:
        return f"Turn around to {clock} o'clock and walk {distance} meters."
    elif clock == 6:
        return f"Turn around and walk {distance} meters."
    elif clock in [8, 10]:
        return f"Turn left to {clock} o'clock and walk {distance} meters."
    else:  # clock == 9
        return f"Turn left and walk {distance} meters."

def calculate_navigation(user_pose, target_tag_id, json_path):
    """
    Calculate the direction and distance to a target AprilTag and return a navigation message.
    Expects `user_pose` to be passed from outside.
    """
    # Load the AprilTag positions from the JSON file
    with open(json_path, 'r') as f:
        apriltag_data = json.load(f)
    apriltag_poses = {tag['id']: (tag['name'], tag['position']) for tag in apriltag_data['apriltags']}

    # Get the pose of the target AprilTag
    tag_pose = apriltag_poses[target_tag_id][1]

    # Calculate direction vector to the target AprilTag
    direction_vector = np.array(tag_pose[:2]) - np.array(user_pose[:2])
    relative_angle = np.degrees(np.arctan2(direction_vector[1], direction_vector[0])) - user_pose[2]
    distance_to_tag = np.linalg.norm(direction_vector)

    return relative_angle, distance_to_tag