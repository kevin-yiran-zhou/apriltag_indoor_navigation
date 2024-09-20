import json
import numpy as np
import calculate_pose

def angle_to_clock_direction(angle):
    result = round(((angle + 15) % 360) / 30)
    if result == 0:
        result = 12
    return result

def message(clock, distance):
    if clock == 12:
        return f"Go staright and walk {distance} meters."
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
        return f"Turn right to {clock} o'clock and walk {distance} meters."
    else: # clock == 9
        return f"Turn right and walk {distance} meters."
    

# Load the AprilTag positions from a JSON file
with open('tags.json', 'r') as f:
    apriltag_data = json.load(f)
apriltag_poses = {tag['id']: (tag['name'], tag['position']) for tag in apriltag_data['apriltags']}

# Calculate the pose of the user using detected AprilTag
detected_tag_id = 4
user_pose = calculate_pose.calculate_pose(detected_tag_id, 3.0, 0)

# Calculate the pose of the selected AprilTag
target_tag_id = 3
tag_pose = apriltag_poses[target_tag_id][1]

# Calculate direction vector to the selected AprilTag
direction_vector = np.array(tag_pose[:2]) - np.array(user_pose[:2])
angle = np.arctan(direction_vector[1]/direction_vector[0]) / np.pi * 180 - user_pose[2]
distance = np.linalg.norm(direction_vector)
print(f"Direction: {angle:.1f} degrees, Distance: {distance:.1f} meters")

# Provide directional feedback
clock = int(angle_to_clock_direction(angle))
distance = round(distance, 1)
print(message(clock, distance))