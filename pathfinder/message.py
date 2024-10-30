import numpy as np

def message(angle, distance):

    while angle <= -180:
        angle += 360
    while angle > 180:
        angle -= 360

    distance = round(distance, 1)

    if -15 <= angle < 15:
        return f"Go straight and walk {distance} meters."
    elif 15 <= angle < 45:
        return f"Go straight and walk {distance} meters along 1 o'clock."
    elif 45 <= angle < 75:
        return f"Turn right to 2 o'clock and walk {distance} meters."
    elif 75 <= angle < 105:
        return f"Turn right and walk {distance} meters."
    elif 105 <= angle < 135:
        return f"Turn right to 4 o'clock and walk {distance} meters."
    elif 135 <= angle < 165:
        return f"Turn around to 5 o'clock and walk {distance} meters."
    elif 165 <= angle <= 180 or -180 < angle <= -165:
        return f"Turn around and walk {distance} meters."
    elif -165 < angle <= -135:
        return f"Turn around to 7 o'clock and walk {distance} meters."
    elif -135 < angle <= -105:
        return f"Turn left to 8 o'clock and walk {distance} meters."
    elif -105 < angle <= -75:
        return f"Turn left and walk {distance} meters."
    elif -75 < angle <= -45:
        return f"Turn left to 10 o'clock and walk {distance} meters."
    elif -45 < angle <= -15:
        return f"Go straight and walk {distance} meters along 11 o'clock."
    else:
        return f"Error: Angle {angle} not recognized."


def direction(angle):

    while angle <= -180:
        angle += 360
    while angle > 180:
        angle -= 360

    if -15 <= angle < 15:
        return f"in front of you"
    elif 15 <= angle < 45:
        return f"in front of you at 1 o'clock"
    elif 45 <= angle < 75:
        return f"on your right at 2 o'clock"
    elif 75 <= angle < 105:
        return f"on your right"
    elif 105 <= angle < 135:
        return f"on your right at 4 o'clock"
    elif 135 <= angle < 165:
        return f"behind you at 5 o'clock"
    elif 165 <= angle <= 180 or -180 < angle <= -165:
        return f"behind you"
    elif -165 < angle <= -135:
        return f"behind you at 7 o'clock"
    elif -135 < angle <= -105:
        return f"on your left at 8 o'clock"
    elif -105 < angle <= -75:
        return f"on your left"
    elif -75 < angle <= -45:
        return f"on your left at 10 o'clock"
    elif -45 < angle <= -15:
        return f"in front of you at 11 o'clock."
    else:
        return f"Error: Angle {angle} not recognized."


def generate_directions(user_pose, path, destination_angle, scale=1.0):
    messages = []
    current_pose = np.array(user_pose[:2])
    current_orientation = user_pose[2]

    for i in range(1, len(path)):
        next_point = np.array(path[i])
        direction_vector = next_point - current_pose
        angle_to_next_point = np.degrees(np.arctan2(direction_vector[1], direction_vector[0]))

        relative_angle = angle_to_next_point - current_orientation
        distance_to_next_point = np.linalg.norm(direction_vector) * scale

        # Create a message for the current step
        if i == 1:
            step_message = message(relative_angle, distance_to_next_point)
        else:
            step_message = "Then " + message(relative_angle, distance_to_next_point)
        if i == len(path) - 1:
            last_angle = destination_angle - current_orientation
            last_direction = direction(last_angle)
            step_message += f" And the destination will be {last_direction}."
        messages.append(step_message)

        # Update the current pose and orientation for the next step
        current_pose = next_point
        current_orientation = angle_to_next_point

    return messages


# Test the function
user_pose = (547, 381, -90)
path = [(547, 381), (540, 263), (538, 203), (229, 209)]
directions = generate_directions(user_pose, path, 0.1)