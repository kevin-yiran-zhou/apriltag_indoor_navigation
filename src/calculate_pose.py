import numpy as np

def calculate_pose(tag_id, detected_tag_info):
    """
    Calculate the user's position and orientation based on the detected AprilTag.
    This involves inverting the tag's pose to get the user's pose in the room,
    considering both yaw and the AprilTag's rotation along the vertical axis.
    """
    # Extract tag information from the detected info
    for tag in detected_tag_info:
        if tag["id"] == tag_id:
            translation = tag["translation"]
            rotation = tag["rotation"]

            # Invert the translation: the user's position is the negative of the tag's translation
            tx, ty, tz = translation
            user_position = [-tx, -ty, -tz]  # Inverted translation

            # Extract the yaw (rotation around the vertical axis) and roll
            yaw = rotation[0]  # Yaw angle (rotation around the vertical axis)
            roll = rotation[2]  # Roll angle (rotation along the camera's view axis)

            # Invert the yaw (flip 180 degrees) to get the user's facing direction
            user_yaw = (yaw + 180) % 360

            # Tag rotation: Adjust the user's facing angle by the tag's rotation (roll)
            adjusted_user_yaw = (user_yaw + roll) % 360

            # Return the user's pose (x, y) and adjusted facing angle (yaw)
            return [user_position[0], user_position[2], adjusted_user_yaw]  # In room coordinates (x, z as y)

    return None  # If no matching tag is found
