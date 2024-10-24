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

def generate_directions(user_pose, path, scale=1.0):
    messages = []
    current_pose = np.array(user_pose[:2])
    current_orientation = user_pose[2]

    for i in range(1, len(path)):
        next_point = np.array(path[i])
        direction_vector = next_point - current_pose
        angle_to_next_point = np.degrees(np.arctan2(direction_vector[1], direction_vector[0]))

        # Adjust for the system where 0 degrees is to the right and angles increase clockwise.
        relative_angle = angle_to_next_point - current_orientation
        distance_to_next_point = np.linalg.norm(direction_vector) * scale  # Apply the scale factor

        # Get the clock direction
        clock_direction = angle_to_clock_direction(relative_angle)

        # Create a message for the current step
        if i == 1:
            step_message = message(clock_direction, distance_to_next_point)
        else:
            step_message = "Then " + message(clock_direction, distance_to_next_point)
        if i == len(path) - 1:
            step_message += " And you will reach your destination."
        messages.append(step_message)

        # Update the current pose and orientation for the next step
        current_pose = next_point
        current_orientation = angle_to_next_point

    return messages


# Test the function
user_pose = (547, 381, -90)
path = [(547, 381), (540, 263), (538, 203), (229, 209)]
directions = generate_directions(user_pose, path, 0.1)