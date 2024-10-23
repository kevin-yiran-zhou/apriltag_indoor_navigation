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

def generate_directions(user_pose, path):
    """
    Generate a series of directional messages guiding the user from their current pose to the destination.
    
    :param user_pose: A tuple representing the current (x, y, orientation) of the user.
    :param path: A list of waypoints [(x1, y1), (x2, y2), ..., (xn, yn)] calculated from pathfinder.py.
    
    :return: A list of direction messages guiding the user along the path.
    """
    messages = []
    current_pose = np.array(user_pose[:2])
    current_orientation = user_pose[2]

    for i in range(1, len(path)):
        next_point = np.array(path[i])
        direction_vector = next_point - current_pose
        relative_angle = np.degrees(np.arctan2(direction_vector[1], direction_vector[0])) - current_orientation
        distance_to_next_point = np.linalg.norm(direction_vector)

        # Normalize the relative angle to be between 0 and 360 degrees
        relative_angle = (relative_angle + 360) % 360
        
        # Get the clock direction
        clock_direction = angle_to_clock_direction(relative_angle)

        # Create a message for the current step
        step_message = message(clock_direction, distance_to_next_point)
        messages.append(step_message)

        # Update the current pose and orientation for the next step
        current_pose = next_point
        current_orientation = (relative_angle + 360) % 360

    return messages

# Test the function
user_pose = (547, 328, 0)
path = [(547, 328), (538, 203), (229, 209)]
directions = generate_directions(user_pose, path)
for i, direction in enumerate(directions):
    print(f"Step {i+1}: {direction}")