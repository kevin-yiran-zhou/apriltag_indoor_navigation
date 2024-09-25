import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for saving plots

import matplotlib.pyplot as plt
import json
import numpy as np

def plot_room(user_pose, target_tag_id, json_path, output_path="1_plot.jpg"):
    """
    Plots the room layout, user position, target tag position, and the path between them,
    and saves the plot as an image file.
    """
    # Load the AprilTag positions from the JSON file
    with open(json_path, 'r') as f:
        apriltag_data = json.load(f)
    apriltag_poses = {tag['id']: (tag['name'], tag['position']) for tag in apriltag_data['apriltags']}

    # Get target tag's position
    target_tag_pose = apriltag_poses[target_tag_id][1]
    target_x, target_y = target_tag_pose[0], target_tag_pose[1]

    # User's position and orientation
    user_x, user_y, user_angle = user_pose

    # Create a plot
    plt.figure(figsize=(6, 6))
    plt.xlim(0, 4)
    plt.ylim(0, 6)
    plt.gca().invert_yaxis()  # Invert the y-axis so positive is downward
    plt.grid(True)

    # Plot AprilTags
    for tag_id, (name, position) in apriltag_poses.items():
        plt.scatter(position[0], position[1], color='blue', label=f'Tag {tag_id}')
        plt.text(position[0] + 0.1, position[1], f'Tag {tag_id}', fontsize=12)

    # Plot user location and orientation
    plt.scatter(user_x, user_y, color='red', label='User')
    plt.text(user_x + 0.1, user_y, 'User', fontsize=12)

    # Draw user orientation (as an arrow)
    arrow_length = 0.5  # Length of the orientation arrow
    orientation_x = user_x + arrow_length * np.cos(np.radians(user_angle))
    orientation_y = user_y + arrow_length * np.sin(np.radians(user_angle))
    plt.arrow(user_x, user_y, orientation_x - user_x, orientation_y - user_y, 
              head_width=0.1, head_length=0.1, fc='red', ec='red', label='User Orientation')

    # Draw path from user to target tag
    plt.plot([user_x, target_x], [user_y, target_y], color='purple', linestyle='--', label='Path to Target')

    # Invert the Y-axis labels to match the inverted axis
    y_ticks = plt.gca().get_yticks()
    plt.gca().set_yticklabels([int(6 - tick) for tick in y_ticks])  # Reverse the tick labels

    # Save the plot to a file instead of displaying it
    plt.xlabel('X')
    plt.ylabel('Y')
    
    plt.savefig(output_path)
    plt.close()  # Close the figure to avoid displaying it
